# EXP-0071: English attract captions in the existing tiles, recoloured in place

Task: UI-003
Status: DONE (superseded for layout by `EXP-0073`; its palette recolour is
still used)
Confidence: CONFIRMED (offline round trips, image checks, and a cold-boot
comparison against two baseline runs)

## Observation

- `EXP-0069`: the caption pages leave irregular bands of characters that are
  used once, and the Saturn's win-banner letters fit most of the US wording
  there; "THE FIGHT!!" does not fit.
- `EXP-0070`: the caption palettes come from section A's compressed command
  script. Capcom's encoder leaves `0x18` bytes free in `MVSOP6`, and the
  optimal encoder (`tools/disc/st2_encode.py`) gains about 4 KB per file.
- The user chose the middle route (2026-10-26): banner letters drawn into the
  existing tiles, FIGHT! instead of THE FIGHT!!, and yellow from palette
  values edited in place.

## Hypothesis

Painting banner letters into the caption characters, and changing only the
colour values of the script's caption palette loads, gives yellow English
captions without changing any map, script command, timing, or other scene.

## Controlled Change

The eight `MVSOP*.ST2` files only:

- caption characters in section C (captions 1-2) and in one `MISS`-stream
  block per caption (3-4), re-encoded in place;
- 14 words in each of NBG2 palette lines 0x600 and 0x610, in the three full
  palette loads per file that start the caption scenes; section A re-encoded
  in place.

## Prediction

- Each caption shows its English lines in the banner's yellow-to-orange
  colours with the purple and cyan outlines, on the same background.
- No other attract screen changes.

## Inputs and Provenance

- Source image: `local/disc_images/mshvsf_saturn_jp/` (manifest hashes).
  `MVSOP*.ST2` SHA-256 (source → built):

  | File | Source | Built |
  | --- | --- | --- |
  | `MVSOP0.ST2` | `9e72b60b…` | `d76a0033…` |
  | `MVSOP1.ST2` | `df9b4310…` | `f8f6dc86…` |
  | `MVSOP2.ST2` | `d22256f9…` | `019d7267…` |
  | `MVSOP3.ST2` | `f4ea3622…` | `59f9ab2d…` |
  | `MVSOP4.ST2` | `2eca40da…` | `1084b1da…` |
  | `MVSOP5.ST2` | `40cd8096…` | `a952c411…` |
  | `MVSOP6.ST2` | `a4907878…` | `3592c0d5…` |
  | `MVSOP7.ST2` | `05009e63…` | `a51d2077…` |

- Caption page maps (local, from `EXP-0068` states; reduced to the committed
  `cells`): `cap1` `5e53eb0c…`, `cap2` `862e2909…`, `cap3` `38a73e19…`,
  `cap4` `6bb2a8ab…`.
- Layout: `data/ui003/attract_captions.json`.
- Banner glyphs: `MEMFIX.PAC` font (`FONT_ENTRY`), codes `0x2E0`+.

## Tools and Environment

`tools/disc/attract_captions.py` (new), `tools/disc/st2_encode.py` (new),
`tools/disc/st2_stream.py`, `tools/text/official_endings.py
--attract-captions`, `tools/text/caption_compiler.py`, patched Mednafen 1.32.1
agent, Python 3.12.13.

## Procedure

1. **Palette records.** Disassemble the palette command (`0x060221F8`): records
   of `[u16 index delta][u16 count][count words]`, the index running on from
   the previous record's end, until a `0xFF` byte. Each record marks its
   16-word lines dirty at `0x0603D048 + line`.
2. **Trace records** (breakpoint `0x06022218`: r2 = index, r3 = count, r12 →
   first word) from cycle state `f001909` for 3,400 frames: 2,076 records.
   Locate each in the decoded scripts (ring offset = script offset mod
   `0x2000`).
3. **Colour format.** The converter (`0x0601FFD8`) writes
   `table[word]` from a 64K-entry table at `0x06060000`. Read the table.
4. **Who else uses lines 0x600/0x610.** Classify every full load
   (`0000 0800`) per file; render NBG2 and force the lines magenta in the
   Spider-Man scene.
