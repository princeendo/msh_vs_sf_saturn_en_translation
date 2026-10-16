"""Build a patched copy of a raw memory range and record every byte change.

The input is a raw dump of a region (for example ``wram_l.bin`` from
``tools.memory.mcs_extract``). The tool copies ``[start, end]`` (inclusive
addresses), applies big-endian writes of ``ADDRESS=VALUE`` with a fixed width, and
writes two files: the original and the patched range. Either file can be loaded with
the stock Mednafen memory editor ``L`` command. A JSON manifest records the
address, original bytes, modified bytes, and hashes for each write. Inputs are
never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path


def parse_write(text: str) -> tuple[int, int]:
    address, _, value = text.partition("=")
    if not value:
        raise ValueError(f"expected ADDRESS=VALUE, got {text!r}")
    return int(address, 0), int(value, 0)


def build(
    region: bytes,
    region_base: int,
    start: int,
    end: int,
    writes: Sequence[tuple[int, int]],
    width: int = 2,
) -> tuple[bytes, bytes, list[dict[str, object]]]:
    """Return (original range, patched range, change records)."""
    if not region_base <= start <= end < region_base + len(region):
        raise ValueError("range is outside the region")
    original = region[start - region_base : end - region_base + 1]
    patched = bytearray(original)
    changes: list[dict[str, object]] = []
    seen: set[int] = set()
    for address, value in writes:
        if not (start <= address and address + width - 1 <= end):
            raise ValueError(f"write 0x{address:08X} is outside the range")
        if address % width:
            raise ValueError(f"write 0x{address:08X} is not {width}-byte aligned")
        if address in seen:
            raise ValueError(f"duplicate write 0x{address:08X}")
        if not 0 <= value < 1 << (8 * width):
            raise ValueError(f"value 0x{value:X} does not fit in {width} bytes")
        seen.add(address)
        offset = address - start
        before = bytes(patched[offset : offset + width])
        after = value.to_bytes(width, "big")
        patched[offset : offset + width] = after
        changes.append(
            {
                "address": f"0x{address:08X}",
                "original": before.hex(" "),
                "modified": after.hex(" "),
            }
        )
    return original, bytes(patched), changes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build original and patched copies of a raw memory range."
    )
    parser.add_argument("region", type=Path, help="raw region dump")
    parser.add_argument(
        "--region-base", type=lambda v: int(v, 0), required=True, help="dump base"
    )
    parser.add_argument("--start", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--end", type=lambda v: int(v, 0), required=True)
    parser.add_argument(
        "--write",
        action="append",
        default=[],
        type=parse_write,
        help="ADDRESS=VALUE (big-endian); repeatable",
    )
    parser.add_argument("--width", type=int, default=2, choices=(1, 2, 4))
    parser.add_argument("--out-prefix", type=Path, required=True)
    parser.add_argument("--purpose", default="", help="recorded in the manifest")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.write:
        parser.error("give at least one --write")
    try:
        region = args.region.read_bytes()
        original, patched, changes = build(
            region, args.region_base, args.start, args.end, args.write, args.width
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))

    prefix: Path = args.out_prefix
    original_path = prefix.with_name(prefix.name + "-original.bin")
    patched_path = prefix.with_name(prefix.name + "-patched.bin")
    manifest_path = prefix.with_name(prefix.name + "-manifest.json")
    for path in (original_path, patched_path, manifest_path):
        if path.resolve() == args.region.resolve():
            parser.error(f"output would overwrite the input: {path}")
    prefix.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(original)
    patched_path.write_bytes(patched)
    manifest = {
        "tool": "tools.memory.make_patch",
        "purpose": args.purpose,
        "region": {
            "path": str(args.region),
            "sha256": hashlib.sha256(region).hexdigest(),
            "base": f"0x{args.region_base:08X}",
        },
        "range": {
            "start": f"0x{args.start:08X}",
            "end": f"0x{args.end:08X}",
            "size_bytes": len(original),
            "region_offset_start": f"0x{args.start - args.region_base:08X}",
            "region_offset_end": f"0x{args.end - args.region_base:08X}",
        },
        "original": {
            "file": original_path.name,
            "sha256": hashlib.sha256(original).hexdigest(),
        },
        "patched": {
            "file": patched_path.name,
            "sha256": hashlib.sha256(patched).hexdigest(),
        },
        "width": args.width,
        "changes": changes,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"original: {original_path}\npatched: {patched_path}\nmanifest: {manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
