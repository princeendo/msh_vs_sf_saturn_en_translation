from __future__ import annotations

import itertools
import json
import random
import struct
from pathlib import Path

import pytest

from tools.disc.pac_lzss import (
    HEADER_SIZE,
    PacFormatError,
    build_pac,
    decode_file,
    decompress,
    encode,
    group_starts,
)
from tools.disc.pac_patch import main, patch


def sample(size: int, seed: int = 1) -> bytes:
    rng = random.Random(seed)
    words = [b"\x08\x03", b"\x08\x2a", b"\x00\x20", b"\x09\xca", b"\x08\x51"]
    return b"".join(rng.choice(words) for _ in range(size // 2))


@pytest.mark.parametrize("size", [0, 1, 5, 64, 5000])
def test_encode_round_trips(size: int) -> None:
    data = sample(size)
    stream = encode(data)
    assert decompress(stream, len(data))[0] == data
    assert decompress(stream, len(data))[1] == len(stream)


def test_splice_at_group_boundary_round_trips() -> None:
    data = sample(6000, seed=2)
    stream = encode(data)
    stream_offset, output_offset = group_starts(stream, len(data))[40]
    spliced = stream[:stream_offset] + encode(data, output_offset)
    assert decompress(spliced, len(data))[0] == data


def test_encode_handles_incompressible_data() -> None:
    data = bytes(random.Random(3).getrandbits(8) for _ in range(300))
    assert decompress(encode(data), len(data))[0] == data


def test_group_starts_tracks_flag_groups() -> None:
    data = sample(400)
    stream = encode(data)
    starts = group_starts(stream, len(data))
    assert starts[0] == (0, 0)
    assert all(a[0] < b[0] and a[1] < b[1] for a, b in itertools.pairwise(starts))


def test_build_pac_header_alignment_and_fill() -> None:
    pac = build_pac(b"\x00abc\x00", 3, size=40)
    words = struct.unpack_from(">6I", pac)
    assert words == (0, 0x80000000 | 13, 0, 0, 5, 3)
    assert len(pac) == 40
    with pytest.raises(PacFormatError):
        build_pac(b"x" * 100, 3, size=40)


def make_source(data: bytes) -> bytes:
    return build_pac(encode(data), len(data))


def test_patch_splices_and_verifies(tmp_path: Path) -> None:
    data = sample(4000, seed=4)
    source = make_source(data) + b"\x00" * 64  # room to grow
    new, info = patch(source, [(3000, 0x0801), (3002, 0x0803)])

    _, decoded, _ = decode_file(new)
    expected = bytearray(data)
    expected[3000:3004] = b"\x08\x01\x08\x03"
    assert decoded == bytes(expected)
    assert len(new) == len(source)
    prefix = int(str(info["unchanged_stream_prefix_bytes"]))
    assert (
        new[HEADER_SIZE : HEADER_SIZE + prefix]
        == source[HEADER_SIZE : HEADER_SIZE + prefix]
    )
    assert info["changes"][0]["modified"] == "0801"  # type: ignore[index]


def test_patch_rejects_bad_offsets() -> None:
    source = make_source(sample(100))
    with pytest.raises(PacFormatError):
        patch(source, [(3, 0x0801)])
    with pytest.raises(PacFormatError):
        patch(source, [(500, 0x0801)])


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "MC99.PAC"
    src.write_bytes(make_source(sample(2000)) + bytes(64))
    out = tmp_path / "out" / "MC99.PAC"
    manifest = tmp_path / "m.json"

    assert (
        main(
            [
                str(src),
                "--write",
                "0x10=0x0805",
                "--out",
                str(out),
                "--manifest",
                str(manifest),
            ]
        )
        == 0
    )
    assert json.loads(manifest.read_text())["changes"][0]["decoded_offset"] == "0x0010"
    assert decode_file(out.read_bytes())[1][0x10:0x12] == b"\x08\x05"
    with pytest.raises(SystemExit):
        main(
            [
                str(src),
                "--write",
                "0x10=1",
                "--out",
                str(src),
                "--manifest",
                str(manifest),
            ]
        )
