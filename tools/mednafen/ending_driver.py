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
word steps from ``0xHH(N-1)`` to ``0xHHN`` (the player has won N stages), so
the earlier fights, and their win quotes, play normally (`SPECIAL-003`). A
single read is not enough: at boot the word holds unrelated values such as
``0x0002`` (`SPECIAL-002`). The high byte ``HH`` varies between runs
(``0x0400`` → ``0x0401``, ``0x0300`` → ``0x0301``), so it is kept: that ARM
holds ``0xHH07``. Every change of the stage word is logged
while waiting.

``--stage N`` arms stage N instead of 8 (``0xHH(N-1)``), and ``--no-ko`` stops
writing once that stage's fight starts, so the player can lose it (to see the
opponent's win quote, `SPECIAL-004`).


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
        help="first arm only once N stages are won (stage word 0xHH(N-1) -> 0xHHN)",
    )
    parser.add_argument("--stage", type=int, default=8, help="stage to arm (1-8)")
    parser.add_argument(
        "--no-ko", action="store_true", help="arm only: the fight plays untouched"
    )
    args = parser.parse_args(argv)
    if not 1 <= args.stage <= 8:
        parser.error("--stage must be 1-8")
    stage = bytes([STAGE_8[0], args.stage - 1])
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

    def wait_for_stage(index: int) -> bytes:
        """Wait for ``index`` won stages; return the stage word to hold."""
        note(f"WAIT: no writes until the stage word reaches stage index {index}")
        last = b""
        while True:
            if not agent.halted():
                word = agent.bus_read(STAGE_WORD, 2)
                if word != last:
                    note(f"stage word {word.hex()}")
                    # Only a step from index - 1 to index: at boot the word
                    # holds unrelated values such as 0002 (SPECIAL-002).
                    if (
                        len(last) == 2
                        and word[0] <= 0x0F
                        and word[0] == last[0]
                        and word[1] == index
                        and last[1] == index - 1
                        and index < stage[1]
                    ):
                        return bytes([word[0], stage[1]])
                    last = word
            time.sleep(args.period)

    target = stage
    try:
        if args.after_stage:
            target = wait_for_stage(args.after_stage)
        while True:
            note(f"ARM: holding the stage word at {target.hex()} (stage {args.stage})")
            previous = vitality()
            while True:
                if agent.halted():
                    time.sleep(args.period)
                    continue
                agent.bus_write(STAGE_WORD, target)
                # Only a fight that starts after arming: the vitality word must
                # rise to full. Armed mid-fight, the word may already be full,
                # and in an ordinary fight it is player 1's (SPECIAL-003).
                now = vitality()
                if (
                    now == FULL_VITALITY
                    and previous != FULL_VITALITY
                    and agent.bus_read(STAGE_WORD, 2) == target
                ):
                    break
                previous = now
                time.sleep(args.period)
            if args.no_ko:
                note(f"DONE: stage {args.stage} fight started; no more writes")
                return 0
            knock_out(f"KO: stage-{args.stage} fight started; zeroing boss vitality")
            note("DONE: no more writes; the ending plays untouched")
            if not args.repeat:
                return 0
            time.sleep(args.rest)
            target = stage
    except AgentError as error:
        print(f"stopped: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
