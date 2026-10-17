from __future__ import annotations

import struct
import zlib

import pytest

from tools.common.png import _paeth, decode_png
from tools.memory.mcs_extract import encode_png


def chunk(kind: bytes, body: bytes) -> bytes:
    crc = zlib.crc32(kind + body) & 0xFFFFFFFF
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)


def filtered_png(width: int, rows: list[bytes], kinds: list[int]) -> bytes:
    """Encode RGB rows with the given PNG filter type per row."""
    raw = bytearray()
    previous = bytes(len(rows[0]))
    for row, kind in zip(rows, kinds, strict=True):
        out = bytearray()
        for i, value in enumerate(row):
            left = row[i - 3] if i >= 3 else 0
            up = previous[i]
            corner = previous[i - 3] if i >= 3 else 0
            predictor = [0, left, up, (left + up) // 2, _paeth(left, up, corner)][kind]
            out.append((value - predictor) & 0xFF)
        raw += bytes([kind]) + out
        previous = row
    header = struct.pack(">IIBBBBB", width, len(rows), 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


def test_round_trip_with_project_encoder() -> None:
    rgb = bytes(range(2 * 3 * 3)) + bytes(2 * 3 * 3)
    image = decode_png(encode_png(3, 4, rgb))
    assert (image.width, image.height, image.rgb) == (3, 4, rgb)
    assert image.pixel(1, 0) == (3, 4, 5)


def test_all_filter_types() -> None:
    rows = [bytes((i * 7 + j * 13) & 0xFF for j in range(12)) for i in range(5)]
    image = decode_png(filtered_png(4, rows, [0, 1, 2, 3, 4]))
    assert image.rgb == b"".join(rows)


def test_rejects_unsupported() -> None:
    with pytest.raises(ValueError):
        decode_png(b"not a png")
    header = struct.pack(">IIBBBBB", 1, 1, 16, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IEND", b"")
    with pytest.raises(ValueError):
        decode_png(data)
