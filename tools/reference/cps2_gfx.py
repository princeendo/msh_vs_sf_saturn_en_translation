"""Render 16 x 16 CPS-II sprite tiles from a set's graphics ROMs (REF-012).

The ``gfx`` region is rebuilt in memory from a zip, using the pinned MAME driver
definition (``ROM_LOAD64_WORD``), then unshuffled in 2 MiB banks as MAME's
``cps2_gfx_decode`` does. Tiles use MAME's ``cps1_layout16x16``: 128 bytes,
4 bit planes at bits 24/16/8/0 of each 64-bit row, the left 8 pixels at bit 0 and
the right 8 at bit 32. A sprite's tile number is its code word plus
``(y & 0x6000) << 3``.

The output PNG holds copyrighted tile art: keep it under an ignored local path.
"""

from __future__ import annotations

import argparse
import zipfile
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import encode_png
from tools.reference.mame_audit import RomSet, parse_driver

TILE_BYTES = 128
BANK_BYTES = 0x200000


def unshuffle(units: list[int], start: int = 0, count: int | None = None) -> None:
    """MAME's CPS-II ``unshuffle``, applied to a list of 8-byte unit indices."""
    count = len(units) if count is None else count
    if count == 2:
        return
    half = count // 2
    unshuffle(units, start, half)
    unshuffle(units, start + half, half)
    for i in range(half // 2):
        a, b = start + half // 2 + i, start + half + i
        units[a], units[b] = units[b], units[a]


def build_gfx(archive: Path, romset: RomSet) -> bytes:
    """Rebuild and unshuffle the ``gfx`` region from a zip."""
    entries = [rom for rom in romset.roms if rom.region == "gfx"]
    if not entries:
        raise ValueError(f"{romset.name} has no gfx ROMs")
    image = bytearray(
        max(rom.offset - rom.offset % 8 + 4 * rom.size for rom in entries)
    )
    with zipfile.ZipFile(archive) as bundle:
        for rom in entries:
            if rom.loader != "ROM_LOAD64_WORD":
                raise ValueError(f"unsupported loader {rom.loader} for {rom.name}")
            data = bundle.read(rom.name)
            if len(data) != rom.size:
                raise ValueError(f"{rom.name}: {len(data)} bytes, expected {rom.size}")
            base = rom.offset
            for i in range(0, len(data), 2):
                image[base + 4 * i : base + 4 * i + 2] = data[i : i + 2]
    order = list(range(BANK_BYTES // 8))
    unshuffle(order)
    banks = []
    for start in range(0, len(image), BANK_BYTES):
        bank = image[start : start + BANK_BYTES]
        banks.append(b"".join(bank[8 * unit : 8 * unit + 8] for unit in order))
    return b"".join(banks)


def tile_pixels(gfx: bytes, tile: int) -> list[int]:
    """Return the 256 pen values (0-15, row-major) of one 16 x 16 tile."""
    base = tile * TILE_BYTES
    pixels = []
    for row in range(16):
        unit = gfx[base + 8 * row : base + 8 * row + 8]
        for x in range(16):
            bit = x if x < 8 else 32 + x - 8
            pen = 0
            for plane, offset in enumerate((24, 16, 8, 0)):
                position = offset + bit
                if unit[position // 8] & (0x80 >> (position % 8)):
                    pen |= 8 >> plane
            pixels.append(pen)
    return pixels


def sheet(gfx: bytes, tiles: Sequence[int], columns: int = 16, scale: int = 2) -> bytes:
    """Lay tiles out on a grid as a grey-ramp PNG (pen 15 = transparent black)."""
    rows = (len(tiles) + columns - 1) // columns
    width, height = columns * 17 * scale, rows * 17 * scale
    rgb = bytearray(b"\x40\x00\x40" * width * height)
    for n, tile in enumerate(tiles):
        pixels = tile_pixels(gfx, tile)
        left, top = (n % columns) * 17 * scale, (n // columns) * 17 * scale
        for i, pen in enumerate(pixels):
            grey = 0 if pen == 15 else 255 - pen * 16
            for dy in range(scale):
                for dx in range(scale):
                    y, x = top + (i // 16) * scale + dy, left + (i % 16) * scale + dx
                    rgb[3 * (y * width + x) : 3 * (y * width + x) + 3] = bytes(
                        (grey,) * 3
                    )
    return encode_png(width, height, bytes(rgb))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--driver", type=Path, required=True, help="MAME driver .cpp")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument("--first", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--count", type=int, default=256)
    parser.add_argument("--columns", type=int, default=16)
    parser.add_argument("--out", type=Path, required=True, help="PNG (local only)")
    parser.add_argument("archive", type=Path, help="ROM zip file")
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    set_name = args.set_name or args.archive.stem
    if set_name not in sets:
        parser.error(f"set not defined in driver: {set_name}")
    gfx = build_gfx(args.archive, sets[set_name])
    tiles = range(args.first, args.first + args.count)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(sheet(gfx, tiles, args.columns))
    print(f"{set_name}: tiles {tiles.start:#x}-{tiles.stop - 1:#x} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
