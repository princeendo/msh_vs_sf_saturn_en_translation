"""Find win-quote record tables in decoded data and census their glyph codes.

A candidate record is 38 big-endian 16-bit words (76 bytes) where every word is:

- ``0x0020`` (blank cell);
- ``0x0000`` (name placeholder, `EXP-0015`); or
- a code with a non-empty glyph in the font.

At least ``MIN_TEXT`` cells must be text, and at least ``MIN_BLANK`` blank. A
table is a run of at least ``MIN_RECORDS`` consecutive records. The shape comes
from Ryu's confirmed table (`EXP-0013`, `EXP-0015`). A match is a structural
candidate; only a display test confirms it is a quote table.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.text.font_pack import unpack

RECORD = 76
CELLS = 38
BLANK = 0x0020
PLACEHOLDER = 0x0000
MIN_TEXT = 3
MIN_BLANK = 1
MIN_RECORDS = 4


def valid_codes(font_image: bytes) -> set[int]:
    _, glyphs = unpack(font_image)
    return {code for code, glyph in enumerate(glyphs) if glyph.kind != "empty"}


def is_record(data: bytes, offset: int, codes: set[int]) -> bool:
    text = blank = 0
    for i in range(CELLS):
        word = int.from_bytes(data[offset + 2 * i : offset + 2 * i + 2], "big")
        if word == BLANK:
            blank += 1
        elif word == PLACEHOLDER or word in codes:
            text += 1
        else:
            return False
    return text >= MIN_TEXT and blank >= MIN_BLANK


def find_tables(data: bytes, codes: set[int]) -> list[tuple[int, int]]:
    """Return (offset, record count) for each maximal run of records."""
    tables: list[tuple[int, int]] = []
    offset = 0
    while offset + RECORD <= len(data):
        count = 0
        while offset + (count + 1) * RECORD <= len(data) and is_record(
            data, offset + count * RECORD, codes
        ):
            count += 1
        if count >= MIN_RECORDS:
            tables.append((offset, count))
            offset += count * RECORD
        else:
            offset += 2
    return tables


def table_codes(data: bytes, offset: int, count: int) -> set[int]:
    words = (
        int.from_bytes(data[offset + 2 * i : offset + 2 * i + 2], "big")
        for i in range(count * CELLS)
    )
    return {word for word in words if word not in (BLANK, PLACEHOLDER)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", type=Path, nargs="+", help="decoded data files")
    parser.add_argument("--memfix", type=Path, required=True)
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument("--out", type=Path, help="write the JSON report here")
    args = parser.parse_args(argv)
    memfix = args.memfix.read_bytes()
    codes = valid_codes(memfix[args.entry_offset : args.entry_offset + args.entry_size])
    report: dict[str, object] = {"files": {}}
    used: set[int] = set()
    files: dict[str, object] = {}
    for path in args.files:
        data = path.read_bytes()
        tables = find_tables(data, codes)
        file_codes: set[int] = set()
        for offset, count in tables:
            file_codes |= table_codes(data, offset, count)
        used |= file_codes
        files[path.name] = {
            "tables": [{"offset": f"0x{o:X}", "records": c} for o, c in tables],
            "distinct_codes": len(file_codes),
        }
    report["files"] = files
    report["union_distinct_codes"] = len(used)
    report["codes"] = [f"0x{c:04X}" for c in sorted(used)]
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text + "\n")
    summary = {
        name: [(t["offset"], t["records"]) for t in info["tables"]]  # type: ignore[index]
        for name, info in files.items()
    }
    print(json.dumps({"tables": summary, "union_distinct_codes": len(used)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
