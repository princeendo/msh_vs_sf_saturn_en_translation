"""Verify forced quote-record captures against a caption-compiler build (`RE-024`).

The build may hold several quote tables (`EXP-0028`). Each capture is checked
against the compiled table that WRAM-L holds at the state's table base, so a Ken
KO is verified against `MC0A` and a Ryu KO against `MC09`.

For each capture directory (written by ``ko_capture.py``) this checks:

- **Pointer.** The stored record pointer equals ``table + 76·index``, with the
  table base read from the state (``0x060F9E4A``).
- **Screen.** ``quote_render.match`` on ``quote.png`` against the build's font and
  table picks the forced record.
- **RAM** (from ``quote.mc``, extractor regions validated in `EXP-0008` and
  `EMU-021` V2):
  - the cart-RAM font image equals the build's font entry;
  - WRAM-L holds the build's decoded quote table at that base;
  - the WRAM-H display buffer (``0x060ED80A``, `EXP-0014`) holds the record's
    codes as ``0x5000|code`` entries.
- **Placeholder.** For a record with a ``0000`` placeholder, the buffer holds the
  expanded name glyphs in its place. They are reported, together with the
  matching entry of the partner-name table.
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

CompiledTable = tuple[str, int, bytes]  # file name, decoded table offset, decoded

FONT_ENTRY = (0x6A558, 0x32740)
FONT_CART = 0x0278CF60
BUFFER = 0x060ED80A
PLACEHOLDER = 0x0000
TABLE_POINTER = 0x060F9E4A  # long: quote table base (EXP-0025)
NAME_TABLE = 0x06095EC4  # partner-name glyphs, 32 bytes per entry (EXP-0025)
NAME_LENGTHS = 0x060AF8E8  # one byte per entry
NAME_ENTRIES = 26
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

    - Each line occupies 19 entries.
    - A line without a placeholder matches entry for entry.
    - A line with a placeholder (`EXP-0026`) holds the expanded name glyphs in
      the placeholder's place. Its trailing cells are dropped to keep 19 entries.
      Only line 1 was observed in M3; line 2 is the `EXP-0028` prediction.
    - Entries after line 2 are returned as extras. Every record observed in
      `EXP-0026` had one extra entry equal to line 2's first cell; it was not
      drawn on screen.
    """
    used = list(shown[: shown.index(0)]) if 0 in shown else list(shown)
    entries = [c & 0x0FFF for c in used]
    line = len(codes) // 2
    name: list[int] = []
    for start in (0, line):
        want = list(codes[start : start + line])
        got = entries[start : start + line]
        if PLACEHOLDER not in want:
            if got != want:
                return False, [], []
            continue
        cut = want.index(PLACEHOLDER)
        if got[:cut] != want[:cut]:
            return False, [], []
        for length in range(1, line - cut + 1):
            glyphs = got[cut : cut + length]
            kept = want[cut + 1 : line - length + 1]
            if BLANK not in glyphs and got[cut + length : line] == kept:
                name = glyphs
                break
        else:
            return False, [], []
    return True, name, entries[2 * line :]


def name_entry(wram_h: bytes, glyphs: Sequence[int]) -> int | None:
    """Index of the partner-name table entry equal to ``glyphs`` (None if none)."""
    base = REGIONS["wram_h"].base_address
    for entry in range(NAME_ENTRIES):
        length = wram_h[NAME_LENGTHS - base + entry]
        start = NAME_TABLE - base + 32 * entry
        codes = [
            int.from_bytes(wram_h[start + 2 * i : start + 2 * i + 2], "big")
            for i in range(length)
        ]
        if codes == list(glyphs):
            return entry
    return None


def screen_matches(records: Sequence[Sequence[int]], best: int, index: int) -> bool:
    """True if the best-matching record renders the same codes as the forced one.

    Records with identical codes draw identical screens, so a tie between them is
    a correct match (for example TR-001, where record ``k + 8`` repeats ``k``).
    """
    return list(records[best]) == list(records[index])


def verify_run(
    run: Path, font_image: bytes, tables: Sequence[CompiledTable]
) -> dict[str, object]:
    capture = json.loads((run / "capture.json").read_text())
    index = int(capture["index"])
    pointer = int(capture["pointer"], 16)
    state = parse_state((run / "quote.mc").read_bytes())
    cart = extract_region(state, REGIONS["cart_ram"], "saturn")
    wram_l = extract_region(state, REGIONS["wram_l"], "saturn")
    wram_h = extract_region(state, REGIONS["wram_h"], "saturn")
    cart_offset = FONT_CART - REGIONS["cart_ram"].base_address
    base_start = TABLE_POINTER - REGIONS["wram_h"].base_address
    base = int.from_bytes(wram_h[base_start : base_start + 4], "big")
    table_offset = base - REGIONS["wram_l"].base_address
    in_ram = wram_l[table_offset : table_offset + RECORDS * RECORD]
    matching = [t for t in tables if t[2][t[1] : t[1] + RECORDS * RECORD] == in_ram]
    name_file, table, decoded = matching[0] if matching else tables[0]
    codes = record_codes(decoded, index, table)
    font = Font(font_image, 0, 0)
    records = [record_codes(decoded, r, table) for r in range(RECORDS)]
    ranked = match(decode_png((run / "quote.png").read_bytes()), font, records)
    buffer_ok, name, extra = expected_buffer(codes, buffer_codes(wram_h, 60))
    checks: dict[str, object] = {
        "index": index,
        "pointer": f"0x{pointer:08X}",
        "table_base": f"0x{base:08X}",
        "table_file": name_file if matching else None,
        "pointer_ok": pointer == base + RECORD * index,
        "screen_best": ranked[0]["record"],
        "screen_iou": ranked[0]["iou"],
        "screen_margin": round(float(ranked[0]["iou"]) - float(ranked[1]["iou"]), 4),  # type: ignore[arg-type]
        "screen_ok": screen_matches(records, int(ranked[0]["record"]), index),  # type: ignore[call-overload]
        "cart_font_ok": cart[cart_offset : cart_offset + len(font_image)] == font_image,
        "wram_l_table_ok": bool(matching),
        "display_buffer_ok": buffer_ok,
    }
    if ranked[0]["record"] != index and checks["screen_ok"]:
        checks["screen_tie_with_identical_record"] = ranked[0]["record"]
    if name:
        checks["placeholder_glyphs"] = [f"0x{c:04X}" for c in name]
        checks["placeholder_name_entry"] = name_entry(wram_h, name)
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
    manifest = json.loads((args.compile_dir / "compile_manifest.json").read_text())
    listed = manifest.get("tables") or [{"file": "MC09.PAC", "table": f"0x{TABLE:04X}"}]
    tables = [
        (
            t["file"],
            int(t["table"], 16),
            decode_file((args.compile_dir / "files" / t["file"]).read_bytes())[1],
        )
        for t in listed
    ]
    report = {run.name: verify_run(run, font_image, tables) for run in args.runs}
    text = json.dumps(report, indent=1)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)
    return 0 if all(r["all_ok"] for r in report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
