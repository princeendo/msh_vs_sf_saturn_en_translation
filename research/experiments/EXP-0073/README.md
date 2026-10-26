# EXP-0073: Arcade-layout English attract captions (new caption maps)

Task: UI-003
Status: DONE
Confidence: CONFIRMED (static parse of all eight scripts, offline render of
every caption frame, cold-boot capture)

## Observation

- The `EXP-0071` captions keep the Japanese map, so the English sits wherever
  free characters were: FIGHT! off to the right, the first caption split
  across two Japanese slots, and THE FIGHT!! and UNITE AGAIN!! shortened or
  split.
- The user (2026-10-26): "The Saturn version doesn't have the same symmetry
  and wording as the PS1/Arcade version. Can we update it so that it
  matches?"
- The US arcade (`EXP-0067`) and PS1 (`EXP-0072`) captions: LEGENDARY /
  HEROES / UNITE AGAIN!!, AMAZING / TEAM BATTLES!, NEW HEROES / JOIN / THE
  FIGHT!!. Three 32-pixel lines at screen y 24, 88, 152 (64-pixel pitch),
  every glyph, space and `!` on a 28-pixel grid, each line centred.

## Hypothesis

The caption pages are built by section-A map updates of 32x32 macro cells.
Rewriting those updates gives each text cell its own macro, so any centred
layout fits within the caption's own glyph macros.

## Controlled Change

The eight `MVSOP*.ST2` files only: in each caption window, the NBG2 map
updates and the caption macros' tiles; the `EXP-0071` palette recolour is
unchanged.

## Prediction

The three arcade captions with the arcade's wording and line breaks, each line
centred, with no change outside the caption windows.

## Inputs and Provenance

- Source image: `local/disc_images/mshvsf_saturn_jp/` (manifest hashes);
  `MVSOP*.ST2` source hashes in `EXP-0071`.
- Layout: `data/ui003/attract_captions.json` (schema 2).
- Arcade layout measured from `local/ui003/fine_u/mshvsfu_f01531.png` and
  `local/ui003/mame/snap/mshvsfu_f02025.png`, `mshvsfu_f02355.png`.

## Tools and Environment

`tools/disc/st2_stream.py` (`script_frames`, new), `tools/disc/st2_encode.py`
(`map_encode`, new), `tools/disc/attract_captions.py` (rewritten), patched
Mednafen 1.32.1 agent, `tools/sh2/disasm.py`, Python 3.12.13.

## Procedure

1. Disassemble the frame dispatcher (`0x06021FE4`), the object-list
   interpreter (`0x06022426`) and the macro-cell builder (`0x0601FD70`).
2. Parse all eight decoded scripts into frames. Replay the NBG2 map updates
   statically and compare the caption pages with the save-state extracts.
3. Measure the arcade captions.
4. Rebuild: per slot, allocate macros, rewrite the window's map updates,
   paint the macros, re-encode.
5. Check offline: render every caption frame from the rebuilt files; compare
   the map state at every other frame with the original.
6. Build the US-names image, cold boot it, and capture (every 30 frames to
   frame 13,200; every 3 frames in 3,420-3,600 and 12,860-13,020).

## Actual Result

- **Frame format** (`0x06021FE4`): one big-endian command word per frame
  (0 = idle, `0xFFFF` = end of script); its bits select sections read in bit
  order:

  | Bit | Handler | Section |
  | --- | --- | --- |
  | 0 | `0x060220C0` | mask byte; a word per set bit of 4 (deltas at `+0xF000`) |
  | 1 | `0x060220E8` | two words |
  | 2 | `0x06022104` | mask byte; per set bit of 6 a byte, or a zero byte and a word |
  | 3 | `0x06022134` | two words |
  | 4 | `0x0602214C` | palette: flag byte; 3-byte lists (bits 0, 2, 4: fade up, fade down, brightness) and `[delta][count][words]` records (bit 5), each list ending at `0xFF` |
  | 5-7 | `0x06022338`/`40`/`48` | word-LZ map updates to `0x0602F020` / `0x06033020` / `0x06037020` |
  | 8 | `0x06022426` | object list: header word (bits 10-12 type, 13-15 subtype) plus 0-6 bytes, ending at `0xFF` |
  | 9 | `0x06022098` | mask byte; a word per set bit of 6 |
  | 10 | — | flag only |

  All eight scripts parse to their end (2,064 frames each; four have one
  trailing pad byte). All 183 map offsets traced in `EXP-0070` are parsed map
  sections.
