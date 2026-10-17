# EXP-0026: All 16 Ryu Marker Records Live From One Compiled Image

Task: `RE-024`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

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

## Actual Result (2026-10-17)

**Boot.** Patched Mednafen (`fe0edb99…`) on the marker image (track 01
`fd007d13…`, re-hashed at run time); log `local/mednafen/logs/re024-markers.log`.

- The user played one arcade fight (Ryu/Ken) and KO'd with Ryu.
- Natural selection gave **index 10**. The screen showed `Ryu record 10 line one`
  / `10 Line two fills cells up to nineteen`, and every check passed
  (`quote.png` `3642fe61ca44ff6b…`).
- The rolling post-KO checkpoint was saved at hit 35 (`060490EC`), 131 frames
  before the pointer store: `postko.mc` `9498140e120dec5b…`.

Boot-time code also writes the watched words (for example PC `060F1C34`); the
capture script ignores those, because it only finishes on a pointer into Ryu's
table.

**Forced runs** (no input; `onhit 060AF282` writes the index). Verification:
`verify_records.py --compile-dir build/re022_markers`, report
`re024-verify.json` `f703522f33927b5e…`.

| Index | Pointer | Screen best | IoU | Font, table, buffer | Screenshot | State |
| ---: | --- | ---: | ---: | --- | --- | --- |
| 0 | `0x002091AC` | 0 | 0.9655 | yes | `fc6e49e7f4c85d48…` | `132ebf2e5f2a5d58…` |
| 1 | `0x002091F8` | 1 | 1.0 | yes | `452b17506c0bf550…` | `0cc5d971487e4417…` |
| 2 | `0x00209244` | 2 | 1.0 | yes | `878f408557db7c72…` | `f6070d892e4370f3…` |
| 3 | `0x00209290` | 3 | 1.0 | yes | `80b593f945a7852d…` | `daa13a2b1ac65e33…` |
| 4 | `0x002092DC` | 4 | 1.0 | yes | `8561a5b9c8c05ae4…` | `1d122320e704f33a…` |
| 5 | `0x00209328` | 5 | 1.0 | yes | `d4daa0a820764dfd…` | `6f072a55420cf893…` |
| 6 | `0x00209374` | 6 | 1.0 | yes | `a456ff426e8539ee…` | `5d66ce2de85f5222…` |
| 7 | `0x002093C0` | 7 | 1.0 | yes | `38d0de55cd531f5e…` | `ef00172de1cf3a8f…` |
| 8 | `0x0020940C` | 8 | 1.0 | yes | `ee761f2c308fc988…` | `5a6cd25cccc70d5d…` |
| 9 | `0x00209458` | 9 | 1.0 | yes | `5fab638603c08641…` | `61a4759939df547d…` |
| 10 | `0x002094A4` | 10 | 1.0 | yes | `b7d0267a419e2ea4…` | `257610bd55276683…` |
| 11 | `0x002094F0` | 11 | 1.0 | yes | `aa5b39790c8800dd…` | `27aa0410b4c4104a…` |
| 12 | `0x0020953C` | 12 | 1.0 | yes | `6f146927d46592ce…` | `126cb2bae6ad344d…` |
| 13 | `0x00209588` | 13 | 1.0 | yes | `2fbf6816217e5651…` | `dc9ecd60c548b03c…` |
| 14 | `0x002095D4` | 14 | 1.0 | yes | `65cc1a51ac9cad23…` | `acf00ac8786d1828…` |
| 15 | `0x00209620` | 15 | 1.0 | yes | `a50cf1ec41c9d0ac…` | `961e7fcc41330d7b…` |

- **All 16 records passed every check.** For each one:
  - the pointer is `0x002091AC + 76·i`;
  - the screenshot is the forced record;
  - the cart-RAM font equals the compiled font entry;
  - WRAM-L equals the compiled table;
  - the display buffer holds the record's codes.
- **Pixel-exact screens.** Records 1-15 match their offline render **exactly**
  (IoU 1.0). Margins over the runner-up are small (0.01-0.04) only because the
  markers differ in their digit pairs.
- **All 51 pair codes render.** Every pair code `0x00A8-0x00DA` appears in some
  record. That includes `0x00B2-0x00DA`, which had never been shown before.
- **Record 0.** The screen reads `Ryu record 00 is` followed by **ケン**: the
  partner name expands, in katakana, directly after the Latin pair glyphs. IoU is
  0.97, because the name cells are drawn empty offline. In the display buffer:
  - line 1 keeps 19 entries, with the 2 name glyphs (`0863 08A5`) replacing the
    placeholder and one trailing blank dropped;
  - line 2 is unchanged.
  The original game's record 0 (`EXP-0025` V4) shows the same layout.
- **Extra entry.** Every record's buffer has one extra 39th entry, equal to line
  2's first cell. It is not drawn: the screens match their renders exactly. Its
  purpose is unknown (`HYPOTHESIS`: a loop-count artefact).

## Conclusion

**`CONFIRMED`:** a single command from a caption file (`RE-022`) produces an image
in which all 16 Ryu records display their compiled text exactly, verified on
screen and in RAM. Placeholder behaviour beside Latin text is recorded: Japanese
partner names appear inline after the Latin text.

Implication for translation: the partner name stays in katakana unless the name
table (`0x06095EC4`) or its glyphs are also localized (new unknown).
