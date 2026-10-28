"""REF-012 option 2 mock-up: arcade narrow-glyph pairs vs the release pairs."""

import sys
from pathlib import Path

from tools.memory.mcs_extract import encode_png
from tools.text import credits_font as cf
from tools.text.font_pack import unpack
from tools.text.pair_font import split_pairs

PUNCT = {
    "!": 0x120,
    "?": 0x121,
    "‼": 0x122,
    '"': 0x160,
    "-": 0x12A,
    ".": 0x184,
    ",": 0x185,
    "'": 0x187,
}


def narrow_code(ch):
    if "A" <= ch <= "Z":
        return 0x140 + ord(ch) - 65
    if "a" <= ch <= "z":
        return 0x161 + ord(ch) - 97
    if "0" <= ch <= "9":
        return 0x130 + ord(ch) - 48
    return PUNCT[ch]


def narrow_pair(glyphs, pair):
    halves = []
    for ch in pair:
        if ch == " ":
            halves.append([[0] * 8 for _ in range(16)])
        else:
            halves.append([row[:8] for row in cf.grid(glyphs[narrow_code(ch)])])
    return [halves[0][r] + halves[1][r] for r in range(16)]


def box(lines, cell_fn, scale=3, cells=19):
    w, h = (cells * 16 + 16) * scale, (len(lines) * 16 + 16) * scale
    img = bytearray(bytes(cf.BOX) * (w * h))
    for li, line in enumerate(lines):
        pairs = split_pairs(line)
        start = max(0, (cells - len(pairs)) // 2)
        for pi, pair in enumerate(pairs[: cells - start]):
            cell = cell_fn(pair)
            for r in range(16):
                for c in range(16):
                    v = cell[r][c]
                    if v not in cf.GOLD:
                        continue
                    for dy in range(scale):
                        for dx in range(scale):
                            x = (8 + (start + pi) * 16 + c) * scale + dx
                            y = (8 + li * 16 + r) * scale + dy
                            img[(y * w + x) * 3 : (y * w + x) * 3 + 3] = bytes(
                                cf.GOLD[v]
                            )
    return w, h, img


def stack(images):
    w = max(i[0] for i in images)
    out = bytearray()
    for iw, ih, img in images:
        for y in range(ih):
            out += img[y * iw * 3 : (y + 1) * iw * 3] + bytes(3 * (w - iw))
        out += bytes(3 * w * 6)  # black separator
    return w, len(out) // (3 * w), bytes(out)


memfix, out = Path(sys.argv[1]), Path(sys.argv[2])
glyphs = [g.cell for g in unpack(memfix.read_bytes()[0x6A558 : 0x6A558 + 0x32740])[1]]
lines = [
    "To live is to fight, to",
    "fight is to live!",
    "Never stop improving",
    "yourself!",
    "Ah, good timing. I needed to replace",
    "When an Air Combo starter",
    "hits the opponent,",
    "Apocalypse... I'm taking",
    '"you can do it!" Bison, Akuma 2 8',
]
for name, fn in (
    ("now", lambda p: cf.caption_cell(glyphs, p)),
    ("narrow", lambda p: narrow_pair(glyphs, p)),
):
    w, h, img = box(lines, fn)
    (out / f"{name}.png").write_bytes(encode_png(w, h, img))
w, h, img = stack(
    [
        box(lines, lambda p: cf.caption_cell(glyphs, p)),
        box(lines, lambda p: narrow_pair(glyphs, p)),
    ]
)
(out / "compare.png").write_bytes(encode_png(w, h, img))
print(out / "compare.png", w, h)
