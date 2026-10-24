# EXP-0041: Marker Builds of the Ending Files

Task: END-007
Status: DONE (2026-10-24)
Confidence: CONFIRMED. Edited `ME.PAC`/`MC13.PAC` on a derived image load into
RAM with only the marker changed (Part 1). The page marker is seen on screen in
a live run from the derived image (Part 2).

## Observation

`EXP-0040` traced:
- the ending pages to raw `ME.PAC`, copied to `0x00230000`;
- the post-boss dialogue to LZSS `MC13.PAC`, decoded to `0x00220000`.

Both load at the `STAGE-08` transition. `EXP-0039` showed that a code written
into those RAM records displays.

## Hypothesis

A derived image built from the untouched source, with one marker code changed
in one file, loads that file at `STAGE-08`. The marker reaches RAM, and the
ending shows it. No second copy, checksum, or length check intervenes.

## Controlled Change

One code per file, both set to full-width R (`0x08F9`, `FONT-002`):

| Build | File | Location | Original | Modified | Purpose |
| --- | --- | --- | --- | --- | --- |
| A | `ME.PAC` | File offset `0x367E` (RAM `0x0023366E`) | `09AD` | `08F9` | Page 1, line 1, cell 5 |
| B | `MC13.PAC` | Decoded offset `0xAE62` (RAM `0x0022AE62`) | `0970` | `08F9` | Box 2, line 1, cell 1 |
| C | Both of the above | | | | For the Part 2 live run |

## Prediction

- **Load.** Replaying the pre-load checkpoint on A or B gives the same RAM as
  the untouched image in both file regions, except that file's marker word.
- **Display.** The marker word in RAM shows R in exactly that cell. This was
  shown for box 2 in `EXP-0039` T1 and is shown here for page 1.
- **No re-read.** The post-KO checkpoint shows no marker on A or B, because
  both files load only at `STAGE-08`.

**Refuted if:** other bytes differ, the marker is absent from RAM, or the
derived image fails to load.

## Inputs and Provenance

- **Source:** untouched image, track 01 `8274307f9562d2da…`. All 13 components
  were checked against `references/mshvsf/saturn_jp/README.md` by
  `patch_image`.
- **Source files:** cut from the source by LSN, hashes as in `EXP-0040`.
  - `ME.PAC`: `77210963…`.
  - `MC13.PAC`: `05263ab6…`, decoded `9eb9b7c6…`.
- **Checkpoints (`EXP-0037`/`EXP-0039`):**
  - `before_stage08_load.mcs`, `bed2673fb2e47201…`;
  - `ryu_gouki_post_boss_ko.mcs`, `f42218550c0fb23c…`.
- **Emulator:** agent build `fe0edb99f1ffe63a…`.

## Tools and Environment

- `tools/disc/pac_patch.py`: for `MC13`, with `--full`.
- `tools/disc/patch_image.py`.
- `tools/mednafen/write_trial.py`: new `--dump DIR` option, which saves WRAM-L
  and WRAM-H after the frames.
- A short inline script for the raw `ME.PAC` edit. It checks the original
  bytes, then writes `build/end007/ME.PAC` and `me_patch.json`.

## Procedure

```bash
# A: raw same-size edit (inline), recorded in build/end007/me_patch.json
# B: MC13 re-encode
./invenv.sh python -m tools.disc.pac_patch local/end004/disc/MC13.PAC \
  --write 0xAE62=0x08F9 --out build/end007/MC13.PAC \
  --manifest build/end007/mc13_patch.json --full
T="Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
./invenv.sh python -m tools.disc.patch_image --source-dir local/disc_images/mshvsf_saturn_jp \
  --manifest references/mshvsf/saturn_jp/README.md --track "$T" \
  --file "ME.PAC;1" --data build/end007/ME.PAC --out-dir build/end007_a
# The same for B (MC13 only) and C (both files).
N="Marvel Super Heroes vs. Street Fighter (Japan).cue"
for d in local/disc_images/mshvsf_saturn_jp build/end007_a build/end007_b build/end007_c; do
  ./invenv.sh python -m tools.mednafen.write_trial "$d/$N" \
    local/end001/checkpoints/before_stage08_load.mcs local/end007/load/<k>.png \
    --frames 600 --dump local/end007/load/<k>
done
./invenv.sh python -m tools.mednafen.write_trial "local/disc_images/mshvsf_saturn_jp/$N" \
  local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs local/end007/display/page1_ram_R.png \
  --frames 1650 --write workraml:3366E:08F9
```

Each display run was paired with a control: the same command without
`--write`, or on the untouched image.

## Actual Result

### Builds

- **`MC13` re-encode.**
  - The splice re-encode was refused: 31,044 bytes, more than the file's
    31,036, because `MC13` has only 1 byte of slack.
  - `--full` re-encoded the whole stream to 30,569 bytes. The declared length
    was kept at 31,011 (`EXP-0036` rule), with 443 zero-fill bytes.
  - The header is unchanged: `00000000 8000792B 00000000 00000000 00007923
    0000EE72`.
  - It decodes offline to the patched data: decoded `aa4d04b1…`, file
    `0d1c4650…`, manifest `ce3146b4…`.
- **`ME.PAC` edit:** file `d4fb288f…`, manifest `ffafe20e…`.

| Build | Track 01 SHA-256 | Changed sectors | Build manifest |
| --- | --- | --- | --- |
| A | `f2f8f673152221a6…` | 1 (LSN 3930) | `6b01e89de2e9e934…` |
| B | `d525e356702a1ca0…` | 16 (LSN 11100-11115) | `9e6d4cd583a06d35…` |
| C | `276bd6c73819903b…` | 17 | `134a050dbbc97a44…` |

