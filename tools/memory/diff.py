"""Report contiguous changed byte ranges between two equal-size raw memory dumps.

Results are facts about byte equality. Optional control pairs exclude every offset
that differs between the control files, for example a same-scene, time-offset pair.
That separates bytes that change with the variable under test from bytes that
change on their own. The tool assigns no meaning to any range.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

SCHEMA_ID = "tools/memory/diff_result.schema.json"


@dataclass(frozen=True)
class ByteRange:
    """An inclusive offset range."""

    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def changed_mask(a: bytes, b: bytes) -> bytearray:
    """Return one byte per offset: 1 where ``a`` and ``b`` differ."""
    if len(a) != len(b):
        raise ValueError(f"size mismatch: {len(a)} != {len(b)}")
    return bytearray(int(x != y) for x, y in zip(a, b, strict=True))


def runs(mask: bytes | bytearray, value: int, merge_gap: int = 0) -> list[ByteRange]:
    """Return contiguous inclusive ranges where ``mask == value``.

    Runs separated by at most ``merge_gap`` other bytes are merged.
    """
    found: list[ByteRange] = []
    start: int | None = None
    for offset, item in enumerate(mask):
        if item == value and start is None:
            start = offset
        elif item != value and start is not None:
            found.append(ByteRange(start, offset - 1))
            start = None
    if start is not None:
        found.append(ByteRange(start, len(mask) - 1))
    if merge_gap <= 0 or not found:
        return found
    merged = [found[0]]
    for current in found[1:]:
        if current.start - merged[-1].end - 1 <= merge_gap:
            merged[-1] = ByteRange(merged[-1].start, current.end)
        else:
            merged.append(current)
    return merged


def file_identity(path: Path, data: bytes) -> dict[str, object]:
    return {
        "path": str(path),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def compare(
    a_path: Path,
    b_path: Path,
    base_address: int,
    controls: Sequence[tuple[Path, Path]] = (),
    merge_gap: int = 0,
    include_unchanged: bool = False,
) -> dict[str, object]:
    """Compare two dumps and return a JSON-serializable result."""
    a = a_path.read_bytes()
    b = b_path.read_bytes()
    mask = changed_mask(a, b)
    raw_changed = sum(mask)

    excluded = bytearray(len(mask))
    control_records = []
    for control_a_path, control_b_path in controls:
        control_a = control_a_path.read_bytes()
        control_b = control_b_path.read_bytes()
        if len(control_a) != len(a):
            raise ValueError(f"control size mismatch: {control_a_path}")
        control_mask = changed_mask(control_a, control_b)
        control_records.append(
            {
                "a": file_identity(control_a_path, control_a),
                "b": file_identity(control_b_path, control_b),
                "changed_bytes": sum(control_mask),
            }
        )
        for offset, item in enumerate(control_mask):
            if item:
                excluded[offset] = 1

    for offset, item in enumerate(excluded):
        if item:
            mask[offset] = 0

    def describe(found: list[ByteRange]) -> list[dict[str, object]]:
        return [
            {
                "start": f"0x{base_address + item.start:08X}",
                "end": f"0x{base_address + item.end:08X}",
                "offset": item.start,
                "length": item.length,
            }
            for item in found
        ]

    result: dict[str, object] = {
        "schema": SCHEMA_ID,
        "a": file_identity(a_path, a),
        "b": file_identity(b_path, b),
        "base_address": f"0x{base_address:08X}",
        "size_bytes": len(a),
        "merge_gap": merge_gap,
        "controls": control_records,
        "raw_changed_bytes": raw_changed,
        "excluded_bytes": sum(excluded),
        "changed_bytes": sum(mask),
        "changed_ranges": describe(runs(mask, 1, merge_gap)),
    }
    if include_unchanged:
        result["unchanged_ranges"] = describe(runs(mask, 0))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report contiguous changed ranges between two raw memory dumps."
    )
    parser.add_argument("a", type=Path, help="first raw dump")
    parser.add_argument("b", type=Path, help="second raw dump")
    parser.add_argument(
        "--base",
        type=lambda value: int(value, 0),
        default=0,
        help="address of offset 0 (e.g. 0x06000000)",
    )
    parser.add_argument(
        "--control",
        nargs=2,
        action="append",
        type=Path,
        metavar=("CONTROL_A", "CONTROL_B"),
        default=[],
        help="exclude offsets that differ between this pair; repeatable",
    )
    parser.add_argument(
        "--merge-gap",
        type=int,
        default=0,
        help="merge changed runs separated by at most this many bytes",
    )
    parser.add_argument(
        "--include-unchanged", action="store_true", help="also list unchanged ranges"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    parser.add_argument(
        "--limit", type=int, default=50, help="ranges shown in text mode"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.merge_gap < 0:
        parser.error("--merge-gap must be non-negative")
    try:
        result = compare(
            args.a,
            args.b,
            args.base,
            [tuple(pair) for pair in args.control],
            args.merge_gap,
            args.include_unchanged,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if args.as_json:
        print(json.dumps(result, indent=2))
        return 0

    ranges = result["changed_ranges"]
    assert isinstance(ranges, list)
    print(f"A: {args.a}  B: {args.b}  base: {result['base_address']}")
    print(
        f"raw changed: {result['raw_changed_bytes']}  "
        f"excluded by controls: {result['excluded_bytes']}  "
        f"changed: {result['changed_bytes']} in {len(ranges)} ranges"
    )
    for item in ranges[: args.limit]:
        print(f"  {item['start']}-{item['end']}  {item['length']} bytes")
    if len(ranges) > args.limit:
        print(f"  ... {len(ranges) - args.limit} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
