"""Census of the roster's endings against the arcade reference (END-021).

For each roster slot (``data/text/m5_roster.json``) it records, as metadata only
(no text):

- the Japanese and English ending-page counts, and whether every Saturn page
  record in ``ME.PAC`` equals the arcade Japanese record (`EXP-0042`);
- for the character's two ``MC13`` dialogue pairs (as partner: index ``slot``;
  as point: ``26 + slot``, `EXP-0043`), whether both records equal the arcade
  block, and whether each English half fits 19 cells with the longest roster
  English name inserted;
- the English name's cells (pair glyphs) and the Japanese name length
  (``MM.BIN`` ``0x96DE8``).

Inputs are read only. The output is JSON metadata that may be committed.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.iso9660 import Track
from tools.disc.pac_lzss import decode_file
from tools.disc.patch_image import find_entry
from tools.reference.arcade_endings import (
    PAGE_TABLES,
    PARTNER_LINES,
    PARTNER_RECORD,
    SLOTS,
    latin,
    page_span,
)
from tools.reference.cps2_text import build_program
from tools.reference.mame_audit import parse_driver
from tools.text.caption_compiler import LINE_CELLS, RECORD
from tools.text.official_endings import (
    ARCADE_DIALOGUE,
    ARCADE_NAMES,
    DIALOGUE_FIRST,
    EN_RECORD,
    MC13_TABLE,
    ME_BASE,
    MM_NAME_LENGTHS,
    NAME_BYTES,
    en_lines,
    name_text,
)
from tools.text.pair_font import split_pairs


def half_cells(text: str, name_cells: int) -> int:
    segments = text.split("{0000}")
    used = sum(len(split_pairs(s)) for s in segments if s)
    return used + name_cells * (len(segments) - 1)


def census(
    program: bytes, me: bytes, mc13: bytes, mm: bytes, roster: Sequence[int]
) -> dict[str, object]:
    decoded = decode_file(mc13)[1]
    names = {
        s: latin(program, ARCADE_NAMES + NAME_BYTES * s, NAME_BYTES).strip()
        for s in roster
    }
    cells = {s: len(split_pairs(name_text(names[s]))) for s in roster}
    longest = max(cells.values())
    rows = []
    for slot in roster:
        js, je = page_span(program, PAGE_TABLES["ja"], slot)
        es, ee = page_span(program, PAGE_TABLES["en"], slot)
        lines = [
            line for a in range(es, ee, EN_RECORD) for line in en_lines(program, a)
        ]
        pairs = []
        for index in (slot, SLOTS + slot):
            record = DIALOGUE_FIRST + 2 * index
            arcade = ARCADE_DIALOGUE + RECORD * (record - DIALOGUE_FIRST)
            identical = (
                program[arcade : arcade + 2 * RECORD]
                == decoded[
                    MC13_TABLE + RECORD * record : MC13_TABLE + RECORD * (record + 2)
                ]
            )
            halves = en_lines(program, PARTNER_LINES + PARTNER_RECORD * index)
            widest = max(half_cells(h, longest) for h in halves)
            pairs.append(
                {
                    "index": index,
                    "mc13_records": [record, record + 1],
                    "equals_arcade_ja": identical,
                    "widest_half_cells": widest,
                    "fits": widest <= LINE_CELLS,
                    "placeholders": sum(h.count("{0000}") for h in halves),
                }
            )
        rows.append(
            {
                "slot": slot,
                "pages_ja": (je - js) // RECORD,
                "pages_en": (ee - es) // EN_RECORD,
                "me_offset": f"0x{js - ME_BASE:X}",
                "pages_equal_arcade_ja": program[js:je]
                == me[js - ME_BASE : je - ME_BASE],
                "widest_page_line_chars": max(len(line) for line in lines),
                "page_placeholders": sum(line.count("{0000}") for line in lines),
                "dialogue_pairs": pairs,
                "name_cells": cells[slot],
                "name_length_ja": mm[MM_NAME_LENGTHS + slot],
            }
        )
    ok = all(
        r["pages_ja"] == r["pages_en"]
        and r["pages_equal_arcade_ja"]
        and all(p["equals_arcade_ja"] and p["fits"] for p in r["dialogue_pairs"])  # type: ignore[attr-defined]
        for r in rows
    )
    return {
        "longest_name_cells": longest,
        "pages_total": sum(int(str(r["pages_en"])) for r in rows),
        "all_consistent": ok,
        "slots": rows,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--roster", type=Path, default=Path("data/text/m5_roster.json"))
    parser.add_argument(
        "--track",
        type=Path,
        default=Path(
            "local/disc_images/mshvsf_saturn_jp/"
            "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
        ),
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.archive.stem])
    with args.track.open("rb") as stream:
        disc = Track(stream, args.track.stat().st_size)
        files = {
            n: disc.read(*find_entry(args.track, f"{n};1"))
            for n in ("ME.PAC", "MC13.PAC", "MM.BIN")
        }
    roster = [int(c["slot"]) for c in json.loads(args.roster.read_text())["characters"]]
    report = census(
        program, files["ME.PAC"], files["MC13.PAC"], files["MM.BIN"], roster
    )
    report = {"tool": "tools.text.ending_census", "archive": args.archive.name} | report
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("longest_name_cells", "pages_total", "all_consistent")
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
