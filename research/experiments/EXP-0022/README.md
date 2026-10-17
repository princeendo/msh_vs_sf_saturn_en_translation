# EXP-0022: English Layout Capacity in Win Quotes

Task: `LAYOUT-001`
Date: 2026-10-17
Status: READY
Confidence: HYPOTHESIS

## Question

Can a win quote hold more English than 2 × 19 = 38 full-width characters? There
are two routes:

- **(R1) Pair glyphs:** custom glyphs carrying two half-width Latin letters in one
  16x16 cell, at up to 76 characters per quote with no layout change.
- **(R2) Layout change:** more cells, or narrower steps, per line.

## Observations

- **Record and layout.** Records are fixed 76-byte, 38-code, 2 × 19 cells
  (`EXP-0013`, `EXP-0015`). On screen, line 1 is at y = 178 and line 2 at y = 194,
  with x = 26-314 in 16-pixel steps (`EXP-0012`).
- **Buffer and builder.** The WRAM-H per-screen buffer header is `0026 0025
  060ED900` (38 entries). The buffer builder at `0x060AF8C6` uses `#76` (`EXP-0014`).
- **Font.** The font is compressed glyphs in cart RAM, base `0x0278CF60`. Its data
  ends at `0x027BF6A0` (206,656 bytes). Each 16-code block has its own table entry
  and size bytes (`EXP-0020`).
- **Free codes.** 712 codes are empty, with free runs `0x00A8-0x00FF` (88),
  `0x0190-0x01DF` (80), `0x0260-0x02AF` (80), and `0x0C5F-0x0DFF` (417).
- **Full-width Latin.** It displays solid and full-size (`EXP-0021`). ASCII glyphs
  are half-width, but faint 8x8 gradients (`EXP-0020`).
- **Unknown source.** The font's disc source is unknown. The stock debugger cannot
  write cart RAM (`EXP-0007`, `EXP-0014`).

## Hypotheses, tested in order (one per phase)

### Phase A (offline): font disc source

**H-A.** The 206,656-byte font image is present on disc verbatim, either in a raw
file or in an LZSS-decoded PAC payload.

- **Test.** Search the `EXP-0016` files and `EXP-0018` decoded PACs for the font's
  first 0x400 bytes (block table plus size table) and for several glyph streams.
- **If found.** Glyph additions can be patched on disc with the `DISC-002`
  pipeline.
- **If not found.** Try a write breakpoint on cart `0x0278CF60-0x0278CF7F` during
  boot to find the loader (Phase A2, interactive, only if needed).

### Phase B (offline): layout limits

**H-B.** Cells per line (19), line count (2), the x step (16), record size (76),
and the buffer count (38) are a small set of immediate constants in the builder
and sprite-layout code. The builder is near `0x060AF8C6`; the sprite emitter is
the code writing VDP1 commands with color `0x61E0`.

- **Test.** Disassemble from the `EXP-0018`/`EXP-0020` WRAM-H dumps with the
  scratch SH-2 decoder (promoted to `tools/` if used). Record every constant and
  each fixed-size buffer: the WRAM-H buffer, VDP1 command slots, and the glyph-cell
  VRAM allocation.
- **Output.** A capacity model that states what R2 would require and what it would
  risk.

### Phase C (live): pair-glyph display

**H-C.** A custom raw glyph assigned to a free code in a fully empty block (for
example `0x0D00`) displays in a quote cell when a record uses that code.

- **Implementation.**
  - Draw a 16x16 4 bpp cell holding two half-width letters (for example `Th`) in
    quote style: body `1`, shadow `F`.
  - Append it as a raw glyph after the font data end (`0x027BF6A0`, checked to be
    unused). Point block `0x0D0x`'s table entry at it, and set code `0x0D00`'s size
    byte to `0x80`. No other block's data moves.
  - Load a WRAM-L table patch that uses `0x0D00`.
- **Prediction.** `Th` appears in the patched cell, solid and with a shadow, and
  other glyphs are unchanged. The control shows the unmodified quote.
- **Delivery mechanism, chosen by Phase A:**
  - a disc patch of the font source (preferred; reuses `DISC-002` tooling); or
  - if no disc source is found, a save-state cart-RAM patch (a new
    `tools/memory/mcs_patch.py`, validated by re-extraction round trip) loaded in
    stock Mednafen.

### Phase D (deferred): layout change

Only if Phase B shows the constants and buffers are contained:

- test R2 (for example an 8-pixel step with 38 cells per line) with a code patch;
- this also needs solid half-width glyphs (new font glyphs) and a 152-byte record
  format.

Otherwise R1 is the recommended route.

## Decision Rule

| Evidence | Decision |
| --- | --- |
| Phase C succeeds | Pair glyphs (R1) become the English route, with capacity 76 characters per quote. The number of distinct pairs needed is measured against free codes (665 in the listed runs). |
| Phase C fails | Diagnose: font table semantics, the empty-block skip, or glyph caching. |
| Phase B shows R2 is cheap and safe | Prototype R2 as a separate task. |

## Actual Result

Pending.
