"""Generate a caption spec from the official arcade English (TR-001).

Each Saturn record ``k`` gets arcade English entry ``remap[k]`` for the character's
slot: the line the arcade shows in the same selection state (`EXP-0031`; the
policy is in `data/translations/README.md`). The text is read from the user's
local arcade ROM at build time, so the repository never stores it. Write the spec
to an ignored path.

Each line keeps the arcade's own line break. It is centred in whole blank cells
(two spaces = one cell), so pairs never straddle the padding.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.reference.cps2_text import build_program, read_quote_table
from tools.reference.mame_audit import parse_driver
from tools.reference.quote_pairing import OBSERVED_REMAP
from tools.text.caption_compiler import LINE_CELLS
from tools.text.pair_font import char_code


def centred(text: str, cells: int = LINE_CELLS, shift: int = 0) -> str:
    """Pad ``text`` with whole blank cells so it sits centred in ``cells``.

    ``shift`` = 1 adds one leading space inside the first cell, which changes how
    the line splits into pairs (``best_shifts``).
    """
    for char in text:
        char_code(char)  # raises ValueError for characters without a glyph
    body = " " * shift + text
    used = (len(body) + 1) // 2
    if used > cells:
        raise ValueError(f"{text!r} needs {used} cells (max {cells})")
    return "  " * ((cells - used) // 2) + body


def line_pairs(text: str, shift: int) -> set[str]:
    body = " " * shift + text
    if len(body) % 2:
        body += " "
    return {body[i : i + 2] for i in range(0, len(body), 2)} - {"  "}


def best_shifts(lines: Sequence[str], cells: int = LINE_CELLS) -> dict[str, int]:
    """Choose a 0/1 shift per distinct line to reduce distinct pairs (greedy).

    Lines are visited in sorted order, and passes repeat until no line changes,
    so the result is deterministic.
    """
    unique = sorted(set(lines))
    choice = dict.fromkeys(unique, 0)

    def fits(line: str, shift: int) -> bool:
        return (len(line) + shift + 1) // 2 <= cells

    changed = True
    while changed:
        changed = False
        for line in unique:
            others: set[str] = set()
            for other in unique:
                if other != line:
                    others |= line_pairs(other, choice[other])
            options = [s for s in (0, 1) if fits(line, s)]
            best = min(options, key=lambda s: (len(others | line_pairs(line, s)), s))
            if best != choice[line]:
                choice[line] = best
                changed = True
    return choice


def spec_records(
    entries: Sequence[Sequence[str]],
    remap: Sequence[int] = OBSERVED_REMAP,
    shifts: dict[str, int] | None = None,
) -> list[dict[str, object]]:
    """Caption-spec records: record ``k`` shows ``entries[remap[k]]``."""
    chosen = shifts or {}
    return [
        {
            "record": k,
            "lines": [
                centred(line.strip(), shift=chosen.get(line.strip(), 0))
                for line in entries[remap[k]]
            ],
        }
        for k in range(len(remap))
    ]


def roster_spec(
    slots: Sequence[Sequence[Sequence[str]]], roster: Sequence[dict[str, object]]
) -> dict[str, object]:
    """Schema-v2 spec: one table per roster character, in roster order.

    ``slots[s]`` holds slot ``s``'s English quotes (lines). Placeholders are never
    emitted, because the roster's policy drops them (`RE-042`).
    """
    used = [
        line.strip()
        for entry in roster
        for quote in slots[int(str(entry["slot"]))]
        for line in quote
        if line.strip()
    ]
    shifts = best_shifts(used)
    tables = [
        {
            "file": str(entry["file"]),
            "table": str(entry["table"]),
            "records": spec_records(slots[int(str(entry["slot"]))], shifts=shifts),
        }
        for entry in roster
    ]
    return {
        "schema": "mshvsf-captions/2",
        "description": (
            "M5 roster official arcade English (RE-044): record k = entry remap[k] "
            "of each character's slot (EXP-0031). Generated from the local arcade "
            "ROM; not committed."
        ),
        "tables": tables,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument("--quote-table", type=lambda v: int(v, 0), default=0x20C014)
    parser.add_argument("--slot", type=int, default=9, help="arcade slot (Ryu = 9)")
    parser.add_argument(
        "--roster", type=Path, help="roster JSON: emit a schema-v2 spec for all of it"
    )
    parser.add_argument("--out", type=Path, required=True, help="spec path (ignored)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    if args.roster:
        roster = json.loads(args.roster.read_text())["characters"]
        quotes = [s.quotes for s in read_quote_table(program, args.quote_table, 26)]
        spec = roster_spec(quotes, roster)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {args.out}: {len(roster)} tables")
        return 0
    slot = read_quote_table(program, args.quote_table, args.slot + 1)[args.slot]
    records = spec_records(slot.quotes)
    spec = {
        "schema": "mshvsf-captions/1",
        "description": (
            f"TR-001 official arcade English, slot {args.slot}, record k = entry "
            "remap[k] (EXP-0031). Generated from the local arcade ROM; not committed."
        ),
        "records": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
