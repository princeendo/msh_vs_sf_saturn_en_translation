"""Cold-boot a disc image silently and screenshot chosen frames (attract checks).

The tool launches the patched Mednafen (agent interface, `EMU-021`) on ``cue``
in the silent home (``replay_state.quiet_home``), pauses it as soon as the agent
answers, then advances to every frame ``--first``, ``--first + --step``, ...
``--last`` and saves ``out/f<frame>.png``. No input is sent, so the attract
sequence plays as it does after power-on. Mednafen is closed afterwards.

Two runs of the same image do not give identical frames: disc-read timing
shifts animation phase by a few frames (`EXP-0071`, attract colour check of
2026-10-26), so compare scenes, not frame numbers.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.replay_state import BINARY, connect, quiet_home


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path, help="disc image CUE (read only)")
    parser.add_argument("out", type=Path, help="output directory (ignored path)")
    parser.add_argument("--first", type=int, default=600)
    parser.add_argument("--last", type=int, default=13200)
    parser.add_argument("--step", type=int, default=30)
    parser.add_argument("--agent-dir", type=Path, default=Path("local/mednafen/agent"))
    parser.add_argument("--home", type=Path, help="default: the silent quiet_home()")
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    agent_dir = args.agent_dir.resolve()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str((args.home or quiet_home()).resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
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
            frame = int(agent.status()["frame"])
            for target in range(args.first, args.last + 1, args.step):
                if target <= frame:
                    continue
                agent.frames(target - frame)
                # Mednafen runs at about real time: allow the longest jump.
                agent.wait_halted(max(60.0, (target - frame) / 30))
                frame = int(agent.status()["frame"])
                agent.screenshot(out / f"f{frame:08d}.png")
            print(f"last frame {frame}")
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
