# EXP-0046: Census and Capacity of the Roster's Endings (M8 Start)

Task: END-021
Status: DONE (2026-10-24)
Confidence: CONFIRMED (records, counts, fit, capacity, all offline and measured).
The per-screen VRAM limit is SUPPORTED only.

## Observation

M7 (`EXP-0044`, `EXP-0045`) localized Ryu's ending for two partners. `END-020`
generalizes to the 17-character M5 roster (`data/text/m5_roster.json`: slots
1-16 and 18). Excluded: Apocalypse (0), Norimaro (17), Cyber-Akuma (19), and
the secret characters (20-25), per `docs/coverage_exceptions.md`.

## Hypothesis

For every roster slot, `EXP-0044`'s pipeline applies unchanged:
- the Saturn ending records equal the arcade Japanese records;
- English pages exist in the same number;
- every English line fits;
- one font can hold the endings and the M5 win quotes together.

## Controlled Change

None. Offline reads of the untouched image and of `mshvsfu.zip`.

## Procedure

```bash
./invenv.sh python -m tools.text.ending_census --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --out data/text/ending_census.json
R=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18)
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --point $R --partners $R \
  --out local/end020/endings_roster.json
./invenv.sh python -m tools.text.official_captions --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --out local/end020/winquotes_roster.json
# The combined spec = win-quote tables + ending tables, fields, and patches
# (local/end020/combined_roster.json).
./invenv.sh python -m tools.text.caption_compiler local/end020/combined_roster.json \
  --out-dir build/end020_cap --capacity
```

`official_endings.py` now takes several point slots (`--point 1 2 …`). A single
point still produces a byte-identical spec, so the `end010` regression is
unaffected.

## Actual Result

### Census (`data/text/ending_census.json`, metadata only)

- **All 17 slots are consistent** (`all_consistent: true`):
  - the Japanese and English page counts are equal (75 pages in total, 2-6
    per character);
  - every Saturn page record in `ME.PAC` equals the arcade Japanese record;
  - both `MC13` dialogue pairs of every slot (as partner, index `slot`; as
    point, `26 + slot`) equal the arcade block.
- **Lines:**
  - English page lines are at most 25 characters (13 cells).
  - English page text has no name placeholders.
  - Every English partner and point half fits 19 cells with the longest roster
    name inserted (CAPTAIN AMERICA, 8 cells).
- **Names:**
  - Every English name fits a 14-cell entry.
  - The name-length table must change for most slots.
  - For BISON it grows (2 → 3), which is untested; `EXP-0044` only shrank
    RYU's.

### Capacity (`caption_compiler.py --capacity`)

| Spec | Records | Distinct pairs | Free codes | Kanji codes reused | Pair bytes / reclaimable | Fits |
| --- | --- | --- | --- | --- | --- | --- |
| 17 endings (pages, 34 dialogue pairs) | 143 | 369 | 248 | 121 | 15,453 / 30,235 | yes |
| Endings + 17-character win quotes | 415 | 454 | 248 | 206 of 321 candidates | 19,303 / 30,235 | yes |

The capacity mode does not count name fields (17 short names, a few pairs). The
margin covers them.

### Glyphs per screen

- English pages need at most 25 distinct glyph cells per page, and a dialogue
  box at most 14. Japanese pages already use up to 34.
- So the per-screen VRAM glyph slots (`EXP-0038`) should suffice. That is
  `SUPPORTED`, not tested at the limit.

## Conclusion

The pipeline generalizes to the whole roster with no structural exceptions.
One image can hold the M5 win quotes and all 17 endings. The remaining risks
are behavioural, not capacity:
- a name-length increase;
- the English names appearing in Japanese text that still inserts names;
- a live check across characters.

Those are `END-022` to `END-024`.

## Uncertainty and Alternatives

- Fit is measured with the `whole` dialogue layout and `EXP-0044`'s centring.
  Rendering quality, such as pair-glyph legibility, is checked only by the
  offline review and the live sample to come.
- Only `mshvsfu` text is used. The US/EU/JP ending data were identical for Ryu
  (`EXP-0042`) but were not compared for every slot.

## Reproduction

See Procedure.
