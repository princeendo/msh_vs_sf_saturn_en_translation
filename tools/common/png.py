"""Decode 8-bit RGB/RGBA PNG files (non-interlaced) with the standard library.

Mednafen screenshots are 8-bit RGB, non-interlaced. Other formats are rejected
rather than guessed.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {2: 3, 6: 4}


@dataclass(frozen=True)
class Image:
    width: int
    height: int
    rgb: bytes  # width * height * 3, row-major

    def pixel(self, x: int, y: int) -> tuple[int, int, int]:
        offset = (y * self.width + x) * 3
        r, g, b = self.rgb[offset : offset + 3]
        return r, g, b


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def decode_png(data: bytes) -> Image:
    if not data.startswith(SIGNATURE):
        raise ValueError("not a PNG file")
    position = len(SIGNATURE)
    header: tuple[int, ...] | None = None
    compressed = bytearray()
    while position < len(data):
        (length,) = struct.unpack(">I", data[position : position + 4])
        kind = data[position + 4 : position + 8]
        body = data[position + 8 : position + 8 + length]
        position += 12 + length
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            compressed += body
        elif kind == b"IEND":
            break
    if header is None:
        raise ValueError("missing IHDR")
    width, height, depth, color, _, _, interlace = header
    if depth != 8 or color not in CHANNELS or interlace:
        raise ValueError(f"unsupported PNG: depth {depth}, color {color}")
    channels = CHANNELS[color]
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    previous = bytearray(stride)
    rgb = bytearray()
    for row in range(height):
        start = row * (stride + 1)
        filter_type = raw[start]
        line = bytearray(raw[start + 1 : start + 1 + stride])
        for i in range(stride):
            left = line[i - channels] if i >= channels else 0
            up = previous[i]
            corner = previous[i - channels] if i >= channels else 0
            if filter_type == 1:
                line[i] = (line[i] + left) & 0xFF
            elif filter_type == 2:
                line[i] = (line[i] + up) & 0xFF
            elif filter_type == 3:
                line[i] = (line[i] + (left + up) // 2) & 0xFF
            elif filter_type == 4:
                line[i] = (line[i] + _paeth(left, up, corner)) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"bad filter type {filter_type}")
        for x in range(width):
            rgb += line[x * channels : x * channels + 3]
        previous = line
    return Image(width, height, bytes(rgb))
