"""Compute and verify ECMA-130 Mode 1 sector EDC and ECC.

Raw Mode 1 sector (2,352 bytes):

| Offset | Length | Content |
| --- | --- | --- |
| 0x000 | 12 | sync |
| 0x00C | 4 | header |
| 0x010 | 2048 | user data |
| 0x810 | 4 | EDC |
| 0x814 | 8 | zero |
| 0x81C | 172 | P parity |
| 0x8C8 | 104 | Q parity |

* EDC: a 32-bit CRC over bytes 0x000-0x80F, reflected polynomial `0xD8018001`,
  stored little-endian.
* P and Q: RSPC products over GF(2^8) with field polynomial 0x11D, computed over
  bytes from 0x00C. P uses 86 columns x 24 rows (major step 2, minor step 86). Q
  uses 52 diagonals x 43 (major step 86, minor step 88).

The algorithm matches the widely used reference formulation in ECMA-130 Annex A.
It is trusted for this project only after `verify` reproduces the stored EDC/ECC
of real source sectors (see `EXP-0019`).
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAW_SECTOR = 2352
EDC_OFFSET = 0x810
P_OFFSET = 0x81C
Q_OFFSET = 0x8C8

EDC_TABLE: list[int] = []
for _value in range(256):
    _edc = _value
    for _ in range(8):
        _edc = (_edc >> 1) ^ (0xD8018001 if _edc & 1 else 0)
    EDC_TABLE.append(_edc)

ECC_F = [0] * 256
ECC_B = [0] * 256
for _i in range(256):
    _j = ((_i << 1) ^ (0x11D if _i & 0x80 else 0)) & 0xFF
    ECC_F[_i] = _j
    ECC_B[_i ^ _j] = _i


def edc(data: bytes | bytearray) -> int:
    value = 0
    for byte in data:
        value = (value >> 8) ^ EDC_TABLE[(value ^ byte) & 0xFF]
    return value


def _index_lists(
    major_count: int, minor_count: int, major_mult: int, minor_inc: int
) -> list[list[int]]:
    size = major_count * minor_count
    lists = []
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        items = []
        for _ in range(minor_count):
            items.append(index)
            index += minor_inc
            if index >= size:
                index -= size
        lists.append(items)
    return lists


P_INDEX = _index_lists(86, 24, 2, 86)
Q_INDEX = _index_lists(52, 43, 86, 88)


def _parity(src: bytes | bytearray, indexes: list[list[int]]) -> bytes:
    count = len(indexes)
    out = bytearray(2 * count)
    for major, items in enumerate(indexes):
        ecc_a = ecc_b = 0
        for index in items:
            value = src[index]
            ecc_a = ECC_F[ecc_a ^ value]
            ecc_b ^= value
        ecc_a = ECC_B[ECC_F[ecc_a] ^ ecc_b]
        out[major] = ecc_a
        out[major + count] = ecc_a ^ ecc_b
    return bytes(out)


def regenerate(sector: bytes | bytearray) -> bytes:
    """Return a Mode 1 sector with EDC, zero fill, and P/Q parity recomputed."""
    if len(sector) != RAW_SECTOR:
        raise ValueError(f"expected {RAW_SECTOR} bytes, got {len(sector)}")
    out = bytearray(sector)
    out[EDC_OFFSET : EDC_OFFSET + 4] = edc(out[:EDC_OFFSET]).to_bytes(4, "little")
    out[0x814:0x81C] = bytes(8)
    out[P_OFFSET:Q_OFFSET] = _parity(out[0xC:], P_INDEX)
    out[Q_OFFSET:RAW_SECTOR] = _parity(out[0xC:], Q_INDEX)
    return bytes(out)


def is_valid(sector: bytes | bytearray) -> bool:
    return regenerate(sector) == bytes(sector)


def _verify_range(args: tuple[str, int, int]) -> list[int]:
    path, first, count = args
    bad = []
    with open(path, "rb") as stream:
        stream.seek(first * RAW_SECTOR)
        for lsn in range(first, first + count):
            if not is_valid(stream.read(RAW_SECTOR)):
                bad.append(lsn)
    return bad


def verify_track(path: Path, workers: int = 8, chunk: int = 4096) -> list[int]:
    """Return LSNs whose stored EDC/ECC differ from recomputed values."""
    sectors = path.stat().st_size // RAW_SECTOR
    jobs = [
        (str(path), first, min(chunk, sectors - first))
        for first in range(0, sectors, chunk)
    ]
    bad: list[int] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(_verify_range, jobs):
            bad.extend(result)
    return bad


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify Mode 1 EDC/ECC of every sector in a track (read only)."
    )
    parser.add_argument("track", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    bad = verify_track(args.track, args.workers)
    sectors = args.track.stat().st_size // RAW_SECTOR
    print(
        json.dumps({"sectors": sectors, "invalid": len(bad), "first_invalid": bad[:20]})
    )
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
