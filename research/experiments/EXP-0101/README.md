# EXP-0101: The quote screen check reads gold captions

Task: RE-050 tooling (follow-up to `EXP-0098`)
Status: DONE
Confidence: CONFIRMED (32 gold captures pass with a clear margin; the white
path is unchanged and unit-tested)

## Observation

- `verify_records.py`'s screen check (`quote_render.match`) compares the
  font's pen-1 pixels with screenshot pixels whose channels are all at least
  200, which is white text.
- Gold captions (`FONT-011`, `EXP-0096`) draw pens 1-9 in yellow to orange.
  They therefore score IoU 0, and 28 of 32 runs failed in `EXP-0098`.

## Hypothesis

With a gold test for screen pixels and a pen 1-9 mask for gold, every gold
capture matches its own record. White captions are unaffected.

## Controlled Change

- **`quote_render`:**
  - `is_gold` (R ≥ 200, G ≥ 96, B ≤ 64);
  - `screen_body(..., gold=)` and `body_mask(..., gold=)`;
  - `match` uses gold when the text box holds more gold pixels than white.
- **Colours:** the thresholds come from the box pixels of two `EXP-0098`
  captures: the text is `(240, 208, 0)` and `(224, 176, 0)`, while the box,
  the portraits and the outline all have blue ≥ 96.
- **Test:** `test_match_reads_gold_captions`.

## Actual Result

- **`verify_records.py`:** run on `build/ref012_m8_roster_gold_us` with the
  32 `EXP-0098` runs. All 32 pass (`all_ok`), each at IoU 1.0 against its
  own record. Records 8-15 tie with their identical copies 0-7.
- **Margin:** the best distinct wrong record scores 0.275 (Bison record 3)
  and 0.25 (Akuma record 6).
- **White path:** `test_match_finds_record_with_small_offset` still passes.
  The `EXP-0036` white-font build is no longer on disk to re-run.

## Conclusion

**CONFIRMED:** gold-caption captures are verified automatically now.

## Reproduction

```bash
./invenv.sh python -m tools.mednafen.verify_records --compile-dir build/ref012_m8_roster_gold_us \
  local/mednafen/agent/runs/re050-bison-r?? local/mednafen/agent/runs/re050-akuma-r??
```
