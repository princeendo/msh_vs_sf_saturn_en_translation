from __future__ import annotations

import pytest

from tools.text.names_switch import (
    MM_BASE,
    SOUND_ENTRY7,
    Site,
    alternates,
    home,
    pack,
    sites,
    unpack,
)


def spec(lines: str, field: str, patch: str | None) -> dict[str, object]:
    patches = (
        [{"file": "MM.BIN", "offset": "0x11", "hex": patch, "expect": "4142"}]
        if patch
        else []
    )
    return {
        "tables": [
            {
                "file": "MC0F.PAC",
                "table": "0x100",
                "records": [{"record": 1, "lines": [lines, "x"]}],
            }
        ],
        "fields": [{"file": "MM.BIN", "offset": "0x40", "cells": 3, "text": field}],
        "patches": patches,
    }


def test_alternates_list_only_what_differs_and_use_expect_for_one_sided_patches() -> (
    None
):
    found = alternates(spec("Bison", " BISON", "5859"), spec("Vega", "VEGA", None))
    kinds = {e["kind"]: e for e in found}
    assert (
        kinds["record"]["lines"] == ["Vega", "x"] and kinds["field"]["text"] == "VEGA"
    )
    assert kinds["bytes"] == {
        "kind": "bytes",
        "file": "MM.BIN",
        "offset": "0x11",
        "american": "5859",
        "saturn": "4142",
    }
    assert alternates(spec("A", "B", None), spec("A", "B", None)) == []
    tagged = spec("A", "B", "5859")
    tagged["patches"][0]["why"] = "OPT-004/OPT-005 MM.BIN 0x11: sub-menu"  # type: ignore[index]
    assert alternates(tagged, spec("A", "B", None)) == []


def test_sites_widen_to_even_and_four_bytes_and_overlay_the_saturn_bytes() -> None:
    mm = bytes(range(64))
    entry = {
        "kind": "bytes",
        "file": "MM.BIN",
        "offset": "0x11",
        "american": "1112",
        "saturn": "abcd",
    }
    (site,) = sites([entry], {"MM.BIN": mm}, {})
    assert site.address == MM_BASE + 0x10 and not site.slots
    assert site.american == mm[0x10:0x14]
    assert site.saturn == bytes([0x10, 0xAB, 0xCD, 0x13])
    with pytest.raises(ValueError, match="American"):
        sites([{**entry, "american": "0000"}], {"MM.BIN": mm}, {})


def test_homes() -> None:
    assert home("MC00.PAC", 0x42F8) == (0x42F8, True)
    assert home("MEMFIX.PAC", 0x124AEA) == (SOUND_ENTRY7 + 0xF32, False)
    with pytest.raises(ValueError):
        home("MC00.BIN", 0)


def test_pack_layout() -> None:
    table = pack(
        [
            Site(
                0x0601E000,
                False,
                b"\x00\x01\x02\x03\x04\x05",
                b"\x00\x01\x02\x09\x04\x05",
            )
        ]
    )
    assert table[:4] == bytes.fromhex("0601E000")
    assert int.from_bytes(table[4:6], "big") == 6  # length
    assert int.from_bytes(table[6:8], "big") == 0  # not in slots
    assert int.from_bytes(table[8:10], "big") == 2  # probe covers the first difference
    assert (
        table[12:18] == b"\x00\x01\x02\x03\x04\x05"
        and table[18:24] == b"\x00\x01\x02\x09\x04\x05"
    )
    assert len(table) % 4 == 0 and table[-4:] == bytes(4)


def test_unpack_reverses_pack() -> None:
    found = [
        Site(
            0x0601E000, False, b"\x00\x01\x02\x03\x04\x05", b"\x00\x01\x02\x09\x04\x05"
        ),
        Site(0x42F8, True, bytes(76), bytes(74) + b"\x00\x01"),
    ]
    assert unpack(pack(found)) == found
