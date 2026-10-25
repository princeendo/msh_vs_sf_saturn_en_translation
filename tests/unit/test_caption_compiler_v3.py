from __future__ import annotations

import pytest

from tests.unit.test_caption_compiler import CANDIDATES, font_image, pac_file
from tools.disc.pac_lzss import decode_file
from tools.text.caption_compiler import (
    BLANK,
    PLACEHOLDER,
    RECORD,
    SCHEMA_V3,
    TABLE,
    SpecError,
    apply_patches,
    compile_tables,
    parse_document,
    parse_patches,
    verify_font,
    verify_raw,
)
from tools.text.quote_render import record_codes

RAW_TABLE, FIELD = 0x40, 0x400


def raw_file() -> bytes:
    data = bytearray(0x600)
    for cell in range(3 * 38):
        offset = RAW_TABLE + 2 * cell
        data[offset : offset + 2] = (0x0801 + cell % 40).to_bytes(2, "big")
    return bytes(data)


def spec_v3() -> dict[str, object]:
    return {
        "schema": SCHEMA_V3,
        "tables": [
            {  # two tables in one PAC; {P} where the original has no placeholder
                "file": "MC13.PAC",
                "table": f"0x{TABLE:X}",
                "placeholder": "anywhere",
                "records": [{"record": 3, "lines": ["We shall meet again", ""]}],
            },
            {
                "file": "MC13.PAC",
                "table": f"0x{TABLE + 4 * RECORD:X}",
                "placeholder": "anywhere",
                "records": [{"record": 0, "lines": ["{P}.", ""]}],
            },
            {
                "file": "ME.PAC",
                "format": "raw",
                "table": f"0x{RAW_TABLE:X}",
                "records": [{"record": 1, "lines": ["Searching for a", "opponent."]}],
            },
        ],
        "fields": [
            {"file": "MM.BIN", "offset": f"0x{FIELD:X}", "cells": 6, "text": " RYU"}
        ],
    }


def test_parse_document_v3() -> None:
    tables, fields = parse_document(spec_v3())
    assert [t.file for t in tables] == ["MC13.PAC", "MC13.PAC", "ME.PAC"]
    assert tables[2].raw and tables[0].placeholder_anywhere
    assert fields[0].file == "MM.BIN" and fields[0].cells == 6


def test_parse_document_rejects_bad_v3() -> None:
    bad = spec_v3()
    tables = bad["tables"]
    assert isinstance(tables, list)
    tables[1]["table"] = f"0x{TABLE + 3 * RECORD:X}"  # same record as table 0
    with pytest.raises(SpecError):
        parse_document(bad)
    bad = spec_v3()
    bad["fields"] = [{"file": "MC13.PAC", "offset": "0x0", "cells": 2, "text": "A"}]
    with pytest.raises(SpecError):
        parse_document(bad)  # fields need a raw file


def test_compile_v3_raw_lzss_and_fields() -> None:
    tables, fields = parse_document(spec_v3())
    pacs = {"MC13.PAC": pac_file(), "ME.PAC": raw_file(), "MM.BIN": bytes(0x600)}
    compiled = compile_tables(tables, font_image(), pacs, CANDIDATES, fields=fields)
    assert set(compiled.files) == {"MC13.PAC", "ME.PAC", "MM.BIN"}
    assert verify_font(font_image(), compiled.font_image, compiled)[
        "pairs_equal_composed"
    ]

    mc13 = decode_file(compiled.files["MC13.PAC"].pac)[1]
    assert record_codes(mc13, 3)[0] == compiled.codes["We"]
    moved = record_codes(mc13, 4)  # table 2, record 0
    assert moved[0] == PLACEHOLDER and moved[1] == compiled.codes[". "]
    assert moved[2:] == [BLANK] * 36

    me = compiled.files["ME.PAC"]
    assert record_codes(me.pac, 1, RAW_TABLE)[19] == compiled.codes["op"]
    assert verify_raw(pacs["ME.PAC"], me.pac, me.writes)["changes_only_in_target_cells"]

    name = compiled.files["MM.BIN"].pac
    codes = [
        int.from_bytes(name[FIELD + 2 * i : FIELD + 2 * i + 2], "big") for i in range(6)
    ]
    assert codes[:2] == [compiled.codes[" R"], compiled.codes["YU"]]
    assert codes[2:] == [BLANK] * 4


def test_patches_parse_and_apply() -> None:
    document = spec_v3() | {
        "patches": [{"file": "MM.BIN", "offset": "0x10", "hex": "02"}]
    }
    patches = parse_patches(document)
    assert patches[0].file == "MM.BIN" and patches[0].data == b"\x02"
    out, checks = apply_patches(bytes(0x20), patches)
    assert out[0x10] == 2 and checks["changed_bytes"] == 1
    assert parse_patches({"schema": "mshvsf-captions/2"}) == []
    with pytest.raises(SpecError):
        apply_patches(bytes(4), parse_patches(document))  # outside the file
