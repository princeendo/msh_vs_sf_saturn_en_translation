"""Capture a win-quote transition through the agent interface (one human KO).

The script:

1. loads a pre-KO state (or, without ``--state``, waits while the user plays from
   the running game);
2. sets write breakpoints in log mode on the quote index word and record pointer
   (`EXP-0025`);
3. waits while the user plays the KO;
4. saves a **post-KO checkpoint** at each hit from a ``--checkpoint-pcs`` writer
   (default: the bonus-tally clearing loop), overwriting it so the last one before
   the quote is kept; later runs then need no gameplay;
5. records every hit;
6. once a record pointer into work RAM low is stored (any table, so team order
   and character do not matter; ``--table-base`` narrows it to one 16-record
   table), runs ``--quote-frames`` frames, then saves a screenshot and a
   quote-screen state. The quote state that produced the pointer (one of two,
   `EXP-0036`) is recorded with its table base and index.

The quote routine keeps one state per side, at ``r12`` = ``QUOTE_STATES``: table
base at ``r12 + 0x34`` and index word at ``r12 + 0x50`` (`EXP-0025` found the first;
`EXP-0036` the second). Optional forcing (``--force-index N``) queues a write of N
to the ``--quote-state`` index word after each hit at the setter PCs, as
pre-registered in `EXP-0025` Part 2.
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import Agent, AgentError, parse_pairs

POINTER = 0x060F249C
QUOTE_STATES = (0x060F9E16, 0x060F9ED6)  # r12 in the pointer routine (EXP-0036)
BASE_OFFSET = 0x34  # long: quote table base (EXP-0025)
INDEX_OFFSET = 0x50  # word: quote index
POINTER_PCS = {0x060AF724, 0x060AF728}
BREAKPOINTS = [
    "060F9E66-060F9E67",
    "260F9E66-260F9E67",
    "060F9F26-060F9F27",
    "260F9F26-260F9F27",
    "060F249C-060F249F",
    "260F249C-260F249F",
]


def parse_hit(line: str) -> dict[str, int] | None:
    if not line.startswith("hit "):
        return None
    pairs = parse_pairs(line)
    return {
        "n": int(pairs["n"]),
        "frame": int(pairs["frame"]),
        "PC": int(pairs["PC"], 16),
        "R0": int(pairs["R0"], 16),
        "R1": int(pairs["R1"], 16),
    }


def quote_state(
    pointer: int, states: dict[int, tuple[int, int]]
) -> tuple[int, int, int]:
    """The state whose ``base + 76·index`` is ``pointer``, else the first one.

    ``states`` maps each ``r12`` to its (table base, index).
    """
    for r12, (base, index) in states.items():
        if base + 76 * index == pointer:
            return r12, base, index
    r12 = next(iter(states))
    return r12, *states[r12]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", type=Path, help="state to load first (optional)")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", action="store_true", help="save post-KO state")
    parser.add_argument("--checkpoint-pcs", default="060490EC")
    parser.add_argument("--table-base", type=lambda v: int(v, 0))
    parser.add_argument("--quote-frames", type=int, default=240)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--force-index", type=int)
    parser.add_argument("--setter-pcs", default="", help="hex PCs for forcing")
    parser.add_argument(
        "--quote-state",
        type=lambda v: int(v, 16),
        default=QUOTE_STATES[0],
        help="r12 of the state whose index is forced (hex)",
    )
    args = parser.parse_args(argv)

    agent = Agent()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {"state": str(args.state), "hits": []}
    hits: list[dict[str, int]] = []
    try:
        agent.clear_events()
        agent.onhit_clear()
        agent.bpmode("log")
        agent.breakpoints("write", BREAKPOINTS)
        if args.force_index is not None:
            for pc in [int(p, 16) for p in args.setter_pcs.split(",") if p]:
                agent.onhit_write(
                    pc,
                    args.quote_state + INDEX_OFFSET,
                    args.force_index.to_bytes(2, "big"),
                )
        if args.state is not None:
            agent.loadstate(args.state)
        checkpoint_pcs = {int(p, 16) for p in args.checkpoint_pcs.split(",") if p}
        table = (
            range(args.table_base, args.table_base + 16 * 76, 76)
            if args.table_base is not None
            else range(0x00200000, 0x00300000)
        )
        last_pointer = -1
        deadline = time.monotonic() + args.timeout
        seen = 0
        pointer_done = False
        while not pointer_done:
            if time.monotonic() > deadline:
                raise AgentError("timed out waiting for the quote transition")
            events = agent.events()
            for line in events[seen:]:
                hit = parse_hit(line)
                if hit is None:
                    continue
                hits.append(hit)
                if args.checkpoint and hit["PC"] in checkpoint_pcs:
                    agent.savestate(out / "postko.mc")
                    report["checkpoint_after_hit"] = hit["n"]
                if hit["PC"] == 0x060AF724:
                    last_pointer = hit["R0"]
                if hit["PC"] == 0x060AF728 and last_pointer in table:
                    pointer_done = True
            seen = len(events)
            time.sleep(0.05)
        pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
        states = {
            r12: (
                int.from_bytes(agent.bus_read(r12 + BASE_OFFSET, 4), "big"),
                int.from_bytes(agent.bus_read(r12 + INDEX_OFFSET, 2), "big"),
            )
            for r12 in QUOTE_STATES
        }
        r12, base, index = quote_state(pointer, states)
        report["pointer"] = f"0x{pointer:08X}"
        report["quote_state"] = f"0x{r12:08X}"
        report["index"] = index
        report["table_base"] = f"0x{base:08X}"
        agent.frames(args.quote_frames)
        agent.wait_halted(60)
        agent.screenshot(out / "quote.png")
        agent.run()
        time.sleep(0.2)
        agent.savestate(out / "quote.mc")
    finally:
        try:
            agent.breakpoints("write")
            agent.onhit_clear()
            agent.bpmode("halt")
        except AgentError:
            pass
    report["hits"] = [
        {k: (f"0x{v:08X}" if k in ("PC", "R0", "R1") else v) for k, v in h.items()}
        for h in hits
    ]
    report["events"] = agent.events()
    (out / "capture.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: report[k] for k in report if k not in ("events",)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
