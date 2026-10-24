from __future__ import annotations

from tools.reference.slot_census import RECORDS, census_file, classify

RECORD = 76


def record(fill: int) -> bytes:
    # a quote-shaped record: text codes, then blank cells
    words = [0x0801 + fill] * 6 + [0x0020] * 32
    return b"".join(w.to_bytes(2, "big") for w in words)


def block(base: int) -> bytes:
    return b"".join(record(base + r) for r in range(RECORDS))


CODES = set(range(0x0801, 0x0900))


def test_census_links_a_whole_block_as_ordinary() -> None:
    slot_a, slot_b = block(0), block(40)
    data = b"\xff" * 10 + slot_b

    result = census_file(data, CODES, [slot_a, slot_b])

    assert result["whole_slot_blocks"] == {"1": "0x000A"}
    assert result["class"] == "ordinary"


def test_extra_table_makes_a_file_irregular() -> None:
    slot_a = block(0)
    data = slot_a + b"\xff" * 4 + block(80)[: 5 * RECORD]

    result = census_file(data, CODES, [slot_a])

    assert result["class"] == "irregular"


def test_classify_partial_and_unmatched() -> None:
    table = [{"offset": "0x0000", "records": 16, "slots": {"3": 5}}]
    assert classify(table, {}) == "partial"
    assert (
        classify([{"offset": "0x0000", "records": 16, "slots": {}}], {}) == "unmatched"
    )
