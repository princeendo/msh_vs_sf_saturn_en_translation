# EXP-0048: Combined Roster Image (Win Quotes and Endings, Offline)

Task: END-023
Status: DONE (2026-10-24)
Confidence: CONFIRMED offline (deterministic build, all checks, renders
reviewed, regression pinned). Live verification is `END-024`.

## Observation

- `EXP-0046`: all 17 roster endings fit, and one font holds them plus the M5
  win quotes.
- `EXP-0047`: names can grow, and the user accepted English names inside the
  Japanese text that remains.

## Hypothesis

One spec, generated from the local ROM, builds a single deterministic image
from the untouched source with:
- the 17 M5 win-quote tables, unchanged from the verified roster image;
- the 17 roster endings;
- every roster partner and point pair, in the `whole` layout;
- the roster's English names and name lengths.

## Controlled Change

`tools/text/official_endings.py --roster data/text/m5_roster.json
--with-win-quotes`. Every roster slot is a point character and a partner, and
the win-quote tables come from `official_captions.roster_spec` (the same code
as the `roster` reference). A single-point spec stays byte-identical (checked
against `end010`'s spec).

## Prediction

- The compiler fits the font and passes every check, and two builds are
  identical.
- The win-quote renders equal the reviewed roster build's.
- The ending renders read as the official English.

## Inputs and Provenance

- **Untouched source:** track 01 `8274307f…`.
- **Arcade:** `mshvsfu.zip` with the pinned driver.
- **Font candidates:** `research/memory_dumps/exp0023/unseen_codes.json`.
- **Spec:** `local/end023/roster_image.json` (`b75f447d…`, ignored).
  - 35 tables: 17 win-quote tables, `MC13` (68 dialogue records), and 17
    `ME.PAC` page tables (75 records).
  - 17 name fields and 17 name-length patches.
  - The win-quote tables are identical to the `roster` reference spec's.
  - Every replaced ending record was checked equal to the arcade Japanese
    record (pages and dialogue: true).

## Procedure

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --out local/end023/roster_image.json
./invenv.sh python -m tools.text.caption_compiler local/end023/roster_image.json \
  --out-dir build/end023
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --report docs/regression_report.md
```

## Actual Result

- **Build:** track 01 `c06cf0ef6e1e74dd…`; the two builds are identical; 178
  changed sectors; manifest `3b753f47…`.
  - 21 files differ: `MC01`-`MC10`, `MC12`, `MC13`, `ME.PAC`, `MEMFIX.PAC`,
    and `MM.BIN`.
  - Every compiler check is true: font, tables, raw files, patches, and image.
- **Font:** 501 pair glyphs, reusing 253 of the 321 candidate kanji codes.
  - The win-quote pairs are allocated first and keep their codes. So all 17
    win-quote PAC files are **byte-identical** to the verified `roster`
    image's: for example, `MC01` `46ae4cf0…` and `MC09` `697720e6…`.
  - Only `MEMFIX.PAC` gains the ending pairs (`430596e0…`).
- **`MC13`:** spliced, with declared length 31,011 kept and 221 zero-fill
  bytes.
- **`MM.BIN`:** 17 name entries; 11 name-length bytes changed (the other 6
  already matched).
- **Renders:**
  - All 17 win-quote renders are byte-identical to the `roster` reference's.
  - The 75 page records were read: all are the official English, in order,
    centred, and legible. The comma pair glyph matches the M5 win quotes.
  - The 68 dialogue records were read: each English line appears in both
    records of its pair, with gaps where names are inserted at runtime.
- **Regression:** new reference `m8_roster`, with the spec regenerated from the
  ROM. All six references pass (`docs/regression_report.md`).

## Conclusion

**CONFIRMED offline.** One deterministic image from the untouched source holds
the M5 win quotes, byte-identical to the verified roster files, and all 17
roster endings in official English. The live check is `END-024`.

## Uncertainty and Alternatives

- Not yet shown live:
  - the endings beyond Ryu's;
  - long names, such as CAPTAIN AMERICA (8 cells);
  - name growth in an image, such as BISON;
  - pages with the most distinct glyphs (25).
- The new font has to be loaded by a cold boot (`EXP-0044`). States saved
  during an `END-024` cold-boot session can be reused later for replays of
  changes that leave the font, `ME.PAC`, and `MM.BIN` unchanged (`EXP-0045`).

## Reproduction

See Procedure.
