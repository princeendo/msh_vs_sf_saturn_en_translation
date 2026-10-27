# EXP-0080: The CONTINUE? screen's hints in English

Task: UI-004
Status: DONE
Confidence: CONFIRMED (glyph match and disc search; compiler checks; seen in
play from a cold boot)

## Observation

- `EXP-0078`'s play-test (`local/special003/play2/rec/shots/f00014000.png`,
  `3fa9e054…`) shows a two-line Japanese box under the CONTINUE? countdown:
  "中P中K同時押しで待機中のパートナーが / 援護攻撃を出すヴァリアブルアシストだ！"
  (press MP+MK together and the waiting partner makes a support attack: the
  Variable Assist).
- Two lines of 19 cells, the shape of a win-quote record (`EXP-0013`).

## Hypothesis

The hint is a 38-code quote-font record in a table on the disc, and the
official US releases have English for it.

## Controlled Change

None for the source search (read-only). The build adds one table to the
release specs (below).

## Prediction

The box's VDP1 cells match quote-font codes; the code sequence occurs once in
a disc file, inside a table of hint records; the US arcade or the PS1 US holds
English hints.

## Inputs and Provenance

- Saturn image (manifest hashes); `MM.BIN` `103a3d1d…`, `MEMFIX.PAC` from
  `local/end010/disc/`.
- State `local/special003/play2/rec/states/f00014068.mcs` (`4e4aabbb…`),
  extracted with `tools/memory/mcs_extract.py` (VDP1 VRAM, WRAM-H, cart RAM;
  `local/ui004/dump_14068/`).
- Arcade `mshvsfu`, `mshvsf`, `mshvsfj` (`local/arcade_roms/mshvsf/`) and
  their text runs (`local/arcade_text/`); PS1 US image
  (`local/disc_images/mshvsf_ps1_us/`).

## Tools and Environment

`tools/memory/vdp1_sprites.py`, `tools/text/glyph_match.py`,
`tools/text/quote_render.py`, `tools/reference/cps2_text.py`,
`tools/disc/iso9660.py`. Python 3.12.13.

## Procedure

1. List the VDP1 sprites of the state; the box is the 38 sprites with color
   word `0x6010` at VDP1 y 178 and 194.
2. `glyph_match --color-word 0x6010`: decode each cell's code.
3. Search `wram_h.bin`, `cart_ram.bin` and every disc file (PACs raw and
   decoded) for the code sequence.
4. Render the table around the hit with the quote font; find its extent and
   the pointers to it.
5. Search the three arcade programs for the Saturn's records, and their text
   runs and every PS1 US file for English hint wording.

## Actual Result

- **Codes:** all 38 cells match a font code exactly (cells 14 and 17 match
  two codes with the same cell, `0x08A8`/`0x093D`).
- **Location:** the sequence occurs once in RAM, WRAM-H `0x06095414`, and
  once on the disc, `MM.BIN` `0x7C914` (so `MM.BIN` is loaded at
  `0x06018B00`). It is record 12 of a 16-record table at `MM.BIN`
  `0x7C584`-`0x7CA44`, after a run of `0x9999` padding and before the story
  dialogue records (the table `TXT-001` tracks). `MM.BIN` holds the table's
  bus address (`0x06095084`) at `0x96890`, `0x96BAC`, `0x96BB0` and
  `0x96BB4`.
- **Content:** gameplay hints: Aerial Rave, Advancing Guard, Variable
  Combination, Variable Counter, Variable Attack, Hyper Combo, recovery,
  Super Jump (two), tagging, throw escape, dash, Variable Assist, and the
  universal LP+LK launcher. Records 13 and 14 repeat records 2 and 9.
- **Arrows:** the hints draw joystick motions with quote-font codes `0x01E2`
  ↑, `0x01E4` →, `0x01E5` ↘, `0x01E6` ↓, `0x01E7` ↙, `0x01E8` ← (rendered,
  `local/ui004/arrows.png`).
- **Correction (`EXP-0085`):** the arcade does hold official English hints,
  at `0x2239FC` (12 hints, two 100-byte records each), used for non-Japanese
  regions. The search below missed them. The cause is not established;
  HYPOTHESIS: it searched for wording such as "Aerial Rave", while the
  arcade says "Air Combo".
- **Official English (as first recorded):** none. The arcade programs hold the same Japanese
  table at `0x2139AC` in all three sets (records 1-15 byte-identical to the
  Saturn's; record 0 differs). No arcade text run and no PS1 US file holds
  English hint wording, and the PS1 US has no copy of the Japanese records.

## Conclusion

- **CONFIRMED:** the hints show in English in play, arrows included.
- **CONFIRMED:** the CONTINUE? hint is drawn from a 16-record quote-font
  table at `MM.BIN` `0x7C584`.
- **CONFIRMED:** no official English exists in the US arcade or the PS1 US;
  the hints need a new translation.

## Build

- `data/translations/continue_hints.json`: new English for the 16 records,
  each tied to its Japanese source by SHA-256; joystick arrows kept as the
  game's own glyphs.
- `caption_compiler`: a line may hold `{XXXX}`, a font code kept as is in a
  whole cell; a kept code is never a pair or a sacrifice. Pair-font
  punctuation adds `+` `:` `(` `)` (`0x08CA`, `0x08AE`, `0x08C0`, `0x08C1`,
  chosen by glyph shape).
- `official_endings --ui-translations`: adds the table to the spec, in both
  release references.
- The release style draws pairs with the staff-credits glyphs, so `+`, `(`
  and `)` were added there too (`0x1FE`, `0x1F9`, `0x1FF`, by glyph shape;
  `:` was already `0x250`). The arrows `0x01E2`-`0x01E8` are credits-font
  glyphs themselves.
- **Result:** all nine regression references pass; every compiler check is
  true, including `MM.BIN` `changes_only_in_target_cells`. Both variants use
  577 pairs (14 and 90 bytes spare); the retired-kanji census now finds 281
  candidates. `m8_roster_gold`: spec `e491ea36…`, track 01 `3ee38981…`, patch
  `abd03143…` (2,933,166 bytes); `m8_roster_gold_us`: spec `37fe1cf2…`, track
  01 `103d40a5…`, patch `46832e4d…` (2,934,610 bytes).
- **Fixed on the way:** the first rebuild failed on the credits font's
  missing `+`; a `| head` pipe hid the failure from `set -e` (the script now
  uses `pipefail`).

## Live Check

2026-10-26, user play, US release image `103d40a5…`,
`local/ui004/play/rec/shots/`: Arcade mode, two lost fights, both countdowns
run out.

- First CONTINUE?: record 0 in English, gold letters, with the game's ↑ arrow
  (`f00009819`, `6e47013d…`).
- Second CONTINUE?: "Low on vitality? Tag your partner! / While resting, some
  vitality returns." (record 9 or its repeat 14; `f00018023`, `fa392517…`).
- Each hint stays unchanged for its whole countdown (box pixels compared
  across the recorded frames).

## Uncertainty and Alternatives

- What picks the hint is unknown (two samples, two different hints).
- The new `+`, `:`, `(` and `)` glyphs were not on screen in this run.
- The arcade record 0's difference from the Saturn's is not examined.
- The translation is not official text.

## Reproduction

```bash
./invenv.sh python -m tools.memory.mcs_extract local/special003/play2/rec/states/f00014068.mcs \
  --out-dir local/ui004/dump_14068 --region vdp1_vram --region wram_h --region cart_ram
./invenv.sh python -m tools.text.glyph_match local/ui004/dump_14068 --color-word 0x6010
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
```
