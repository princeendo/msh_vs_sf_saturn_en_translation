"""OPT-005: does the V-blank guard call the tail routine once it has loaded?

``guard_watch.py CUE OUT [--frames N]`` boots CUE in the agent Mednafen with
CPU write breakpoints logged on the guard (``0x0601E22C``-``0x0601E253``) and
the handler's literal (``0x0600C1C0``). Every ``--shot`` frames it records
the frame, the V-blank-in handler (``0x06000A00``) and a screenshot. At the
end it saves a state and reads the tail's ``frames`` counter from cart RAM
(through ``mcs_extract``, as `EXP-0107`).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.sh2.asm import assemble
from tools.text.caption_compiler import FONT_ADDRESS, FONT_ENTRY
from tools.text.options_submenu import RESERVE, SOURCE

CART_BASE = 0x02400000


def counter_address() -> int:
    _, symbols = assemble(SOURCE.read_text(), FONT_ADDRESS + FONT_ENTRY[1] - RESERVE)
    return symbols["frames"]


def cart_long(state: Path, address: int) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, "-m", "tools.memory.mcs_extract", str(state),
             "--region", "cart_ram", "--out-dir", tmp],
            check=True,
            capture_output=True,
        )  # fmt: skip
        cart = (Path(tmp) / "cart_ram.bin").read_bytes()
    offset = address - CART_BASE
    return int.from_bytes(cart[offset : offset + 4], "big")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--frames", type=int, default=20000)
    parser.add_argument("--shot", type=int, default=1000)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    agent_dir = out / "agent"
    home = quiet_home(target=Path("local/mednafen_quiet_opt004"))
    env = dict(
        os.environ, MEDNAFEN_HOME=str(home.resolve()), MEDNAFEN_AGENT_DIR=str(agent_dir)
    )
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            agent = connect(agent_dir)
            agent.pause()
            agent.wait_halted()
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("write", ["0601E22C-0601E253", "0600C1C0-0600C1C3"])
            frame = int(agent.status()["frame"])
            while frame < args.frames:
                step = min(args.shot, args.frames - frame)
                agent.frames(step)
                agent.wait_halted(max(60.0, step / 20))
                frame = int(agent.status()["frame"])
                handler = agent.bus_read(0x06000A00, 4).hex()
                agent.screenshot(out / f"f{frame:08d}.png")
                print(f"frame {frame} V-blank-in {handler}", flush=True)
            agent.breakpoints("write")
            agent.bpmode("halt")
            hits = [e for e in agent.events() if e.startswith("hit ")]
            (out / "hits.log").write_text("\n".join(hits) + "\n")
            by = Counter(
                (dict(p.split("=", 1) for p in h.split()[1:] if "=" in p)["frame"])
                for h in hits
            )
            print(f"write hits {len(hits)} by frame {sorted(by.items())[:10]}")
            agent.run()
            agent.savestate(out / "end.mcs")
        finally:
            proc.terminate()
            proc.wait(10)
    print(f"tail frames counter {cart_long(out / 'end.mcs', counter_address())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
