# EXP-0018: Trace the Load of the Ryu Quote Table

Task: `DISC-001`
Date: 2026-10-17
Status: READY (needs the user at the keyboard and a new pre-load checkpoint)
Confidence: HYPOTHESIS

## Observation

- `EXP-0017` disproved verbatim or plain-text storage of the table on disc.
- The table (WRAM-L `0x002091AC-0x0020966B`) is absent at the title screen and
  present from the first fight onward.
- WRAM-H `0x06094FD8` changes from `00000000` (title) to `002091AC` (fights), inside
  a run of 4-byte entries that are either placeholders or WRAM-L addresses.
- The `EXP-0014` runbook confirms that CPU write breakpoints fire with the debugger
  hidden.

## Hypothesis

A CPU routine writes the table during the pre-fight load from a source buffer that
holds transformed data. A write breakpoint on the table catches that routine, and
its registers identify the source buffer.

## Controlled Change

None to memory. Only write breakpoints are added, during a load started from a
checkpoint taken before the table exists.

## Prediction

- With write breakpoints `002091AC-0020966B 202091AC-2020966B` set at the
  checkpoint, starting the match halts in a routine whose registers include a
  destination inside the table and a source pointer outside it. The source might
  be WRAM-H, WRAM-L, cart RAM, or a CD-block-related address.
- A second run with a breakpoint on `06094FD8-06094FDB` halts when the slot entry is
  written. The surrounding code identifies the loader that registers the table.

If no breakpoint fires, the table is written by DMA or another non-CPU path. That
would be recorded as a limitation (`docs/known_unknowns.md`).

## Procedure (to be expanded into a step table before the run)

1. **Checkpoint.** From a cold boot, go to arcade mode character select and pick
   Ryu and Ken. Before the fight loads, freeze with `Option+A`, save to slot 6
   (C2 is archived), and take an F9 screenshot. Verify by extraction that the
   table is absent.
2. **Run 1 (table writes).** Load the checkpoint. In the CPU view, set
   `Shift+W` to `002091AC-0020966B 202091AC-2020966B`, hide the debugger, and
   continue into the match. At each of the first three halts, record PC, R0-R15,
   and PR with a screenshot, pressing `R` between halts. Then clear the
   breakpoint.
3. **Run 2 (slot entry).** Reload the checkpoint and repeat with
   `06094FD8-06094FDB`.
4. **Dumps.** While halted at the first useful break, dump the memory around each
   source-pointer register with `D`. Paused-state dumps are allowed; do not load a
   state or reset while halted.

## Actual Result

Pending.
