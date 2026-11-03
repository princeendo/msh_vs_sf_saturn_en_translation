# EXP-0114: GRAMMAR FIXES switch, and a saved slot of its own (OPT-006)

Task: OPT-006 (and a correction to OPT-005)
Status: DONE (cold boot, unattended; checkpoint for the menu); the user's
session follows
Confidence: CONFIRMED (cold boot and checkpoint)

## Observation

- `TXT-004`'s fixes touch 40 places: CONTINUE? hint pages in `MM.BIN`, and
  win quotes, partner lines and endings in nine MC PACs and `ME.PAC`.
- The NAMES switch (`EXP-0112`) has 42 places. A four-variant diff
  (`EXP-0106`'s specs) found **no place in both**, so each place depends on
  one setting.
- **Correction:** NAMES used `0x06017AB4` as "saved and unused"
  (`EXP-0105` HYPOTHESIS, from pointer literals only). `EXP-0089` had
  already found it is the game's Mech-Gouki unlock: a MECH-GOUKI NOW!!
  clear sets it, and any nonzero value lets character select give
  Mech-Gouki. So:
  - in the user's `EXP-0113` session, NAMES SATURN also set that unlock on
    the test image's save;
  - a save that already had the unlock would read as NAMES SATURN, and
    switching to AMERICAN would clear the unlock.

  Nothing of this was pushed.

## Hypothesis

1. The site table can carry a setting bit per site (1 NAMES, 2 GRAMMAR),
   with both settings as bits of one value.
2. **The P1 button struct's second long `0x06017ADC`** is saved (inside the
   `0x80` block) and never read:
   - the in-game mapping `0x0601A618` starts with `add #8,r10`;
   - both BUTTON CONFIG row tables use offsets 8-36;
   - no code refers to `0x06017ADC`;
   - only the Options entry init (`0x0601DCA6`) writes it, with a pointer.

   The two bits can live in a tail variable, mirrored there each frame
   with a 16-bit marker (`0x4E53`), and adopted from there after a load.

## Controlled Change

- **`names_switch`:** `Site.switch` and the table's setting field;
  overlaps between a NAMES and a GRAMMAR site in one file are refused.
- **`caption_compiler`:**
  - reads `grammar_switch` entries as bit 2;
  - finds each alternate record's own base table: `MC13.PAC` has three
    tables at `0xA06C` with different placeholder rules, and record 42 was
    refused until the lookup used the record too.
- **`official_endings --grammar-switch FIXES`:** diffs the official spec
  with the `--fix-grammar FIXES` spec. The sub-menu has 4 rows and a 12 KiB
  tail.
- **`data/opt004/submenu.s`:**
  - NAMES and GRAMMAR FIXES are bit rows on the tail variable `switches`;
  - `vblank` mirrors it to `0x06017ADC` as `0x4E53xxxx`, adopts a marked
    value it did not write, and applies each site by its bit.

## Prediction

- Each bit switches only its own sites, both ways.
- The rows toggle their own bit.
- `0x06017AB4` is no longer touched.

## Actual Result

- **Image** `build/opt006/release2`:
  - 82 sites (32 in character slots);
  - payload 11,056 bytes at `0x027BC6A0`;
  - 592 pairs, 239 kanji sacrificed.
- **Cold boot** (`EXP-0112/switch_watch.py --bit 1/2 --reserve 12288 --rows
  4`): the setting was written as a save load would leave it, `0x4E530001`
  or `0x4E530002` at `0x06017ADC`.
  - NAMES: 26 resident sites American → Saturn → American.
  - GRAMMAR: the 5 resident hint pages official → fixed → official.
  - The ending sites were untouched (not loaded).
- **Checkpoint menu** (`EXP-0109/menu_drive.py --memfix`):
  - the sub-menu shows BOSS FIGHT, COMBO GAUGE, NAMES and GRAMMAR FIXES;
  - NAMES SATURN with GRAMMAR FIXES ON (`08-right.png`), then NAMES
    AMERICAN with GRAMMAR FIXES still ON (`10-left.png`).

## Conclusion

**CONFIRMED (cold boot, checkpoint):**
- the two settings are independent bits;
- each switches only its own sites, both ways;
- they are taken from the saved slot `0x06017ADC` after a load.

The game's Mech-Gouki unlock is no longer used.

## Uncertainty and Alternatives

- **BACK UP across a real power cycle** was not run (the user's session).
  The adoption path was exercised by writing the marked value directly.
- **The ending's sites** need a player.
- **`0x06017ADC` unused** rests on the code read above, not on a write log.

## Reproduction

```bash
R=build/opt006/release2
./invenv.sh python research/experiments/EXP-0112/switch_watch.py \
  "$R/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" $R/files/MEMFIX.PAC \
  local/opt006/switch2_bit2 --bit 2 --reserve 12288 --rows 4
./invenv.sh python research/experiments/EXP-0109/menu_drive.py \
  local/loc006/play/rec/states/f00003213.mcs local/opt006/release2.json \
  "$R/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" local/opt006/menu2 \
  --memfix $R/files/MEMFIX.PAC 20 up:15 up:15 ac:40 down:20 down:20 right:20 down:20 \
  right:20 up:20 left:20 start:40
```
