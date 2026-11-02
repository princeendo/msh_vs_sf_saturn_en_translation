"""OPT-004: the Options screen's EXTRA OPTIONS sub-menu.

The sub-menu code (``data/opt004/submenu.s``) is assembled into the quote
font's tail (``caption_compiler.FontTail``, `EXP-0107`); the cart executes it
(`EXP-0108`). In ``MM.BIN`` (loaded at ``0x06018B00``, `EXP-0105`):

- Options row 8 becomes EXTRA OPTIONS, always shown at y = 22; its handler
  is the sub-menu's ``entry``;
- VS POWER GAGE, still shown only when unlocked, moves to row 9 (y = 24) and
  is spelled VS POWER GAUGE (user, 2026-11-02);
- the game's hidden COMBO GAGE row is gone from OPTION MODE: COMBO GAUGE is
  in the sub-menu with BOSS FIGHT;
- the unused menu state 2 runs the sub-menu: its input routine
  (``0x0601E22C``) jumps to ``submenu`` and its draw call is skipped.

Every write names the original bytes it expects.
"""

from __future__ import annotations

from pathlib import Path

from tools.sh2.asm import assemble
from tools.text.caption_compiler import FONT_ADDRESS, FONT_ENTRY

SOURCE = Path("data/opt004/submenu.s")
RESERVE = 1024  # bytes of font tail; the sub-menu is 676
MM_BASE = 0x06018B00
VS_LABEL = b"VS POWER GAUGE  --" + b" " * 13  # 31 characters, as the original
ENTRY_LABEL = b" EXTRA OPTIONS" + b" " * 17


def _label(x: int, y: int, text: bytes) -> bytes:
    return bytes((x, y, 0)) + text + b"\x00"


def _record(x: int, y: int, text: bytes) -> bytes:
    return bytes((x, y)) + text + b"\x00"


def _long(value: int) -> bytes:
    return value.to_bytes(4, "big")


def submenu(reserve: int = RESERVE) -> tuple[bytes, list[dict[str, str]]]:
    """The tail payload and the ``MM.BIN`` patches (spec v3 ``patches``)."""
    origin = FONT_ADDRESS + FONT_ENTRY[1] - reserve
    code, symbols = assemble(SOURCE.read_text(), origin)
    if len(code) > reserve:
        raise ValueError(f"the sub-menu is {len(code)} bytes; the reserve {reserve}")
    writes: list[tuple[int, bytes, bytes, str]] = [
        # the cursor's last row: 8 always (EXTRA OPTIONS), 9 with VS POWER GAUGE
        (0x0601DEC2, bytes.fromhex("e407"), bytes.fromhex("e408"), "mov #8,r4"),
        (0x0601DECE, bytes.fromhex("e408"), bytes.fromhex("e409"), "mov #9,r4"),
        # labels: the COMBO GAGE slot's label is drawn always (bt -> nop)
        (0x0601DE20, bytes.fromhex("8902"), bytes.fromhex("0009"), "nop"),
        (
            0x0601E8B8,
            _label(6, 22, b" VS POWER GAGE  --" + b" " * 13),
            _label(6, 24, VS_LABEL),
            "VS POWER GAUGE label at y = 24",
        ),
        (
            0x0601E8DB,
            _label(6, 24, b"    COMBO GAGE  --" + b" " * 13),
            _label(6, 22, ENTRY_LABEL),
            "EXTRA OPTIONS label at y = 22",
        ),
        # values: VS POWER GAUGE as row 9 with the y = 24 strings
        (0x0601E58A, bytes.fromhex("e408"), bytes.fromhex("e409"), "mov #9,r4"),
        (0x0601E5FC, _long(0x0601F138), _long(0x0601F154), "y = 24 NORMAL/FULL"),
        # EXTRA OPTIONS' value as row 8, always (bt -> nop)
        (0x0601E596, bytes.fromhex("8905"), bytes.fromhex("0009"), "nop"),
        (0x0601E59E, bytes.fromhex("e409"), bytes.fromhex("e408"), "mov #8,r4"),
        (0x0601E604, _long(0x06017AD4), _long(0x06017AA4), "a setting always 0"),
        (0x0601E608, _long(0x0601F154), _long(symbols["entry_values"]), "PRESS A OR C"),
        # row records: max, label record, setting, handler
        (
            0x0601E9D4,
            _long(1) + _long(0x0601EA98) + _long(0x06017AD0) + _long(0x0601E16C),
            _long(0) + _long(0x0601EA98) + _long(0x06017AA4) + _long(symbols["entry"]),
            "row 8: EXTRA OPTIONS",
        ),
        (
            0x0601E9E4,
            _long(1) + _long(0x0601EAAA) + _long(0x06017AD4) + _long(0x0601E172),
            _long(1) + _long(0x0601EAAA) + _long(0x06017AD0) + _long(0x0601E16C),
            "row 9: VS POWER GAUGE",
        ),
        # highlight records of rows 8 and 9
        (
            0x0601EA98,
            _record(6, 22, b" VS POWER GAGE "),
            _record(6, 22, b" EXTRA OPTIONS "),
            "row 8 highlight",
        ),
        (
            0x0601EAAA,
            _record(6, 24, b"    COMBO GAGE "),
            _record(6, 24, b"VS POWER GAUGE "),
            "row 9 highlight",
        ),
        # state 2: input jumps to the sub-menu; the BUTTON CONFIG draw is skipped
        (
            0x0601E22C,
            bytes.fromhex("d90a61929011201920088bec"),
            bytes.fromhex("d001402b00090009") + _long(symbols["submenu"]),
            "mov.l @(0x0601E234),r0; jmp @r0; nop; nop; .long submenu",
        ),
        (0x0601DDAC, bytes.fromhex("b43a4f22"), bytes.fromhex("a0000009"), "bra; nop"),
    ]
    patches = []
    for address, old, new, why in writes:
        if len(old) != len(new):
            raise ValueError(f"0x{address:08X}: {why} changes the length")
        patches.append(
            {
                "file": "MM.BIN",
                "offset": f"0x{address - MM_BASE:X}",
                "hex": new.hex(),
                "expect": old.hex(),
                "why": f"OPT-004 0x{address:08X}: {why}",
            }
        )
    return code, patches
