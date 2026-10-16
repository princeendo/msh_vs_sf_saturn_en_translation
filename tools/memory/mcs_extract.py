"""Extract raw Saturn memory regions from stock Mednafen 1.32.1 save states.

The container layout follows ``MDFNSS_SaveSM`` and ``MDFNSS_StateAction`` in
Mednafen 1.32.1 ``src/state.cpp``:

* optional gzip wrapping (``filesys.state_comp_level``);
* a 32-byte header: ``MDFNSVST`` magic, 64-bit time, 32-bit version at offset 16,
  31-bit total length at offset 20 (bit 31 set when variable data is big-endian),
  and 32-bit preview width and height at offsets 24 and 28, all little-endian;
* a ``width * height * 3`` byte preview image;
* sections, each a 32-byte NUL-padded name and a little-endian 32-bit size,
  containing variables, each a length-prefixed name, a little-endian 32-bit size,
  and the raw variable bytes.

Element widths are not stored in the file. The region table below records them
from the Saturn module source. Extracted data is research evidence only for regions
validated against a stock debugger dump (see ``AGENTS.md``).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
import zlib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

HEADER_MAGIC = b"MDFNSVST"
HEADER_SIZE = 32
SECTION_NAME_SIZE = 32
GZIP_MAGIC = b"\x1f\x8b"
BIG_ENDIAN_FLAG = 0x80000000
DEFAULT_OUTPUT_ROOT = Path("research/memory_dumps")


class StateFormatError(ValueError):
    """Raised when a file does not match the documented save-state layout."""


@dataclass(frozen=True)
class RegionSpec:
    """A Saturn memory region stored as one or more save-state variables."""

    name: str
    section: str
    variables: tuple[str, ...]
    element_width: int
    base_address: int
    size: int
    provenance: str


# Section and variable names, element widths, and sizes come from Mednafen 1.32.1
# Saturn sources. Base addresses are that build's bus mapping.
REGIONS: dict[str, RegionSpec] = {
    spec.name: spec
    for spec in (
        RegionSpec(
            "wram_l",
            "MAIN",
            ("WorkRAML",),
            2,
            0x00200000,
            0x100000,
            "ss/ss.cpp: uint16 WorkRAML[]; SFVAR(WorkRAML); map 0x00200000",
        ),
        RegionSpec(
            "wram_h",
            "MAIN",
            ("WorkRAMH",),
            2,
            0x06000000,
            0x100000,
            "ss/ss.cpp: uint16 WorkRAMH[]; SFVAR(WorkRAMH); map 0x06000000",
        ),
        RegionSpec(
            "cart_ram",
            "CART_EXTRAM",
            ("LO", "HI"),
            2,
            0x02400000,
            0x400000,
            "ss/cart/extram.cpp: uint16 ExtRAM[]; LO/HI; map 0x02400000 (4 MiB)",
        ),
        RegionSpec(
            "vdp1_vram",
            "VDP1",
            ("VRAM",),
            2,
            0x05C00000,
            0x80000,
            "ss/vdp1.cpp: uint16 VRAM[0x40000]; SFVAR(VRAM); map 0x05C00000",
        ),
        RegionSpec(
            "vdp2_vram",
            "VDP2",
            ("VRAM",),
            2,
            0x05E00000,
            0x80000,
            "ss/vdp2.cpp: uint16 VRAM[262144]; SFVAR(VRAM); map 0x05E00000",
        ),
    )
}


@dataclass(frozen=True)
class StateHeader:
    """Fields decoded from the 32-byte save-state header."""

    version: int
    total_length: int
    big_endian_data: bool
    preview_width: int
    preview_height: int


@dataclass(frozen=True)
class SaveState:
    """Decoded save-state header and section variables."""

    header: StateHeader
    sections: dict[str, dict[str, bytes]]
    preview_rgb: bytes = b""


def decompress(raw: bytes) -> bytes:
    """Return the uncompressed state bytes, unwrapping gzip when present."""
    return gzip.decompress(raw) if raw.startswith(GZIP_MAGIC) else raw


def _read_u32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise StateFormatError(f"truncated 32-bit field at offset {offset:#x}")
    value: int = struct.unpack_from("<I", data, offset)[0]
    return value


def _parse_variables(data: bytes, start: int, end: int) -> dict[str, bytes]:
    variables: dict[str, bytes] = {}
    pos = start
    while pos < end:
        name_length = data[pos]
        name_end = pos + 1 + name_length
        if name_end + 4 > end:
            raise StateFormatError(f"truncated variable header at offset {pos:#x}")
        name = data[pos + 1 : name_end].decode("latin-1")
        size = _read_u32(data, name_end)
        value_start = name_end + 4
        value_end = value_start + size
        if value_end > end:
            raise StateFormatError(f"variable {name!r} exceeds its section")
        if name in variables:
            raise StateFormatError(f"duplicate variable {name!r}")
        variables[name] = data[value_start:value_end]
        pos = value_end
    return variables


def parse_state(raw: bytes) -> SaveState:
    """Decode a full (non-data-only) Mednafen save state."""
    data = decompress(raw)
    if len(data) < HEADER_SIZE or not data.startswith(HEADER_MAGIC):
        raise StateFormatError("missing MDFNSVST header")

    length_field = _read_u32(data, 20)
    header = StateHeader(
        version=_read_u32(data, 16),
        total_length=length_field & ~BIG_ENDIAN_FLAG,
        big_endian_data=bool(length_field & BIG_ENDIAN_FLAG),
        preview_width=_read_u32(data, 24),
        preview_height=_read_u32(data, 28),
    )
    if header.total_length > len(data):
        raise StateFormatError("header length exceeds state data")

    pos = HEADER_SIZE + header.preview_width * header.preview_height * 3
    preview_rgb = data[HEADER_SIZE:pos]
    sections: dict[str, dict[str, bytes]] = {}
    while pos < header.total_length:
        name_end = pos + SECTION_NAME_SIZE
        name = data[pos:name_end].split(b"\x00", 1)[0].decode("latin-1")
        size = _read_u32(data, name_end)
        body_start = name_end + 4
        body_end = body_start + size
        if body_end > header.total_length:
            raise StateFormatError(f"section {name!r} exceeds state length")
        if name in sections:
            raise StateFormatError(f"duplicate section {name!r}")
        sections[name] = _parse_variables(data, body_start, body_end)
        pos = body_end
    return SaveState(header=header, sections=sections, preview_rgb=preview_rgb)


def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    """Encode 8-bit RGB pixels as a PNG image."""
    if len(rgb) != width * height * 3:
        raise StateFormatError("preview size does not match its dimensions")
    stride = width * 3
    scanlines = b"".join(
        b"\x00" + rgb[row * stride : (row + 1) * stride] for row in range(height)
    )

    def chunk(kind: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(scanlines))
        + chunk(b"IEND", b"")
    )


def swap_elements(data: bytes, width: int) -> bytes:
    """Reverse the byte order of each ``width``-byte element."""
    if width == 1:
        return data
    if len(data) % width:
        raise StateFormatError(f"length {len(data)} is not a multiple of {width}")
    swapped = bytearray(len(data))
    for index in range(width):
        swapped[index::width] = data[width - 1 - index :: width]
    return bytes(swapped)


def extract_region(state: SaveState, spec: RegionSpec, byte_order: str) -> bytes:
    """Return a region as Saturn big-endian bytes or as stored in the state."""
    section = state.sections.get(spec.section)
    if section is None:
        raise StateFormatError(f"missing section {spec.section!r}")
    parts = []
    for variable in spec.variables:
        if variable not in section:
            raise StateFormatError(f"missing variable {spec.section}/{variable}")
        parts.append(section[variable])
    stored = b"".join(parts)
    if len(stored) != spec.size:
        raise StateFormatError(
            f"{spec.name}: expected {spec.size} bytes, found {len(stored)}"
        )
    if byte_order == "state" or state.header.big_endian_data:
        return stored
    return swap_elements(stored, spec.element_width)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract raw Saturn memory regions from a Mednafen save state."
    )
    parser.add_argument("state", type=Path, help="Mednafen 1.32.1 save-state file")
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="output directory (default: research/memory_dumps/<state sha256[:16]>)",
    )
    parser.add_argument(
        "--region",
        action="append",
        choices=sorted(REGIONS),
        help="region to extract; repeatable (default: all)",
    )
    parser.add_argument(
        "--byte-order",
        choices=("saturn", "state"),
        default="saturn",
        help="saturn: big-endian bus order; state: bytes as stored in the state",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list sections and variables instead of extracting",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="replace existing output files"
    )
    return parser


def _list_sections(state: SaveState) -> None:
    header = state.header
    print(
        f"version={header.version:#x} total_length={header.total_length} "
        f"big_endian_data={header.big_endian_data} "
        f"preview={header.preview_width}x{header.preview_height}"
    )
    for section_name, variables in state.sections.items():
        print(f"[{section_name}]")
        for variable, value in variables.items():
            print(f"  {variable}: {len(value)} bytes")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    state_path: Path = args.state
    try:
        raw = state_path.read_bytes()
        state = parse_state(raw)
    except (OSError, StateFormatError, gzip.BadGzipFile) as error:
        parser.error(str(error))

    if args.list:
        _list_sections(state)
        return 0

    input_hash = sha256(raw)
    out_dir: Path = args.out_dir or DEFAULT_OUTPUT_ROOT / input_hash[:16]
    names: list[str] = args.region or sorted(REGIONS)
    suffix = "" if args.byte_order == "saturn" else ".state-order"
    outputs = {name: out_dir / f"{name}{suffix}.bin" for name in names}
    manifest_path = out_dir / f"manifest{suffix}.json"
    header = state.header
    has_preview = header.preview_width > 0 and header.preview_height > 0
    preview_path = out_dir / "preview.png"
    targets = [*outputs.values(), manifest_path]
    if has_preview:
        targets.append(preview_path)
    resolved_input = state_path.resolve()
    for path in targets:
        if path.resolve() == resolved_input:
            parser.error(f"output would overwrite the input: {path}")
        if path.exists() and not args.overwrite:
            parser.error(f"output exists (use --overwrite): {path}")

    try:
        regions = {
            name: extract_region(state, REGIONS[name], args.byte_order)
            for name in names
        }
    except StateFormatError as error:
        parser.error(str(error))

    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, data in regions.items():
        spec = REGIONS[name]
        outputs[name].write_bytes(data)
        records.append(
            {
                "region": name,
                "file": outputs[name].name,
                "base_address": f"0x{spec.base_address:08X}",
                "size_bytes": len(data),
                "sha256": sha256(data),
                "section": spec.section,
                "variables": list(spec.variables),
                "element_width": spec.element_width,
                "provenance": spec.provenance,
            }
        )
    preview_record: dict[str, object] | None = None
    if has_preview:
        png = encode_png(header.preview_width, header.preview_height, state.preview_rgb)
        preview_path.write_bytes(png)
        preview_record = {
            "file": preview_path.name,
            "width": header.preview_width,
            "height": header.preview_height,
            "sha256": sha256(png),
            "note": "Mednafen save-time screen thumbnail, scaled by the emulator",
        }
    manifest = {
        "tool": "tools.memory.mcs_extract",
        "byte_order": args.byte_order,
        "input": {
            "filename": state_path.name,
            "size_bytes": len(raw),
            "sha256": input_hash,
        },
        "header": {
            "version": f"0x{state.header.version:X}",
            "big_endian_data": state.header.big_endian_data,
            "preview": [state.header.preview_width, state.header.preview_height],
        },
        "preview": preview_record,
        "regions": records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    for record in records:
        print(f"{record['sha256']}  {out_dir / str(record['file'])}")
    if has_preview:
        print(f"preview: {preview_path}")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
