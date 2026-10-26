# EXP-0081: Apocalypse's and Mech-Gouki's win quotes in English

Task: SPECIAL-004
Status: IN_PROGRESS (built and checked offline; live check pending)
Confidence: SUPPORTED (pairing, compiler checks)

## Observation

- `docs/coverage_exceptions.md` excluded the bosses' win quotes: Apocalypse
  (`MC00` slot 0, inside a 26-record table at `0x3106`) and Mech-Gouki
  (`MC13` records 0-15).
- The user asked for them on 2026-10-26, and whether Mech-Gouki has an
  ending.

## Hypothesis

The Saturn's boss tables equal the arcade Japanese slots 0 and 19, and the
arcade has English blocks of their own for both, so the roster pipeline
applies unchanged.

## Controlled Change

`data/text/secret_roster.json` adds slot 0 (`MC00.PAC` `0x3174`) and slot 19
(`MC13.PAC` `0xA06C`). Nothing else changes.

## Prediction

Both tables byte-identical to the arcade Japanese; English unique to each
slot; the font fits; every compiler check true.

## Inputs and Provenance

Saturn image (manifest hashes), `MC00.PAC` and `MC13.PAC` decoded
(`local/special003/mc/`); arcade `mshvsfu`, `mshvsf`, `mshvsfj`; PS1 US.

## Tools and Environment

`tools/reference/roster_pairing.py`, `tools/text/official_endings.py`,
`tools/text/caption_compiler.py`. Python 3.12.13.

## Procedure

1. Read the arcade Japanese table (`0x20BFAC`) slots 0 and 19 and search the
   decoded Saturn files for each 16-record block.
2. `roster_pairing` on a trial roster with both slots (three arcade sets).
3. Read their English (`0x20C014`); add both slots; rebuild both release
   references.

## Actual Result

- **Location:** Apocalypse's 16 records are at `MC00.PAC` `0x3174`,
  Mech-Gouki's at `MC13.PAC` `0xA06C`: each byte-identical to the arcade
  Japanese slot (`0x20C2EC`, `0x211D2C`) in all three sets.
- **English:** each slot has its own block (`0x219E00`, `0x21D960`), shared
  with no other slot, identical in all three sets, and on the PS1
  (`SELECT.BIN` `0x0F8EC`, `0x1344C`). Record `k` pairs with entry `k & 7`;
  no name placeholders; no character names in the text, so both name
  variants read the same.
- **Build:** all nine regression references pass; every compiler check true;
  581 pairs (90 and 64 bytes spare). `m8_roster_gold`: spec `d7567c46…`,
  track 01 `00e15be7…`, patch `156fc456…` (2,952,948 bytes);
  `m8_roster_gold_us`: spec `272b3408…`, track 01 `3d2a13d2…`, patch
  `953ae519…` (2,954,388 bytes).
- **Mech-Gouki as a player (outside claim, untested):** the user's GameFAQs
  copy says that after a Survival clear, holding Start while choosing Akuma
  twice in Arcade or Versus mode gives Mech-Gouki. The Saturn's Japanese
  ending table points slot 19 at Dan's pages (`docs/coverage_exceptions.md`),
  so a Mech-Gouki ending would show Dan's pages (HYPOTHESIS).
- **Apocalypse as a player:** nothing found (the same page lists him as
  "coming soon"); no ending is expected (HYPOTHESIS).

## Conclusion

**SUPPORTED** (offline): both bosses' win quotes are the official English in
both release variants.

## Uncertainty and Alternatives

- When each boss quote is shown is not yet seen in play (after the boss beats
  the player is expected).
- Which stage holds Apocalypse is unknown: every driver run so far met
  CYBER-AKUMA at stage 8.
- `MC00`'s three other tables (`0x392E`, `0x3D7A`, `0x404E`) are still
  unidentified.

## Reproduction

```bash
./invenv.sh python -m tools.reference.roster_pairing --roster data/text/secret_roster.json \
  --saturn-dir local/special003/mc --driver local/mame_src/cps2.cpp \
  --archives local/arcade_roms/mshvsf/mshvsfu.zip local/arcade_roms/mshvsf/mshvsf.zip local/arcade_roms/mshvsf/mshvsfj.zip
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
```
