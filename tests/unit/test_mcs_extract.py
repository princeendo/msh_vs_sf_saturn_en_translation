from __future__ import annotations

import gzip
import hashlib
import json
import struct
from pathlib import Path

import pytest

from tools.memory.mcs_extract import (
    REGIONS,
    RegionSpec,
    StateFormatError,
    extract_region,
    main,
    parse_state,
    swap_elements,
)


def make_section(name: str, variables: dict[str, bytes]) -> bytes:
    body = b"".join(
        bytes([len(var)]) + var.encode() + struct.pack("<I", len(value)) + value
        for var, value in variables.items()
    )
    return name.encode().ljust(32, b"\x00") + struct.pack("<I", len(body)) + body


def make_state(
    sections: dict[str, dict[str, bytes]],
    preview: tuple[int, int] = (2, 1),
    big_endian: bool = False,
    compress: bool = True,
) -> bytes:
    width, height = preview
    body = b"\xaa" * (width * height * 3)
    body += b"".join(make_section(name, v) for name, v in sections.items())
    total = 32 + len(body)
    length_field = total | (0x80000000 if big_endian else 0)
    header = b"MDFNSVST" + struct.pack("<QIIII", 0, 0x103201, length_field, *preview)
    data = header + body + b"trailing"
    return gzip.compress(data) if compress else data


def pattern(size: int) -> bytes:
    return bytes(index % 251 for index in range(size))


def test_parse_state_reads_header_sections_and_variables() -> None:
    raw = make_state({"MAIN": {"A": b"\x01\x02", "B": b""}, "VDP1": {"VRAM": b"x"}})

    state = parse_state(raw)

    assert state.header.version == 0x103201
    assert state.header.preview_width == 2
    assert state.header.big_endian_data is False
    assert state.sections == {
        "MAIN": {"A": b"\x01\x02", "B": b""},
        "VDP1": {"VRAM": b"x"},
    }


def test_parse_state_accepts_uncompressed_states() -> None:
    raw = make_state({"MAIN": {"A": b"\x01"}}, compress=False)

    assert parse_state(raw).sections == {"MAIN": {"A": b"\x01"}}


def test_parse_state_rejects_missing_magic() -> None:
    with pytest.raises(StateFormatError, match="MDFNSVST"):
        parse_state(gzip.compress(b"NOTSTATE" + bytes(40)))


def test_parse_state_rejects_truncated_section() -> None:
    raw = bytearray(make_state({"MAIN": {"A": b"\x01\x02"}}, compress=False))
    struct.pack_into("<I", raw, 32 + 6 + 32, 999)

    with pytest.raises(StateFormatError, match="exceeds"):
        parse_state(bytes(raw))


def test_swap_elements_reverses_each_element() -> None:
    assert swap_elements(b"\x01\x02\x03\x04", 2) == b"\x02\x01\x04\x03"
    assert swap_elements(b"\x01\x02\x03\x04", 4) == b"\x04\x03\x02\x01"
    with pytest.raises(StateFormatError):
        swap_elements(b"\x01\x02\x03", 2)


def test_extract_region_orders_and_concatenates_variables() -> None:
    spec = RegionSpec("test", "CART", ("LO", "HI"), 2, 0x1000, 4, "synthetic")
    state = parse_state(make_state({"CART": {"LO": b"\x01\x02", "HI": b"\x03\x04"}}))

    assert extract_region(state, spec, "saturn") == b"\x02\x01\x04\x03"
    assert extract_region(state, spec, "state") == b"\x01\x02\x03\x04"


def test_extract_region_keeps_big_endian_state_data() -> None:
    spec = RegionSpec("test", "MAIN", ("A",), 2, 0, 2, "synthetic")
    state = parse_state(make_state({"MAIN": {"A": b"\x01\x02"}}, big_endian=True))

    assert extract_region(state, spec, "saturn") == b"\x01\x02"


def test_extract_region_rejects_wrong_size_and_missing_data() -> None:
    spec = RegionSpec("test", "MAIN", ("A",), 2, 0, 4, "synthetic")
    state = parse_state(make_state({"MAIN": {"A": b"\x01\x02"}}))

    with pytest.raises(StateFormatError, match="expected 4 bytes"):
        extract_region(state, spec, "saturn")
    with pytest.raises(StateFormatError, match="missing variable"):
        extract_region(state, RegionSpec("t", "MAIN", ("Z",), 2, 0, 2, "s"), "saturn")
    with pytest.raises(StateFormatError, match="missing section"):
        extract_region(state, RegionSpec("t", "X", ("A",), 2, 0, 2, "s"), "saturn")


def test_main_writes_regions_and_manifest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stored = pattern(REGIONS["wram_h"].size)
    state_path = tmp_path / "synthetic.mc2"
    state_path.write_bytes(make_state({"MAIN": {"WorkRAMH": stored}}))
    out_dir = tmp_path / "out"

    args = [str(state_path), "--out-dir", str(out_dir), "--region", "wram_h"]
    assert main(args) == 0

    extracted = (out_dir / "wram_h.bin").read_bytes()
    assert extracted == swap_elements(stored, 2)
    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert (
        manifest["input"]["sha256"]
        == hashlib.sha256(state_path.read_bytes()).hexdigest()
    )
    assert manifest["regions"] == [
        {
            "region": "wram_h",
            "file": "wram_h.bin",
            "base_address": "0x06000000",
            "size_bytes": 0x100000,
            "sha256": hashlib.sha256(extracted).hexdigest(),
            "section": "MAIN",
            "variables": ["WorkRAMH"],
            "element_width": 2,
            "provenance": REGIONS["wram_h"].provenance,
        }
    ]
    assert "manifest:" in capsys.readouterr().out

    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert main([*args, "--overwrite"]) == 0


def test_main_lists_sections(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    state_path = tmp_path / "synthetic.mc0"
    state_path.write_bytes(make_state({"MAIN": {"WorkRAML": b"\x00\x01"}}))

    assert main([str(state_path), "--list"]) == 0

    output = capsys.readouterr().out
    assert "[MAIN]" in output
    assert "WorkRAML: 2 bytes" in output


def test_main_rejects_invalid_state(tmp_path: Path) -> None:
    state_path = tmp_path / "bad.mc0"
    state_path.write_bytes(b"not a state")

    with pytest.raises(SystemExit) as error:
        main([str(state_path), "--list"])
    assert error.value.code == 2
