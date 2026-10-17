"""Minimal SH-2 disassembler for reading code in raw memory dumps.

It covers the common SH-2 instruction forms seen in MSHvSF code (data moves,
arithmetic, shifts, compares, branches, PC- and GBR-relative loads, and system
register moves). Unknown encodings are shown as ``.word``. PC-relative loads also
show the literal value. Mnemonics follow the Hitachi SH-2 programming manual
conventions, as summarized in `docs/code_map.md`; branch targets are `pc + 4 +
2 * displacement`.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path


def _s8(value: int) -> int:
    return value - 0x100 if value & 0x80 else value


def _s12(value: int) -> int:
    return value - 0x1000 if value & 0x800 else value


def _word(memory: bytes, base: int, address: int, size: int) -> int | None:
    offset = address - base
    if 0 <= offset <= len(memory) - size:
        return int.from_bytes(memory[offset : offset + size], "big")
    return None


MOV6 = (
    "mov.b @r{m},r{n}",
    "mov.w @r{m},r{n}",
    "mov.l @r{m},r{n}",
    "mov r{m},r{n}",
    "mov.b @r{m}+,r{n}",
    "mov.w @r{m}+,r{n}",
    "mov.l @r{m}+,r{n}",
    "not r{m},r{n}",
    "swap.b r{m},r{n}",
    "swap.w r{m},r{n}",
    "negc r{m},r{n}",
    "neg r{m},r{n}",
    "extu.b r{m},r{n}",
    "extu.w r{m},r{n}",
    "exts.b r{m},r{n}",
    "exts.w r{m},r{n}",
)
OP2 = {
    0x0: "mov.b r{m},@r{n}",
    0x1: "mov.w r{m},@r{n}",
    0x2: "mov.l r{m},@r{n}",
    0x4: "mov.b r{m},@-r{n}",
    0x5: "mov.w r{m},@-r{n}",
    0x6: "mov.l r{m},@-r{n}",
    0x7: "div0s r{m},r{n}",
    0x8: "tst r{m},r{n}",
    0x9: "and r{m},r{n}",
    0xA: "xor r{m},r{n}",
    0xB: "or r{m},r{n}",
    0xC: "cmp/str r{m},r{n}",
    0xD: "xtrct r{m},r{n}",
    0xE: "mulu.w r{m},r{n}",
    0xF: "muls.w r{m},r{n}",
}
OP3 = {
    0x0: "cmp/eq",
    0x2: "cmp/hs",
    0x3: "cmp/ge",
    0x4: "div1",
    0x5: "dmulu.l",
    0x6: "cmp/hi",
    0x7: "cmp/gt",
    0x8: "sub",
    0xA: "subc",
    0xB: "subv",
    0xC: "add",
    0xD: "dmuls.l",
    0xE: "addc",
    0xF: "addv",
}
OP4 = {
    0x00: "shll r{n}",
    0x01: "shlr r{n}",
    0x04: "rotl r{n}",
    0x05: "rotr r{n}",
    0x08: "shll2 r{n}",
    0x09: "shlr2 r{n}",
    0x0B: "jsr @r{n}",
    0x10: "dt r{n}",
    0x11: "cmp/pz r{n}",
    0x15: "cmp/pl r{n}",
    0x18: "shll8 r{n}",
    0x19: "shlr8 r{n}",
    0x1E: "ldc r{n},gbr",
    0x20: "shal r{n}",
    0x21: "shar r{n}",
    0x22: "sts.l pr,@-r{n}",
    0x24: "rotcl r{n}",
    0x25: "rotcr r{n}",
    0x26: "lds.l @r{n}+,pr",
    0x28: "shll16 r{n}",
    0x29: "shlr16 r{n}",
    0x2A: "lds r{n},pr",
    0x2B: "jmp @r{n}",
}
GBR = {
    0x0: ("mov.b r0,@({},gbr)", 1),
    0x1: ("mov.w r0,@({},gbr)", 2),
    0x2: ("mov.l r0,@({},gbr)", 4),
    0x4: ("mov.b @({},gbr),r0", 1),
    0x5: ("mov.w @({},gbr),r0", 2),
    0x6: ("mov.l @({},gbr),r0", 4),
}


def decode(memory: bytes, base: int, pc: int) -> tuple[int, str]:
    """Return (opcode, text) for the instruction at ``pc``."""
    op = _word(memory, base, pc, 2)
    if op is None:
        raise ValueError(f"address 0x{pc:08X} is outside the dump")
    top, n, m, low = op >> 12, (op >> 8) & 0xF, (op >> 4) & 0xF, op & 0xF
    imm = op & 0xFF
    if top == 0x0:
        if op == 0x0009:
            return op, "nop"
        if op == 0x000B:
            return op, "rts"
        if op == 0x0008:
            return op, "clrt"
        if op == 0x0018:
            return op, "sett"
        forms = {
            0x4: "mov.b r{m},@(r0,r{n})",
            0x5: "mov.w r{m},@(r0,r{n})",
            0x6: "mov.l r{m},@(r0,r{n})",
            0x7: "mul.l r{m},r{n}",
            0xC: "mov.b @(r0,r{m}),r{n}",
            0xD: "mov.w @(r0,r{m}),r{n}",
            0xE: "mov.l @(r0,r{m}),r{n}",
        }
        if low in forms:
            return op, forms[low].format(m=m, n=n)
        system = {
            0x0A: "sts mach,r{n}",
            0x1A: "sts macl,r{n}",
            0x2A: "sts pr,r{n}",
            0x29: "movt r{n}",
            0x02: "stc sr,r{n}",
            0x12: "stc gbr,r{n}",
        }
        if op & 0xFF in system:
            return op, system[op & 0xFF].format(n=n)
    elif top == 0x1:
        return op, f"mov.l r{m},@({low * 4},r{n})"
    elif top == 0x2 and low in OP2:
        return op, OP2[low].format(m=m, n=n)
    elif top == 0x3 and low in OP3:
        return op, f"{OP3[low]} r{m},r{n}"
    elif top == 0x4 and op & 0xFF in OP4:
        return op, OP4[op & 0xFF].format(n=n)
    elif top == 0x5:
        return op, f"mov.l @({low * 4},r{m}),r{n}"
    elif top == 0x6:
        return op, MOV6[low].format(m=m, n=n)
    elif top == 0x7:
        return op, f"add #{_s8(imm)},r{n}"
    elif top == 0x8:
        if n == 0x0:
            return op, f"mov.b r0,@({low},r{m})"
        if n == 0x1:
            return op, f"mov.w r0,@({low * 2},r{m})"
        if n == 0x4:
            return op, f"mov.b @({low},r{m}),r0"
        if n == 0x5:
            return op, f"mov.w @({low * 2},r{m}),r0"
        if n == 0x8:
            return op, f"cmp/eq #{_s8(imm)},r0"
        branches = {0x9: "bt", 0xB: "bf", 0xD: "bt/s", 0xF: "bf/s"}
        if n in branches:
            return op, f"{branches[n]} 0x{pc + 4 + _s8(imm) * 2:08X}"
    elif top == 0x9:
        address = pc + 4 + imm * 2
        value = _word(memory, base, address, 2)
        literal = f"   ! 0x{value:04X}" if value is not None else ""
        return op, f"mov.w @(0x{address:08X}),r{n}{literal}"
    elif top in (0xA, 0xB):
        name = "bra" if top == 0xA else "bsr"
        return op, f"{name} 0x{pc + 4 + _s12(op & 0xFFF) * 2:08X}"
    elif top == 0xC:
        if n in GBR:
            form, size = GBR[n]
            return op, form.format(imm * size)
        if n == 0x3:
            return op, f"trapa #{imm}"
        if n == 0x7:
            return op, f"mova @(0x{(pc & ~3) + 4 + imm * 4:08X}),r0"
        logic = {0x8: "tst", 0x9: "and", 0xA: "xor", 0xB: "or"}
        if n in logic:
            return op, f"{logic[n]} #0x{imm:02X},r0"
    elif top == 0xD:
        address = (pc & ~3) + 4 + imm * 4
        value = _word(memory, base, address, 4)
        literal = f"   ! 0x{value:08X}" if value is not None else ""
        return op, f"mov.l @(0x{address:08X}),r{n}{literal}"
    elif top == 0xE:
        return op, f"mov #{_s8(imm)},r{n}"
    return op, f".word 0x{op:04X}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Disassemble SH-2 code in a raw dump.")
    parser.add_argument("dump", type=Path)
    parser.add_argument("--base", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--start", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--end", type=lambda v: int(v, 0), required=True)
    args = parser.parse_args(argv)
    memory = args.dump.read_bytes()
    try:
        for pc in range(args.start & ~1, args.end, 2):
            op, text = decode(memory, args.base, pc)
            print(f"{pc:08X}: {op:04X}  {text}")
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
