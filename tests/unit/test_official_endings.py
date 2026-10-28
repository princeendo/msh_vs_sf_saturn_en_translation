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


def test_spec_pairs_reads_tables_and_fields() -> None:
    from tools.text.official_endings import spec_pairs

    spec = {
        "tables": [{"records": [{"lines": ["  ABCD", "E"]}]}],
        "fields": [{"text": " RYU"}],
    }
    assert spec_pairs(spec) == {"AB", "CD", "E ", " R", "YU"}


def test_secret_tables_refuse_a_different_source(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import json

    import pytest

    from tools.text import official_endings as oe

    record: dict[str, object] = {
        "record": 0,
        "source_sha256": "0" * 64,
        "lines": ["Hi"],
    }
    doc = {
        "tables": [
            {"file": "ME.PAC", "format": "raw", "table": "0x0", "records": [record]}
        ]
    }
    path = tmp_path / "t.json"
    path.write_text(json.dumps(doc))

    class FakeTrack:
        def __init__(self, stream, size):  # type: ignore[no-untyped-def]
            pass

        def read(self, lsn, size):  # type: ignore[no-untyped-def]
            return bytes(76)

    track = tmp_path / "track.bin"
    track.write_bytes(b"")
    monkey = pytest.MonkeyPatch()
    monkey.setattr(oe, "Track", FakeTrack)
    monkey.setattr(oe, "find_entry", lambda t, n: (0, 76))
    try:
        with pytest.raises(ValueError, match="source differs"):
            oe.secret_tables(path, track)
        import hashlib

        record["source_sha256"] = hashlib.sha256(bytes(76)).hexdigest()
        path.write_text(json.dumps(doc))
        tables = oe.secret_tables(path, track, existing={"Hi"})
        assert tables[0]["format"] == "raw"
        records = tables[0]["records"]
        assert isinstance(records, list)
        assert records[0]["lines"][0].strip() == "Hi"
    finally:
        monkey.undo()


def test_localize_uses_vega_for_bison_only_in_the_saturn_variant() -> None:
    assert localize("Bison, Psycho Power is") == "Vega, Psycho Power is"
    assert localize("Bison, Psycho Power is", "us") == "Bison, Psycho Power is"


def test_exchange_table_pairs_boxes_and_refuses_another_block(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import pytest

    from tools.text import official_endings as oe

    count = oe.SLOTS * oe.EXCHANGE_BOXES
    program = bytearray(b"\x00\x20" * ((oe.EXCHANGES_EN + 100 * count) // 2))
    japanese = bytes(range(256)) * (76 * count // 256 + 1)
    program[oe.EXCHANGES_JA : oe.EXCHANGES_JA + 76 * count] = japanese[: 76 * count]
    # Box 4, line 2: "Ok" + code 0x011E + "No" (arcade codes: A = 0x0140, a = 0x0161).
    line2 = oe.EXCHANGES_EN + 100 * 4 + 50
    program[line2 : line2 + 10] = bytes.fromhex("014e016b011e014d016f")
    mc00 = bytearray(oe.EXCHANGES_MC00 + 76 * count)
    mc00[oe.EXCHANGES_MC00 :] = japanese[: 76 * count]

    class FakeTrack:
        def __init__(self, stream, size):  # type: ignore[no-untyped-def]
            pass

        def read(self, lsn, size):  # type: ignore[no-untyped-def]
            return b""

    track = tmp_path / "track.bin"
    track.write_bytes(b"")
    monkey = pytest.MonkeyPatch()
    monkey.setattr(oe, "Track", FakeTrack)
    monkey.setattr(oe, "find_entry", lambda t, n: (0, 0))
    monkey.setattr(oe, "decode_file", lambda data: (None, bytes(mc00)))
    try:
        table = oe.exchange_table(bytes(program), track)
        records = table["records"]
        assert isinstance(records, list)
        assert table["file"] == "MC00.PAC" and len(records) == count
        assert records[4]["lines"][1].strip() == "Ok,No"
        assert [x.strip() for x in records[5]["lines"]] == ["", ""]
        mc00[oe.EXCHANGES_MC00] ^= 1
        with pytest.raises(ValueError, match="differ"):
            oe.exchange_table(bytes(program), track)
    finally:
        monkey.undo()


def test_official_hints_read_cells_and_refuse_other_hints(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import hashlib

    import pytest

    from tools.text import official_endings as oe

    count = oe.HINT_RECORDS
    program = bytearray(b"\x00\x20" * ((oe.HINTS_EN + 100 * count) // 2))
    japanese = bytes(range(256)) * (76 * count // 256 + 1)
    program[oe.HINTS_JA : oe.HINTS_JA + 76 * count] = japanese[: 76 * count]
    # Page 3, line 1: arrow 0x01E2, "H", code 0x0129 ("+"), "K".
    line = oe.HINTS_EN + 100 * 3
    program[line : line + 8] = bytes.fromhex("01e20147012901 4a".replace(" ", ""))
    mm = bytearray(oe.HINTS_MM + 76 * count)
    mm[oe.HINTS_MM :] = japanese[: 76 * count]
    mm[oe.HINTS_MM] ^= 0xFF  # the Saturn's record 0 differs from the arcade's

    class FakeTrack:
        def __init__(self, stream, size):  # type: ignore[no-untyped-def]
            pass

        def read(self, lsn, size):  # type: ignore[no-untyped-def]
            return bytes(mm)

    track = tmp_path / "track.bin"
    track.write_bytes(b"")
    monkey = pytest.MonkeyPatch()
    monkey.setattr(oe, "Track", FakeTrack)
    monkey.setattr(oe, "find_entry", lambda t, n: (0, 0))
    record0 = hashlib.sha256(bytes(mm[oe.HINTS_MM : oe.HINTS_MM + 76])).hexdigest()
    monkey.setattr(oe, "HINT0_SHA256", record0)
    try:
        table = oe.official_hint_table(bytes(program), track)
        records = table["records"]
        assert isinstance(records, list)
        assert table["file"] == "MM.BIN" and table["format"] == "raw"
        assert len(records) == count
        assert records[3]["lines"][0].strip() == "{01E2}H+K"
        page3 = hashlib.sha256(b"{01E2}H+K\n").hexdigest()
        fixed = oe.official_hint_table(
            bytes(program), track, fixes={3: (page3, ["Fixed", "page"])}
        )
        assert [x.strip() for x in fixed["records"][3]["lines"]] == ["Fixed", "page"]
        with pytest.raises(ValueError, match="official text"):
            oe.official_hint_table(
                bytes(program), track, fixes={3: ("0" * 64, ["Fixed", "page"])}
            )
        mm[oe.HINTS_MM + 76] ^= 1
        with pytest.raises(ValueError, match="differ"):
            oe.official_hint_table(bytes(program), track)
    finally:
        monkey.undo()


def test_hint_page_patches_keep_lengths() -> None:
    from tools.text import official_endings as oe

    patches = oe.hint_page_patches()
    assert {p["offset"] for p in patches} == {"0x96848", "0x968A0", "0x9638C"}
    for p in patches:
        assert len(p["hex"]) == len(p["expect"])
    new_map = bytes.fromhex(next(p["hex"] for p in patches if p["offset"] == "0x968A0"))
    assert sorted(set(new_map)) == [0, 2, 4, 6, 8, 10, 12, 14]


def test_story_tables_build_records_16_to_43_with_lines(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import hashlib
    import json

    import pytest

    from tools.text import official_endings as oe

    mm = bytearray(0x7C584 + 76 * 48)
    for k in range(48):
        mm[0x7C584 + 76 * k] = k + 1
    digest = {
        k: hashlib.sha256(
            bytes(mm[0x7C584 + 76 * k : 0x7C584 + 76 * (k + 1)])
        ).hexdigest()
        for k in range(48)
    }
    records = [
        {"record": 16, "source_sha256": digest[16], "lines": ["Give your body", ""]},
        {"record": 27, "source_sha256": digest[27], "lines": ["Oh? {P}, see", ""]},
        {"record": 35, "source_sha256": digest[35], "note": "symbol noise; kept"},
        {"record": 42, "source_sha256": digest[42], "lines": ["Go, Shadow!", ""]},
        {"record": 45, "source_sha256": digest[45], "lines": ["Cyborg KAWASE!", ""]},
    ]
    path = tmp_path / "story.json"
    path.write_text(
        json.dumps(
            {
                "tables": [
                    {
                        "file": "MM.BIN",
                        "table": "0x7C584",
                        "format": "raw",
                        "records": records,
                    }
                ]
            }
        )
    )

    class FakeTrack:
        def __init__(self, stream, size):  # type: ignore[no-untyped-def]
            pass

        def read(self, lsn, size):  # type: ignore[no-untyped-def]
            return bytes(mm)

    track = tmp_path / "track.bin"
    track.write_bytes(b"")
    monkey = pytest.MonkeyPatch()
    monkey.setattr(oe, "Track", FakeTrack)
    monkey.setattr(oe, "find_entry", lambda t, n: (0, 0))
    try:
        (table,) = oe.story_tables(path, track)
        built = table["records"]
        assert isinstance(built, list)
        assert [r["record"] for r in built] == [16, 27, 42]
        assert table["placeholder"] == "anywhere" and table["format"] == "raw"
        assert "{P}" in built[1]["lines"][0]
    finally:
        monkey.undo()
