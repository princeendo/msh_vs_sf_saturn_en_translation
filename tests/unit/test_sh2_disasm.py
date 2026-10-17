from __future__ import annotations

from pathlib import Path

import pytest

from tools.sh2.disasm import decode, main

BASE = 0x06000000


def text(op: int, pc: int = BASE, extra: bytes = b"") -> str:
    memory = bytearray(64)
    memory[pc - BASE : pc - BASE + 2] = op.to_bytes(2, "big")
    memory[0x20 : 0x20 + len(extra)] = extra
    return decode(bytes(memory), BASE, pc)[1]


@pytest.mark.parametrize(
    ("op", "expected"),
    [
        (0x0009, "nop"),
        (0x000B, "rts"),
        (0xE04C, "mov #76,r0"),
        (0xE7FF, "mov #-1,r7"),
        (0x2601, "mov.w r0,@r6"),
        (0x6094, "mov.b @r9+,r0"),
        (0x641C, "extu.b r1,r4"),
        (0x4401, "shlr r4"),
        (0x4F22, "sts.l pr,@-r15"),
        (0x400B, "jsr @r0"),
        (0x392C, "add r2,r9"),
        (0x3200, "cmp/eq r0,r2"),
        (0xC50D, "mov.w @(26,gbr),r0"),
        (0xC207, "mov.l r0,@(28,gbr)"),
        (0xC33E, "trapa #62"),
        (0x80C4, "mov.b r0,@(4,r12)"),
        (0x5881, "mov.l @(4,r8),r8"),
        (0x7AFF, "add #-1,r10"),
        (0xFFFF, ".word 0xFFFF"),
    ],
)
def test_decode_forms(op: int, expected: str) -> None:
    assert text(op) == expected


def test_branch_targets_and_pc_relative_literals() -> None:
    assert text(0x8FF5, BASE + 0x12) == "bf/s 0x06000000"
    assert text(0xA002, BASE) == "bra 0x06000008"
    literal = (0x0601CEEC).to_bytes(4, "big")
    # mov.l @(disp,pc): (pc & ~3) + 4 + disp*4 = 0x06000020 when pc=0x06000000, disp=7
    assert text(0xD807, BASE, literal) == "mov.l @(0x06000020),r8   ! 0x0601CEEC"
    assert text(0x900E, BASE, b"\x50\x00") == "mov.w @(0x06000020),r0   ! 0x5000"


def test_decode_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        decode(b"\x00\x09", BASE, BASE + 4)


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dump = tmp_path / "code.bin"
    dump.write_bytes(bytes.fromhex("000b0009"))
    assert (
        main(
            [
                str(dump),
                "--base",
                "0x06000000",
                "--start",
                "0x06000000",
                "--end",
                "0x06000004",
            ]
        )
        == 0
    )
    assert capsys.readouterr().out.splitlines() == [
        "06000000: 000B  rts",
        "06000002: 0009  nop",
    ]
