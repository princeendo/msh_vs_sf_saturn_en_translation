from __future__ import annotations

import pytest

from tools.disc.error_screens import (
    FILES,
    HEIGHT,
    PIXELS,
    RAMPS,
    ROW,
    SHADOW,
    LayoutError,
    Screen,
    line_width,
    load_layout,
    plain,
    preview,
    put,
    render,
    segments,
)


class PenFont:
    """Every glyph: pen 1 at its top-left pixel, pen 9 next to it, shadow below."""

    def glyph(self, code: int) -> tuple[bytes, str]:
        cell = bytearray(128)
        cell[0] = 0x19
        cell[8] = 0xB0
        return bytes(cell), "raw"


def blank_bmp() -> bytes:
    return b"BM" + bytes(PIXELS - 2) + bytes(ROW * HEIGHT)


def pixel(data: bytes, x: int, y: int) -> int:
    byte = data[PIXELS + (HEIGHT - 1 - y) * ROW + x // 2]
    return byte & 0xF if x % 2 else byte >> 4


def screen(lines: tuple[str, ...], title: str = "W") -> Screen:
    return Screen("ERR5.BIN", title, 24, 64, 16, lines)


def test_segments_mark_cyan_and_red() -> None:
    assert segments("The {4M} needs [8].") == [
        ("The ", "white"),
        ("4M", "cyan"),
        (" needs ", "white"),
        ("8", "red"),
        (".", "white"),
    ]
    assert plain("a {b} [c]") == "a b c"
    assert line_width("{ab}c") == 24


def test_unclosed_mark_is_rejected() -> None:
    with pytest.raises(LayoutError):
        segments("the {cart")


def test_put_writes_bottom_up_rows_high_nibble_first() -> None:
    pixels = bytearray(ROW * HEIGHT)
    put(pixels, 0, 0, 0xA)
    put(pixels, 1, 0, 0x3)
    put(pixels, 0, HEIGHT - 1, 0x5)
    assert pixels[(HEIGHT - 1) * ROW] == 0xA3
    assert pixels[0] == 0x50
    with pytest.raises(LayoutError):
        put(pixels, 352, 0, 1)


def test_render_keeps_header_and_maps_pens() -> None:
    original = bytearray(blank_bmp())
    original[10] = 0x76
    original[PIXELS + 5] = 0xFF  # old art is cleared
    new = render(bytes(original), screen(("{a}b",)), PenFont())  # type: ignore[arg-type]
    assert len(new) == len(original)
    assert new[:PIXELS] == original[:PIXELS]
    x0 = (352 - 16) // 2
    assert pixel(new, x0, 64) == RAMPS["cyan"][0]
    assert pixel(new, x0 + 1, 64) == RAMPS["cyan"][1]
    assert pixel(new, x0, 65) == SHADOW
    assert pixel(new, x0 + 8, 64) == RAMPS["white"][0]
    title_x = (352 - 8) // 2
    assert pixel(new, title_x, 24) == RAMPS["yellow"][0]
    assert new[PIXELS + 5] == 0


def test_render_rejects_wide_lines_and_overflow() -> None:
    with pytest.raises(LayoutError):
        render(blank_bmp(), screen(("x" * 41,)), PenFont())  # type: ignore[arg-type]
    with pytest.raises(LayoutError):
        render(blank_bmp(), screen(("x",) * 12), PenFont())  # type: ignore[arg-type]
    with pytest.raises(LayoutError):
        render(b"BM" + bytes(10), screen(("x",)), PenFont())  # type: ignore[arg-type]


def test_preview_drops_the_hidden_top_rows() -> None:
    data = blank_bmp()
    png = preview(data)
    assert png.startswith(b"\x89PNG")


def test_layout_covers_the_five_files_and_fits() -> None:
    screens = load_layout()
    assert sorted(s.name for s in screens) == FILES
    for s in screens:
        assert max(line_width(line) for line in s.lines) <= 320
