"""OPT-003: is the quote font's tail loaded at boot and never written after?

Subcommands:

- ``boot CUE OUT``: start the agent Mednafen on CUE, halt at once, log CPU
  writes to the tail (``bpmode log``), run ``--frames`` frames with a
  screenshot every ``--shot`` frames, save ``OUT/boot.mcs`` and stop.
- ``check STATE MEMFIX``: extract cart RAM from STATE and compare the font
  region with entry 4 of the built ``MEMFIX.PAC`` (font and tail separately).

The agent cannot read cart RAM (Mednafen's physical-bus peek is a TODO), so
the read-back goes through ``mcs_extract``. A 16 KiB pseudorandom marker found
byte for byte at the predicted offset also checks that extraction.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import Agent
from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.text.caption_compiler import FONT_ADDRESS, FONT_ENTRY

CART_BASE = 0x02400000


def tail_range(reserve: int) -> tuple[int, int]:
    end = FONT_ADDRESS + FONT_ENTRY[1]
    return end - reserve, end


def cart_font(state: Path) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, "-m", "tools.memory.mcs_extract", str(state),
             "--region", "cart_ram", "--out-dir", tmp],
            check=True,
            capture_output=True,
        )  # fmt: skip
        cart = (Path(tmp) / "cart_ram.bin").read_bytes()
    start = FONT_ADDRESS - CART_BASE
    return cart[start : start + FONT_ENTRY[1]]


def check(state: Path, memfix: Path, reserve: int) -> bool:
    offset, length = FONT_ENTRY
    built = memfix.read_bytes()[offset : offset + length]
    found = cart_font(state)
    body = length - reserve
    diffs = [i for i in range(length) if built[i] != found[i]]
    body_ok, tail_ok = found[:body] == built[:body], found[body:] == built[body:]
    print(f"{state.name}: font body equal {body_ok}, tail equal {tail_ok}, "
          f"{len(diffs)} bytes differ")  # fmt: skip
    if diffs:
        print("  first differing addresses:",
              [f"0x{FONT_ADDRESS + i:08X}" for i in diffs[:8]])  # fmt: skip
    return not diffs


def boot(
    cue: Path, out: Path, home: Path, frames: int, shot: int, reserve: int
) -> None:
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    agent_dir = (out / "agent").resolve()
    env = dict(
        os.environ, MEDNAFEN_HOME=str(home.resolve()), MEDNAFEN_AGENT_DIR=str(agent_dir)
    )
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            agent: Agent = connect(agent_dir)
            agent.pause()
            agent.wait_halted()
            agent.clear_events()
            start, end = tail_range(reserve)
            agent.bpmode("log")
            agent.breakpoints("write", [f"{start:08X}-{end - 1:08X}"])
            frame = int(agent.status()["frame"])
            print(f"armed at frame {frame}")
            while frame < frames:
                step = min(shot, frames - frame)
                agent.frames(step)
                agent.wait_halted(max(60.0, step / 20))
                frame = int(agent.status()["frame"])
                agent.screenshot(out / f"f{frame:08d}.png")
            agent.breakpoints("write")
            agent.bpmode("halt")
            hits = [e for e in agent.events() if e.startswith("hit ")]
            (out / "hits.log").write_text("\n".join(hits) + "\n")
            print(f"frame {frame}: {len(hits)} write hits in the tail")
            agent.run()
            agent.savestate(out / "boot.mcs")
        finally:
            proc.terminate()
            proc.wait(10)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("boot")
    b.add_argument("cue", type=Path)
    b.add_argument("out", type=Path)
    b.add_argument("--home", type=Path)
    b.add_argument("--frames", type=int, default=6000)
    b.add_argument("--shot", type=int, default=600)
    c = sub.add_parser("check")
    c.add_argument("state", type=Path)
    c.add_argument("memfix", type=Path)
    for p in (b, c):
        p.add_argument("--reserve", type=int, default=16384)
    args = parser.parse_args(argv)
    if args.command == "boot":
        home = args.home or quiet_home()
        boot(args.cue, args.out, home, args.frames, args.shot, args.reserve)
        return 0
    return 0 if check(args.state, args.memfix, args.reserve) else 1


if __name__ == "__main__":
    raise SystemExit(main())
