"""Watch (and optionally help) the Mech-Gouki unlock and select code (SPECIAL-004).

Attach to a patched Mednafen (agent interface, `EMU-021`). The user plays; the
driver logs every change of the words the unlock and the select code use
(`EXP-0089`):

- ``0x06017AB0`` (MECH-GOUKI NOW!! unlocked; the release presets it),
  ``0x06017AB4`` (Mech-Gouki selectable), ``0x06017AA8``;
- the mode flags ``0x0601801C`` / ``0x06018024``;
- the per-player Gouki counters ``0x06017CEE`` / ``0x06017CEF``;
- the team words ``0x060F48B0``-``0x060F48B7`` (character x 2).

With ``--ko-boss`` it zeroes the boss vitality (``0x060F3E50``/``0x060F4844``,
`EXP-0042`) once, for ``--ko-seconds``, after a fight starts in the
MECH-GOUKI NOW!! mode (both mode flags non-zero), so that mode can be cleared
without skill. With ``--set-ab4`` it writes ``0x06017AB4`` = 1 whenever it reads
0, skipping that clear. The run ends when ``--log``'s folder holds ``STOP`` or
Mednafen stops answering.
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import DEFAULT_DIR, Agent, AgentError
from tools.mednafen.ending_driver import FULL_VITALITY, VITALITY

WATCH = {
    "AB0": (0x06017AB0, 4),
    "AB4": (0x06017AB4, 4),
    "AA8": (0x06017AA8, 4),
    "mode801C": (0x0601801C, 1),
    "mode8024": (0x06018024, 1),
    "gouki_count": (0x06017CEE, 2),
    "teams": (0x060F48B0, 8),
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agent-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--period", type=float, default=0.1)
    parser.add_argument("--ko-boss", action="store_true")
    parser.add_argument("--ko-seconds", type=float, default=3.0)
    parser.add_argument("--set-ab4", action="store_true")
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

    last: dict[str, bytes] = {}
    previous_vitality = 0
    knocked_out = False
    note(f"ARMED: ko_boss={args.ko_boss} set_ab4={args.set_ab4}")
    try:
        while not stop.exists():
            if agent.halted():
                time.sleep(args.period)
                continue
            now = {k: agent.bus_read(a, n) for k, (a, n) in WATCH.items()}
            changed = [f"{k}={v.hex()}" for k, v in now.items() if last.get(k) != v]
            if changed:
                note(" ".join(changed))
                last = now
            if args.set_ab4 and now["AB4"] == bytes(4):
                agent.bus_write(0x06017AB4, (1).to_bytes(4, "big"))
                note("set AB4 = 1")
            boss_mode = now["mode801C"] != b"\x00" and now["mode8024"] != b"\x00"
            vitality = int.from_bytes(agent.bus_read(VITALITY[0], 2), "big")
            if (
                args.ko_boss
                and boss_mode
                and not knocked_out
                and vitality == FULL_VITALITY
                and previous_vitality != FULL_VITALITY
            ):
                note("KO: zeroing the boss vitality")
                deadline = time.monotonic() + args.ko_seconds
                while time.monotonic() < deadline:
                    for address in VITALITY:
                        agent.bus_write(address, b"\x00\x00")
                    time.sleep(args.period)
                knocked_out = True
            if not boss_mode:
                knocked_out = False
            previous_vitality = vitality
            time.sleep(args.period)
    except AgentError as error:
        print(f"agent stopped answering: {error}", flush=True)
        return 0
    note("STOP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
