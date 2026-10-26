"""Draw English attract-mode captions into the ``MVSOP*.ST2`` streams (UI-003).

The middle route of `EXP-0069`/`EXP-0071`: the caption layer's map is kept, and
the Saturn's own win-banner letters (``MEMFIX.PAC`` font, codes ``0x2E0``+) are
painted into the caption characters already on the disc. The caption palette
values are recoloured in place to the banner colours.

- **Layout** (``data/ui003/attract_captions.json``): each caption's NBG2 scroll,
  its English lines (page centre x, top y), and the caption page's pattern names
  within the visible window (char number and flips per cell; derived from
  save states by ``derive``).
- **Tiles.** A character used at one cell takes that cell's 16x16 block of the
  drawn text. A character used at several cells must receive identical blocks
  (usually empty); otherwise the layout is refused. Characters with no text are
  blanked to the background colour. Background colour index 1 is kept, so the
  banner's colour n is drawn as caption colour n + 1 (2-15).
- **Palette slots.** The converter (``0x0601FFD8``) writes array word k to CRAM
  slot k + 1 of the line, so caption colour c shows array word c - 1: the
  background (colour 1) is word 0 (``0xF000``, black), and banner colour n
  (caption colour n + 1) goes in word n.
- **Palette.** Of the five full palette loads per script (record ``0000 0800``)
  whose NBG2 lines 0x600 and 0x610 hold the Japanese captions' grey and red
  ramps, the three that start the caption slots (the first, third and fifth)
  get words 1-14 of both lines set to the banner colours (`EXP-0071`).
- **Rebuild.** Section A and the caption graphics blocks are re-encoded
  (``st2_encode``) and written over the originals in place. Each block keeps its
  header's compressed size and the original bytes after the new stream, so no
  sector moves and every following block stays where it was.

The output (patched files, patches) is game-derived: keep it under ``local/`` or
``build/`` only (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.st2_encode import lz_encode, script_encode
from tools.disc.st2_stream import (
    SECTOR,
    TAG,
    blocks,
    lz_decode,
    miss_payload,
    script_decode,
    sections,
    stream_start,
)
from tools.text.font import Font, nibble_at

LAYOUT = Path("data/ui003/attract_captions.json")
FILES = [f"MVSOP{i}.ST2" for i in range(8)]
PAGE = 32  # cells per page side; a cell is a 16x16 character
SCREEN = (352, 224)
BACKGROUND = 1  # caption colour of the background characters
FULL_LOAD = b"\x00\x00\x08\x00"  # palette record: index delta 0, 0x800 words
GREY = (0xF000, *(0xF000 | 0x111 * n for n in range(2, 16)), 0xF000)  # line 0x600
RED = (0xF000, *(0xF000 | n << 8 for n in range(2, 16)), 0xF001)  # line 0x610
# Banner colours 1-14 (VDP2 CRAM 0x11-0x1E at the captions, EXP-0069) in the
# stream's 0xFRGB form; each converts back exactly through the game's table
# at 0x06060000 (nibble n -> level [0, 2, ..., 14, 17, ..., 31]).
BANNER = (
    0xFFF0, 0xFFE0, 0xFFD0, 0xFFC0, 0xFFB0, 0xFFA0, 0xFF90,
    0xFF80, 0xFF70, 0xFF50, 0xF206, 0xF0CC, 0xF1AA, 0xF278,
)  # fmt: skip
ADVANCE = {"!": 14, " ": 16}
LETTER = 24
CAPTION_LOADS = (0, 2, 4)  # of the five ramp loads per script


class LayoutError(ValueError):
    pass


def banner_code(ch: str) -> int:
    """Top-left font code of a banner letter (2x2 cells t, t+1, t+0x10, t+0x11)."""
    punctuation = {"!": 0x348, "?": 0x34A, ".": 0x34C, "-": 0x34E}
    if ch in punctuation:
        return punctuation[ch]
    if not "A" <= ch <= "Z":
        raise LayoutError(f"no banner letter for {ch!r}")
    i = ord(ch) - 63
    return 0x2E0 + 2 * (i % 8) + 0x20 * (i // 8)


def line_width(text: str, advance: int = LETTER) -> int:
    widths = [ADVANCE.get(c, advance) for c in text[:-1]]
    return sum(widths) + (18 if text[-1] == "!" else 32)


@dataclass(frozen=True)
class Line:
    text: str
    centre: int  # page x
    top: int  # page y
    advance: int = LETTER


def draw(font: Font, lines: Sequence[Line]) -> dict[tuple[int, int], int]:
    """Banner colours (1-14) of the text pixels, keyed by page (x, y)."""
    canvas: dict[tuple[int, int], int] = {}
    for line in lines:
        x = line.centre - line_width(line.text, line.advance) // 2
        for ch in line.text:
            if ch != " ":
                code, dx = banner_code(ch), -8 if ch == "!" else 0
                for k, cell_code in enumerate((code, code + 1, code + 16, code + 17)):
                    cell = font.glyph(cell_code)[0]
                    for y in range(16):
                        for xx in range(16):
                            n = nibble_at(cell, y, xx)
                            if n:
                                px = x + dx + (k % 2) * 16 + xx
                                py = line.top + (k // 2) * 16 + y
                                canvas[(px % (PAGE * 16), py % (PAGE * 16))] = n
            x += ADVANCE.get(ch, line.advance)
    return canvas


def char_tile(canvas: dict[tuple[int, int], int], cell: int, flags: int) -> bytes:
    """A character's 128 bytes holding ``canvas`` at page ``cell`` under ``flags``
    (pattern-name word 0: bit 14 = h-flip, bit 15 = v-flip)."""
    row, col = divmod(cell, PAGE)
    hflip, vflip = (flags >> 14) & 1, (flags >> 15) & 1
    out = bytearray(128)
    for y in range(16):
        for x in range(16):
            sx, sy = 15 - x if hflip else x, 15 - y if vflip else y
            n = canvas.get((col * 16 + sx, row * 16 + sy), 0)
            value = n + 1 if n else BACKGROUND
            sub = (y // 8) * 2 + x // 8
            o = sub * 32 + (y % 8) * 4 + (x % 8) // 2
            out[o] |= value << 4 if x % 2 == 0 else value
    return bytes(out)


def paint(
    canvas: dict[tuple[int, int], int],
    cells: dict[int, tuple[int, int]],
    wanted: dict[int, bytes] | None = None,
) -> dict[int, bytes]:
    """New data for each character in ``cells`` (cell -> (char, flags)), merged
    into ``wanted`` (characters already given data by another caption).

    Characters whose every use is empty get a background tile.
    """
    wanted = {} if wanted is None else wanted
    for cell, (char, flags) in sorted(cells.items()):
        tile = char_tile(canvas, cell, flags)
        if char in wanted and wanted[char] != tile:
            raise LayoutError(
                f"char 0x{char:X} (cell {divmod(cell, PAGE)}) is shared with "
                "another cell that needs different pixels"
            )
        wanted[char] = tile
    for x, y in canvas:
        if (y // 16) * PAGE + x // 16 not in cells:
            raise LayoutError(f"text at page ({x}, {y}) is outside the caption cells")
    return wanted


def inked(tile: bytes | bytearray) -> bool:
    return any(v not in (0, BACKGROUND) for b in tile for v in (b >> 4, b & 15))


def ramp_loads(script: bytes) -> list[int]:
    """Offsets of the full palette loads whose NBG2 lines 0x600/0x610 hold the
    Japanese captions' grey and red ramps."""
    found = []
    j = script.find(FULL_LOAD)
    while j >= 0:
        body = script[j + 4 : j + 4 + 0x1000]
        if len(body) == 0x1000:
            words = struct.unpack(">2048H", body)
            if (
                words[0x600:0x610] == GREY
                and words[0x610:0x620] == RED
                and all(w == 0 or w >> 12 in (0x1, 0xF) for w in words)
            ):
                found.append(j)
        j = script.find(FULL_LOAD, j + 1)
    return found


