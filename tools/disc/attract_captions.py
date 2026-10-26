"""Draw the English attract-mode captions into the ``MVSOP*.ST2`` streams (UI-003).

The arcade/PS1 layout (`EXP-0067`, `EXP-0072`, `EXP-0073`) in the Saturn's own
win-banner letters (``MEMFIX.PAC`` font, codes ``0x2E0``+) and colours:

- **Slots** (``data/ui003/attract_captions.json``): each caption slot's frames
  in the section-A script, the NBG2 page halves it shows (scroll and palette
  line), its English lines and, per file, its tile block and macro origin.
- **Maps.** The caption page is built from 32x32 macro cells: index word k and
  attribute word 0x1000 + k of the NBG2 map arrays, laid out by
  ``0x0601FD70`` (``macro_slot``), each index naming four 16x16 characters at
  ``base + 16 * index``, which are 512 bytes at ``origin + 512 * index`` in the
  slot's graphics block. The script's map updates are replayed statically
  (``script_frames``) to read each caption's map. Every macro cell under the
  new text gets its own index, taken from the indices of the Japanese
  caption's glyph macros; the other cells get the background index. The map
  updates inside the caption window are rewritten so the new map holds until
  the scene's own clear (``map_encode``).
- **Text.** Lines are drawn on a 24-pixel grid (space and ``!`` included) and
  centred on the screen. The banner's colour n is drawn as caption colour
  n + 1 (2-15), keeping colour 1, the background.
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
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.st2_encode import lz_encode, map_encode, script_encode
from tools.disc.st2_stream import (
    SECTOR,
    TAG,
    blocks,
    lz_decode,
    map_decode,
    miss_payload,
    script_decode,
    script_frames,
    sections,
    stream_start,
)
from tools.text.font import Font, nibble_at

LAYOUT = Path("data/ui003/attract_captions.json")
FILES = [f"MVSOP{i}.ST2" for i in range(8)]
NBG2_MAP = 0x06037020  # index words; attributes follow at word 0x1000
ATTRIBUTES = 0x1000
SCREEN = (352, 224)
MACRO = 32  # pixels per macro cell side
HALF = (16, 8)  # macro columns and rows in one half of the caption page
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
LETTER = 24  # grid advance, as the win banner
GLYPH = 32
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


def line_width(text: str) -> int:
    return LETTER * (len(text) - 1) + GLYPH


def macro_slot(half: int, col: int, row: int) -> int:
    """Map-array index of a macro cell: ``0x0601FD70`` fills each half page
    column by column, eight rows per column."""
    return 512 * half + col * HALF[1] + row


@dataclass(frozen=True)
class Line:
    text: str
    top: int  # screen y


@dataclass(frozen=True)
class View:
    half: int  # 0 = page rows 0-7, 1 = rows 8-15
    scroll: tuple[int, int]
    palette: int


@dataclass(frozen=True)
class Slot:
    name: str
    main: int  # frame of the update that builds the caption
    until: int  # frame of the scene's own clear
    views: tuple[View, ...]
    lines: tuple[Line, ...]
    tiles: dict[str, tuple[str, int]]  # file -> ("C" or block "NN", origin)


def draw(
    font: Font, lines: Sequence[Line], scroll: tuple[int, int]
) -> dict[tuple[int, int], int]:
    """Banner colours (1-14) of the text pixels, keyed by page (x, y), for a
    screen at ``scroll``; each line is centred on the screen."""
    canvas: dict[tuple[int, int], int] = {}
    for line in lines:
        x = SCREEN[0] // 2 - line_width(line.text) // 2 + scroll[0]
        for ch in line.text:
            if ch != " ":
                code = banner_code(ch)
                for k, cell_code in enumerate((code, code + 1, code + 16, code + 17)):
                    cell = font.glyph(cell_code)[0]
                    for y in range(16):
                        for xx in range(16):
                            n = nibble_at(cell, y, xx)
                            if n:
                                px = x + (k % 2) * 16 + xx
                                py = line.top + scroll[1] + (k // 2) * 16 + y
                                canvas[(px % 512, py % 512)] = n
            x += LETTER
    return canvas


def macro_tiles(canvas: dict[tuple[int, int], int], x0: int, y0: int) -> bytes:
    """The four characters (512 bytes: top-left, top-right, bottom-left,
    bottom-right) of the macro cell whose top-left page pixel is (x0, y0)."""
    out = bytearray(512)
    for q, (dx, dy) in enumerate(((0, 0), (16, 0), (0, 16), (16, 16))):
        for y in range(16):
            for x in range(16):
                n = canvas.get((x0 + dx + x, y0 + dy + y), 0)
                value = n + 1 if n else BACKGROUND
                o = q * 128 + ((y // 8) * 2 + x // 8) * 32 + (y % 8) * 4 + (x % 8) // 2
                out[o] |= value << 4 if x % 2 == 0 else value
    return bytes(out)


def inked(tile: bytes | bytearray) -> bool:
    return any(v not in (0, BACKGROUND) for b in tile for v in (b >> 4, b & 15))


def map_states(script: bytes, frames: Sequence[int]) -> dict[int, list[int]]:
    """The NBG2 map arrays (0x2000 words) after each of ``frames``."""
    state, out = [0xFFFF] * 0x2000, {}
    wanted = set(frames)
    for n, frame in enumerate(script_frames(script)):
        for section in frame.sections:
            if section.kind == "map" and section.target == NBG2_MAP:
                for k, v in enumerate(map_decode(script, section.start)[0]):
                    if v != 0xFFFF:
                        state[k] = v
        if n in wanted:
            out[n] = list(state)
        if n >= max(wanted):
            break
    return out


@dataclass(frozen=True)
class Plan:
    words: dict[int, int]  # map-array entry -> value for the caption window
    tiles: dict[int, bytes]  # macro index -> 512 bytes (text or blank)


def plan_slot(
    script: bytes, slot: Slot, font: Font, glyph: Callable[[int], bool]
) -> Plan:
    """The caption window's map entries and the macro tiles of ``slot``.

    Free macros are the indices the caption window shows, other than the
    background and indices used elsewhere in the map, whose tiles ``glyph``
    accepts (caption ink in the slot's block). Free macros the new text does
    not need are blanked, which also leaves room for the re-encoded block.
    """
    states = map_states(script, range(slot.main, slot.until))
    cells = {
        macro_slot(view.half, c, r)
        for view in slot.views
        for c in range(HALF[0])
        for r in range(HALF[1])
    }
    counts = Counter(states[slot.main][k] for k in cells)
    background = counts.most_common(1)[0][0]
    shown = {state[k] for state in states.values() for k in cells}
    elsewhere = {
        v for k, v in enumerate(states[slot.main][:ATTRIBUTES]) if k not in cells
    }
    free = sorted(i for i in shown - elsewhere - {background, 0xFFFF} if glyph(i))
    words: dict[int, int] = {}
    tiles: dict[bytes, int] = {}
    for view in slot.views:
        canvas = draw(font, slot.lines, view.scroll)
        for c in range(HALF[0]):
            for r in range(HALF[1]):
                k = macro_slot(view.half, c, r)
                x0, y0 = c * MACRO, (8 * view.half + r) * MACRO
                data = macro_tiles(canvas, x0, y0)
                if inked(data):
                    if data not in tiles:
                        if len(tiles) == len(free):
                            raise LayoutError(
                                f"{slot.name}: needs more than {len(free)} macros"
                            )
                        tiles[data] = free[len(tiles)]
                    words[k] = tiles[data]
                else:
                    words[k] = background
                words[ATTRIBUTES + k] = view.palette
    used = {index: data for data, index in tiles.items()}
    blank = bytes([BACKGROUND * 0x11]) * 512
    return Plan(words, used | {i: blank for i in free if i not in used})


def apply_plan(script: bytes, slot: Slot, plan: Plan) -> bytes:
    """``script`` with the NBG2 map updates in the caption window rewritten: the
    main update writes every planned entry, and later updates in the window
    write the planned value wherever they touch a planned entry."""
    frames = script_frames(script)
    main = [
        s
        for s in frames[slot.main].sections
        if s.kind == "map" and s.target == NBG2_MAP
    ]
    if len(main) != 1:
        raise LayoutError(f"{slot.name}: frame {slot.main} has no caption map update")
    edits: list[tuple[int, int, bytes]] = []
    for n in range(slot.main, slot.until):
        for section in frames[n].sections:
            if section.kind != "map" or section.target != NBG2_MAP:
                continue
            words = map_decode(script, section.start)[0]
            new = list(words)
            for k, v in plan.words.items():
                if n == slot.main or words[k] != 0xFFFF:
                    new[k] = v
            if new != words:
                edits.append((section.start, section.end, map_encode(new)))
    out = bytearray(script)
    for start, end, data in reversed(edits):
        out[start:end] = data
    return bytes(out)


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


def load_layout(path: Path = LAYOUT) -> list[Slot]:
    document = json.loads(path.read_text())
    return [
        Slot(
            name,
            entry["frames"]["main"],
            entry["frames"]["until"],
            tuple(
                View(v["half"], tuple(v["scroll"]), v["palette"])
                for v in entry["views"]
            ),
            tuple(Line(line["text"], line["top"]) for line in entry["lines"]),
            {
                f: (part, int(origin, 16))
                for f, (part, origin) in entry["tiles"].items()
            },
        )
        for name, entry in document["slots"].items()
    ]


def rebuild(name: str, data: bytes, font: Font, slots: Sequence[Slot]) -> bytes:
    """``data`` (one MVSOP file) with the English captions and banner palette."""
    out = bytearray(data)
    (a0, asize), _, (c0, csection) = sections(data)[:3]
    script, _ = script_decode(data[a0 : a0 + asize])
    parts: dict[str, bytearray] = {}
    payload = miss_payload(data)
    found = {f"{n:02d}": b for n, b in enumerate(blocks(payload))}
    for slot in slots:
        part, _ = slot.tiles[name]
        if part not in parts:
            source = data if part == "C" else payload
            start = c0 if part == "C" else found[part].offset
            parts[part] = bytearray(lz_decode(source, start)[0])

    def offset(slot: Slot, index: int) -> int:
        return slot.tiles[name][1] + 512 * index

    def glyph_of(slot: Slot) -> Callable[[int], bool]:
        tiles = parts[slot.tiles[name][0]]
        return lambda i: (
            0 <= offset(slot, i) <= len(tiles) - 512
            and inked(tiles[offset(slot, i) : offset(slot, i) + 512])
        )

    plans = [(slot, plan_slot(script, slot, font, glyph_of(slot))) for slot in slots]
    for slot, plan in plans:
        script = apply_plan(script, slot, plan)
    new_script, _ = recolour(script)
    encoded = script_encode(new_script)
    if len(encoded) > asize:
        raise LayoutError(f"{name}: section A needs 0x{len(encoded):X} bytes")
    out[a0 : a0 + len(encoded)] = encoded
    if script_decode(bytes(out[a0 : a0 + asize]))[0] != new_script:
        raise LayoutError(f"{name}: section A does not round-trip")
    for slot, plan in plans:
        tiles = parts[slot.tiles[name][0]]
        for index, tile in plan.tiles.items():
            tiles[offset(slot, index) : offset(slot, index) + 512] = tile
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
    slots = load_layout(layout)
    patches = []
    for name in FILES:
        patches += diff_patches(
            name, files[name], rebuild(name, files[name], font, slots)
        )
    return patches


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--st2-dir", type=Path, required=True)
    parser.add_argument("--memfix", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    parser.add_argument("--layout", type=Path, default=LAYOUT)
    args = parser.parse_args(argv)
    from tools.text.caption_compiler import FONT_ENTRY

    memfix = args.memfix.read_bytes()
    offset, length = FONT_ENTRY
    font = Font(memfix[offset : offset + length], 0, 0)
    slots = load_layout(args.layout)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for name in FILES:
        data = (args.st2_dir / name).read_bytes()
        new = rebuild(name, data, font, slots)
        (args.out_dir / name).write_bytes(new)
        report[name] = {
            "sha256": hashlib.sha256(new).hexdigest(),
            "patches": len(diff_patches(name, data, new)),
        }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
