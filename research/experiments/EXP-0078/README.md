# EXP-0078: Secret characters' win quotes, endings and partner lines in English

Task: SPECIAL-003
Status: DONE
Confidence: CONFIRMED (compiler checks, source hashes, arcade identity of the
replaced dialogue records; seen in play from a cold boot for slot 20)

## Observation

`EXP-0077`: official English exists for Shadow's, U.S. Agent's and Mephisto's
win quotes and for every secret slot's partner lines. Metal Zangief's and Dark
Sakura's own quotes and all secret ending pages have only substitutes.

## Hypothesis

The existing pipeline can carry the official parts unchanged, and new
translations can replace the rest within the quote font's space.

## Controlled Change

Two generator options (both release references):

- `--secret-roster data/text/secret_roster.json`: slots 22-24's win quotes,
  official English (record `k` = entry `remap[k]`, as the roster);
- `--secret-translations data/translations/secret_characters.json`: new
  English for `MC14` `0xCCEC` and `MC15` `0xBCB0` (16 records each) and the
  `ME.PAC` ending pages at `0x4254` (5), `0x43D0` (3), `0x44B4` (6) and
  `0x467C` records 3-5; plus the official partner lines (`MC13` records 56-67,
  108-119) and the name entries for slots 20-25.

## Prediction

Every compiler check true; the replaced `MC13` records equal the arcade
Japanese; the font fits.

## Inputs and Provenance

- Saturn image (manifest hashes); `MC*.PAC` extracted to
  `local/special003/mc/`.
- Arcade `mshvsfu`, `mshvsf`, `mshvsfj` (`local/arcade_roms/mshvsf/`).
- Translations: by Claude from the Saturn's own Japanese records, rendered
  with the quote font (`local/special003/jp_*.png`); no official source.

## Tools and Environment

`tools/reference/roster_pairing.py`, `tools/text/quote_render.py`,
`tools/text/official_endings.py` (new `--secret-roster`,
`--secret-translations`, `secret_tables`, `spec_pairs`, `ending_spec
extra_slots`), `tools/reference/cps2_text.py` (digits and `0x0186`),
`tools/text/caption_compiler.py`. Python 3.12.13.

## Procedure

1. `roster_pairing` on slots 22-24 (all three arcade sets).
2. Render the Japanese records of `MC14`, `MC15` and the `ME.PAC` ending
   blocks; find the shared block's extent.
3. Translate; record each source record's SHA-256.
4. Generate and compile both variants; fit the font.

## Actual Result

- **Slots 22-24:** each Saturn table is byte-identical to its arcade Japanese
  slot; the English blocks are identical in all three arcade sets and present
  on the PS1 (`SELECT.BIN` `0x13DAC`, `0x140CC`, `0x143EC`). Shadow has two
  partner-name placeholders (records 12 and 14), dropped as the roster policy
  does.
- **Arcade codes:** two quotes use codes the decoder lacked: `0x0138` ("before
  9 am") and `0x0186` ("'Cause"). Digits are ASCII − 1 + `0x100` ("Level
  3" = `0x0132`); `0x0186` is an opening quote, drawn as the apostrophe.
- **Japanese sources:** `MC14` holds 9 distinct quotes (records 9-15 repeat
  0-6), `MC15` 8 (8-15 repeat 0-7). The `ME.PAC` ending blocks are
  contiguous: slot 20 `0x4254`-`0x43D0`, 21 `0x43D0`-`0x44B4`, 22
  `0x44B4`-`0x467C`, and the 23-25 block `0x467C`-`0x4844` (6 records; codes
  outside the font follow). Its records 0-2 are already English
  ("Congratulations! / You've defeated the game / with a secret character!");
  records 3-5 are Japanese developer leftovers (a "now in production" notice,
  a CalorieMate joke, a Shadaloo line), translated in case they are shown.
- **Dialogue:** `check_targets` passes with slots 20-25 included: the Saturn's
  `MC13` records 56-67 and 108-119 equal the arcade Japanese.
- **Font:** the first build was 656 bytes over (`207312` of `206656`).
  Choosing each translated line's half-cell shift against the pairs already
  in use cut the new pairs from 25 to 16 (56 bytes over); rewording three
  lines ("What?", "Noooo!!", "to him...") removed three more. US variant:
  524 pairs, 12 bytes spare; Saturn variant: 526 pairs, 16 bytes spare. All
  compiler checks true.
- **Release:** see the regression baseline and `release/README.md`
  (rebaselined with this change).

- **Live check** (2026-10-26, user play, US release image `de8b2e0d…`,
  `local/special003/play2/rec/shots/`): Arcade mode with Metal Zangief
  (Blackheart + Start) and Shadow (Dhalsim + Start), codes from the user's
  GameFAQs copy.
  - Fight 1 won by the user: Metal Zangief's translated win quote "I'm out
    of vodka... / No more fire breath..." (`f00009061`, `d0d5bf0f…`).
  - Boss via `ending_driver`: VS SHADOW / ZANGIEF vs CYBER-AKUMA; banner
    ZANGIEF / SHADOW / WIN; post-boss lines "You are worthy ZANGIEF." and
    "I say Good-bye to you, SHADOW." (official).
  - All five translated ending pages under the speaker label "Zangief"
    (`f00028631` `d307ca79…`, `f00028810` `7f67dd29…`, `f00029048`
    `dde9ecfe…`, `f00029285` `df5d93ff…`, `f00029516` `c6494ed7…`).
- **Driver:** the stage word read `0x0400` → `0x0401` in this run (not
  `0x06NN`); `--after-stage` now accepts any high byte below `0x10` and keeps
  it. Armed mid-fight, the old KO test fired in an ordinary fight, where
  `0x060F3E50` is player 1's vitality, and knocked out the player; the driver
  now waits for the vitality word to rise to full in a fight that starts
  after arming.

## Conclusion

**CONFIRMED:** the secret characters' quotes, endings and partner lines are in
English in both variants; slot 20's win quote, dialogue and ending were seen
in play. The other secret slots are checked offline (same pipeline, compiler
checks and source hashes).

## Uncertainty and Alternatives

- Whether the game shows the 23-25 block's records 3-5 is unknown.
- The font now has 12-16 bytes free: further text needs freed glyphs.
- The translations are not official text.

## Reproduction

```bash
./invenv.sh python -m tools.reference.roster_pairing --roster data/text/secret_roster.json \
  --saturn-dir local/special003/mc --driver local/mame_src/cps2.cpp \
  --archives local/arcade_roms/mshvsf/mshvsfu.zip local/arcade_roms/mshvsf/mshvsf.zip local/arcade_roms/mshvsf/mshvsfj.zip
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold m8_roster_gold_us
```
