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
