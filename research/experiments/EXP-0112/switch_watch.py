"""OPT-005: does the NAMES setting switch the resident name sites at run time?

``switch_watch.py CUE MEMFIX OUT`` reads the site table from the built
``MEMFIX.PAC``'s font tail, boots CUE in the agent Mednafen, and from frame
``--start`` steps ``--step`` frames at a time. It sets NAMES
(``0x06017AB4``) to Saturn, waits for every resident site (``MM.BIN`` in
WRAM-H, the name calls in sound RAM) to hold its Saturn bytes, then sets it
back and waits for the American bytes. Sites in the character slots and the
ending's ``ME.PAC`` area are only checked for unwanted writes: those files
are not loaded at the title.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import Agent
from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.sh2.asm import assemble
from tools.text.caption_compiler import FONT_ADDRESS, FONT_ENTRY
from tools.text.names_switch import Site, unpack
from tools.text.options_submenu import NAMES_RESERVE, SOURCE

NAMES = 0x06017AB4


def site_table(memfix: Path) -> list[Site]:
    offset, length = FONT_ENTRY
    tail = memfix.read_bytes()[offset + length - NAMES_RESERVE : offset + length]
    origin = FONT_ADDRESS + length - NAMES_RESERVE
    _, symbols = assemble(SOURCE.read_text(), origin)
    return unpack(tail[symbols["sites"] - origin :])


def read(agent: Agent, site: Site) -> bytes:
    if 0x05A00000 <= site.address < 0x05A80000:
        return agent.read("scspram", site.address - 0x05A00000, len(site.american))
    return agent.bus_read(site.address, len(site.american))


def state(agent: Agent, resident: Sequence[Site]) -> str:
    seen = [read(agent, s) for s in resident]
    american = sum(b == s.american for b, s in zip(seen, resident, strict=True))
    saturn = sum(b == s.saturn for b, s in zip(seen, resident, strict=True))
    return f"american {american} saturn {saturn} of {len(resident)}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path)
    parser.add_argument("memfix", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--start", type=int, default=2100)
    parser.add_argument("--end", type=int, default=2600)
    parser.add_argument("--step", type=int, default=5)
    args = parser.parse_args(argv)
    found = site_table(args.memfix)
    resident = [
        s for s in found if not s.slots and not 0x001FFFF0 <= s.address < 0x00300000
    ]
    others = [s for s in found if s not in resident]
    print(f"{len(found)} sites: {len(resident)} resident, {len(others)} slot or ME")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    home = quiet_home(target=Path("local/mednafen_quiet_opt004"))
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(home.resolve()),
        MEDNAFEN_AGENT_DIR=str(out / "agent"),
    )
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            agent = connect(out / "agent")
            agent.pause()
            agent.wait_halted()
            frame = int(agent.status()["frame"])
            agent.frames(args.start - frame)
            agent.wait_halted(120)
            print(f"frame {args.start}: {state(agent, resident)}")
            phase, want = "saturn", 1
            while frame < args.end:
                agent.bus_write(NAMES, want.to_bytes(4, "big"))
                agent.frames(args.step)
                agent.wait_halted(60)
                frame = int(agent.status()["frame"])
                handler = agent.bus_read(0x06000A00, 4).hex()
                now = state(agent, resident)
                print(
                    f"frame {frame} handler {handler} names {want}: {now}", flush=True
                )
                if phase == "saturn" and now.startswith("american 0 saturn"):
                    if f"saturn {len(resident)}" in now:
                        phase, want = "american", 0
                elif phase == "american" and now.startswith(
                    f"american {len(resident)}"
                ):
                    break
            untouched = sum(
                read(agent, s) not in (s.american, s.saturn)
                for s in others
                if not s.slots
            )
            print(f"ME sites holding neither variant (not loaded): {untouched}")
            agent.screenshot(out / "end.png")
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
