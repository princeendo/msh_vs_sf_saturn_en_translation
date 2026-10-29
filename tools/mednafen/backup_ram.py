"""Write Saturn internal backup-RAM files (Mednafen ``.bkr``) for UI-008 checks.

Layout, as read from a Mednafen ``.bkr`` holding the game's save (`EXP-0104`):

- 32 KiB in 512 blocks of 64 bytes; block 0 holds "BackUpRam Format" four
  times, and blocks 0-1 are never allocated;
- a file's first block: ``80 00 00 00``, an 11-byte name, a language byte, a
  10-byte comment, a 4-byte date and a 4-byte big-endian data size (34
  bytes). Then come the numbers of its other blocks (16-bit, ending in
  ``0000``) and the data, continued in those blocks after their own 4-byte
  ``00 00 00 00`` tags.

The game's save (``MSH_VS_SF__``, 480 bytes) takes 9 blocks: its first block
and 8 more.

Kinds:

- ``zero``: all zero, as unformatted memory (the game shows ``ERR1.BIN``);
- ``freeN``: formatted, with one dummy file leaving N blocks free
  (``ERR3.BIN`` at N = 7 and 8, not at 9);
- ``corrupt``: a copy of ``--from`` with one byte of block 5 inverted (with the
  game's save there, ``ERR2.BIN``).

The output is a test fixture for an emulator's save folder, not game data.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

BLOCK, BLOCKS = 64, 512
RESERVED = 2
HEADER = 34
FORMAT = b"BackUpRam Format" * 4


def formatted() -> bytearray:
    image = bytearray(BLOCK * BLOCKS)
    image[:BLOCK] = FORMAT
    return image


def add_file(
    image: bytearray, first: int, name: bytes, size: int, others: Sequence[int]
) -> None:
    """Write a file of ``size`` zero bytes at ``first`` and ``others``."""
    head = (
        b"\x80\x00\x00\x00"
        + name.ljust(11, b"_")[:11]
        + b"\x00"
        + b"DUMMYFILE_"
        + bytes(4)
        + size.to_bytes(4, "big")
    )
    stream = b"".join(n.to_bytes(2, "big") for n in others) + bytes(2) + bytes(size)
    start = first * BLOCK
    image[start : start + HEADER] = head
    room = BLOCK - HEADER
    image[start + HEADER : start + HEADER + min(room, len(stream))] = stream[:room]
    stream = stream[room:]
    for n in others:
        chunk, stream = stream[: BLOCK - 4], stream[BLOCK - 4 :]
        image[n * BLOCK : n * BLOCK + 4] = bytes(4)
        image[n * BLOCK + 4 : n * BLOCK + 4 + len(chunk)] = chunk
    if stream:
        raise ValueError("the file does not fit its blocks")


def with_free(free: int) -> bytearray:
    """Formatted memory with exactly ``free`` unallocated blocks."""
    others = BLOCKS - RESERVED - free - 1
    if others < 0:
        raise ValueError(f"at most {BLOCKS - RESERVED - 1} blocks can be free")
    image = formatted()
    # The stream (block list, terminator, data) ends halfway into the last
    # block, so it needs every one of the ``others`` blocks (`EXP-0104` sizes).
    size = (BLOCK - 4) * others - 2 * (others + 1)
    add_file(
        image, RESERVED, b"DUMMY", size, range(RESERVED + 1, RESERVED + 1 + others)
    )
    return image


def corrupt(image: bytes) -> bytearray:
    out = bytearray(image)
    out[5 * BLOCK + 20] ^= 0xFF
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("kind", help="zero, freeN, or corrupt")
    parser.add_argument("out", type=Path, help="output .bkr (ignored path)")
    parser.add_argument("--from", dest="source", type=Path, help="for corrupt")
    args = parser.parse_args(argv)
    if args.kind == "zero":
        image = bytearray(BLOCK * BLOCKS)
    elif args.kind.startswith("free"):
        image = with_free(int(args.kind.removeprefix("free")))
    elif args.kind == "corrupt" and args.source:
        image = corrupt(args.source.read_bytes())
    else:
        parser.error("kind must be zero, freeN, or corrupt (with --from)")
    args.out.write_bytes(image)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
