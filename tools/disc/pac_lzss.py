"""Decode the LZSS-compressed MSHvSF Saturn ``MCxx.PAC`` files.

The format was derived from the in-game decompressor observed in `EXP-0018` (PC
around ``0x0603E3E4-0x0603E454``). It was verified by decoding ``MC09.PAC`` and
comparing the output byte for byte with WRAM-L.

Header (big-endian 32-bit words):

* bytes ``0x10-0x13`` give the compressed stream length;
* bytes ``0x14-0x17`` give the decompressed length;
* other words are recorded but not interpreted.

The stream starts at ``0x18``:

* a flag byte covers the next eight items, most significant bit first;
* flag bit 0 means one literal byte;
* flag bit 1 means a two-byte match ``v``: length ``(v & 0xF) + 3`` and source
  ``out_pos - 0x1000 + ((v >> 4) & 0xFFF)``, copied byte by byte (overlaps allowed).

A match that reaches before the start of the output reads zero. That case is
unverified against hardware, and the verified file does not depend on it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

HEADER_SIZE = 0x18
WINDOW = 0x1000


class PacFormatError(ValueError):
    """Raised when a file does not decode as the expected PAC layout."""


@dataclass(frozen=True)
class PacHeader:
    """Header words of a PAC file."""

    words: tuple[int, ...]
    compressed_length: int
    decompressed_length: int


def read_header(data: bytes) -> PacHeader:
    if len(data) < HEADER_SIZE:
        raise PacFormatError("file shorter than the 0x18-byte header")
    words = struct.unpack_from(">6I", data, 0)
    return PacHeader(words, words[4], words[5])


def decompress(stream: bytes, length: int) -> tuple[bytes, int]:
    """Decode ``length`` output bytes; return (output, input bytes consumed)."""
    out = bytearray()
    pos = 0
    while len(out) < length:
        if pos >= len(stream):
            raise PacFormatError("stream ended before the declared length")
        flags = stream[pos]
        pos += 1
        for bit in range(7, -1, -1):
            if len(out) >= length:
                break
            if not (flags >> bit) & 1:
                if pos >= len(stream):
                    raise PacFormatError("stream ended inside a literal")
                out.append(stream[pos])
                pos += 1
                continue
            if pos + 1 >= len(stream):
                raise PacFormatError("stream ended inside a match")
            value = (stream[pos] << 8) | stream[pos + 1]
            pos += 2
            source = len(out) - WINDOW + ((value >> 4) & 0xFFF)
            for _ in range((value & 0xF) + 3):
                out.append(out[source] if source >= 0 else 0)
                source += 1
    return bytes(out[:length]), pos


def decode_file(data: bytes) -> tuple[PacHeader, bytes, int]:
    header = read_header(data)
    end = HEADER_SIZE + header.compressed_length
    if end > len(data):
        raise PacFormatError("compressed length exceeds the file")
    output, used = decompress(data[HEADER_SIZE:end], header.decompressed_length)
    return header, output, used


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Decode an MSHvSF Saturn PAC file.")
    parser.add_argument("pac", type=Path, nargs="+", help="PAC files (read only)")
    parser.add_argument(
        "--out-dir", type=Path, help="write <name>.bin decoded output here (ignored)"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    records = []
    for path in args.pac:
        try:
            data = path.read_bytes()
            header, output, used = decode_file(data)
        except (OSError, PacFormatError) as error:
            records.append({"file": path.name, "error": str(error)})
            continue
        if args.out_dir is not None:
            args.out_dir.mkdir(parents=True, exist_ok=True)
            (args.out_dir / (path.name.split(";")[0] + ".bin")).write_bytes(output)
        records.append(
            {
                "file": path.name,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "header": asdict(header),
                "consumed": used,
                "trailing_bytes": len(data) - HEADER_SIZE - header.compressed_length,
                "stream_fully_consumed": used == header.compressed_length,
                "decoded_length": len(output),
                "decoded_sha256": hashlib.sha256(output).hexdigest(),
            }
        )
    print(json.dumps(records, indent=2))
    return 0 if all("error" not in r for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
