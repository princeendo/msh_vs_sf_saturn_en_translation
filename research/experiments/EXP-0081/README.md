# EXP-0081: Apocalypse's and Mech-Gouki's win quotes in English

Task: SPECIAL-004
Status: DONE (win quotes built and seen in play)
Confidence: CONFIRMED (win quotes, US build)

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

### Live check (play session of 2026-10-26)

US build (track 01 `3d2a13d2…`), user at the controls; session recorder
(`local/special004/play/rec`), `bp_log` on `06095544-06095EC3` plus PC
`060AF32C`, `ending_driver --after-stage 1 --stage 7 --no-ko`, then
`--after-stage 1`.

- **Mech-Gouki's win quote** (CYBER-AKUMA NOW!!, user lost): "My creator
  wants you / dead. It is done..." (`f00008800.png`, `07db32afb1add90e…`),
  as in the spec (records 7 and 15). No CONTINUE? follows in that mode.
- **Apocalypse is the stage-7 boss:** with the stage word held at `0x0006`
  the fight was against Apocalypse. His win quote after the user lost:
  "Destruction is a small / price to pay for power!" (`f00019878.png`,
  `f57704f85a3f0ab1…`), as in the spec (records 3 and 11).
- **New text found:** before the fight, Ryu and Apocalypse exchange three
  Japanese boxes at the top of the screen (`f00014237.png`
  `4eccb7ee16af0632…`, `f00014363.png` `5fdc89fd1560df28…`,
  `f00014479.png` `490113695858b632…`). Rendered with the quote font, they
  are `MC00`'s three "unidentified" tables (`0x392E`, `0x3D7A`, `0x404E`):
  one exchange with Apocalypse per hero (Hulk, Wolverine, Shuma-Gorath, Omega
  Red, Spider-Man, Blackheart, Ryu, Ken, Chun-Li, Dhalsim, Zangief, Vega,
  Gouki, Sakura, …). 24-byte probes from all 67 76-byte slices
  `0x392E`-`0x4CC6` occur in all three arcade sets (from `0x210B5A`,
  mostly `0x216552`-`0x216B4A`). The US arcade has official English for
  them (`tools.reference.cps2_text.decode_code`, from `0x222AFE`), for
  example Ryu's "I've looked forward to meeting you Apocalypse..." and
  Apocalypse's repeated "Now, let only the strong survive!". No 32-bit
  pointers to the Japanese record starts were found, so how the arcade
  indexes them is still unknown.
- **Mech-Gouki as a player:** not reproduced. After choosing Akuma, the user
  could not choose him again (one attempt). The GameFAQs claim stays
  unconfirmed; the second run played Akuma and Ryu, met Cyber-Akuma at stage
  8, and started Akuma's ending in English.
- **Apocalypse as a player:** nothing seen to suggest it.

## Conclusion

**CONFIRMED** in play for both win quotes (US build): each boss shows the
official English from its spec after beating the player. Apocalypse's
pre-fight exchanges are new, untranslated scope.

## Uncertainty and Alternatives

- Only the US build was played; the Saturn-name build has the same quote
  bytes for both bosses (no names in the text) but was not seen.
- The census record grid for `MC00`'s three extra tables does not line up
  with the dialogue boxes (some 76-byte slices start mid-sentence), so the
  real record boundaries and the arcade's index for the exchanges are still
  to be found.
- One failed attempt does not disprove the Mech-Gouki select code.

## Reproduction

```bash
./invenv.sh python -m tools.reference.roster_pairing --roster data/text/secret_roster.json \
  --saturn-dir local/special003/mc --driver local/mame_src/cps2.cpp \
  --archives local/arcade_roms/mshvsf/mshvsfu.zip local/arcade_roms/mshvsf/mshvsf.zip local/arcade_roms/mshvsf/mshvsfj.zip
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
```
