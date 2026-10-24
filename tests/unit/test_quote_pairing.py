from __future__ import annotations

import hashlib

from tools.reference.quote_pairing import EN_ENTRY, JP_RECORD, pair


def synthetic_program(jp: bytes, en_entries: int) -> bytes:
    jp_table, en_table, jp_base = 0x00, 0x10, 0x40
    en_base = jp_base + len(jp)
    program = bytearray(en_base + en_entries * EN_ENTRY)
    program[jp_table + 4 : jp_table + 8] = jp_base.to_bytes(4, "big")  # slot 1
    program[en_table + 4 : en_table + 8] = en_base.to_bytes(4, "big")
    program[jp_base : jp_base + len(jp)] = jp
    for entry in range(en_entries):
        start = en_base + entry * EN_ENTRY
        program[start : start + EN_ENTRY] = bytes([entry + 1]) * EN_ENTRY
    return bytes(program)


def test_pair_maps_records_through_remap_and_checks_identity() -> None:
    saturn = bytes([1]) * JP_RECORD + bytes([2]) * JP_RECORD + bytes([3]) * JP_RECORD
    program = synthetic_program(saturn, 2)

    report = pair(saturn, program, 1, 0x00, 0x10, remap=(0, 1, 0))

    assert report["tables_identical"] is True
    rows = report["rows"]
    assert isinstance(rows, list)
    assert [row["arcade_en_entry"] for row in rows] == [0, 1, 0]
    assert (
        rows[2]["en_codes_sha256"] == hashlib.sha256(bytes([1]) * EN_ENTRY).hexdigest()
    )
    assert (
        rows[1]["jp_codes_sha256"] == hashlib.sha256(bytes([2]) * JP_RECORD).hexdigest()
    )


def test_pair_reports_a_differing_record() -> None:
    saturn = bytes([1]) * JP_RECORD + bytes([2]) * JP_RECORD
    program = bytearray(synthetic_program(saturn, 1))
    program[0x40 + JP_RECORD] = 9

    report = pair(saturn, bytes(program), 1, 0x00, 0x10, remap=(0, 0))

    assert report["tables_identical"] is False
    rows = report["rows"]
    assert isinstance(rows, list)
    assert [row["arcade_jp_identical"] for row in rows] == [True, False]
