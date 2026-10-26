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
