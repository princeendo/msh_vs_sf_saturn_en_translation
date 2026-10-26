"""Extract and render one VDP2 map page from a Mednafen save state (UI-003).

For a 16-colour layer with 2-word pattern names and 2x2-cell characters (the
attract-mode caption layer NBG2, `EXP-0068`), the tool reads VDP2 VRAM, CRAM and
the colour-RAM offset from the state and writes:

- ``map.bin``: the page's 32x32 pattern names (big-endian u32 each);
- ``tiles.bin`` and ``tiles.json``: the 128-byte character data of every
  character the page uses, in first-use order;
- ``page.png``: the page rendered (512x512) with the state's palette.

The VRAM in the state's ``VDP2`` section is stored as host-order u16 and is
swapped to bus order here (checked against ``mcs_extract``'s ``vdp2_vram``). The
output is game-derived: write it under ``local/`` only.
"""

from __future__ import annotations

import argparse
import json
import struct
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import encode_png, parse_state, swap_elements

PAGE_CELLS = 32
CHAR_BYTES = 128  # 2x2 cells of 8x8 4bpp


def load_vdp2(raw: bytes) -> tuple[bytes, bytes, tuple[int, ...]]:
    """(VRAM in bus order, CRAM as stored, VDP2 registers)."""
    vdp2 = parse_state(raw).sections["VDP2"]
    vram = swap_elements(vdp2["VRAM"], 2)
    registers = struct.unpack("<256H", vdp2["RawRegs"])
    return vram, vdp2["CRAM"], registers


def page_entries(vram: bytes, page: int) -> list[int]:
    return list(struct.unpack_from(f">{PAGE_CELLS * PAGE_CELLS}I", vram, page))


def render_page(
    vram: bytes, cram: bytes, entries: Sequence[int], cram_offset: int
) -> bytes:
    """RGB pixels (512x512) of a page of 2x2-cell 4bpp characters."""
    side = PAGE_CELLS * 16
    pixels = bytearray(side * side * 3)
    for index, entry in enumerate(entries):
        flags, char = entry >> 16, entry & 0x7FFF
        palette, hflip, vflip = flags & 0x7F, (flags >> 14) & 1, (flags >> 15) & 1
        top, left = (index // PAGE_CELLS) * 16, (index % PAGE_CELLS) * 16
        for sub in range(4):
            base = ((char + sub) * 32) % len(vram)
            cell = vram[base : base + 32]
            sx, sy = (sub % 2) * 8, (sub // 2) * 8
            if hflip:
                sx = 8 - sx
            if vflip:
                sy = 8 - sy
            for y in range(8):
                for x in range(8):
                    byte = cell[y * 4 + x // 2]
                    colour = (byte >> 4) if x % 2 == 0 else byte & 15
                    i = ((cram_offset << 8) + palette * 16 + colour) & 0x7FF
                    word = struct.unpack_from("<H", cram, i * 2)[0]
                    px = left + sx + (7 - x if hflip else x)
                    py = top + sy + (7 - y if vflip else y)
                    o = (py * side + px) * 3
                    pixels[o : o + 3] = bytes(
                        (
                            (word & 31) << 3,
                            ((word >> 5) & 31) << 3,
                            ((word >> 10) & 31) << 3,
                        )
                    )
    return bytes(pixels)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("state", type=Path)
    parser.add_argument("--page", type=lambda v: int(v, 0), default=0x70000)
    parser.add_argument(
        "--cram-offset-shift", type=int, default=8, help="CRAOFA bit offset (NBG2: 8)"
    )
    parser.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    args = parser.parse_args(argv)
    vram, cram, registers = load_vdp2(args.state.read_bytes())
    cram_offset = (registers[0xE4 // 2] >> args.cram_offset_shift) & 7
    entries = page_entries(vram, args.page)
    chars = list(dict.fromkeys(e & 0x7FFF for e in entries))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "map.bin").write_bytes(struct.pack(f">{len(entries)}I", *entries))
    (args.out_dir / "tiles.bin").write_bytes(
        b"".join(vram[c * 32 : c * 32 + CHAR_BYTES] for c in chars)
    )
    (args.out_dir / "tiles.json").write_text(
        json.dumps([f"0x{c:X}" for c in chars]) + "\n"
    )
    side = PAGE_CELLS * 16
    (args.out_dir / "page.png").write_bytes(
        encode_png(side, side, render_page(vram, cram, entries, cram_offset))
    )
    print(
        json.dumps(
            {
                "out_dir": str(args.out_dir),
                "chars": len(chars),
                "cram_offset": cram_offset,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
