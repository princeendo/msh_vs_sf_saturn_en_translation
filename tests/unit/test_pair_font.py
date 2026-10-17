from __future__ import annotations

import pytest

from tests.unit.test_font_pack import header, letter
from tools.text.font import CELL_BYTES
from tools.text.font_pack import CODES, Glyph, pack, unpack
from tools.text.pair_font import build, char_code, split_pairs


def base_image(extra: int = 0) -> bytes:
    glyphs = [Glyph("empty", bytes(CELL_BYTES))] * CODES
    glyphs = list(glyphs)
    for i in range(26):
        glyphs[0x08E8 + i] = Glyph("compressed", letter(i))
        glyphs[0x0902 + i] = Glyph("compressed", letter(100 + i))
    for code in range(0x0A00, 0x0A10):
        glyphs[code] = Glyph("compressed", letter(code))
    image = pack(header(0x0C60), glyphs)
    return image + bytes(extra)


def test_char_code_and_split() -> None:
    assert char_code("A") == 0x08E8
    assert char_code("z") == 0x091B
    assert char_code("0") == 0x091C
    assert char_code(" ") is None
    with pytest.raises(ValueError):
        char_code("~")
    assert split_pairs("The") == ["Th", "e "]


def test_build_adds_pairs_and_sacrifices_only_as_needed() -> None:
    image = base_image()
    candidates = list(range(0x0A0F, 0x09FF, -1))
    new, info = build(image, ["Th", "e "], 0x00A8, candidates)

    assert len(new) == len(image)
    _, glyphs = unpack(new)
    assert glyphs[0x00A8].kind == "compressed"
    assert glyphs[0x00A9].kind == "compressed"
    listed = info["sacrificed"]
    assert isinstance(listed, list)
    sacrificed = [int(c, 16) for c in listed]
    assert sacrificed and all(glyphs[c].kind == "empty" for c in sacrificed)
    assert sacrificed == candidates[: len(sacrificed)]
    untouched = [c for c in candidates if c not in sacrificed]
    _, original = unpack(image)
    assert all(glyphs[c] == original[c] for c in untouched)


def test_build_with_slack_sacrifices_nothing() -> None:
    image = base_image(extra=4096)
    _, info = build(image, ["Th"], 0x00A8, [0x0A00])
    assert info["sacrificed"] == []


def test_build_rejects_occupied_code() -> None:
    with pytest.raises(ValueError):
        build(base_image(), ["Th"], 0x0A00, [])
