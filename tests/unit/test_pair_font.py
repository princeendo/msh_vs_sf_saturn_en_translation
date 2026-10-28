from __future__ import annotations

import json
import re
import string
from pathlib import Path

import pytest

from tests.unit.test_font_pack import header, letter
from tools.text.font import CELL_BYTES
from tools.text.font_pack import CODES, Glyph, pack, unpack
from tools.text.pair_font import (
    PUNCTUATION,
    build,
    char_code,
    narrow_code,
    narrow_pair,
    split_pairs,
)


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
    new, info = build(image, ["Th", "e "], [0x00A8, 0x00A9], candidates)

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
    _, info = build(image, ["Th"], [0x00A8], [0x0A00])
    assert info["sacrificed"] == []


def test_build_rejects_occupied_code() -> None:
    with pytest.raises(ValueError):
        build(base_image(), ["Th"], [0x0A00], [])
    with pytest.raises(ValueError):
        build(base_image(), ["Th", "is"], [0x00A8, 0x00A8], [])


def schema_patterns(node: object) -> set[str]:
    if isinstance(node, dict):
        found = {node["pattern"]} if isinstance(node.get("pattern"), str) else set()
        return found.union(*(schema_patterns(v) for v in node.values()))
    if isinstance(node, list):
        return set().union(*(schema_patterns(v) for v in node))
    return set()


def test_schema_accepts_exactly_the_mapped_characters() -> None:
    schema = json.loads(Path("data/captions/caption_spec.schema.json").read_text())
    (line_pattern,) = {
        p for p in schema_patterns(schema) if "\\{P\\}" in p
    }  # v1 and v2
    pattern = re.compile(line_pattern)
    mapped = string.ascii_letters + string.digits + " " + "".join(PUNCTUATION)
    for char in mapped:
        assert pattern.fullmatch(char), char
    for char in map(chr, range(0x20, 0x7F)):
        if char not in mapped:
            assert not pattern.fullmatch(char), char
    assert pattern.fullmatch("{P}Ab")
    assert pattern.fullmatch("{01E6}+P")


def test_punctuation_codes_are_distinct_full_width_glyphs() -> None:
    codes = list(PUNCTUATION.values())
    assert len(set(codes)) == len(codes)
    assert all(0x08A0 <= code < 0x08E8 for code in codes)  # below "A"


def test_narrow_pair_keeps_each_glyphs_left_eight_columns() -> None:
    assert (narrow_code("A"), narrow_code("a"), narrow_code("0")) == (
        0x140,
        0x161,
        0x130,
    )
    cells = [bytes(CELL_BYTES)] * 0x200
    cells = list(cells)
    cells[narrow_code("A")] = bytes(range(128))
    cells[narrow_code("b")] = bytes(range(128, 256))
    pair = narrow_pair(cells, "Ab")
    for row in range(16):
        assert pair[row * 8 : row * 8 + 4] == bytes(range(row * 8, row * 8 + 4))
        assert pair[row * 8 + 4 : row * 8 + 8] == bytes(
            range(128 + row * 8, 132 + row * 8)
        )
    assert narrow_pair(cells, " b")[:4] == bytes(4)
    with pytest.raises(ValueError):
        narrow_code("~")
