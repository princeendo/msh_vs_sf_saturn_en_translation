"""Census Saturn quote files against the arcade's Japanese character slots (RE-041).

For each decoded Saturn file, two things are checked:

- The Saturn-side record tables, found by ``quote_census.find_tables``.
- For every arcade Japanese slot (pointer table ``0x20BFAC``, 16 x 76-byte
  blocks; `EXP-0031`), whether its whole block, or any of its records, occurs
  byte-identically in the file.

Each Saturn table is then linked to the arcade slots whose records lie inside
it. The output is metadata only: offsets, counts, slots, and hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.pac_lzss import decode_file
from tools.reference.cps2_text import build_program
from tools.reference.mame_audit import parse_driver
from tools.reference.quote_pairing import JP_RECORD, pointer
from tools.text.quote_census import find_tables, valid_codes

RECORDS = 16


def slot_blocks(program: bytes, table: int, slots: int) -> list[bytes]:
    """The 16-record Japanese block of each arcade slot."""
    blocks = []
    for slot in range(slots):
        start = pointer(program, table, slot)
        blocks.append(program[start : start + RECORDS * JP_RECORD])
    return blocks


def record_hits(data: bytes, block: bytes) -> list[int]:
    """Offset in ``data`` of each record of ``block`` (-1 if absent)."""
    return [
        data.find(block[r * JP_RECORD : (r + 1) * JP_RECORD]) for r in range(RECORDS)
    ]


SLACK = 2  # find_tables may start a record one word early (EXP-0028, 0xA59A)


def classify(tables: list[dict[str, object]], blocks: dict[str, int]) -> str:
    """Classify a file structurally (character roles are `RE-043`'s job).

    - ``ordinary``: one whole 16-record slot block (several arcade slots may share
      it), and every Saturn table lies within it, up to ``SLACK`` bytes.
    - ``irregular``: at least one whole block, plus other blocks or tables.
    - ``partial``: only some records of a slot occur.
    - ``unmatched``: no slot records occur.
    """
    offsets = set(blocks.values())
    if len(offsets) == 1:
        start = offsets.pop()
        end = start + RECORDS * JP_RECORD
        if tables and all(within(t, start, end) for t in tables):
            return "ordinary"
    if blocks:
        return "irregular"
    if any(t["slots"] for t in tables):
        return "partial"
    return "unmatched"


def within(table: dict[str, object], start: int, end: int) -> bool:
    offset = int(str(table["offset"]), 16)
    last = offset + int(str(table["records"])) * JP_RECORD
    return offset >= start - SLACK and last <= end + SLACK


def census_file(
    data: bytes, codes: set[int], blocks: Sequence[bytes]
) -> dict[str, object]:
    """Link each Saturn table in ``data`` to the arcade slots it contains."""
    hits = [record_hits(data, block) for block in blocks]
    whole = {
        str(slot): offset
        for slot, block in enumerate(blocks)
        if (offset := data.find(block)) >= 0
    }
    tables: list[dict[str, object]] = []
    for offset, count in find_tables(data, codes):
        end = offset + count * JP_RECORD
        slots: dict[str, int] = {}
        for slot, offsets in enumerate(hits):
            inside = sum(offset - JP_RECORD < h < end for h in offsets if h >= 0)
            if inside:
                slots[str(slot)] = inside
        tables.append(
            {
                "offset": f"0x{offset:04X}",
                "records": count,
                "sha256": hashlib.sha256(data[offset:end]).hexdigest(),
                "slots": slots,
            }
        )
    partial = {
        str(slot): sum(h >= 0 for h in offsets)
        for slot, offsets in enumerate(hits)
        if str(slot) not in whole and any(h >= 0 for h in offsets)
    }
    return {
        "whole_slot_blocks": {s: f"0x{o:04X}" for s, o in whole.items()},
        "partial_slots": partial,
        "tables": tables,
        "class": classify(tables, whole),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="+", help="Saturn MC*.PAC files")
    parser.add_argument("--memfix", type=Path, required=True, help="MEMFIX.PAC")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument("--jp-table", type=lambda v: int(v, 0), default=0x20BFAC)
    parser.add_argument("--slots", type=int, default=26)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    font = args.memfix.read_bytes()[
        args.entry_offset : args.entry_offset + args.entry_size
    ]
    codes = valid_codes(font)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    blocks = slot_blocks(program, args.jp_table, args.slots)
    report: dict[str, object] = {"arcade_set": args.set_name or args.archive.stem}
    files: dict[str, object] = {}
    for path in args.files:
        raw = path.read_bytes()
        decoded = decode_file(raw)[1]
        entry = census_file(decoded, codes, blocks)
        entry["file_sha256"] = hashlib.sha256(raw).hexdigest()
        files[path.name] = entry
    report["files"] = files
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