def recolour(script: bytes) -> tuple[bytes, list[int]]:
    """Set the caption lines of the caption scenes' palette loads to the banner
    colours; return the new script and the record offsets changed.

    Each script has five ramp loads. The first, third and fifth start the
    caption slots (ヴァリアブル…/第2弾!!, 解き放て!, 広がれ!!); the second and
    fourth start character scenes, and the fourth fades the ramps into its own
    colours (`EXP-0071`), so both are left alone.
    """
    loads = ramp_loads(script)
    if len(loads) != 5:
        raise LayoutError(f"expected 5 caption-ramp palette loads, found {len(loads)}")
    out, changed = bytearray(script), [loads[i] for i in CAPTION_LOADS]
    for j in changed:
        for line in (0x600, 0x610):
            at = j + 4 + 2 * (line + 1)  # word n -> caption colour n + 1
            out[at : at + 2 * len(BANNER)] = struct.pack(f">{len(BANNER)}H", *BANNER)
    return bytes(out), changed


def overwrite_block(
    original: bytes, start: int, data: bytes, limit: int | None = None
) -> bytes:
    """Replace the LZ block at ``start`` with ``data``'s re-encoding, in place.

    A stream no longer than the original keeps the header's compressed size, and
    the bytes after it keep their original values (the decoder stops at the
    decompressed size), so a chain of blocks is undisturbed. A longer stream is
    allowed only up to ``limit`` bytes (zero padding that the game loads with
    the block, as in section C), and its header then gives the new size.
    """
    csize, size = struct.unpack_from(">II", original, start)
    if len(data) != size:
        raise LayoutError("a block's decompressed size cannot change")
    encoded = lz_encode(data)
    length = len(encoded) - 8
    if length > csize and (limit is None or length > limit):
        raise LayoutError(
            f"block at 0x{start:X} re-encodes to 0x{length:X} bytes; "
            f"0x{max(csize, limit or 0):X} available"
        )
    out = bytearray(original)
    if length > csize:
        if any(original[start + 8 + csize : start + 8 + length]):
            raise LayoutError(f"block at 0x{start:X} would overwrite data")
        out[start : start + 4] = struct.pack(">I", length)
    out[start + 8 : start + len(encoded)] = encoded[8:]
    if lz_decode(bytes(out), start)[0] != data:
        raise LayoutError(f"block at 0x{start:X} does not round-trip")
    return bytes(out)


