from __future__ import annotations

import pytest

from tests.unit.test_font_pack import header, letter
from tools.disc.pac_lzss import build_pac, decode_file, encode
from tools.text.caption_compiler import (
    BLANK,
    PLACEHOLDER,
    RECORD,
    SCHEMA,
    TABLE,
    Caption,
    SpecError,
    capacity,
    compile_files,
    distinct_pairs,
    line_cells,
    parse_spec,
    record_cells,
    verify_font,
    verify_table,
)
from tools.text.font import CELL_BYTES
from tools.text.font_pack import CODES, Glyph, pack
from tools.text.quote_render import record_codes

CANDIDATES = list(range(0x0A3F, 0x09FF, -1))


def font_image() -> bytes:
    glyphs = [Glyph("empty", bytes(CELL_BYTES))] * CODES
    glyphs = list(glyphs)
    for i in range(26):
        glyphs[0x08E8 + i] = Glyph("compressed", letter(i))
        glyphs[0x0902 + i] = Glyph("compressed", letter(50 + i))
    for i in range(10):
        glyphs[0x091C + i] = Glyph("compressed", letter(90 + i))
    for code in CANDIDATES:
        glyphs[code] = Glyph("compressed", letter(code))
    return pack(header(0x0C60), glyphs)


def pac_file() -> bytes:
    decoded = bytearray(TABLE + 16 * RECORD + 64)
    for record in range(16):
        for cell in range(38):
            offset = TABLE + record * RECORD + 2 * cell
            decoded[offset : offset + 2] = (0x0801 + (record + cell) % 40).to_bytes(
                2, "big"
            )
    decoded[TABLE : TABLE + 2] = PLACEHOLDER.to_bytes(2, "big")  # record 0, cell 0
    stream = encode(bytes(decoded))
    return build_pac(stream, len(decoded), 0x18 + len(stream) + 2048)


def spec(*records: tuple[int, str, str]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "records": [{"record": r, "lines": [a, b]} for r, a, b in records],
    }


def test_line_cells() -> None:
    assert line_cells("Ryu 07") == ["Ry", "u ", "07"]
    assert line_cells("{P} Hi") == [None, " H", "i "]
    with pytest.raises(SpecError):
        line_cells("x" * 39)
    with pytest.raises(ValueError):
        line_cells("what?")


def test_parse_spec_rejects_bad_input() -> None:
    assert parse_spec(spec((3, "a", "b"), (1, "c", "d")))[0].record == 1
    with pytest.raises(SpecError):
        parse_spec({"schema": "other", "records": []})
    with pytest.raises(SpecError):
        parse_spec(spec((1, "a", "b"), (1, "c", "d")))
    with pytest.raises(SpecError):
        parse_spec(spec((16, "a", "b")))


def test_placeholder_only_where_original_has_one() -> None:
    original = [PLACEHOLDER] + [0x0801] * 37
    cells = record_cells(Caption(0, ("{P}Ab", "Cd")), original)
    assert cells[0] is None and len(cells) == 38 and cells[19] == "Cd"
    with pytest.raises(SpecError):
        record_cells(Caption(0, ("Ab{P}", "Cd")), original)


def test_distinct_pairs_in_first_appearance_order() -> None:
    assert distinct_pairs([["Ab", "  ", None, "Cd"], ["Ab", "Ef"]]) == [
        "Ab",
        "Cd",
        "Ef",
    ]


def test_compile_files_end_to_end() -> None:
    image, pac = font_image(), pac_file()
    captions = parse_spec(
        spec(
            (0, "{P} Ryu record 00", "00 Line two fills cells up to nineteen"),
            (5, "Ryu record 05", "Short"),
        )
    )
    compiled = compile_files(captions, image, pac, CANDIDATES)

    assert len(compiled.font_image) == len(image)
    assert len(compiled.pac) == len(pac)
    assert verify_font(image, compiled.font_image, compiled)["pairs_equal_composed"]
    assert verify_table(pac, compiled.pac, compiled.writes)["target_cells_expected"]
    sacrificed = compiled.font_info["sacrificed"]
    assert isinstance(sacrificed, list) and sacrificed  # the image had no slack

    decoded = decode_file(compiled.pac)[1]
    record0 = record_codes(decoded, 0)
    assert record0[0] == PLACEHOLDER
    assert record0[1] == compiled.codes[" R"]
    assert record0[19] == compiled.codes["00"]
    assert record0[37] == compiled.codes["en"]
    record5 = record_codes(decoded, 5)
    assert record5[7:19] == [BLANK] * 12
    assert record_codes(decoded, 1) == record_codes(decode_file(pac)[1], 1)


def test_capacity_reports_without_building() -> None:
    report = capacity(
        parse_spec(spec((2, "Ab Cd", "Ab"))), font_image(), pac_file(), CANDIDATES
    )
    assert report["distinct_pairs"] == 3  # "Ab", " C", "d "
    assert report["fits"] is True


def test_too_many_pairs_is_rejected() -> None:
    captions = parse_spec(spec((1, "Ab", "Cd")))
    with pytest.raises(SpecError):
        compile_files(
            captions, font_image(), pac_file(), CANDIDATES, ranges=[(0xA8, 0xA8)]
        )
