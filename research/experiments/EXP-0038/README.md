# EXP-0038: Which Video Path Draws Ryu's Ending Text

Task: END-002
Status: DONE (2026-10-24)
Confidence: CONFIRMED (VDP1 sprite path and glyph identity, for dialogue box 1
and ending page 1). The glyph routine is CONFIRMED for the box 1 → box 2
transition.

## Observation

`EXP-0037` showed Ryu's post-boss dialogue (four boxes at the top of the stage)
and three ending pages (bottom box), with 13-row glyphs on a 16-px grid. Nothing
was known about how they are drawn. The win-quote path (`EXP-0012`, `FONT-001`)
may not be assumed (`AGENTS.md` rules 13-14).

## Hypothesis

The glyphs of dialogue box 1 are drawn by VDP1 normal-sprite commands, one per
glyph cell.

A second hypothesis, formed from the passive result and tested separately: the
glyph cells are quote-font cells decoded by the `FONT-001` routine at
`0x0601CE00`.

## Controlled Change

| Step | Change |
| --- | --- |
| Passive | None. Read only: VDP1, VDP2, WRAM, and cart-RAM extraction from two checkpoints |
| Active A | Zero the 128 bytes of one VDP1 character cell (`0x0A780`, the cell of the line-2 glyph at cell 6) at `ending_dialogue_box1.mcs`, then run 2 or 60 frames |
| Active B | Zero one cell (`0x0BD80`, the first glyph of line 1) at `ending_page1.mcs`, then run 2 frames |
| Controls | The same load, pause, and frames with no write |
| Routine check | None. A PC breakpoint (log mode) on `0x0601CE00`, replayed from box 1 across the box 1 → 2 change |

## Prediction

- **Passive.** A set of normal sprites lies on the text grid, one per cell, and
  the non-blank cells correspond to the visible glyphs.
- **Active.** Zeroing one cell removes exactly that glyph from the screen, and
  nothing else in the box changes.
- **Font.** Every non-blank cell equals a decoded quote-font cell byte for byte.
- **Routine.** `0x0601CE00` runs once per new glyph when box 2 appears, with the
  glyph's code in R3 (as `FONT-001` documents for win quotes).

**Refuted if:** no sprite set matches the grid, zeroing a cell leaves its glyph
visible or changes other text, cells match no font cell, or the routine does
not run at the box change.

## Inputs and Provenance

- **Image:** untouched `local/disc_images/mshvsf_saturn_jp`, track 01
  `8274307f9562d2da…`.
- **Checkpoints (`EXP-0037`):**
  - `ending_dialogue_box1.mcs`, `949ee58d095d4376…`;
  - `ending_page1.mcs`, `a68b2da188428f57…`.
- **Emulator:** patched Mednafen 1.32.1 agent build, `fe0edb99f1ffe63a…`.
- **Dumps** (`tools/memory/mcs_extract.py`, Saturn byte order,
  `local/end002/dumps/<state>/`):

  | Region | Box 1 | Page 1 |
  | --- | --- | --- |
  | VDP1 VRAM | `57f53a4393c454ca…` | `50b9180b95a5b9b1…` |
  | WRAM-H | `dcc3c33ac7862f00…` | `c2aa3a88f5de2cfb…` |
  | Cart RAM | `cbae9444096f5f49…` | `cbae9444096f5f49…` (identical) |

  VDP1 and WRAM extraction is validated (`DBG-012`); cart RAM is not (see
  Uncertainty).

## Tools and Environment

- `tools/memory/vdp1_sprites.py`: command walk, local coordinates applied.
- New `tools/text/glyph_match.py` (test `tests/unit/test_glyph_match.py`). It
  lists the sprites with one color word in reading order, decodes the quote font
  from the base pointer at `0x0601D8E4`, and reports the font codes whose cell
  equals each sprite's 128 bytes.
- New `tools/mednafen/write_trial.py`. It loads a state, pauses, applies
  read-back-checked writes, runs N frames, takes a screenshot, and reports
  whether each write survived.
- `tools/mednafen/replay_state.py --bp`: breakpoint log.

## Procedure

