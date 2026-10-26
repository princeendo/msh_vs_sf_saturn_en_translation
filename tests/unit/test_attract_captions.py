from __future__ import annotations

import struct

import pytest

from tools.disc.attract_captions import (
    ATTRIBUTES,
    BANNER,
    GREY,
    NBG2_MAP,
    RED,
    LayoutError,
    Line,
    Plan,
    Slot,
    View,
    apply_plan,
    banner_code,
    diff_patches,
    draw,
    line_width,
    macro_slot,
    macro_tiles,
    map_states,
    overwrite_block,
    recolour,
)
from tools.disc.st2_encode import lz_encode, map_encode
from tools.disc.st2_stream import lz_decode, script_frames


class SolidFont:
    """Every banner cell is a solid 16x16 block of colour 3."""

    def glyph(self, code: int) -> tuple[bytes, str]:
        return bytes([0x33]) * 128, "raw"


def test_banner_codes_follow_the_letter_grid() -> None:
    assert banner_code("A") == 0x2E0 + 2 * 2  # i = 2
    assert banner_code("G") == 0x2E0 + 0x20  # i = 8: next row
    assert banner_code("!") == 0x348
    with pytest.raises(LayoutError):
        banner_code("a")


def test_lines_sit_on_a_24_pixel_grid() -> None:
    assert line_width("A") == 32
    assert line_width("A B!") == 3 * 24 + 32


def test_macro_slots_run_down_each_column() -> None:
    assert macro_slot(0, 0, 0) == 0
    assert macro_slot(0, 0, 7) == 7
    assert macro_slot(0, 1, 0) == 8
    assert macro_slot(1, 2, 3) == 512 + 19


def test_draw_centres_each_line_on_the_screen() -> None:
    canvas = draw(SolidFont(), [Line("AB", 10)], (16, 272))  # type: ignore[arg-type]
    xs = {x for x, _ in canvas}
    ys = {y for _, y in canvas}
    width = 24 + 32
    assert (min(xs), max(xs)) == (176 - width // 2 + 16, 176 + width // 2 + 16 - 1)
    assert (min(ys), max(ys)) == (282, 313)
    assert set(canvas.values()) == {3}


def test_macro_tiles_pack_four_characters_and_shift_colours() -> None:
    canvas = {(16, 0): 5}  # the top-right character's first pixel
    tiles = macro_tiles(canvas, 0, 0)
    assert len(tiles) == 512
    assert tiles[128] == 0x61  # colour 5 drawn as 6, then background 1
    assert tiles[:128] == bytes([0x11]) * 128


def frame(word: int, *updates: list[int]) -> bytes:
    return struct.pack(">H", word) + b"".join(map_encode(u) for u in updates)


def test_apply_plan_rewrites_the_caption_window() -> None:
    keep = [0xFFFF] * 0x2000
    main, later, after = list(keep), list(keep), list(keep)
    main[0] = main[1] = 9
    later[0] = 7  # a later update touching a planned entry
    after[0] = 3  # the scene's own clear
    script = frame(0x80, main) + frame(0x80, later) + frame(0x80, after) + b"\xff\xff"
    slot = Slot("s", 0, 2, (View(0, (0, 0), 0),), (), {})
    plan = Plan({0: 5, ATTRIBUTES: 1}, {})
    new = apply_plan(script, slot, plan)
    states = map_states(new, [0, 1, 2])
    assert states[0][0] == 5 and states[0][ATTRIBUTES] == 1
    assert states[0][1] == 9  # not planned: unchanged
    assert states[1][0] == 5  # the later update now keeps the plan
    assert states[2][0] == 3
    assert len(script_frames(new)) == 4
    with pytest.raises(LayoutError):
        apply_plan(script, Slot("s", 3, 4, (), (), {}), plan)


def test_map_states_follow_only_the_nbg2_array() -> None:
    other = [0xFFFF] * 0x2000
    other[0] = 4
    script = struct.pack(">H", 0x20) + map_encode(other) + b"\xff\xff"
    assert map_states(script, [0])[0][0] == 0xFFFF
    assert NBG2_MAP == 0x06037020


def test_recolour_changes_the_caption_slot_ramp_loads() -> None:
    words = [0] * 0x800
    words[0x600:0x610] = GREY
    words[0x610:0x620] = RED
    load = b"\x00\x00\x08\x00" + struct.pack(">2048H", *words)
    other = load.replace(struct.pack(">H", 0xF333), struct.pack(">H", 0xF334))
    script = b"\x01" + other + load * 5
    new, changed = recolour(script)
    starts = [1 + len(other) + k * len(load) for k in range(5)]
    assert changed == [starts[0], starts[2], starts[4]]
    for start in starts:
        grey = struct.unpack_from(">16H", new, start + 4 + 2 * 0x600)
        red = struct.unpack_from(">16H", new, start + 4 + 2 * 0x610)
        if start in changed:
            assert grey[0] == GREY[0] and grey[1:15] == BANNER
            assert red[0] == RED[0] and red[1:15] == BANNER
            assert grey[15] == GREY[15] and red[15] == RED[15]
        else:
            assert grey == GREY and red == RED
    assert new[: starts[0]] == script[: starts[0]]
    with pytest.raises(LayoutError):
        recolour(b"\x01" + load * 4)


def test_overwrite_block_keeps_the_header_size_when_shorter() -> None:
    data = bytes(range(256)) * 4
    original = lz_encode(bytes(1024)) + b"\xaa" * 16  # tiny block
    with pytest.raises(LayoutError):
        overwrite_block(original, 0, data)  # does not fit
    roomy = lz_encode(data) + b"tail"
    out = overwrite_block(roomy, 0, bytes(1024))
    assert out[:4] == roomy[:4] and out.endswith(b"tail")
    assert lz_decode(out, 0)[0] == bytes(1024)


def test_overwrite_block_grows_into_zero_padding_up_to_the_limit() -> None:
    data = bytes(range(256)) * 4
    small = lz_encode(bytes(1024))
    original = small + bytes(2048)
    out = overwrite_block(original, 0, data, limit=len(original) - 8)
    assert struct.unpack_from(">I", out)[0] == len(lz_encode(data)) - 8
    assert lz_decode(out, 0)[0] == data


def test_diff_patches_merge_nearby_changes() -> None:
    old = bytes(64)
    new = bytearray(old)
    new[2] = new[10] = new[40] = 1
    patches = diff_patches("X.ST2", old, bytes(new))
    assert [(p["offset"], len(p["hex"]) // 2) for p in patches] == [
        ("0x2", 9),
        ("0x28", 1),
    ]
    assert patches[0]["expect"] == "00" * 9
