"""OPT-004 development loop: drive the Options menu of a patched checkpoint.

1. Patch a recorded OPTION MODE state with what a build changes in the
   menu's RAM: the spec's ``MM.BIN`` patches (at ``0x06018B00`` + offset) and
   its font-tail payload in cart RAM. The result mixes two builds, so it is a
   development checkpoint only; the build's cold boot is the real test.
2. Start the agent Mednafen on the build's image, load the checkpoint, and
   play a script of presses. A press writes the menu's pad words
   (``0x0601A3F4`` buttons, ``0x0601A3F8`` directions; `EXP-0105`) right
   after the dispatcher's first instruction (``0x0601DD3E``) for one frame,
   so every menu state reads it. A screenshot follows each step.

Script steps are ``WAIT``, or ``NAME`` for a press then ``WAIT`` frames:
``start``, ``ac``, ``up``, ``down``, ``left``, ``right``, ``none``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import Agent
from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.text.caption_compiler import parse_font_tail, parse_patches

MM_BASE = 0x06018B00
DISPATCH = 0x0601DD3E
PRESSES = {  # (buttons, directions)
    "none": (0, 0),
    "start": (0x0080, 0),
    "ac": (0x0040, 0),
    "up": (0, 1),
    "down": (0, 2),
    "left": (0, 4),
    "right": (0, 8),
}


def patch_state(state: Path, spec: Path, out: Path) -> None:
    """The state's WRAM-H holds 16-bit elements, so the menu's ``MM.BIN``
    writes (some odd-sized) go into an extracted copy, written back as one
    aligned span."""
    document = json.loads(spec.read_text())
    tmp = out.with_suffix(".tmp.mcs")
    current = state
    subprocess.run(
        [sys.executable, "-m", "tools.memory.mcs_extract", str(state),
         "--region", "wram_h", "--out-dir", str(out.parent / "extract"), "--overwrite"],
        check=True,
        capture_output=True,
    )  # fmt: skip
    wram = bytearray((out.parent / "extract" / "wram_h.bin").read_bytes())
    for p in parse_patches(document):
        if p.file == "MM.BIN" and 0x5000 <= p.offset < 0x6000:
            start = MM_BASE + p.offset - 0x06000000
            wram[start : start + len(p.data)] = p.data
    span = (MM_BASE + 0x5000, MM_BASE + 0x6000)
    writes: list[tuple[str, int, bytes]] = [
        ("wram_h", span[0], bytes(wram[span[0] - 0x06000000 : span[1] - 0x06000000]))
    ]
    tail = parse_font_tail(document)
    if tail:
        writes.append(("cart_ram", tail.address, tail.payload))
    for index, (region, address, data) in enumerate(writes):
        blob = out.parent / f"write{index}.bin"
        blob.write_bytes(data)
        target = out if index == len(writes) - 1 else tmp.with_name(f"step{index}.mcs")
        subprocess.run(
            [sys.executable, "-m", "tools.memory.mcs_patch", str(current), str(target),
             "--region", region, "--address", f"0x{address:X}", "--data", str(blob)],
            check=True,
            capture_output=True,
        )  # fmt: skip
        current = target
    print(f"{len(writes)} writes into {out.name}")


def press(agent: Agent, name: str) -> None:
    buttons, directions = PRESSES[name]
    data = buttons.to_bytes(4, "big") + directions.to_bytes(4, "big")
    agent.command(f"onhit {DISPATCH:08X} write workramh 1A3F4 {data.hex().upper()}")
    agent.bpmode("log")
    agent.breakpoints("pc", [f"{DISPATCH:08X}"])
    agent.frames(1)
    agent.wait_halted(30)
    agent.breakpoints("pc")
    agent.onhit_clear()
    agent.bpmode("halt")


def drive(
    cue: Path, checkpoint: Path, out: Path, steps: Sequence[str], pokes: Sequence[str]
) -> None:
    out = out.resolve()
    agent_dir = out / "agent"
    home = quiet_home(target=Path("local/mednafen_quiet_opt004"))
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
            agent = connect(agent_dir)
            agent.frames(300)
            agent.wait_halted(60)
            agent.run()
            agent.loadstate(checkpoint.resolve())
            agent.pause()
            agent.wait_halted()
            for poke in pokes:
                address, _, value = poke.partition("=")
                agent.bus_write(int(address, 16), bytes.fromhex(value))
            for number, step in enumerate(steps):
                name, _, wait = step.partition(":")
                if name.isdigit():
                    name, wait = "none", name
                if name != "none":
                    press(agent, name)
                agent.frames(int(wait or 20))
                agent.wait_halted(60)
                state = agent.bus_read(0x06017A84, 4).hex()
                cursor = agent.bus_read(0x06017A88, 4).hex()
                boss = agent.bus_read(0x06017AB0, 4).hex()
                combo = agent.bus_read(0x06017AD4, 4).hex()
                effect = agent.bus_read(0x06049D34, 2).hex()
                agent.screenshot(out / f"{number:02d}-{name}.png")
                print(
                    f"{number:02d} {name:6} state {state} cursor {cursor} "
                    f"boss {boss} combo {combo} combo effect {effect}"
                )
        finally:
            proc.terminate()
            proc.wait(10)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("state", type=Path, help="a recorded OPTION MODE state")
    parser.add_argument("spec", type=Path)
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("steps", nargs="+", help="for example ac:30 down:20 right:20")
    parser.add_argument(
        "--poke", action="append", default=[], help="ADDRESS=HEX written after loading"
    )
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    checkpoint = args.out / "checkpoint.mcs"
    patch_state(args.state, args.spec, checkpoint)
    drive(args.cue, checkpoint, args.out, args.steps, args.poke)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
