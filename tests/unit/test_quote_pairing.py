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


def test_pair_reads_each_slot_through_its_own_pointers() -> None:
    one, two = bytes([1]) * JP_RECORD, bytes([2]) * JP_RECORD
    jp_table, en_table = 0x00, 0x10
    program = bytearray(0x40 + 2 * JP_RECORD + 2 * EN_ENTRY)
    for slot, (jp_base, en_base) in enumerate(
        [
            (0x40, 0x40 + 2 * JP_RECORD),
            (0x40 + JP_RECORD, 0x40 + 2 * JP_RECORD + EN_ENTRY),
        ],
        start=1,
    ):
        program[jp_table + 4 * slot : jp_table + 4 * slot + 4] = jp_base.to_bytes(
            4, "big"
        )
        program[en_table + 4 * slot : en_table + 4 * slot + 4] = en_base.to_bytes(
            4, "big"
        )
        program[jp_base : jp_base + JP_RECORD] = (one, two)[slot - 1]
        program[en_base : en_base + EN_ENTRY] = bytes([slot + 10]) * EN_ENTRY

    report = pair(two, bytes(program), 2, jp_table, en_table, remap=(0,))
    wrong = pair(two, bytes(program), 1, jp_table, en_table, remap=(0,))

    assert report["tables_identical"] is True
    assert wrong["tables_identical"] is False
    rows = report["rows"]
    assert isinstance(rows, list)
    assert (
        rows[0]["en_codes_sha256"] == hashlib.sha256(bytes([12]) * EN_ENTRY).hexdigest()
    )
