"""Minimal two-pass SH-2 assembler for small game patches (OPT-004).

It covers the forms ``tools.sh2.disasm`` prints, in the same syntax, so a
disassembly of game code reassembles to the same bytes. Source is one
statement per line:

- ``label:`` defines a label at the current address;
- ``! comment`` or ``; comment``;
- ``.equ NAME, value``, ``.long expr``, ``.word expr``, ``.byte expr``,
  ``.ascii "text"``, ``.asciz "text"``, ``.align N``, ``.space N``;
- instructions. PC-relative loads are written ``mov.l @(target),rN``,
  ``mov.w @(target),rN`` and ``mova @(target),r0``, where ``target`` is the
  literal's address (a label or a number). Branch targets are labels or
  numbers.

Expressions are integers (decimal, ``0x``), names, and ``+``/``-`` between
them. Delay slots are not checked: write them as the SH-2 manual requires.
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Callable
from pathlib import Path

REG = r"r(1[0-5]|[0-9])"
Operands = Callable[[re.Match[str], int, dict[str, int]], int]


class AsmError(ValueError):
    pass


def evaluate(text: str, symbols: dict[str, int]) -> int:
    total, sign = 0, 1
    for token in re.findall(r"[+-]|[^+\-\s]+", text.replace(" ", "")):
        if token in "+-":
            sign = 1 if token == "+" else -1
            continue
        if re.fullmatch(r"-?(0x[0-9a-fA-F]+|\d+)", token):
            value = int(token, 0)
        elif token in symbols:
            value = symbols[token]
        else:
            raise AsmError(f"unknown symbol {token!r}")
        total += sign * value
        sign = 1
    return total


def _signed(value: int, bits: int, what: str) -> int:
    if not -(1 << (bits - 1)) <= value < 1 << (bits - 1):
        raise AsmError(f"{what} {value} does not fit {bits} bits")
    return value & ((1 << bits) - 1)


def _unsigned(value: int, bits: int, what: str) -> int:
    if not 0 <= value < 1 << bits:
        raise AsmError(f"{what} {value} does not fit {bits} unsigned bits")
    return value


def _imm8(value: int) -> int:
    if -128 <= value <= 255:
        return value & 0xFF
    raise AsmError(f"immediate {value} does not fit 8 bits")


def _branch(target: int, pc: int, bits: int) -> int:
    offset = target - pc - 4
    if offset % 2:
        raise AsmError(f"branch target 0x{target:X} is odd")
    return _signed(offset // 2, bits, "branch displacement")


def _pcrel(target: int, pc: int, size: int) -> int:
    base = (pc & ~3) + 4 if size == 4 else pc + 4
    offset = target - base
    if offset % size or target % size:
        raise AsmError(f"literal 0x{target:X} is not aligned for size {size}")
    return _unsigned(offset // size, 8, "PC-relative displacement")


def _rr(op: int) -> Operands:
    return lambda m, pc, s: op | int(m["n"]) << 8 | int(m["m"]) << 4


def _rn(op: int) -> Operands:
    return lambda m, pc, s: op | int(m["n"]) << 8


def _fixed(op: int) -> Operands:
    return lambda m, pc, s: op


RN, RM = f"(?P<n>{REG[2:-1]})", f"(?P<m>{REG[2:-1]})"
R_N, R_M = f"r{RN}", f"r{RM}"
EXPR = r"(?P<e>[^,()@]+)"

FORMS: list[tuple[str, Operands]] = [
    ("nop", _fixed(0x0009)),
    ("rts", _fixed(0x000B)),
    ("clrt", _fixed(0x0008)),
    ("sett", _fixed(0x0018)),
    (
        f"mov #{EXPR},{R_N}",
        lambda m, pc, s: 0xE000 | int(m["n"]) << 8 | _imm8(evaluate(m["e"], s)),
    ),
    (f"mov {R_M},{R_N}", _rr(0x6003)),
    (f"mov\\.b @{R_M},{R_N}", _rr(0x6000)),
    (f"mov\\.w @{R_M},{R_N}", _rr(0x6001)),
    (f"mov\\.l @{R_M},{R_N}", _rr(0x6002)),
    (f"mov\\.b @{R_M}\\+,{R_N}", _rr(0x6004)),
    (f"mov\\.w @{R_M}\\+,{R_N}", _rr(0x6005)),
    (f"mov\\.l @{R_M}\\+,{R_N}", _rr(0x6006)),
    (f"mov\\.b {R_M},@{R_N}", _rr(0x2000)),
    (f"mov\\.w {R_M},@{R_N}", _rr(0x2001)),
    (f"mov\\.l {R_M},@{R_N}", _rr(0x2002)),
    (f"mov\\.b {R_M},@-{R_N}", _rr(0x2004)),
    (f"mov\\.w {R_M},@-{R_N}", _rr(0x2005)),
    (f"mov\\.l {R_M},@-{R_N}", _rr(0x2006)),
    (f"mov\\.b {R_M},@\\(r0,{R_N}\\)", _rr(0x0004)),
    (f"mov\\.w {R_M},@\\(r0,{R_N}\\)", _rr(0x0005)),
    (f"mov\\.l {R_M},@\\(r0,{R_N}\\)", _rr(0x0006)),
    (f"mov\\.b @\\(r0,{R_M}\\),{R_N}", _rr(0x000C)),
    (f"mov\\.w @\\(r0,{R_M}\\),{R_N}", _rr(0x000D)),
    (f"mov\\.l @\\(r0,{R_M}\\),{R_N}", _rr(0x000E)),
    (
        f"mov\\.l {R_M},@\\({EXPR},{R_N}\\)",
        lambda m, pc, s: 0x1000 | int(m["n"]) << 8 | int(m["m"]) << 4 | _disp(m, s, 4),
    ),
    (
        f"mov\\.l @\\({EXPR},{R_M}\\),{R_N}",
        lambda m, pc, s: 0x5000 | int(m["n"]) << 8 | int(m["m"]) << 4 | _disp(m, s, 4),
    ),
    (
        f"mov\\.b r0,@\\({EXPR},{R_M}\\)",
        lambda m, pc, s: 0x8000 | int(m["m"]) << 4 | _disp(m, s, 1),
    ),
    (
        f"mov\\.w r0,@\\({EXPR},{R_M}\\)",
        lambda m, pc, s: 0x8100 | int(m["m"]) << 4 | _disp(m, s, 2),
    ),
    (
        f"mov\\.b @\\({EXPR},{R_M}\\),r0",
        lambda m, pc, s: 0x8400 | int(m["m"]) << 4 | _disp(m, s, 1),
    ),
    (
        f"mov\\.w @\\({EXPR},{R_M}\\),r0",
        lambda m, pc, s: 0x8500 | int(m["m"]) << 4 | _disp(m, s, 2),
    ),
    (
        f"mov\\.l @\\({EXPR}\\),{R_N}",
        lambda m, pc, s: 0xD000 | int(m["n"]) << 8 | _pcrel(evaluate(m["e"], s), pc, 4),
    ),
    (
        f"mov\\.w @\\({EXPR}\\),{R_N}",
        lambda m, pc, s: 0x9000 | int(m["n"]) << 8 | _pcrel(evaluate(m["e"], s), pc, 2),
    ),
    (
        f"mova @\\({EXPR}\\),r0",
        lambda m, pc, s: 0xC700 | _pcrel(evaluate(m["e"], s), pc, 4),
    ),
    (
        f"add #{EXPR},{R_N}",
        lambda m, pc, s: 0x7000 | int(m["n"]) << 8 | _imm8(evaluate(m["e"], s)),
    ),
    (f"cmp/eq #{EXPR},r0", lambda m, pc, s: 0x8800 | _imm8(evaluate(m["e"], s))),
    (f"tst #{EXPR},r0", lambda m, pc, s: 0xC800 | _imm8(evaluate(m["e"], s))),
    (f"and #{EXPR},r0", lambda m, pc, s: 0xC900 | _imm8(evaluate(m["e"], s))),
    (f"xor #{EXPR},r0", lambda m, pc, s: 0xCA00 | _imm8(evaluate(m["e"], s))),
    (f"or #{EXPR},r0", lambda m, pc, s: 0xCB00 | _imm8(evaluate(m["e"], s))),
    (f"trapa #{EXPR}", lambda m, pc, s: 0xC300 | _imm8(evaluate(m["e"], s))),
    (f"bt {EXPR}", lambda m, pc, s: 0x8900 | _branch(evaluate(m["e"], s), pc, 8)),
    (f"bf {EXPR}", lambda m, pc, s: 0x8B00 | _branch(evaluate(m["e"], s), pc, 8)),
    (f"bt/s {EXPR}", lambda m, pc, s: 0x8D00 | _branch(evaluate(m["e"], s), pc, 8)),
    (f"bf/s {EXPR}", lambda m, pc, s: 0x8F00 | _branch(evaluate(m["e"], s), pc, 8)),
    (f"bra {EXPR}", lambda m, pc, s: 0xA000 | _branch(evaluate(m["e"], s), pc, 12)),
    (f"bsr {EXPR}", lambda m, pc, s: 0xB000 | _branch(evaluate(m["e"], s), pc, 12)),
    (f"jsr @{R_N}", _rn(0x400B)),
    (f"jmp @{R_N}", _rn(0x402B)),
    (f"sts\\.l pr,@-{R_N}", _rn(0x4022)),
    (f"lds\\.l @{R_N}\\+,pr", _rn(0x4026)),
    (f"sts pr,{R_N}", _rn(0x002A)),
    (f"lds {R_N},pr", _rn(0x402A)),
    (f"sts macl,{R_N}", _rn(0x001A)),
    (f"sts mach,{R_N}", _rn(0x000A)),
    (f"movt {R_N}", _rn(0x0029)),
    (f"mul\\.l {R_M},{R_N}", _rr(0x0007)),
]
for name, op in (
    ("shll", 0x4000), ("shlr", 0x4001), ("shll2", 0x4008), ("shlr2", 0x4009),
    ("shll8", 0x4018), ("shlr8", 0x4019), ("shll16", 0x4028), ("shlr16", 0x4029),
    ("shal", 0x4020), ("shar", 0x4021), ("rotl", 0x4004), ("rotr", 0x4005),
    ("rotcl", 0x4024), ("rotcr", 0x4025), ("dt", 0x4010), ("cmp/pz", 0x4011),
    ("cmp/pl", 0x4015),
):  # fmt: skip
    FORMS.append((f"{re.escape(name)} {R_N}", _rn(op)))
for name, op in (
    ("tst", 0x2008), ("and", 0x2009), ("xor", 0x200A), ("or", 0x200B),
    ("cmp/eq", 0x3000), ("cmp/hs", 0x3002), ("cmp/ge", 0x3003), ("cmp/hi", 0x3006),
    ("cmp/gt", 0x3007), ("sub", 0x3008), ("add", 0x300C), ("dmuls.l", 0x300D),
    ("dmulu.l", 0x3005), ("not", 0x6007), ("neg", 0x600B), ("extu.b", 0x600C),
    ("extu.w", 0x600D), ("exts.b", 0x600E), ("exts.w", 0x600F), ("swap.w", 0x6009),
):  # fmt: skip
    FORMS.append((f"{re.escape(name)} {R_M},{R_N}", _rr(op)))
COMPILED = [(re.compile(pattern + r"$", re.IGNORECASE), enc) for pattern, enc in FORMS]


def _disp(m: re.Match[str], symbols: dict[str, int], size: int) -> int:
    value = evaluate(m["e"], symbols)
    if value % size:
        raise AsmError(f"displacement {value} is not a multiple of {size}")
    return _unsigned(value // size, 4, "displacement")


def encode(text: str, pc: int, symbols: dict[str, int]) -> int:
    canonical = re.sub(r"\s*,\s*", ",", text.strip())
    canonical = re.sub(r"\s+", " ", canonical)
    for pattern, encoder in COMPILED:
        match = pattern.match(canonical)
        if match:
            return encoder(match, pc, symbols)
    raise AsmError(f"unsupported instruction {text!r}")


def _string(text: str) -> bytes:
    match = re.fullmatch(r'"(.*)"', text.strip())
    if not match:
        raise AsmError(f"expected a quoted string, got {text!r}")
    return match[1].encode("ascii").decode("unicode_escape").encode("latin-1")


def _statements(source: str) -> list[tuple[int, str]]:
    out = []
    for number, raw in enumerate(source.splitlines(), 1):
        line = re.split(r"[!;]", raw, maxsplit=1)[0] if '"' not in raw else raw
        line = line.strip()
        while (label := re.match(r"([A-Za-z_.][\w.]*):\s*", line)) is not None:
            out.append((number, label[0].strip()))
            line = line[label.end() :]
        if line:
            out.append((number, line))
    return out


def _size(statement: str, pc: int, symbols: dict[str, int]) -> int:
    directive, _, rest = statement.partition(" ")
    if directive == ".long":
        return 4 * len(rest.split(","))
    if directive == ".word":
        return 2 * len(rest.split(","))
    if directive == ".byte":
        return len(rest.split(","))
    if directive in (".ascii", ".asciz"):
        return len(_string(rest)) + (directive == ".asciz")
    if directive == ".align":
        step = evaluate(rest, symbols)
        return -pc % step
    if directive == ".space":
        return evaluate(rest, symbols)
    if directive == ".equ":
        return 0
    return 2


def assemble(
    source: str, origin: int, symbols: dict[str, int] | None = None
) -> tuple[bytes, dict[str, int]]:
    """Assemble ``source`` at ``origin``; return (bytes, symbols with labels)."""
    table = dict(symbols or {})
    statements = _statements(source)
    pc = origin
    for number, statement in statements:  # pass 1: addresses
        try:
            if statement.endswith(":"):
                table[statement[:-1]] = pc
            elif statement.startswith(".equ"):
                name, expr = statement[4:].split(",", 1)
                table[name.strip()] = evaluate(expr, table)
            else:
                pc += _size(statement, pc, table)
        except AsmError as error:
            raise AsmError(f"line {number}: {error}") from error
    out = bytearray()
    pc = origin
    for number, statement in statements:  # pass 2: bytes
        if statement.endswith(":") or statement.startswith(".equ"):
            continue
        try:
            directive, _, rest = statement.partition(" ")
            if directive in (".long", ".word", ".byte"):
                width = {".long": 4, ".word": 2, ".byte": 1}[directive]
                for item in rest.split(","):
                    value = evaluate(item, table) & ((1 << (8 * width)) - 1)
                    out += value.to_bytes(width, "big")
            elif directive in (".ascii", ".asciz"):
                out += _string(rest) + (b"\x00" if directive == ".asciz" else b"")
            elif directive in (".align", ".space"):
                out += bytes(_size(statement, pc, table))
            else:
                if pc % 2:
                    raise AsmError("instruction at an odd address")
                out += encode(statement, pc, table).to_bytes(2, "big")
        except AsmError as error:
            raise AsmError(f"line {number}: {error}") from error
        pc = origin + len(out)
    return bytes(out), table


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("--origin", type=lambda v: int(v, 0), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data, symbols = assemble(args.source.read_text(), args.origin)
    args.out.write_bytes(data)
    for name, value in sorted(symbols.items(), key=lambda kv: kv[1]):
        print(f"0x{value:08X} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
