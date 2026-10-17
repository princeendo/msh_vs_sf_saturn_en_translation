"""Verify forced quote-record captures against a caption-compiler build (`RE-024`).

For each capture directory (written by ``ko_capture.py``) this checks:

- **Pointer.** The stored record pointer equals ``table + 76·index``, and the
  index equals the forced index.
- **Screen.** ``quote_render.match`` on ``quote.png`` against the build's font and
  table picks the forced record.
- **RAM** (from ``quote.mc``, extractor regions validated in `EXP-0008` and
  `EMU-021` V2):
  - the cart-RAM font image equals the build's font entry;
  - WRAM-L holds the build's decoded quote table;
  - the WRAM-H display buffer (``0x060ED80A``, `EXP-0014`) holds the record's
    codes as ``0x5000|code`` entries.
- **Placeholder.** For a record with a ``0000`` placeholder, the buffer holds the
  expanded name glyphs in its place. These are reported, not assumed.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.common.png import decode_png
from tools.disc.pac_lzss import decode_file
from tools.memory.mcs_extract import REGIONS, extract_region, parse_state
from tools.text.font import Font
from tools.text.quote_render import RECORD, RECORDS, TABLE, match, record_codes

FONT_ENTRY = (0x6A558, 0x32740)
FONT_CART = 0x0278CF60
BUFFER = 0x060ED80A
PLACEHOLDER = 0x0000
BLANK = 0x0020


def buffer_codes(wram_h: bytes, count: int) -> list[int]:
    start = BUFFER - REGIONS["wram_h"].base_address
    return [
        int.from_bytes(wram_h[start + 4 * i : start + 4 * i + 2], "big")
        for i in range(count)
    ]


def expected_buffer(
    codes: Sequence[int], shown: Sequence[int]
) -> tuple[bool, list[int], list[int]]:
    """Match a record against displayed entries.

    Returns (ok, placeholder glyphs, extra entries). Entries end at the first raw
    ``0x0000``.

    - A record without a placeholder matches entry for entry.
    - With a placeholder (`RE-024`, `EXP-0026`), line 1 still holds 19 entries:
      the expanded name glyphs replace the placeholder, and line 1's trailing
      cells are dropped to make room. Line 2 follows unchanged.
    - Entries after line 2 are returned as extras. Every record observed in
      `EXP-0026` had one extra entry equal to line 2's first cell; it was not
      drawn on screen.
    """
    used = list(shown[: shown.index(0)]) if 0 in shown else list(shown)
    entries = [c & 0x0FFF for c in used]
    line = len(codes) // 2
    if PLACEHOLDER not in codes:
        return entries[: len(codes)] == list(codes), [], entries[len(codes) :]
    cut = codes.index(PLACEHOLDER)
    if cut >= line or entries[:cut] != list(codes[:cut]):
        return False, [], []
    for length in range(1, line - cut + 1):
        name = entries[cut : cut + length]
        kept = list(codes[cut + 1 : line - length + 1])
        if (
            BLANK not in name
            and entries[cut + length : line] == kept
            and entries[line : 2 * line] == list(codes[line:])
        ):
            return True, name, entries[2 * line :]
    return False, [], []


def verify_run(run: Path, font_image: bytes, decoded: bytes) -> dict[str, object]:
    capture = json.loads((run / "capture.json").read_text())
    index = int(capture["index"])
    pointer = int(capture["pointer"], 16)
    codes = record_codes(decoded, index)
    font = Font(font_image, 0, 0)
    records = [record_codes(decoded, r) for r in range(RECORDS)]
    ranked = match(decode_png((run / "quote.png").read_bytes()), font, records)
    state = parse_state((run / "quote.mc").read_bytes())
    cart = extract_region(state, REGIONS["cart_ram"], "saturn")
    wram_l = extract_region(state, REGIONS["wram_l"], "saturn")
    wram_h = extract_region(state, REGIONS["wram_h"], "saturn")
    cart_offset = FONT_CART - REGIONS["cart_ram"].base_address
    table_offset = 0x002091AC - REGIONS["wram_l"].base_address
    buffer_ok, name, extra = expected_buffer(codes, buffer_codes(wram_h, 60))
    checks: dict[str, object] = {
        "index": index,
        "pointer": f"0x{pointer:08X}",
        "pointer_ok": pointer == 0x002091AC + RECORD * index,
        "screen_best": ranked[0]["record"],
        "screen_iou": ranked[0]["iou"],
        "screen_margin": round(float(ranked[0]["iou"]) - float(ranked[1]["iou"]), 4),  # type: ignore[arg-type]
        "screen_ok": ranked[0]["record"] == index,
        "cart_font_ok": cart[cart_offset : cart_offset + len(font_image)] == font_image,
        "wram_l_table_ok": wram_l[table_offset : table_offset + RECORDS * RECORD]
        == decoded[TABLE : TABLE + RECORDS * RECORD],
        "display_buffer_ok": buffer_ok,
    }
    if name:
        checks["placeholder_glyphs"] = [f"0x{c:04X}" for c in name]
    if extra:
        checks["extra_entries"] = [f"0x{c:04X}" for c in extra]
    checks["all_ok"] = all(
        checks[k]
        for k in (
            "pointer_ok",
            "screen_ok",
            "cart_font_ok",
            "wram_l_table_ok",
            "display_buffer_ok",
        )
    )
    return checks


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--compile-dir", type=Path, required=True)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    memfix = (args.compile_dir / "files" / "MEMFIX.PAC").read_bytes()
    font_image = memfix[FONT_ENTRY[0] : FONT_ENTRY[0] + FONT_ENTRY[1]]
    decoded = decode_file((args.compile_dir / "files" / "MC09.PAC").read_bytes())[1]
    report = {run.name: verify_run(run, font_image, decoded) for run in args.runs}
    text = json.dumps(report, indent=1)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)
    return 0 if all(r["all_ok"] for r in report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
