"""Pair Saturn win-quote records with arcade English entries by game logic.

The arcade selects a 16-way index. Japanese mode shows Japanese record `k`; other
languages show English entry `remap[k]`, with the remap table read in `EXP-0031`.
This tool checks that the Saturn table is byte-identical to the arcade Japanese
table for the same slot, then writes the pairing as metadata and SHA-256 hashes.
No game text is written.
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

JP_RECORD = 76  # 2 lines x 19 codes x 2 bytes
EN_ENTRY = 100  # 2 lines x 25 codes x 2 bytes
OBSERVED_REMAP = (0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7)


def pointer(program: bytes, table: int, slot: int) -> int:
    entry = table + 4 * slot
    return int.from_bytes(program[entry : entry + 4], "big")


def pair(
    saturn_table: bytes,
    program: bytes,
    slot: int,
    jp_table: int,
    en_table: int,
    remap: Sequence[int] = OBSERVED_REMAP,
) -> dict[str, object]:
    """Return the pairing report for one character slot."""
    records = len(saturn_table) // JP_RECORD
    jp_base = pointer(program, jp_table, slot)
    en_base = pointer(program, en_table, slot)
    arcade_jp = program[jp_base : jp_base + records * JP_RECORD]
    rows = []
    for k in range(records):
        saturn = saturn_table[k * JP_RECORD : (k + 1) * JP_RECORD]
        en_address = en_base + EN_ENTRY * remap[k]
        en = program[en_address : en_address + EN_ENTRY]
        rows.append(
            {
                "saturn_record": k,
                "arcade_jp_address": f"0x{jp_base + k * JP_RECORD:06x}",
                "arcade_jp_identical": saturn
                == arcade_jp[k * JP_RECORD : (k + 1) * JP_RECORD],
                "jp_codes_sha256": hashlib.sha256(saturn).hexdigest(),
                "arcade_en_entry": remap[k],
                "arcade_en_address": f"0x{en_address:06x}",
                "en_codes_sha256": hashlib.sha256(en).hexdigest(),
            }
        )
    return {
        "slot": slot,
        "arcade_jp_base": f"0x{jp_base:06x}",
        "arcade_en_base": f"0x{en_base:06x}",
        "remap": list(remap),
        "tables_identical": saturn_table == arcade_jp,
        "rows": rows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saturn-pac", type=Path, required=True, help="e.g. MC09.PAC")
    parser.add_argument("--saturn-table", type=lambda v: int(v, 0), default=0x91AC)
    parser.add_argument("--records", type=int, default=16)
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument("--slot", type=int, default=9)
    parser.add_argument("--jp-table", type=lambda v: int(v, 0), default=0x20BFAC)
    parser.add_argument("--en-table", type=lambda v: int(v, 0), default=0x20C014)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    decoded = decode_file(args.saturn_pac.read_bytes())[1]
    start = args.saturn_table
    saturn_table = decoded[start : start + args.records * JP_RECORD]
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    report = pair(saturn_table, program, args.slot, args.jp_table, args.en_table)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
