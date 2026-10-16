"""Search raw files for exact byte patterns or explicitly encoded text.

Encodings are hypotheses chosen by the caller (for example ``shift_jis``); a match
shows only that the encoded bytes occur, not that the game stores text that way.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pattern:
    """A byte pattern and how it was produced."""

    label: str
    encoding: str | None
    data: bytes


def parse_hex(value: str) -> bytes:
    """Parse hex such as ``82A0`` or ``82 a0``."""
    cleaned = "".join(value.split())
    if not cleaned or len(cleaned) % 2:
        raise ValueError(f"invalid hex pattern: {value!r}")
    return bytes.fromhex(cleaned)


def encode_text(text: str, encoding: str) -> bytes:
    """Encode text strictly; unencodable characters are an error."""
    if not text:
        raise ValueError("empty text pattern")
    try:
        return text.encode(encoding)
    except (LookupError, UnicodeEncodeError) as error:
        raise ValueError(f"cannot encode {text!r} as {encoding}: {error}") from error


def find_all(data: bytes, pattern: bytes) -> list[int]:
    """Return every (possibly overlapping) offset of ``pattern`` in ``data``."""
    offsets = []
    start = data.find(pattern)
    while start != -1:
        offsets.append(start)
        start = data.find(pattern, start + 1)
    return offsets


def context(data: bytes, offset: int, length: int, radius: int) -> dict[str, object]:
    start = max(0, offset - radius)
    end = min(len(data), offset + length + radius)
    return {"start_offset": start, "hex": data[start:end].hex(" ")}


def search(
    paths: Sequence[Path],
    patterns: Sequence[Pattern],
    base_address: int = 0,
    radius: int = 16,
) -> dict[str, object]:
    """Search every file for every pattern and return a JSON-serializable result."""
    files = []
    for path in paths:
        data = path.read_bytes()
        results = []
        for pattern in patterns:
            offsets = find_all(data, pattern.data)
            results.append(
                {
                    "label": pattern.label,
                    "encoding": pattern.encoding,
                    "pattern_hex": pattern.data.hex(" "),
                    "match_count": len(offsets),
                    "matches": [
                        {
                            "offset": offset,
                            "address": f"0x{base_address + offset:08X}",
                            "context": context(data, offset, len(pattern.data), radius),
                        }
                        for offset in offsets
                    ],
                }
            )
        files.append(
            {
                "path": str(path),
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "results": results,
            }
        )
    return {"base_address": f"0x{base_address:08X}", "files": files}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search raw files for byte patterns or encoded text."
    )
    parser.add_argument("files", nargs="+", type=Path, help="raw files to search")
    parser.add_argument(
        "--hex", action="append", default=[], help="hex byte pattern; repeatable"
    )
    parser.add_argument(
        "--text", action="append", default=[], help="text pattern; repeatable"
    )
    parser.add_argument(
        "--encoding",
        action="append",
        default=[],
        help="encoding for --text (Python codec name); repeatable; default shift_jis",
    )
    parser.add_argument(
        "--base",
        type=lambda value: int(value, 0),
        default=0,
        help="address of offset 0 in every file",
    )
    parser.add_argument(
        "--context", type=int, default=16, help="context bytes on each side"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    encodings: list[str] = args.encoding or ["shift_jis"]
    try:
        patterns = [
            Pattern(f"hex:{value}", None, parse_hex(value)) for value in args.hex
        ]
        patterns += [
            Pattern(f"text:{text}", encoding, encode_text(text, encoding))
            for text in args.text
            for encoding in encodings
        ]
        if not patterns:
            parser.error("give at least one --hex or --text pattern")
        if args.context < 0:
            parser.error("--context must be non-negative")
        result = search(args.files, patterns, args.base, args.context)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    files = result["files"]
    assert isinstance(files, list)
    for record in files:
        print(f"{record['path']}  sha256={record['sha256']}")
        for item in record["results"]:
            print(
                f"  {item['label']} [{item['encoding'] or 'raw'}] "
                f"{item['pattern_hex']}: {item['match_count']} match(es)"
            )
            for match in item["matches"]:
                print(f"    {match['address']}  {match['context']['hex']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
