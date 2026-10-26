"""Log which bank clip each SH-2 mixer channel starts, frame by frame (EXP-0057).

The tool launches the patched Mednafen (agent interface) on ``cue``, loads
``state`` and runs ``--frames`` frames one at a time. After each frame it reads
the 16 mixer channel records (layout in ``tools/audio/channel_check.py``). A
channel whose (start, end) changed has started a new clip. Its first bytes are
read and matched to the clips of every sound bank on the disc
(``tools/audio/sound_bank.py``):

- work RAM and sound RAM are read through the agent when the clip starts;
- cartridge RAM has no agent space, and the agent cannot save a state while
  halted. Cart clips are therefore read from one state saved after the last
  frame, extracted with ``mcs_extract`` (not validated for cart RAM,
  ``DBG-012``). Fighter banks stay in cart RAM through a fight, and the length
  must match too.

``--poke`` writes bytes into an agent space after the state loads, for
controlled trials. The channels already playing on the first frame are logged with
``"initial": true``; they are not starts.

A match needs the clip's first ``PROBE`` bytes and its length to agree. Output is
one JSON object per start. Everything goes to ``out``, an ignored path.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from tools.audio.channel_check import CHANNELS, RECORD_SIZE, RECORDS_POINTER
from tools.audio.sound_bank import TRACK, disc_files, is_bank, pac_payloads, parse
from tools.mednafen.agent import Agent
from tools.mednafen.replay_state import BINARY, connect, wait_halted
from tools.memory.mcs_extract import REGIONS, extract_region, parse_state

PROBE = 64
SOUND_RAM = 0x05A00000
CART_RAM = 0x02400000


def clip_index(track: Path) -> dict[tuple[bytes, int], list[str]]:
    """(first PROBE bytes, length) -> clip labels, over every bank on the disc."""
    index: dict[tuple[bytes, int], list[str]] = {}
    for name, data in sorted(disc_files(track, ["*"]).items()):
        try:
            payloads = pac_payloads(data)
        except ValueError:
            continue
        for number, span in enumerate(payloads):
            if span is None:
                continue
            bank = data[span[0] : span[0] + span[1]]
            if not is_bank(bank):
                continue
            stem = f"{Path(name).stem.lower()}_{number}"
            for clip in parse(bank):
                key = (bank[clip.offset : clip.offset + PROBE], clip.length)
                label = f"{stem}#{clip.index}(0x{clip.clip_id:03X})"
                index.setdefault(key, []).append(label)
    return index


def in_cart(address: int) -> bool:
    return CART_RAM <= address & 0x0FFFFFFF < CART_RAM + 0x400000


def read_data(agent: Agent, address: int, length: int) -> bytes:
    plain = address & 0x0FFFFFFF
    if SOUND_RAM <= plain < SOUND_RAM + 0x80000:
        return agent.read("scspram", plain - SOUND_RAM, length)
    return agent.bus_read(address, length)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path)
    parser.add_argument("state", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--frames", type=int, default=600)
    parser.add_argument("--track", type=Path, default=TRACK)
    parser.add_argument(
        "--poke",
        action="append",
        default=[],
        help="SPACE:ADDRESS:HEX written after the state loads (e.g. scspram:758C:004F)",
    )
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    index = clip_index(args.track)
    agent_dir = Path("local/mednafen/agent").resolve()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(Path("local/mednafen").resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
    )
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    starts: list[dict[str, object]] = []
    try:
        agent = connect(agent_dir)
        time.sleep(2)
        agent.loadstate(args.state.resolve())
        for poke in args.poke:
            space, address, data = poke.split(":")
            agent.write(space, int(address, 16), bytes.fromhex(data))
        previous: dict[int, tuple[int, int]] = {}
        for step in range(args.frames):
            agent.frames(1)
            wait_halted(agent, 30)
            frame = int(agent.status()["frame"])
            records = struct.unpack(">I", agent.bus_read(RECORDS_POINTER, 4))[0]
            if not 0x06000000 <= records < 0x06100000:
                continue
            table = agent.bus_read(records, RECORD_SIZE * CHANNELS)
            for channel in range(CHANNELS):
                start, end = struct.unpack_from(">II", table, RECORD_SIZE * channel)
                if not start or end <= start or previous.get(channel) == (start, end):
                    continue
                previous[channel] = (start, end)
                row: dict[str, object] = {
                    "frame": frame,
                    "channel": channel,
                    "start": f"0x{start:08X}",
                    "length": end - start,
                    "initial": step == 0,
                }
                if not in_cart(start):
                    data = read_data(agent, start, PROBE)
                    row["clips"] = index.get((data, end - start), [])
                starts.append(row)
        agent.screenshot(out / "last.png")
        agent.run()
        agent.savestate(out / "probe.mcs")
        time.sleep(0.5)
        cart = extract_region(
            parse_state((out / "probe.mcs").read_bytes()), REGIONS["cart_ram"], "saturn"
        )
        for row in starts:
            if "clips" not in row:
                offset = int(str(row["start"]), 16) - CART_RAM
                data = cart[offset : offset + PROBE]
                row["clips"] = index.get((data, int(str(row["length"]))), [])
    finally:
        proc.terminate()
        proc.wait(10)
        (out / "probe.mcs").unlink(missing_ok=True)
    (out / "starts.json").write_text(json.dumps(starts, indent=1) + "\n")
    for row in starts:
        print(json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
