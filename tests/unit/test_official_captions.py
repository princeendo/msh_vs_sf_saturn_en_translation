from __future__ import annotations

import pytest

from tools.text.official_captions import centred, roster_spec, spec_records
from tools.text.pair_font import char_code


def test_centred_pads_in_whole_cells() -> None:
    assert centred("Ab", cells=5) == "    Ab"
    assert centred("Abc", cells=5) == "  Abc"
    assert centred("Abcdefghij", cells=5) == "Abcdefghij"


def test_centred_rejects_overflow_and_unknown_characters() -> None:
    with pytest.raises(ValueError, match="cells"):
        centred("Abcdefghijk", cells=5)
    with pytest.raises(ValueError):
        centred("a~b")


def test_period_and_comma_have_glyphs() -> None:
    assert char_code(".") == 0x08AB
    assert char_code(",") == 0x08AC


def test_spec_records_follow_remap() -> None:
    entries = [[" One  ", "uno"], ["Two", " dos "]]

    records = spec_records(entries, remap=(0, 1, 0))

    assert [r["record"] for r in records] == [0, 1, 2]
    assert records[2]["lines"] == records[0]["lines"]
    lines = records[1]["lines"]
    assert isinstance(lines, list)
    assert [line.strip() for line in lines] == ["Two", "dos"]


def test_roster_spec_emits_one_table_per_character() -> None:
    slots = [[["Slot zero", "line"]] * 8, [["Slot one", "line"]] * 8]
    roster = [{"slot": 1, "file": "MC01.PAC", "table": "0xAC50"}]

    spec = roster_spec(slots, roster)

    assert spec["schema"] == "mshvsf-captions/2"
    tables = spec["tables"]
    assert isinstance(tables, list)
    assert tables[0]["file"] == "MC01.PAC"
    assert tables[0]["table"] == "0xAC50"
    assert len(tables[0]["records"]) == 16
    assert tables[0]["records"][0]["lines"][0].strip() == "Slot one"


def test_new_punctuation_has_glyphs() -> None:
    assert char_code("?") == 0x08DC
    assert char_code("'") == 0x08B9
    assert char_code('"') == 0x08BB
    assert char_code("-") == 0x08CB
    assert char_code("\u203c") == 0x08DF
