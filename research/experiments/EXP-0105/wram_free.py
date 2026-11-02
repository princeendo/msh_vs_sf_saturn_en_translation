"""OPT-002: WRAM-L and WRAM-H 256-byte blocks that are zero in every given state.

Usage: wram_free.py STATE_DIR [STATE_DIR ...]

Each state is extracted with ``tools.memory.mcs_extract`` (WRAM regions are
validated against debugger dumps, ``EMU-020`` V2). Prints each run of
always-zero blocks of at least 1 KiB. Zero in every recorded state is a
candidate for new code, not proof of free memory: a write log must confirm it.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

REGIONS = {"wram_l": 0x00200000, "wram_h": 0x06000000}
states = [p for d in sys.argv[1:] for p in sorted(Path(d).glob("*.mc*"))]
free: dict[str, set[int] | None] = dict.fromkeys(REGIONS)
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
                "wram_l",
                "--region",
                "wram_h",
            ],
            capture_output=True,
            check=True,
        )
        for region in REGIONS:
            m = (out / f"{region}.bin").read_bytes()
            z = {i for i in range(0, len(m), 0x100) if not any(m[i : i + 0x100])}
            seen = free[region]
            free[region] = z if seen is None else seen & z
        for f in out.iterdir():
            f.unlink()
print(len(states), "states")
for region, base in REGIONS.items():
    blocks = sorted(free[region] or ())
    runs: list[tuple[int, int]] = []
    for i in blocks:
        if runs and runs[-1][1] == i:
            runs[-1] = (runs[-1][0], i + 0x100)
        else:
            runs.append((i, i + 0x100))
    for a, b in runs:
        if b - a >= 0x400:
            print(region, hex(base + a), hex(b - a))
