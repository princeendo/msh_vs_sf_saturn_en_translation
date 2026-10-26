from __future__ import annotations

import random

from tools.disc.st2_encode import lz_encode, script_encode
from tools.disc.st2_stream import lz_decode, script_decode


def samples() -> list[bytes]:
    rng = random.Random(7)
    noise = bytes(rng.randrange(256) for _ in range(3000))
    runs = b"".join(
        bytes([rng.randrange(4)]) * rng.randrange(1, 40) for _ in range(300)
    )
    far = noise[:600] + bytes(5000) + noise[:600]  # a repeat beyond 4 KB
    return [b"", b"A", noise, runs, far, bytes(range(256)) * 20]


def test_lz_encode_round_trips() -> None:
    for data in samples():
        encoded = lz_encode(data)
        assert lz_decode(encoded)[0] == data


def test_lz_encode_compresses_repeats() -> None:
    assert len(lz_encode(bytes(4096))) < 4096 // 8


def test_script_encode_round_trips_and_ends_cleanly() -> None:
    for data in samples():
        encoded = script_encode(data)
        out, end = script_decode(encoded + b"\xee" * 4)
        assert out == data
        assert end == len(encoded)


def test_script_encode_uses_long_copies() -> None:
    data = bytes(range(200)) * 30  # 200-byte period: short copies cannot reach
    assert len(script_encode(data)) < 400
