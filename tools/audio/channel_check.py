"""Check ``cmnse_bank.decode`` against the game's own mixer channels (EXP-0055).

The SH-2 mixer (``0x0600D338``) walks 16 channels (``mov #16`` at ``0x0600D33E``)
with one 44-byte record each. The record table's address is at ``0x06012B6C``
and the active-channel mask (bit 15 = channel 0) at ``0x060132D4``. Each record
holds:

- ``+0`` start, ``+4`` end, ``+8`` next byte to decode;
- ``+12`` step and ``+16`` predictor after the last decoded byte;
- ``+20`` loop start, with ``+24`` predictor and ``+28`` step there;
- ``+36``/``+40`` left and right volume (16.16).

For each channel, the data from start to the next byte is decoded from predictor
0 and step ``0x80``. The prediction is that the result equals the stored step and
predictor. Clip data lives in sound RAM, WRAM-L or cartridge RAM. Sound RAM is
read from the state's ``SCSP``/``RAM`` variable, swapped to bus order like the
other regions. That region is not validated against a debugger dump (``DBG-012``).
"""

from __future__ import annotations

import argparse
import json
import struct
from collections.abc import Sequence
from pathlib import Path

from tools.audio.cmnse_bank import decode_state
from tools.memory.mcs_extract import REGIONS, extract_region, parse_state, swap_elements

DECODER = 0x0600D420
# tst #8,r0; and #7,r0; muls.w r7,r0; sts macl,r1
DECODER_CODE = bytes.fromhex("c808c907207f011a")
RECORDS_POINTER = 0x06012B6C
ACTIVE_MASK = 0x060132D4
CHANNELS = 16
RECORD_SIZE = 44
SOUND_RAM = 0x05A00000


def signed(value: int) -> int:
    return value - (1 << 32) if value & 0x80000000 else value


def check(raw: bytes) -> list[dict[str, object]]:
    state = parse_state(raw)
    sound = state.sections["SCSP"]["RAM"]
    if not state.header.big_endian_data:
        sound = swap_elements(sound, 2)
    areas = [(SOUND_RAM, sound)] + [
        (REGIONS[name].base_address, extract_region(state, REGIONS[name], "saturn"))
        for name in ("wram_l", "wram_h", "cart_ram")
    ]

    def read(address: int, length: int) -> bytes:
        address &= 0x0FFFFFFF
        for base, data in areas:
            if base <= address and address + length <= base + len(data):
                return data[address - base : address - base + length]
        raise ValueError(f"0x{address:08X} is not in a known region")

    mask = struct.unpack(">I", read(ACTIVE_MASK, 4))[0]
    if read(DECODER, len(DECODER_CODE)) != DECODER_CODE:
        return []  # the mixer program is not loaded
    records = struct.unpack(">I", read(RECORDS_POINTER, 4))[0]
    if not 0x06000000 <= records < 0x06100000:
        return []  # the record table is not set up
    rows: list[dict[str, object]] = []
    for channel in range(CHANNELS):
        fields = struct.unpack(">11I", read(records + RECORD_SIZE * channel, 44))
        start, end, cursor, step, predictor = fields[:5]
        if not start or not start <= cursor <= end:
            continue
        _, *replay = decode_state(read(start, cursor - start))
        stored = [signed(predictor), step]
        rows.append(
            {
                "channel": channel,
                "active": bool(mask & (0x8000 >> channel)),
                "start": f"0x{start:08X}",
                "decoded_bytes": cursor - start,
                "stored": stored,
                "replayed": replay,
                "match": replay == stored,
            }
        )
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("state", type=Path, help="Mednafen 1.32.1 save state")
    args = parser.parse_args(argv)
    rows = check(args.state.read_bytes())
    print(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
