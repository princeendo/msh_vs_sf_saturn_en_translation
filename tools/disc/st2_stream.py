"""Parse the attract-mode ``.ST2`` streams and decode their graphics blocks (UI-003).

Layout (`EXP-0068`):

- **Header sector** (0x800 bytes): up to eight big-endian u32 section sizes,
  zero-terminated. The sections follow back to back from 0x800, each a
  multiple of 0x800. In ``MVSOP*.ST2``, section A (loaded to WRAM-L
  ``0x2C0000``) holds the bit-flag-LZ map streams, section B an event table,
  and section C one graphics block.
- **Stream** (after the sections): 0x800-byte sectors. Sectors that start with
  the tag ``MISS`` carry 0x7FC bytes of the graphics stream; other sectors are
  interleaved (probably audio). The concatenated ``MISS`` payloads hold
  graphics blocks, each 4-byte aligned.
- **Section A** is one script compressed with a Kosinski-like bit-flag LZ
  (``script_decode``); the game decodes it progressively through an 8 KB ring
  and a command interpreter (``0x06022426``) consumes it in order. Its map
  updates are word-LZ blocks (``map_decode``) and its palette writes come from
  handler ``0x06022242`` (`EXP-0070`).
- **Graphics block**: u32 compressed size, u32 decompressed size, then LZSS
  data, decoded by the SH-2 routine at ``0x06021EDA`` (``lz_decode``): flag
  bytes MSB first; 0 = literal byte; 1 = big-endian word ``w``, copying
  ``(w & 0xF) + 3`` bytes from ``(w >> 4) - 0x1000`` back in the output.
  A decoded block begins with a table of u32 offsets to its parts (tiles,
  palette, ...).

The output is game-derived data: write it under ``local/`` only (``AGENTS.md``
rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

SECTOR = 0x800
TAG = b"MISS"


@dataclass(frozen=True)
class Block:
    offset: int  # in the MISS payload
    compressed: int
    size: int


def sections(data: bytes) -> list[tuple[int, int]]:
    """(offset, size) of each header section."""
    sizes = [s for s in struct.unpack_from(">8I", data, 0)]
    out, offset = [], SECTOR
    for size in sizes:
        if not size:
            break
        if size % SECTOR:
            raise ValueError(f"section size 0x{size:X} is not sector-aligned")
        out.append((offset, size))
        offset += size
    return out


def stream_start(data: bytes) -> int:
    return sum(size for _, size in sections(data)) + SECTOR


def miss_payload(data: bytes) -> bytes:
    """The concatenated payloads of the stream's ``MISS`` sectors."""
    return b"".join(
        data[o + len(TAG) : o + SECTOR]
        for o in range(stream_start(data), len(data), SECTOR)
        if data[o : o + len(TAG)] == TAG
    )


def lz_decode(data: bytes, start: int = 0) -> tuple[bytes, int]:
    """Decode one graphics block at ``start``; return (output, end offset)."""
    compressed, size = struct.unpack_from(">II", data, start)
    position, end = start + 8, start + 8 + compressed
    out = bytearray()
    while len(out) < size:
        if position >= end:
            raise ValueError("block ended before its decompressed size")
        flags = data[position]
        position += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                word = (data[position] << 8) | data[position + 1]
                position += 2
                source = len(out) + (word >> 4) - 0x1000
                if source < 0:
                    raise ValueError("copy reaches before the output start")
                for k in range((word & 0xF) + 3):
                    out.append(out[source + k])
            else:
                out.append(data[position])
                position += 1
    return bytes(out[:size]), position


def script_decode(data: bytes, start: int = 0) -> tuple[bytes, int]:
    """Decode section A's bit-flag LZ (``0x06022750``); return (script, end offset).

    Flag bits are read LSB first from bytes. 1 = literal byte. 0 then 0 = short
    copy: two more flag bits (MSB first) give length 2-5, then a byte b gives the
    offset ``b - 0x100``. 0 then 1 = long copy: a big-endian word ``w`` gives the
    offset ``(w | ~0xFFFF) >> 3`` (arithmetic); length ``(w & 7) + 2`` if nonzero,
    else the next byte c gives ``c + 1``, and c = 0 ends the stream.
    """
    position, out, flags, left = start, bytearray(), 0, 0

    def bit() -> int:
        nonlocal position, flags, left
        if left == 0:
            flags, left = data[position], 8
            position += 1
        value = flags & 1
        flags >>= 1
        left -= 1
        return value

    while True:
        if bit():
            out.append(data[position])
            position += 1
            continue
        if not bit():
            length = ((bit() << 1) | bit()) + 2
            offset = data[position] - 0x100
            position += 1
        else:
            word = (data[position] << 8) | data[position + 1]
            position += 2
            offset = ((word | 0xFFFF0000) - (1 << 32)) >> 3
            if word & 7:
                length = (word & 7) + 2
            else:
                count = data[position]
                position += 1
                if count == 0:
                    return bytes(out), position
                length = count + 1
        source = len(out) + offset
        for k in range(length):
            out.append(out[source + k])