5. **Paint and rebuild** (`attract_captions build`), check by decoding.
6. **Generate and compile** the US-names build with `--attract-captions`.
7. **Cold-boot compare** the new image with `m8_roster_gold_us`: a screenshot
   every 30 frames for 13,200 frames from power-on, no input (four captures
   per image: `local/ui003/verify/{new,new2,new3,base,base2}`). The baseline
   was captured twice to measure run-to-run jitter.

## Actual Result

- **Palette words are `0xFRGB`.** The table maps each nibble n to the 5-bit
  level [0, 2, 4, 6, 8, 10, 12, 14, 17, 19, 21, 23, 25, 27, 29, 31]; the top
  nibble is a brightness (`F` = full). All 14 banner colours (CRAM `0x11`-
  `0x1E`) convert exactly: `FFF0 FFE0 FFD0 FFC0 FFB0 FFA0 FF90 FF80 FF70 FF50`
  (yellow to orange), `F206` (purple), `F0CC F1AA F278` (cyan outline).
- **Caption colours.** Every background character is solid colour 1. The
  banner glyphs use colours 1-9 and 11-14, so they are drawn as caption
  colours n + 1 (2-15), and colour 1 stays the background.
- **Palette slots are shifted by one.** The converter's first write is to
  `@(2, r13)`: array word k goes to CRAM slot k + 1, so caption colour c
  shows array word c - 1. The background (colour 1) is word 0 (`f000`,
  black), and banner colour n belongs in word n (words 1-14). The first
  builds wrote words 2-15 and showed every colour one step off (see the
  colour check below).
- **The caption lines are shared.** Lines 0x600-0x61F are loaded with the grey
  and red ramps by a full 0x800-word load at the start of five scenes per
  file, and are animated in other scenes (for example frames 796-838 after
  `f001909`). Each file has exactly five such loads, at matching script
  positions; in `MVSOP6`: `0x13164`, `0x1B5EE`, `0x26C8B`, `0x2DBDF`,
  `0x3CDA1` (traced at frames 735, 1023, 1214, 1334 and 1525 after
  `f001909`).
  - In the Spider-Man scene (the 2nd load), NBG2 uses palette 0 only for empty
    cells, and with lines 0x600-0x61F forced magenta (the CRAM copy at
    `0x06046C00` read back magenta) no magenta pixel appears.
  - **Which loads are captions** (from the cold-boot captures, each cycle
    about 3,150 frames): caption 1 or 第2弾!! at the 1st load; 解き放て! 480
    frames later (the 3rd, 735 → 1214); 広がれ!! about 790 frames later (the
    5th). The 4th (1,320 frames after caption 1) starts the Akuma/Chun-Li
    lightning scene, which fades the ramps into its own colours.
- **Paint.** All four layouts paint without conflicts. Characters shared
  between cells receive identical blocks (blank), and text never lands on a
  background cell. Final page positions (centre x, top y):
  - caption 1 (scroll 16,16): LEGENDARY (192, 32), HEROES (192, 64);
  - caption 2 (16,272): UNITE (192, 336), AGAIN!! (192, 368);
  - caption 3 (80,16): NEW HEROES (256, 32), JOIN THE (256, 64), FIGHT!
    (320, 160, advance 22), the only feasible place for FIGHT!;
  - caption 4 (64,16): AMAZING (240, 32), TEAM (240, 64), BATTLES! (240, 128).
- **Rebuild.** Three loads recoloured per file (168 bytes of script).
  Section A shrinks by about 0x1000-0x1200 bytes in each file (`MVSOP6`:
  `0x27FE8` → `0x26FD0` of `0x28000`). Section C grows from `0x182D5` to
  `0x1834F` (`MVSOP0` `0x1834B`, `MVSOP2` `0x182E0` → `0x18357`) into its own
  zero padding (`0x187F8` usable; the header size is updated). Every caption
  block shrinks and keeps its header size, so the `MISS` block chain, section
  B and all non-`MISS` sectors are byte-identical. Every changed part decodes
  back to the intended data.
