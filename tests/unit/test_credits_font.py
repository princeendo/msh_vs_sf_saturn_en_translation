from __future__ import annotations

import pytest

from tools.memory.vdp1_commands import glyph_sprites
from tools.text.credits_font import OUTLINE, credit_code, grid, squeeze


def test_credit_code_follows_the_credits_layout() -> None:
    assert credit_code("A") == 0x210
    assert credit_code("Z") == 0x229
    assert credit_code("a") == 0x231
    assert credit_code("z") == 0x24A
    assert credit_code("0") == 0x200
    assert credit_code(".") == 0x252
    with pytest.raises(ValueError):
        credit_code("@")


def test_squeeze_keeps_fill_over_outline() -> None:
    row = [OUTLINE, 3, 0, 0, OUTLINE, 0, 5, 2] + [0] * 8
    assert squeeze([row])[0][:4] == [3, 0, OUTLINE, 2]


def test_grid_reads_high_nibble_first() -> None:
    cell = bytes([0x1B] + [0] * 127)
    assert grid(cell)[0][:2] == [1, OUTLINE]


def command(ctrl: int, x: int, y: int, srca: int = 0, size: int = 0) -> bytes:
    words = [ctrl, 0, 0x0880, 0x6030, srca // 8, size, x & 0xFFFF, y & 0xFFFF]
    return b"".join(w.to_bytes(2, "big") for w in words) + bytes(16)


def test_glyph_sprites_apply_local_coordinates() -> None:
    vram = (
        command(0xA, -80, -16)
        + command(0x0, 100, 40, srca=0x8000, size=(2 << 8) | 16)
        + command(0x0, 0, 0, srca=0x8000, size=(4 << 8) | 16)
        + command(0x8000, 0, 0)
    )
    found = glyph_sprites(vram)
    assert [(s.x, s.y, s.source) for s in found] == [(20, 24, 0x8000)]


def font_cells() -> list[bytes]:
    """A synthetic font: every credits code is a 4-wide bar of fill value 3."""
    bar = bytes(
        (0x03 if 2 <= column // 2 < 4 else 0)
        for row in range(16)
        for column in range(0, 16, 2)
    )
    return [bar] * 0x260


def test_caption_cell_bands_and_outline() -> None:
    from tools.text.credits_font import BANDS, caption_cell

    cell = caption_cell(font_cells(), "AB")
    fills = {v for row in cell for v in row} - {0, OUTLINE}
    assert fills <= {value for _, value in BANDS}
    assert cell[0][1] == OUTLINE  # the 4-connected outline left of the fill


def test_pair_glyph_styles() -> None:
    from tools.text.credits_font import pair_bytes
    from tools.text.pair_font import pair_glyph

    cells = font_cells()
    assert pair_glyph(cells, "AB", "credits") == pair_bytes(cells, "AB")
    with pytest.raises(ValueError):
        pair_glyph(cells, "AB", "gothic")