In every build, tracks 02-12 and the CUE are byte-identical to the source.

### Load path (pre-load checkpoint, 600 frames, no input)

Comparison regions: `MC13` decode `0x00220000-0x0022EE71`, and the `ME.PAC`
body `0x00230000-0x0023ED03`.

| Image | Differing bytes vs the untouched run | Marker words |
| --- | --- | --- |
| A | 2: `0x0023366E-6F` only | page `08F9`; box `0970` (unchanged) |
| B | 2: `0x0022AE62-63` only | box `08F9`; page `09AD` (unchanged) |
| C | 4: both marker words only | both `08F9` |

- Everything else in both regions is identical across the four runs. That
  includes the relocated pointers and the 30 unexplained longwords of
  `EXP-0040`.
- Dumps (`local/end007/load/<k>/workraml.bin`):

  | Run | SHA-256 |
  | --- | --- |
  | Untouched | `ebb2314d…` |
  | A | `286e8ca0…` |
  | B | `4a9454f5…` |
  | C | `616ef111…` |

### Display of the same RAM change

| Trial | Inside the box | Result |
| --- | --- | --- |
| Page 1 RAM `0x0023366E` → `08F9` (untouched image, post-KO + 1,650 frames) | 145 px, x 107-120, y 187-200 | R in place of the first glyph of line 1, the rest unchanged (`page1_ram_R.png`, `e19b6752…`; control `d24d4863…`) |
| Box 2 RAM `0x0022AE62` → `08F9` | (`EXP-0039` T1) | R in cell 1 only |

### No re-read after the KO

- Post-KO replays on image A (1,650 frames) and image B (760 frames) are
  pixel-identical to the untouched controls (`d24d4863…` and `38ea9a4e…`; both
  hashes equal earlier runs). Neither file is re-read between the KO and the
  ending.
- The loader context's name field over run 1 reads `me.pac` (before the boss
  stage), `end.pac` (after it), `sel.pac` (character select after the
  continue), and `end.pac` again after the continue.
  - So the boss-stage load sequence repeats after a continue, and it also
    opens `END.PAC` (LSN 3,757, 340,632 bytes, content not examined).
  - Whether `ME.PAC`/`MC13` are re-read after a continue is not shown.

## Conclusion

**CONFIRMED (Part 1).**
- A same-size raw edit of `ME.PAC`, or a full LZSS re-encode of `MC13.PAC` that
  keeps the declared length, builds from the untouched source.
- The image loads at `STAGE-08`, and the edited code reaches the ending's RAM
  record with nothing else changed.
- That RAM change displays as the marker in exactly its cell.

**CONFIRMED (Part 2).** In a live run from the derived image, the page marker
appears in exactly its cell, and pages 2-3 are unchanged. The `MC13` path is
confirmed in RAM (Part 1), and the same RAM change displays (`EXP-0039` T1).
Ryu/Ken does not show the Ryu/Gouki box 2, so the `MC13` marker was not seen
on screen in a derived-image run.

## Part 2: Live Run on Image C (2026-10-24)

- **Setup.** The agent launched `build/end007_c` (track 01 `276bd6c7…`) and
  loaded `before_stage08_load.mcs`, with `session_recorder.py` on
  (`local/end007/run2/rec`).
  - After the load, RAM read back `08F9` at both `0x0022AE62` and `0x0023366E`.
  - The user lost the first attempt. The agent reloaded the same state, and
    the files loaded from image C again.
  - Ryu (point, team Ryu/Ken) won and landed the KO. No other input.
- **Page 1 shows R at line 1 cell 5.** The screenshot `f00011597.png` is
  byte-identical (`e19b67528856ba79…`) to Part 1's RAM-trial screenshot
  `page1_ram_R.png`.
  - Inside the text box, it differs from the untouched Ryu/Gouki run's page 1
    (`EXP-0037` `f00070481.png`) in 145 px at x 107-120, y 187-200: the marker
    cell only.
  - The picture panel is identical.
- **Pages 2 and 3 are pixel-identical** inside the box to the untouched run.
  Page 3's `f00012465.png` is byte-identical to `EXP-0037` `f00071824.png`
  (`312498fe…`).
- **The box 2 marker is not applicable.** The Ryu/Ken dialogue uses different
  boxes 1-2 (other lines), so the edited Ryu/Gouki record is not shown. That
  is the anticipated outcome, not a refutation.
- **Dialogue compared with Ryu/Gouki** (inside the top box, against
  `EXP-0037`):
  - Box 4 is pixel-identical (`f00011249.png`).
  - Box 3 differs only at x 107-161, in line 1's name cells: the partner's
    name instead of Gouki's (`f00011024.png`, 298 px).
  - Boxes 1-2 are different lines.
  - These are observations for `END-005`, not a controlled test there: the
    image (one marker per file) and the partner both differ from `EXP-0037`.
- **Checkpoint:** `local/end001/checkpoints/ryu_ken_post_boss_ko_imageC.mcs`
  (`b1ef3827ba0b31be…`), at the Ryu/Ken KO. Its RAM holds
  image C's marker words.

## Uncertainty and Alternatives

- **Composition.** The end-to-end claim rests on two measured links (disc to
  RAM, RAM to screen) and determinism. A rendering path that reads the disc
  copy again would be missed. No such read was seen after the KO.
- **Full re-encode.** It replaces `MC13`'s whole stream. The other files and
  quotes loaded from `MC13` were compared only in RAM (identical), not
  displayed.

## Reproduction

See Procedure. Part 1 needs no gameplay.
