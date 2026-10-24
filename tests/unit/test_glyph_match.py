from __future__ import annotations

import struct
from pathlib import Path

from tools.memory.mcs_extract import REGIONS
from tools.memory.vdp1_sprites import VRAM_SIZE
from tools.text.glyph_match import FONT_POINTER, match

COLOR = 0x6030
GLYPH = bytes(range(1, 129))


def sprite(color: int, source: int, x: int, y: int) -> bytes:
    words = [0, 0, 0, color, source // 8, (2 << 8) | 16, x, y] + [0] * 8
    return struct.pack(">16H", *words)


def make_dump(directory: Path) -> None:
    vram = bytearray(VRAM_SIZE)
    commands = [
        sprite(COLOR, 0x1000, 42, 30),  # glyph, row 1
        sprite(COLOR, 0x1080, 26, 30),  # blank, row 1
        sprite(COLOR, 0x1000, 26, 14),  # glyph, row 0
        sprite(0x7040, 0x1000, 0, 0),  # other color word: ignored
    ]
    for index, raw in enumerate(commands):
        vram[index * 32 : index * 32 + 32] = raw
    vram[len(commands) * 32] = 0x80  # end of list
    vram[0x1000 : 0x1000 + 128] = GLYPH
    (directory / "vdp1_vram.bin").write_bytes(bytes(vram))

    cart_base = REGIONS["cart_ram"].base_address
    font_base = cart_base + 0x1000
    cart = bytearray(REGIONS["cart_ram"].size)
    table = 0x1000 + 16
    cart[table : table + 4] = (0x400).to_bytes(4, "big")  # block 0 data offset
    cart[table + 0x380 + 5] = 0x80  # code 5: raw cell; codes 0-4 empty
    cart[table + 0x400 : table + 0x400 + 128] = GLYPH
    (directory / "cart_ram.bin").write_bytes(bytes(cart))

    wram_h = bytearray(REGIONS["wram_h"].size)
    offset = FONT_POINTER - REGIONS["wram_h"].base_address
    wram_h[offset : offset + 4] = font_base.to_bytes(4, "big")
    (directory / "wram_h.bin").write_bytes(bytes(wram_h))


def test_match_orders_cells_and_finds_codes(tmp_path: Path) -> None:
    make_dump(tmp_path)
    report = match(tmp_path, COLOR)
    cells = report["cells"]
    assert isinstance(cells, list)
    assert [(c["row"], c["x"]) for c in cells] == [(0, 26), (1, 26), (1, 42)]
    assert [c["blank"] for c in cells] == [False, True, False]
    assert cells[0]["codes"] == ["0x0005"] and cells[2]["codes"] == ["0x0005"]
    assert report["sprites"] == 3
    assert report["glyph_cells"] == 2
    assert report["matched_glyph_cells"] == 2
