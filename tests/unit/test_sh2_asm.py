from __future__ import annotations

import pytest

from tools.sh2.asm import AsmError, assemble, encode
from tools.sh2.disasm import decode

BASE, PC = 0x06000000, 0x06000800


def test_every_disassembled_form_reassembles_to_the_same_opcode() -> None:
    covered = 0
    for op in range(0x10000):
        memory = bytearray(0x1000)
        memory[PC - BASE : PC - BASE + 2] = op.to_bytes(2, "big")
        _, text = decode(bytes(memory), BASE, PC)
        text = text.split("!")[0].strip()
        if text.startswith(".word"):
            continue
        try:
            got = encode(text, PC, {})
        except AsmError:
            continue
        assert got == op, f"{text}: 0x{got:04X} != 0x{op:04X}"
        covered += 1
    assert covered > 40000


def test_labels_literals_and_directives() -> None:
    source = """
        .equ TARGET, 0x06017AB0
    start:
        mov.l @(lit),r1      ! literal below
        mov #1,r0
        mov.l r0,@r1
        bra start
        nop
        .align 4
    lit: .long TARGET
    text: .asciz "AB"
    """
    data, symbols = assemble(source, 0x027BB6A0)
    assert symbols["start"] == 0x027BB6A0 and symbols["lit"] == 0x027BB6AC
    assert data[:2] == bytes.fromhex("D102")
    assert data[6:8] == bytes.fromhex("AFFB")  # bra back to start
    assert data[12:16] == bytes.fromhex("06017AB0")
    assert data[16:] == b"AB\x00"


def test_errors() -> None:
    with pytest.raises(AsmError, match="line 1"):
        assemble("mov #300,r1", 0)
    with pytest.raises(AsmError):
        assemble("bra far\nnop\n.space 0x2000\nfar: nop", 0)
    with pytest.raises(AsmError):
        assemble("mov.l @(lit),r1\nlit: .word 1", 0)  # literal not aligned
