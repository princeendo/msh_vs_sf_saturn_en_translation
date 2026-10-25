from __future__ import annotations

from tools.text.ending_census import half_cells
from tools.text.official_endings import box_line, localize, name_text


def test_name_text_ends_on_a_cell_edge() -> None:
    assert name_text("RYU") == " RYU"
    assert name_text("CHUN-LI") == " CHUN-LI"
    assert name_text("KENS") == "KENS"


def test_localize_uses_the_saturn_boss_name() -> None:
    assert localize("behind the Cyber Akuma!!") == "behind the Mech-Gouki!!"
    assert localize("Akuma! You know who I am!") == "Gouki! You know who I am!"
    assert localize("Hulk smash!") == "Hulk smash!"


def test_box_line_centres_with_a_name_guess() -> None:
    line = box_line("{0000},")
    assert line.endswith("{P},")
    assert line.startswith("  " * 8)  # (19 - (2 + 1)) // 2 blank cells


def test_half_cells_counts_the_inserted_name() -> None:
    assert half_cells("We shall meet again", 8) == 10
    assert half_cells("{0000}.", 8) == 9
