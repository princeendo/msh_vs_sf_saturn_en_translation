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
RESERVE = 2048  # bytes of font tail for the sub-menu alone
NAMES_RESERVE = 6144  # with the OPT-005 site table
SWITCHES_RESERVE = 12288  # with NAMES and GRAMMAR sites (OPT-006)
MM_BASE = 0x06018B00
SYS_BASE = 0x06002000  # SYS.BIN is loaded raw here
VBLANK_LITERAL = 0x0600C1C0  # the main V-blank handler's call to VBLANK_NEXT
VBLANK_NEXT = 0x0600CB5C
STATE2_INPUT = 0x0601E22C  # dead: state 2 is never set (EXP-0105)
GUARD = 0x0601E232
STATE2_ORIGINAL = bytes.fromhex(  # 0x0601E22C-0x0601E253 in MM.BIN
    "d90a61929011201920088becdb08dc09dd09de0ab01c4f22db09dc0add0ade0bb0164f224f26000b"
)
VS_LABEL = b"VS POWER GAUGE  --" + b" " * 13  # 31 characters, as the original
ENTRY_LABEL = b" EXTRA OPTIONS" + b" " * 17


def _label(x: int, y: int, text: bytes) -> bytes:
    return bytes((x, y, 0)) + text + b"\x00"


def _record(x: int, y: int, text: bytes) -> bytes:
    return bytes((x, y)) + text + b"\x00"


def _long(value: int) -> bytes:
    return value.to_bytes(4, "big")


def guard(submenu_at: int, vblank_at: int, signature: int) -> bytes:
    """``0x0601E22C``-``0x0601E253``: the state-2 trampoline, then the V-blank
    guard. The guard runs the tail's ``vblank`` only when its first long is
    there (the tail loads after the handler is installed, `EXP-0111`)."""
    source = f"""
        mov.l @(t_submenu),r0
        jmp @r0
        nop
    guard:
        mov.l @(t_vblank),r2
        mov.l @r2,r0
        mov.l @(t_signature),r1
        cmp/eq r1,r0
        bt go
        mov.l @(t_next),r2
    go:
        jmp @r2
        nop
        .align 4
    t_submenu: .long {submenu_at}
    t_vblank: .long {vblank_at}
    t_signature: .long {signature}
    t_next: .long {VBLANK_NEXT}
    """
    code, symbols = assemble(source, STATE2_INPUT)
    if symbols["guard"] != GUARD or len(code) != len(STATE2_ORIGINAL):
        raise ValueError("the guard no longer fits the dead state-2 routine")
    return code


def _assemble(reserve: int, rows: int) -> tuple[bytes, dict[str, int], int]:
    if rows not in (2, 3, 4):
        raise ValueError("the sub-menu has 2, 3 or 4 rows")
    origin = FONT_ADDRESS + FONT_ENTRY[1] - reserve
    code, symbols = assemble(SOURCE.read_text(), origin, {"ROWS": rows})
    return code, symbols, origin


def tail(reserve: int, sites: bytes, rows: int = 3) -> bytes:
    """The payload with an OPT-005 site table (``names_switch.pack``) in place
    of the empty one; the code before it is the same as ``submenu``'s."""
    code, symbols, origin = _assemble(reserve, rows)
    cut = symbols["sites"] - origin
    if code[cut:] != bytes(4):
        raise ValueError("the site table is not the end of the payload")
    payload = code[:cut] + sites
    if len(payload) > reserve:
        raise ValueError(f"the payload is {len(payload)} bytes; the reserve {reserve}")
    return payload


def code_long(code: bytes, origin: int, address: int) -> int:
    return int.from_bytes(code[address - origin : address - origin + 4], "big")


def submenu(
    reserve: int = RESERVE, rows: int = 2
) -> tuple[bytes, list[dict[str, str]]]:
    """The tail payload and the ``MM.BIN`` patches (spec v3 ``patches``).
    ``rows``: 2 (BOSS FIGHT, COMBO GAUGE), 3 (+ NAMES), 4 (+ GRAMMAR FIXES)."""
    code, symbols, origin = _assemble(reserve, rows)
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
        # state 2: input jumps to the sub-menu; the BUTTON CONFIG draw is skipped.
        # The rest of that dead routine holds the V-blank guard (OPT-005).
        (
            0x0601E22C,
            STATE2_ORIGINAL,
            guard(
                symbols["submenu"],
                symbols["vblank"],
                code_long(code, origin, symbols["vblank"]),
            ),
            "state-2 trampoline and the V-blank guard",
        ),
        (0x0601DDAC, bytes.fromhex("b43a4f22"), bytes.fromhex("a0000009"), "bra; nop"),
    ]
    patches = []
    for address, old, new, why in writes:
        patches.append(_patch("MM.BIN", address - MM_BASE, old, new, why))
    # the V-blank handler's call to 0x0600CB5C goes through the guard
    patches.append(
        _patch(
            "SYS.BIN",
            VBLANK_LITERAL - SYS_BASE,
            _long(VBLANK_NEXT),
            _long(GUARD),
            "V-blank call through the guard",
        )
    )
    return code, patches


def _patch(name: str, offset: int, old: bytes, new: bytes, why: str) -> dict[str, str]:
    if len(old) != len(new):
        raise ValueError(f"{name} 0x{offset:X}: {why} changes the length")
    return {
        "file": name,
        "offset": f"0x{offset:X}",
        "hex": new.hex(),
        "expect": old.hex(),
        "why": f"OPT-004/OPT-005 {name} 0x{offset:X}: {why}",
    }
