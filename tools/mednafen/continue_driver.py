"""Force the post-loss story line and step the CONTINUE? hints in play (TXT-002).

Attach to a patched Mednafen (agent interface, `EMU-021`) running a release
image built with ``--story-lines --official-hints``. The user plays and loses;
the driver only rewrites ``MM.BIN`` code and data in work RAM while it is
resident, which it recognises by the roll test ``cmp/eq #39`` (``0x8827`` at
``0x060AF224``) and the release's own ``nop`` at ``0x060AF348``:

- **story line:** the ``bf`` after the 1-in-64 roll (``0x060AF228``) becomes a
  ``nop``, so every loss to the CPU shows the winner's story line
  (`EXP-0085`, `EXP-0087`);
- **hints:** the index map (``0x060AF3A0``) is set to sixteen ``2k`` bytes, so
  the next CONTINUE? shows hint ``k``. A log-mode PC breakpoint just after the
  map read (``0x060AF352``) marks each new hint, and ``k`` then steps to the
  next of ``--hints`` (`EXP-0086`).

Writes are repeated whenever the bytes differ, because a mode change can
restore ``MM.BIN`` from its saved copy. The run ends when ``--log``'s folder
holds ``STOP`` or Mednafen stops answering. Then the breakpoint is cleared and
the mode set back to halt.
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import DEFAULT_DIR, Agent, AgentError

ROLL_TEST, ROLL_TEST_CODE = 0x060AF224, bytes.fromhex("8827")
MAP_NOP, NOP = 0x060AF348, bytes.fromhex("0009")
ROLL_BRANCH, ROLL_BRANCH_CODE = 0x060AF228, bytes.fromhex("8B14")
HINT_MAP, HINT_CREATED = 0x060AF3A0, 0x060AF352


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agent-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--period", type=float, default=0.25)
    parser.add_argument("--hints", type=int, nargs="+", default=list(range(8)))
    parser.add_argument("--no-story", action="store_true", help="leave the roll alone")
    parser.add_argument("--log", type=Path, required=True, help="log (ignored path)")
    args = parser.parse_args(argv)
    agent = Agent(args.agent_dir.resolve(), 10)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    stop = args.log.parent / "STOP"

    def note(text: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} frame={agent.status()['frame']} {text}"
        print(line, flush=True)
        with args.log.open("a") as stream:
            stream.write(line + "\n")

    step = 0
    agent.clear_events()
    agent.bpmode("log")
    agent.breakpoints("pc", [f"{HINT_CREATED:08X}"])
    note(f"ARMED: story={'off' if args.no_story else 'forced'} hints={args.hints}")
    try:
        while not stop.exists():
            if agent.halted():
                time.sleep(args.period)
                continue
            resident = (
                agent.bus_read(ROLL_TEST, 2) == ROLL_TEST_CODE
                and agent.bus_read(MAP_NOP, 2) == NOP
            )
            if resident:
                if not args.no_story and agent.bus_read(ROLL_BRANCH, 2) != NOP:
                    agent.bus_write(ROLL_BRANCH, NOP)
                    note("story line forced (bf -> nop at 060AF228)")
                hint = args.hints[step % len(args.hints)]
                wanted = bytes([2 * hint]) * 16
                if agent.bus_read(HINT_MAP, 16) != wanted:
                    agent.bus_write(HINT_MAP, wanted)
                    note(f"next CONTINUE? shows hint {hint} (record {2 * hint})")
            hits = [line for line in agent.events() if line.startswith("hit ")]
            if hits:
                agent.clear_events()
                # Outside MM.BIN another overlay's code may sit at that address.
                if resident:
                    note(f"hint {args.hints[step % len(args.hints)]} created")
                    step += 1
            time.sleep(args.period)
    except AgentError as error:
        print(f"agent stopped answering: {error}", flush=True)
        return 0
    finally:
        try:
            agent.breakpoints("pc")
            agent.bpmode("halt")
        except AgentError:
            pass
    note("STOP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
