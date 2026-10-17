"""Unpack and repack the MSHvSF Saturn quote font image (`MEMFIX.PAC` entry 4).

Image layout, measured in `EXP-0023`:

| Offset | Content |
| --- | --- |
| 0x000 | 16-byte header; the last big-endian word is the code count (`0x0C60`) |
| 0x010 | block table: 224 big-endian longs, one per 16 codes, relative to 0x010 |
| 0x390 | size table: one byte per code (0 empty, ``0x80`` raw, else length) |
| 0x1190 | glyph data, in code order |

Blocks below the code count point at the running data offset. Blocks at or above it
hold 0.

Compressed glyphs use the canonical column-run encoding (`tools/text/font.py`).
A glyph whose encoding would exceed 127 bytes, or that was raw, is stored raw.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.text.font import CELL_BYTES, Font

HEADER = 16
BLOCKS = 224
CODES = BLOCKS * 16
SIZE_TABLE = HEADER + BLOCKS * 4
DATA = SIZE_TABLE + CODES
RAW = 0x80


@dataclass(frozen=True)
class Glyph:
    kind: str  # "empty", "raw", or "compressed"
    cell: bytes


def compress(cell: bytes) -> bytes:
    """Canonical column-run encoding (the inverse of ``font.decompress``)."""
    nibbles = [0] * 32
    data = bytearray()
    index = 0
    for column in range(8):
        previous = 0
        for group in range(4):
            bits = 0
            for bit in range(4):
                value = cell[(group * 4 + bit) * 8 + column]
                if value != previous:
                    bits |= 1 << bit
                    data.append(value)
                    previous = value
            nibbles[index] = bits
            index += 1
    mask = 0
    mask_bytes = bytearray()
    for j in range(4):
        for k in range(4):
            value = nibbles[8 * k + j] | (nibbles[8 * k + 4 + j] << 4)
            if value:
                mask |= 1 << (4 * j + k)
                mask_bytes.append(value)
    return mask.to_bytes(2, "big") + bytes(mask_bytes) + bytes(data)


def unpack(image: bytes) -> tuple[bytes, list[Glyph]]:
    """Return (header, glyphs for all 3,584 codes)."""
    font = Font(image, 0, 0)
    glyphs = []
    for code in range(CODES):
        cell, kind = font.glyph(code)
        glyphs.append(Glyph("compressed" if kind == "compressed" else kind, cell))
    return image[:HEADER], glyphs


def pack(header: bytes, glyphs: Sequence[Glyph]) -> bytes:
    """Build a font image from a header and one glyph per code."""
    if len(header) != HEADER or len(glyphs) != CODES:
        raise ValueError("expected a 16-byte header and 3,584 glyphs")
    count = int.from_bytes(header[12:16], "big")
    sizes = bytearray(CODES)
    chunks: list[bytes] = []
    for code, glyph in enumerate(glyphs):
        if glyph.kind == "empty":
            continue
        if len(glyph.cell) != CELL_BYTES:
            raise ValueError(f"code 0x{code:04X}: cell must be 128 bytes")
        encoded = compress(glyph.cell)
        if glyph.kind == "raw" or len(encoded) > 0x7F:
            sizes[code] = RAW
            chunks.append(glyph.cell)
        else:
            sizes[code] = len(encoded)
            chunks.append(encoded)
    table = bytearray(BLOCKS * 4)
    position = SIZE_TABLE + CODES - HEADER
    for block in range(BLOCKS):
        if block * 16 < count:
            table[block * 4 : block * 4 + 4] = position.to_bytes(4, "big")
        for code in range(block * 16, block * 16 + 16):
            position += CELL_BYTES if sizes[code] == RAW else sizes[code]
    return bytes(header) + bytes(table) + bytes(sizes) + b"".join(chunks)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Round-trip the quote font image.")
    parser.add_argument("memfix", type=Path, help="MEMFIX.PAC (read only)")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    args = parser.parse_args(argv)
    data = args.memfix.read_bytes()
    image = data[args.entry_offset : args.entry_offset + args.entry_size]
    header, glyphs = unpack(image)
    rebuilt = pack(header, glyphs)
    kinds: dict[str, int] = {}
    for glyph in glyphs:
        kinds[glyph.kind] = kinds.get(glyph.kind, 0) + 1
    report = {
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
        "identical": rebuilt == image,
        "size": len(image),
        "rebuilt_size": len(rebuilt),
        "kinds": kinds,
        "code_count": f"0x{int.from_bytes(header[12:16], 'big'):04X}",
    }
    print(json.dumps(report, indent=2))
    return 0 if rebuilt == image else 1


if __name__ == "__main__":
    raise SystemExit(main())
