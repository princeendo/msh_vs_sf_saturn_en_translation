from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from tools.reference.cps2_text import (
    build_program,
    decode_code,
    extract_runs,
    main,
    read_quote_table,
    text_digest,
)
from tools.reference.mame_audit import RomEntry, RomSet


def encode(text: str) -> bytes:
    """Encode synthetic text with the EXP-0029 character map (letters only)."""
    codes = []
    for char in text:
        if char == " ":
            codes.append(0x0020)
        elif char.isupper():
            codes.append(0x0140 + ord(char) - ord("A"))
        elif char.islower():
            codes.append(0x0161 + ord(char) - ord("a"))
        else:
            codes.append({".": 0x0184, ",": 0x0185, "!": 0x0120}[char])
    return b"".join(code.to_bytes(2, "big") for code in codes)


def swap(data: bytes) -> bytes:
    swapped = bytearray(len(data))
    swapped[0::2] = data[1::2]
    swapped[1::2] = data[0::2]
    return bytes(swapped)


def test_decode_code_maps_observed_codes_and_marks_unknowns() -> None:
    assert decode_code(0x0020) == " "
    assert decode_code(0x0140) == "A"
    assert decode_code(0x0159) == "Z"
    assert decode_code(0x0161) == "a"
    assert decode_code(0x0120) == "!"
    assert decode_code(0x0185) == ","
    assert decode_code(0x0122) == "\u203c"
    assert decode_code(0x0160) == '"'
    assert decode_code(0x012F) == "0"
    assert decode_code(0x0132) == "3"  # "Level 3"
    assert decode_code(0x0138) == "9"
    assert decode_code(0x0186) == "'"  # opening quote, drawn as an apostrophe
    assert decode_code(0x01E6) == "{01e6}"
    assert decode_code(0x0872) is None


def test_build_program_unswaps_word_swapped_roms(tmp_path: Path) -> None:
    low, high = b"\x01\x02\x03\x04", b"\x05\x06\x07\x08"
    archive = tmp_path / "game.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("p.03", low)
        bundle.writestr("p.04", high)
        bundle.writestr("gfx", b"ignored")
    romset = RomSet(
        "game",
        [
            RomEntry("p.04", 4, "", "", "maincpu", 4, "ROM_LOAD16_WORD_SWAP"),
            RomEntry("p.03", 4, "", "", "maincpu", 0, "ROM_LOAD16_WORD_SWAP"),
            RomEntry("gfx", 7, "", "", "gfx", 0, "ROM_LOAD64_WORD"),
        ],
    )

    assert build_program(archive, romset) == bytes([2, 1, 4, 3, 6, 5, 8, 7])


def test_build_program_rejects_unknown_loader(tmp_path: Path) -> None:
    archive = tmp_path / "game.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("p.03", b"\x00\x00")
    romset = RomSet("game", [RomEntry("p.03", 2, "", "", "maincpu", 0, "ROM_LOAD")])

    with pytest.raises(ValueError, match="unsupported loader"):
        build_program(archive, romset)


def test_extract_runs_keeps_only_phrases() -> None:
    program = b"\x08\x72" + encode("Hello there friend.") + b"\x08\x72" + encode("Xy")

    runs = extract_runs(program)

    assert [(run.offset, run.text) for run in runs] == [(2, "Hello there friend.")]
    assert text_digest(runs) == text_digest(extract_runs(program))


def test_read_quote_table_splits_blocks_into_lines() -> None:
    width, lines, quotes = 4, 2, 2
    block = encode("Ab  cd! Ef  gh, ")
    assert len(block) == 2 * width * lines * quotes
    table = (0x10).to_bytes(4, "big") + (0x10).to_bytes(4, "big")
    program = table.ljust(0x10, b"\x00") + block

    slots = read_quote_table(program, 0, 2, quotes, lines, width)

    assert slots[0].address == slots[1].address == 0x10
    assert slots[0].quotes == [["Ab  ", "cd! "], ["Ef  ", "gh, "]]


def test_main_writes_runs_and_quotes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = encode("We did it.")
    rom = swap((8).to_bytes(4, "big") + b"\x00\x00\x00\x00" + text)
    archive = tmp_path / "game.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("p.03", rom)
    driver = tmp_path / "driver.cpp"
    driver.write_text(
        "ROM_START( game )\n"
        '\tROM_REGION( CODE_SIZE, "maincpu", 0 )\n'
        f'\tROM_LOAD16_WORD_SWAP( "p.03", 0x000000, {len(rom):#x}, '
        f"CRC(00000000) SHA1({'0' * 40}) )\n"
        "ROM_END\n"
    )
    runs_out, quotes_out = tmp_path / "runs.json", tmp_path / "quotes.json"

    args = [
        "--driver",
        str(driver),
        "--out",
        str(runs_out),
        "--quote-table",
        "0",
        "--slots",
        "1",
        "--quotes-out",
        str(quotes_out),
        str(archive),
    ]
    assert main(args) == 0

    report = capsys.readouterr().out
    assert "Runs: 1" in report
    assert "Distinct blocks: 1" in report
    assert json.loads(runs_out.read_text())[0]["text"] == "We did it."
    assert json.loads(quotes_out.read_text())[0]["quotes"][0][0].startswith("We did")
