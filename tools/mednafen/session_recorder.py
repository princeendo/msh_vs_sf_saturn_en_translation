"""Record rolling save states and screenshots while the user plays (END-001).

Attaches to a running patched Mednafen (agent interface, `EMU-021`) and, until
``out/STOP`` exists or Mednafen stops answering:

- every ``--shot-interval`` seconds saves a screenshot ``shots/f<frame>.png``;
- every ``--state-interval`` seconds saves a state ``states/f<frame>.mcs``.

Only the newest ``--keep-states`` states (and ``--keep-shots`` screenshots, when
set) are kept, so a moment the user cannot pause on, such as a continue
countdown, can be picked afterwards from the screenshots and its nearest state
kept as a checkpoint. ``index.tsv`` lists every capture with its frame number.
States are checkpoints, not RAM evidence (`AGENTS.md`). All outputs go to
``out``, an ignored path.
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import DEFAULT_DIR, Agent, AgentError


def prune(directory: Path, pattern: str, keep: int) -> list[Path]:
    """Delete all but the newest ``keep`` files (by frame-numbered name)."""
    files = sorted(directory.glob(pattern), key=lambda p: int(p.stem[1:]))
    doomed = files[:-keep] if keep > 0 else []
    for path in doomed:
        path.unlink()
    return doomed


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path, help="output directory (ignored path)")
    parser.add_argument("--agent-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--shot-interval", type=float, default=1.0)
    parser.add_argument("--state-interval", type=float, default=3.0)
    parser.add_argument("--keep-states", type=int, default=60)
    parser.add_argument("--keep-shots", type=int, default=0, help="0 keeps all")
    args = parser.parse_args(argv)
    out = args.out.resolve()
    shots, states = out / "shots", out / "states"
    shots.mkdir(parents=True, exist_ok=True)
    states.mkdir(parents=True, exist_ok=True)
    agent = Agent(args.agent_dir.resolve(), 10)
    next_shot = next_state = time.monotonic()
    with (out / "index.tsv").open("a") as index:
        while not (out / "STOP").exists():
            now = time.monotonic()
            try:
                if now >= next_shot or now >= next_state:
                    frame = int(agent.status()["frame"])
                if now >= next_shot:
                    agent.screenshot(shots / f"f{frame:08d}.png")
                    index.write(f"{time.time():.2f}\t{frame}\tshot\n")
                    next_shot = now + args.shot_interval
                    if args.keep_shots:
                        prune(shots, "f*.png", args.keep_shots)
                if now >= next_state:
                    if agent.halted():
                        next_state = now + args.state_interval
                    else:
                        agent.savestate(states / f"f{frame:08d}.mcs")
                        index.write(f"{time.time():.2f}\t{frame}\tstate\n")
                        next_state = now + args.state_interval
                        prune(states, "f*.mcs", args.keep_states)
                index.flush()
            except AgentError as error:
                print(f"stopped: {error}")
                return 1
            time.sleep(0.05)
    print(f"stopped by {out / 'STOP'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
