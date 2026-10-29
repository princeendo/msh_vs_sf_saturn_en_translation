"""Draw English into the boot-time warning screens ``ERR1.BIN``-``ERR5.BIN`` (UI-008).

Each file is a Windows BMP (`EXP-0103`): a 118-byte header and 16-colour
palette, then 352x240 4 bpp pixels stored bottom-up, two pixels a byte, high
nibble first. The game draws the pixels as they are, shifted up 8 rows, with the
file's own palette (a marker band showed at exactly its rows, and the screen
matched the BMP pixel for pixel). ERR5 is the no-cartridge screen.

The palette is the same in all five files and is kept: 0 black, 1-6 grey to
white, 7-10 cyan, 11-12 yellow, 13-14 red.

- **Text** (``data/ui008/error_screens.json``): the US arcade's narrow
  win-quote glyphs (``pair_font.narrow_code``), already in the quote font
  (``MEMFIX.PAC`` entry 4), 8 pixels apart; each 16x16 cell's left 8 columns
  are drawn. ``{text}`` is cyan and ``[text]`` red, as in the Japanese art;
  the rest is white, and the title yellow.
- **Pens.** The glyphs' gradient pens 1-9 (bright at the bottom) map to a
  colour's bright and dim entries (``RAMPS``); the shadow pen ``B`` maps to
  dark grey.
- **Rebuild.** The header and palette are kept, the pixels are cleared to
  black, and the text is drawn. The file keeps its size.

The output is game-derived: keep it under ``local/`` or ``build/`` only
(``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.attract_captions import diff_patches
from tools.memory.mcs_extract import encode_png
from tools.text.font import Font, nibble_at
from tools.text.pair_font import narrow_code

LAYOUT = Path("data/ui008/error_screens.json")
FILES = [f"ERR{i}.BIN" for i in range(1, 6)]
PIXELS = 118  # BMP header and palette
WIDTH, HEIGHT = 352, 240
ROW = WIDTH // 2
PITCH, LINE = 8, 16
MAX_WIDTH = 320  # 40 glyphs: 16-pixel margins inside the 352-pixel screen
SHADOW_PEN = 0xB
SHADOW = 1  # dark grey
# Colour name: (palette index for pens 1-6, for pens 7-9).
RAMPS = {
    "white": (6, 5),
    "cyan": (10, 9),
    "red": (14, 13),
    "yellow": (12, 12),
}
MARKS = {"{": ("}", "cyan"), "[": ("]", "red")}


class LayoutError(ValueError):
    pass


@dataclass(frozen=True)
class Screen:
    name: str
    title: str
    title_top: int
    top: int
    gap: int
    lines: tuple[str, ...]


def segments(line: str) -> list[tuple[str, str]]:
    """Split a marked-up line into (text, colour) runs."""
    runs: list[tuple[str, str]] = []
    rest = line
    while rest:
        starts = [i for i in (rest.find(m) for m in MARKS) if i >= 0]
        if not starts:
            runs.append((rest, "white"))
            break
        i = min(starts)
        end, colour = MARKS[rest[i]]
        j = rest.find(end, i + 1)
        if j < 0:
            raise LayoutError(f"unclosed {rest[i]!r} in {line!r}")
        if i:
            runs.append((rest[:i], "white"))
        runs.append((rest[i + 1 : j], colour))
        rest = rest[j + 1 :]
    return runs


def plain(line: str) -> str:
    return "".join(text for text, _ in segments(line))


def line_width(line: str) -> int:
    return PITCH * len(plain(line))


def load_layout(path: Path = LAYOUT) -> list[Screen]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != "mshvsf-error-screens/1":
        raise LayoutError("unknown error-screen layout schema")
    screens = [
        Screen(
            name,
            str(entry["title"]),
            int(entry["title_top"]),
            int(entry["top"]),
            int(entry["gap"]),
            tuple(str(line) for line in entry["lines"]),
        )
        for name, entry in document["screens"].items()
    ]
    if sorted(s.name for s in screens) != FILES:
        raise LayoutError(f"the layout must cover exactly {FILES}")
    return screens


def draw_text(
    pixels: bytearray, font: Font, text: str, colour: str, x: int, y: int
) -> None:
    """Draw ``text`` with its first cell's top-left corner at (x, y)."""
    bright, dim = RAMPS[colour]
    for k, char in enumerate(text):
        if char == " ":
            continue
        cell, _ = font.glyph(narrow_code(char))
        for row in range(LINE):
            for column in range(PITCH):
                pen = nibble_at(cell, row, column)
                if not pen:
                    continue
                if pen == SHADOW_PEN:
                    value = SHADOW
                elif pen <= 6:
                    value = bright
                else:
                    value = dim
                put(pixels, x + PITCH * k + column, y + row, value)


