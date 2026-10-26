from __future__ import annotations

import struct

import pytest

from tools.disc.st2_stream import (
    SECTOR,
    TAG,
    blocks,
    lz_decode,
    miss_payload,
    sections,
    stream_start,
)


def block(literal_bytes: bytes, extra: bytes = b"", size: int | None = None) -> bytes:
    """A graphics block of literals (flag 0x00 per 8 bytes) plus ``extra`` tokens."""
    body = bytearray()
    for i in range(0, len(literal_bytes), 8):
        body.append(0)
        body += literal_bytes[i : i + 8]
    body += extra
    return struct.pack(">II", len(body), size or len(literal_bytes)) + bytes(body)


def test_lz_decode_literals_and_a_copy() -> None:
    # 8 literals, then a flag byte 0x80 whose first token copies 3+2 bytes from 8 back.
    copy = bytes([0x80]) + struct.pack(">H", ((0x1000 - 8) << 4) | 2)
    data = block(b"ABCDEFGH", copy, size=13)
    out, end = lz_decode(data)
    assert out == b"ABCDEFGHABCDE"
    assert end == len(data)


def test_lz_decode_rejects_a_short_block() -> None:
    with pytest.raises(ValueError):
        lz_decode(block(b"ABCDEFGH", size=12))


def test_sections_and_miss_payload() -> None:
    header = struct.pack(">3I", SECTOR, SECTOR * 2, SECTOR) + bytes(SECTOR - 12)
    body = bytes(SECTOR * 4)
    miss = TAG + b"x" * (SECTOR - 4)
    other = b"AUDI" + b"y" * (SECTOR - 4)
    data = header + body + miss + other + miss
    assert sections(data) == [(0x800, 0x800), (0x1000, 0x1000), (0x2000, 0x800)]
    assert stream_start(data) == 0x2800
    assert miss_payload(data) == b"x" * (2 * (SECTOR - 4))


def test_blocks_are_found_on_four_byte_boundaries() -> None:
    # Each block: 8 literals and one 18-byte copy, so it compresses (12 < 26).
    copy = bytes([0x80]) + struct.pack(">H", ((0x1000 - 8) << 4) | 15)
    first = block(b"ABCDEFGH", copy, size=26)
    padded = first + bytes((-len(first)) % 4)
    second = block(b"QRSTUVWX", copy, size=26)
    found = blocks(padded + b"\x00" * 4 + second)
    assert [(b.offset, b.size) for b in found] == [(0, 26), (len(padded) + 4, 26)]
    assert (
        lz_decode(padded + b"\x00" * 4 + second, found[1].offset)[0][:8] == b"QRSTUVWX"
    )
