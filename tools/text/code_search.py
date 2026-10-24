"""Search raw memory dumps for 16-bit glyph-code sequences (END-003).

A pattern is a list of big-endian 16-bit hex codes; ``?`` matches any code.
Only word-aligned matches are reported. Dumps come from
``tools.memory.mcs_extract`` (Saturn byte order); a dump named ``wram_l.bin``
or ``wram_h.bin`` reports bus addresses, any other file reports file offsets.

Codes are the quote-font codes read from glyph matches (`EXP-0038`), not an
assumed encoding: a hit shows only that the sequence occurs.
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from pathlib import Path

BUS_BASES = {"wram_l": 0x00200000, "wram_h": 0x06000000}


def compile_pattern(text: str) -> re.Pattern[bytes]:
    parts = []
    for token in text.split():
        if token == "?":
            parts.append(b"..")
        else:
            parts.append(re.escape(int(token, 16).to_bytes(2, "big")))
    if not parts:
        raise ValueError("empty pattern")
    return re.compile(b"".join(parts), re.S)


def search(data: bytes, pattern: str, base: int = 0) -> list[int]:
    """Return the addresses of word-aligned matches (overlaps included)."""
    regex = compile_pattern(pattern)
    hits = []
    position = 0
    while (match := regex.search(data, position)) is not None:
        if match.start() % 2 == 0:
            hits.append(base + match.start())
        position = match.start() + 1
    return hits


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pattern", help='codes, e.g. "089C 0897 ? 08AE"')
    parser.add_argument("dumps", nargs="+", type=Path, help="raw dump files")
    args = parser.parse_args(argv)
    for dump in args.dumps:
        base = BUS_BASES.get(dump.stem, 0)
        hits = search(dump.read_bytes(), args.pattern, base)
        print(f"{dump}: {' '.join(f'0x{h:08X}' for h in hits) or 'no hits'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
