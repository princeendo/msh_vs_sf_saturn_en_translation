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
one cell (8 columns each), keeping the gradient and the outline; ``OVERRIDES``
redraws letters too wide to squeeze.

The full gradient does not fit the font (`EXP-0052`: 40,852 bytes of pairs
against 30,235 reclaimable). ``caption_cell`` is what the compiler stores
(``glyph_style: credits``, FONT-011): two shading bands (``BANDS``) and a
4-connected outline, 29,284 bytes for the roster spec. The CLI renders mockups
on the red text box for review.
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
    # UI-004, by glyph shape: the CONTINUE? hints' button notation.
    "+": 0x1FE,
    "(": 0x1F9,
    ")": 0x1FF,
    "\u203c": 0x1F0,  # one-cell double exclamation: drawn by OVERRIDES, shaded as "!"
}
GOLD = {value: (240, 240 - 16 * (value - 1), 0) for value in range(1, 10)} | {
    OUTLINE: (32, 0, 96)
}
WHITE = {value: (240, 240, 240) for value in range(1, 10)} | {OUTLINE: (0, 0, 0)}
BOX = (192, 0, 0)
# The captions' own palette (CRAM banks 0x030, 0x1E0, 0x1F0, `EXP-0052`): the
# same layout as the credits bank, in grey.
SILVER = {
    value: (256 - 16 * value, 256 - 16 * value, 256 - 16 * value)
    for value in range(1, 10)
} | {OUTLINE: (16, 16, 0)}
BANDS = ((8, 5), (16, 1))  # (rows below, fill value): darker top, bright bottom

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


def squeeze_fill(cells: Grid) -> Grid:
    """16 to 8 columns of fill only (the outline is dropped, lowest fill kept)."""
    return [
        [
            min(fills) if (fills := [v for v in pair if v not in (0, OUTLINE)]) else 0
            for pair in zip(row[0::2], row[1::2], strict=True)
        ]
        for row in cells
    ]


def fit_fill(cells: Grid, width: int = 6, threshold: float = 0.5) -> Grid:
    """Resample the glyph's fill columns into ``width`` columns of an 8-column slot.

    The fill's bounding columns are mapped onto columns ``1 .. width`` (centred),
    leaving room for the outline. A target pixel is filled when at least
    ``threshold`` of its source span is fill; it takes the lowest fill value
    there, which keeps the vertical gradient.
    """
    fill = [[v not in (0, OUTLINE) for v in row] for row in cells]
    columns = [c for c in range(16) if any(row[c] for row in fill)]
    out = [[0] * 8 for _ in cells]
    if not columns:
        return out
    left, span = columns[0], columns[-1] - columns[0] + 1
    target = min(width, span)
    start = (8 - target) // 2
    for row_index, row in enumerate(cells):
        for j in range(target):
            a = left + j * span / target
            b = left + (j + 1) * span / target
            covered, values = 0.0, []
            for x in range(int(a), min(16, int(b) + 1)):
                overlap = min(b, x + 1) - max(a, x)
                if overlap > 0 and fill[row_index][x]:
                    covered += overlap
                    values.append(row[x])
            if values and covered / (b - a) >= threshold:
                out[row_index][start + j] = min(values)
    return out


# Hand-drawn fill for letters too wide to squeeze (EXP-0052): row strings from
# the glyph's first fill row, eight columns each, "#" = fill. The vertical
# gradient comes from the original glyph's rows, and the outline is added later.
OVERRIDES: dict[str, tuple[int, tuple[str, ...]]] = {
    "I": (2, ("..##....",) * 13),
    "!": (2, ("..##....",) * 9 + ("........", "..##....", "..##....")),
    "'": (2, ("..##....", "..##....", "...#....", "..#.....")),
    "\u203c": (2, ("##.##...",) * 9 + ("........", "##.##...", "##.##...")),
    "M": (2, ("##...##.", "###.###.", "##.#.##.", "##.#.##.") + ("##...##.",) * 9),
    "W": (
        2,
        ("##...##.",) * 4
        + ("##.#.##.",) * 4
        + ("#######.", "###.###.", ".##.##..", ".##.##..", ".#...#.."),
    ),
    "m": (3, ("######..", "#######.") + ("##.#.##.",) * 7),
    "w": (3, ("##.#.##.",) * 6 + ("#######.", ".##.##..", ".##.##..")),
}


