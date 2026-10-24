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


def group_starts(stream: bytes, length: int) -> list[tuple[int, int]]:
    """Return (stream offset, output position) at the start of each flag group."""
    starts: list[tuple[int, int]] = []
    out_pos = 0
    pos = 0
    while out_pos < length:
        starts.append((pos, out_pos))
        flags = stream[pos]
        pos += 1
        for bit in range(7, -1, -1):
            if out_pos >= length:
                break
            if not (flags >> bit) & 1:
                pos += 1
                out_pos += 1
            else:
                value = (stream[pos] << 8) | stream[pos + 1]
                pos += 2
                out_pos += (value & 0xF) + 3
    return starts


MIN_MATCH = 3
MAX_MATCH = 18
MAX_CANDIDATES = 512


def encode(data: bytes, start: int = 0) -> bytes:
    """LZSS-encode ``data[start:]``, assuming ``data[:start]`` is already output.

    Matches never reach before output position 0, and their distance is between 1
    and ``WINDOW``. Encoding is greedy with one-step lazy evaluation, and
    deterministic.
    """
    chains: dict[bytes, list[int]] = {}

    def insert(position: int) -> None:
        if position + MIN_MATCH <= len(data):
            chains.setdefault(data[position : position + MIN_MATCH], []).append(
                position
            )

    for position in range(max(0, start - WINDOW), start):
        insert(position)

    def best_match(position: int) -> tuple[int, int]:
        if position + MIN_MATCH > len(data):
            return 0, 0
        candidates = chains.get(data[position : position + MIN_MATCH], [])
        best_length = best_distance = 0
        limit = min(MAX_MATCH, len(data) - position)
        for candidate in reversed(candidates[-MAX_CANDIDATES:]):
            distance = position - candidate
            if distance > WINDOW:
                break
            length = 0
            while (
                length < limit and data[candidate + length] == data[position + length]
            ):
                length += 1
            if length > best_length:
                best_length, best_distance = length, distance
                if length == limit:
                    break
        return best_length, best_distance

    out = bytearray()
    tokens: list[bytes] = []
    flags = 0
    position = start
    while position < len(data):
        length, distance = best_match(position)
        if length >= MIN_MATCH:
            next_length, _ = best_match(position + 1)
            if next_length > length:
                length = 0
        if length >= MIN_MATCH:
            field = WINDOW - distance
            value = (field << 4) | (length - MIN_MATCH)
            tokens.append(value.to_bytes(2, "big"))
            flags |= 0x80 >> (len(tokens) - 1)
            for offset in range(length):
                insert(position + offset)
            position += length
        else:
            tokens.append(data[position : position + 1])
            insert(position)
            position += 1
        if len(tokens) == 8:
            out.append(flags)
            out += b"".join(tokens)
            tokens = []
            flags = 0
    if tokens:
        out.append(flags)
        out += b"".join(tokens)
    return bytes(out)


def build_pac(
    stream: bytes,
    decompressed_length: int,
    size: int | None = None,
    declared_length: int | None = None,
) -> bytes:
    """Return a PAC file: header, stream, 4-byte alignment, optional zero fill.

    ``declared_length`` (at least ``len(stream)``) is the compressed length the
    header states. The bytes between the stream's end and it are zero; the game
    stops decoding at ``decompressed_length`` (`EXP-0036`).
    """
    declared = len(stream) if declared_length is None else declared_length
    if declared < len(stream):
        raise PacFormatError(f"declared length {declared} < stream {len(stream)}")
    header = struct.pack(
        ">6I",
        0,
        0x80000000 | (declared + 8),
        0,
        0,
        declared,
        decompressed_length,
    )
    body = header + stream + bytes(declared - len(stream))
    body += bytes(-len(body) % 4)
    if size is not None:
        if len(body) > size:
            raise PacFormatError(f"encoded file {len(body)} exceeds size {size}")
        body += bytes(size - len(body))
    return body


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
