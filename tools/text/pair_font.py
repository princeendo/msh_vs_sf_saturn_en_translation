"""Add pair glyphs to the quote font by sacrificing declared glyphs (same size).

The font image (`MEMFIX.PAC` entry 4) is unpacked with ``font_pack.unpack``. Then:

- each sacrificial code becomes empty;
- each pair is composed with ``glyph_patch.compose`` from full-width quote glyphs
  (`data/text/font_codes.json` ranges) and stored at consecutive free codes from
  ``--first-code``;
- the image is repacked.

The new image must be no larger than the entry; it is zero-filled to the exact
entry size, so the `MEMFIX` header and every other entry are unchanged. Sacrifices
are chosen by the caller (from the `EXP-0023` census), and every one is recorded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.text.font import CELL_BYTES
from tools.text.font_pack import Glyph, compress, pack, unpack
from tools.text.glyph_patch import compose

UPPER, LOWER, DIGITS = 0x08E8, 0x0902, 0x091C
# "!" EXP-0021 family; "." and "," chosen by glyph shape for TR-001 (EXP-0033);
# the rest chosen by glyph shape for the M5 roster (RE-044). The arcade uses one
# straight-quote code for both sides, so '"' maps to a single glyph.
PUNCTUATION = {
    "!": 0x08DD,
    ".": 0x08AB,
    ",": 0x08AC,
    "?": 0x08DC,
    "'": 0x08B9,
    '"': 0x08BB,
    "-": 0x08CB,
    "\u203c": 0x08DF,  # double exclamation in one cell
}


def char_code(char: str) -> int | None:
    """Return the full-width quote-style code for ``char`` (None for space)."""
    if char == " ":
        return None
    if "A" <= char <= "Z":
        return UPPER + ord(char) - ord("A")
    if "a" <= char <= "z":
        return LOWER + ord(char) - ord("a")
    if "0" <= char <= "9":
        return DIGITS + ord(char) - ord("0")
    if char in PUNCTUATION:
        return PUNCTUATION[char]
    raise ValueError(f"no full-width glyph mapping for {char!r}")


STYLES = ("quote", "credits")


def pair_glyph(cells: Sequence[bytes], pair: str, style: str = "quote") -> bytes:
    """The pair glyph for ``pair`` from the font's ``cells``.

    ``quote`` composes two full-width quote glyphs (``glyph_patch.compose``);
    ``credits`` squeezes two staff-credits glyphs (``credits_font``, FONT-011).
    """
    if style == "credits":
        from tools.text.credits_font import pair_bytes

        return pair_bytes(cells, pair)
    if style != "quote":
        raise ValueError(f"unknown glyph style {style!r}")
    blank = bytes(CELL_BYTES)
    codes = [char_code(char) for char in pair]
    return compose(*(blank if code is None else cells[code] for code in codes))


def split_pairs(text: str) -> list[str]:
    padded = text if len(text) % 2 == 0 else text + " "
    return [padded[i : i + 2] for i in range(0, len(padded), 2)]


def stored_size(glyph: Glyph) -> int:
    if glyph.kind == "empty":
        return 0
    encoded = compress(glyph.cell)
    return CELL_BYTES if glyph.kind == "raw" or len(encoded) > 0x7F else len(encoded)


def build(
    image: bytes,
    pairs: Sequence[str],
    codes: Sequence[int],
    candidates: Sequence[int],
    reusable: Sequence[int] = (),
    style: str = "quote",
    copies: dict[int, int | None] | None = None,
) -> tuple[bytes, dict[str, object]]:
    """Store ``pairs[i]`` at ``codes[i]``, emptying candidates only as needed.

    A code in ``reusable`` (a sacrificial glyph, RE-044 option A) may be non-empty:
    its glyph is emptied first and the pair stored in its place.
    """
    if len(pairs) != len(codes) or len(set(codes)) != len(codes):
        raise ValueError("need one distinct code per pair")
    header, glyphs = unpack(image)
    glyphs = list(glyphs)
    count = int.from_bytes(header[12:16], "big")
    allowed = set(reusable)
    for code in codes:
        if code >= count or (glyphs[code].kind != "empty" and code not in allowed):
            raise ValueError(
                f"code 0x{code:04X} is not a free code below 0x{count:04X}"
            )
    reused = [code for code in codes if glyphs[code].kind != "empty"]
    for code in reused:
        glyphs[code] = Glyph("empty", bytes(CELL_BYTES))
    # UI art replacements (UI-001/UI-002): a target takes a source glyph's cell,
    # or becomes empty. Sources are read from the original font.
    copies = copies or {}
    if set(copies) & set(codes):
        raise ValueError("a copy target is also a pair code")
    original = list(glyphs)
    for target, source in copies.items():
        glyphs[target] = (
            Glyph("empty", bytes(CELL_BYTES)) if source is None else original[source]
        )

    cells = [g.cell for g in glyphs]
    new = [Glyph("compressed", pair_glyph(cells, p, style)) for p in pairs]
    needed = sum(stored_size(g) for g in new)
    sacrificed: list[int] = []
    freed = 0
    current = len(pack(header, glyphs))
    for code in candidates:
        if current + needed - freed <= len(image):
            break
        if glyphs[code].kind == "empty" or code in codes or code in copies:
            continue
        freed += stored_size(glyphs[code])
        sacrificed.append(code)
    for code in sacrificed:
        glyphs[code] = Glyph("empty", bytes(CELL_BYTES))
    for code, glyph in zip(codes, new, strict=True):
        glyphs[code] = glyph
    packed = pack(header, glyphs)
    if len(packed) > len(image):
        raise ValueError(f"repacked font {len(packed)} exceeds {len(image)} bytes")
    result = packed + bytes(len(image) - len(packed))
    info: dict[str, object] = {
        "pairs": {f"0x{c:04X}": p for c, p in zip(codes, pairs, strict=True)},
        "pair_bytes": needed,
        "sacrificed": [f"0x{c:04X}" for c in sacrificed],
        "freed_bytes": freed,
        "packed_size": len(packed),
        "zero_fill": len(image) - len(packed),
    }
    if reused:
        info["reused"] = [f"0x{c:04X}" for c in reused]
    if copies:
        info["copies"] = {
            f"0x{t:04X}": None if s is None else f"0x{s:04X}" for t, s in copies.items()
        }
    return result, info


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("memfix", type=Path, help="source MEMFIX.PAC (read only)")
    parser.add_argument("--entry-offset", type=lambda v: int(v, 0), default=0x6A558)
    parser.add_argument("--entry-size", type=lambda v: int(v, 0), default=0x32740)
    parser.add_argument("--text", required=True, help="text to split into pairs")
    parser.add_argument("--first-code", type=lambda v: int(v, 0), required=True)
    parser.add_argument(
        "--candidates", type=Path, required=True, help="JSON {'unseen_codes': [...]}"
    )
    parser.add_argument("--candidate-range", default="0x0926-0x0C5F")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.resolve() == args.memfix.resolve():
        parser.error("output would overwrite the input")
    low, high = (int(v, 16) for v in args.candidate_range.split("-"))
    unseen = [
        int(c, 16) for c in json.loads(args.candidates.read_text())["unseen_codes"]
    ]
    # Highest codes first, so sacrifices come from the end of the kanji range.
    candidates = sorted((c for c in unseen if low <= c <= high), reverse=True)
    data = bytearray(args.memfix.read_bytes())
    image = bytes(data[args.entry_offset : args.entry_offset + args.entry_size])
    try:
        pairs = split_pairs(args.text)
        codes = range(args.first_code, args.first_code + len(pairs))
        new_image, info = build(image, pairs, list(codes), candidates)
    except ValueError as error:
        parser.error(str(error))
    data[args.entry_offset : args.entry_offset + args.entry_size] = new_image
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(bytes(data))
    info.update(
        {
            "tool": "tools.text.pair_font",
            "text": args.text,
            "source_sha256": hashlib.sha256(args.memfix.read_bytes()).hexdigest(),
            "font_image_sha256": hashlib.sha256(new_image).hexdigest(),
            "output_sha256": hashlib.sha256(bytes(data)).hexdigest(),
            "candidate_range": args.candidate_range,
            "code_count": f"0x{int.from_bytes(new_image[12:16], 'big'):04X}",
        }
    )
    args.manifest.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
