from __future__ import annotations

import random

import pytest

from tools.text.font import CELL_BYTES, decompress
from tools.text.font_pack import CODES, RAW, Glyph, compress, pack, unpack


def letter(seed: int) -> bytes:
    rng = random.Random(seed)
    cell = bytearray(CELL_BYTES)
    for row in range(2, 13):
        cell[row * 8 + rng.randrange(1, 6)] = rng.choice([0x1F, 0x11, 0x10])
    return bytes(cell)


def noisy() -> bytes:
    rng = random.Random(9)
    return bytes(rng.randrange(256) for _ in range(CELL_BYTES))


def header(count: int) -> bytes:
    return bytes(12) + count.to_bytes(4, "big")


def test_compress_is_inverse_of_decompress() -> None:
    for seed in range(20):
        cell = letter(seed)
        assert decompress(compress(cell)) == cell
    assert compress(bytes(CELL_BYTES)) == b"\x00\x00"


def test_pack_unpack_round_trip_with_raw_policy() -> None:
    glyphs = [Glyph("empty", bytes(CELL_BYTES))] * CODES
    glyphs = list(glyphs)
    glyphs[0x41] = Glyph("compressed", letter(1))
    glyphs[0x42] = Glyph("raw", letter(2))
    glyphs[0x43] = Glyph("compressed", noisy())  # too large: stored raw
    image = pack(header(0x50), glyphs)

    head, back = unpack(image)

    assert head == header(0x50)
    assert back[0x41] == glyphs[0x41]
    assert back[0x42] == glyphs[0x42]
    assert back[0x43] == Glyph("raw", noisy())
    assert image[0x390 + 0x43] == RAW
    assert pack(head, back) == image


def test_blocks_beyond_code_count_are_zero() -> None:
    glyphs = [Glyph("empty", bytes(CELL_BYTES))] * CODES
    image = pack(header(0x20), list(glyphs))
    table = [int.from_bytes(image[16 + 4 * b : 20 + 4 * b], "big") for b in range(224)]
    assert table[0] == table[1] != 0
    assert all(value == 0 for value in table[2:])


def test_pack_rejects_bad_input() -> None:
    with pytest.raises(ValueError):
        pack(bytes(15), [])
    glyphs = [Glyph("empty", bytes(CELL_BYTES))] * CODES
    bad = list(glyphs)
    bad[5] = Glyph("compressed", b"short")
    with pytest.raises(ValueError):
        pack(header(0x10), bad)
