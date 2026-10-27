"""Write bytes into one memory region of a Mednafen save state (UI-006).

The reverse of ``mcs_extract`` for checkpoints: it overwrites ``data`` at a bus
address inside one region (for example the quote font in cart RAM, which the
agent cannot write) and saves the whole state again, uncompressed. Every other
byte is kept. ``data`` is Saturn big-endian; it is stored in the state's element
order, as ``mcs_extract`` reads it. A patched state is a test checkpoint only:
it mixes memory from two builds, so findings from it need a matching cold-boot
check before they count (``AGENTS.md``).
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import (
    HEADER_SIZE,
    REGIONS,
    SECTION_NAME_SIZE,
    StateFormatError,
    _read_u32,
    decompress,
    parse_state,
    swap_elements,
)


def variable_spans(data: bytes) -> dict[tuple[str, str], tuple[int, int]]:
    """(section, variable) -> (start, size) of each variable's bytes in ``data``."""
    total = _read_u32(data, 20) & 0x7FFFFFFF
    pos = HEADER_SIZE + _read_u32(data, 24) * _read_u32(data, 28) * 3
    spans: dict[tuple[str, str], tuple[int, int]] = {}
    while pos < total:
        name_end = pos + SECTION_NAME_SIZE
        section = data[pos:name_end].split(b"\x00", 1)[0].decode("latin-1")
        end = name_end + 4 + _read_u32(data, name_end)
        cursor = name_end + 4
        while cursor < end:
            length = data[cursor]
            variable = data[cursor + 1 : cursor + 1 + length].decode("latin-1")
            size = _read_u32(data, cursor + 1 + length)
            start = cursor + 1 + length + 4
            spans[(section, variable)] = (start, size)
            cursor = start + size
        pos = end
    return spans


def patch_region(raw: bytes, region: str, address: int, data: bytes) -> bytes:
    """The uncompressed state with ``data`` written at bus ``address``."""
    spec = REGIONS[region]
    offset = address - spec.base_address
    if offset < 0 or offset + len(data) > spec.size:
        raise StateFormatError(f"{address:#x}+{len(data)} is outside {region}")
    width = spec.element_width
    if offset % width or len(data) % width:
        raise StateFormatError(f"the write must be aligned to {width}-byte elements")
    state = bytearray(decompress(raw))
    big_endian = parse_state(bytes(state)).header.big_endian_data
    stored = data if big_endian else swap_elements(data, width)
    spans = variable_spans(bytes(state))
    base = 0
    for variable in spec.variables:
        start, size = spans[(spec.section, variable)]
        lo, hi = max(offset, base), min(offset + len(data), base + size)
        if lo < hi:
            state[start + lo - base : start + hi - base] = stored[
                lo - offset : hi - offset
            ]
        base += size
    return bytes(state)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("state", type=Path)
    parser.add_argument("out", type=Path, help="patched state (ignored location)")
    parser.add_argument("--region", required=True, choices=sorted(REGIONS))
    parser.add_argument("--address", required=True, type=lambda x: int(x, 16))
    parser.add_argument("--data", required=True, type=Path, help="bytes to write")
    args = parser.parse_args(argv)
    patched = patch_region(
        args.state.read_bytes(), args.region, args.address, args.data.read_bytes()
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(patched)
    print(f"{args.out}: {len(args.data.read_bytes())} bytes at {args.address:#x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