def map_decode(data: bytes, start: int) -> tuple[list[int], int]:
    """Decode one word-LZ map update (``0x0602234C``); return (0x2000 words, end).

    Control bytes are read LSB first. 1 = literal big-endian word. 0 = copy back
    in the output, from a byte b:

    - b >= 0x80: distance ``(b & 15) + 1``, length ``((b >> 4) & 7) + 1``;
    - 0 < b < 0x80: length b, then a byte d gives distance ``d + 1``;
    - b == 0: a word w; mode ``w >> 13``: 0 = length ``(w & 0x1FFF) + 1`` and a
      word distance + 1; 1 = the same length and a byte distance + 1;
      2 = distance ``(w & 0x1FFF) + 1`` and a byte length + 1.

    The game copies every word except ``0xFFFF`` (= keep) into its target array.
    """
    position, out = start, list[int]()
    while len(out) < 0x2000:
        control = data[position]
        position += 1
        for _ in range(8):
            if len(out) >= 0x2000:
                break
            if control & 1:
                out.append((data[position] << 8) | data[position + 1])
                position += 2
            else:
                byte = data[position]
                position += 1
                if byte >= 0x80:
                    distance, length = (byte & 15) + 1, ((byte >> 4) & 7) + 1
                elif byte:
                    length, distance = byte, data[position] + 1
                    position += 1
                else:
                    word = (data[position] << 8) | data[position + 1]
                    position += 2
                    mode = word >> 13
                    if mode == 0:
                        length = (word & 0x1FFF) + 1
                        distance = ((data[position] << 8) | data[position + 1]) + 1
                        position += 2
                    elif mode == 1:
                        length, distance = (word & 0x1FFF) + 1, data[position] + 1
                        position += 1
                    elif mode == 2:
                        distance, length = (word & 0x1FFF) + 1, data[position] + 1
                        position += 1
                    else:
                        raise ValueError(f"map copy mode {mode} at 0x{position:X}")
                source = len(out) - distance
                if source < 0:
                    raise ValueError("map copy reaches before the output start")
                for k in range(length):
                    out.append(out[source + k])
            control >>= 1
    if len(out) != 0x2000:
        raise ValueError("map update overran 0x2000 words")
    return out, position


def blocks(payload: bytes) -> list[Block]:
    """The graphics blocks of a ``MISS`` payload, in order."""
    found, position = [], 0
    while position + 8 <= len(payload):
        compressed, size = struct.unpack_from(">II", payload, position)
        if 0 < compressed < size < 0x80000 and position + 8 + compressed <= len(
            payload
        ):
            found.append(Block(position, compressed, size))
            position = (position + 8 + compressed + 3) & ~3
        else:
            position += 4
    return found


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("st2", type=Path, help="an extracted .ST2 file")
    parser.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    args = parser.parse_args(argv)
    data = args.st2.read_bytes()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "file": args.st2.name,
        "sections": [
            {"offset": f"0x{o:X}", "size": f"0x{s:X}"} for o, s in sections(data)
        ],
    }
    decoded = []
    third = sections(data)[2] if len(sections(data)) > 2 else None
    if third:
        out, _ = lz_decode(data, third[0])
        (args.out_dir / "section_c.bin").write_bytes(out)
        decoded.append(
            {
                "name": "section_c",
                "size": len(out),
                "sha256": hashlib.sha256(out).hexdigest(),
            }
        )
    payload = miss_payload(data)
    for number, block in enumerate(blocks(payload)):
        out, end = lz_decode(payload, block.offset)
        if end != block.offset + 8 + block.compressed:
            raise ValueError(f"block {number} did not end at its compressed size")
        name = f"block{number:02d}"
        (args.out_dir / f"{name}.bin").write_bytes(out)
        decoded.append(
            {
                "name": name,
                "payload_offset": f"0x{block.offset:X}",
                "compressed": block.compressed,
                "size": len(out),
                "sha256": hashlib.sha256(out).hexdigest(),
            }
        )
    report["miss_payload"] = len(payload)
    report["decoded"] = decoded
    (args.out_dir / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({"out_dir": str(args.out_dir), "blocks": len(decoded)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
