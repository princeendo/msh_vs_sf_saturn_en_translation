"""Write a MAME timeline that reaches an MSHvSF arcade ending with no play (END-006).

The route was found empirically for the local sets with their default EEPROM
(`EXP-0042`):

- two coins and 1P start; a point character (default Ryu, or a cursor path from
  Ryu), then a partner (default Ken, or a cursor path from where the partner
  cursor starts; paths are only valid for the point they were observed with);
- the stage word at ``0xFF4880`` is forced to ``0x0607`` from boot, so the first
  fight is stage 8 (Mech-Gouki), and released during that fight;
- the boss's vitality words ``0xFF3E50`` and ``0xFF4844`` are forced to zero, so
  the fight ends at once, and released after the KO.

The offsets are the Saturn ones (`EXP-0042`) with ``0x060F`` replaced by ``0xFF``.
Snapshots go to MAME's snapshot directory; keep it under an ignored path.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

STAGE_WORD, STAGE_8 = 0xFF4880, 0x0607
VITALITY = (0xFF3E50, 0xFF4844)
SETUP = [
    "3200 press 6 Coin 1",
    "3230 press 6 Coin 1",
    "3320 press 6 1 Player Start",
]
POINT_PATHS = {"ryu": [], "gouki": ["Up"]}
# From the partner cursor's start; observed with point Ryu unless noted.
PARTNER_PATHS = {
    "ken": [],
    "gouki": ["Up", "Right"],
    "chunli": ["Up", "Right", "Right"],
    "captain_america": ["Down", "Right"],  # observed with point Gouki (EXP-0043)
}


def timeline(
    partner: str = "ken", end: int = 16000, every: int = 30, point: str = "ryu"
) -> list[str]:
    """Return timeline lines for tools/reference/mame_timeline.lua."""
    lines = [f"3000 force16 {STAGE_WORD:#x} {STAGE_8:#06x}", *SETUP]
    frame = 4300 - 40 * len(POINT_PATHS[point])
    for direction in POINT_PATHS[point]:
        lines += [f"{frame} press 4 P1 {direction}", f"{frame + 20} snap"]
        frame += 40
    lines.append("4300 press 6 P1 Button 1")
    frame = 4360
    for direction in PARTNER_PATHS[partner]:
        lines += [f"{frame} press 4 P1 {direction}", f"{frame + 20} snap"]
        frame += 40
    lines.append(f"{frame} press 6 P1 Button 1")
    if PARTNER_PATHS[partner]:
        lines.append(f"{frame + 30} snap")
    lines += [f"5600 force16 {address:#x} 0x0000" for address in VITALITY]
    lines.append(f"7100 unforce {STAGE_WORD:#x}")
    lines += [f"8100 unforce {address:#x}" for address in VITALITY]
    lines += [f"{f} snap" for f in range(6500, 7800, 120)]
    lines += [f"{f} snap" for f in range(7800, end, every)]
    lines.append(f"{end} exit")
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--point", choices=sorted(POINT_PATHS), default="ryu")
    parser.add_argument("--partner", choices=sorted(PARTNER_PATHS), default="ken")
    parser.add_argument("--end", type=int, default=16000)
    parser.add_argument("--every", type=int, default=30)
    args = parser.parse_args(argv)
    print("\n".join(timeline(args.partner, args.end, args.every, args.point)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
