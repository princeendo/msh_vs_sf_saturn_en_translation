"""Log breakpoint hits while someone plays, without halting (TXT-001).

Attach to a patched Mednafen (agent interface, `EMU-021`), switch breakpoints to
log-and-continue (``bpmode log``), and set ``--kind`` breakpoints on
``--range`` (debugger syntax, for example ``06095544-06095EC3``), plus PC
breakpoints on any ``--pc-range``. Every
``--poll`` seconds the new lines of ``events.log`` are parsed. The run ends when
``out/STOP`` exists or Mednafen goes away. Then the breakpoints are cleared,
the mode is set back to halt, and ``out/summary.json`` lists each reading PC
with its hit count and first and last frames.

The address a hit touched is not in the event line; the registers are, so the
summary keeps the first hit's registers for each PC. Once ``--max-hits`` hits
are logged the breakpoints are cleared, so a busy range cannot flood the log.
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.agent import DEFAULT_DIR, Agent, AgentError


def parse_hit(line: str) -> dict[str, str] | None:
    if not line.startswith("hit "):
        return None
    return dict(part.split("=", 1) for part in line.split()[1:] if "=" in part)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path, help="output directory (ignored path)")
    parser.add_argument("--range", dest="ranges", action="append", required=True)
    parser.add_argument("--kind", choices=("read", "write", "pc"), default="read")
    parser.add_argument(
        "--pc-range", action="append", default=[], help="also log these PCs"
    )
    parser.add_argument("--agent-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--poll", type=float, default=1.0)
    parser.add_argument("--max-hits", type=int, default=5000)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    agent = Agent(args.agent_dir.resolve(), 10)
    agent.clear_events()  # the log grows across runs; read only this one's hits
    seen = 0
    by_pc: dict[str, dict[str, object]] = {}
    total = 0
    agent.bpmode("log")
    agent.breakpoints(args.kind, args.ranges)
    if args.pc_range:
        agent.breakpoints("pc", args.pc_range)
    armed = True
    try:
        while not (out / "STOP").exists():
            time.sleep(args.poll)
            lines = agent.events()
            for line in lines[seen:]:
                hit = parse_hit(line)
                if hit is None:
                    continue
                total += 1
                pc = hit.get("PC", "?")
                frame = int(hit.get("frame", "0"))
                entry = by_pc.setdefault(
                    pc, {"hits": 0, "first_frame": frame, "first_hit": hit}
                )
                entry["hits"] = int(str(entry["hits"])) + 1
                entry["last_frame"] = frame
            seen = len(lines)
            if armed and total >= args.max_hits:
                agent.breakpoints(args.kind)
                if args.pc_range:
                    agent.breakpoints("pc")
                armed = False
            summary = {"total_hits": total, "armed": armed, "pcs": by_pc}
            (out / "summary.json").write_text(json.dumps(summary, indent=1))
    except AgentError as error:
        print(f"stopped: {error}")
    finally:
        try:
            agent.breakpoints(args.kind)
            if args.pc_range:
                agent.breakpoints("pc")
            agent.bpmode("halt")
        except AgentError:
            pass
    print(f"{total} hits at {len(by_pc)} PCs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
