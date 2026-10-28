"""Decode 16-bit Latin text from a CPS-II set's raw 68000 program ROM.

The program region is rebuilt in memory from a zip, using the pinned MAME driver
definition. Nothing is written except the requested report, which contains game
text and must go to an ignored local path. The character map is empirical
(`EXP-0029`). Codes not in it are shown as `{xxxx}` instead of being guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from tools.reference.mame_audit import RomSet, parse_driver

SPACE = 0x0020
UPPER_BASE = 0x0140  # "A"; uppercase codes are ASCII - 1 + 0x100
LOWER_BASE = 0x0161  # "a"; lowercase codes are ASCII + 0x100
DIGIT_BASE = 0x0130  # "0"; digits are ASCII + 0x100 ("before 8 am", EXP-0090)
PUNCTUATION = {
    0x0120: "!",
    0x0121: "?",
    0x0122: "\u203c",  # double exclamation, one cell (seen on screen, RE-044)
    0x0160: '"',  # straight double quote (seen on screen, RE-044)
    0x012A: "-",
    0x0184: ".",
    0x0185: ",",
    0x0186: "'",  # opening quote ("'Cause", EXP-0078); drawn as the apostrophe
    0x0187: "'",
    0x0196: "ã",
    0x019A: "á",
    0x01A3: "é",
    0x01A4: "ê",
    0x01AB: "í",
    0x01AE: "ñ",
    0x01B7: "ó",
    0x01C0: "ú",
    0x01D8: "ç",
}
UNKNOWN_TEXT_CODES = range(0x0100, 0x0200)
PHRASE = re.compile(r"[A-Za-z]{2,}\S* [A-Za-z]{2,}")


@dataclass(frozen=True)
class QuoteSlot:
    """One pointer-table slot: its target block split into quotes of lines."""

    slot: int
    address: int
    quotes: list[list[str]]


@dataclass(frozen=True)
class TextRun:
    """A maximal run of decodable words that contains at least one phrase."""

    offset: int
    text: str


def build_program(archive: Path, romset: RomSet, region: str = "maincpu") -> bytes:
    """Rebuild a word-swapped program region from a zip, in 68000 byte order."""
    entries = [rom for rom in romset.roms if rom.region == region]
    if not entries:
        raise ValueError(f"{romset.name} has no {region} ROMs")
    image = bytearray(max(rom.offset + rom.size for rom in entries))
    with zipfile.ZipFile(archive) as bundle:
        for rom in entries:
            if rom.loader != "ROM_LOAD16_WORD_SWAP":
                raise ValueError(f"unsupported loader {rom.loader} for {rom.name}")
            data = bundle.read(rom.name)
            if len(data) != rom.size:
                raise ValueError(f"{rom.name}: {len(data)} bytes, expected {rom.size}")
            swapped = bytearray(len(data))
            swapped[0::2] = data[1::2]
            swapped[1::2] = data[0::2]
            image[rom.offset : rom.offset + rom.size] = swapped
    return bytes(image)


def decode_code(code: int) -> str | None:
    """Decode one 16-bit code; None means it ends a text run."""
    if code == SPACE:
        return " "
    if UPPER_BASE <= code < UPPER_BASE + 26:
        return chr(ord("A") + code - UPPER_BASE)
    if LOWER_BASE <= code < LOWER_BASE + 26:
        return chr(ord("a") + code - LOWER_BASE)
    if DIGIT_BASE <= code < DIGIT_BASE + 10:
        return chr(ord("0") + code - DIGIT_BASE)
    if code in PUNCTUATION:
        return PUNCTUATION[code]
    if code in UNKNOWN_TEXT_CODES:
        return f"{{{code:04x}}}"
    return None


def extract_runs(
    program: bytes, start: int = 0, end: int | None = None
) -> list[TextRun]:
    """Return decodable runs in [start, end) that contain at least one phrase."""
    stop = len(program) if end is None else end
    runs: list[TextRun] = []
    chars: list[str] = []
    run_start = start
    for offset in range(start - start % 2, stop - 1, 2):
        char = decode_code(int.from_bytes(program[offset : offset + 2], "big"))
        if char is not None:
            if not chars:
                run_start = offset
            chars.append(char)
            continue
        if chars and PHRASE.search(text := "".join(chars)):
            runs.append(TextRun(run_start, text))
        chars = []
    if chars and PHRASE.search(text := "".join(chars)):
        runs.append(TextRun(run_start, text))
    return runs


def read_quote_table(
    program: bytes,
    table: int,
    slots: int,
    quotes: int = 8,
    lines: int = 2,
    width: int = 25,
) -> list[QuoteSlot]:
    """Follow big-endian longword pointers to fixed-size blocks of text lines.

    The defaults are the win-quote layout observed in `EXP-0029`. Line padding is
    kept, so centering survives; `.strip()` gives the displayed words.
    """
    result: list[QuoteSlot] = []
    for slot in range(slots):
        entry = table + 4 * slot
        address = int.from_bytes(program[entry : entry + 4], "big")
        block: list[list[str]] = []
        for quote in range(quotes):
            quote_lines = []
            for line in range(lines):
                start = address + 2 * width * (quote * lines + line)
                codes = (
                    int.from_bytes(program[i : i + 2], "big")
                    for i in range(start, start + 2 * width, 2)
                )
                quote_lines.append(
                    "".join(decode_code(c) or f"{{{c:04x}}}" for c in codes)
                )
            block.append(quote_lines)
        result.append(QuoteSlot(slot, address, block))
    return result


def text_digest(runs: Sequence[TextRun]) -> str:
    """SHA-256 of the run texts alone, for comparing sets without committing text."""
    return hashlib.sha256("\n".join(run.text for run in runs).encode()).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True, help="MAME driver .cpp")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument("--start", type=lambda v: int(v, 0), default=0)
    parser.add_argument("--end", type=lambda v: int(v, 0), default=None)
    parser.add_argument("--grep", default="", help="print runs matching this regex")
    parser.add_argument("--out", type=Path, help="write all runs as JSON (local only)")
    parser.add_argument(
        "--quote-table",
        type=lambda v: int(v, 0),
        default=None,
        help="also read a win-quote pointer table at this program address",
    )
    parser.add_argument("--slots", type=int, default=78, help="pointer-table slots")
    parser.add_argument(
        "--quotes-out", type=Path, help="write the quote table as JSON (local only)"
    )
    parser.add_argument("archive", type=Path, help="ROM zip file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    set_name = args.set_name or args.archive.stem
    if set_name not in sets:
        parser.error(f"set not defined in driver: {set_name}")
    program = build_program(args.archive, sets[set_name])
    runs = extract_runs(program, args.start, args.end)

    print(f"Set: {set_name}")
    print(f"Program SHA-256: {hashlib.sha256(program).hexdigest()}")
    print(f"Runs: {len(runs)}")
    if runs:
        print(f"Span: 0x{runs[0].offset:06x}-0x{runs[-1].offset:06x}")
    print(f"Characters: {sum(len(run.text) for run in runs)}")
    print(f"Text SHA-256: {text_digest(runs)}")
    if args.grep:
        pattern = re.compile(args.grep)
        for run in runs:
            if pattern.search(run.text):
                print(f"0x{run.offset:06x} {run.text}")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps([asdict(run) for run in runs], ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    if args.quote_table is not None:
        slots = read_quote_table(program, args.quote_table, args.slots)
        addresses = [slot.address for slot in slots]
        print(f"Quote table 0x{args.quote_table:06x}: {len(slots)} slots")
        print(f"Distinct blocks: {len(set(addresses))}")
        for slot in slots:
            first = addresses.index(slot.address)
            if first != slot.slot:
                print(f"  slot {slot.slot} shares the block of slot {first}")
        quote_text = json.dumps([asdict(slot) for slot in slots], ensure_ascii=False)
        print(f"Quote SHA-256: {hashlib.sha256(quote_text.encode()).hexdigest()}")
        if args.quotes_out:
            args.quotes_out.parent.mkdir(parents=True, exist_ok=True)
            args.quotes_out.write_text(
                json.dumps([asdict(s) for s in slots], ensure_ascii=False, indent=1),
                encoding="utf-8",
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
