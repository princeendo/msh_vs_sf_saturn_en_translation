"""Pair on-screen quote glyph cells with their 16-bit codes from save states.

For each Mednafen save state taken on a win-quote screen:

1. Extract VDP1 VRAM and WRAM-H with the validated extractor (`EXP-0008`).
2. Read the 38 quote sprites (VDP1 color word ``0x61E0``) in reading order
   (`EXP-0012`).
3. Read the 38 per-screen buffer entries at WRAM-H ``0x060ED80A``. Each entry is
   ``0x5000 | code`` followed by ``0x0002`` (`EXP-0013`).

Cell *i* is paired with code *i*. Blank cells (code ``0x0020``) are skipped. States
without 38 quote sprites, or without ``0x5xxx`` buffer entries, are reported and
skipped. A code that appears with two different cells is reported as a conflict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import (
    REGIONS,
    StateFormatError,
    extract_region,
    parse_state,
)
from tools.memory.vdp1_sprites import pixel_bytes, sprites

QUOTE_COLOR_WORD = 0x61E0
BUFFER_ADDRESS = 0x060ED80A
CELLS = 38
BLANK = 0x0020


def pair_cells(vdp1_vram: bytes, wram_h: bytes) -> dict[int, bytes] | None:
    """Return {code: 128-byte cell} for one quote screen, or None if absent."""
    cells = sorted(
        (s for s in sprites(vdp1_vram) if s.color_word == QUOTE_COLOR_WORD),
        key=lambda s: (s.y, s.x),
    )
    if len(cells) != CELLS:
        return None
    offset = BUFFER_ADDRESS - REGIONS["wram_h"].base_address
    entries = [
        int.from_bytes(wram_h[offset + 4 * i : offset + 4 * i + 2], "big")
        for i in range(CELLS)
    ]
    if any(entry >> 12 != 0x5 for entry in entries):
        return None
    pairs: dict[int, bytes] = {}
    for sprite, entry in zip(cells, entries, strict=True):
        code = entry & 0x0FFF
        if code != BLANK:
            pairs.setdefault(code, pixel_bytes(vdp1_vram, sprite))
    return pairs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Catalog quote glyph cells by code from win-screen save states."
    )
    parser.add_argument("states", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True, help="JSON (ignored path)")
    args = parser.parse_args(argv)
    catalog: dict[int, bytes] = {}
    conflicts: list[str] = []
    report = []
    for path in args.states:
        raw = path.read_bytes()
        record: dict[str, object] = {
            "state": path.name,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        try:
            state = parse_state(raw)
            vram = extract_region(state, REGIONS["vdp1_vram"], "saturn")
            wram_h = extract_region(state, REGIONS["wram_h"], "saturn")
        except StateFormatError as error:
            record["skipped"] = str(error)
            report.append(record)
            continue
        pairs = pair_cells(vram, wram_h)
        if pairs is None:
            record["skipped"] = "no quote screen"
        else:
            record["codes"] = len(pairs)
            for code, cell in pairs.items():
                if code in catalog and catalog[code] != cell:
                    conflicts.append(f"0x{code:04X} in {path.name}")
                catalog.setdefault(code, cell)
        report.append(record)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "states": report,
                "conflicts": conflicts,
                "glyphs": {
                    f"0x{c:04X}": cell.hex() for c, cell in sorted(catalog.items())
                },
            },
            indent=1,
        )
        + "\n"
    )
    print(
        json.dumps(
            {"codes": len(catalog), "conflicts": len(conflicts), "states": report},
            indent=1,
        )
    )
    return 0 if not conflicts else 1


if __name__ == "__main__":
    raise SystemExit(main())
