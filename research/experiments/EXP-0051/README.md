# EXP-0051: The Staff-Credits Font, and How It Compares with the US Caption Font

Task: FONT-010
Status: DONE (2026-10-25)
Confidence:
- **CONFIRMED:** where the credits font is and how it is drawn.
- **SUPPORTED:** the visual similarity to the US arcade caption font (by
  inspection, not measurement).

## Observation

- The user noted that the staff credits use a font much like the one the US
  arcade uses for post-fight captions and endings, and asked to use it instead
  of the white font (`FONT-010`, high priority).
- The credits after the Vega ending (`local/end026/rec`, frame `f00009966`,
  `6fc4e105…`) show a gold, shaded, slanted Latin font with upper and lower
  case.

## Hypotheses

1. The credits font can be located (file, format, codes) from a credits
   checkpoint, with no gameplay.
2. It resembles the US arcade caption font.

## Procedure

No gameplay. The recorder's states from the `END-026` session were replayed:
`local/end026/rec/states/f00006862.mcs` (credits start) and `f00009676.mcs`.

`build/end026` had been removed from `build/` meanwhile (see Uncertainty). Its
replays used `build/regression/m8_roster/build/image_a` instead. That image is
byte-identical to the live-verified `build/end027`; credits assets are not
touched by any build.

1. **Capture.** Load `f00009676`, run 290 frames, and dump a screenshot, VDP1
   VRAM, VDP2 VRAM, and WRAM-L/H through the agent interface. (One-off script;
   the agent's `read` length is decimal.) The screenshot equals the recorder's
   frame exactly (`6fc4e105…`).
2. **Sprite list:**

   ```bash
   ./invenv.sh python -m tools.memory.vdp1_commands <vdp1vram.bin> --font <MEMFIX.PAC>
   ```

3. **Disc search.** Search every file (raw, and LZSS-decoded where possible)
   for the 16 × 16 tiles and for their 8 × 8 quadrants.
4. **Upload path:**
   - CPU write breakpoints on the VDP1 glyph tiles logged nothing (two
     address forms, two state windows).
   - The 'a' tile appears within 120 frames of `f00006862`, and is never in
     WRAM or extracted cart RAM.
   - So the SCU DMA registers (`write:25FE0000-25FE007F`, log mode) were
     logged instead.
5. **Palettes.** Map each sprite pixel value to its screenshot colour, for the
   credits and for a dialogue box (`f00004752` + 60 frames, offset (0, 8)).
6. **Mockups:**

   ```bash
   ./invenv.sh python -m tools.text.credits_font <MEMFIX.PAC> --line … --palette gold|white --out …
   ```

   The comparison with the arcade's own box uses `local/end006/mame/boxes.png`
   (`EXP-0042`, `mshvsfu`).

## Actual Result

### Where the font is

- **The credits draw quote-font codes.** Every credits glyph sprite's 128
  bytes equal a quote-font glyph (`MEMFIX.PAC` entry 4): 121 of 121 named on
  the checked screen, and every non-leftover tile in the glyph area.

  | Codes | Content |
  | --- | --- |
  | `0x1E0`-`0x1EF` | arrows, brackets, symbols |
  | `0x1F0`-`0x1FF` | `!` (`0x1F0`), `?` (`0x1F1`), `%`, `&`, `#`, `*`, `(`, `)`, math signs |
  | `0x200`-`0x209` | digits `0`-`9` |
  | `0x20A`-`0x20F` | the hiragana の, `<`, `=`, `>`, and a long dash (`0x20F`) |
  | `0x210`-`0x229` | `A`-`Z` |
  | `0x22A`-`0x22F` | `[`, `\`, `]`, `^`, `_`, and others |
  | `0x230` | `"` |
  | `0x231`-`0x24A` | `a`-`z` |
  | `0x24B`-`0x24F` | `{`, `/`, `}`, `~`, an arrow |
  | `0x250`-`0x25F` | `:` (`0x250`), `;`, `.` (`0x252`), `,` (`0x253`), apostrophe-like marks (`0x255`), an ellipsis (`0x259`), symbols |

  All are stored compressed, which is why no raw search found them.
  Rendering: `local/font010/quote_1e0_26f.png` (`fb7388e5…`).
- **Same routine as the captions.** The SCU DMA routine at `0x0601BABC`
  (R9 = source, R10 = destination, R11 = count) copies each glyph, 128 bytes
  at a time, from the buffer at `0x0601CEEC` into VDP1 VRAM. This was seen
  at frames 275-304 for destinations `0x25C0C900`-`0x25C0D000`.
  - The caller's return address is `0x0601CDF2`, inside the quote-font glyph
    routine at `0x0601CE00` (`FONT-001`, `EXP-0038`).
  - Glyphs are built once, when a letter first appears, and stay in VRAM for
    the rest of the credits.
