from __future__ import annotations

from tools.text.ending_census import half_cells
from tools.text.official_endings import (
    NAME_VARIANTS,
    box_line,
    localize,
    name_text,
    voice_patches,
)


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


def test_ui_glyph_copies_target_only_japanese_art() -> None:
    from tools.text.official_endings import UI_GLYPH_COPIES

    targets = set(UI_GLYPH_COPIES)
    assert {0x45B, 0x45C, 0x45F, 0x424, 0x43D} <= targets
    sources = {s for s in UI_GLYPH_COPIES.values() if s is not None}
    assert not targets & sources
    assert UI_GLYPH_COPIES[0x429] == 0x6A8 and UI_GLYPH_COPIES[0x42A] == 0x6A9


def test_us_variant_keeps_the_arcade_names() -> None:
    assert localize("behind the Cyber Akuma!!", "us") == "behind the Cyber Akuma!!"
    assert localize("Akuma! You know who I am!", "us") == "Akuma! You know who I am!"
    assert NAME_VARIANTS["us"].names == {}


def test_voice_patches_copy_the_american_calls_with_expect() -> None:
    assert voice_patches("saturn") == []
    patches = voice_patches("us")
    assert len(patches) == 6
    assert {p["file"] for p in patches} == {"MEMFIX.PAC"}
    by_offset = {p["offset"]: (p["expect"], p["hex"]) for p in patches}
    assert by_offset["0x124AEA"] == ("0286", "004f")  # table A: Vega -> Bison
    assert by_offset["0x124C44"] == ("0048", "0338")  # table B: Gouki -> Akuma
    assert by_offset["0x124B1C"] == ("0082", "005b")  # table A: Mech-Gouki
