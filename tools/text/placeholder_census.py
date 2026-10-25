"""Census of name placeholders, and what a roster image leaves Japanese (END-022).

The ``0x0000`` cell inserts a character's name from the ``MM.BIN`` name table
(`EXP-0039`, `EXP-0044`). Once that table holds English names, every placeholder
that stays in Japanese text shows an English name. This census reads the
untouched image and reports, as metadata only (no text):

- win-quote tables (``data/text/coverage_manifest.json``; roster tables from
  ``data/text/m5_roster.json``). Roster tables become English with the
  placeholder dropped (`RE-042`); the others stay Japanese;
- ``MC13``'s 120-record table: records 0-15 are Cyber-Akuma's win quotes, and
  pair ``i`` (records ``16 + 2i``, ``17 + 2i``) is a partner line (``i < 26``) or a
  point line (``i >= 26``, slot ``i - 26``, `EXP-0043`). A roster image makes the
  pairs of roster slots English;
- ``ME.PAC`` Japanese pages, and any other placeholder found by a strict
  text-run sweep of every file (a ``0x0000`` inside 25 text-like words with at
  least four kana and at most two placeholder cells), such as the ``MM.BIN``
  Japanese text table.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.disc.iso9660 import Track, primary_volume, walk
from tools.disc.pac_lzss import decode_file

RECORD, CELLS = 76, 38
MC13_TABLE, MC13_RECORDS, DIALOGUE_FIRST, SLOTS = 0xA06C, 120, 16, 26


def words(data: bytes) -> list[int]:
    return [int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data) - 1, 2)]


def texty(word: int) -> bool:
    return word in (0x0000, 0x0020) or 0x0800 <= word <= 0x0C5F


def text_sites(data: bytes) -> list[int]:
    """Byte offsets of ``0x0000`` cells inside runs of text-like words."""
    ws = words(data)
    sites = []
    for i, word in enumerate(ws):
        if word:
            continue
        window = ws[max(0, i - 12) : i + 13]
        kana = sum(1 for w in window if 0x0800 <= w <= 0x08AF)
        zeros = window.count(0x0000)
        if (
            len(window) >= 20
            and all(texty(w) for w in window)
            and kana >= 4
            and zeros <= 2
        ):
            sites.append(2 * i)
    return sites


def table_sites(data: bytes, table: int, records: int) -> list[list[int]]:
    """[record, cell] of each placeholder in a 19 x 2 record table."""
    out = []
    for record in range(records):
        start = table + RECORD * record
        cells = words(data[start : start + RECORD])
        out += [[record, c] for c, w in enumerate(cells) if w == 0x0000]
    return out


def block_slot(item: dict[str, object], offset: int, records: int) -> int:
    """The arcade slot whose block lies in this table (EXP-0034 census)."""
    blocks = item["slot_blocks"]
    assert isinstance(blocks, dict)
    for slot, block in blocks.items():
        start = int(str(block["offset"]), 16)
        if offset - RECORD <= start < offset + RECORD * records:
            return int(slot)
    return int(next(iter(blocks)))


def mc13_role(record: int, roster: set[int]) -> dict[str, object]:
    if record < DIALOGUE_FIRST:
        return {"content": "Cyber-Akuma win quote", "slot": 19, "english": False}
    index = (record - DIALOGUE_FIRST) // 2
    role, slot = ("partner", index) if index < SLOTS else ("point", index - SLOTS)
    return {
        "content": f"post-boss {role} line",
        "slot": slot,
        "english": slot in roster,
    }


def census(
    files: dict[str, bytes], manifest: dict[str, Any], roster_doc: dict[str, Any]
) -> dict[str, object]:
    roster = {int(c["slot"]): c for c in roster_doc["characters"]}
    roster_tables = {c["file"]: int(c["table"], 16) for c in roster.values()}
    entries: list[dict[str, object]] = []
    covered: dict[str, list[tuple[int, int]]] = {}
    for item in manifest["files"]:
        name = item["file"]
        data = decode_file(files[name])[1]
        if name == "MC13.PAC":
            for record, cell in table_sites(data, MC13_TABLE, MC13_RECORDS):
                entries.append(
                    {
                        "file": name,
                        "table": f"0x{MC13_TABLE:X}",
                        "record": record,
                        "cell": cell,
                    }
                    | mc13_role(record, set(roster))
                )
            covered[name] = [(MC13_TABLE, MC13_TABLE + RECORD * MC13_RECORDS)]
            continue
        spans = []
        for table in item["saturn_tables"]:
            offset, records = int(table["offset"], 16), int(table["records"])
            is_roster = (
                name in roster_tables
                and abs(offset - roster_tables[name]) < RECORD * 16
            )
            if is_roster:  # the roster's own offset and 16 records (RE-042)
                offset, records = roster_tables[name], 16
            spans.append((offset, offset + RECORD * records))
            for record, cell in table_sites(data, offset, records):
                entries.append(
                    {
                        "file": name,
                        "table": f"0x{offset:X}",
                        "record": record,
                        "cell": cell,
                        "content": "win quote",
                        "slot": block_slot(item, offset, records),
                        "english": is_roster,
                    }
                )
        covered[name] = spans
    others = []
    for name, raw in sorted(files.items()):
        try:
            data = decode_file(raw)[1]
        except ValueError:
            data = raw
        for offset in text_sites(data):
            if not any(a <= offset < b for a, b in covered.get(name, [])):
                others.append(
                    {"file": name, "offset": f"0x{offset:X}", "english": False}
                )
    unique = {(e["file"], e["table"], e["record"], e["cell"]): e for e in entries}
    rows = list(unique.values())
    return {
        "placeholders": len(rows) + len(others),
        "english_in_roster_image": sum(1 for e in rows if e["english"]),
        "japanese_in_roster_image": sum(1 for e in rows if not e["english"])
        + len(others),
        "tables": rows,
        "other_text": others,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--track",
        type=Path,
        default=Path(
            "local/disc_images/mshvsf_saturn_jp/"
            "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
        ),
    )
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/text/coverage_manifest.json")
    )
    parser.add_argument("--roster", type=Path, default=Path("data/text/m5_roster.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    files: dict[str, bytes] = {}
    with args.track.open("rb") as stream:
        track = Track(stream, args.track.stat().st_size)
        volume = primary_volume(track)
        for entry in walk(
            track, int(str(volume["root_lsn"])), int(str(volume["root_size"]))
        ):
            if not entry.is_dir:
                files[entry.path.split(";")[0]] = track.read(
                    entry.lsn, entry.size_bytes
                )
    report = census(
        files,
        json.loads(args.manifest.read_text()),
        json.loads(args.roster.read_text()),
    )
    report = {"tool": "tools.text.placeholder_census"} | report
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "placeholders",
                    "english_in_roster_image",
                    "japanese_in_roster_image",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
