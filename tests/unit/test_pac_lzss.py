from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from tools.disc.pac_lzss import PacFormatError, decode_file, decompress, main


def match(distance: int, length: int) -> bytes:
    """Encode a match copying ``length`` bytes from ``distance`` bytes back."""
    field = 0x1000 - distance
    return ((field << 4) | (length - 3)).to_bytes(2, "big")


def test_literals_then_overlapping_match() -> None:
    # flags 0b0001_0000: three literals, then one match (bit 4), then literals
    stream = bytes([0b0001_0000]) + b"ABC" + match(3, 6) + b"Z"
    out, used = decompress(stream, 10)

    assert out == b"ABCABCABCZ"
    assert used == len(stream)


def test_match_overlapping_last_byte_repeats() -> None:
    stream = bytes([0b0100_0000]) + b"x" + match(1, 4)
    out, _ = decompress(stream, 5)

    assert out == b"xxxxx"


def test_truncated_stream_raises() -> None:
    with pytest.raises(PacFormatError):
        decompress(bytes([0x00]) + b"ab", 5)
    with pytest.raises(PacFormatError):
        decompress(bytes([0x80, 0xF0]), 3)


def make_pac(payload: bytes, length: int) -> bytes:
    header = struct.pack(
        ">6I", 0, 0x80000000 | (len(payload) + 8), 0, 0, len(payload), length
    )
    return header + payload + b"\x00\x00\x00"


def test_decode_file_and_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = bytes([0b0001_0000]) + b"ABC" + match(3, 6) + b"Z"
    data = make_pac(payload, 10)
    header, out, used = decode_file(data)
    assert (header.compressed_length, header.decompressed_length) == (len(payload), 10)
    assert out == b"ABCABCABCZ"
    assert used == len(payload)

    path = tmp_path / "MC99.PAC"
    path.write_bytes(data)
    assert main([str(path), "--out-dir", str(tmp_path / "out")]) == 0
    record = json.loads(capsys.readouterr().out)[0]
    assert record["stream_fully_consumed"] is True
    assert record["trailing_bytes"] == 3
    assert (tmp_path / "out" / "MC99.PAC.bin").read_bytes() == b"ABCABCABCZ"


def test_cli_reports_bad_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "bad.PAC"
    path.write_bytes(b"short")
    assert main([str(path)]) == 1
    assert "error" in json.loads(capsys.readouterr().out)[0]
