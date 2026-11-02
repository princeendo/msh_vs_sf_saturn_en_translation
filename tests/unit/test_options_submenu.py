from __future__ import annotations

from itertools import pairwise

from tools.text.caption_compiler import FONT_ADDRESS, FONT_ENTRY
from tools.text.options_submenu import MM_BASE, RESERVE, submenu


def test_patches_keep_lengths_expect_originals_and_do_not_overlap() -> None:
    code, patches = submenu()
    assert 0 < len(code) <= RESERVE
    spans = []
    for patch in patches:
        assert patch["file"] == "MM.BIN"
        assert (
            len(patch["hex"]) == len(patch["expect"])
            and patch["hex"] != patch["expect"]
        )
        start = int(patch["offset"], 16)
        spans.append((start, start + len(patch["hex"]) // 2))
    spans.sort()
    assert all(a[1] <= b[0] for a, b in pairwise(spans))


def test_row_8_handler_and_state_2_jump_point_into_the_payload() -> None:
    code, patches = submenu()
    origin = FONT_ADDRESS + FONT_ENTRY[1] - RESERVE
    by_address = {
        int(p["offset"], 16) + MM_BASE: bytes.fromhex(p["hex"]) for p in patches
    }
    handler = int.from_bytes(by_address[0x0601E9D4][12:16], "big")
    jump = int.from_bytes(by_address[0x0601E22C][8:12], "big")
    for target in (handler, jump):
        assert origin <= target < origin + len(code)
    assert handler == origin  # `entry` is the first routine
    assert by_address[0x0601E8B8][3:17] == b"VS POWER GAUGE"
    assert b"COMBO GAUGE" in code and b"EXTRA OPTIONS" in code
