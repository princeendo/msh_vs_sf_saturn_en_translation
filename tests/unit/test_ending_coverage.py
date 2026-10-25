from __future__ import annotations

from tools.text.ending_coverage import dialogue_records, outside_unchanged


def test_dialogue_records_are_partner_then_point_pairs() -> None:
    assert dialogue_records(9) == [34, 35, 86, 87]  # Ryu (EXP-0043)
    assert dialogue_records(19) == [54, 55, 106, 107]


def test_outside_unchanged_accepts_changes_inside_spans_only() -> None:
    source = bytes(8)
    inside = bytes([0, 0, 1, 1, 0, 0, 0, 0])
    assert outside_unchanged(source, inside, [(2, 4)]) == {
        "same_length": True,
        "outside_unchanged": True,
        "changed_bytes_inside": 2,
    }
    outside = bytes([0, 0, 0, 0, 0, 1, 0, 0])
    assert outside_unchanged(source, outside, [(2, 4)])["outside_unchanged"] is False
    assert outside_unchanged(source, bytes(9), [])["outside_unchanged"] is False
    assert outside_unchanged(source, bytes(7), [])["outside_unchanged"] is False
