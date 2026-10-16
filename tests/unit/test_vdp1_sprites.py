from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from tools.memory.vdp1_sprites import (
    VRAM_SIZE,
    main,
    pixel_bytes,
    render,
    signed,
    sprites,
    to_gray,
    walk,
)


def command(
    control: int,
    *,
    link: int = 0,
    mode: int = 0,
    color: int = 0,
    source: int = 0,
    size: int = 0,
    x: int = 0,
    y: int = 0,
) -> bytes:
    words = [control, link, mode, color, source, size, x, y] + [0] * 8
    return struct.pack(">16H", *words)


def make_vram(commands: list[tuple[int, bytes]], data: dict[int, bytes]) -> bytes:
    vram = bytearray(VRAM_SIZE)
    for address, raw in commands:
        vram[address : address + 32] = raw
    for address, raw in data.items():
        vram[address : address + len(raw)] = raw
    return bytes(vram)


def test_signed_handles_negative_values() -> None:
    assert signed(0x1FFF, 13) == -1
    assert signed(0x0010, 13) == 16
    assert signed(0x7B0, 11) == -80


def test_walk_follows_jump_skip_and_end() -> None:
    vram = make_vram(
        [
            (0x00, command(0x1000, link=0x100 >> 3)),  # jump to 0x100
            (0x20, command(0x0000)),  # bypassed by the jump
            (0x100, command(0x4000)),  # skipped
            (0x120, command(0x000A, x=0x7B0, y=0x7F0)),  # local coordinates
            (0x140, command(0x8000)),  # end
        ],
        {},
    )

    found = walk(vram)

    assert [(c.address, c.kind) for c in found] == [(0x00, 0), (0x120, 0xA)]


def test_walk_rejects_wrong_size() -> None:
    with pytest.raises(ValueError):
        walk(b"\x00" * 32)


def test_sprites_apply_local_coordinates_and_decode_fields() -> None:
    vram = make_vram(
        [
            (0x00, command(0x000A, x=0x7B0, y=0x7F0)),  # local (-80, -16)
            (
                0x20,
                command(
                    0x0000,
                    mode=0x0080,
                    color=0x61E0,
                    source=0x1000 >> 3,
                    size=(2 << 8) | 16,
                    x=100,
                    y=50,
                ),
            ),
            (0x40, command(0x8000)),
        ],
        {0x1000: bytes([0x12] * 128)},
    )

    (sprite,) = sprites(vram)

    assert (sprite.source, sprite.width, sprite.height) == (0x1000, 16, 16)
    assert (sprite.x, sprite.y) == (20, 34)
    assert sprite.color_word == 0x61E0
    assert sprite.color_mode == 0
    assert pixel_bytes(vram, sprite) == bytes([0x12] * 128)


def test_to_gray_expands_4bpp() -> None:
    assert to_gray(b"\x1f", 2, 1, 4) == bytearray([17, 255])


def test_render_and_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vram = make_vram(
        [
            (
                0x00,
                command(0x0000, color=0x61E0, source=0x1000 >> 3, size=(1 << 8) | 8),
            ),
            (
                0x20,
                command(0x0000, color=0x1111, source=0x1000 >> 3, size=(1 << 8) | 8),
            ),
            (0x40, command(0x8000)),
        ],
        {0x1000: bytes([0xFF] * 32)},
    )
    assert render(vram, sprites(vram)).startswith(b"\x89PNG")
    path = tmp_path / "vdp1.bin"
    path.write_bytes(vram)
    out = tmp_path / "out.png"

    assert (
        main([str(path), "--color-word", "0x61E0", "--render", str(out), "--json"]) == 0
    )

    records = json.loads(capsys.readouterr().out)
    assert len(records) == 1
    assert records[0]["color_word"] == 0x61E0
    assert out.read_bytes().startswith(b"\x89PNG")
