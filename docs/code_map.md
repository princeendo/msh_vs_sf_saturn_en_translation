# Code Map

## Status

No executable regions, functions, call sites, or code addresses have been confirmed
for the target release.

## SH-2 Debugger Interpretation

This is a processor-level checklist, not a target code map. The supporting Hitachi
manuals and exact sections are recorded in `docs/references.md`.

- Record `R0` through `R15`, `SR`, `GBR`, `VBR`, `MACH`, `MACL`, `PR`, and the
  debugger's displayed program counter when those values matter to a trace. `R15`
  participates in exception stacking and `PR` holds subroutine return state.
- Decode the instruction's documented addressing mode before calculating a memory
  operand. Byte and word loads sign-extend into the 32-bit destination register;
  immediate extension depends on the instruction.
- Treat the manual's architectural `PC` convention separately from the debugger's
  disassembly cursor or register label. Establish Mednafen's presentation by test.
- Account for delay slots. A delayed branch executes the following instruction before
  control reaches the branch target, and a control-transfer instruction in that slot
  is illegal.
- Distinguish instruction-fetch, data-read, and data-write events. The SH7604 hardware
  can compare those cycle types, but stock Mednafen's breakpoint semantics remain to
  be tested.
- Treat CPU, DMA, cache, and interrupt activity as competing explanations when a
  memory value changes. A CPU breakpoint alone does not prove that the CPU performed
  the transfer.

The exact debugger register presentation, address spaces, alias treatment, breakpoint
timing, and use of the SH7604 user-break controller remain unobserved until `EMU-010`
and `EMU-011`.

## Recording Rules

Add an entry only when evidence identifies executable behavior in the exact hashed
target. Each entry must record:

- address space and measured address or file offset;
- source-image and relevant artifact hashes;
- function or region behavior demonstrated by the experiment;
- original bytes or instructions when legally recordable as minimal factual data;
- control-flow or data-flow evidence;
- experiment identifier and reproduction procedure;
- confidence and unresolved alternatives.

Use neutral labels until behavior is confirmed. Do not copy symbols, addresses, or
structure from XvSF, CPS-II, PlayStation, or another Saturn title.
