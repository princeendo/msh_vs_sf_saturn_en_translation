"""Search raw memory for value runs that match a symbol equality pattern.

A pattern is a sequence of tokens. A symbol token (for example ``A`` or ``17``)
stands for an unknown value. Equal symbols must have equal values, and different
symbols must have different values. A literal token ``=0x20`` must match that
value exactly, and no symbol may take a literal's value.

This finds encoded text whose character values are unknown but whose repeat
structure is known, for example from rendered glyph identities. A hit shows only
that the structure occurs.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Token:
    """A pattern element: a symbol name or a literal value."""

    symbol: str | None
    literal: int | None


@dataclass(frozen=True)
class Hit:
    """A matching offset and the symbol-to-value assignment."""

    offset: int
    mapping: dict[str, int]


def parse_pattern(text: str) -> list[Token]:
    """Parse whitespace-separated tokens; ``=N`` marks a literal value."""
    tokens = []
    for item in text.split():
        if item.startswith("="):
            tokens.append(Token(None, int(item[1:], 0)))
        else:
            tokens.append(Token(item, None))
    if not tokens:
        raise ValueError("empty pattern")
    return tokens


def read_value(data: bytes, offset: int, width: int) -> int:
    return int.from_bytes(data[offset : offset + width], "big")


def search(
    data: bytes,
    pattern: Sequence[Token],
    width: int = 2,
    stride: int | None = None,
    alignment: int | None = None,
) -> list[Hit]:
    """Return every offset whose values satisfy ``pattern``."""
    if width not in (1, 2, 4):
        raise ValueError("width must be 1, 2, or 4")
    step = stride or width
    align = alignment or width
    literals = {token.literal for token in pattern if token.literal is not None}
    first: dict[str, int] = {}
    for index, token in enumerate(pattern):
        if token.symbol is not None:
            first.setdefault(token.symbol, index)
    equal_pairs = [
        (index, first[token.symbol])
        for index, token in enumerate(pattern)
        if token.symbol is not None and first[token.symbol] != index
    ]
    fixed = [
        (index, token.literal)
        for index, token in enumerate(pattern)
        if token.literal is not None
    ]
    span = (len(pattern) - 1) * step + width
    hits: list[Hit] = []
    for offset in range(0, len(data) - span + 1, align):

        def value(index: int, base: int = offset) -> int:
            return read_value(data, base + index * step, width)

        if any(value(index) != literal for index, literal in fixed):
            continue
        if any(value(a) != value(b) for a, b in equal_pairs):
            continue
        mapping = {symbol: value(index) for symbol, index in first.items()}
        values = list(mapping.values())
        if len(set(values)) != len(values) or literals & set(values):
            continue
        hits.append(Hit(offset, mapping))
    return hits


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search raw memory for a symbol equality pattern."
    )
    parser.add_argument("dump", type=Path, help="raw memory dump")
    parser.add_argument("pattern", help="tokens, e.g. 'A B A B =0x20 C'")
    parser.add_argument("--width", type=int, default=2, help="value size in bytes")
    parser.add_argument("--stride", type=int, help="bytes between values")
    parser.add_argument(
        "--base",
        type=lambda value: int(value, 0),
        default=0,
        help="address of offset 0",
    )
    parser.add_argument("--limit", type=int, default=50, help="hits to print")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        pattern = parse_pattern(args.pattern)
        hits = search(args.dump.read_bytes(), pattern, args.width, args.stride)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    records = [
        {
            "offset": hit.offset,
            "address": f"0x{args.base + hit.offset:08X}",
            "mapping": {k: f"0x{v:0{args.width * 2}X}" for k, v in hit.mapping.items()},
        }
        for hit in hits
    ]
    if args.as_json:
        print(json.dumps({"hit_count": len(records), "hits": records}, indent=2))
        return 0
    print(f"{len(records)} hit(s)")
    for record in records[: args.limit]:
        print(f"  {record['address']}  {record['mapping']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