def put(pixels: bytearray, x: int, y: int, value: int) -> None:
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        raise LayoutError(f"pixel ({x}, {y}) is off the screen")
    offset = (HEIGHT - 1 - y) * ROW + x // 2
    if x % 2:
        pixels[offset] = pixels[offset] & 0xF0 | value
    else:
        pixels[offset] = pixels[offset] & 0x0F | value << 4


def render(original: bytes, screen: Screen, font: Font) -> bytes:
    """The BMP with its pixels replaced by ``screen``'s English text."""
    if len(original) != PIXELS + ROW * HEIGHT or original[:2] != b"BM":
        raise LayoutError(f"{screen.name} is not the expected 352x240 4 bpp BMP")
    widths = [line_width(line) for line in screen.lines]
    if max(widths) > MAX_WIDTH:
        wide = screen.lines[widths.index(max(widths))]
        raise LayoutError(f"{screen.name}: {wide!r} is wider than {MAX_WIDTH}")
    pixels = bytearray(ROW * HEIGHT)
    title_x = (WIDTH - line_width(screen.title)) // 2
    draw_text(pixels, font, screen.title, "yellow", title_x, screen.title_top)
    x0 = (WIDTH - max(widths)) // 2
    y = screen.top
    for line in screen.lines:
        if not line:
            y += screen.gap
            continue
        x = x0
        for text, colour in segments(line):
            draw_text(pixels, font, text, colour, x, y)
            x += PITCH * len(text)
        y += LINE
    if y > HEIGHT:
        raise LayoutError(f"{screen.name}: the text runs past the bottom")
    return original[:PIXELS] + bytes(pixels)


def preview(data: bytes) -> bytes:
    """A PNG of the screen as the game shows it (BMP rows 8-239)."""
    palette = [tuple(data[54 + 4 * k : 57 + 4 * k][::-1]) for k in range(16)]
    rgb = bytearray()
    for y in range(8, HEIGHT):
        row = data[PIXELS + (HEIGHT - 1 - y) * ROW :][:ROW]
        for byte in row:
            rgb += bytes(palette[byte >> 4]) + bytes(palette[byte & 0xF])
    return encode_png(WIDTH, HEIGHT - 8, bytes(rgb))


def error_patches(
    files: dict[str, bytes], memfix_font: bytes, layout: Path = LAYOUT
) -> list[dict[str, str]]:
    """Patches for all five ``ERR`` files (``files`` from the source image)."""
    font = Font(memfix_font, 0, 0)
    patches = []
    for screen in load_layout(layout):
        patches += diff_patches(
            screen.name, files[screen.name], render(files[screen.name], screen, font)
        )
    return patches


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--err-dir", type=Path, required=True)
    parser.add_argument("--memfix", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    parser.add_argument("--layout", type=Path, default=LAYOUT)
    args = parser.parse_args(argv)
    from tools.text.caption_compiler import FONT_ENTRY

    memfix = args.memfix.read_bytes()
    offset, length = FONT_ENTRY
    font = Font(memfix[offset : offset + length], 0, 0)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for screen in load_layout(args.layout):
        data = (args.err_dir / screen.name).read_bytes()
        new = render(data, screen, font)
        (args.out_dir / screen.name).write_bytes(new)
        stem = screen.name.removesuffix(".BIN")
        (args.out_dir / f"{stem}.png").write_bytes(preview(new))
        (args.out_dir / f"{stem}_before.png").write_bytes(preview(data))
        report[screen.name] = {
            "sha256": hashlib.sha256(new).hexdigest(),
            "patches": len(diff_patches(screen.name, data, new)),
        }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
