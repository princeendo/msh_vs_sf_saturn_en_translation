from __future__ import annotations

from tools.reference.ps1_text import BLOCK, compare, swap16


def test_swap16_reverses_each_word() -> None:
    assert swap16(b"\x01\x02\x03\x04") == b"\x02\x01\x04\x03"


def test_compare_finds_swapped_blocks_and_partial_matches() -> None:
    block_a = bytes(range(256)) * 3 + bytes(range(32))
    block_b = bytes(reversed(block_a))
    assert len(block_a) == BLOCK
    program = bytearray(16) + block_a + block_b
    program[0:4] = (16).to_bytes(4, "big")
    program[4:8] = (16 + BLOCK).to_bytes(4, "big")
    partial = swap16(block_b)[:100]  # only the first quote of slot 1
    ps1_file = b"\xff" * 10 + swap16(block_a) + partial

    rows = compare(bytes(program), ps1_file, 0, 2)

    assert rows[0]["ps1_offset"] == "0x0000a"
    assert rows[0]["quotes_found"] == 8
    assert rows[1]["ps1_offset"] is None
    assert rows[1]["quotes_found"] == 1
