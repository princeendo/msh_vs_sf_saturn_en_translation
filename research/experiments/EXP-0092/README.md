# EXP-0092: Descenders for g, j, p, q and y in the credits pair glyphs

Task: RE-048
Status: DONE
Confidence: CONFIRMED (offline renders of every affected line; two built records on the Saturn)

## Observation

- `EXP-0036` noted that the white pair glyphs cut `p`'s stem short.
- The release now uses the credits font (`FONT-011`). It has no descenders
  at all: the lower case ends on row 11, and `p`'s stem is one row in the
  squeezed fill. "Keep your guard up, puppy" renders like "Kee0 vour 9uard
  u0, 0u00v" (`local/re048/credits_now.png` `4acbbdcd…`).
- Capitals already use rows 12-14 (for example `K`).

## Hypothesis

Hand-drawn fills for g, j, p, q and y that reach rows 12-14 make them
readable. `OVERRIDES` in `tools/text/credits_font.py` already redraws
letters this way: `I`, `M`, `W`, `m` and `w`.

## Controlled Change

Five new `OVERRIDES` entries, each 8 columns:
- **p, q, g, y:** body on rows 4-11, descender on rows 12-14;
- **j:** dot on rows 2-3, stem from row 5, hook on rows 13-14.

The text is unchanged, so the specs are unchanged. Only the pair glyphs of
the three credits-style references change: `m8_roster_credits`,
`m8_roster_gold` and `m8_roster_gold_us`.

## Prediction

- Every release line with g, j, p, q or y shows a descender.
- The font still fits `MEMFIX.PAC` entry 4: the build would fail
  otherwise.
- Only the credits-style references change.

## Inputs and Provenance

- `MEMFIX.PAC` from the source image (`references/mshvsf/saturn_jp/README.md`),
  copied read-only to `local/re048/MEMFIX.PAC` for offline renders.
- Spec `local/ui003/spec/m8_roster_gold.json` (`5cce9a7e…`, `EXP-0091`).

## Procedure

1. **Mock-up:** `local/re048/draft.py` patches the overrides at run time and
   calls the `credits_font` CLI.
2. **Every affected line, offline:**
   - all 1,430 spec lines were collected;
   - 496 distinct lines hold g, j, p, q or y and only credits glyphs (3 more
     hold arrows or `{P}`);
   - they were rendered in 16 sheets (`local/re048/sheets/s00`-`s15.png`) and
     every sheet was read.
3. **Rebaseline:** `bash local/re048/rebaseline.sh` runs
   `reference_builds --only m8_roster_credits m8_roster_gold
   m8_roster_gold_us --write-baseline` with the reason, then the report,
   `make_patch` and `make_ssp`.
4. **Saturn:** `bash research/experiments/EXP-0092/verify_descenders.sh`.

## Actual Result

### Offline

- **After:** `credits_after.png` (`e2111085…`) is identical to the draft. The
  two test lines read "Freedom prevails! gpqy jg" and "Keep your guard up,
  puppy".
- **All 496 lines** show the descenders, with no clashes with neighbouring
  letters or the next line. Sheet hashes, in order `s00`-`s15`: `1c154482`,
  `2c49373c`, `bf7fc705`, `697c7260`, `5c4391c1`, `9298de3c`, `e8cbccaf`,
  `444ac786`, `cbae9548`, `0b0c1650`, `aef40b4e`, `216e1ccc`, `aeab6b9c`,
  `57966760`, `3e160d68`, `99889690`.

### Rebaseline (`local/re048/rebaseline.log`)

- **Reason:** "EXP-0092: lower-case g, j, p, q, y drawn with descenders in
  the credits pair glyphs (RE-048)".
- **Builds:** all three references built, so the font still fits entry 4.
  The report passed nine of nine; the six untouched references are
  unchanged.

| Reference | Track 01 before | Track 01 after |
| --- | --- | --- |
| `m8_roster_credits` | `bede40b1…` | `5d1c69b92c4a0bcb0cb4b0c701e601ec5d8fa2109b228b669cd73402b3980d4a` |
| `m8_roster_gold` | `ceeca6ab…` | `0d55127a1757de3d15d40808d98b9cd900b50a7cf38eba93c666550899f4b125` |
| `m8_roster_gold_us` | `a1bf1809…` | `0c3f72bbe856acd8f24d072185a12190b97a7344beb94e0b821cb3266bb21ef0` |

- **Patches:** both formats round-trip.
  - xdelta: 644,592 bytes (`6b46f74c…`) and 645,359 bytes (`84ea21e7…`);
  - `.ssp`: 563,121 bytes (`b0f642da…`) and 563,205 bytes (`c1391cd9…`).

### On the Saturn (built US image, box 4 of the `EXP-0089` checkpoint)

- `MC0B` record 7 (`MC0B_r7_f1100.png` `7a0902e9…`): "I hope I get
  royalties, / not just a one time fee!". The p, g, y and j descend below
  the line.
- `MC02` record 5 (`MC02_r5_f1100.png` `4e0e1b14…`): "Never stop improving
  / yourself!". The p, g and y descend.
- The box is silver because the checkpoint runs the original `MM.BIN`
  palette. Only the glyph shapes are under test.

## Conclusion

**CONFIRMED:** the five overrides give g, j, p, q and y clear descenders in
every affected release line, and the font still fits.

## Uncertainty and Alternatives

- **Design:** the shapes are hand-drawn and upright, like the existing
  overrides. They may look plainer than the slanted source glyphs. The user
  has not reviewed them yet.
- **Coverage on the Saturn:** two records were shown there. The rest rely on
  the offline renders, which use the same composition code.

## Reproduction

```bash
./invenv.sh python -m tools.text.credits_font local/re048/MEMFIX.PAC \
  --line "Freedom prevails! gpqy jg" --line "Keep your guard up, puppy" \
  --palette gold --out local/re048/credits_after.png
bash local/re048/rebaseline.sh    # reference_builds --only m8_roster_credits m8_roster_gold
                                  # m8_roster_gold_us --write-baseline --reason …; report; patches
bash research/experiments/EXP-0092/verify_descenders.sh
```
