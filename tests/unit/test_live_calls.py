from __future__ import annotations

from tools.audio.live_calls import call_of


def test_call_of_flags_name_calls() -> None:
    assert call_of(["pl0e_1#1(0x04F)", "sel_1#4(0x04F)"]) == "Bison"
    assert call_of(["pl0f_1#23(0x338)"]) == "Akuma"
    assert call_of(["pl0e_1#5(0x133)"]) is None
    assert call_of([]) is None
