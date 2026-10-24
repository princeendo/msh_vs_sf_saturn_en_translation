from __future__ import annotations

from tools.mednafen.verify_records import screen_matches


def test_screen_matches_accepts_exact_and_identical_records() -> None:
    records = [[1, 2], [3, 4], [1, 2]]

    assert screen_matches(records, 1, 1)
    assert screen_matches(records, 0, 2)  # record 2 repeats record 0
    assert not screen_matches(records, 1, 2)
