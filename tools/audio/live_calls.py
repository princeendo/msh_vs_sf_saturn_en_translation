"""Log mixer clip starts live while the user plays, flagging name calls (LOC-005).

Attaches to a running patched Mednafen (agent interface) without pausing it, like
``tools/mednafen/session_recorder.py``, and until ``out/STOP`` exists polls the 16
SH-2 mixer channel records every ``--period`` seconds (layout in
``tools/audio/channel_check.py``). A channel whose (start, end) changed has
started a clip. It is named from every sound bank on the disc
(``tools/audio/sound_bank.py``):

- clips in work RAM or sound RAM by their first bytes and length
  (``mixer_log.clip_index``);
- clips in cartridge RAM, which the agent cannot read, by length alone, so the
  label lists every clip of that length (``"by_length": true``).

Name calls (`EXP-0057`, `EXP-0058`) are flagged in ``"call"``. A clip shorter
than the poll period can be missed. Each start is appended to ``calls.jsonl``
with the emulator frame. Output goes to ``out``, an ignored path.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import time
from collections.abc import Sequence
from pathlib import Path

from tools.audio.channel_check import CHANNELS, RECORD_SIZE, RECORDS_POINTER
from tools.audio.mixer_log import PROBE, clip_index, in_cart, read_data
from tools.audio.sound_bank import TRACK
from tools.mednafen.agent import DEFAULT_DIR, Agent, AgentError

NAME_CALLS = {
    0x286: "Vega",
    0x04F: "Bison",
    0x048: "Gouki",
    0x338: "Akuma",
    0x082: "Mech Gouki",
    0x05B: "Cyber Akuma",
}


def call_of(labels: Sequence[str]) -> str | None:
    """The name call among clip labels such as ``pl0e_1#1(0x04F)``, if any."""
    for label in labels:
        match = re.search(r"\(0x([0-9A-F]{3})\)$", label)
        if match and int(match.group(1), 16) in NAME_CALLS:
            return NAME_CALLS[int(match.group(1), 16)]
    return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path, help="output directory (ignored path)")
    parser.add_argument("--agent-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--period", type=float, default=0.02)
    parser.add_argument("--track", type=Path, default=TRACK)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    index = clip_index(args.track)
    by_length: dict[int, list[str]] = {}
    for (_, length), labels in index.items():
        by_length.setdefault(length, []).extend(labels)
    agent = Agent(args.agent_dir.resolve(), 10)
    previous: dict[int, tuple[int, int]] = {}
    first = True
    with (out / "calls.jsonl").open("a") as log:
        while not (out / "STOP").exists():
            try:
                frame = int(agent.status()["frame"])
                records = struct.unpack(">I", agent.bus_read(RECORDS_POINTER, 4))[0]
                if not 0x06000000 <= records < 0x06100000:
                    time.sleep(args.period)
                    continue
                table = agent.bus_read(records, RECORD_SIZE * CHANNELS)
            except AgentError:
                time.sleep(1)
                continue
            for channel in range(CHANNELS):
                start, end = struct.unpack_from(">II", table, RECORD_SIZE * channel)
                if not start or end <= start or previous.get(channel) == (start, end):
                    continue
                previous[channel] = (start, end)
                if first:
                    continue  # already playing when the logger attached
                row: dict[str, object] = {
                    "frame": frame,
                    "channel": channel,
                    "start": f"0x{start:08X}",
                    "length": end - start,
                }
                if in_cart(start):
                    labels = by_length.get(end - start, [])
                    row["by_length"] = True
                else:
                    labels = index.get(
                        (read_data(agent, start, PROBE), end - start), []
                    )
                row["clips"] = labels
                call = call_of(labels)
                if call:
                    row["call"] = call
                log.write(json.dumps(row) + "\n")
                log.flush()
                if call:
                    print(f"frame {frame}: name call {call!r} {labels}", flush=True)
            first = False
            time.sleep(args.period)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
