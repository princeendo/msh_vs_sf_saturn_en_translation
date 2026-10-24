from __future__ import annotations

from tools.mednafen.ko_capture import quote_state
from tools.mednafen.verify_records import screen_matches


def test_screen_matches_accepts_exact_and_identical_records() -> None:
    records = [[1, 2], [3, 4], [1, 2]]

    assert screen_matches(records, 1, 1)
    assert screen_matches(records, 0, 2)  # record 2 repeats record 0
    assert not screen_matches(records, 1, 2)


def test_quote_state_picks_the_state_matching_the_pointer() -> None:
    states = {0x060F9E16: (0x0607FD0C, 0), 0x060F9ED6: (0x0021C7F4, 13)}

    assert quote_state(0x0021C7F4 + 76 * 13, states) == (0x060F9ED6, 0x0021C7F4, 13)
    assert quote_state(0x1234, states) == (0x060F9E16, 0x0607FD0C, 0)  # no match
