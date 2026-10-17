"""Compose a two-letter pair glyph and write it over a raw font glyph in MEMFIX.PAC.

Pair glyph (quote style, `EXP-0012`/`EXP-0020`):

- Each source glyph's ink is its non-shadow, non-zero pixels.
- Ink is squeezed horizontally from 16 to 8 columns by OR-ing column pairs, and the
  two letters are placed side by side (left in columns 0-7, right in 8-15).
- Ink is drawn as nibble ``1``. A drop shadow ``F`` is added at +1 column, +1 row,
  and +1 diagonal wherever no ink is present, as observed in game glyphs.

The target must be a *raw* glyph (size byte with bit 7 set), so its 128 bytes can
be replaced in place: the font's tables and every other glyph are unchanged.
MEMFIX entry 4 holds the font (`EXP-0022`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.text.font import CELL_BYTES, Font, nibble_at

BODY = 0x1
SHADOW = 0xF


def ink(cell: bytes) -> list[list[bool]]:
    return [
        [nibble_at(cell, row, column) not in (0, SHADOW) for column in range(16)]
        for row in range(16)
    ]


def squeeze(mask: list[list[bool]]) -> list[list[bool]]:
    return [[row[2 * c] or row[2 * c + 1] for c in range(8)] for row in mask]


def compose(left: bytes, right: bytes) -> bytes:
    """Return a 128-byte 4 bpp cell with two squeezed letters and a shadow."""
    a, b = squeeze(ink(left)), squeeze(ink(right))
    body = [a[row] + b[row] for row in range(16)]
    nibbles = [[0] * 16 for _ in range(16)]
    for row in range(16):
        for column in range(16):
            if body[row][column]:
                nibbles[row][column] = BODY
    for row in range(16):
        for column in range(16):
            if not body[row][column]:
                for dr, dc in ((0, 1), (1, 0), (1, 1)):
                    r, c = row - dr, column - dc
                    if r >= 0 and c >= 0 and body[r][c]:
                        nibbles[row][column] = SHADOW
    out = bytearray(CELL_BYTES)
    for row in range(16):
        for column in range(0, 16, 2):
            out[row * 8 + column // 2] = (nibbles[row][column] << 4) | nibbles[row][
                column + 1
            ]
    return bytes(out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("memfix", type=Path, help="source MEMFIX.PAC (read only)")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument("--load-address", type=lambda v: int(v, 0), default=0x0278CF60)
    parser.add_argument("--left", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--right", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--target", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.resolve() == args.memfix.resolve():
        parser.error("output would overwrite the input")
    data = bytearray(args.memfix.read_bytes())
    entry = bytes(data[args.entry_offset : args.entry_offset + args.entry_size])
    font = Font(entry, args.load_address, args.load_address)
    address, size = font.locate(args.target)
    if not size & 0x80:
        parser.error(f"target 0x{args.target:04X} is not a raw glyph")
    cell = compose(font.glyph(args.left)[0], font.glyph(args.right)[0])
    file_offset = args.entry_offset + (address - args.load_address)
    original = bytes(data[file_offset : file_offset + CELL_BYTES])
    data[file_offset : file_offset + CELL_BYTES] = cell
    patched_font = Font(
        bytes(data[args.entry_offset : args.entry_offset + args.entry_size]),
        args.load_address,
        args.load_address,
    )
    if patched_font.glyph(args.target)[0] != cell:
        parser.error("patched font does not return the new glyph")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(bytes(data))
    manifest = {
        "tool": "tools.text.glyph_patch",
        "source_sha256": hashlib.sha256(args.memfix.read_bytes()).hexdigest(),
        "target_code": f"0x{args.target:04X}",
        "left_code": f"0x{args.left:04X}",
        "right_code": f"0x{args.right:04X}",
        "font_address": f"0x{address:08X}",
        "file_offset": f"0x{file_offset:X}",
        "original_bytes": original.hex(),
        "modified_bytes": cell.hex(),
        "output_sha256": hashlib.sha256(bytes(data)).hexdigest(),
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if "bytes" not in k}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
