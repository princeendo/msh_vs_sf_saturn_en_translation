# EXP-0096: Caption pairs from the arcade's narrow win-quote glyphs

Task: REF-012 (the user's fit decision)
Status: DONE
Confidence: CONFIRMED (both variants build and fit; quotes seen on the
Saturn by forced record and in play, `EXP-0098`)

## Observation

- `EXP-0090` found that the Saturn quote font already holds the US arcade's
  narrow Latin glyphs at the arcade's own codes (`0x120`-`0x1DF`, Saturn
  pen = arcade pen + 1).
- Each glyph is 8 pixels wide. Its drawn part, outline included, sits in
  columns 0-7 of a 16 × 16 cell.
- The release drew captions as squeezed staff-credits letters (`FONT-011`).

## Hypothesis

Two narrow glyphs placed side by side (each glyph's columns 0-7, unchanged)
make a pair cell. The cell:
- reads like the arcade;
- uses the same palette convention as the gold captions;
- fits the font as the credits pairs do.

## Controlled Change

- **`pair_font`:** new style `arcade`:
  - `narrow_code` maps A-Z to `0x140`+, a-z to `0x161`+ and 0-9 to `0x130`+,
    with punctuation from `cps2_text`;
  - "+", "(", ")" and ":" (`0x129`, `0x128`, `0x12F`, `0x13B`) were picked
    by shape from a sheet of `0x120`-`0x1DF`;
  - `narrow_pair` joins the left 8 columns of the two glyphs.
- **Generator and references:** `official_endings --glyph-style arcade`. The
  two release references `m8_roster_gold` and `m8_roster_gold_us` change
  only that argument.

Unit test: `test_narrow_pair_keeps_each_glyphs_left_eight_columns`.

## Prediction

- Both variants build, and every compiler check passes.
- Quotes show the arcade's letter shapes on the Saturn, with no squeezing.

## Inputs and Provenance

- Source image as `references/mshvsf/saturn_jp/README.md`.
- Arcade `mshvsfu.zip`, driver `a8c09ef8…`.
- Release options as `EXP-0091`, with `--glyph-style arcade`
  (`local/ref012/arcade/gen.sh`).

## Procedure and Actual Result

1. **Offline mock-up** (`mockup.py`, `compare.png` `96245d05…`), shown to the
   user beside the current pairs. User decision (2026-10-28): adopt.
2. **The glyph at `0x122`**, which the decoder reads as "‼", is "!?" in both
   the arcade ROM (tile `0x15122`) and the Saturn font. Only two release
   lines use it. The decoder note is corrected; the decoding is unchanged.
3. **Build:** `caption_compiler` for both specs:
   - every check passes (font header, pairs equal composed, sacrificed codes
     empty, tables);
   - specs: Saturn names `67fed505…`, American names `86e0ebd6…`;
   - track 01: `bf36e4cb…`, `b9372a58…`.
4. **Saturn, forced records** (`verify_arcade.sh`, as `EXP-0092`):
   - "Never stop improving / yourself!" (`022a43b4…`);
   - "I hope I get royalties, / not just a one time fee!" (`4034257a…`).

   Both are in the arcade's letters with the gold gradient and outline.
5. **Saturn, in play** (`EXP-0098`): three user wins (Bison, Akuma), plus
   all 16 records of each character by forced index.
6. **Rebaseline** of `m8_roster_gold` and `m8_roster_gold_us` with the reason
   "EXP-0096: pair glyphs from the US arcade narrow win-quote glyphs" (record
   below).

## Conclusion

**CONFIRMED:**
- the arcade-glyph pairs fit the font, build in both variants and draw
  correctly on the Saturn;
- the release now uses them.

`--glyph-style credits` still builds the previous look, and `m8_roster_credits`
keeps it as a reference.

## Uncertainty and Alternatives

- **Pitch:** two 8-pixel glyphs per 16-pixel cell give an 8-pixel pitch
  against the arcade's 12, so the letters sit closer than in the arcade.
- **Not seen on the Saturn:** ending pages and hint pages in the new
  letters. They use the same font and record writer.

## Reproduction

```bash
bash local/ref012/arcade/gen.sh local/ref012/arcade/spec   # EXP-0091 command with --glyph-style arcade
./invenv.sh python -m tools.text.caption_compiler local/ref012/arcade/spec/m8_roster_gold_us.json \
  --source-dir local/disc_images/mshvsf_saturn_jp --candidates data/text/font_candidates.json \
  --out-dir build/ref012_m8_roster_gold_us
bash research/experiments/EXP-0096/verify_arcade.sh
./invenv.sh python research/experiments/EXP-0096/mockup.py local/re048/MEMFIX.PAC local/ref012/narrow
```
