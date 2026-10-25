"""Generate a caption spec for one ending from the official arcade English (END-010).

The policy (user decision, 2026-10-24, `data/translations/README.md`):

- the point character's three ending pages get the official English pages
  (English page table ``0x20C1B4``, `EXP-0042`), in ``ME.PAC``;
- the post-boss dialogue gets the arcade's two English partner lines
  (``0x22226C``): record ``p`` for each listed partner ``p`` and record
  ``26 + point`` for the point character (`EXP-0043`). Each English line fills
  its ``MC13`` pair (``16 + 2 * index``). With the default ``whole`` layout,
  both boxes hold the full two-line text: the box never closes between the two
  records, so it reads as one block lasting both boxes' time (`EXP-0045`, user
  request). ``split`` puts one half per box at the line break (`EXP-0044`);
- the inserted names (``0000``) come from the ``MM.BIN`` name table, set to the
  arcade's English names for the point character and the listed partners. The
  game inserts a fixed number of cells per name from a one-byte length table
  (``MM.BIN`` ``0x96DE8``, `EXP-0044`), so those entries are set to the English
  names' cell counts.

With ``--roster`` (`END-023`), every roster slot is both a point character and a
partner, and ``--with-win-quotes`` adds the M5 win-quote tables
(``official_captions.roster_spec``), giving one combined spec for one font.

Before writing anything, every Saturn record to be replaced is checked against
the arcade Japanese record it pairs with (byte-identical, `EXP-0042`). The text is
read from the local arcade ROM at build time and written to an ignored path.
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
from tools.reference.cps2_text import build_program, read_quote_table
from tools.reference.mame_audit import parse_driver
from tools.text.caption_compiler import LINE_CELLS, RECORD, SCHEMA_V3, TOKEN
from tools.text.official_captions import best_shifts, centred, roster_spec
from tools.text.pair_font import split_pairs

EN_RECORD, EN_CELLS = 100, 25  # arcade English records: 2 lines of 25 cells
ARCADE_DIALOGUE = 0x217BE0  # Japanese dialogue block = MC13 records 16-119
MC13_TABLE, DIALOGUE_FIRST = 0xA06C, 16  # EXP-0034, EXP-0043
ME_BASE = 0x211D58  # ME.PAC file offset = arcade Japanese page address - this
ARCADE_NAMES, NAME_BYTES = 0x2236BC, 32  # English names, 16 cells per slot
MM_NAMES, NAME_LEAD = 0x7D3C0, 2  # MM.BIN name table; two leading blank cells
MM_NAME_LENGTHS = 0x96DE8  # MM.BIN: one byte per slot, cells inserted per name
NAME_GUESS = 2  # cells assumed for an inserted name when centring a line
WIN_QUOTES_EN = 0x20C014  # arcade English win-quote table (EXP-0029)


def en_lines(program: bytes, address: int) -> list[str]:
    """The two lines of an arcade English record, stripped."""
    text = latin(program, address, EN_RECORD)
    return [text[:EN_CELLS].strip(), text[EN_CELLS:].strip()]


def box_line(text: str) -> str:
    """Centre one dialogue half in whole cells; ``{0000}`` becomes ``{P}``."""
    text = text.replace("{0000}", TOKEN)
    segments = text.split(TOKEN)
    used = sum(len(split_pairs(s)) for s in segments if s)
    used += NAME_GUESS * (len(segments) - 1)
    if used > LINE_CELLS:
        raise ValueError(f"{text!r} needs {used} cells (max {LINE_CELLS})")
    return "  " * ((LINE_CELLS - used) // 2) + text


def name_text(name: str) -> str:
    """Odd-length names get a leading half space, so they end on a cell edge."""
    return name if len(name) % 2 == 0 else " " + name


def ending_spec(
    program: bytes,
    point: int | Sequence[int],
    partners: Sequence[int],
    layout: str = "whole",
) -> tuple[dict[str, object], dict[str, list[int]]]:
    """The v3 spec, and the arcade Japanese records it replaces.

    ``point`` may list several point characters (`END-020`): each gets its pages
    and its point pair; the partner pairs are shared.
    """
    points = [point] if isinstance(point, int) else list(point)
    page_tables, pages_ja = [], []
    for slot in points:
        start, end = page_span(program, PAGE_TABLES["en"], slot)
        pages = [en_lines(program, a) for a in range(start, end, EN_RECORD)]
        shifts = best_shifts([line for page in pages for line in page if line])
        jp_start, jp_end = page_span(program, PAGE_TABLES["ja"], slot)
        if (jp_end - jp_start) // RECORD != len(pages):
            raise ValueError(f"slot {slot}: Japanese and English page counts differ")
        pages_ja += [jp_start, len(pages)]
        page_tables.append(
            {
                "file": "ME.PAC",
                "format": "raw",
                "table": f"0x{jp_start - ME_BASE:X}",
                "records": [
                    {
                        "record": k,
                        "lines": [centred(x, shift=shifts.get(x, 0)) for x in page],
                    }
                    for k, page in enumerate(pages)
                ],
            }
        )
    dialogue = []
    for index in [*partners, *(SLOTS + slot for slot in points)]:
        halves = en_lines(program, PARTNER_LINES + PARTNER_RECORD * index)
        first = DIALOGUE_FIRST + 2 * index
        if layout == "whole":
            lines = [box_line(half) for half in halves]
            boxes = [lines, lines]
        else:
            boxes = [[box_line(half), ""] for half in halves]
        for offset, box in enumerate(boxes):
            dialogue.append({"record": first + offset, "lines": box})
    names, lengths = [], []
    for slot in sorted({*points, *partners}):
        address = ARCADE_NAMES + NAME_BYTES * slot
        name = latin(program, address, NAME_BYTES).strip()
        cells = len(split_pairs(name_text(name)))
        lengths.append(
            {
                "file": "MM.BIN",
                "offset": f"0x{MM_NAME_LENGTHS + slot:X}",
                "hex": f"{cells:02x}",
            }
        )
        names.append(
            {
                "file": "MM.BIN",
                "offset": f"0x{MM_NAMES + NAME_BYTES * slot + 2 * NAME_LEAD:X}",
                "cells": NAME_BYTES // 2 - NAME_LEAD,
                "text": name_text(name),
            }
        )
    spec: dict[str, object] = {
        "schema": SCHEMA_V3,
        "description": (
            f"END-010 official arcade English ending: point slot "
            f"{points[0] if len(points) == 1 else points}, partners "
            f"{list(partners)}, dialogue layout {layout}. Generated from the local "
            "arcade ROM; not committed."
        ),
        "tables": [
            {
                "file": "MC13.PAC",
                "table": f"0x{MC13_TABLE:X}",
                "placeholder": "anywhere",
                "records": dialogue,
            },
            *page_tables,
        ],
        "fields": names,
        "patches": lengths,
    }
    targets: dict[str, list[int]] = {
        "pages_ja": pages_ja,  # start, count for each point character
        "dialogue_records": [int(str(r["record"])) for r in dialogue],
        "dialogue_ja": [
            ARCADE_DIALOGUE + RECORD * (int(str(r["record"])) - DIALOGUE_FIRST)
            for r in dialogue
        ],
    }
    return spec, targets


def check_targets(
    program: bytes, targets: dict[str, list[int]], mc13: bytes, me: bytes
) -> dict[str, bool]:
    """Every replaced Saturn record must equal its arcade Japanese record."""
    spans = targets["pages_ja"]
    pages_ok = all(
        program[start + RECORD * k : start + RECORD * (k + 1)]
        == me[start - ME_BASE + RECORD * k : start - ME_BASE + RECORD * (k + 1)]
        for start, count in zip(spans[::2], spans[1::2], strict=True)
        for k in range(count)
    )
    decoded = decode_file(mc13)[1]
    dialogue_ok = all(
        program[a : a + RECORD]
        == decoded[MC13_TABLE + RECORD * r : MC13_TABLE + RECORD * (r + 1)]
        for a, r in zip(
            targets["dialogue_ja"], targets["dialogue_records"], strict=True
        )
    )
    if not (pages_ok and dialogue_ok):
        raise ValueError(
            f"Saturn records differ from arcade: {pages_ok=} {dialogue_ok=}"
        )
    return {"pages_equal_arcade_ja": pages_ok, "dialogue_equal_arcade_ja": dialogue_ok}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument(
        "--point", type=int, nargs="+", default=[9], help="slot(s) (Ryu = 9)"
    )
    parser.add_argument("--partners", type=int, nargs="+", default=[10, 15])
    parser.add_argument(
        "--dialogue-layout", choices=("whole", "split"), default="whole"
    )
    parser.add_argument(
        "--roster", type=Path, help="roster JSON: every slot as point and partner"
    )
    parser.add_argument(
        "--with-win-quotes", action="store_true", help="add the roster win quotes"
    )
    parser.add_argument(
        "--track",
        type=Path,
        default=Path(
            "local/disc_images/mshvsf_saturn_jp/"
            "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
        ),
    )
    parser.add_argument("--out", type=Path, required=True, help="spec path (ignored)")
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    roster = json.loads(args.roster.read_text())["characters"] if args.roster else []
    points = [int(c["slot"]) for c in roster] or args.point
    partners = [int(c["slot"]) for c in roster] or args.partners
    spec, targets = ending_spec(program, points, partners, args.dialogue_layout)
    if args.with_win_quotes:
        if not roster:
            parser.error("--with-win-quotes needs --roster")
        quotes = [s.quotes for s in read_quote_table(program, WIN_QUOTES_EN, SLOTS)]
        tables = spec["tables"]
        assert isinstance(tables, list)
        win_quote_tables = roster_spec(quotes, roster)["tables"]
        assert isinstance(win_quote_tables, list)
        spec["tables"] = win_quote_tables + tables
        spec["description"] = (
            "END-023 combined roster image: M5 official English win quotes (RE-044) "
            "and the roster's official English endings, dialogue layout "
            f"{args.dialogue_layout}. Generated from the local arcade ROM; not "
            "committed."
        )
    with args.track.open("rb") as stream:
        disc = Track(stream, args.track.stat().st_size)
        files = {
            name: disc.read(*find_entry(args.track, f"{name};1"))
            for name in ("MC13.PAC", "ME.PAC")
        }
    checks = check_targets(program, targets, files["MC13.PAC"], files["ME.PAC"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
