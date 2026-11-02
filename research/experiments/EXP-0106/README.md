# EXP-0106: Can one quote font serve every text switch? (OPT-002 study, font half)

Task: OPT-002 (study first)
Status: DONE
Confidence: CONFIRMED (offline build: one font holds the pairs of all four
text variants); SUPPORTED (the font registry and the MEMFIX loader, read from
code, not stepped); HYPOTHESIS (the costs)

## Observation

- `EXP-0095`: the two release images differ by 58,369 bytes of the quote font
  (`MEMFIX.PAC` entry 4, 206,656 bytes) plus about 490 bytes of text and
  tables.
- Both fonts do not fit side by side in the cart RAM seen free.
- The grammar fixes (`TXT-004`) rewrite win quotes too, so they might need a
  third and fourth font.
- Two ways out had not been tested: re-reading the font when the setting
  changes, or one merged font.

## Hypothesis

The variants differ in only a few letter pairs, so one font built from the
union of all four variants' pairs still fits. The 58 KB difference is then a
repacking shift, not new glyphs.

## Controlled Change

None to any image. The compiler's own build (`caption_compiler.compile_tables`
and `pair_font.build`) is run on the base spec. It is then run again with the
other variants' extra pairs added as scratch fields in a dummy raw file whose
writes are discarded.

## Prediction

- The union adds tens of pairs, not hundreds.
- The merged build fits, with candidate kanji left over.

## Inputs and Provenance

- **Source track:** `local/disc_images/mshvsf_saturn_jp/… (Track 01).bin`
  (the untouched JP image).
- **Candidates:** `data/text/font_candidates.json` (`32e513ae…`).
- **Specs:** generated with the release references' arguments
  (`data/regression/reference_builds.json`) into `local/opt002/specs/`:

  | Spec | Extra arguments | SHA-256 |
  | --- | --- | --- |
  | `saturn.json` | none | `2a7eacaf…fc55`, the `m8_roster_gold` baseline |
  | `us.json` | `--names us` | `7d35cfe7…9b2c`, the `m8_roster_gold_us` baseline |
  | `saturn_grammar.json` | `--fix-grammar data/translations/grammar_fixes.json` | `92a8ba3f…2b7e` |
  | `us_grammar.json` | both | `8320b222…67bc` |

- **Code:** the `EXP-0105` WRAM-H extraction (`f00003213`).

## Tools and Environment

- `pair_union.py`: distinct pairs per spec, counted as the compiler does.
- `merged_font.py`: the base build and the merged build.
- `record_diff.py`: the records, fields and patches that differ between two
  specs.
- Python 3.12 via `./invenv.sh`. The generator needs the pinned MAME driver
  `local/mame_src/cps2.cpp` and the arcade archive.

## Procedure

1. Generate the four specs (about seven minutes each).
2. `pair_union.py` on all four.
3. `merged_font.py` with each release spec as base and all four as others.
   Check that the base build reproduces the baseline `MEMFIX.PAC`.
4. `record_diff.py` for the names switch and for the grammar switch.
5. Read the font registry and the MEMFIX loader in WRAM-H.

## Actual Result

### 1. Pairs

| Spec | Pairs | Not in `saturn` |
| --- | --- | --- |
| `saturn` | 580 | none |
| `us` | 577 | 7: `-a` `Ak` `Bi` `ON` `Tr` `ku` `o'` |
| `saturn_grammar` | 580 | 5: `2 ` `At` `ds` `k,` `ya` |
| `us_grammar` | 577 | 12 (both sets) |
| union | 592 | 12 |

### 2. Font builds (803 candidate kanji)

| Build | Pairs | Zero fill | Kanji sacrificed | Kanji reused | `MEMFIX.PAC` |
| --- | --- | --- | --- | --- | --- |
| `saturn` | 580 | 44 | 109 (10,430 bytes) | 332 | `6f0dc7f1…`, equals the baseline |
| `us` | 577 | 92 | 110 (10,458 bytes) | 329 | `be24dc10…`, equals the baseline (with the name-call patches) |
| `saturn` + `us` | 587 | 105 | 109 | 339 | |
| all four | 592 | 21 | 107 (10,159 bytes) | 344 | |

- The merged font fits. 352 candidates are still untouched, and the builder
  sacrifices them only as bytes run short.
