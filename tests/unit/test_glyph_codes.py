from __future__ import annotations

from tests.unit.test_vdp1_sprites import command, make_vram
from tools.memory.glyph_codes import BUFFER_ADDRESS, CELLS, pair_cells

WRAM_H_BASE = 0x06000000


def quote_screen(codes: list[int]) -> tuple[bytes, bytes]:
    commands = []
    data = {}
    for i, _ in enumerate(codes):
        source = 0x40000 + 0x80 * i
        y, x = divmod(i, 19)
        commands.append(
            (
                0x20 * i,
                command(
                    0x0000,
                    color=0x61E0,
                    source=source >> 3,
                    size=(2 << 8) | 16,
                    x=26 + 16 * x,
                    y=178 + 16 * y,
                ),
            )
        )
        data[source] = bytes([i + 1]) * 128
    commands.append((0x20 * len(codes), command(0x8000)))
    vram = make_vram(commands, data)
    wram_h = bytearray(0x100000)
    offset = BUFFER_ADDRESS - WRAM_H_BASE
    for i, code in enumerate(codes):
        wram_h[offset + 4 * i : offset + 4 * i + 4] = (0x5000 | code).to_bytes(
            2, "big"
        ) + b"\x00\x02"
    return vram, bytes(wram_h)


def test_pair_cells_maps_codes_and_skips_blanks() -> None:
    codes = [0x0020] * CELLS
    codes[3] = 0x0803
    codes[20] = 0x09CA
    vram, wram_h = quote_screen(codes)

    pairs = pair_cells(vram, wram_h)

    assert pairs == {0x0803: bytes([4]) * 128, 0x09CA: bytes([21]) * 128}


def test_pair_cells_rejects_non_quote_screens() -> None:
    vram, wram_h = quote_screen([0x0020] * 10)
    assert pair_cells(vram, wram_h) is None
    vram, _ = quote_screen([0x0020] * CELLS)
    assert pair_cells(vram, bytes(0x100000)) is None