def miss_offsets(data: bytes) -> list[int]:
    return [
        o
        for o in range(stream_start(data), len(data), SECTOR)
        if data[o : o + len(TAG)] == TAG
    ]


@dataclass(frozen=True)
class Caption:
    name: str
    lines: tuple[Line, ...]
    cells: dict[int, tuple[int, int]]  # page cell -> (char, flags)
    tiles: dict[str, tuple[str, int]]  # file -> ("C" or block "NN", delta)


def load_layout(path: Path = LAYOUT) -> list[Caption]:
    document = json.loads(path.read_text())
    captions = []
    for name, entry in document["captions"].items():
        cells = {}
        for key, value in entry["cells"].items():
            row, col = (int(v) for v in key.split(","))
            char, flags = (int(v, 16) for v in value.split(":"))
            cells[row * PAGE + col] = (char, flags)
        captions.append(
            Caption(
                name,
                tuple(
                    Line(
                        line["text"],
                        line["centre"],
                        line["top"],
                        line.get("advance", LETTER),
                    )
                    for line in entry["lines"]
                ),
                cells,
                {
                    f: (part, int(delta, 16))
                    for f, (part, delta) in entry["tiles"].items()
                },
            )
        )
    return captions


def rebuild(name: str, data: bytes, font: Font, captions: Sequence[Caption]) -> bytes:
    """``data`` (one MVSOP file) with the English captions and banner palette."""
    out = bytearray(data)
    (a0, asize), _, (c0, csection) = sections(data)[:3]
    script, _ = script_decode(data[a0 : a0 + asize])
    new_script, loads = recolour(script)
    if not loads:
        raise LayoutError(f"{name}: no caption palette loads found")
    encoded = script_encode(new_script)
    if len(encoded) > asize:
        raise LayoutError(f"{name}: section A needs 0x{len(encoded):X} bytes")
    out[a0 : a0 + len(encoded)] = encoded
    if script_decode(bytes(out[a0 : a0 + asize]))[0] != new_script:
        raise LayoutError(f"{name}: section A does not round-trip")
    parts: dict[str, bytearray] = {}
    wanted: dict[str, dict[int, bytes]] = {}
    payload = miss_payload(data)
    found = {f"{n:02d}": b for n, b in enumerate(blocks(payload))}
    for caption in captions:
        part, _ = caption.tiles[name]
        wanted[part] = paint(
            draw(font, caption.lines), caption.cells, wanted.get(part, {})
        )
    for caption in captions:
        part, delta = caption.tiles[name]
        if part not in parts:
            source = data if part == "C" else payload
            start = c0 if part == "C" else found[part].offset
            parts[part] = bytearray(lz_decode(source, start)[0])
        tiles = parts[part]
        for char, tile in wanted[part].items():
            o = char * 32 - delta
            if not 0 <= o <= len(tiles) - 128:
                raise LayoutError(f"{name}: char 0x{char:X} is outside block {part}")
            if inked(tile) or inked(tiles[o : o + 128]):
                tiles[o : o + 128] = tile
    new_payload = payload
    for part, tiles in parts.items():
        if part == "C":
            out[:] = overwrite_block(bytes(out), c0, bytes(tiles), csection - 8)
        else:
            new_payload = overwrite_block(new_payload, found[part].offset, bytes(tiles))
    if new_payload != payload:
        for k, o in enumerate(miss_offsets(data)):
            chunk = new_payload[k * (SECTOR - 4) : (k + 1) * (SECTOR - 4)]
            out[o + 4 : o + 4 + len(chunk)] = chunk
    return bytes(out)


