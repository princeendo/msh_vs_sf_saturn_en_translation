from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.text.font import CELL_BYTES, SIZE_TABLE, Font, decompress, main, nibble_at

IMAGE_BASE = 0x02400000
FONT_BASE = 0x02400100


def compress_column_major(cell: bytes) -> bytes:
    """Reference encoder used only to build fixtures."""
    nibbles = [0] * 32
    data = bytearray()
    index = 0
    for column in range(8):
        previous = 0
        for group in range(4):
            bits = 0
            for bit in range(4):
                value = cell[(group * 4 + bit) * 8 + column]
                if value != previous:
                    bits |= 1 << bit
                    data.append(value)
                    previous = value
            nibbles[index] = bits
            index += 1
    mask = 0
    mask_bytes = bytearray()
    for j in range(4):
        for k in range(4):
            value = nibbles[8 * k + j] | (nibbles[8 * k + 4 + j] << 4)
            if value:
                mask |= 1 << (4 * j + k)
                mask_bytes.append(value)
    return mask.to_bytes(2, "big") + bytes(mask_bytes) + bytes(data)


def build_image(glyphs: dict[int, tuple[str, bytes]]) -> bytes:
    image = bytearray(0x10000)
    table = FONT_BASE + 16
    data_pos = FONT_BASE + SIZE_TABLE + 0x1000
    for block in range(0, 0x40, 16):
        offset = data_pos - table
        image[
            table - IMAGE_BASE + (block >> 2) : table - IMAGE_BASE + (block >> 2) + 4
        ] = offset.to_bytes(4, "big")
        for code in range(block, block + 16):
            kind, payload = glyphs.get(code, ("empty", b""))
            size = 0x80 if kind == "raw" else len(payload)
            image[FONT_BASE + SIZE_TABLE + code - IMAGE_BASE] = size
            image[data_pos - IMAGE_BASE : data_pos - IMAGE_BASE + len(payload)] = (
                payload
            )
            data_pos += 128 if kind == "raw" else len(payload)
    return bytes(image)


def letter() -> bytes:
    cell = bytearray(CELL_BYTES)
    for row in range(3, 12):
        cell[row * 8 + 0] = 0x1F
        cell[row * 8 + 1] = 0x10 if row % 2 else 0x00
    return bytes(cell)


def test_decompress_matches_reference_encoder() -> None:
    cell = letter()
    assert decompress(compress_column_major(cell)) == cell
    assert decompress(compress_column_major(bytes(CELL_BYTES))) == bytes(CELL_BYTES)


def test_font_locates_raw_empty_and_compressed_glyphs() -> None:
    raw = bytes(range(128))
    image = build_image(
        {0x21: ("comp", compress_column_major(letter())), 0x23: ("raw", raw)}
    )
    font = Font(image, IMAGE_BASE, FONT_BASE)

    assert font.glyph(0x21) == (letter(), "compressed")
    assert font.glyph(0x22) == (bytes(CELL_BYTES), "empty")
    assert font.glyph(0x23) == (raw, "raw")
    assert nibble_at(letter(), 3, 1) == 0xF
    with pytest.raises(ValueError):
        Font(image, IMAGE_BASE, 0x03000000).glyph(0)


def test_cli_render_and_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    image = build_image({0x21: ("comp", compress_column_major(letter()))})
    cart = tmp_path / "cart_ram.bin"
    cart.write_bytes(bytes(0x100) + image[0x100:])
    known = tmp_path / "known.json"
    known.write_text(json.dumps({"glyphs": {"0x0021": letter().hex()}}))
    atlas = tmp_path / "atlas.png"

    args = [
        str(cart),
        "--font-base",
        hex(FONT_BASE),
        "--first",
        "0x20",
        "--count",
        "16",
    ]
    assert main([*args, "--render", str(atlas), "--check", str(known)]) == 0

    report = json.loads(capsys.readouterr().out)
    assert report["check"] == {"known": 1, "exact_matches": 1}
    assert atlas.read_bytes().startswith(b"\x89PNG")