- The base builds reproduce both release fonts byte for byte, so the merged
  build follows the compiler's rules.

### 3. What each switch would still swap (`record_diff.py`)

| Switch | Entries | Files |
| --- | --- | --- |
| Names | 43 | `MM.BIN` 21, `ME.PAC` 10, `MEMFIX.PAC` 6 (name-call patches), `MC00.PAC` 4, `MC0F.PAC` 2 |
| Grammar | 40 | `ME.PAC` 9, `MC13.PAC` 6, `MM.BIN` 5, `MC00.PAC` 4, `MC0E.PAC` 4, `MC01`/`MC02`/`MC05`/`MC09`/`MC0C`/`MC0F.PAC` 2 each |

- **`MM.BIN` stays in RAM** (`0x06018B00`), so its records could be
  rewritten in place.
- **The MC PACs are loaded and decoded per fight** through the queued loader
  (`0x0603F90C` → `0x0603DB30`). A switch must patch them after each load,
  or choose between two copies on disc.
- **`ME.PAC` (endings):** when it loads was not traced.
- **The name-call table** is `MEMFIX` payload 7, loaded into sound RAM.

### 4. How the font is found (read from code, not stepped)

- The MEMFIX loader (`0x060401FC`) reads `memfix.pac` by name and scatters
  its entries. The name is at `0x06041298`, and the destination list is
  pointed to by `0x06041294`; entry 4 goes to `0x0278CF60`.
- It then registers resource ids `0x20`-`0x2F` in a 16-byte-per-id table at
  `0x0601D5F0`. Id `0x2F` (`0x0601D8E0`) is `1, 0x0278CF60, 0, 0x2E6C`, so
  the font's address is held in one place.
- A second font could in principle be selected by rewriting that long. With
  one merged font this is not needed.

## Conclusion

**CONFIRMED (offline build):** one quote font holds the pairs of all four
text variants (names × grammar): 592 pairs, built under the compiler's own
rules, with 352 candidate kanji spare. Text switches do not need a font
reload or a second font.

**HYPOTHESIS: costs, nothing built:**
- **Names switch:**
  - the 21 `MM.BIN` entries patched in RAM when the setting changes;
  - the six PAC entries patched after each load (a load hook);
  - the name-call table rewritten in sound RAM;
  - ME.PAC's 10 entries, depending on when it loads;
  - the art and pointer changes (life-bar labels, banner and VS pointers)
    are among the `MM.BIN` entries.
- **Grammar switch:** the same mechanism over more files (nine MC PACs,
  ME.PAC, five `MM.BIN` hint records). Built after the names switch, it
  shares the load hook.
- **The release font would change:** both variants would move to the merged
  font, so every reference is rebaselined.

## Uncertainty and Alternatives

- **Font build only:** the merged font was built offline and never drawn.
  The scratch fields stand in for text that would use the new codes.
- **Code assignment:**
  - each variant's records must be compiled against the merged font's code
    map. Today the compiler assigns codes per spec, so that is new tooling;
  - `record_diff.py` compares spec text, so it counts differing records, not
    differing bytes.
- **Candidate kanji are "unseen" kanji:** text the census cannot see could
  still use one. This risk is already accepted for the release (`EXP-0079`).
- **Loading:** the post-load hook point for MC PACs and when ME.PAC loads
  are not traced.

## Reproduction

```bash
# generate one spec (repeat with --names us and/or --fix-grammar ...)
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --glyph-style arcade --caption-palette gold --ui-english \
  --attract-captions --secret-roster data/text/secret_roster.json \
  --secret-translations data/translations/secret_characters.json \
  --story-lines data/translations/story_lines.json --official-hints \
  --boss-exchanges --error-screens --out local/opt002/specs/saturn.json
S=local/opt002/specs
./invenv.sh python research/experiments/EXP-0106/pair_union.py \
  $S/saturn.json $S/us.json $S/saturn_grammar.json $S/us_grammar.json
./invenv.sh python research/experiments/EXP-0106/merged_font.py \
  $S/saturn.json $S/saturn.json $S/us.json $S/saturn_grammar.json $S/us_grammar.json
./invenv.sh python research/experiments/EXP-0106/record_diff.py $S/saturn.json $S/us.json
./invenv.sh python research/experiments/EXP-0106/record_diff.py $S/saturn.json $S/saturn_grammar.json
```
