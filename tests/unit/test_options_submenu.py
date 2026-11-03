from __future__ import annotations

from itertools import pairwise

import pytest

from tools.sh2.disasm import decode
from tools.text.caption_compiler import FONT_ADDRESS, FONT_ENTRY
from tools.text.options_submenu import (
    GUARD,
    MM_BASE,
    RESERVE,
    STATE2_INPUT,
    SWITCHES_RESERVE,
    SYS_BASE,
    VBLANK_LITERAL,
    VBLANK_NEXT,
    submenu,
)

ORIGIN = FONT_ADDRESS + FONT_ENTRY[1] - RESERVE


def by_address() -> tuple[bytes, dict[int, bytes]]:
    code, patches = submenu()
    base = {"MM.BIN": MM_BASE, "SYS.BIN": SYS_BASE}
    return code, {
        int(p["offset"], 16) + base[p["file"]]: bytes.fromhex(p["hex"]) for p in patches
    }


def test_patches_keep_lengths_expect_originals_and_do_not_overlap() -> None:
    code, patches = submenu()
    assert 0 < len(code) <= RESERVE
    assert {p["file"] for p in patches} == {"MM.BIN", "SYS.BIN"}
    for name in ("MM.BIN", "SYS.BIN"):
        spans = sorted(
            (int(p["offset"], 16), int(p["offset"], 16) + len(p["hex"]) // 2)
            for p in patches
            if p["file"] == name
        )
        assert all(a[1] <= b[0] for a, b in pairwise(spans))
    for patch in patches:
        assert (
            len(patch["hex"]) == len(patch["expect"])
            and patch["hex"] != patch["expect"]
        )


def test_row_8_handler_and_state_2_jump_point_into_the_payload() -> None:
    code, sites = by_address()
    handler = int.from_bytes(sites[0x0601E9D4][12:16], "big")
    assert ORIGIN <= handler < ORIGIN + len(code) and handler % 2 == 0
    assert sites[0x0601E8B8][3:17] == b"VS POWER GAUGE"
    assert b"COMBO GAUGE" in code and b"EXTRA OPTIONS" in code


def test_v_blank_goes_through_the_guard_to_the_tail_or_the_original() -> None:
    code, sites = by_address()
    assert sites[VBLANK_LITERAL] == GUARD.to_bytes(4, "big")
    block = sites[STATE2_INPUT]
    literal = {
        name: int.from_bytes(block[offset : offset + 4], "big")
        for name, offset in (
            ("submenu", 0x18),
            ("vblank", 0x1C),
            ("sig", 0x20),
            ("next", 0x24),
        )
    }
    assert literal["next"] == VBLANK_NEXT
    vblank = literal["vblank"] - ORIGIN
    assert 0 <= vblank < len(code) and vblank % 4 == 0
    assert literal["sig"] == int.from_bytes(code[vblank : vblank + 4], "big")
    assert ORIGIN <= literal["submenu"] < ORIGIN + len(code)
    # the guard ends in jmp @r2 with a nop in its delay slot
    texts = [decode(block, STATE2_INPUT, STATE2_INPUT + 2 * i)[1] for i in range(11)]
    assert texts[0].startswith("mov.l @(") and texts[9:11] == ["jmp @r2", "nop"]


def test_rows_choose_the_reserve_and_are_checked() -> None:
    code, _ = submenu(SWITCHES_RESERVE, 4)
    assert b"GRAMMAR FIXES" in code and len(code) <= SWITCHES_RESERVE
    with pytest.raises(ValueError):
        submenu(RESERVE, 5)
