"""LOC-006: bytes steady in window A and steady at another value in window B."""

import sys
from pathlib import Path

from tools.memory import mcs_extract as mx

states = sorted(Path(sys.argv[1]).glob("f*.mcs"))
a0, a1, b0, b1 = (int(v) for v in sys.argv[2:6])


def window(lo, hi, region):
    return [
        mx.extract_region(mx.parse_state(p.read_bytes()), mx.REGIONS[region], "saturn")
        for p in states
        if lo <= int(p.stem[1:]) <= hi
    ]


for region, base in (("wram_h", 0x06000000), ("wram_l", 0x00200000)):
    wa, wb = window(a0, a1, region), window(b0, b1, region)
    first_a, first_b = wa[0], wb[0]
    for o in range(len(first_a)):
        va, vb = first_a[o], first_b[o]
        if va != vb and all(w[o] == va for w in wa) and all(w[o] == vb for w in wb):
            # change frames across the whole session
            print(f"{base + o:08X} {va:3d} -> {vb:3d}")
