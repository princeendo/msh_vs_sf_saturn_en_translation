from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from tools.text.pattern_search import Token, main, parse_pattern, search


def words(*values: int) -> bytes:
    return struct.pack(f">{len(values)}H", *values)


def test_parse_pattern_reads_symbols_and_literals() -> None:
    assert parse_pattern("A =0x20 7") == [
        Token("A", None),
        Token(None, 0x20),
        Token("7", None),
    ]
    with pytest.raises(ValueError):
        parse_pattern("   ")


def test_search_enforces_equality_distinctness_and_literals() -> None:
    data = words(1, 0x83D, 0x81F, 0x83D, 0x81F, 0x20, 9, 9, 9, 9, 0x20)
    pattern = parse_pattern("A B A B =0x20")

    hits = search(data, pattern)

    assert [hit.offset for hit in hits] == [2]
    assert hits[0].mapping == {"A": 0x83D, "B": 0x81F}
    # distinct symbols may not share a value; symbols may not equal a literal
    assert search(words(9, 9, 9, 9, 0x20), pattern) == []
    assert search(words(0x20, 1, 0x20, 1, 0x20), pattern) == []


def test_search_supports_width_stride_and_rejects_bad_width() -> None:
    data = bytes([5, 0, 6, 0, 5, 0])

    assert [h.offset for h in search(data, parse_pattern("A B A"), 1, 2, 1)] == [0]
    with pytest.raises(ValueError):
        search(data, parse_pattern("A"), width=3)


def test_main_json_and_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "dump.bin"
    path.write_bytes(words(0x20, 0x803, 0x82A, 0x803, 0x20))

    assert main([str(path), "=0x20 A B A =0x20", "--base", "0x200000", "--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["hit_count"] == 1
    assert output["hits"][0]["address"] == "0x00200000"
    assert output["hits"][0]["mapping"] == {"A": "0x0803", "B": "0x082A"}

    assert main([str(path), "A B A"]) == 0
    assert "1 hit(s)" in capsys.readouterr().out
