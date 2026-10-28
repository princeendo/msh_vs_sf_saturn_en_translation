"""LOC-006 groundwork: cart-RAM 256-byte blocks that are zero in every given state."""

import subprocess
import sys
import tempfile
from pathlib import Path

states = [p for d in sys.argv[1:] for p in sorted(Path(d).glob("*.mc*"))]
free = None
with tempfile.TemporaryDirectory() as tmp:
    for s in states:
        out = Path(tmp) / s.stem
        subprocess.run(
            [
                "./invenv.sh",
                "python",
                "-m",
                "tools.memory.mcs_extract",
                str(s),
                "--out-dir",
                str(out),
                "--region",
                "cart_ram",
            ],
            capture_output=True,
        )
        m = (out / "cart_ram.bin").read_bytes()
        z = {i for i in range(0, len(m), 0x100) if not any(m[i : i + 0x100])}
        free = z if free is None else free & z
blocks = sorted(free)
runs, start, prev = [], None, None
for i in blocks:
    if start is None:
        start = prev = i
        continue
    if i != prev + 0x100:
        runs.append((start, prev + 0x100))
        start = i
    prev = i
if start is not None:
    runs.append((start, prev + 0x100))
print(len(states), "states")
for a, b in runs:
    if b - a >= 0x8000:
        print(hex(0x02400000 + a), hex(b - a))
