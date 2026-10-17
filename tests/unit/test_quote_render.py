from __future__ import annotations

from tests.unit.test_font_pack import header, letter
from tools.common.png import Image, decode_png
from tools.text.font import CELL_BYTES, Font
from tools.text.font_pack import CODES, Glyph, pack
from tools.text.quote_render import (
    BODY,
    ORIGIN,
    RECORD,
    TABLE,
    body_mask,
    match,
    nibbles,
    parse_records,
    record_codes,
    render,
    summary,
)

GLYPH_CODES = [0x0801 + i for i in range(6)]


def font() -> Font:
    glyphs = [Glyph("empty", bytes(CELL_BYTES))] * CODES
    glyphs = list(glyphs)
    for i, code in enumerate(GLYPH_CODES):
        glyphs[code] = Glyph("compressed", letter(i))
    return Font(pack(header(0x0C60), glyphs), 0, 0)


def table(records: list[list[int]]) -> bytes:
    data = bytearray(TABLE + 16 * RECORD)
    for index, codes in enumerate(records):
        for cell, code in enumerate(codes):
            offset = TABLE + index * RECORD + 2 * cell
            data[offset : offset + 2] = code.to_bytes(2, "big")
    return bytes(data)


def records() -> list[list[int]]:
    out = []
    for index in range(16):
        codes = [0x0020] * 38
        for cell in range(4):
            codes[cell] = GLYPH_CODES[(index + cell) % 6]
            codes[19 + cell] = GLYPH_CODES[(index // 6 + cell) % 6]
        out.append(codes)
    out[0][5] = 0x0000
    return out


def screenshot(mask: set[tuple[int, int]], shift: tuple[int, int]) -> Image:
    width, height = 352, 240
    rgb = bytearray(width * height * 3)
    for x, y in mask:
        offset = ((y + shift[1]) * width + x + shift[0]) * 3
        rgb[offset : offset + 3] = b"\xf0\xf0\xf0"
    return Image(width, height, bytes(rgb))


def test_record_codes_and_summary() -> None:
    data = table(records())
    assert record_codes(data, 3) == records()[3]
    rows = summary(data)
    assert rows[0]["placeholder_cells"] == [5]
    assert rows[1]["placeholder_cells"] == []
    assert rows[1]["line_lengths"] == [4, 4]


def test_layout_places_cells_on_16_pixel_grid() -> None:
    f = font()
    codes = [0x0020] * 38
    codes[20] = GLYPH_CODES[0]  # line 2, column 1
    pixels = nibbles(f, codes)
    assert pixels
    assert all(16 <= x < 32 and 16 <= y < 32 for x, y in pixels)
    assert body_mask(f, codes) == {xy for xy, v in pixels.items() if v == BODY}


def test_placeholder_cell_is_empty() -> None:
    f = font()
    codes = [0x0000] * 38
    assert nibbles(f, codes) == {}


def test_match_finds_record_with_small_offset() -> None:
    f = font()
    recs = records()
    origin = (ORIGIN[0] + 1, ORIGIN[1] - 2)
    image = screenshot(body_mask(f, recs[7]), origin)
    ranked = match(image, f, recs)
    assert ranked[0]["record"] == 7
    assert ranked[0]["iou"] == 1.0
    assert ranked[0]["origin"] == list(origin)
    assert float(ranked[1]["iou"]) < 1.0  # type: ignore[arg-type]


def test_render_and_parse_records() -> None:
    png = render(font(), records()[:2], scale=1)
    image = decode_png(png)
    assert image.width == 19 * 16 + 8
    assert parse_records("0-2,5") == [0, 1, 2, 5]
