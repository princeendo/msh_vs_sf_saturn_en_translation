"""Coverage of the ending text: what the roster image changes and leaves (END-025).

For every arcade slot (0-25) it records, as metadata only (no text):

- the Japanese ending pages in ``ME.PAC`` (offset, record count, the slots that
  share the same pointer, and whether the Saturn records equal the arcade
  Japanese ones). The last pointer has no following pointer, so its extent is
  unknown and reported as ``null``;
- the English pages (the arcade English table, ``0x20C1B4``) and the slots that
  share them, with the same ``null`` rule for the last pointer;
- the two ``MC13`` dialogue pairs (partner index ``slot``, point index
  ``26 + slot``, `EXP-0043`) and whether they equal the arcade block;
- whether the slot is in the roster (``data/text/m5_roster.json``).

With ``--built-track`` it also compares a built image with the source and
checks that every byte outside the roster's targets is unchanged:
``ME.PAC`` outside the roster's page spans, decoded ``MC13`` outside the roster's
dialogue records, and ``MM.BIN`` outside the roster's name and name-length
entries.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.iso9660 import Track
from tools.disc.pac_lzss import decode_file
from tools.disc.patch_image import find_entry
from tools.reference.arcade_endings import PAGE_TABLES, SLOTS, long_at, page_span
from tools.reference.cps2_text import build_program
from tools.reference.mame_audit import parse_driver
from tools.text.caption_compiler import RECORD
from tools.text.official_endings import (
    ARCADE_DIALOGUE,
    DIALOGUE_FIRST,
    EN_RECORD,
    MC13_TABLE,
    ME_BASE,
    MM_NAME_LENGTHS,
    MM_NAMES,
    NAME_BYTES,
)

FILES = ("ME.PAC", "MC13.PAC", "MM.BIN")
DEFAULT_TRACK = Path(
    "local/disc_images/mshvsf_saturn_jp/"
    "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
)


def read_files(track: Path) -> dict[str, bytes]:
    with track.open("rb") as stream:
        disc = Track(stream, track.stat().st_size)
        return {n: disc.read(*find_entry(track, f"{n};1")) for n in FILES}


def pointer_groups(program: bytes, table: int) -> dict[int, list[int]]:
    groups: dict[int, list[int]] = {}
    for slot in range(SLOTS):
        groups.setdefault(long_at(program, table + 4 * slot), []).append(slot)
    return groups


def dialogue_records(slot: int) -> list[int]:
    """MC13 records of the slot's partner pair and point pair."""
    return [
        DIALOGUE_FIRST + 2 * index + k for index in (slot, SLOTS + slot) for k in (0, 1)
    ]


def slot_rows(
    program: bytes, me: bytes, mc13: bytes, roster: set[int]
) -> list[dict[str, object]]:
    decoded = decode_file(mc13)[1]
    last = {
        k: max(long_at(program, t + 4 * s) for s in range(SLOTS))
        for k, t in PAGE_TABLES.items()
    }
    groups = {k: pointer_groups(program, t) for k, t in PAGE_TABLES.items()}
    rows = []
    for slot in range(SLOTS):
        js, je = page_span(program, PAGE_TABLES["ja"], slot)
        es, ee = page_span(program, PAGE_TABLES["en"], slot)
        known = js != last["ja"]
        records = dialogue_records(slot)
        dialogue_equal = all(
            program[a : a + RECORD]
            == decoded[MC13_TABLE + RECORD * r : MC13_TABLE + RECORD * (r + 1)]
            for r in records
            for a in [ARCADE_DIALOGUE + RECORD * (r - DIALOGUE_FIRST)]
        )
        rows.append(
            {
                "slot": slot,
                "in_roster": slot in roster,
                "me_offset": f"0x{js - ME_BASE:X}",
                "pages_ja": (je - js) // RECORD if known else None,
                "pages_shared_with": [
                    s
                    for s in groups["ja"][
                        long_at(program, PAGE_TABLES["ja"] + 4 * slot)
                    ]
                    if s != slot
                ],
                "pages_equal_arcade_ja": (
                    program[js:je] == me[js - ME_BASE : je - ME_BASE] if known else None
                ),
                "pages_en": (ee - es) // EN_RECORD if es != last["en"] else None,
                "english_shared_with": [
                    s
                    for s in groups["en"][
                        long_at(program, PAGE_TABLES["en"] + 4 * slot)
                    ]
                    if s != slot
                ],
                "mc13_records": records,
                "dialogue_equal_arcade_ja": dialogue_equal,
            }
        )
    return rows


def outside_unchanged(
    source: bytes, built: bytes, spans: Sequence[tuple[int, int]]
) -> dict[str, object]:
    """Whether every byte outside ``spans`` is unchanged, and how many differ inside."""
    inside = bytearray(len(source))
    for a, b in spans:
        inside[a:b] = b"\x01" * (b - a)
    common = min(len(source), len(built))
    changed = [i for i in range(common) if source[i] != built[i]]
    return {
        "same_length": len(source) == len(built),
        "outside_unchanged": len(source) == len(built)
        and not any(not inside[i] for i in changed),
        "changed_bytes_inside": sum(1 for i in changed if inside[i]),
    }


def built_checks(
    program: bytes,
    source: dict[str, bytes],
    built: dict[str, bytes],
    roster: Sequence[int],
) -> dict[str, object]:
    me_spans = []
    for slot in roster:
        js, je = page_span(program, PAGE_TABLES["ja"], slot)
        me_spans.append((js - ME_BASE, je - ME_BASE))
    mc13_spans = [
        (MC13_TABLE + RECORD * r, MC13_TABLE + RECORD * (r + 1))
        for slot in roster
        for r in dialogue_records(slot)
    ]
    mm_spans = [
        (MM_NAMES + NAME_BYTES * s, MM_NAMES + NAME_BYTES * (s + 1)) for s in roster
    ] + [(MM_NAME_LENGTHS + s, MM_NAME_LENGTHS + s + 1) for s in roster]
    return {
        "ME.PAC": outside_unchanged(source["ME.PAC"], built["ME.PAC"], me_spans),
        "MC13.PAC (decoded)": outside_unchanged(
            decode_file(source["MC13.PAC"])[1],
            decode_file(built["MC13.PAC"])[1],
            mc13_spans,
        ),
        "MM.BIN": outside_unchanged(source["MM.BIN"], built["MM.BIN"], mm_spans),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--roster", type=Path, default=Path("data/text/m5_roster.json"))
    parser.add_argument("--track", type=Path, default=DEFAULT_TRACK)
    parser.add_argument("--built-track", type=Path, help="track 01 of a built image")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.archive.stem])
    roster = [int(c["slot"]) for c in json.loads(args.roster.read_text())["characters"]]
    source = read_files(args.track)
    rows = slot_rows(program, source["ME.PAC"], source["MC13.PAC"], set(roster))
    report: dict[str, object] = {
        "tool": "tools.text.ending_coverage",
        "archive": args.archive.name,
        "roster_slots": roster,
        "excluded_slots": [s for s in range(SLOTS) if s not in roster],
        "slots": rows,
    }
    if args.built_track:
        checks = built_checks(program, source, read_files(args.built_track), roster)
        report["built_track"] = args.built_track.name
        report["built_checks"] = checks
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(
        json.dumps(
            {"excluded_slots": report["excluded_slots"]}
            | {"built_checks": report.get("built_checks")}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
