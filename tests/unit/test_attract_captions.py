from __future__ import annotations

import struct

import pytest

from tools.disc.attract_captions import (
    BANNER,
    GREY,
    RED,
    LayoutError,
    Line,
    banner_code,
    char_tile,
    derive_cells,
    diff_patches,
    draw,
    line_width,
    overwrite_block,
    paint,
    recolour,
)
from tools.disc.st2_encode import lz_encode
from tools.disc.st2_stream import lz_decode


class SolidFont:
    """Every banner cell is a solid 16x16 block of colour 3."""

    def glyph(self, code: int) -> tuple[bytes, str]:
        return bytes([0x33]) * 128, "raw"


def test_banner_codes_follow_the_letter_grid() -> None:
    assert banner_code("A") == 0x2E0 + 2 * 2  # i = 2
    assert banner_code("G") == 0x2E0 + 0x20  # i = 8: next row
    assert banner_code("!") == 0x348
    with pytest.raises(LayoutError):
        banner_code("a")


def test_line_width_counts_advances_and_the_last_glyph() -> None:
    assert line_width("AB") == 24 + 32
    assert line_width("A!") == 24 + 18
    assert line_width("A B", advance=22) == 22 + 16 + 32


def test_draw_centres_a_line() -> None:
    canvas = draw(SolidFont(), [Line("A", 100, 10)])  # type: ignore[arg-type]
    xs = {x for x, _ in canvas}
    ys = {y for _, y in canvas}
    assert (min(xs), max(xs)) == (84, 115)  # width 32 centred on 100
    assert (min(ys), max(ys)) == (10, 41)
    assert set(canvas.values()) == {3}


def test_char_tile_shifts_colours_and_flips() -> None:
    canvas = {(16 + 0, 0): 5}  # page cell (0, 1), its top-left pixel
    plain = char_tile(canvas, 1, 0)
    assert plain[0] == 0x61  # colour 5 drawn as 6, then background 1
    assert set(plain[1:]) == {0x11}
    flipped = char_tile(canvas, 1, 0x4000)  # h-flip: the pixel lands top-right
    assert flipped[32 + 3] == 0x16


def test_paint_refuses_conflicting_shared_characters() -> None:
    canvas = {(0, 0): 2}
    cells = {0: (0x100, 0), 1: (0x100, 0)}  # one char at two cells
    with pytest.raises(LayoutError):
        paint(canvas, cells)
    blank = paint({}, cells)
    assert blank == {0x100: bytes([0x11]) * 128}


def test_paint_refuses_text_on_background_cells() -> None:
    with pytest.raises(LayoutError):
        paint({(40, 0): 2}, {0: (0x100, 0)})  # (40, 0) is cell 2


def test_recolour_changes_the_caption_slot_ramp_loads() -> None:
    words = [0] * 0x800
    words[0x600:0x610] = GREY
    words[0x610:0x620] = RED
    load = b"\x00\x00\x08\x00" + struct.pack(">2048H", *words)
    other = load.replace(struct.pack(">H", 0xF333), struct.pack(">H", 0xF334))
    script = b"\x01" + other + load * 5
    new, changed = recolour(script)
    starts = [1 + len(other) + k * len(load) for k in range(5)]
    assert changed == [starts[0], starts[2], starts[4]]
    for start in starts:
        grey = struct.unpack_from(">16H", new, start + 4 + 2 * 0x600)
        red = struct.unpack_from(">16H", new, start + 4 + 2 * 0x610)
        if start in changed:
            assert grey[:2] == GREY[:2] and grey[2:] == BANNER
            assert red[:2] == RED[:2] and red[2:] == BANNER
        else:
            assert grey == GREY and red == RED
    assert new[: starts[0]] == script[: starts[0]]
    with pytest.raises(LayoutError):
        recolour(b"\x01" + load * 4)


def test_overwrite_block_keeps_the_header_size_when_shorter() -> None:
    data = bytes(range(256)) * 4
    original = lz_encode(bytes(1024)) + b"\xaa" * 16  # tiny block
    with pytest.raises(LayoutError):
        overwrite_block(original, 0, data)  # does not fit
    roomy = lz_encode(data) + b"tail"
    out = overwrite_block(roomy, 0, bytes(1024))
    assert out[:4] == roomy[:4] and out.endswith(b"tail")
    assert lz_decode(out, 0)[0] == bytes(1024)


def test_overwrite_block_grows_into_zero_padding_up_to_the_limit() -> None:
    data = bytes(range(256)) * 4
    small = lz_encode(bytes(1024))
    original = small + bytes(2048)
    out = overwrite_block(original, 0, data, limit=len(original) - 8)
    assert struct.unpack_from(">I", out)[0] == len(lz_encode(data)) - 8
    assert lz_decode(out, 0)[0] == data


def test_diff_patches_merge_nearby_changes() -> None:
    old = bytes(64)
    new = bytearray(old)
    new[2] = new[10] = new[40] = 1
    patches = diff_patches("X.ST2", old, bytes(new))
    assert [(p["offset"], len(p["hex"]) // 2) for p in patches] == [
        ("0x2", 9),
        ("0x28", 1),
    ]
    assert patches[0]["expect"] == "00" * 9


def test_derive_cells_skips_background_and_reads_flips() -> None:
    words = [0x0000_0010] * 1024  # background char 0x10 everywhere
    words[1 * 32 + 2] = 0x4000_0123  # h-flip, char 0x123
    cells = derive_cells(words, (16, 16))
    assert cells == {"1,2": "123:4000"}
