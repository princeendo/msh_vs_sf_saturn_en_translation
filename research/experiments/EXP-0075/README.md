# EXP-0075: Boss fight unlocked from the start (`--unlock-boss-fight`)

Task: OPT-001
Status: DONE
Confidence: CONFIRMED (disassembly, controlled cold-boot RAM read, cold-boot
play)

## Observation

The user believed the title menu's "MECH-GOUKI NOW!!" ("CYBER-AKUMA NOW!!" in
the American-name variant) can only be selected after clearing Survival mode,
and asked for a build option that unlocks it, on by default.

## Hypothesis

A single flag, set by a Survival clear, gates the menu entry. Starting the game
with the flag set makes the entry selectable from a cold boot.

## Controlled Change

One byte of `MM.BIN`: offset `0x50E4` (`0x0601DBE4`), `E000` (`mov #0,r0`) →
`E001` (`mov #1,r0`).

## Prediction

- The word at `0x06017AB0` reads 1 once `MM.BIN` is loaded, and 0 in the
  unchanged image.
- On the SURVIVAL MODE row, L/R switches to CYBER-AKUMA NOW!!, and Start
  begins the boss fight.

## Inputs and Provenance

- Images: `build/regression/m8_roster_gold_us/build/image_a` (control,
  track 01 `db1ede9f…`); `build/opt001/test/image_a` (the same plus the one
  byte); `build/opt001/us/image_a` (generated with the option, track 01
  `3a32e364…`). The two option images differ from the control only at
  `MM.BIN` `0x50E5` (`00` → `01`).
- The user played the option image on 2026-10-26.

## Tools and Environment

`tools/sh2/disasm.py` on `MM.BIN` (base `0x06018B00`), patched Mednafen
1.32.1 agent, `tools/mednafen/session_recorder.py`, Python 3.12.13.

## Procedure

1. Find the menu tables from the strings at `0x24F03` and the code that uses
   them.
2. Cold-boot the test and control images, and read `0x06017AB0` every 600
   frames up to frame 7,264.
3. The user cold-boots the option image, opens the title menu, moves to
   SURVIVAL MODE, presses L/R (keyboard P in this configuration) and Start,
   and plays to the fight.

## Actual Result

- **Menu** (`MM.BIN` `0x24CA8`-`0x24EC0`): tables of 8-byte rows (x, y,
  highlight, `0xFF`, string pointer), indexed by the menu state
  `0x06017C28` through the pointer array `0x0603D750` (0 = PRESS START, 1-4
  = the four modes, 5 = the Survival row as MECH-GOUKI NOW!!). After each
  table, `(button mask, next index | action)` pairs drive navigation
  (`0x0603D5A0`). From SURVIVAL MODE (3), mask `0x88008800` (L/R) goes to 5;
  from 5 it goes back to 3; Start/A on 5 give actions 8/9.
- **Gate** (`0x0603D644`): if the word at `0x06017AB0` is 0 and the next index
  is 5, the index is forced to 3. The word is cleared by the initialiser
  (`0x0601DBE2`) and set to 1 by `0x06098A1A` when two saved-data bytes
  (`0x0601801C`, `0x06018024`) say so; no other code refers to it.
- **RAM:** the test image reads `00000001` from frame 2,464 (when `MM.BIN`
  is resident) to 7,264; the control reads `00000000` throughout.
- **Play** (`local/opt001/rec/shots/`): `f00004663` (`04d8cadd…`) the
  menu shows ARCADE MODE / VERSUS MODE / **CYBER-AKUMA NOW!!** (highlighted)
  / OPTION MODE (`menu_zoom.png`); then character select (Ryu, Akuma), the VS
  screen AKUMA / RYU vs CYBER-AKUMA (`f00005881`, `b454fbd0…`), and the fight
  (`f00006353`, `e53529f0…`).
- **Build option:** `official_endings --unlock-boss-fight` (default on;
  `--no-unlock-boss-fight` turns it off) adds the expect-checked patch
  `UNLOCK_BOSS_PATCH`. The release references take the default; `end010`,
  `m8_roster` and `m8_roster_credits` pass `--no-unlock-boss-fight` and keep
  their hashes.

## Conclusion

**CONFIRMED:** the boss fight is gated by the word at `0x06017AB0`, set by a
saved-data condition; starting it at 1 makes MECH-GOUKI NOW!! / CYBER-AKUMA
NOW!! selectable from a cold boot, and the boss fight runs.

## Uncertainty and Alternatives

- The saved-data condition behind `0x06098A1A` is assumed to be the Survival
  clear (the user's report); it was not traced.
- L/R are mapped to the keyboard's P key in this Mednafen configuration.

## Reproduction

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --out local/opt001/m8_roster_gold_us.json \
  --roster data/text/m5_roster.json --with-win-quotes --glyph-style credits \
  --caption-palette gold --ui-english --names us --attract-captions
./invenv.sh python -m tools.text.caption_compiler local/opt001/m8_roster_gold_us.json \
  --candidates data/text/font_candidates.json --out-dir build/opt001/us
```
