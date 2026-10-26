"""Drive a running game straight to the stage-8 boss and win it (END-010).

Attach to a patched Mednafen (agent interface, `EMU-021`) running any image. The
user only works the menus (start arcade mode, pick a team). The driver then:

1. ARM: writes the stage word ``0x060F4880`` = ``0x0607`` every ``--period``
   seconds, so the next stage the game loads is stage 8 (`EXP-0042`);
2. KO: once the boss fight has started (boss vitality ``0x060F3E50`` reads 144
   with the stage word still ``0x0607``), stops writing the stage and zeroes the
   boss vitality words ``0x060F3E50``/``0x060F4844`` for ``--ko-seconds``;
3. DONE: writes nothing more, so the dialogue, ending, and credits play
   untouched. With ``--repeat``, it re-arms after ``--rest`` seconds.

With ``--after-stage N``, the first ARM waits, writing nothing, until the stage
word reads ``0x06NN`` or later (the player has won N stages), so the earlier
fights, and their win quotes, play normally (`SPECIAL-003`). Every change of the
stage word is logged while waiting.


These are the Saturn offsets found in `EXP-0042`. Every phase change is logged
with the emulator frame number.
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import DEFAULT_DIR, Agent, AgentError

STAGE_WORD, STAGE_8 = 0x060F4880, b"\x06\x07"
VITALITY = (0x060F3E50, 0x060F4844)
FULL_VITALITY = 144


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agent-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--period", type=float, default=0.1)
    parser.add_argument("--ko-seconds", type=float, default=3.0)
    parser.add_argument("--repeat", action="store_true")
    parser.add_argument("--rest", type=float, default=150.0)
    parser.add_argument("--log", type=Path, help="phase log (ignored path)")
    parser.add_argument(
        "--after-stage",
        type=int,
        default=0,
        help="first arm only once N stages are won (stage word 0x06NN)",
    )
    args = parser.parse_args(argv)
    agent = Agent(args.agent_dir.resolve(), 10)

    def note(text: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} frame={agent.status()['frame']} {text}"
        print(line, flush=True)
        if args.log:
            with args.log.open("a") as stream:
                stream.write(line + "\n")

    # Boss vitality only: in an ordinary 2-vs-2 fight the opponent's vitality is
    # elsewhere (EXP-0049), so this driver wins the stage-8 boss fight alone.
    def knock_out(text: str) -> None:
        note(text)
        deadline = time.monotonic() + args.ko_seconds
        while time.monotonic() < deadline:
            for address in VITALITY:
                agent.bus_write(address, b"\x00\x00")
            time.sleep(args.period)

    def vitality() -> int:
        return int.from_bytes(agent.bus_read(VITALITY[0], 2), "big")

    def wait_for_stage(index: int) -> None:
        note(f"WAIT: no writes until the stage word reaches 0x06{index:02X}")
        last = b""
        while True:
            if not agent.halted():
                word = agent.bus_read(STAGE_WORD, 2)
                if word != last:
                    note(f"stage word {word.hex()}")
                    last = word
                if word[0] == STAGE_8[0] and index <= word[1] < STAGE_8[1]:
                    return
            time.sleep(args.period)

    try:
        if args.after_stage:
            wait_for_stage(args.after_stage)
        while True:
            note("ARM: holding the stage word at stage 8")
            while True:
                if agent.halted():
                    time.sleep(args.period)
                    continue
                agent.bus_write(STAGE_WORD, STAGE_8)
                if (
                    vitality() == FULL_VITALITY
                    and agent.bus_read(STAGE_WORD, 2) == STAGE_8
                ):
                    break
                time.sleep(args.period)
            knock_out("KO: stage-8 fight started; zeroing the boss vitality")
            note("DONE: no more writes; the ending plays untouched")
            if not args.repeat:
                return 0
            time.sleep(args.rest)
    except AgentError as error:
        print(f"stopped: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