- **Macro cells** (`0x0601FD70`): NBG2 index word k (`0x06037020`) and
  attribute word k (`0x06039020`: bits 5-6 flips, 0-4 palette) give a 32x32
  cell of four characters `base + 16 * index` + 0/4/8/12. Each half page is
  16x8 cells filled column by column (k = 512 * half + 8 * column + row).
- **Static maps.** Replaying the updates reproduces the four extracted caption
  pages in every cell except the flipped ones (16, 20 and 4 cells: the builder
  orders flipped cells differently). Slot frames are the same in all eight
  files:

  | Slot | Japanese | Build | Clear | Halves (scroll, palette) |
  | --- | --- | --- | --- | --- |
  | 1 | ヴァリアブル…, then 第2弾!! (frame 294) | 257 | 315 | top (16,16) 0; bottom (16,272) 1 |
  | 3 | 解き放て! | 734 | 753 | top (64,16) 0 |
  | 5 | 広がれ!! | 1044 | 1063 | top (80,16) 0 |

- **Macro origins differ per file.** The block offset of macro index 0,
  found by matching each file's caption macros against a save-state-verified
  file (slot 1: file 1; slot 3: file 1; slot 5: file 3), is unique in every
  case (all 35 or 69 caption macros match; the next offset matches one
  fewer): slot 1 `0x5EA0` in section C; slot 3 `0x7AA0` (files 0, 2, 6),
  `0x6220` (1, 3, 5, 7), `0x120` (4); slot 5 `0x7F20` (0), `0x75A0` (1),
  `0xF20` (2, 3, 6, 7), `0x96A0` (4), `0x7AA0` (5). The `EXP-0071` per-character
  deltas came from one cycle's states and do not hold for slot 3 in files 0,
  2, 4, 6 or slot 5 in files 0, 1, 4, 5.
- **Layout.** The Saturn screen is 352 pixels wide, so the arcade's 28-pixel
  grid does not fit UNITE AGAIN!! (362 pixels). The lines use the Saturn
  banner's 24-pixel grid (space and `!` included), centred on the screen, at
  screen y 16, 80, 144: one macro row each, 8 pixels above the arcade's.
  Macros used: 24 (slot 1, both halves share), 18 (slot 3), 22 (slot 5), of
  68, 34-35 and 34-35 free. Slot 1 shows the same caption in both halves, so
  it holds through the switch at frame 294.
- **Rebuild.** In each window the main update writes every planned entry and
  later updates keep the plan; unused free macros are blanked (section C did
  not fit otherwise: `0x18AD4` of `0x187F8` bytes).
- **Offline check.** For all eight files, every slot renders exactly the
  intended pixels at every frame of its window, and the NBG2 map state is
  identical to the original at every frame outside the windows.
- **Build.** Spec `e4a3e4aa…`, track 01 `db1ede9f…`; the compiler's `MVSOP`
  files equal the standalone rebuild.
- **Cold boot.** LEGENDARY / HEROES / UNITE AGAIN!! (`f002673`, `f33f0747…`),
  AMAZING / TEAM BATTLES! (`f006303`, `fd78378c…`) and NEW HEROES / JOIN /
  THE FIGHT!! (`dense5/f012929`, `d85ec89a…`; on screen for about six frames,
  as the Japanese caption). Comparison sheet with the original and the arcade:
  `local/ui003/verify/saturn_vs_arcade.png` (`57c3016f…`). The shots before
  and after each caption show normal scenes. This capture ran one frame out
  of phase with the baselines, so other screens were checked by inspection
  and by the offline map check.

## Conclusion

- **CONFIRMED:** the section-A frame format, the macro-cell map layout, and
  per-file macro origins; the static map replay.
- **CONFIRMED:** the Saturn attract mode now shows the arcade's three English
  captions with its wording, line breaks and centring.
- The `EXP-0071` per-character deltas are superseded.

## Uncertainty and Alternatives

- Letters are 24 pixels apart rather than the arcade's 28, and lines sit 8
  pixels higher.
- Blanked macros are assumed unused outside the caption windows; the offline
  check covers the NBG2 map only, and the cold-boot shots around each caption
  showed no artefacts.

## Reproduction

```sh
./invenv.sh python -m tools.disc.attract_captions --st2-dir local/ui003/st2 \
  --memfix <MEMFIX.PAC> --out-dir local/ui003/st2_en
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --out local/ui003/build/us_attract.json \
  --roster data/text/m5_roster.json --with-win-quotes --glyph-style credits \
  --caption-palette gold --ui-english --names us --attract-captions
```
