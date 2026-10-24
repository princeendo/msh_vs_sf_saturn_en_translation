from __future__ import annotations

import pytest

from tools.mednafen.write_trial import parse_write


def test_parse_write_plain_and_repeated() -> None:
    assert parse_write("vdp1vram:A780:0102") == ("vdp1vram", 0xA780, b"\x01\x02")
    space, address, data = parse_write("workramh:F9E66:00*128")
    assert (space, address, data) == ("workramh", 0xF9E66, bytes(128))


def test_parse_write_rejects_odd_hex() -> None:
    with pytest.raises(ValueError):
        parse_write("vdp1vram:0:123")
