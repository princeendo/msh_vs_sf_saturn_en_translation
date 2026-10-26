# EXP-0066: Attract-mode teaser screens (inventory and source)

Task: UI-003 (inventory and sources)
Status: DONE (inventory). UI-003 continues with the oracle and the
replacement.
Confidence: CONFIRMED (screens and timing from a cold boot; the source by a
write breakpoint and an exact data match)

## Observation

The user reports that the attract mode's teaser screens, before the gameplay
demo, show a lot of Japanese.

## Hypothesis

The teasers are a fixed set of screens that repeats each attract cycle. Their
Japanese is art loaded from a disc file that can be found by tracing it back
from video RAM.

## Controlled Change

None to the game. A cold boot without input, captured and traced.

## Prediction

A full cycle shows a small set of Japanese caption screens. Each comes from
one identifiable file.

## Inputs and Provenance

- Image `build/regression/m8_roster_gold/build/image_a` (reference
  `m8_roster_gold`). The attract files are unmodified by the translation.
- Cold-boot capture: `local/ui003/cycle/` (21,000 frames, a screenshot every
  30 frames and a state every 600).

## Tools and Environment

- Patched Mednafen 1.32.1 agent, with scratch scripts for the capture, a
  6-frame fine scan, write breakpoints and state saves.
- `tools/memory/mcs_extract.py`, `tools/memory/vdp1_commands.py`.
- Python 3.12.13.

## Procedure

1. Cold boot and capture 21,000 frames. Find frames that are mostly black
   with white or red text.
2. Fine-scan one full cycle every 6 frames from state `f002532`, keeping each
   distinct caption frame.
3. Save a state during the first caption (`f002532` + 142,
   `local/ui003/cap1.mcs`, `5e025d05…`). List VDP1 sprites and decode the
   VDP2 layer registers.
4. Search every disc file (raw and LZSS) for chunks of the caption tiles in
   VDP2 VRAM. Then search work RAM and cart RAM.
5. Write breakpoints on the VDP2 VRAM tiles, then on the WRAM-H copy, from
   `f001909` for 650 frames.
6. Search every disc file for the decompressor's input stream (WRAM-L
   `0x002428EB`, from a state at `f001909` + 600).

## Actual Result

- **Cycle.** The attract mode repeats about every 3,146 frames. Each cycle
  shows the same four Japanese caption screens: large text on black, with
  "PRESS START BUTTON" below.

  | # | Caption | Rough meaning | Colour | Example frame |
  | --- | --- | --- | --- | --- |
  | 1 | ヴァリアブル / ヒーロー / バトル | "Variable Hero Battle" | white | `f002674` (`5552f44e…`) |
  | 2 | 広がれ!! / ヒーロー / ワールド | "Spread out!! Hero World" | white | `f003447` (`12ff9c4a…`) |
  | 3 | 第2弾!! | "Part 2!!" | red | `f005850` (`1b75e79b…`) |
  | 4 | 解き放て! / 友情パワー | "Unleash it! The power of friendship" | white | `f012614` (`62aa88d8…`) |

  Also seen:
  - a **Norimaro** screen: red Japanese brush lettering above the English
    "NORIMARO CHALLENGES IMPOSSIBLE" (`f004574`, `00f2235a…`). Out of scope
    without approval (`AGENTS.md` rule 24, `SPECIAL-001`);
  - the rest is logos (SEGA, CAPCOM, MARVEL COMICS), the intro animation,
    rankings and the demo fight, all English or wordless.
- **Rendering.** No VDP1 sprites are drawn at the caption. All four NBG
  layers are in cell (tile) mode (`BGON 0x000F`, no bitmap). The caption is
  4bpp VDP2 tiles from VRAM `0x6000`, so it is not a movie frame.
- **Source.**
  - The caption tiles are not stored raw or as LZSS in any file. They are in
    WRAM-H at `0x06086020`+ at the caption.
  - No CPU writes reach the VDP2 tiles, so they arrive by DMA.
  - The WRAM-H buffer is written first by `0x0600CD60` (frame 469 after
    `f001909`), then by a decompressor at `0x06021F0C`/`0x06021F44`
    (frame 648): an LZ copy with R9 = output, R1 = R9 − `0x12`, and the
    input near WRAM-L `0x002428EB`.
  - That input stream is in **all eight `MVSOP0`-`MVSOP7.ST2`** files, at
    `0x4A0EB`-`0x518EB` (file `MVSOP0.ST2` `0x500EB`).

## Conclusion

**CONFIRMED:** the attract mode has four Japanese teaser captions per cycle.
They are VDP2 tile graphics, LZ-compressed in the opening stream files
`MVSOP*.ST2` (eight variants; the same caption data at nearly the same
offset in each). The game decompresses them to WRAM-H `0x06086000` and DMAs
them to VDP2 VRAM `0x6000`.

## Uncertainty and Alternatives

- The `.ST2` container layout and the LZ format are not decoded. The
  decompressor is at `0x06021F0C`-`0x06021F48`.
- Whether the eight `MVSOP` files are chosen per boot, per cycle or per
  region, and whether all hold identical caption data, is not known.
- The US releases' versions of these screens are not recorded yet: the US
  arcade (`mshvsfu`) in MAME and the PS1 US release.

## Next Experiments

1. **Oracle:** record the US arcade attract (MAME `mshvsfu`) and, if
   possible, the PS1 US attract at the same points.
2. **Decode:** the `MVSOP*.ST2` stream layout and the LZ codec (disassemble
   `0x06021F0C`), then the caption tile set and its VDP2 map.
3. **Plan with the user:** English art per caption (from the US releases,
   or drawn in the same style), then re-encode and rebuild.

## Reproduction

The capture, fine scan, breakpoint and save scripts are scratch agent
scripts; their parameters are under Procedure. Evidence is in `local/ui003/`
(`cycle/`, `fine/`, `cap1*`, `pre*`, `bp_vram/`, `bp_buf/`).
