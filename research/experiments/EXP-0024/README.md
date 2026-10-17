# EXP-0024: Map Ryu Quote Labels to Table Records by Offline Rendering

Task: `RE-021`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED (renderer and matcher); SUPPORTED (5 labels with no RAM
evidence)

## Observation

- Ryu's quotes were labelled `Q1`-`Q11` in order of first observation
  (`EXP-0009`, `EXP-0010`). These labels are not table indices.
- Six labels already had a record address or a display-buffer state. Five (Q1, Q3,
  Q4, Q7, Q9) had only screenshots.
- In `EXP-0023` the WRAM-H display buffer `0x060ED80A` identified records 4 and 5.

## Hypothesis

A renderer that draws a record's glyphs from the font image on a 16-pixel grid
reproduces the game's text box exactly. If so, comparing glyph body pixels with a
screenshot identifies the shown record without a debugger.

## Controlled Change

None to the game. The single variable is the record compared against each
screenshot. All 16 records of the build the screenshot came from are scored.

## Prediction

- On every screenshot whose record is already known from RAM, the best match is
  that record, with a clear margin over the runner-up.
- Each label maps to one record across all its screenshots, and distinct labels
  map to distinct records.

## Inputs and Provenance

- Original `MC09.PAC` and `MEMFIX.PAC` (extracted, identity per `DISC-010`).
- Patched builds `build/exp0022c`, `build/disc002`, `build/exp0023c`.
- 24 Mednafen screenshots (`-0018` … `-0057`). Hashes are in
  `data/text/ryu_quote_records.json`; the EXP-0009 hashes match that experiment's
  record.
- States `exp0019-slot7`/`slot8` (`fa2f1b607cdc50a9…`, `49e6cb536f2ba481…`) and
  `exp0023c-slot7`/`slot8`.

## Tools and Environment

New tools, both with tests:

- `tools/common/png.py`: a stdlib PNG decoder for 8-bit RGB/RGBA, all five filter
  types.
- `tools/text/quote_render.py`:
  - `record_codes`, `nibbles`, `body_mask`, `render`;
  - `match`: body-pixel IoU over a ±3-pixel window, text box region
    `(16,176)-(336,232)`;
  - `summary`: placeholder cells and line lengths.

## Procedure

1. Measure body colour and rows in `-0056.png`. Body pixels are `(240,240,240)`;
   line 1 spans rows 187-199 and line 2 rows 203-215.
2. Calibrate the origin on `-0056`/`-0057` against the `exp0023c` build with a
   ±12 window. Both choose origin `(26, 186)`, and the best record equals the
   RAM-identified one (4 and 5, IoU 0.94 vs runner-up ≤ 0.59).
3. Fix `ORIGIN = (26, 186)` and run with window 3:

```bash
X=research/extracted_files/mshvsf_saturn_jp
S="local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)"
./invenv.sh python -m tools.text.quote_render --pac $X/MC09.PAC --memfix $X/MEMFIX.PAC \
  --render build/re021/original_records.png --match "$S-0018.png" … "$S-0053.png"
./invenv.sh python -m tools.text.quote_render --pac build/exp0022c/MC09.PAC \
  --memfix build/exp0022c/MEMFIX.PAC --match "$S-0054.png" "$S-0055.png"
./invenv.sh python -m tools.text.quote_render --pac build/disc002/MC09.PAC \
  --memfix $X/MEMFIX.PAC --match "$S-0046.png" "$S-0047.png"
```

   Reports (ignored): `build/re021/match_{original,exp0022c,disc002}.json`
   (`426bf378…`, `da45c9fd…`, `b2bf5ff3…`).
4. Read the `exp0019` states' display buffers with `mcs_extract` (`wram_h`,
   `wram_l`).

## Actual Result

Every screenshot matched with IoU between 0.83 and 0.89 and a margin of at least
0.63.

| Label | Record | Screenshots | RAM evidence | Confidence |
| --- | ---: | --- | --- | --- |
| Q1 | 13 | `-0018`, `-0019` | none | SUPPORTED |
| Q2 | 5 | `-0020`, `-0026`, `-0046` | `exp0019` slot 7 buffer = record 5 | CONFIRMED |
| Q3 | 2 | `-0021`, `-0024` | none | SUPPORTED |
| Q4 | 10 | `-0022` | none | SUPPORTED |
| Q5 | 11 | `-0023`, `-0042`, `-0053` | `0x002094F0` (`EXP-0015`) | CONFIRMED |
| Q6 | 1 | `-0025`, `-0047`, `-0054` | `exp0019` slot 8 buffer = record 1 | CONFIRMED |
| Q7 | 9 | `-0027` | none | SUPPORTED |
| Q8 | 3 | `-0028` | `0x00209290` (`EXP-0013`) | CONFIRMED |
| Q9 | 15 | `-0029` | none | SUPPORTED |
| Q10 | 8 | `-0030`, `-0034`, `-0037`, `-0038` | `0x0020940C` (`EXP-0013`) | CONFIRMED |
| Q11 | 12 | `-0055` | `0x0020953C` (`EXP-0013`) | CONFIRMED |

- Record 4 was seen once without a label (`EXP-0023` win 1, buffer evidence).
- Records 0, 6, 7, and 14 have never been seen.
- The 11 labels map to 11 distinct records, and each label is consistent across
  all of its screenshots.
- A visual check of rendered records 13 and 2 against `-0018`/`-0021` shows the
  same glyphs.
- Only record 0 has a `0000` placeholder: cell 8, the last used cell of its
  9-cell line 1. Lines of records 1-15 use 12-19 cells. All values are in the data
  file.

**Correction.** `EXP-0019` labelled `-0046` as "Q2, record 4". Its own state's
display buffer equals record **5**, and the matcher agrees. The record-4 label was
a mistake made by inspection. Q2 is record 5.

## Conclusion

- **Renderer `CONFIRMED`.** The layout model (16-pixel cell and line step, origin
  `(26, 186)` in 352×240 screenshots, body nibble 1 drawn as `(240,240,240)`)
  identifies the RAM-known record in 10 of 10 test screenshots, across four
  different builds.
- **Mapping recorded** in `data/text/ryu_quote_records.json` (`27fdb316…`, hashes
  and indices only, no text). Six labels are `CONFIRMED` by RAM; five are
  `SUPPORTED` by the validated matcher alone.

## Uncertainty and Alternatives

- The matcher assumes 352×240 screenshots and the measured origin. Other
  resolutions or layout modes (the alternate 25-cell set) would need
  recalibration.
- Placeholder cells are drawn empty, so record 0 may score lower than other
  records until its run-time content is known.

## Reproduction

The commands are in Procedure step 3; screenshots live in ignored paths.
`./invenv.sh pytest tests/unit/test_png.py tests/unit/test_quote_render.py`.
