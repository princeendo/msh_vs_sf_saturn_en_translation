# EXP-0091: Arcade digits are ASCII + 0x100 ("Level 2", "before 8 am")

Task: TXT-005
Status: DONE
Confidence: CONFIRMED (forced Saturn trials of both corrected lines)

## Observation

- `EXP-0090` showed the arcade draws code `0x0138` as "8" ("I beat more
  people / before 8 am...", `mshvsfu`). The Saturn draws `0x012F`-`0x0132`
  as ")012".
- `tools/reference/cps2_text.py` decoded digits as ASCII − 1 + `0x100` (base
  `0x012F`, from `EXP-0078`'s reading "Level 3" = `0x0132`).
- So the release builds showed "When Level 3 or higher," (CONTINUE? hint 2)
  and "before 9 am..." (slot 22's quote).

## Hypothesis

With the digit base at `0x0130`, the release specs change in exactly the
lines that hold digits, and those lines show the arcade's numbers on the
Saturn.

## Controlled Change

One constant: `DIGIT_BASE` `0x012F` → `0x0130` in
`tools/reference/cps2_text.py`. Its test now checks `0x0130` = "0",
`0x0132` = "2" and `0x0138` = "8", and `0x012F` is unknown (`{012f}`; the
glyph is ")").

## Prediction

- Both release specs change only in "Level 3" → "Level 2" (`MM.BIN` hint
  record 4) and "9 am" → "8 am" (`MC16.PAC` table `0x984C`, records 1 and 9).
- The other references are unchanged; their specs are stored.

## Inputs and Provenance

- MAME driver `local/mame_src/cps2.cpp` (`a8c09ef8…`) and
  `local/arcade_roms/mshvsf/mshvsfu.zip` (`references/mshvsf/arcade/README.md`).
- Source image: `references/mshvsf/saturn_jp/README.md`.

## Procedure

1. `bash local/txt005/gen.sh <dir>` runs `tools.text.official_endings` with the
   release options (as `EXP-0089`), before and after the change.
2. `bash local/txt005/rebaseline.sh`:
   - copies the specs;
   - updates `data/regression/reference_builds.json`;
   - runs `reference_builds --write-baseline` with the reason, then the
     report, `make_patch` and `make_ssp`.
3. `bash research/experiments/EXP-0091/verify_digits.sh` on the built US
   image:
   - hint 2, forced as in `EXP-0086`;
   - `MC16` record 1, written over box 4 of the `EXP-0089` checkpoint.

## Actual Result

### Specs

- **Before the change:** the generator reproduced both reference specs byte
  for byte (`a824a86e…`, `d79c2fce…`).
- **After:** each spec differs in exactly three lines:
  - spec line 2380 and 2436: "before 9 am..." → "before 8 am...";
  - spec line 4713: "When Level 3 or higher," → "When Level 2 or higher,".

### Rebaseline (`local/txt005/rebaseline.log`)

- **References:** both release references were rebaselined with the reason
  "EXP-0091: arcade digits are ASCII + 0x100 (Level 2, before 8 am)". The
  report run passed all nine references.
- **Patches:** both formats round-trip.

| Variant | Spec | Track 01 | xdelta | `.ssp` |
| --- | --- | --- | --- | --- |
| Saturn names | `5cce9a7e…` | `ceeca6abe9678ee1580395242c3a93c47ea57fceaa13d246e1043f21e48be0e1` | 644,524 bytes, `eeb0b497…` | 563,143 bytes, `4f641d3f…` |
| American names | `7028eff9…` | `a1bf1809cf26ff36525206ad9933a679c3732d8eaf33523e9e7dc4da93fea372` | 645,279 bytes, `a796a3b9…` | 563,206 bytes, `0912e6a0…` |

### On the Saturn (built US image)

- **Hint 2, page 1** (`hint2_f850.png` `f88ba15b…`): "When Level 2 or
  higher, / enter ↓↘→ HP+HK".
- **Hint 2, page 2** (`hint2_f1180.png` `aa5deb00…`): unchanged, the same
  hash as in `EXP-0086`.
- **`MC16` record 1 in box 4** (`am_f1100.png` `916480ae…`): "I beat more
  people / before 8 am...".
- All writes survived.

## Conclusion

**CONFIRMED:**
- the digit fix changes exactly the three predicted lines in each release
  spec;
- both corrected lines show the arcade's numbers on the Saturn.

## Uncertainty and Alternatives

- **Saturn-names image:** the trials used the American-names image only.
  The Saturn-names spec has the same three changes, and no name appears in
  these lines.
- **Record 9 not shown:** slot 22's quote record 9 (the repeat of record 1)
  was not shown on screen. It holds the same lines.
- **Older references:** their specs are stored and were not regenerated.
  None of them holds "9 am" or "Level 3" (`grep` of each spec).

## Reproduction

```bash
COMMON="--driver local/mame_src/cps2.cpp --archive local/arcade_roms/mshvsf/mshvsfu.zip \
  --roster data/text/m5_roster.json --with-win-quotes --glyph-style credits --caption-palette gold \
  --ui-english --attract-captions --secret-roster data/text/secret_roster.json \
  --secret-translations data/translations/secret_characters.json \
  --story-lines data/translations/story_lines.json --official-hints --boss-exchanges"
./invenv.sh python -m tools.text.official_endings $COMMON --names us --out local/txt005/after/m8_roster_gold_us.json
./invenv.sh python -m tools.text.official_endings $COMMON --out local/txt005/after/m8_roster_gold.json
bash local/txt005/rebaseline.sh                # rebaseline, report, patches
bash research/experiments/EXP-0091/verify_digits.sh
```