def override_fill(cells: Grid, char: str) -> Grid:
    """The hand-drawn fill of ``char``, shaded with the source glyph's row values."""
    first, rows = OVERRIDES[char]
    shade = [
        min(fills) if (fills := [v for v in row if v not in (0, OUTLINE)]) else 0
        for row in cells
    ]
    filled = [r for r in range(16) if shade[r]]
    out = [[0] * 8 for _ in range(16)]
    for offset, pattern in enumerate(rows):
        row = first + offset
        value = shade[row] or shade[min(filled, key=lambda r: abs(r - row))]
        out[row] = [value if mark == "#" else 0 for mark in pattern]
    return out


def outlined(cells: Grid, connectivity: int = 8) -> Grid:
    """Draw ``OUTLINE`` on empty pixels adjacent to fill (8-adjacent, as the font)."""
    height, width = len(cells), len(cells[0])
    steps = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if connectivity == 4:
        steps = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    out = [row[:] for row in cells]
    for row in range(height):
        for column in range(width):
            if cells[row][column]:
                continue
            if any(
                0 <= row + dy < height
                and 0 <= column + dx < width
                and cells[row + dy][column + dx]
                for dy, dx in steps
            ):
                out[row][column] = OUTLINE
    return out


def pair_cell(glyphs: Sequence[bytes], pair: str, method: str = "outline") -> Grid:
    """Two characters squeezed side by side in one 16 x 16 cell.

    ``outline`` (default) squeezes the fill and redraws a one-pixel outline
    around the pair; ``fit`` resamples each letter's fill into six columns
    first (``fit_fill``); ``naive`` squeezes fill and outline together.
    """
    squeezer = {"naive": squeeze, "outline": squeeze_fill, "fit": fit_fill}[method]

    def half(char: str) -> Grid:
        if char == " ":
            return [[0] * 8 for _ in range(16)]
        cells = grid(glyphs[credit_code(char)])
        if method != "naive" and char in OVERRIDES:
            return override_fill(cells, char)
        return squeezer(cells)

    halves = [half(char) for char in pair]
    cell = [halves[0][row] + halves[1][row] for row in range(16)]
    return cell if method == "naive" else outlined(cell)


def caption_cell(glyphs: Sequence[bytes], pair: str) -> Grid:
    """The stored FONT-011 pair: squeezed fill, ``BANDS`` shading, 4-way outline."""
    fill = [
        [v if v not in (0, OUTLINE) else 0 for v in row]
        for row in pair_cell(glyphs, pair)
    ]
    banded = [
        [next(value for below, value in BANDS if row < below) if v else 0 for v in line]
        for row, line in enumerate(fill)
    ]
    return outlined(banded, connectivity=4)


def cell_bytes(cells: Grid) -> bytes:
    """A 16 x 16 grid of 4-bit values as a 128-byte cell."""
    return bytes(
        (cells[row][column] << 4) | cells[row][column + 1]
        for row in range(16)
        for column in range(0, 16, 2)
    )


def pair_bytes(glyphs: Sequence[bytes], pair: str) -> bytes:
    """The credits-style pair glyph for ``pair`` (FONT-011), as a font cell."""
    return cell_bytes(caption_cell(glyphs, pair))


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
            cell = caption_cell(glyphs, pair)
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
    parser.add_argument(
        "--palette", choices=("gold", "silver", "white"), default="silver"
    )
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument("--out", type=Path, required=True, help="PNG (ignored path)")
    args = parser.parse_args(argv)
    entry = args.memfix.read_bytes()[
        args.entry_offset : args.entry_offset + args.entry_size
    ]
    glyphs = [glyph.cell for glyph in unpack(entry)[1]]
    palette = {"gold": GOLD, "silver": SILVER, "white": WHITE}[args.palette]
    width, height, image = render_box(args.line, glyphs, palette)
    args.out.write_bytes(encode_png(width, height, image))
    print(f"{args.out} {width}x{height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
