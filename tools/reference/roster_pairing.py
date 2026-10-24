"""Record official-English pairing for every roster character (RE-042).

For each character in ``data/text/m5_roster.json`` this does four things:

- Pair the Saturn table with the arcade slot (``quote_pairing.pair``): table
  identity, plus English entry ``remap[k]`` for record ``k``.
- Compare that slot's English block across arcade sets (US, EU, JP builds).
- Look up the PS1 result from ``references/mshvsf/ps1_us/arcade_en_comparison.json``
  (`EXP-0032`).
- List every ``0000`` partner-name placeholder cell (record, cell).

The output is metadata and hashes only.
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
from tools.reference.quote_pairing import EN_ENTRY, JP_RECORD, pair, pointer

RECORDS = 16
CELLS = JP_RECORD // 2
PLACEHOLDER = 0x0000


def placeholders(table: bytes) -> list[dict[str, int]]:
    """Every ``0000`` cell in a 16-record table, as record and cell numbers."""
    found = []
    for record in range(len(table) // JP_RECORD):
        for cell in range(CELLS):
            start = record * JP_RECORD + 2 * cell
            if int.from_bytes(table[start : start + 2], "big") == PLACEHOLDER:
                found.append({"record": record, "cell": cell})
    return found


def english_block(program: bytes, table: int, slot: int) -> bytes:
    start = pointer(program, table, slot)
    return program[start : start + 8 * EN_ENTRY]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=Path("data/text/m5_roster.json"))
    parser.add_argument("--saturn-dir", type=Path, required=True, help="MC*.PAC folder")
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archives", type=Path, nargs="+", required=True)
    parser.add_argument(
        "--ps1-comparison",
        type=Path,
        default=Path("references/mshvsf/ps1_us/arcade_en_comparison.json"),
    )
    parser.add_argument("--jp-table", type=lambda v: int(v, 0), default=0x20BFAC)
    parser.add_argument("--en-table", type=lambda v: int(v, 0), default=0x20C014)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    roster = json.loads(args.roster.read_text())["characters"]
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    programs = {a.stem: build_program(a, sets[a.stem]) for a in args.archives}
    primary = programs[args.archives[0].stem]
    ps1_rows = {
        row["slot"]: row for row in json.loads(args.ps1_comparison.read_text())["rows"]
    }
    characters = []
    for entry in roster:
        slot, offset = int(entry["slot"]), int(entry["table"], 16)
        decoded = decode_file((args.saturn_dir / entry["file"]).read_bytes())[1]
        table = decoded[offset : offset + RECORDS * JP_RECORD]
        report = pair(table, primary, slot, args.jp_table, args.en_table)
        blocks = {
            name: english_block(p, args.en_table, slot) for name, p in programs.items()
        }
        digests = {name: hashlib.sha256(b).hexdigest() for name, b in blocks.items()}
        ps1 = ps1_rows.get(slot, {})
        characters.append(
            {
                "slot": slot,
                "arcade_name": entry["arcade_name"],
                "file": entry["file"],
                "table": entry["table"],
                "tables_identical": report["tables_identical"],
                "arcade_en_base": report["arcade_en_base"],
                "remap": report["remap"],
                "en_block_sha256": digests,
                "en_identical_across_sets": len(set(digests.values())) == 1,
                "ps1_block_found": ps1.get("ps1_offset") is not None,
                "ps1_offset": ps1.get("ps1_offset"),
                "placeholders": placeholders(table),
                "rows": report["rows"],
            }
        )
    print(
        json.dumps({"arcade_sets": list(programs), "characters": characters}, indent=1)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
