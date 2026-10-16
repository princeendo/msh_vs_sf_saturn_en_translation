# EXP-0015: Live Mutation of the Ryu Quote Table

Task: `RE-012`
Date: 2026-10-15
Status: BLOCKED (requires `GATE-M0`, which requires `EMU-011` / `EXP-0014`)
Confidence: HYPOTHESIS

## Observation

`EXP-0013` found that each displayed Ryu quote matches exactly one 38-cell record of
16-bit codes in a WRAM-L table. The table is 15 records of 76 bytes at
`0x002091F8-0x0020966B`, identical in every state including pre-KO state A.

Kana codes follow `0x0800 + (Shift-JIS second byte − 0x9F)`. All 11 observed quotes
(Q1-Q11) map to records in this table. Quote selection after a checkpoint varies
(`EXP-0009`).

## Hypothesis

The quote screen builds its text from this WRAM-L table. Changing a record's codes
before the quote screen changes the displayed glyphs to the glyphs for the new
codes.

## Controlled Change

There is exactly one variable: in state A (slot 5), line-1 cells 0-2 of all 15
records are set to `0801 0803 0805`. This is 45 two-byte writes, made by loading
`re012-aiu-patched.bin` into workraml `000091F8-0000966B` while frozen. Every other
byte of the range is unchanged. Changing every record makes the prediction
independent of which quote is selected.

The control is the same procedure, loading `re012-aiu-original.bin` (no byte
changes).

## Prediction

- **Patched runs.** The top-left three cells of line 1 show `あ い う`, whichever
  quote appears. The rest of the quote is unchanged. Most records have blank cells
  there. Records 0 and 4 lose three characters, records 8 and 10 lose two, and
  record 1 loses one.
- **Control runs.** The quote is shown normally.
- **If the cells change to glyphs other than あいう:** the table drives the display,
  but the kana formula is wrong for あ/う.
- **If nothing changes:** this table is not the display source, for example because
  it is reloaded or a different copy is used. The hypothesis is then `DISPROVEN`.

Run both the patched and control procedures at least twice, from a clean reload of
state A each time.

## Original and Modified Bytes

All 45 writes are listed in ignored `local/mednafen/dumps/re012-aiu-manifest.json`
(SHA-256 `2df36119…d125`). For record `r` (0-14), with base
`0x002091F8 + 76·r`:

- offsets `+0`, `+2`, `+4` change from their original codes to `0801`, `0803`, and
  `0805` respectively;
- records 2, 3, 5, 6, 7, 9, 11, 12, 13, and 14 have `0020` (blank) in all three
  cells;
- record 1 has `0020` in cells 0-1;
- records 8 and 10 have `0020` in cell 0 only;
- records 0 and 4 have text in all three cells.

Purpose: a visible, quote-independent marker.

## Procedure (after `EMU-011` is `DONE`)

1. Launch from the repository root. Press `5`, then `F7`, then `Option+A`.
2. Press `Option+D`, then `Option+3`. Select Low Work RAM, press `L`, and enter
   `000091F8 0000966B local/mednafen/dumps/re012-aiu-patched.bin`. Press `D` and
   dump the same range to `re012-run1-loaded.bin` to verify.
3. Press `Option+D` to close the debugger, then `Option+R`. KO Vega with Ryu and
   wait for the full quote.
4. Press `Option+A`, then select slot 9 and `F5` to save the visible result, then
   `F9`. Press `Option+R`.
5. Repeat steps 1-4 once more (run 2, slot 9 again after recording it).
6. Run the control twice with `re012-aiu-original.bin`.

## Actual Result

Pending.
