from __future__ import annotations

from tools.reference.roster_pairing import english_block, placeholders


def test_placeholders_lists_record_and_cell() -> None:
    record = bytearray(b"\x00\x20" * 38)
    record[2 * 8 : 2 * 8 + 2] = b"\x00\x00"
    other = bytes(b"\x00\x20" * 38)

    assert placeholders(bytes(record) + other) == [{"record": 0, "cell": 8}]
    assert placeholders(other * 2) == []


def test_english_block_follows_the_slot_pointer() -> None:
    program = bytearray(16 + 800)
    program[4:8] = (16).to_bytes(4, "big")  # slot 1 points at offset 16
    program[16:816] = bytes([7]) * 800

    assert english_block(bytes(program), 0, 1) == bytes([7]) * 800
