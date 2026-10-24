"""Compare arcade win-quote blocks with a PlayStation data file (REF-005).

The PS1 port stores the same 16-bit codes as the arcade, little-endian. Each
arcade English slot block (8 quotes x 100 bytes, `EXP-0029`) is byte-swapped and
searched for in one file of the PS1 disc. The output is offsets and hashes only;
no game text is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.iso9660 import Track, primary_volume, walk
from tools.reference.cps2_text import build_program
from tools.reference.mame_audit import parse_driver
from tools.reference.quote_pairing import EN_ENTRY, pointer

BLOCK = 8 * EN_ENTRY


def swap16(data: bytes) -> bytes:
    swapped = bytearray(len(data))
    swapped[0::2] = data[1::2]
    swapped[1::2] = data[0::2]
    return bytes(swapped)


def compare(
    program: bytes, ps1_file: bytes, table: int, slots: int
) -> list[dict[str, object]]:
    """Locate each arcade slot block, byte-swapped, in the PS1 file."""
    rows: list[dict[str, object]] = []
    for slot in range(slots):
        address = pointer(program, table, slot)
        block = swap16(program[address : address + BLOCK])
        offset = ps1_file.find(block)
        quotes = [
            ps1_file.find(block[q * EN_ENTRY : (q + 1) * EN_ENTRY]) for q in range(8)
        ]
        rows.append(
            {
                "slot": slot,
                "arcade_address": f"0x{address:06x}",
                "block_sha256": hashlib.sha256(block).hexdigest(),
                "ps1_offset": f"0x{offset:05x}" if offset >= 0 else None,
                "quotes_found": sum(q >= 0 for q in quotes),
            }
        )
    return rows


def read_disc_file(track_path: Path, name: str) -> bytes:
    with track_path.open("rb") as stream:
        track = Track(stream, track_path.stat().st_size)
        volume = primary_volume(track)
        root = (int(str(volume["root_lsn"])), int(str(volume["root_size"])))
        for entry in walk(track, *root):
            if entry.path == name:
                return track.read(entry.lsn, entry.size_bytes)
    raise FileNotFoundError(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ps1-track", type=Path, required=True, help="PS1 BIN (read only)"
    )
    parser.add_argument("--ps1-file", default="DAT/SELECT.BIN;1")
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument("--table", type=lambda v: int(v, 0), default=0x20C014)
    parser.add_argument("--slots", type=int, default=26)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    ps1_file = read_disc_file(args.ps1_track, args.ps1_file)
    report = {
        "ps1_file": args.ps1_file,
        "ps1_file_sha256": hashlib.sha256(ps1_file).hexdigest(),
        "rows": compare(program, ps1_file, args.table, args.slots),
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
