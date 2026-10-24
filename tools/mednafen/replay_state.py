"""Replay a saved state on a given disc image and capture what happens (EXP-0036).

Mednafen Saturn states hold machine memory, not disc contents. So loading a state
saved on one image while another image is mounted replays the same moment, with
every later disc read coming from the new image. That turns a gameplay-reached
moment, such as the stage map before a fight loads, into an automatic test of a
modified image.

The tool launches the patched Mednafen (agent interface, `EMU-021`) on ``cue``,
loads ``state``, then runs ``--steps`` x ``--step-frames`` frames. After each step
it takes a screenshot. Optionally it logs breakpoint hits (``--bp kind:ranges``)
or halts on a PC range and records registers, the stack, and work RAM
(``--halt-pc``). Mednafen is closed afterwards. All outputs go to ``out``, an
ignored path.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import Agent

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
WRAM_BYTES = 1 << 20


def connect(directory: Path, timeout: float = 30.0) -> Agent:
    deadline = time.time() + timeout
    while True:
        try:
            agent = Agent(directory, 10)
            agent.status()
            return agent
        except Exception:
            if time.time() > deadline:
                raise
            time.sleep(0.5)


def wait_halted(agent: Agent, timeout: float) -> bool:
    deadline = time.time() + timeout
    while not agent.halted():
        if time.time() > deadline:
            return False
        time.sleep(0.05)
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cue", type=Path, help="disc image CUE (read only)")
    parser.add_argument("state", type=Path, help="Mednafen save state")
    parser.add_argument("out", type=Path, help="output directory (ignored path)")
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--step-frames", type=int, default=120)
    parser.add_argument("--bp", default="", help="log hits, e.g. write:2010001F")
    parser.add_argument(
        "--halt-pc", default="", help="halt on a PC range, e.g. 0-7FFFF"
    )
    parser.add_argument("--agent-dir", type=Path, default=Path("local/mednafen/agent"))
    parser.add_argument("--home", type=Path, default=Path("local/mednafen"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(args.home.resolve()),
        MEDNAFEN_AGENT_DIR=str(args.agent_dir.resolve()),
    )
    with (out / "mednafen.log").open("w") as log:
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
            agent.clear_events()
            if args.bp:
                kind, ranges = args.bp.split(":", 1)
                agent.bpmode("log")
                agent.breakpoints(kind, ranges.split(","))
            if args.halt_pc:
                agent.bpmode("halt")
                agent.breakpoints("pc", [args.halt_pc])
                if wait_halted(agent, args.steps * args.step_frames / 60 + 10):
                    regs = agent.regs()
                    stack = agent.bus_read(regs["R15"], 32)
                    (out / "regs.txt").write_text(
                        " ".join(f"{k}={v:X}" for k, v in regs.items())
                        + f"\nstack {stack.hex(' ')}\n"
                    )
                    agent.screenshot(out / "halt.png")
                    for space in ("workramh", "workraml"):
                        agent.command(f"read {space} 0 {WRAM_BYTES} {out / space}.bin")
                print(f"status {agent.status()}")
                return 0
            for step in range(1, args.steps + 1):
                agent.frames(args.step_frames)
                wait_halted(agent, 30)
                agent.screenshot(out / f"step{step:02d}.png")
                agent.run()
            (out / "events.log").write_text("\n".join(agent.events()))
            print(f"done {out}")
            return 0
        finally:
            proc.terminate()
            try:
                proc.wait(10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
