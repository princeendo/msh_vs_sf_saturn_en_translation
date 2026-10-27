"""Compare a rebuilt track 01 with a reference track (EXP-0084).

Usage: ``./invenv.sh python research/experiments/EXP-0084/compare_layout.py REF NEW``

Prints the sizes, the primary volume descriptors, files that moved, changed
size or changed contents, differing system-area sectors, differing raw
sectors, and both SHA-256 values.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import BinaryIO

from tools.disc.iso9660 import RAW_SECTOR, Entry, Track, primary_volume, walk

PVD_KEYS = ("system_id", "volume_id", "volume_space_size", "root_lsn", "root_size")


def open_track(
    path: Path,
) -> tuple[BinaryIO, Track, dict[str, object], dict[str, Entry]]:
    stream = path.open("rb")
    track = Track(stream, path.stat().st_size)
    volume = primary_volume(track)
    lsn, size = int(str(volume["root_lsn"])), int(str(volume["root_size"]))
    entries = {e.path.split(";")[0]: e for e in walk(track, lsn, size)}
    return stream, track, volume, entries


def main(argv: list[str]) -> int:
    ref, new = Path(argv[1]), Path(argv[2])
    fa, ta, pa, ea = open_track(ref)
    fb, tb, pb, eb = open_track(new)
    print("sizes", ref.stat().st_size, new.stat().st_size)
    print("pvd ref", {k: pa[k] for k in PVD_KEYS})
    print("pvd new", {k: pb[k] for k in PVD_KEYS})
    print("same names", sorted(ea) == sorted(eb))
    common = [n for n in ea if n in eb]
    moved = [(n, ea[n].lsn, eb[n].lsn) for n in common if ea[n].lsn != eb[n].lsn]
    resized = [n for n in common if ea[n].size_bytes != eb[n].size_bytes]
    changed = [
        n
        for n in common
        if ta.read(ea[n].lsn, ea[n].size_bytes) != tb.read(eb[n].lsn, eb[n].size_bytes)
    ]
    print("moved", len(moved), moved[:8])
    print("resized", len(resized), resized[:8])
    print("different contents", len(changed), changed[:40])
    print(
        "system-area sectors that differ",
        [i for i in range(16) if ta.user(i) != tb.user(i)],
    )
    differing, index = [], 0
    fa.seek(0)
    fb.seek(0)
    while True:
        a, b = fa.read(RAW_SECTOR * 1024), fb.read(RAW_SECTOR * 1024)
        if not a and not b:
            break
        for k in range(0, max(len(a), len(b)), RAW_SECTOR):
            if a[k : k + RAW_SECTOR] != b[k : k + RAW_SECTOR]:
                differing.append(index + k // RAW_SECTOR)
        index += max(len(a), len(b)) // RAW_SECTOR
    print("raw sectors that differ", len(differing), differing[:20])
    for path in (ref, new):
        print(path.name, hashlib.sha256(path.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
