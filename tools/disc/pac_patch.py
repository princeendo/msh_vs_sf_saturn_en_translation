"""Patch decoded bytes of a PAC file and re-encode it (splice or full).

The original compressed stream is kept unchanged up to the last flag group that
starts at or before the first changed decoded offset. Only the rest is
re-encoded with ``pac_lzss.encode``. The new file is verified by decoding it
again. Inputs are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.pac_lzss import (
    HEADER_SIZE,
    PacFormatError,
    build_pac,
    decode_file,
    encode,
    group_starts,
)


def parse_write(text: str) -> tuple[int, int]:
    offset, _, value = text.partition("=")
    if not value:
        raise ValueError(f"expected OFFSET=VALUE, got {text!r}")
    return int(offset, 0), int(value, 0)


def patch(
    data: bytes,
    writes: Sequence[tuple[int, int]],
    keep_size: bool = True,
    full: bool = False,
) -> tuple[bytes, dict[str, object]]:
    """Return the patched PAC file and a description of every change."""
    header, decoded, _ = decode_file(data)
    stream = data[HEADER_SIZE : HEADER_SIZE + header.compressed_length]
    patched = bytearray(decoded)
    changes = []
    for offset, value in sorted(writes):
        if offset % 2 or not 0 <= offset <= len(decoded) - 2:
            raise PacFormatError(f"invalid 16-bit write offset 0x{offset:X}")
        before = bytes(patched[offset : offset + 2])
        patched[offset : offset + 2] = value.to_bytes(2, "big")
        changes.append(
            {
                "decoded_offset": f"0x{offset:04X}",
                "original": before.hex(),
                "modified": f"{value:04x}",
            }
        )
    first = min(offset for offset, _ in writes)
    if full:
        stream_offset, output_offset = 0, 0
    else:
        stream_offset, output_offset = max(
            (item for item in group_starts(stream, len(decoded)) if item[1] <= first),
            key=lambda item: item[1],
        )
    new_stream = stream[:stream_offset] + encode(bytes(patched), output_offset)
    new_file = build_pac(
        new_stream, header.decompressed_length, len(data) if keep_size else None
    )
    check_header, check_decoded, used = decode_file(new_file)
    if check_decoded != bytes(patched) or used != len(new_stream):
        raise PacFormatError("re-encoded file does not decode to the patched data")
    info: dict[str, object] = {
        "original_size": len(data),
        "original_sha256": hashlib.sha256(data).hexdigest(),
        "original_compressed_length": header.compressed_length,
        "splice_stream_offset": stream_offset,
        "splice_output_offset": output_offset,
        "new_compressed_length": len(new_stream),
        "new_header_words": [f"0x{w:08X}" for w in check_header.words],
        "new_size": len(new_file),
        "zero_fill_bytes": len(new_file) - HEADER_SIZE - len(new_stream),
        "new_sha256": hashlib.sha256(new_file).hexdigest(),
        "decoded_original_sha256": hashlib.sha256(decoded).hexdigest(),
        "decoded_patched_sha256": hashlib.sha256(patched).hexdigest(),
        "unchanged_stream_prefix_bytes": stream_offset,
        "changes": changes,
    }
    return new_file, info


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Patch decoded 16-bit values in a PAC file and re-encode it."
    )
    parser.add_argument("pac", type=Path, help="source PAC (read only)")
    parser.add_argument("--write", action="append", type=parse_write, default=[])
    parser.add_argument("--out", type=Path, required=True, help="new PAC path")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--full",
        action="store_true",
        help="re-encode the whole stream instead of splicing",
    )
    parser.add_argument(
        "--allow-size-change",
        action="store_true",
        help="do not zero-fill to the original size",
    )
    args = parser.parse_args(argv)
    if not args.write:
        parser.error("give at least one --write")
    if args.out.resolve() == args.pac.resolve():
        parser.error("output would overwrite the input")
    try:
        new_file, info = patch(
            args.pac.read_bytes(), args.write, not args.allow_size_change, args.full
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(new_file)
    args.manifest.write_text(json.dumps(info, indent=2) + "\n")
    summary = {k: v for k, v in info.items() if k != "changes"}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
