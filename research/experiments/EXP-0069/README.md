# EXP-0069: English attract captions with the win-banner letters (design and constraints)

Task: UI-003 (replacement)
Status: IN_PROGRESS (design measured; the map/palette codec work comes next)
Confidence: CONFIRMED (the constraints and the palette path below); the
mock-ups are a design, not yet in the game

## Observation

- The user's decision (2026-10-26): draw the English captions with the
  Saturn's own large win-banner letters, with no imported art, as close to
  the US arcade wording as fits.
- `EXP-0067`: US wording. `EXP-0068`: tiles, maps and codecs.

## Hypothesis

The English can be drawn into the existing caption tiles without changing the
maps or palettes.

## Controlled Change

None to the game. Analysis of the extracted maps and palettes, plus offline
mock-ups.

## Prediction

If the hypothesis holds, every caption has enough uniquely used tiles for its
English lines, and the colours can stay as they are.

## Inputs and Provenance

- `local/ui003/extract/cap1`-`cap4` (`EXP-0068`).
- `MEMFIX.PAC` quote font, win-banner letters `0x2E0`-`0x35F`.
- States `cap1.mcs`, `local/loc004/banner200.mcs`.

## Tools and Environment

Python 3.12.13 analysis scripts; `tools/memory/vdp2_plane.py`; patched
Mednafen 1.32.1 agent (write breakpoints).

## Procedure

1. Classify each caption page's map positions: blank (the shared background
   character), unique (character used once) or shared.
2. Render the banner letter set and measure each glyph's width. Read the
   banner palette (VDP2 CRAM bank `0x10`) and the caption palettes (CRAM
   `0x600`, `0x610`).
3. Find the caption palette's source: work-RAM copies, write breakpoints, the
   writer's code and its input.
4. Render mock-ups of the US wording.

## Actual Result

- **Letters.** The banner font has A-Z and `!` (`0x348`), `?` (`0x34A`),
  `.` (`0x34C`) and `-` (`0x34E`); digits 8 and 9 are at `0x2E0`/`0x2E2`.
  - Each letter is 2×2 quote-font cells (top-left t, t+1, t+0x10, t+0x11),
    32×32 px, drawn 24 px apart.
  - Letter code: t = `0x2E0 + 2 * (i % 8) + 0x20 * (i // 8)` with
    i = ASCII − 63.
  - Colours: bank `0x10` (1-10 yellow to orange, 11 dark purple outline).
- **Tile constraint.** Repeated Japanese characters (ー) share tiles, so only
  irregular bands are repaintable:
  - caption 1: 304×64 and 192×64;
  - caption 2: 224×96;
  - caption 3: 256×64, 128×64 and 64×128;
  - caption 4: 288×64 and 256×64.

  Most of the US wording fits, but not all: "THE FIGHT!!" does not.
- **Palette path.** The caption palettes are grey (palette 0) and red
  (palette 1) 16-level ramps:
  1. They are DMA'd from WRAM-H `0x06046C00`.
  2. Code at `0x0601FFD8` writes that copy by converting 16-bit `0xFRGB`
     values from an array at `0x0602E020` through a lookup table at
     `0x06060000`.
  3. That array is filled by the same word-LZ map codec from section A
     (`EXP-0068`).

  So the colours, and with them a yellow caption, live in the section-A map
  streams.
- **Mock-ups** (`local/ui003/mockup*.png`): centred US-style captions in the
  banner colours:
  - slot 1: LEGENDARY / HEROES;
  - slot 2: UNITE / AGAIN!!;
  - caption 3: NEW HEROES / JOIN / THE FIGHT!!;
  - caption 4: AMAZING / TEAM BATTLES!.

## Conclusion

- **DISPROVEN** (as the full solution): drawing into the existing tiles
  cannot place all the US wording, and cannot make the captions yellow.
- **Required next:** decode and re-encode section A's two map codecs (the
  bit-flag LZ `0x06022750` and the word LZ `0x0602234C`). That gives free
  placement, using new tiles as the budget allows, and palettes changed to
  the banner colours.
- Also required: a graphics-LZ encoder, with each block's compressed size
  kept within its sector space.

## Uncertainty and Alternatives

- The two-to-one mapping of the opening (ヴァリアブル… + 第2弾!! for LEGENDARY
  HEROES UNITE AGAIN!!) is the user's choice. The mock-ups split it into
  LEGENDARY / HEROES then UNITE / AGAIN!!.
- If the section-A route proves too costly, the fallback is white (grey-ramp)
  banner letters within the repaintable bands, with "FIGHT!" in place of
  "THE FIGHT!!".

## Reproduction

The analysis used scratch scripts over `local/ui003/extract/`. The mock-ups
are rendered from the `MEMFIX.PAC` banner glyphs and the CRAM bank `0x10`
colours.
