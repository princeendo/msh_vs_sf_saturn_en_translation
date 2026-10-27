from __future__ import annotations

import bz2
import io
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from tests.unit.test_patch_image import valid_image
from tools.disc.iso9660 import RAW_SECTOR
from tools.disc.make_ssp import (
    BSDIFF_MAGIC,
    SSP_VERSION,
    apply_ssp,
    bsdiff40,
    bspatch,
    build_ssp,
    changed_files,
    drive_order,
    entries,
    offtin,
    offtout,
    read_ssp,
)
from tools.disc.patch_image import replace_file

META = {
    "Name": "Test",
    "Author": "Someone",
    "URL": "https://example.invalid",
    "Version": "0.0.1",
    "Description": "synthetic",
    "Contact": "https://example.invalid/issues",
}


def images(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source.bin"
    source.write_bytes(valid_image())
    built = tmp_path / "built.bin"
    replace_file(source, built, 20, 5, b"HELLO")
    return source, built


def test_offt_round_trips_sign_magnitude() -> None:
    for value in (0, 1, 2352, -1, -(1 << 40)):
        assert offtin(offtout(value)) == value
    assert offtout(-1) == b"\x01" + bytes(6) + b"\x80"


def test_bsdiff40_round_trips() -> None:
    old = bytes(range(256)) * 40
    new = bytearray(old)
    new[5000:5010] = b"0123456789"
    patch = bsdiff40(old, bytes(new))
    assert patch[:8] == BSDIFF_MAGIC
    assert offtin(patch[24:32]) == len(new)
    assert bspatch(old, patch) == bytes(new)


def test_bsdiff40_matches_moved_data() -> None:
    blob = bytes((i * 7919 + (i >> 5) * 31) % 251 for i in range(20000))
    old = blob + bytes(1000)
    new = bytes(1000) + blob
    patch = bsdiff40(old, new)
    assert bspatch(old, patch) == new
    assert len(patch) < 600
    assert bspatch(b"", bsdiff40(b"", b"abc")) == b"abc"


@pytest.mark.skipif(shutil.which("bspatch") is None, reason="no system bspatch")
def test_system_bspatch_applies_the_patch(tmp_path: Path) -> None:
    old = bytes(range(256)) * 40
    new = old[:100] + b"\xff" * 300 + old[400:]
    (tmp_path / "old").write_bytes(old)
    (tmp_path / "p").write_bytes(bsdiff40(old, new))
    subprocess.run(
        ["bspatch", str(tmp_path / "old"), str(tmp_path / "new"), str(tmp_path / "p")],
        check=True,
    )
    assert (tmp_path / "new").read_bytes() == new


def test_bspatch_follows_insert_and_seek() -> None:
    old = b"abcdefgh"
    ctrl = offtout(2) + offtout(3) + offtout(2) + offtout(2) + offtout(0) + offtout(0)
    diff = bytes([0, 1, 0, 0])
    parts = [bz2.compress(ctrl), bz2.compress(diff), bz2.compress(b"XYZ")]
    header = BSDIFF_MAGIC + offtout(len(parts[0])) + offtout(len(parts[1]))
    # a, b+1 -> "ac"; insert "XYZ"; skip c, d; e, f -> "ef"
    assert bspatch(old, header + offtout(7) + b"".join(parts)) == b"acXYZef"


def test_ssp_reproduces_the_built_track(tmp_path: Path) -> None:
    source, built = images(tmp_path)
    changes = changed_files(source, built)
    assert [(c.name, c.lsn, c.old, c.new) for c in changes] == [
        ("A.BIN", 20, b"hello", b"HELLO")
    ]
    ssp = build_ssp(changes, entries(source), META)
    assert ssp == build_ssp(changes, entries(source), META)
    target = tmp_path / "applied.bin"
    assert apply_ssp(ssp, source, target) == ["A.BIN"]
    assert target.read_bytes() == built.read_bytes()


def test_ssp_entries_match_the_official_layout(tmp_path: Path) -> None:
    source, built = images(tmp_path)
    ssp = build_ssp(changed_files(source, built), entries(source), META)
    archive = zipfile.ZipFile(io.BytesIO(ssp))
    assert archive.namelist() == [
        "A.BIN._DFR",
        "version.txt",
        "readme.txt",
        "driveOrder.txt",
        "changes.md5",
        "meta.txt",
    ]
    assert archive.read("version.txt") == f"{SSP_VERSION}\r\n".encode()
    assert archive.read("changes.md5") == b"A.BIN:5D41402ABC4B2A76B9719D911017C592\r\n"
    assert (
        archive.read("driveOrder.txt") == b"SUB,0,0\r\nA.BIN,1,0\r\nSUB\\B.DAT,2,0\r\n"
    )
    assert b"Version:0.0.1\r\n" in archive.read("meta.txt")
    md5, patches = read_ssp(ssp)
    assert md5 == {"A.BIN": "5D41402ABC4B2A76B9719D911017C592"}
    assert set(patches) == {"A.BIN"}


def test_drive_order_sorts_by_extent(tmp_path: Path) -> None:
    source, _ = images(tmp_path)
    lines = drive_order(entries(source)).splitlines()
    assert lines[0] == "SUB,0,0"


def test_apply_refuses_a_different_source(tmp_path: Path) -> None:
    source, built = images(tmp_path)
    ssp = build_ssp(changed_files(source, built), entries(source), META)
    with pytest.raises(ValueError, match="MD5"):
        apply_ssp(ssp, built, tmp_path / "again.bin")


def test_changes_outside_files_are_refused(tmp_path: Path) -> None:
    source, _ = images(tmp_path)
    raw = bytearray(source.read_bytes())
    raw[17 * RAW_SECTOR + 100] ^= 1
    built = tmp_path / "system.bin"
    built.write_bytes(bytes(raw))
    with pytest.raises(ValueError, match="outside any file"):
        changed_files(source, built)


def test_subdirectory_files_are_refused(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(valid_image())
    built = tmp_path / "built.bin"
    replace_file(source, built, 21, 2050, b"Q" * 2050)
    with pytest.raises(ValueError, match="root files"):
        changed_files(source, built)
