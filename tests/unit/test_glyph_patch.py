from __future__ import annotations

from tools.text.font import CELL_BYTES, nibble_at
from tools.text.glyph_patch import compose, ink, squeeze


def vertical_bar(column: int) -> bytes:
    cell = bytearray(CELL_BYTES)
    for row in range(2, 12):
        index = row * 8 + column // 2
        cell[index] |= (0x1 << 4) if column % 2 == 0 else 0x1
    return bytes(cell)


def test_squeeze_or_combines_column_pairs() -> None:
    mask = ink(vertical_bar(5))
    squeezed = squeeze(mask)
    assert squeezed[5][2] is True
    assert sum(sum(row) for row in squeezed) == 10


def test_compose_places_letters_side_by_side_with_shadow() -> None:
    cell = compose(vertical_bar(4), vertical_bar(4))
    # left letter ink at column 2, right letter ink at column 8 + 2
    assert nibble_at(cell, 5, 2) == 0x1
    assert nibble_at(cell, 5, 10) == 0x1
    # shadow to the right and below the ink
    assert nibble_at(cell, 5, 3) == 0xF
    assert nibble_at(cell, 12, 2) == 0xF
    assert nibble_at(cell, 0, 0) == 0
    assert len(cell) == CELL_BYTES


def test_shadow_pixels_in_sources_are_not_ink() -> None:
    cell = bytearray(vertical_bar(4))
    cell[8 * 8 + 2] |= 0x0F  # add a shadow nibble at row 8, column 5
    assert ink(bytes(cell))[8][5] is False
