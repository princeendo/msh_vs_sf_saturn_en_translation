"""The staff-credits font inside the quote font, and caption mockups (FONT-010).

`EXP-0051` found that the credits draw quote-font codes ``0x1E0``-``0x25F``
(MEMFIX entry 4) through the same glyph routine as captions:

- upper case at ``0x210`` + letter, lower case at ``0x231`` + letter;
- digits at ``0x200`` + digit;
- punctuation as in ``PUNCTUATION`` (chosen by glyph shape).

Each glyph fills a 16 x 16 4 bpp cell: values 1-9 are a gradient, ``B`` is the
outline. The credits palette maps 1-9 to yellow through orange, and ``B`` to
dark purple (measured from a screenshot, `EXP-0051`).

A caption line has 19 cells, and official English lines run to 25 characters,
so one glyph per cell does not fit. ``pair_cell`` squeezes two credits glyphs into
one cell (8 columns each), keeping the gradient and the outline. The CLI renders
mockups on the red text box for review. Nothing here changes a disc image.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from tools.text.font_pack import unpack
from tools.text.pair_font import split_pairs

UPPER, LOWER, DIGITS = 0x210, 0x231, 0x200
OUTLINE = 0xB
PUNCTUATION = {
    "!": 0x1F0,
    "?": 0x1F1,
    '"': 0x230,
    ":": 0x250,
    ";": 0x251,
    ".": 0x252,
    ",": 0x253,
    "'": 0x255,
    "-": 0x20F,
}
GOLD = {value: (240, 240 - 16 * (value - 1), 0) for value in range(1, 10)} | {
    OUTLINE: (32, 0, 96)
}
WHITE = {value: (240, 240, 240) for value in range(1, 10)} | {OUTLINE: (0, 0, 0)}
BOX = (192, 0, 0)

Grid = list[list[int]]


def credit_code(char: str) -> int:
    if "A" <= char <= "Z":
        return UPPER + ord(char) - ord("A")
    if "a" <= char <= "z":
        return LOWER + ord(char) - ord("a")
    if "0" <= char <= "9":
        return DIGITS + ord(char) - ord("0")
    if char in PUNCTUATION:
        return PUNCTUATION[char]
    raise ValueError(f"no credits glyph for {char!r}")


def grid(cell: bytes) -> Grid:
    """16 x 16 pixel values of a 128-byte 4 bpp cell."""
    return [
        [
            (cell[row * 8 + column // 2] >> 4)
            if column % 2 == 0
            else cell[row * 8 + column // 2] & 0xF
            for column in range(16)
        ]
        for row in range(16)
    ]


def squeeze(cells: Grid) -> Grid:
    """16 to 8 columns: a fill value wins over the outline (lowest fill kept)."""
    out = []
    for row in cells:
        squeezed = []
        for column in range(8):
            pair = (row[2 * column], row[2 * column + 1])
            fills = [v for v in pair if v not in (0, OUTLINE)]
            squeezed.append(
                min(fills) if fills else (OUTLINE if OUTLINE in pair else 0)
            )
        out.append(squeezed)
    return out


def pair_cell(glyphs: Sequence[bytes], pair: str) -> Grid:
    """Two characters squeezed side by side in one 16 x 16 cell."""
    halves = [
        squeeze(grid(glyphs[credit_code(char)])) if char != " " else [[0] * 8] * 16
        for char in pair
    ]
    return [halves[0][row] + halves[1][row] for row in range(16)]


def render_box(
    lines: Sequence[str],
    glyphs: Sequence[bytes],
    palette: dict[int, tuple[int, int, int]],
    cells: int = 19,
    scale: int = 2,
) -> tuple[int, int, bytes]:
    """RGB image of a text box with each line centred in whole cells."""
    width, height = (cells * 16 + 16) * scale, (len(lines) * 16 + 16) * scale
    image = bytearray(bytes(BOX) * (width * height))
    for line_index, line in enumerate(lines):
        pairs = split_pairs(line)
        start = max(0, (cells - len(pairs)) // 2)
        for pair_index, pair in enumerate(pairs[: cells - start]):
            cell = pair_cell(glyphs, pair)
            for row in range(16):
                for column in range(16):
                    value = cell[row][column]
                    if value not in palette:
                        continue
                    for dy in range(scale):
                        for dx in range(scale):
                            x = (8 + (start + pair_index) * 16 + column) * scale + dx
                            y = (8 + line_index * 16 + row) * scale + dy
                            offset = (y * width + x) * 3
                            image[offset : offset + 3] = bytes(palette[value])
    return width, height, bytes(image)


def main(argv: Sequence[str] | None = None) -> int:
    from tools.memory.mcs_extract import encode_png

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("memfix", type=Path, help="MEMFIX.PAC (read only)")
    parser.add_argument("--line", action="append", required=True, help="repeatable")
    parser.add_argument("--palette", choices=("gold", "white"), default="gold")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument("--out", type=Path, required=True, help="PNG (ignored path)")
    args = parser.parse_args(argv)
    entry = args.memfix.read_bytes()[
        args.entry_offset : args.entry_offset + args.entry_size
    ]
    glyphs = [glyph.cell for glyph in unpack(entry)[1]]
    palette = GOLD if args.palette == "gold" else WHITE
    width, height, image = render_box(args.line, glyphs, palette)
    args.out.write_bytes(encode_png(width, height, image))
    print(f"{args.out} {width}x{height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
