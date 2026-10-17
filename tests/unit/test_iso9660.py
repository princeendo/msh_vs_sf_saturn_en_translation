from __future__ import annotations

import io
import json
import struct
from pathlib import Path

import pytest

from tools.disc.iso9660 import (
    RAW_SECTOR,
    SYNC,
    DiscFormatError,
    Track,
    check_track,
    header_fad,
    main,
    primary_volume,
    walk,
)


def to_bcd(value: int) -> int:
    return ((value // 10) << 4) | (value % 10)


def raw_sector(lsn: int, user: bytes, mode: int = 1) -> bytes:
    fad = lsn + 150
    minute, rest = divmod(fad, 75 * 60)
    second, frame = divmod(rest, 75)
    header = bytes([to_bcd(minute), to_bcd(second), to_bcd(frame), mode])
    body = user.ljust(2048, b"\x00")
    return SYNC + header + body + bytes(RAW_SECTOR - 16 - 2048)


def dir_record(name: bytes, lsn: int, size: int, flags: int) -> bytes:
    length = 33 + len(name) + (1 if len(name) % 2 == 0 else 0)
    record = bytearray(length)
    record[0] = length
    struct.pack_into("<I", record, 2, lsn)
    struct.pack_into(">I", record, 6, lsn)
    struct.pack_into("<I", record, 10, size)
    struct.pack_into(">I", record, 14, size)
    record[25] = flags
    record[32] = len(name)
    record[33 : 33 + len(name)] = name
    return bytes(record)


def make_image() -> bytes:
    sectors = [b""] * 24
    pvd = bytearray(2048)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[8:40] = b"SEGA SATURN".ljust(32)
    pvd[40:72] = b"TEST_VOLUME".ljust(32)
    struct.pack_into("<I", pvd, 80, 24)
    struct.pack_into("<H", pvd, 128, 2048)
    pvd[156 : 156 + 34] = dir_record(b"\x00", 18, 2048, 2)
    sectors[16] = bytes(pvd)
    sectors[18] = (
        dir_record(b"\x00", 18, 2048, 2)
        + dir_record(b"\x01", 18, 2048, 2)
        + dir_record(b"A.BIN;1", 20, 5, 0)
        + dir_record(b"SUB", 19, 2048, 2)
    )
    sectors[19] = (
        dir_record(b"\x00", 19, 2048, 2)
        + dir_record(b"\x01", 18, 2048, 2)
        + dir_record(b"B.DAT;1", 21, 2050, 0)
    )
    sectors[20] = b"hello"
    sectors[21] = b"X" * 2048
    sectors[22] = b"YZ"
    return b"".join(raw_sector(lsn, data) for lsn, data in enumerate(sectors))


def test_header_fad_decodes_bcd() -> None:
    assert header_fad(raw_sector(0, b"")) == 150
    assert header_fad(raw_sector(4500, b"")) == 4650


def test_check_track_counts_problems() -> None:
    image = bytearray(make_image())
    image[RAW_SECTOR * 3 + 15] = 2  # mode 2 sector
    image[RAW_SECTOR * 5 : RAW_SECTOR * 5 + 12] = bytes(12)  # broken sync

    check = check_track(io.BytesIO(bytes(image)), len(image))

    assert check.sectors == 24
    assert (check.bad_sync, check.non_mode1, check.address_mismatch) == (1, 1, 0)
    assert (check.first_fad, check.last_fad) == (150, 173)
    with pytest.raises(DiscFormatError):
        check_track(io.BytesIO(b"x"), 1)


def test_volume_and_walk_list_files() -> None:
    image = make_image()
    track = Track(io.BytesIO(image), len(image))

    volume = primary_volume(track)
    entries = list(walk(track, 18, 2048))

    assert volume["volume_id"] == "TEST_VOLUME"
    assert volume["logical_block_size"] == 2048
    assert [(e.path, e.lsn, e.size_bytes, e.is_dir) for e in entries] == [
        ("A.BIN;1", 20, 5, False),
        ("SUB", 19, 2048, True),
        ("SUB/B.DAT;1", 21, 2050, False),
    ]
    assert track.read(21, 2050) == b"X" * 2048 + b"YZ"
    with pytest.raises(DiscFormatError):
        track.user(99)


def test_main_reports_and_extracts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    track_path = tmp_path / "track.bin"
    track_path.write_bytes(make_image())
    out = tmp_path / "extracted"
    stream = tmp_path / "user.bin"

    assert (
        main(
            [
                str(track_path),
                "--check",
                "--extract",
                str(out),
                "--user-stream",
                str(stream),
            ]
        )
        == 0
    )

    report = json.loads(capsys.readouterr().out)
    assert report["check"]["bad_sync"] == 0
    assert [f["path"] for f in report["files"]] == ["A.BIN;1", "SUB", "SUB/B.DAT;1"]
    assert (out / "A.BIN").read_bytes() == b"hello"
    assert (out / "SUB" / "B.DAT").read_bytes() == b"X" * 2048 + b"YZ"
    assert stream.stat().st_size == 24 * 2048
    assert track_path.read_bytes() == make_image()
