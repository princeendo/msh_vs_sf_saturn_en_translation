from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.memory.make_patch import build, main, parse_write


def test_parse_write() -> None:
    assert parse_write("0x2091F8=0x0801") == (0x2091F8, 0x801)
    with pytest.raises(ValueError):
        parse_write("0x2091F8")


def test_build_records_original_and_modified_bytes() -> None:
    region = bytes(range(16))

    original, patched, changes = build(
        region, 0x200000, 0x200004, 0x200009, [(0x200006, 0xABCD)]
    )

    assert original == bytes([4, 5, 6, 7, 8, 9])
    assert patched == bytes([4, 5, 0xAB, 0xCD, 8, 9])
    assert changes == [
        {"address": "0x00200006", "original": "06 07", "modified": "ab cd"}
    ]


@pytest.mark.parametrize(
    ("start", "end", "writes"),
    [
        (0x200000, 0x200020, [(0x200000, 1)]),  # range outside region
        (0x200000, 0x200003, [(0x200004, 1)]),  # write outside range
        (0x200000, 0x200003, [(0x200001, 1)]),  # misaligned
        (0x200000, 0x200003, [(0x200000, 1), (0x200000, 2)]),  # duplicate
        (0x200000, 0x200003, [(0x200000, 0x10000)]),  # too large
    ],
)
def test_build_rejects_invalid_requests(
    start: int, end: int, writes: list[tuple[int, int]]
) -> None:
    with pytest.raises(ValueError):
        build(bytes(16), 0x200000, start, end, writes)


def test_main_writes_files_and_manifest(tmp_path: Path) -> None:
    region = tmp_path / "wram_l.bin"
    region.write_bytes(bytes(8))
    prefix = tmp_path / "out" / "test"

    args = [
        str(region),
        "--region-base",
        "0x200000",
        "--start",
        "0x200002",
        "--end",
        "0x200005",
        "--write",
        "0x200004=0x0801",
        "--out-prefix",
        str(prefix),
        "--purpose",
        "synthetic",
    ]
    assert main(args) == 0

    patched = (tmp_path / "out" / "test-patched.bin").read_bytes()
    manifest = json.loads((tmp_path / "out" / "test-manifest.json").read_text())
    assert patched == bytes([0, 0, 0x08, 0x01])
    assert manifest["range"]["region_offset_start"] == "0x00000002"
    assert manifest["changes"][0]["modified"] == "08 01"
    assert region.read_bytes() == bytes(8)