- **Build.** `local/ui003/build/us_attract.json` (`db8d699d…`) compiles to
  `build/ui003/us_attract/image_a`, track 01 `0f87cc6d…`. The compiler's
  patched `MVSOP` files equal the standalone rebuild, only patched bytes
  change, and the image checks pass (Mode 1, EDC/ECC, 414 files).
- **Cold boot, first attempt (all five loads recoloured; DISPROVEN as safe).**
  The Akuma/Chun-Li lightning background turned beige instead of cyan.
- **Second attempt (1st and 5th only).** AMAZING TEAM BATTLES! stayed white:
  its scene starts at the 3rd load.
- **Third attempt (1st, 3rd, 5th; words 2-15).** All four captions appear,
  and the two baseline runs differ from each other in 72 of 440 frames
  (animation phase: title lightning, demo fights, star fields). The new image
  differs from both baselines in 36 frames: the 8 caption frames, and 28 of
  those same jitter kinds, with no palette change outside the captions on
  inspection.
- **Colour check against the arcade (user report: "the colors seem really
  off").** In the `mshvsfu` caption (`local/ui003/fine_u/mshvsfu_f01531.png`)
  the most common letter colours are purple (34,0,102) 4,305 px, yellow
  (255,255,0) 3,721 px and cyan (0,204,204) 3,252 px, then the oranges down
  to `FF70`: the banner colour set. The third build instead showed dark grey
  (32,32,32) where the yellow belongs, orange `FF50` (never used by the
  glyphs) where the purple belongs, and purple where the cyan belongs: every
  colour one slot off.
- **Final (words 1-14).** LEGENDARY HEROES now shows purple (32,0,96)
  2,248 px, yellow (248,248,0) 2,100 px, cyan (0,200,200) 1,697 px: the
  arcade's order. Evidence (local): `captions_before_after.png`
  (`90d58b82…`), `arcade_vs_saturn_zoom.png`; frames (`verify/new4/shots`)
  `f002674` LEGENDARY HEROES `1c845a83…`, `f005854` UNITE AGAIN!!
  `afed4d3f…`, `f006304` AMAZING TEAM BATTLES! `05cb02df…`, `f012934` NEW
  HEROES JOIN THE FIGHT! `0b1027b0…`. This capture runs one frame out of
  phase with the baselines, so the other-scene check rests on the third
  attempt, which recoloured the same three loads.

## Conclusion

- **CONFIRMED:** the middle route. Banner letters painted into the existing
  caption characters, and caption colours set in the three caption-scene
  palette loads, give the four English captions in yellow, with no map,
  command, timing or other-scene change detected.
- **DISPROVEN:** that every grey/red-ramp palette load belongs to a caption
  (the 4th load feeds a character scene's lightning).
- The tool is `tools/disc/attract_captions.py`, and the generator option
  `official_endings --attract-captions`.

## Uncertainty and Alternatives

- The caption maps come from save states of one cycle. All four captions
  rendered correctly in the cold-boot capture, which covers every caption
  slot at least once, but not every `MVSOP` file in every slot.
- The 2nd load (Spider-Man) is left unchanged, though recolouring it showed
  no effect.
- Screenshot jitter between runs means the "no other change" check is by
  inspection of the 28 non-caption frames, not exact equality.
- FIGHT! sits to the right of the other lines: no other position has free
  characters (searched over centre x 160-380, top y 96-200, advances
  20-24).

## Reproduction

The cold-boot captures used a scratch script (cold boot; one screenshot every
30 frames for 13,200 frames; `local/ui003/verify/`).

```sh
./invenv.sh python -m tools.disc.attract_captions derive --maps local/ui003/extract
./invenv.sh python -m tools.disc.attract_captions build --st2-dir local/ui003/st2 \
  --memfix <MEMFIX.PAC> --out-dir local/ui003/st2_en
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --out local/ui003/build/us_attract.json \
  --roster data/text/m5_roster.json --with-win-quotes --glyph-style credits \
  --caption-palette gold --ui-english --names us --attract-captions
./invenv.sh python -m tools.text.caption_compiler local/ui003/build/us_attract.json \
  --candidates data/text/font_candidates.json --out-dir build/ui003/us_attract
```
