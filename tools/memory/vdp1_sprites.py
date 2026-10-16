"""List and render VDP1 sprite commands from a raw VDP1 VRAM dump.

The input is a 512 KiB VDP1 VRAM dump in Saturn byte order (for example
``vdp1_vram.bin`` from ``tools.memory.mcs_extract``). The command layout follows
the Mednafen 1.32.1 implementation (``src/ss/vdp1.cpp`` and
``src/ss/vdp1_sprite.cpp``), not a hardware manual:

* commands are 16 big-endian words (32 bytes), and the list starts at offset 0;
* word 0 (control): bit 15 ends the list, bit 14 skips the command, bits 12-13
  select the jump mode, and bits 0-3 give the command type;
* word 1 (link) times 8 is the jump target byte address;
* word 2 (mode): bits 3-5 give the color mode (0-1 4 bpp, 2-4 8 bpp, 5 16 bpp);
* word 3 is the color/table word;
* word 4 (source) times 8 is the character data byte address;
* word 5 (size): bits 8-13 give width / 8, and bits 0-7 give height;
* words 6-7 are the X/Y coordinates (13-bit signed);
* type 0xA sets local coordinates.

Rendering is grayscale, ignores palettes and flips, and draws only normal sprites
(type 0). It is meant for identifying content, not for faithful display.
"""

from __future__ import annotations

import argparse
import json
import struct
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from tools.memory.mcs_extract import encode_png, sha256

COMMAND_SIZE = 32
VRAM_SIZE = 0x80000
BITS_PER_PIXEL = {0: 4, 1: 4, 2: 8, 3: 8, 4: 8, 5: 16}


@dataclass(frozen=True)
class Command:
    """One decoded VDP1 command."""

    address: int
    kind: int
    words: tuple[int, ...]


@dataclass(frozen=True)
class Sprite:
    """A normal-sprite command with resolved screen position."""

    command_address: int
    color_mode: int
    color_word: int
    source: int
    width: int
    height: int
    x: int
    y: int


def signed(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def walk(vram: bytes, limit: int = 4096) -> list[Command]:
    """Follow the command list from offset 0 until an end command or a loop."""
    if len(vram) != VRAM_SIZE:
        raise ValueError(f"expected {VRAM_SIZE} bytes of VDP1 VRAM, got {len(vram)}")
    commands: list[Command] = []
    address = 0
    return_address: int | None = None
    seen: set[int] = set()
    for _ in range(limit):
        if address in seen:
            break
        seen.add(address)
        words = struct.unpack_from(">16H", vram, address)
        control = words[0]
        if control & 0x8000:
            break
        if not control & 0x4000:
            commands.append(Command(address, control & 0xF, words))
        following = (address + COMMAND_SIZE) % VRAM_SIZE
        jump = (control >> 12) & 0x3
        if jump == 1:
            following = (words[1] << 3) & ~0x1F
        elif jump == 2:
            if return_address is None:
                return_address = following
            following = (words[1] << 3) & ~0x1F
        elif jump == 3 and return_address is not None:
            following, return_address = return_address, None
        address = following
    return commands


def sprites(vram: bytes) -> list[Sprite]:
    """Return normal sprites with local coordinates applied."""
    local_x = local_y = 0
    found: list[Sprite] = []
    for command in walk(vram):
        words = command.words
        if command.kind == 0xA:
            local_x = signed(words[6], 11)
            local_y = signed(words[7], 11)
        elif command.kind == 0:
            found.append(
                Sprite(
                    command_address=command.address,
                    color_mode=(words[2] >> 3) & 0x7,
                    color_word=words[3],
                    source=words[4] * 8,
                    width=((words[5] >> 8) & 0x3F) * 8,
                    height=words[5] & 0xFF,
                    x=signed(words[6], 13) + local_x,
                    y=signed(words[7], 13) + local_y,
                )
            )
    return found


def pixel_bytes(vram: bytes, sprite: Sprite) -> bytes:
    """Return the raw character data a sprite reads."""
    bpp = BITS_PER_PIXEL.get(sprite.color_mode, 8)
    size = sprite.width * sprite.height * bpp // 8
    return vram[sprite.source : sprite.source + size]


def to_gray(data: bytes, width: int, height: int, bpp: int) -> bytearray:
    """Convert raw character data to 8-bit grayscale values."""
    out = bytearray(width * height)
    if bpp == 4:
        for index, value in enumerate(data[: width * height // 2]):
            out[2 * index] = (value >> 4) * 17
            out[2 * index + 1] = (value & 0xF) * 17
    elif bpp == 8:
        chunk = data[: width * height]
        out[: len(chunk)] = chunk
    else:
        for index in range(min(width * height, len(data) // 2)):
            color = (data[2 * index] << 8) | data[2 * index + 1]
            total = (color & 31) + ((color >> 5) & 31) + ((color >> 10) & 31)
            out[index] = total * 255 // 93
    return out


def render(
    vram: bytes,
    chosen: Sequence[Sprite],
    origin: tuple[int, int] = (0, 0),
    size: tuple[int, int] = (512, 320),
) -> bytes:
    """Draw sprites (nonzero pixels only) and return a grayscale PNG."""
    width, height = size
    canvas = bytearray(width * height)
    for sprite in chosen:
        bpp = BITS_PER_PIXEL.get(sprite.color_mode, 8)
        gray = to_gray(pixel_bytes(vram, sprite), sprite.width, sprite.height, bpp)
        for row in range(sprite.height):
            y = sprite.y - origin[1] + row
            if not 0 <= y < height:
                continue
            for column in range(sprite.width):
                x = sprite.x - origin[0] + column
                value = gray[row * sprite.width + column]
                if value and 0 <= x < width:
                    canvas[y * width + x] = value
    rgb = bytes(channel for value in canvas for channel in (value, value, value))
    return encode_png(width, height, rgb)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List or render VDP1 normal sprites from a raw VDP1 VRAM dump."
    )
    parser.add_argument("vram", type=Path, help="raw VDP1 VRAM dump (512 KiB)")
    parser.add_argument(
        "--color-word",
        type=lambda value: int(value, 0),
        help="only sprites with this color/table word (e.g. 0x61E0)",
    )
    parser.add_argument("--render", type=Path, help="write a grayscale PNG here")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit sprite list as JSON"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        vram = args.vram.read_bytes()
        found = sprites(vram)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.color_word is not None:
        found = [item for item in found if item.color_word == args.color_word]

    if args.render:
        args.render.write_bytes(render(vram, found))
    records = [
        {**asdict(item), "pixel_sha256": sha256(pixel_bytes(vram, item))}
        for item in found
    ]
    if args.as_json:
        print(json.dumps(records, indent=2))
    else:
        for record in records:
            print(
                f"cmd@0x{record['command_address']:05X} cm{record['color_mode']} "
                f"colr=0x{record['color_word']:04X} src=0x{record['source']:05X} "
                f"{record['width']}x{record['height']} "
                f"xy=({record['x']},{record['y']})"
            )
        print(f"{len(records)} sprites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