def diff_patches(
    name: str, old: bytes, new: bytes, gap: int = 16
) -> list[dict[str, str]]:
    """Expect-checked byte patches turning ``old`` into ``new``."""
    if len(old) != len(new):
        raise LayoutError("a rebuilt file must keep its size")
    spans: list[list[int]] = []
    for i in range(len(old)):
        if old[i] != new[i]:
            if spans and i - spans[-1][1] <= gap:
                spans[-1][1] = i + 1
            else:
                spans.append([i, i + 1])
    return [
        {
            "file": name,
            "offset": f"0x{a:X}",
            "hex": new[a:b].hex(),
            "expect": old[a:b].hex(),
        }
        for a, b in spans
    ]


def st2_patches(
    files: dict[str, bytes], memfix_font: bytes, layout: Path = LAYOUT
) -> list[dict[str, str]]:
    """Patches for all eight ``MVSOP`` files (``files`` from the source image)."""
    font = Font(memfix_font, 0, 0)
    captions = load_layout(layout)
    patches = []
    for name in FILES:
        patches += diff_patches(
            name, files[name], rebuild(name, files[name], font, captions)
        )
    return patches


def derive_cells(
    map_words: Sequence[int], scroll: tuple[int, int], shared: int = 8
) -> dict[str, str]:
    """The pattern names of the cells a screen at ``scroll`` shows (``derive``),
    without the background: characters used more than ``shared`` times."""
    uses = Counter(word & 0x7FFF for word in map_words)
    x0, y0 = scroll
    rows = range(y0 // 16, (y0 + SCREEN[1] - 1) // 16 + 1)
    cols = range(x0 // 16, (x0 + SCREEN[0] - 1) // 16 + 1)
    out = {}
    for r in rows:
        for c in cols:
            word = map_words[(r % PAGE) * PAGE + c % PAGE]
            if uses[word & 0x7FFF] <= shared:
                flags = (word >> 16) & 0xC000
                out[f"{r % PAGE},{c % PAGE}"] = f"{word & 0x7FFF:X}:{flags:X}"
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    derive = sub.add_parser("derive", help="fill the layout's cells from page maps")
    derive.add_argument("--maps", type=Path, required=True, help="dir of capN/map.bin")
    derive.add_argument("--layout", type=Path, default=LAYOUT)
    build = sub.add_parser("build", help="write patched MVSOP files")
    build.add_argument("--st2-dir", type=Path, required=True)
    build.add_argument("--memfix", type=Path, required=True)
    build.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    build.add_argument("--layout", type=Path, default=LAYOUT)
    args = parser.parse_args(argv)
    if args.command == "derive":
        document = json.loads(args.layout.read_text())
        for entry in document["captions"].values():
            words = struct.unpack(
                ">1024I", (args.maps / entry["map"] / "map.bin").read_bytes()
            )
            entry["cells"] = derive_cells(words, tuple(entry["scroll"]))
        args.layout.write_text(
            json.dumps(document, indent=1, ensure_ascii=False) + "\n"
        )
        print(
            json.dumps(
                {name: len(e["cells"]) for name, e in document["captions"].items()}
            )
        )
        return 0
    from tools.text.caption_compiler import FONT_ENTRY

    memfix = args.memfix.read_bytes()
    offset, length = FONT_ENTRY
    font = Font(memfix[offset : offset + length], 0, 0)
    captions = load_layout(args.layout)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for name in FILES:
        data = (args.st2_dir / name).read_bytes()
        new = rebuild(name, data, font, captions)
        (args.out_dir / name).write_bytes(new)
        report[name] = {
            "sha256": hashlib.sha256(new).hexdigest(),
            "patches": len(diff_patches(name, data, new)),
        }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