```bash
CUE="local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue"
for s in ending_dialogue_box1 ending_page1; do
  ./invenv.sh python -m tools.memory.mcs_extract local/end001/checkpoints/$s.mcs \
    --out-dir local/end002/dumps/$s
done
./invenv.sh python -m tools.memory.vdp1_sprites \
  local/end002/dumps/ending_dialogue_box1/vdp1_vram.bin --json
./invenv.sh python -m tools.text.glyph_match local/end002/dumps/ending_dialogue_box1 --color-word 0x6030
./invenv.sh python -m tools.text.glyph_match local/end002/dumps/ending_page1 --color-word 0x61F0
./invenv.sh python -m tools.mednafen.write_trial "$CUE" \
  local/end001/checkpoints/ending_dialogue_box1.mcs local/end002/trial/box1_control.png --frames 2
./invenv.sh python -m tools.mednafen.write_trial "$CUE" \
  local/end001/checkpoints/ending_dialogue_box1.mcs local/end002/trial/box1_zero_ri_cell.png \
  --write 'vdp1vram:A780:00*128' --frames 2
./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
  local/end001/checkpoints/ending_dialogue_box1.mcs local/end002/bp_box2 \
  --steps 30 --step-frames 10 --bp pc:0601CE00-0601CE01
```

The active trials were first run by a one-off agent script, with the same
writes plus a 60-frame variant and page 1 (`local/end002/active/`). The
`write_trial.py` runs above reproduce box 1 (`local/end002/trial/`).

## Actual Result

### Passive: VDP1 sprites on a 19 × 2 grid

- **Dialogue box 1.** There are 38 normal sprites with color word `0x6030`:
  - 4 bpp (color mode 0), 16 × 16;
  - x = 26 + 16k for k = 0-18, at y = 14 and 30 (VDP1 coordinates);
  - every cell has a sprite, including blank ones.
- **Ending page 1.** The bottom box has 38 sprites with color word `0x61F0` on
  the same 19-cell x grid, at y = 178 and 194.
- **Screen mapping.** Screenshot rows = VDP1 y + 8 for both the text and the box
  border (`0x7040` sprites), and x is unchanged. So the grid origin x = 26 is the
  `EXP-0037` grid (x ≡ 12 mod 16, with ink starting 2 px into the cell).
- **Character addresses.**

  | Screen | Blank cells | Glyph cells |
  | --- | --- | --- |
  | Box 1 | One shared address (`0x32A80`) | One per distinct glyph: the repeated mark shares `0x0A700`; the three line-2 glyphs use `0x0A780`, `0x0A800`, `0x0A880` |
  | Page 1 | `0x0BD00` | 23 distinct glyph addresses at `0x0BD80`-`0x0C880`, consecutive 128-byte cells |

  The page 1 count matches the transcription's 23 distinct characters, so a
  repeated character shares one cell.
- **Glyph pixels.** Each cell has a main stroke (nibble `1`), a one-pixel
  drop shadow down and to the right (nibble `F`), and edge shades (`2`-`A`).
- **Picture panel.** On page 1, the picture is also VDP1 16 × 16 4 bpp tiles
  (color words `0x5190`-`0x51B0`, y 32-112). More `0x50xx`/`0x51xx` tiles at y
  160-208 lie behind the text box and are unexplained. The scrolling logo
  background has no VDP1 sprites, so it is presumably VDP2 (not tested).

### Font identity: byte-exact quote-font cells

- `glyph_match.py` read the font base `0x0278CF60` from `0x0601D8E4` in both
  states, the same as the `FONT-001` session. Cart RAM is identical in both
  states.
- **Every glyph cell matches exactly one code:** 15 of 15 in box 1 and 25 of 25
  on page 1. Reports: `local/end002/ending_dialogue_box1_match.json`
  (`d1fa1c1d…`) and `ending_page1_match.json` (`8d56e32d…`).
- The codes agree with the documented code system (`EXP-0031`, `EXP-0013`):

  | Glyphs | Codes |
  | --- | --- |
  | Punctuation ・ 、 。 | `0x08AE`, `0x08A9`, `0x08AA` |
  | Hiragana | `0x0800 + n` for U+3041 + n (の `0x082D`, が `0x080B`) |
  | Katakana, Shift-JIS order | リ ュ ウ = `0x089C 0x0897 0x0858` |

  Kanji fall in `0x09xx`-`0x0Cxx`.
- **No raw copies.** The 4 bpp cell bytes are not stored verbatim in WRAM or
  cart RAM, as expected for a compressed font. WRAM-H `0x0601CEEC`, the
  `FONT-001` staging cell, holds the last glyph built for each screen: the
  final glyph in box 1 and the final glyph on page 1.

### Active: one cell, one glyph

| Trial | Inside the box (x 18-333) | Elsewhere |
| --- | --- | --- |
| Box 1, zero `0x0A780`, 2 frames | 69 px differ, all in x 125-134, y 40-52: the line-2 cell-6 glyph is gone | Fighter area (see below) |
| Box 1, same write, 60 frames | The same 69 px only; the write survived, so cells are not refreshed | Animated stage |
| Page 1, zero `0x0BD80`, 2 frames | 150 px differ, all in x 107-120, y 187-200: the first glyph of line 1 is gone | Nothing |

