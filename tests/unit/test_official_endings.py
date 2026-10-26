from __future__ import annotations

from tools.text.ending_census import half_cells
from tools.text.official_endings import (
    NAME_VARIANTS,
    box_line,
    label_patches,
    localize,
    name_text,
    pointer_patches,
    speaker_patches,
    string_patches,
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


def test_speaker_patches_set_the_us_labels_with_expect() -> None:
    assert speaker_patches("saturn") == []
    by_offset = {p["offset"]: p for p in speaker_patches("us")}
    vega = by_offset["0xB244"]  # field 14
    assert bytes.fromhex(vega["expect"]) == b"Vega".ljust(16)
    assert bytes.fromhex(vega["hex"]) == b"Bison".ljust(16)
    assert bytes.fromhex(by_offset["0xB294"]["hex"]) == b"Cyber Akuma".ljust(16)


def test_label_patches_copy_whole_records() -> None:
    assert label_patches("saturn") == []
    patches = {p["offset"]: p for p in label_patches("us")}
    assert len(patches) == 6
    assert all(len(bytes.fromhex(p["hex"])) == 16 for p in patches.values())
    akuma = bytes.fromhex(patches["0x32D94"]["hex"])  # P1 GOUKI slot
    assert akuma[:8] == bytes.fromhex("5753575457555756")  # AKUMA, 4 cells


def test_string_patches_keep_lengths_and_expect_the_saturn_text() -> None:
    assert string_patches("saturn") == []
    by_offset = {p["offset"]: p for p in string_patches("us")}
    menu = by_offset["0x24F03"]
    assert bytes.fromhex(menu["expect"]) == b" MECH-GOUKI NOW!!"
    assert bytes.fromhex(menu["hex"]) == b"CYBER-AKUMA NOW!!"
    assert bytes.fromhex(by_offset["0x6341"]["hex"]) == b"18.BISON".ljust(20)
    assert all(len(p["hex"]) == len(p["expect"]) for p in by_offset.values())


def test_pointer_patches_point_at_the_us_records() -> None:
    assert pointer_patches("saturn") == []
    by_offset = {p["offset"]: (p["expect"], p["hex"]) for p in pointer_patches("us")}
    assert by_offset == {
        "0x9FCA0": ("060b8a88", "060b8bce"),  # banner
        "0x9FCAC": ("060b8aa2", "060b8bec"),
        "0x9FCDC": ("060b8b22", "060b8c0a"),
        "0x665DE": ("0607f2d8", "0607f3b2"),  # VS screen
        "0x665EA": ("0607f2ea", "0607f3c6"),
        "0x6661A": ("0607f348", "0607f3da"),
    }


def test_unlock_boss_patch_sets_the_boot_value_with_expect() -> None:
    from tools.text.official_endings import UNLOCK_BOSS_PATCH

    assert UNLOCK_BOSS_PATCH["file"] == "MM.BIN"
    assert UNLOCK_BOSS_PATCH["offset"] == "0x50E4"
    assert UNLOCK_BOSS_PATCH["expect"] == "e000"  # mov #0,r0
    assert UNLOCK_BOSS_PATCH["hex"] == "e001"  # mov #1,r0
