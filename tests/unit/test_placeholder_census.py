from __future__ import annotations

from tools.text.placeholder_census import mc13_role, table_sites, text_sites


def words(*codes: int) -> bytes:
    return b"".join(c.to_bytes(2, "big") for c in codes)


def test_text_sites_need_a_text_run_and_few_zeros() -> None:
    text = words(*([0x0801, 0x0020] * 10), 0x0000, *([0x0803, 0x0020] * 10))
    assert text_sites(text) == [40]
    data = words(*([0x0000, 0x0801] * 20))  # dense zeros: data, not text
    assert text_sites(data) == []


def test_table_sites_and_mc13_roles() -> None:
    record = bytearray(words(*([0x0801] * 38)))
    record[10:12] = b"\x00\x00"
    assert table_sites(bytes(record), 0, 1) == [[0, 5]]
    assert mc13_role(36, {9, 10})["slot"] == 10
    assert mc13_role(86, {9})["english"] is True
    assert mc13_role(3, {9})["content"] == "Cyber-Akuma win quote"
