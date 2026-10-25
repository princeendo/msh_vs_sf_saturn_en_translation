"""Read one character's ending text from an MSHvSF arcade program ROM (END-006).

Layout found in `EXP-0042` (identical in mshvsf, mshvsfu, and mshvsfj):

- four 26-slot pointer tables of ending pages, one per language:
  Japanese ``0x20C14C`` (76-byte records, 2 x 19 cells), then English, Spanish,
  and Portuguese at ``+0x68`` steps (100-byte records, 2 x 25 cells). A slot's
  pages run to the next distinct pointer;
- English partner lines at ``0x22226C``: 52 records of 100 bytes. Record
  ``partner`` is the partner's line and record ``26 + point`` the point
  character's reply; code ``0x0000`` inserts the other character's name.

The Japanese post-boss dialogue has no English counterpart in these sets. The
report contains game text and must go to an ignored path.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.reference.cps2_text import build_program, decode_code
from tools.reference.mame_audit import parse_driver

PAGE_TABLES = {"ja": 0x20C14C, "en": 0x20C1B4, "es": 0x20C21C, "pt": 0x20C284}
RECORD_BYTES = {"ja": 76, "en": 100, "es": 100, "pt": 100}
PARTNER_LINES, PARTNER_RECORD, SLOTS = 0x22226C, 100, 26


def long_at(program: bytes, address: int) -> int:
    return int.from_bytes(program[address : address + 4], "big")


def page_span(program: bytes, table: int, slot: int) -> tuple[int, int]:
    """(start, end) of a slot's pages: up to the next larger pointer in the table."""
    start = long_at(program, table + 4 * slot)
    later = [
        value
        for value in (long_at(program, table + 4 * k) for k in range(SLOTS))
        if value > start
    ]
    return start, min(later) if later else start


def latin(program: bytes, start: int, length: int) -> str:
    codes = (
        int.from_bytes(program[a : a + 2], "big")
        for a in range(start, start + length, 2)
    )
    return "".join(decode_code(c) or f"{{{c:04X}}}" for c in codes)


def records(data: bytes, size: int) -> list[str]:
    return [data[i : i + size].hex() for i in range(0, len(data) - size + 1, size)]


def ending(program: bytes, point: int, partner: int) -> dict[str, object]:
    report: dict[str, object] = {"point_slot": point, "partner_slot": partner}
    for language, table in PAGE_TABLES.items():
        start, end = page_span(program, table, point)
        size = RECORD_BYTES[language]
        entry: dict[str, object] = {
            "address": f"0x{start:06X}",
            "records": (end - start) // size,
            "codes": records(program[start:end], size),
        }
        if language != "ja":
            entry["text"] = latin(program, start, end - start)
        report[f"pages_{language}"] = entry
    lines = {}
    for role, index in (("partner", partner), ("point", SLOTS + point)):
        address = PARTNER_LINES + PARTNER_RECORD * index
        lines[role] = {
            "address": f"0x{address:06X}",
            "text": latin(program, address, PARTNER_RECORD),
        }
    report["partner_lines_en"] = lines
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("archive", type=Path, help="ROM zip (read only)")
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--set", dest="set_name")
    parser.add_argument("--point", type=int, default=9, help="slot (Ryu = 9)")
    parser.add_argument("--partner", type=int, default=10, help="slot (Ken = 10)")
    parser.add_argument("--out", type=Path, required=True, help="ignored path")
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text())
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    report = ending(program, args.point, args.partner)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
