"""Whether one quote font can hold the pairs of several build variants.

Usage: merged_font.py BASE_SPEC [OTHER_SPEC ...]

Builds the base spec's font exactly as ``caption_compiler`` does (same track,
candidates, retired kanji, glyph style and copies). Then builds it again with
every pair the other specs use and the base does not, added as scratch fields
in a dummy raw file. Only the font is kept: the scratch writes are discarded.
For each build it prints the pair count, the free bytes left (zero fill), and
the kanji sacrificed or reused. A build that cannot fit raises ``SpecError``
or ``ValueError``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tools.disc.iso9660 import Track
from tools.disc.patch_image import find_entry
from tools.text.caption_compiler import (
    FONT_ENTRY,
    LINE_CELLS,
    MEMFIX_NAME,
    FieldSpec,
    SpecError,
    apply_patches,
    census_sources,
    compile_tables,
    load_candidates,
    parse_document,
    parse_glyph_copies,
    parse_patches,
    retired_kanji,
)

sys.path.insert(0, str(Path(__file__).parent))
from pair_union import pairs

TRACK = Path(
    "local/disc_images/mshvsf_saturn_jp/"
    "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
)
CANDIDATES = Path("data/text/font_candidates.json")
DUMMY = "SCRATCH.BIN"


def report(label: str, built: dict[str, object], count: int) -> None:
    sacrificed = built["sacrificed"]
    reused = built.get("reused", [])
    assert isinstance(sacrificed, list) and isinstance(reused, list)
    print(
        f"{label}: {count} pairs, zero fill {built['zero_fill']} bytes, "
        f"pair bytes {built['pair_bytes']}, sacrificed {len(sacrificed)}"
        f" ({built['freed_bytes']} bytes), reused {len(reused)}"
    )


def main(argv: list[str]) -> int:
    base_path, others = Path(argv[0]), [Path(a) for a in argv[1:]]
    document = json.loads(base_path.read_text())
    tables, fields = parse_document(document)
    style = str(document.get("glyph_style", "quote"))
    copies = parse_glyph_copies(document)
    raw_files = (
        {t.file for t in tables if t.raw}
        | {f.file for f in fields}
        | {p.file for p in parse_patches(document)}
    )
    pacs: dict[str, bytes] = {}
    with TRACK.open("rb") as stream:
        disc = Track(stream, TRACK.stat().st_size)
        lsn, size = find_entry(TRACK, MEMFIX_NAME)
        memfix = disc.read(lsn, size)
        for name in {t.file for t in tables} | raw_files:
            lsn, size = find_entry(TRACK, f"{name};1")
            pacs[name] = disc.read(lsn, size)
    offset, length = FONT_ENTRY
    font = memfix[offset : offset + length]
    candidates = load_candidates(CANDIDATES)
    if document.get("retire_replaced_kanji"):
        candidates += retired_kanji(census_sources(TRACK), tables, font, candidates)
    print(f"candidates: {len(candidates)} kanji")

    base = pairs(base_path)
    base_set = compile_tables(
        tables, font, pacs, candidates, fields=fields, style=style, copies=copies
    )
    report(base_path.stem, base_set.font_info, len(base))
    built = memfix[:offset] + base_set.font_image + memfix[offset + length :]
    patches = [p for p in parse_patches(document) if p.file == "MEMFIX.PAC"]
    if patches:  # the US name-call table (EXP-0058)
        built = apply_patches(built, patches)[0]
    print(f"{base_path.stem} MEMFIX.PAC sha256 {hashlib.sha256(built).hexdigest()}")

    extra = sorted(set().union(*(pairs(p) for p in others)) - base) if others else []
    scratch = [
        FieldSpec(DUMMY, i * 2, LINE_CELLS, "".join(extra[i : i + LINE_CELLS]))
        for i in range(0, len(extra), LINE_CELLS)
    ]
    pacs[DUMMY] = bytes(2 * len(extra) + 2 * LINE_CELLS)
    try:
        merged = compile_tables(
            tables,
            font,
            pacs,
            candidates,
            fields=fields + scratch,
            style=style,
            copies=copies,
        )
    except (SpecError, ValueError) as error:
        print(f"merged (+{len(extra)} pairs): does not fit: {error}")
        return 1
    report(f"merged (+{len(extra)} pairs)", merged.font_info, len(base) + len(extra))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
