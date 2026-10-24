"""Match on-screen VDP1 glyph cells against the quote font (END-002).

Input is a dump directory from ``tools.memory.mcs_extract`` (``vdp1_vram.bin``,
``wram_h.bin``, ``cart_ram.bin``) of one paused instant. The script:

1. lists the VDP1 normal sprites with one color/table word, in reading order
   (top to bottom, then left to right);
2. reads the quote-font base pointer at WRAM-H ``0x0601D8E4`` (`FONT-001`) and
   decodes every code with ``tools.text.font``;
3. reports, per sprite, its grid position, character address, and every font
   code whose decoded cell equals the sprite's 128 bytes exactly.

An exact match shows only that the cell equals a decoded font cell. It does not
show which code the game looked up, since codes may share a cell.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import REGIONS
from tools.memory.vdp1_sprites import Sprite, pixel_bytes, sprites
from tools.text.font import CELL_BYTES, Font

FONT_POINTER = 0x0601D8E4
CODES = 0xE00  # the block table covers 0x380 / 4 blocks of 16 codes


def font_index(font: Font, codes: int = CODES) -> dict[bytes, list[int]]:
    """Map each decodable cell to the codes that produce it."""
    index: dict[bytes, list[int]] = {}
    for code in range(codes):
        try:
            cell, _ = font.glyph(code)
        except (ValueError, IndexError):
            continue
        index.setdefault(cell, []).append(code)
    return index


def text_sprites(vram: bytes, color_word: int) -> list[Sprite]:
    chosen = [s for s in sprites(vram) if s.color_word == color_word]
    return sorted(chosen, key=lambda s: (s.y, s.x))


def match(dump: Path, color_word: int) -> dict[str, object]:
    vram = (dump / "vdp1_vram.bin").read_bytes()
    wram_h = (dump / "wram_h.bin").read_bytes()
    offset = FONT_POINTER - REGIONS["wram_h"].base_address
    base = int.from_bytes(wram_h[offset : offset + 4], "big")
    font = Font(
        (dump / "cart_ram.bin").read_bytes(), REGIONS["cart_ram"].base_address, base
    )
    index = font_index(font)
    rows = sorted({s.y for s in text_sprites(vram, color_word)})
    cells = []
    for sprite in text_sprites(vram, color_word):
        data = pixel_bytes(vram, sprite)
        cells.append(
            {
                "row": rows.index(sprite.y),
                "x": sprite.x,
                "y": sprite.y,
                "source": f"0x{sprite.source:05X}",
                "blank": not any(data),
                "codes": [f"0x{c:04X}" for c in index.get(data, [])],
            }
        )
    glyphs = [c for c in cells if not c["blank"]]
    return {
        "dump": str(dump),
        "color_word": f"0x{color_word:04X}",
        "font_base": f"0x{base:08X}",
        "cell_bytes": CELL_BYTES,
        "sprites": len(cells),
        "glyph_cells": len(glyphs),
        "matched_glyph_cells": sum(1 for c in glyphs if c["codes"]),
        "cells": cells,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dump", type=Path, help="mcs_extract output directory")
    parser.add_argument("--color-word", type=lambda v: int(v, 0), required=True)
    args = parser.parse_args(argv)
    print(json.dumps(match(args.dump, args.color_word), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
