"""LOC-006: WRAM bytes that change at most three times, by one after frame argv[2]."""

import re
import sys
from collections import defaultdict
from pathlib import Path

from tools.memory import mcs_extract as mx

states = sorted(Path(sys.argv[1]).glob("f*.mcs"))
frames = [int(p.stem[1:]) for p in states]
for region, base in (("wram_h", 0x06000000), ("wram_l", 0x00200000)):
    prev = None
    steps = defaultdict(list)
    for frame, p in zip(frames, states, strict=True):
        cur = mx.extract_region(
            mx.parse_state(p.read_bytes()), mx.REGIONS[region], "saturn"
        )
        if prev is not None:
            x = (int.from_bytes(prev, "big") ^ int.from_bytes(cur, "big")).to_bytes(
                len(cur), "big"
            )
            for m in re.finditer(rb"[^\x00]", x):
                o = m.start()
                steps[o].append((frame, prev[o], cur[o]))
        prev = cur
    for o in sorted(steps):
        s = steps[o]
        late = [t for t in s if t[0] > int(sys.argv[2])]
        if len(s) <= 3 and late and all(abs(n - v) == 1 for _, v, n in late):
            print(f"{base + o:08X} {s}")