- **Cell format.** 16 × 16, 4 bpp, colour-bank mode (`pmod` `0x0880`), the
  same as caption glyphs. Each letter fills its whole cell (one character per
  cell). Values `1`-`9` are a vertical gradient; `B` is the outline.
- **Credits palette** (screenshot mapping, banks `0x70F0`-`0x7170`):
  - `1` = (240,240,0) through `9` = (240,112,0), in steps of 16 green;
  - `B` = (32,0,96).
- **Caption palette** (dialogue box, bank `0x6030`): only `1` = white
  (240,240,240) and `F` = black are used. Values 2-9 and `B` were not seen in
  that bank.

### A side finding: `TESTFIX.DAT`

`TESTFIX.DAT` (13,696 bytes, `ffb5ee72…`) holds two fonts, stored as raw 8 × 8
4 bpp cells:
- an 8 × 8 ASCII font at `0x0000`-`0x0FFF`, resident in VDP2 VRAM at `0x400`
  during the credits;
- 16 × 16 glyphs (4 cells each, glyph offset = (ASCII − 1) × 128) for
  punctuation, digits, capitals, and "st", "nd", "rd", "th". Their art
  matches the credits glyphs for those characters.

It has no lower case beyond those suffixes. The credits do not take their
glyphs from it: the DMA source is the quote-font routine. What uses
`TESTFIX.DAT` is unknown.

### Comparison with the US arcade caption font

`local/font010/arcade_vs_credits.png` (`9cdf2844…`) puts the arcade's own
"We shall meet again / AKUMA." box beside a mockup of the same line.

- **Same style:** gold vertical gradient, dark outline, and a slant.
- **Different widths:** the arcade letters are narrow (about 8 pixels), with a
  gap between letters. The Saturn credits letters are 16 pixels wide.

So the fonts are visually very similar, but not the same glyph set. The
arcade's own glyph data was not located (`REF-012`).

### Fit for captions and endings

`local/font010/mock_options.png` (`dcc73c70…`) shows three versions of a
25-character page line and a dialogue line:
1. the current white pairs;
2. credits glyphs squeezed two per cell, in gold;
3. credits glyphs one per cell, in gold.

- **One glyph per cell does not fit.** A box line has 19 cells, and official
  English lines run to 25 characters, so such a line is cut off.
- **Two squeezed glyphs per cell fit.** This uses the same pair method and
  the same capacity as now: the number of distinct pairs depends on the text,
  not the font. It reads well and looks like the arcade. Some thin glyphs lose
  shape when squeezed (`I` like `]`, `!` like `)`), and per-glyph tuning
  would fix that. Gold: `mock_gold.png` (`0e10a45f…`).
- **Colour:**
  - Gold needs the gradient colours in the caption palette, or a sprite
    colour bank that holds them during win-quote and ending screens. Whether
    such a bank exists there, and where the palette comes from, is not
    known.
  - White needs no palette work: the gradient maps to `1`, the outline to
    `F` (`mock_white.png`, `e204ed24…`).

## Conclusion

1. **CONFIRMED:** the credits font is quote-font codes `0x1E0`-`0x25F`,
   compressed in `MEMFIX.PAC` entry 4. It is drawn by the same glyph routine
   as the captions (`0x0601CE00`) and DMA'd to VDP1 as 16 × 16 4 bpp cells.
   The caption renderer can therefore already show these glyphs.
2. **SUPPORTED (inspection):** it is the same visual style as the US arcade
   caption font, but twice as wide.
3. **Adoption is the user's decision** (`FONT-011`). Options:
   - squeezed pairs in gold (needs palette work);
   - squeezed pairs in white (no palette work);
   - locate and convert the arcade's narrow font itself (`REF-012`), which
     needs a provenance decision.

## Uncertainty and Alternatives

- **Squeeze quality:** judged from mockups, not live screens. Per-glyph tuning
  is untested.
- **Palette:** which CRAM banks exist on win-quote and ending screens, and
  whether bank `0x6030` indices 2-9 and `B` are used by other sprites, is
  unknown.
- **Font candidates:** 120 of the 128 credits codes are in
  `data/text/font_candidates.json`, the "not seen in record tables" list. The
  compiler only reclaims kanji (`0x926`-`0xC5F`), so it is safe today. The list
  must never be read as "unused" (`EXP-0023` already warned).
- **VDP1 breakpoints:** CPU write breakpoints on VDP1 VRAM logged nothing,
  even on the command table. Either those writes are all DMA, or breakpoints
  do not cover VDP1 VRAM. That was not resolved, as there was no positive
  control.
- **Cart RAM** was searched in save-state extractions, a region not validated
  against a debugger dump (`AGENTS.md`). It was used only for a negative
  search.
- **`build/` cleanup:** during this session, `build/end010`, `end023`,
  `end024_vega`, `end026`, and `end027` were removed by something outside this
  session. All are reproducible from specs; `build/regression` holds the
  current reference images.
