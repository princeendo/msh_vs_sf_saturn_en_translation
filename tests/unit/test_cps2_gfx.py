from __future__ import annotations

from tools.reference.cps2_gfx import TILE_BYTES, tile_pixels, unshuffle


def test_unshuffle_matches_mame_on_eight_units() -> None:
    units = list(range(8))
    unshuffle(units)
    # len 8: halves of 4 each swap their middle pair, then units 2-3 swap with 4-5.
    assert units == [0, 2, 4, 6, 1, 3, 5, 7]


def test_tile_pixels_reads_planes_and_halves() -> None:
    tile = bytearray(TILE_BYTES)
    tile[3] = 0x80  # plane offset 24 (MSB of the pen), pixel 0 of row 0
    tile[4] = 0x01  # plane offset 0 (LSB), right half: pixel 15 of row 0
    tile[8 + 1] = 0x40  # row 1, plane offset 8, pixel 1
    pixels = tile_pixels(bytes(tile), 0)
    assert pixels[0] == 8
    assert pixels[15] == 1
    assert pixels[16 + 1] == 2
    assert sum(1 for pen in pixels if pen) == 3
