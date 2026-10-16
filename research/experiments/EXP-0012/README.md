# EXP-0012: Compare VDP VRAM Across Quote Checkpoints

Task: `DBG-013`
Date: 2026-10-15
Status: DONE
Confidence: DISPROVEN (VDP2); SUPPORTED (VDP1 sprite glyphs)

## Observation

`EXP-0011` disproved Shift-JIS quote text in WRAM. Quote-dependent WRAM-L ranges hold
big-endian 16-bit values with a constant high byte and sequential low bytes
(`0x0C5E, 0x0C5F, …`), separated by `FFFF`. These are consistent with VDP2
pattern-name (cell map) entries pointing at sequentially allocated tiles. The quote
screen shows the same portrait and layout in every C state.

Implementation reference, not a hardware manual: Mednafen 1.32.1
`src/ss/vdp2_render.cpp` (lines 380-430) decodes a character number from pattern-name
data. For one-word pattern names it uses 10 or 12 low bits plus supplementary
register bits, depending on mode. It addresses character data at
`charno << 4` 16-bit words, which is `charno * 0x20` bytes in VDP2 VRAM.

## Hypothesis

The rendered quote glyph pixels are in VDP2 VRAM, at addresses that differ between
different quotes and are stable between C1 and C1′.

## Controlled Change

The variable is the displayed quote (C1 vs C2 vs C2b). C1 vs C1′ is the time-only
control.

## Prediction

1. VDP2 VRAM C1 vs C2 and C1 vs C2b, with C1/C1′ changes excluded, leave a
   concentrated block of changed bytes. Its size should match a two-line text box,
   on the order of a few KB to a few tens of KB.
2. Rendering that block as 8x8 tiles (4 bpp and 8 bpp, grayscale) shows glyph-like
   shapes, and the shapes differ between quotes.
3. Secondary: at least one candidate pattern-name mapping of the `EXP-0011` WRAM-L
   entries (`(v & 0xFFF) * 0x20` or `(v & 0x3FF) * 0x20`) points into that block at a
   rate well above the base rate of changed bytes in VDP2 VRAM.

VDP1 VRAM is compared the same way as an alternative location.

## Inputs and Provenance

`EXP-0010` states A, C1, C1′, C2, and C2b. VDP1 and VDP2 VRAM were extracted with
`tools.memory.mcs_extract`, validated by `EXP-0008`, into ignored
`research/memory_dumps/<state sha256[:16]>/`.

## Tools

- `tools/memory/diff.py`, with the C1/C1′ control.
- `tools/memory/vdp1_sprites.py` (new). It walks the VDP1 command list in a raw VDP1
  VRAM dump and lists or renders normal sprites in grayscale. The command layout
  comes from Mednafen 1.32.1 `src/ss/vdp1.cpp` and `vdp1_sprite.cpp`, as documented
  in the module. Synthetic tests cover it.

## Actual Result

### VRAM diffs

| Region | C1 vs C1′ | C1 vs C2 | C1 vs C2b |
| --- | ---: | ---: | ---: |
| VDP2 VRAM | 147,031 bytes in one block, `0x05E2EB58-0x05E5335F` | **0** | **0** |
| VDP1 VRAM | 170,913 bytes | 170,004 raw; 65,868 after control | 127,346 raw; 61,669 after control |

VDP2 VRAM is byte-identical across C1, C2, and C2b (SHA-256 prefix
`3a98953b99e3f665`) even though the quotes differ. The C1′ VDP2 change is a single
contiguous ~146 KB block, consistent with the start of a scene transition. So C1′ is
not a clean time-only control for VRAM: it changes more than time. That caveat
applies to the `EXP-0011` WRAM-H exclusions as well.

### VDP1 command lists

`vdp1_sprites` walked each command list to its end command.

| State | Normal sprites | Sprites with color word `0x61E0` | Distinct `0x61E0` cells | Screen rows |
| --- | ---: | ---: | ---: | --- |
| A | 273 | 0 | 0 | — |
| C1 | 396 | 38 | 23 | y = 178, 194 |
| C1′ | 388 | 38 | 23 | y = 178, 194 |
| C2 | 398 | 38 | 24 | y = 178, 194 |
| C2b | 402 | 38 | 16 | y = 178, 194 |

Rendering all normal sprites from VDP1 VRAM alone reproduces the visible win screen,
including the quote text, matching each state's save-time thumbnail. Rendering only
the `0x61E0` sprites gives exactly the two quote lines:

- C1 shows Q10 and C2 shows Q8, by visual comparison with the thumbnails.
- C1 and C1′ glyph renders are byte-identical (SHA-256 `ae2240840ab6…`).
- C2 renders to `e1e22224c66d…` and C2b to `f2a008409713…`.

The text-area sprites with other color words are the box frame and the
CAPCOM/MARVEL COMICS logos.

The glyph cells are 16x16, 4 bpp (128 bytes), in VDP1 VRAM:

- C1: `0x05C4B380-0x05C4BEFF`
- C2: `0x05C4B080-0x05C4BC7F`
- C2b: `0x05C4B080-0x05C4B87F`

### Shared cells

Shared non-blank glyph cells, compared by 128-byte content:

- C1 and C2: 9
- C1 and C2b: 2
- C2 and C2b: 7

The cells shared by C1 and C2 sit at different VRAM addresses and screen positions.
Rendered, they are single characters: `の い 拳 を る え な ！` and a combined `!!`
cell. Each appears in both the Q10 and Q8 text.

### Secondary prediction

The secondary prediction (WRAM-L entries index quote-dependent VDP2 tiles) fails:
there are no quote-dependent VDP2 bytes for them to index.

Derived renders and JSON (ignored, `research/memory_dumps/exp0012/`) are
`<role>_vdp1_frame.png`, `<role>_glyphs.png`, `<role>_vdp1_sprites.json`, and
`<role>_glyphs.json`.

## Conclusion

The hypothesis that the quote glyph pixels are in VDP2 VRAM is `DISPROVEN`. VDP2
VRAM does not change with the quote.

`SUPPORTED` (strong, but no mutation test yet): the quote is drawn by VDP1 normal
sprites with color word `0x61E0`. Each sprite uses a 16x16 4 bpp glyph cell in VDP1
VRAM, one cell per distinct character, and identical characters produce
byte-identical cells across quotes. The game therefore assembles quotes per
character from a font, so a per-quote character sequence must exist upstream.
Its location and encoding are unknown.

## Uncertainty and Alternatives

- No bytes were modified, so causality is not confirmed. A live VDP1 VRAM or
  upstream mutation is `RE-012` (M1) work, gated by `GATE-M0`.
- The grayscale render ignores palettes. Glyph identity is visual and was compared
  only by exact byte equality.
- C1′ is contaminated by a transition. A cleaner time control would use fewer
  frames.

## Next Discriminating Experiment

Search the validated WRAM dumps for the exact 128-byte glyph cells, such as 拳 and
を. The unvalidated cart RAM can be searched too, labeled `HYPOTHESIS`. A hit would
locate the font. The glyph's index in it is a candidate character code, and
searching for the code sequence of Q10 would test whether the quote is stored as
those codes.