- Each write read back exactly and was still present after the frames.
- **The fighter-area difference is not caused by the write.** Two box 1 control
  runs with no write differ from each other by the same 1,865 px (bbox x
  191-288, y 119-207). The idle animation lands on a different phase between
  launches, because the pause after `loadstate` is asynchronous.
- Only the text sprite references `0x0A780`, checked across all drawing
  commands, including scaled and distorted ones and color lookup tables.
- Screenshots: `local/end002/active/` and `local/end002/trial/`. Hashes:

  | Screenshot | SHA-256 |
  | --- | --- |
  | `active/box1_control.png` | `f28ea7304841c0a1…` |
  | `active/box1_zero_ri_cell.png` | `2166c40fe79e3845…` |
  | `active/box1_zero_ri_cell_60f.png` | `1840496a4fd846d8…` |
  | `active/page1_control.png` | `d24d4863391e5186…` (equal to live frame 70,481 of `EXP-0037`) |
  | `active/page1_zero_first_glyph.png` | `6e7bac332ee2ee34…` |
  | `trial/box1_control.png` | `a875c7c1b4d4c9ba…` |
  | `trial/box1_zero_ri_cell.png` | `c712fda5ab6a57ba…` |

### Routine check: `0x0601CE00` builds each new glyph

- The breakpoint log (`local/end002/bp_box2/events.log`, `b477b32c…`) shows 12
  hits, all in one frame, when box 2 appears. PR is `0x0601CDE2` for every hit.
- **R3 holds a code each time.** The 12 codes are box 2's distinct characters in
  reading order:
  `0970 080B 09F8 082A 0823 0803 0825 080E 084A 0827 082E 0829`.
  Box 2's trailing ・ (`0x08AE`) is not rebuilt; it is already in VRAM from box
  1.
- **R9 is the VDP1 destination.** It advances by `0x80` per glyph, from
  `0x25C0DD80` (VDP1 VRAM `0x0DD80`).
- **R1 steps through a WRAM-L table** from `0x00260E5E`. It holds slot numbers
  (`0x00BB`, `0x00BC`, …; `0x1BB × 0x80 = 0xDD80`) with `0xFFFF` gaps.
  - The table is already filled while box 1 is showing (box 1 dump), with
    entries running past box 2.
  - That suggests that VRAM slots for the upcoming boxes are assigned ahead of
    time (`HYPOTHESIS`; for `END-003`/`END-004`).
  - R1 is a slot table, not the text.

## Conclusion

- **CONFIRMED** for dialogue box 1 and ending page 1:
  - The ending text is drawn by VDP1 normal sprites, 16 × 16 4 bpp, one per
    cell, on a 19-cell × 2-line grid (x = 26 + 16k).
  - Each glyph's character data is a byte-exact quote-font cell (font base
    `0x0278CF60`), built by the `FONT-001` routine at `0x0601CE00` through the
    staging cell `0x0601CEEC`.
  - Cells are uploaded once per screen, with one cell per distinct glyph.
- **The text is therefore handled as quote-font codes.** The routine receives
  them in R3 from a caller that returns to `0x0601CDE2`.
- This is a **measured** result, not an equivalence assumed from win quotes. It
  still does not say where the codes come from, how they are stored on disc, or
  whether the same line layout or length limits as win quotes apply.
- **Consequence for M7:** if the codes come from a disc table, changing them and
  reusing the composed pair glyphs (`FONT-003`) is a plausible route. That is
  not yet tested.

## Uncertainty and Alternatives

- **Coverage.** Only box 1 and page 1 were inspected in full. Box 2 was checked
  through the routine log only. Pages 2-3 and boxes 3-4 are assumed by
  similarity, not tested.
- **Cart RAM.** Its extraction is unvalidated (`DBG-012`). The 40 byte-exact
  matches against validated VDP1 cells corroborate the decoded glyph bytes, but
  not the rest of the cart region.
- **Unexplained:** the `0x50xx`/`0x51xx` tiles behind the page 1 text box, and
  the background layer (presumably VDP2).
- **Not assumed:** line capacity. Ending lines reach 16 glyphs in this run. The
  grid is 19 cells, as for win quotes, but whether ending lines may use all 19
  cells (or more lines) is untested.

## Reproduction

See Procedure. The checkpoints and their hashes are in `EXP-0037`. The grid,
codes, and diff boxes above are reproducible from those states with no
gameplay.
