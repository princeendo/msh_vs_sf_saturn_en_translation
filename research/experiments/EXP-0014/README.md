# EXP-0014: Stock Debugger Write, Revert, and Write-Breakpoint Workflow

Task: `EMU-011`
Date: 2026-10-15
Status: READY
Confidence: HYPOTHESIS

## Observation

`EXP-0007` confirmed debugger entry, CPU `S`/`R`, the address-space list, and `D`
dumps. Memory writes, register display, and breakpoints remain untested, and they
are required before the first live mutation (`GATE-M0`, as amended).

Source reading of stock 1.32.1 (implementation, not runtime evidence):

- **Load command.** The memory editor's `L` command reads
  `start end filename` (inclusive end) or `start +count filename`, then writes
  through `PutAddressSpaceBytes` (`src/drivers/memdebugger.cpp`). For `workraml`
  this writes the `WorkRAML` array directly (`src/ss/debug.inc`).
- **Write breakpoints.** `Shift+W` in the CPU view takes space-separated hex
  addresses or `A-B` ranges (`src/drivers/debugger.cpp`). They are checked against
  CPU writes (`src/ss/debug.inc`).

## Hypothesis

Three things hold for the stock debugger:

1. While frozen, `L` writes a prepared file into Low Work RAM, and a following `D`
   dump reads back exactly the written bytes.
2. Loading the original file restores the original bytes.
3. A write breakpoint on the WRAM-H quote buffer (`EXP-0013`) halts the CPU when a
   replay from state A reaches the quote screen.

## Controlled Change

- **Write test.** All writes happen while frozen with frame advance, and are
  reverted before any frame runs. No game behavior is observed in the write test.
- **Breakpoint test.** No memory is modified. The only addition is a breakpoint.

## Prediction

- **Write test** (each dump covers workraml `000091F8 0000966B`, 1,140 bytes):
  - The dump before any load has SHA-256 `78fd5a38…3ebce3`, equal to
    `re012-aiu-original.bin`.
  - The dump after loading `re012-aiu-patched.bin` has SHA-256 `08a1a3aa…ab06bf`.
  - The dump after loading `re012-aiu-original.bin` again has `78fd5a38…3ebce3`.
- **Breakpoint test.** With `060ED80A-060ED8A1 260ED80A-260ED8A1` set as write
  breakpoints, a replay from state A halts at or after the KO, before the quote is
  fully drawn. The CPU view shows the writing instruction's PC.

If the breakpoint never fires, either the buffer is written by DMA or via an
untested alias, or CPU write breakpoints do not trigger here. That would be
recorded as a limitation, not inferred away.

## Inputs and Provenance

- **State A:** slot 5, SHA-256 `ab60af86089a95750629396088932bfe30a66c0daff7681c1ae973d5fd91dce6`.
- **Patch files:** ignored `local/mednafen/dumps/`, built by `tools.memory.make_patch`
  from A's validated WRAM-L extraction:
  - `re012-aiu-original.bin`: 1,140 bytes, SHA-256
    `78fd5a38c1e545ca04a6bf3d5f460c57d100821c2a7a8d35d20345cb083ebce3`.
  - `re012-aiu-patched.bin`: 1,140 bytes, SHA-256
    `08a1a3aa1d9d759ff9dc849e227fa2bf79df6175f49cf37ca8453466c0ab06bf`.
  - `re012-aiu-manifest.json`: SHA-256
    `2df361197000d9dc2776f3ee05d7086bd495767ed1b5a00b97379a5450bed125`, listing all
    45 original and modified values.

## Procedure

Use left Option for Alt. Launch from the repository root as in `EXP-0007`.

Part 1, registers and write/revert (no frame runs while memory is modified):

1. Press `5`, then `F7` to load state A. Press `Option+A` to freeze.
2. Press `Option+D` to open the debugger. Record the register names shown in the
   CPU view.
3. Press `Option+3`. Use `.` to reach Low Work RAM.
4. `D`: `000091F8 0000966B local/mednafen/dumps/emu011-before.bin`
5. `L`: `000091F8 0000966B local/mednafen/dumps/re012-aiu-patched.bin`
6. `D`: `000091F8 0000966B local/mednafen/dumps/emu011-after-patch.bin`
7. `L`: `000091F8 0000966B local/mednafen/dumps/re012-aiu-original.bin`
8. `D`: `000091F8 0000966B local/mednafen/dumps/emu011-after-revert.bin`
9. Press `Option+D` to close the debugger, then `Option+R`. Press `5` and `F7` to
   reload A, discarding everything.

Part 2, write breakpoint:

10. Press `Option+D`, then `Option+1` for the CPU view. Press `Shift+W` and enter
    `060ED80A-060ED8A1 260ED80A-260ED8A1`.
11. Press `Option+D` to close the debugger. Press `5` and `F7`, then KO Vega with
    Ryu.
12. If the debugger halts, record the PC and the highlighted instruction (a phone
    photo is fine), and whether the quote is drawn yet.
13. Press `Shift+W`, clear the field, and press Return. Then press `R` and
    `Option+D`.

## Actual Result

Pending.
