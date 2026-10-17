"""Capture a win-quote transition through the agent interface (one human KO).

The script:

1. loads a pre-KO state;
2. sets write breakpoints in log mode on the quote index word and record pointer
   (`EXP-0025`);
3. waits while the user plays the KO;
4. saves a **post-KO checkpoint** at the first index-word hit that is not the
   pointer store, so later runs need no gameplay;
5. records every hit;
6. after the pointer store, runs ``--quote-frames`` frames, then saves a screenshot
   and a quote-screen state.

Optional forcing (``--force-index N``) queues a write of N to the index word after
each hit at the setter PCs, as pre-registered in `EXP-0025` Part 2.
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import Agent, AgentError, parse_pairs

INDEX_WORD = 0x060F9E66
POINTER = 0x060F249C
POINTER_PCS = {0x060AF724, 0x060AF728}
BREAKPOINTS = [
    "060F9E66-060F9E67",
    "260F9E66-260F9E67",
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", type=Path, required=True, help="state to load first")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", action="store_true", help="save post-KO state")
    parser.add_argument("--quote-frames", type=int, default=240)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--force-index", type=int)
    parser.add_argument("--setter-pcs", default="", help="hex PCs for forcing")
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
                agent.onhit_write(pc, INDEX_WORD, args.force_index.to_bytes(2, "big"))
        agent.loadstate(args.state)
        checkpoint_saved = False
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
                if (
                    args.checkpoint
                    and not checkpoint_saved
                    and hit["PC"] not in POINTER_PCS
                ):
                    agent.savestate(out / "postko.mc")
                    checkpoint_saved = True
                    report["checkpoint_after_hit"] = hit["n"]
                if hit["PC"] == 0x060AF728:
                    pointer_done = True
            seen = len(events)
            time.sleep(0.05)
        report["pointer"] = f"0x{agent.bus_read(POINTER, 4).hex().upper()}"
        report["index"] = int.from_bytes(agent.bus_read(INDEX_WORD, 2), "big")
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
