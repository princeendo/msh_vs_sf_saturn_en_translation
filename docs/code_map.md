# Code Map

## Status

No executable regions, functions, call sites, or code addresses have been confirmed
for the target release.

## SH-2 Semantics Needed For Debugger Work

These are processor-level operating notes, not a target code map. They are supported
by the SH-1/SH-2 Programming Manual and SH7604 Hardware Manual recorded in
`docs/references.md`.

- Track the SH-2 general registers and programmer-visible special registers rather
  than treating a disassembly window as the complete machine state.
- Decode the documented operand addressing modes before interpreting an effective
  address or memory access.
- Account for delayed branch execution when relating a program counter, a branch
  instruction, and the next executed instruction.
- Treat exception and interrupt entry as a control-flow event involving the vector
  and status state described by the processor documentation.
- Distinguish CPU instruction/data accesses from DMA, interrupt-controller, cache,
  and other SH7604 peripheral behavior when explaining a breakpoint or memory change.
- Record the debugger's address space and any translation or aliasing explicitly;
  processor documentation does not establish a Saturn game address.

The exact debugger presentation, breakpoint timing, and emulator-specific treatment
of these semantics remain unobserved until `EMU-010` and `EMU-011`.

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
