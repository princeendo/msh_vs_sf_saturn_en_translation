from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.test_iso9660 import make_image
from tools.disc.iso9660 import RAW_SECTOR
from tools.disc.patch_image import find_entry, replace_file
from tools.disc.sector import is_valid, regenerate


def valid_image() -> bytes:
    raw = make_image()
    return b"".join(
        regenerate(raw[i : i + RAW_SECTOR]) for i in range(0, len(raw), RAW_SECTOR)
    )


def test_regenerate_is_stable_and_detects_changes() -> None:
    sector = valid_image()[:RAW_SECTOR]
    assert is_valid(sector)
    broken = bytearray(sector)
    broken[100] ^= 1
    assert not is_valid(bytes(broken))
    assert regenerate(bytes(broken)) != sector


def test_replace_file_rewrites_only_its_sectors(tmp_path: Path) -> None:
    source = tmp_path / "track.bin"
    source.write_bytes(valid_image())
    lsn, size = find_entry(source, "SUB/B.DAT;1")
    target = tmp_path / "out.bin"

    changed = replace_file(source, target, lsn, size, b"Q" * 2048 + b"RS")

    original = source.read_bytes()
    derived = target.read_bytes()
    assert [c["lsn"] for c in changed] == [21, 22]
    for index in range(len(original) // RAW_SECTOR):
        a = original[index * RAW_SECTOR : (index + 1) * RAW_SECTOR]
        b = derived[index * RAW_SECTOR : (index + 1) * RAW_SECTOR]
        assert is_valid(b)
        assert (a != b) == (index in (21, 22))
    last = derived[22 * RAW_SECTOR : 23 * RAW_SECTOR]
    assert last[16:18] == b"RS"
    # bytes after the file end in the last sector are preserved
    assert (
        last[18 : 16 + 2048]
        == original[22 * RAW_SECTOR + 18 : 22 * RAW_SECTOR + 16 + 2048]
    )


def test_replace_file_requires_same_size(tmp_path: Path) -> None:
    source = tmp_path / "track.bin"
    source.write_bytes(valid_image())
    with pytest.raises(ValueError):
        replace_file(source, tmp_path / "o.bin", 20, 5, b"too long")
