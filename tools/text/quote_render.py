"""Render win-quote records offline and match screenshots to records.

A record is 38 big-endian 16-bit codes: 2 lines x 19 cells (`EXP-0013`,
`EXP-0018`). Each cell's 16x16 glyph is drawn from the quote font image
(`MEMFIX.PAC` entry 4, `EXP-0022`) at a 16-pixel step on both axes. ``0x0000`` (the
partner-name placeholder, `HYPOTHESIS`) is drawn empty, because its content is
supplied at run time.

Matching compares glyph body pixels (nibble 1) with screenshot pixels whose
channels are all at least ``BODY_MIN`` (body colour `(240, 240, 240)` in Mednafen
screenshots, measured in `RE-021`). For each record, the best score over a small
offset window around the origin is kept. The score is intersection over union of
the two pixel sets. Only the text box region is compared.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.common.png import Image, decode_png
from tools.disc.pac_lzss import decode_file
from tools.memory.mcs_extract import encode_png
from tools.text.font import Font, nibble_at

CELLS, LINE_CELLS, RECORD = 38, 19, 76
STEP = 16
TABLE = 0x91AC
RECORDS = 16
PLACEHOLDER = 0x0000
BODY, SHADOW = 1, 15
BODY_MIN = 200
ORIGIN = (26, 186)  # top-left of line-1 cell 0 in a 352x240 screenshot (RE-021)
REGION = (16, 176, 336, 232)  # x0, y0, x1, y1 of the compared text box


def record_codes(decoded: bytes, index: int, table: int = TABLE) -> list[int]:
    start = table + index * RECORD
    return [
        int.from_bytes(decoded[start + 2 * i : start + 2 * i + 2], "big")
        for i in range(CELLS)
    ]


def cell_origin(cell: int) -> tuple[int, int]:
    line, column = divmod(cell, LINE_CELLS)
    return column * STEP, line * STEP


def nibbles(font: Font, codes: Sequence[int]) -> dict[tuple[int, int], int]:
    """Non-zero nibbles of a record, keyed by (x, y) relative to the origin."""
    pixels: dict[tuple[int, int], int] = {}
    for cell, code in enumerate(codes):
        if code == PLACEHOLDER:
            continue
        glyph, _ = font.glyph(code)
        left, top = cell_origin(cell)
        for row in range(16):
            for column in range(16):
                value = nibble_at(glyph, row, column)
                if value:
                    pixels[(left + column, top + row)] = value
    return pixels


def body_mask(font: Font, codes: Sequence[int]) -> set[tuple[int, int]]:
    return {xy for xy, value in nibbles(font, codes).items() if value == BODY}


def render(font: Font, records: Sequence[Sequence[int]], scale: int = 2) -> bytes:
    """Draw records one under another as a PNG (body white, shadow dark gray)."""
    width = LINE_CELLS * STEP + 8
    band = 2 * STEP + 8
    height = band * len(records)
    pixels = bytearray(width * height * 3)
    for index, codes in enumerate(records):
        for (x, y), value in nibbles(font, codes).items():
            shade = 240 if value == BODY else 60 if value == SHADOW else 160
            offset = ((index * band + 4 + y) * width + 4 + x) * 3
            pixels[offset : offset + 3] = bytes((shade, shade, shade))
    if scale > 1:
        pixels = _scale(pixels, width, height, scale)
        width, height = width * scale, height * scale
    return encode_png(width, height, bytes(pixels))


def _scale(pixels: bytearray, width: int, height: int, scale: int) -> bytearray:
    out = bytearray()
    for y in range(height):
        row = bytearray()
        for x in range(width):
            row += pixels[(y * width + x) * 3 : (y * width + x) * 3 + 3] * scale
        out += row * scale
    return out


def screen_body(
    image: Image, region: tuple[int, int, int, int] = REGION
) -> set[tuple[int, int]]:
    x0, y0, x1, y1 = region
    return {
        (x, y)
        for y in range(y0, min(y1, image.height))
        for x in range(x0, min(x1, image.width))
        if min(image.pixel(x, y)) >= BODY_MIN
    }


def score(
    mask: set[tuple[int, int]],
    screen: set[tuple[int, int]],
    origin: tuple[int, int],
    window: int,
    region: tuple[int, int, int, int] = REGION,
) -> tuple[float, tuple[int, int]]:
    """Best IoU of ``mask`` placed near ``origin`` against ``screen``."""
    x0, y0, x1, y1 = region
    best = (0.0, origin)
    for dy in range(-window, window + 1):
        for dx in range(-window, window + 1):
            ox, oy = origin[0] + dx, origin[1] + dy
            placed = {
                (x + ox, y + oy)
                for x, y in mask
                if x0 <= x + ox < x1 and y0 <= y + oy < y1
            }
            union = len(placed | screen)
            value = len(placed & screen) / union if union else 0.0
            if value > best[0]:
                best = (value, (ox, oy))
    return best


def match(
    image: Image,
    font: Font,
    records: Sequence[Sequence[int]],
    origin: tuple[int, int] = ORIGIN,
    window: int = 3,
) -> list[dict[str, object]]:
    """Score every record against a screenshot, best first."""
    screen = screen_body(image)
    results = []
    for index, codes in enumerate(records):
        value, at = score(body_mask(font, codes), screen, origin, window)
        results.append({"record": index, "iou": round(value, 4), "origin": list(at)})
    return sorted(results, key=lambda item: -float(item["iou"]))  # type: ignore[arg-type]


def summary(decoded: bytes, table: int = TABLE) -> list[dict[str, object]]:
    rows = []
    for index in range(RECORDS):
        codes = record_codes(decoded, index, table)
        lengths = []
        for line in (codes[:LINE_CELLS], codes[LINE_CELLS:]):
            used = [i + 1 for i, code in enumerate(line) if code != 0x0020]
            lengths.append(max(used or [0]))
        rows.append(
            {
                "record": index,
                "placeholder_cells": [
                    i for i, c in enumerate(codes) if c == PLACEHOLDER
                ],
                "line_lengths": lengths,
            }
        )
    return rows


def parse_records(text: str) -> list[int]:
    out: list[int] = []
    for part in text.split(","):
        low, _, high = part.partition("-")
        out.extend(range(int(low), int(high or low) + 1))
    return out


def load(pac: Path, memfix: Path, offset: int, size: int) -> tuple[bytes, Font]:
    decoded = decode_file(pac.read_bytes())[1]
    image = memfix.read_bytes()[offset : offset + size]
    return decoded, Font(image, 0, 0)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pac", type=Path, required=True, help="quote PAC (read only)")
    parser.add_argument("--memfix", type=Path, required=True, help="MEMFIX.PAC")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument(
        "--table", type=lambda v: int(v, 0), default=TABLE, help="decoded offset"
    )
    parser.add_argument("--records", default="0-15")
    parser.add_argument("--render", type=Path, help="write a PNG (ignored path)")
    parser.add_argument("--match", type=Path, nargs="*", default=[], help="screenshots")
    parser.add_argument("--window", type=int, default=3)
    args = parser.parse_args(argv)
    decoded, font = load(args.pac, args.memfix, args.entry_offset, args.entry_size)
    indices = parse_records(args.records)
    records = [record_codes(decoded, i, args.table) for i in range(RECORDS)]
    report: dict[str, object] = {"records": summary(decoded, args.table)}
    if args.render:
        args.render.write_bytes(render(font, [records[i] for i in indices]))
    matches: dict[str, object] = {}
    for path in args.match:
        ranked = match(decode_png(path.read_bytes()), font, records, window=args.window)
        best, second = ranked[0], ranked[1]
        matches[path.name] = {
            "best": best,
            "second": second,
            "margin": round(float(best["iou"]) - float(second["iou"]), 4),  # type: ignore[arg-type]
        }
    if matches:
        report["matches"] = matches
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
