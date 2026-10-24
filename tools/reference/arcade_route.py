"""Write a MAME timeline that reaches an MSHvSF arcade win-quote screen (EXP-0030).

The route was found empirically for the local sets with their default EEPROM:
- two coins and 1P start;
- Ryu, then a second confirm (which picks Ken);
- Mode and Speed time out to their defaults;
- a Hadouken loop (down, right, heavy punch) for P1.

The loop's start offset and end frame change the fight, and so the winner and quote.
Inputs held while a quote screen starts appear to skip it, so the loop must end
before the KO. Snapshots, and dumps of the quote pointer that MAME's program space
holds at `0xFF2498`-`0xFF24A3`, go to the paths given.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

POINTER_FIRST, POINTER_LAST = 0xFF2498, 0xFF24A3
SETUP = [
    "3200 press 6 Coin 1",
    "3230 press 6 Coin 1",
    "3320 press 6 1 Player Start",
    "4300 press 6 P1 Button 1",
    "4360 press 6 P1 Button 1",
]


def timeline(
    offset: int,
    loop_end: int,
    snap_start: int,
    snap_end: int,
    snap_every: int,
    dump_prefix: str,
) -> list[str]:
    """Return timeline lines for tools/reference/mame_timeline.lua."""
    lines = list(SETUP)
    for frame in range(5200 + offset, loop_end, 36):
        lines += [
            f"{frame} press 10 P1 Down",
            f"{frame + 5} press 10 P1 Right",
            f"{frame + 12} press 4 P1 Button 3",
        ]
    for frame in range(snap_start, snap_end, snap_every):
        lines.append(f"{frame} snap")
        if dump_prefix:
            lines.append(
                f"{frame} dump {POINTER_FIRST:#x} {POINTER_LAST:#x} "
                f"{dump_prefix}_f{frame:05d}.bin"
            )
    lines.append(f"{snap_end} exit")
    return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--loop-end", type=int, default=10300)
    parser.add_argument("--snap-start", type=int, default=10000)
    parser.add_argument("--snap-end", type=int, default=12400)
    parser.add_argument("--snap-every", type=int, default=40)
    parser.add_argument(
        "--dump-prefix", default="", help="pointer dump path prefix (local only)"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(
        "\n".join(
            timeline(
                args.offset,
                args.loop_end,
                args.snap_start,
                args.snap_end,
                args.snap_every,
                args.dump_prefix,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
