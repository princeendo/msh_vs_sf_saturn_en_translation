"""List VDP1 normal sprites from a raw VDP1 VRAM dump (FONT-010).

The command table starts at VRAM ``0x0``. Each command is 32 bytes of big-endian
words: CMDCTRL (end bit ``0x8000``, skip bit ``0x4000``, command in the low
nibble), CMDLINK, CMDPMOD, CMDCOLR, CMDSRCA (address / 8), CMDSIZE (width / 8
in bits 8-13, height in bits 0-7), then CMDXA and CMDYA. Command ``0xA`` sets the
local coordinates, which are added to later sprites' positions. This reader
walks the table in order and ignores jump links, which is enough for the screens
checked so far (credits and dialogue, `EXP-0051`).

With ``--font``, each 16 x 16 4 bpp sprite's 128 bytes are matched against the
glyphs of an unpacked quote font, to name the code each sprite shows.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

COMMAND = 32
END, SKIP = 0x8000, 0x4000
NORMAL, LOCAL = 0x0, 0xA


@dataclass(frozen=True)
class Sprite:
    index: int
    x: int
    y: int
    pmod: int
    colr: int
    source: int
    width: int
    height: int


def word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def signed(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def sprites(vram: bytes) -> list[Sprite]:
    """Normal sprites in table order, with local coordinates applied."""
    out = []
    local = (0, 0)
    for index in range(len(vram) // COMMAND):
        base = index * COMMAND
        ctrl = word(vram, base)
        if ctrl & END:
            break
        if ctrl & SKIP:
            continue
        command = ctrl & 0xF
        x, y = signed(word(vram, base + 12)), signed(word(vram, base + 14))
        if command == LOCAL:
            local = (x, y)
        elif command == NORMAL:
            size = word(vram, base + 10)
            out.append(
                Sprite(
                    index,
                    x + local[0],
                    y + local[1],
                    word(vram, base + 4),
                    word(vram, base + 6),
                    word(vram, base + 8) * 8,
                    ((size >> 8) & 0x3F) * 8,
                    size & 0xFF,
                )
            )
    return out


def glyph_sprites(vram: bytes) -> list[Sprite]:
    """16 x 16 sprites in 4 bpp colour-bank mode (the quote-font glyph shape)."""
    return [
        s
        for s in sprites(vram)
        if s.width == 16 and s.height == 16 and (s.pmod >> 3) & 7 == 0
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("vram", type=Path, help="raw VDP1 VRAM dump (512 KiB)")
    parser.add_argument("--font", type=Path, help="MEMFIX.PAC, to name glyph codes")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    args = parser.parse_args(argv)
    vram = args.vram.read_bytes()
    codes: dict[bytes, list[int]] = {}
    if args.font:
        from tools.text.font_pack import unpack

        entry = args.font.read_bytes()[
            args.entry_offset : args.entry_offset + args.entry_size
        ]
        for code, glyph in enumerate(unpack(entry)[1]):
            codes.setdefault(glyph.cell, []).append(code)
    rows = []
    for sprite in glyph_sprites(vram):
        tile = vram[sprite.source : sprite.source + 128]
        if not any(tile):
            continue
        row: dict[str, object] = asdict(sprite)
        row["codes"] = [f"0x{c:03X}" for c in codes.get(tile, [])]
        rows.append(row)
    print(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
