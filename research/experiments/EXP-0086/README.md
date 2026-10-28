# EXP-0086: The arcade's official English CONTINUE? hints, paged

Task: UI-006
Status: DONE
Confidence: CONFIRMED (forced trial; cold-boot play check)

## Observation

- **English hints exist:** the arcade holds official English CONTINUE? hints
  at `0x2239FC` in every set (`EXP-0085`).
- **The user decided (2026-10-27)** to use them instead of `UI-004`'s new
  translations: "fit them into the Saturn box".
- **The arcade shows each hint as two pages** (US set, `local/ui006/arcu1`):
  - record 6 was read at frame 11,782 (page 1: "←↙↓ HP+HK while / guarding
    for the Counter!");
  - record 7 was read 383 frames later at 12,165 (page 2: "Your partner
    will / assist you.").
  - The Japanese set never pages (`EXP-0085`, run 2), and neither does the
    Saturn: the same hint was on screen at countdown 8 and 4 in the
    `EXP-0081` play session (`f00020217`, `f00020640`).
- **Page code (arcade):** the hint object's first state (`0x07011A`) tests
  the region word (`-$3370,A5`). Outside Japan, when its `0x180`-frame timer
  ends, it adds 1 to the record index and redraws (`0x07012A`). The creator
  (`0x07041A`) maps the random index through `0x070448`: `0,2,…,22,0,2,4,6`.
- **The Saturn kept both steps behind the same region test (`0xCC90`):**
  - **creator:** `0x060AF33E`-`0x060AF350`; `bt` at `0x060AF348` (`MM.BIN`
    `0x96848`) skips the map; the map is at `0x060AF3A0` (`0x968A0`);
  - **handler:** `0x060AEE84`-`0x060AEEAA`; `bt` at `0x060AEE8C` (`0x9638C`)
    skips the page step.
  - The display keeps the Japanese layout, two lines of 19 cells per
    76-byte record (`0x060AF6FC`).

## Fit

- **One page does not fit:** every hint is 72-103 characters (both pages).
  The Saturn box is two lines of about 38 characters with two letters per
  cell, so each hint needs three lines.
- **There is no room for more records:** paging needs two records per hint.
  The 16 hint records are followed by story records 16-47, and every
  `0x9999` padding run in `MM.BIN` is overwritten in RAM during play (work
  memory; RAM dumps from states `f00019422` and `f00020280`).
- **User decision (2026-10-27): 8 hints, exact, 2 pages.**
  - The 16 records take the arcade's English records 0-15, which are hints
    0-7, page 1 and page 2, word for word with the arcade's line breaks
    (each 25-cell arcade line becomes one Saturn line).
  - Hints 8-11 are left out.

## Hypothesis

Two 2-byte `nop`s and a new index map make the Saturn page its hints as the
arcade does. Hints 0-7 then show both pages, in English, in the release.

## Controlled Change

`tools/text/official_endings.py --official-hints` (replaces
`--ui-translations data/translations/continue_hints.json` in the release
references):

- **Records 0-15 at `MM.BIN` `0x7C584`:** the arcade's English records 0-15,
  read cell by cell from the ROM at build time (`en_cell_lines`), with code
  `0x0129` drawn as "+". Arrows keep their codes (`0x01E2`-`0x01E8`), which
  are the same in the Saturn's quote font. The Saturn records must be the
  Japanese hints (records 1-15 equal to the arcade's, record 0 by hash).
- **Patches:**

  | `MM.BIN` | Bus | Original | New | Purpose |
  | --- | --- | --- | --- | --- |
  | `0x96848` | `0x060AF348` | `8903` (`bt`) | `0009` (`nop`) | always map the random index |
  | `0x968A0` | `0x060AF3A0` | `00 02 … 16 00 02 04 06` | `00 02 … 0E 00 02 … 0E` | index map: hints 0-7, each 2/16 |
  | `0x9638C` | `0x060AEE8C` | `8910` (`bt`) | `0009` (`nop`) | page to the next record after `0x180` frames |

## Prediction

- Both release references rebuild deterministically.
- On the Saturn, each of hints 0-7 shows its page 1 under CONTINUE?. After
  `0x180` frames, page 2 replaces it, in English with the right arrows.

## Actual Result

### Build

- **Specs (`local/ui006/gen.sh`):** `--official-hints` in place of
  `--ui-translations`. Saturn names `74641239…`, American names `1c5d5b72…`.
  Records 0-15 equal the arcade's English pages 0-15, with code `0x0129` as
  "+".
- **References:** `m8_roster_gold` and `m8_roster_gold_us` were rebaselined.
  All nine references pass.

| Variant | Track 01 | xdelta | `.ssp` |
| --- | --- | --- | --- |
| Saturn names | `93965dd4ea6577a6410277b4734f0315842518b85aaf9f0decb6f07b7531da41` | 641,843 bytes, `c430a4fa…` | 559,332 bytes, `3b07c3ba…` |
| American names | `b978085db3aa3e5ac7e8c1ef463b1b4d65c0c50b8d89a8b5e6903323f19171b5` | 643,267 bytes, `0886a018…` | 559,184 bytes, `34058d36…` |

- Both patch formats round-trip. `saturn-patcher-egui` gives both track 01
  hashes from the `.ssp` files.

### Saturn trial (`verify_hints.sh`)

- **The checkpoint:**
  - state `local/special004/play/rec/states/f00019422.mcs` (Apocalypse is
    about to beat the player);
  - its cart RAM font replaced with the built US image's font (`MEMFIX.PAC`
    entry 4, `0x32740` bytes at `0x0278CF60`) by the new
    `tools/memory/mcs_patch.py`.
- **After loading, written to work RAM:**
  - the built `MM.BIN` records 0-15;
  - the two `nop`s;
  - an index map of sixteen `2k` bytes, which forces hint k.
- **Screenshots:** `write_trial` with the new `--shot-at`, at frames 850 and
  1,180.
- **Result:** all 32 writes survived. Every hint showed page 1 under
  CONTINUE?, and page 2 had replaced it by frame 1,180 (countdown 7 → 4):

| Hint | Page 1 (`f850`) | Page 2 (`f1180`) |
| --- | --- | --- |
| 0 | "When Air Combo starts to / move hits the opponent," `775fdded…` | "put the lever ↑ to chase / him and execute a combo!" `3c5eec27…` |
| 1 | "Push PPP while guarding / for the Advancing Guard." `fdd5e017…` | "Push the opponent back!" `0b7be3fa…` |
| 2 | "When Level 3 or higher, / enter ↓↘→ HP+HK" `3881d378…` | "for the Cross-Over / Combination move!" `aa5deb00…` |
| 3 | "←↙↓ HP+HK while / guarding for the Counter!" `ceb9ef97…` | "Your partner will / assist you." `44680526…` |
| 4 | "HP HK simultaneously for / the Cross-over Attack!" `d4055757…` | "You can switch / your character any time!" `e840f0e6…` |
| 5 | "By charging the gauge / past level one," `5ff435ba…` | "you can do a Hyper Combo! / Make a comeback!" `903d578a…` |
| 6 | "←↙↓ P before landing / for the safe fall!" `49d1133f…` | "Outsmart your opponent!" `440b892d…` |
| 7 | "Enter ↓↑ or KKK for / a Super Jump!" `6a14530c…` | "You can attack infinitely / while doing a Super Jump!" `eb962224…` |

Erratum (2026-10-27): hint 2 page 1 read "Level 3" because of a digit-decoding
error. The arcade text is "Level 2" (`EXP-0090`). `TXT-005` (`EXP-0091`) fixed
it, and the corrected page shows "When Level 2 or higher," (`f88ba15b…`).

- **Glyphs:** all six arrows (`0x01E2`, `0x01E4`-`0x01E8`) and "+" render
  correctly. Contact sheet: `local/ui006/verify/sheet.png`.

### Cold-boot play check (2026-10-27, user at the controls)

- **Setup:**
  - US release image, track 01 `0f430c0a…` (built with `--story-lines
    --official-hints`);
  - your PS4 controller;
  - recorder `local/txt002/play2/rec`;
  - driver `tools/mednafen/continue_driver.py`. It forces the story-line
    branch and steps the hint map 0-7, one per CONTINUE?. It writes only
    `0x060AF228` and the 16-byte map.
- **Eight losses to the stage-1 CPU team** (Blackheart and Zangief):
  - **Story line:** every post-loss screen showed Blackheart's record 24 in
    English, "Now, a devil or a reaper... / which shall I introduce you to?"
    (`f00008493.png` `c0081ff0…`).
  - **Hints:** each CONTINUE? showed hints 0-7 in order, page 1 at countdown
    8 and page 2 by countdown 5. For example:
    - hint 0 `f00008731.png` `18a77987…` and `f00009019.png` `71cd2a4e…`;
    - hint 2 page 2 "for the Cross-Over / Combination move!" `027b645f…`;
    - hint 7 `f00064952.png` `d136d228…` and `f00065252.png` `1cfac482…`.
  - The driver log (`local/txt002/play2/driver.log`) records each hint's
    creation frame.
- **After Start, page 2 stays on the team screen until character select.**
  The user saw it on every continue. The US arcade does the same: MAME
  `mshvsfu`, coin and Start after page 2; its team screen still shows "Your
  partner will / assist you." (`local/txt002/play2/sheet_arcu.png`). So it is
  the arcade's own behaviour.
  - Not checked: whether the Japanese original keeps its single page there
    too. A comparison run mistimed its inputs.

## Conclusion

**CONFIRMED** (forced trial):
- With two `nop`s and a new map, the Saturn pages its CONTINUE? hints as the
  US arcade does.
- The release shows hints 0-7 of the arcade's official English, word for
  word, page 2 after `0x180` frames.
- `UI-004`'s new translations are no longer built (`--ui-translations` stays
  available).

## Uncertainty and Alternatives

- **Cold boot:** the cold-boot play check showed all eight hints. The page
  step was forced only through the map, never through the release's own
  random index.
- **Hints 8-11 are not shown** (the user's choice): quick air combo / switch
  when low, vitality and throw escape, dash, partner support. There is no
  free space for their records.
- **The CONTINUE? countdown can end before page 2,** as in the arcade.
- **Code shared with other text?** The page-step branch is in the hint
  object's handler. No other caller of that state was found.
  HYPOTHESIS: only hints use it.

## Reproduction

```bash
# Specs: the release options with --official-hints (see data/regression/
# reference_builds.json, m8_roster_gold*). Then rebuild and check:
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
# The eight hints on the Saturn (US image, play state of EXP-0081):
bash research/experiments/EXP-0086/verify_hints.sh
```
