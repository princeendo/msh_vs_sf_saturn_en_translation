from __future__ import annotations

import random
import struct

from tools.disc.st2_encode import lz_encode, map_encode, script_encode
from tools.disc.st2_stream import lz_decode, map_decode, script_decode


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


def test_map_encode_round_trips_runs_and_far_copies() -> None:
    rng = random.Random(3)
    words = [0xFFFF] * 0x2000
    for k in range(0, 0x2000, 97):
        words[k] = rng.randrange(0x10000)
    words[0x1800:0x1900] = words[0x100:0x200]  # a copy from far back
    encoded = map_encode(words)
    assert map_decode(encoded, 0) == (words, len(encoded))
    assert len(encoded) < 1000


def _shared(a: bytes, b: bytes) -> int:
    """Bytes of ``b`` also found, in order, as runs of 32+ bytes of ``a``."""
    import difflib

    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(m.size for m in matcher.get_matching_blocks() if m.size >= 32)


def test_lz_splice_keeps_the_original_when_nothing_changes() -> None:
    from tools.disc.st2_encode import lz_splice

    for data in samples()[2:]:
        original = lz_encode(data)
        assert lz_splice(original, data) == original


def test_lz_splice_reencodes_only_the_change() -> None:
    from tools.disc.st2_encode import lz_splice

    data = samples()[5] + samples()[3]
    original = lz_encode(data)
    new = bytearray(data)
    new[2000:2040] = bytes(range(100, 140))
    spliced = lz_splice(original, bytes(new))
    assert lz_decode(spliced)[0] == bytes(new)
    assert _shared(original[8:], spliced[8:]) > 0.8 * (len(original) - 8)


def test_script_splice_follows_a_length_change() -> None:
    from tools.disc.st2_encode import script_splice

    old = samples()[5] + samples()[3] + samples()[2]
    original = script_encode(old)
    assert script_splice(original, old, [(0, len(old), 0)]) == original
    cut, gone, insert = 3000, 40, bytes(range(7, 30))
    new = old[:cut] + insert + old[cut + gone :]
    runs = [(0, cut, 0), (cut + gone, len(old), cut + len(insert))]
    spliced = script_splice(original, new, runs)
    out, end = script_decode(spliced + b"\xee" * 4)
    assert out == new and end == len(spliced)
    assert _shared(original, spliced) > 0.8 * len(original)


def test_lz_splice_absorbs_a_larger_change_in_place() -> None:
    from tools.disc.st2_encode import lz_splice

    rng = random.Random(3)
    # Repetitive data, encoded greedily (literal-heavy) so re-encoding saves room.
    data = b"".join(
        bytes([rng.randrange(3)]) * rng.randrange(1, 6) for _ in range(4000)
    )
    original = bytearray(struct.pack(">II", 0, len(data)))
    for start in range(0, len(data), 8):
        original.append(0)
        original += data[start : start + 8]
    struct.pack_into(">I", original, 0, len(original) - 8)
    new = bytearray(data)
    new[5000:5060] = bytes(rng.randrange(256) for _ in range(60))  # noise
    spliced = lz_splice(bytes(original), bytes(new), len(original) - 8)
    assert lz_decode(spliced)[0] == bytes(new)
    assert len(spliced) == len(original)
    assert spliced[-200:] == bytes(original[-200:])  # the tail is not shifted
