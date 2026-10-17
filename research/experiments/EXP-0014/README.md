# EXP-0014: Stock Debugger Write, Revert, and Write-Breakpoint Workflow

Task: `EMU-011`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

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

Run on 2026-10-17 in one cold launch:

- process 57446;
- log `local/mednafen/logs/emu011-exp0014.log`, reporting `T-1238G`, area `J`,
  and `Cart: 4MiB Extended RAM`.

Pre-run hashes matched for the source manifest (13 components), the binary, both
BIOS aliases, the state A slot, and both patch files.

### Registers (step 3, user screenshot)

The CPU view lists:

- **SH-2 CPU registers:** `PC`, `RPC`, `PID`, `PIF`, `EP`, `R0`-`R15`, `SR`, `GBR`,
  `VBR`, `MACH`, `MACL`, `PR`.
- **On-chip and device registers:** DMA (`DMAOR`, `SAR`, `DAR`, `TCR`, `CHCR`),
  division, timer, interrupt, SCU, VDP, and CD registers.

The CPU view's memory pane showed `AA` for every byte at `0x06004000`. The stock
source's Saturn `DBG_MemPeek` is a stub returning `0xAA`, so that pane is not a
usable memory reader. Use the memory editor (`Option+3`) instead.

### Write, read-back, revert (steps 4-10)

The first attempt at step 6 failed. A long filename was most likely mistyped (the
error text was not recorded). The retry used byte-identical short copies `p.bin`
and `o.bin` (same SHA-256 as `re012-aiu-patched.bin` and `re012-aiu-original.bin`).

| Dump (ignored, `local/mednafen/dumps/`) | Time | Size | SHA-256 | Equals |
| --- | --- | ---: | --- | --- |
| `emu011-before.bin` | 13:15:34 | 1,140 | `78fd5a38c1e545ca04a6bf3d5f460c57d100821c2a7a8d35d20345cb083ebce3` | original table |
| `emu011-after-patch.bin` | 13:18:10 | 1,140 | `08a1a3aa1d9d759ff9dc849e227fa2bf79df6175f49cf37ca8453466c0ab06bf` | `p.bin` (`cmp` identical) |
| `emu011-after-revert.bin` | 13:19:00 | 1,140 | `78fd5a38c1e545ca04a6bf3d5f460c57d100821c2a7a8d35d20345cb083ebce3` | `o.bin` (`cmp` identical) |

The before and after-patch dumps differ in 79 bytes: 45 two-byte writes, some of
whose high bytes were already `0x08`. The live table equals the `EXP-0008`-validated
extraction of state A.

### Write breakpoint (steps 11-15)

`Shift+W` with `060ED80A-060ED8A1 260ED80A-260ED8A1` fired during a replay from
state A after the KO. The debugger opened by itself. The quote text was **not yet
visible**. Values read from the user's screenshot (some digits may be misread from
the debugger font):

- PC `060AF8C6`, highlighted `mov.w r0,@r6`; RPC `060AF8CA`, PR `0604CA24`.
- R1 `00005000`, R6 `060ED80A` (one digit is unclear but lies in the breakpoint
  range), R7 `060ED900`, R8 `002091FA`.
- The preceding listing includes `mov #76,r0` (twice), `add #2,r8`, and a
  literal-pool load `! 0x5000` followed by `add r1,r0`.

R7 equals the pointer seen just before the buffer in `EXP-0013`. R8 points into the
WRAM-L quote table (`0x002091F8` + 2). `#76` equals the observed record size, and
`0x5000` equals the observed buffer flag.

## Conclusion

`CONFIRMED` for the tested scope:

- `L` writes a prepared file into Low Work RAM while frozen.
- `D` reads back exactly the written bytes.
- Loading the original restores them exactly.
- CPU write breakpoints on the WRAM-H quote buffer fire with the debugger hidden,
  before the quote is drawn, and show the writing instruction and registers.

`SUPPORTED` (not confirmed): the code at `0x060AF8C6` builds the WRAM-H buffer from
the WRAM-L table, reading through R8 and using the 76-byte record stride and the
`0x5000` flag. That predicts the `EXP-0015` mutation will be visible.

## Uncertainty and Alternatives

- Not tested: read breakpoints, PC breakpoints, memory-editor edit mode, and `P`
  pokes. The CPU-view memory pane is unreliable (`0xAA` stub).
- Whether breakpoints catch DMA writes remains unknown. This write was a CPU store.
- Register values were transcribed from a screenshot; the screenshot image is not
  retained in the repository.

## Reproduction

Follow the Procedure, using the inclusive form `000091F8 0000966B <file>`. Short
copies `p.bin` and `o.bin` reduce typing errors. Verify with `shasum -a 256` and
`cmp` against `re012-aiu-*.bin`.
