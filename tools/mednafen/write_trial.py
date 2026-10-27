"""Apply memory writes at a checkpoint and screenshot the result (END-002).

The tool launches the patched Mednafen (agent interface, `EMU-021`) on ``cue``,
loads ``state``, pauses, and applies each ``--write SPACE:HEXADDR:HEXBYTES``,
checking each by reading it back. It then runs ``--frames`` frames, saves a
screenshot to ``out``, and reports whether each write survived (the game may
rewrite the memory meanwhile). With no ``--write`` it is the control run.
``--dump DIR`` also saves WRAM-L and WRAM-H after the frames (``workraml.bin``,
``workramh.bin``), for example to compare what a derived image loads.
Mednafen is closed afterwards.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.replay_state import (
    BINARY,
    WRAM_BYTES,
    connect,
    quiet_home,
    wait_halted,
)


def parse_write(text: str) -> tuple[str, int, bytes]:
    """Parse ``SPACE:HEXADDR:HEXBYTES``; ``HEXBYTES`` may be ``00*128``."""
    space, address, data = text.split(":", 2)
    if "*" in data:
        unit, count = data.split("*", 1)
        data = unit * int(count)
    return space, int(address, 16), bytes.fromhex(data)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path, help="disc image CUE (read only)")
    parser.add_argument("state", type=Path, help="Mednafen save state")
    parser.add_argument("out", type=Path, help="screenshot path (ignored location)")
    parser.add_argument("--write", action="append", default=[], type=parse_write)
    parser.add_argument("--frames", type=int, default=2)
    parser.add_argument(
        "--shot-at",
        type=int,
        action="append",
        default=[],
        help="also save <out stem>_f<N>.png after N frames (N < --frames)",
    )
    parser.add_argument("--dump", type=Path, help="save work RAM here after the frames")
    parser.add_argument("--agent-dir", type=Path, default=Path("local/mednafen/agent"))
    parser.add_argument("--home", type=Path, help="default: the silent quiet_home()")
    args = parser.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str((args.home or quiet_home()).resolve()),
        MEDNAFEN_AGENT_DIR=str(args.agent_dir.resolve()),
    )
    with args.out.with_suffix(".log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            agent = connect(args.agent_dir.resolve())
            time.sleep(3)  # let the boot settle before replacing the machine state
            for kind in ("write", "read", "pc"):
                agent.breakpoints(kind)
            if agent.halted():
                agent.run()
            agent.loadstate(args.state.resolve())
            agent.pause()
            wait_halted(agent, 10)
            report: list[dict[str, object]] = []
            for space, address, data in args.write:
                before = agent.read(space, address, len(data))
                agent.write(space, address, data)
                if agent.read(space, address, len(data)) != data:
                    raise SystemExit(f"write to {space}:{address:X} did not read back")
                report.append(
                    {
                        "space": space,
                        "address": f"0x{address:X}",
                        "before": before.hex(),
                    }
                )
            done = 0
            for at in sorted(set(args.shot_at)):
                if not 0 < at < args.frames:
                    raise SystemExit(
                        f"--shot-at {at} is not inside 1..{args.frames - 1}"
                    )
                agent.frames(at - done)
                wait_halted(agent, 30)
                agent.screenshot(
                    args.out.with_name(f"{args.out.stem}_f{at}.png").resolve()
                )
                done = at
            agent.frames(args.frames - done)
            wait_halted(agent, 30)
            for entry, (space, address, data) in zip(report, args.write, strict=True):
                entry["survived"] = agent.read(space, address, len(data)) == data
            agent.screenshot(args.out.resolve())
            if args.dump:
                args.dump.mkdir(parents=True, exist_ok=True)
                for space in ("workraml", "workramh"):
                    target = (args.dump / f"{space}.bin").resolve()
                    agent.command(f"read {space} 0 {WRAM_BYTES} {target}")
            print(json.dumps({"frames": args.frames, "writes": report}, indent=1))
            return 0
        finally:
            proc.terminate()
            try:
                proc.wait(10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
