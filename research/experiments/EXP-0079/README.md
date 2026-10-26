# EXP-0079: Norimaro's post-fight text and ending in English

Task: SPECIAL-002
Status: IN_PROGRESS (built and checked offline; live check pending)
Confidence: SUPPORTED (pairing, compiler checks, source hashes)

## Observation

- The user asked for Norimaro's post-fight text and ending in English
  (2026-10-26), not the attract-mode Norimaro screen.
- `docs/coverage_exceptions.md`: win quotes `MC11` slot 17; ending pages
  `ME.PAC` `0x3F5C` (5 records); dialogue `MC13` 50, 51, 102, 103. The US
  arcade's English page table points slot 17 at Dan's pages.
- RC-1/RC-2: the international ROMs hold Norimaro's English quotes.
- After `EXP-0078` the font had 12-16 bytes free.

## Hypothesis

Official English exists for Norimaro's win quotes and partner lines; his
ending needs a new translation; reclaiming kanji that only replaced records
use makes room in the font.

## Controlled Change

- `data/text/secret_roster.json`: slot 17 (official quotes, placeholders
  dropped).
- `data/translations/secret_characters.json`: `ME.PAC` `0x3F5C` records 0-4.
- `SECRET_SLOTS` adds 17 (dialogue and name).
- `caption_compiler.retired_kanji` (spec flag `retire_replaced_kanji`, set
  with `--secret-translations`): kanji used only by records the spec replaces
  join the font's sacrificial candidates, after the unseen kanji.
- `secret_tables` localizes names per variant (Cyber Akuma / Mech-Gouki).

## Prediction

Pairing identical to the arcade Japanese; the font fits; all checks true.

## Inputs and Provenance

Saturn image (manifest hashes); arcade `mshvsfu`, `mshvsf`, `mshvsfj`; PS1 US.

## Tools and Environment

`tools/reference/roster_pairing.py`, `tools/text/quote_render.py`,
`tools/text/official_endings.py`, `tools/text/caption_compiler.py`,
`tools/text/quote_census.py`. Python 3.12.13.

## Procedure

1. `roster_pairing` for slot 17 on the three arcade sets.
2. Render the Japanese ending (`ME.PAC` `0x3F5C`-`0x40D8`) and translate.
3. Build; enable the retired-kanji census; rebuild.

## Actual Result

- **Win quotes:** the Saturn table (`MC11` `0xA158`) is byte-identical to the
  arcade Japanese slot 17; record `k` pairs with English entry `k & 7`; the
  English block is unique to slot 17, identical in all three sets, and on the
  PS1 (`SELECT.BIN` `0x12E0C`). Placeholders in records 1, 3, 9, 10 and 15 are
  dropped.
- **Partner lines:** official English for slot 17 (`0x22226C`, records 17 and
  43).
- **Ending:** five Japanese pages, a mock epilogue (Norimaro beats
  Apocalypse and the boss, conquers the world, is remembered as a wicked king
  who now torments exam students through history books, "The End"),
  translated with the boss name in the US form and localized per variant.
- **Font:** the build was 657 bytes over. The retired-kanji census found 250
  kanji used only by replaced records; the US build used 8 of them
  (`0x0C51`, `0x0C55`-`0x0C5B`) and fits with 71 bytes spare (536 pairs). All
  compiler checks true; the dialogue records equal the arcade Japanese.
- **Fixed on the way:** `secret_tables` was called without the name variant,
  so the US build said "Mech-Gouki"; it now passes `--names`.
- **Release:** all nine regression references pass. `m8_roster_gold`: spec
  `1031e44f…`, track 01 `7859e93e…`, patch `fb8474ef…` (2,930,736 bytes);
  `m8_roster_gold_us`: spec `6e809c5a…`, track 01 `4a24ab67…`, patch
  `fbc93fb7…` (2,932,174 bytes). Saturn variant: 536 pairs, 22 bytes spare.
- **Rendered ending (US build):** the page images read "Cyber Akuma"
  (`build/regression/m8_roster_gold_us/build/records-ME-3F5C.png`).

## Conclusion

**SUPPORTED** (offline): Norimaro's win quotes (official), partner lines
(official) and ending (translated) are built into both release variants.

## Uncertainty and Alternatives

- Like the unseen kanji, the retired-kanji census sees only record-shaped
  text; a kanji also used by other-format text would be lost there.
- The translation is not official text.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold m8_roster_gold_us
```
