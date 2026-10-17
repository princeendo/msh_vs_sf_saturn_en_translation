# EXP-0026: All 16 Ryu Marker Records Live From One Compiled Image

Task: `RE-024`
Date: 2026-10-17
Status: IN_PROGRESS (pre-registered)
Confidence: HYPOTHESIS

## Observation

- `RE-022` built `build/re022_markers/image_a` (track 01 `fd007d13…`; the two
  builds are identical). Each record shows its own marker:
  - line 1: `Ryu record NN line one`, or `Ryu record 00 is{P}` for record 0, which
    keeps its placeholder at cell 8;
  - line 2: `NN Line two fills cells up to nineteen`, all 19 cells.
- It uses 51 pair glyphs at `0x00A8-0x00DA`. Only `0x00A8-0x00B1` had been shown
  on screen before (`EXP-0023`).
- `EXP-0025` showed that overwriting the index word after PC `060AF282` selects
  any record, from a post-KO checkpoint, with no input.

## Hypothesis

From one cold boot of the marker image, every record 0-15 displays its marker
exactly as compiled.

## Controlled Change

- The image is the `RE-022` marker build.
- Per run, the only variable is the forced index (0-15). The method is
  `onhit 060AF282 write workramh F9E66 <index>` from one post-KO checkpoint made
  on this image.

## Procedure

1. Launch the patched Mednafen (`fe0edb99…`, `EMU-021`) on the marker CUE with
   the agent enabled.
2. Run `ko_capture.py --checkpoint` (no state). The user boots into arcade mode,
   picks Ryu and Ken, and KOs the first opponent with Ryu. The script keeps a
   rolling checkpoint at each bonus-tally clear (`060490EC`) and stops at the
   first pointer into Ryu's table.
3. For index 0-15: `ko_capture.py --state postko.mc --force-index i
   --setter-pcs 060AF282`.
4. Run `verify_records.py --compile-dir build/re022_markers` on all 16 runs.

## Prediction

For each index `i`:

- the pointer is `0x002091AC + 76·i`;
- `quote_render --match` against the marker font and table picks record `i`;
- cart-RAM font = compiled font entry, WRAM-L table = compiled table, and the
  display buffer holds record `i`'s codes;
- for record 0, the placeholder expands to the partner's name glyphs, beside the
  Latin pairs.

All 51 pair codes, including the untested `0x00B2-0x00DA`, render, because every
code is used in at least one record.

**Refuted if:** any record shows other text, blank or garbage cells, or a RAM
mismatch.
