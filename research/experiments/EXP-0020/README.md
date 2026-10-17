# EXP-0020: Find Latin Glyphs in the Quote Font and the Codes That Select Them

Task: `FONT-001`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED (font format; ASCII display) / SUPPORTED (full-width Latin)

## Observation

- **Rendering path.** Win quotes are 38-cell records of 16-bit codes (`EXP-0013`,
  `EXP-0015`). Each code is drawn as a 16x16 4 bpp VDP1 sprite cell: body pixels
  are nibble `1`, and a one-pixel shadow is nibble `F` (`EXP-0012`, `EXP-0013`).
  Glyph cells pass through a WRAM-H staging cell at `0x0601CEEC`.
- **Code blocks seen.** Ryu's 16 records use 112 distinct codes:
  - `0x0000` (name placeholder) and `0x0020` (blank);
  - `0x0401-0x0403`;
  - `0x08xx`: hiragana at `0x0800 + (Shift-JIS second byte − 0x9F)`, katakana from
    `0x0853`, and ・ `08AE`, ！ `08DD`, `!!` `08DF`;
  - `0x09xx-0x0Cxx` (kanji).

  No Latin letter or digit appears in any observed quote.
- **Earlier font search.** `EXP-0013` found no resident font in WRAM or cart RAM as
  4 bpp cells or uncompressed 1 bpp. **Disc files were not searched.**
- **Searchable disc data.** `EXP-0016`/`EXP-0018` provide all 414 extracted files
  and 52 decodable PAC payloads.

## Hypotheses (tested in order, one per phase)

- **H1 (offline):** the quote font is stored in a disc file (raw or PAC-decoded) as
  glyph bitmaps whose body shape matches the known glyph cells, and the glyph index
  relates to the code by a block-linear rule.
- **H2 (runtime):** specific codes derived from H1 display Latin letters or digits
  in a win quote.

## Phase 1: Offline font search (no user input)

1. **Known glyphs.** From `EXP-0012` cells, take about 60 distinct non-blank glyphs
   with their `EXP-0013` codes. Build body masks (nibble == 1) as 16x16 1 bpp, at
   shifts of 0-2 px, in MSB/LSB order, plus 4 bpp, 2 bpp, and unshadowed forms.
2. **Search.** Look in every extracted file and every decoded PAC payload.
3. **Predicted hits.** One file (or region) holds most known glyphs at offsets
   `base + index × stride`. The stride is consistent with the format (for example
   32 bytes for 16x16 1 bpp), and the index order matches code order within each
   block (for example kana index difference = code difference).
4. **If found.**
   - Fit the index↔code rule. Confirm it predicts the offsets of held-out known
     glyphs (at least 10).
   - Render the whole font to an atlas PNG (ignored) labelled with the predicted
     codes.
   - Identify Latin letters, digits, and punctuation visually, and list candidate
     codes.
5. **If not found.** Phase 1b: an interactive write breakpoint on
   `0601CEEC-0601CF6B` while a quote screen builds, from the `EXP-0010` state A
   replay. The halt identifies the renderer PC and its font-source register. Dump
   that region with `D` while halted, and repeat steps 1-4 on the dump.

## Phase 2: Runtime confirmation (user session, `EXP-0015` workflow)

- **Patch.** Build a WRAM-L table patch with `tools.memory.make_patch`. It sets
  line-1 cells 0-N of all 16 records to the candidate Latin codes for a short probe
  string (for example `A B C 1 2 3`). Load it at state A with `L`, KO with Ryu, and
  take a screenshot.
- **Prediction.** The cells show the predicted Latin glyphs, and the rest of the
  quote is unchanged.
- **Control.** The same procedure with the original table.
- **ASCII probe (separate run, separate hypothesis).** Codes `0x0041-0x0046`. Its
  result is recorded independently.

## Discriminating Outcomes

| Outcome | Interpretation |
| --- | --- |
| H1 holds and the atlas has Latin glyphs | Codes exist; Phase 2 confirms them |
| H1 holds and the atlas has no Latin glyphs | English needs new glyphs added to the font (a later, separate task) |
| H1 fails, Phase 1b finds the source | Repeat the analysis on the identified region |
| Phase 2 shows other glyphs | The index↔code rule is wrong for that block; refine it |

## Inputs

- `research/extracted_files/mshvsf_saturn_jp/` (414 files) and
  `research/extracted_files/pac_decoded/`, all ignored.
- `research/memory_dumps/exp0012/`, `exp0013/`, and the `EXP-0010` VDP1
  extractions.

## Actual Result: Phase 1 (2026-10-17)

### Known-glyph catalog

`tools/memory/glyph_codes.py` (new, with tests) pairs each quote sprite cell with
its code from the WRAM-H buffer:

```bash
./invenv.sh python -m tools.memory.glyph_codes research/savestates/archive-2026-10-17/*.mc* \
  --out research/memory_dumps/exp0020/known_glyphs.json
```

- **79 codes, 0 conflicts**, from 12 quote-screen states. Output (ignored) SHA-256
  prefix `a1bf8324e47dd886`.
- Codes covered: `0402-0403`, 46 `08xx` (kana and punctuation), and 30 kanji
  `093A-0C42`.

### Glyph pixel format

- Pixel nibbles are `0` (empty), `1` (body), `2`-`A` (intermediate shading), and
  `F` (shadow, equal to the body shifted by +1 column, +1 row, and +1 diagonal).
  Overall counts: `0` 12,054; `1` 2,970; `2-A` 2,101; `F` 3,099.
- Bodies occupy rows 1-13 and columns 1-14 of the 16x16 cell.

### Searches (all zero unless noted)

The search covered 466 files, 397,416,080 bytes: all 414 extracted files plus 52
LZSS-decoded PAC payloads.

| Form | Hits |
| --- | ---: |
| Exact 4 bpp cell | 0 |
| 1 bpp body mask, MSB or LSB, unshifted | 0 |
| Shadow-free 4 bpp cell (`F` → 0), 0-3 px left shifts, 0-2 row shifts | 0 |
| Densest two shadow-free rows per glyph, 0-3 px shifts | 3 (see below) |

The 3 two-row hits were all for the same horizontal-stroke glyph, `093D`, in
`BG03`, `BG0D`, and `BGSEL` background graphics. They are coincidental.

The shadow-free two-row search was repeated on WRAM-L, WRAM-H, and cart RAM
(unvalidated) of states C1 and A: 0 hits.

### Static observation

WRAM-H holds `0601CEEC` (the staging-cell address) in two places:

- `0x0601CEE8`, next to `0601CF6C` at `0x0601CEE4`, immediately after an
  `000B 0009` (`rts; nop`) sequence at `0x0601CEE0`;
- `0x0601D9E0`, after `000B 0009` at `0x0601D9DA`.

Both look like SH-2 literal pools at the end of routines. These are candidates for
the glyph renderer and the cell copy (`HYPOTHESIS`; not disassembled).

## Phase 1 Conclusion

H1 is not supported for the tested formats. The font is not stored as 4 bpp,
shadow-free 4 bpp, or 1 bpp 16x16 glyphs in any disc file, decoded PAC payload, or
work RAM.

The intermediate shading suggests that glyphs are generated from another
representation, for example a compressed font, a non-decodable PAC, or a different
resolution. That remains unknown. Phase 1b follows.

## Phase 1b Design (interactive)

**Hypothesis.** A CPU write breakpoint on the staging cell
`0601CEEC-0601CF6B 2601CEEC-2601CF6B`, set during a replay from state A on the
original image, halts in the glyph renderer. Its registers identify the font source
address and the code being drawn.

**Procedure.**

1. Boot the original image and load slot 5 (state A).
2. Set the write breakpoint, unpause, and KO with Ryu.
3. At the halt, record PC, R0-R15, and PR (screenshot).
4. With `D`, dump High Work RAM and Low Work RAM.
5. Clear the breakpoint and press `R`.

**Predictions.**

- A register holds a source address outside the staging cell (font data or a
  decompression buffer).
- The bytes there relate to the glyph being drawn, which the next offline step
  tests.
- If the source is cart RAM, the debugger cannot dump it, so a save state taken
  after resuming will be extracted (unvalidated region, `HYPOTHESIS` strength).

## Phase 1b Run

The run started 2026-10-17 on the original image (log
`local/mednafen/logs/font001-exp0020-1b.log`, process 70836), with source identity
verified before launch.

### Breakpoint

From state A (slot 5, `ab60af86…`), write breakpoints
`0601CEEC-0601CF6B 2601CEEC-2601CF6B` fired immediately after the debugger was
hidden, before the KO. The staging cell is also used outside the quote screen.

Values from the user's screenshot (digits read from the debugger font):

- PC `0601CEB2`, `mov.b r3,@r10`;
- R9 `0279192A` (stream pointer, in cart RAM) and R8 `0278D4F2`;
- R10 `0601CEEC` (staging cell), R12 `0601CF6D`;
- PR `0601D9BE`.

### Dump

`local/mednafen/dumps/f1b-wramh.bin`, High Work RAM, 1,048,576 bytes, SHA-256
`0f364591415db396a1b3ec5919802b1e05611670af27be28b2c6d97a7e359dbc`. The Low Work RAM
dump requested in the same session was not written; it is not needed for this
result.

### Disassembly

A scratch SH-2 decoder was used over `0x0601CDB8-0x0601CEE2` of the dump.

- **Caller.** Around `0x0601CDDC`, R3 = `@(24,r10)` (the glyph code); then
  `bsr 0x0601CE00`, then `jsr 0x0601BA76` with R9 = `0601CEEC` and R11 = `0x80`
  (the cell transfer).
- **Glyph routine `0x0601CE00`.**
  - Font base = `@(4, 0x0601D8E0)` = `0x0278CF60`. The next word in the same
    structure is `0x0000B5D0`.
  - Locating a glyph uses a block table at base+16 (one long per 16 codes, an
    offset from base+16), plus a size table at base+16+`0x380` (one byte per
    code) summed over the earlier codes in the block.
  - A negative size means a raw 128-byte copy, and zero means clearing the cell.
  - A positive size means a two-stage mask decompression, filled column by
    column. The exact semantics are in `tools/text/font.py`.

### Offline decoder validation

`tools/text/font.py` (new, with tests), run on state A's cart RAM extraction
(`research/memory_dumps/ab60af86089a9575/cart_ram.bin`, unvalidated region):

```bash
./invenv.sh python -m tools.text.font research/memory_dumps/ab60af86089a9575/cart_ram.bin \
  --first 0 --count 3584 --check research/memory_dumps/exp0020/known_glyphs.json
```

- Codes `0x000-0xDFF`: 2,842 compressed, 30 raw, 712 empty.
- **79 / 79 known glyph cells reproduced byte for byte**, including the shadow.

### Atlas

`research/memory_dumps/exp0020/atlas/` (ignored; for example
`tool_font_000.png`, prefix `2182e228`):

- **ASCII set.** Codes `0x0020-0x007E` hold a complete ASCII set at the ASCII
  values: space, punctuation, `0-9`, `A-Z`, `a-z`, and `{|}~`.
- **Other glyphs.** Codes `0x0000-0x000F` show hex-digit glyphs. Some later codes
  in the `0x00xx` range hold artwork resembling "QUICK CONTINUE".
- **Half width.** Latin glyphs occupy columns 0-8 of the 16-pixel cell. Kana and
  kanji occupy columns 1-14.

## Phase 1b Conclusion

`CONFIRMED`: the quote font is a compressed glyph table in cartridge RAM at
`0x0278CF60` (in this session), in the format implemented by `tools/text/font.py`.
Decoding it reproduces every observed quote glyph exactly. This also gives indirect
support that cart RAM extraction is correct for the font region.

`SUPPORTED` (H2 pending): codes `0x0020-0x007E` select ASCII-shaped Latin glyphs.
They are half-width, so one Latin letter per 16-pixel cell would leave wide gaps,
with at most 19 letters per line. Display in a quote is not yet tested (Phase 2).

## Phase 2 Plan (unchanged design, now with concrete codes)

- **Patch.** Line-1 cells 0-2 of all 16 records set to `0041 0042 0043`
  (`A B C`), loaded with `L` at state A, using the `EXP-0015` procedure.
- **Prediction.** `ABC` (half-width, gapped) appears at the start of line 1.
- **Control.** The original table.

## Phase 2 Run Setup (2026-10-17)

Patch built with `tools.memory.make_patch` from state A's validated WRAM-L, range
`0x002091AC-0x0020966B` (1,216 bytes, all 16 records). It makes 48 writes:
`0x002091AC + 76·r + 2·c` = `0041`/`0042`/`0043`.

| File (ignored, `local/mednafen/dumps/`) | SHA-256 prefix |
| --- | --- |
| `f2-abc-patched.bin` = `abc.bin` | `0124f0b7e7fec042` |
| `f2-abc-original.bin` = `org.bin` | `6aaf1f8883642a17` |
| `f2-abc-manifest.json` (original and modified values per write) | `c6ae3ec512dc492e` |

Procedure: the same as `EXP-0015`, with load range `000091AC 0000966B`.

| Run | Load | Verification dump | Slot |
| --- | --- | --- | --- |
| Patched 1 | `abc.bin` | `a1.bin` | 1 |
| Patched 2 | `abc.bin` | `a2.bin` | 2 |
| Control | `org.bin` | `k1.bin` | 3 |

Slots 1-3 were archived in `research/savestates/archive-2026-10-17/` beforehand.

## Phase 2 Result (2026-10-17)

| Run | Verification dump | Slot / state SHA-256 | Screenshot | Shown |
| --- | --- | --- | --- | --- |
| Patched 1 | `a1.bin` = `abc.bin` (`0124f0b7…`) | 1 / `55523b5f179bd30e…6158` | `-0048.png` `25f89623…f51e` | Ken-template quote (record 0) with `A B C` in cells 0-2, replacing two blanks and `教` |
| Patched 2 | `a2.bin` = `abc.bin` | 2 / `7c2fa0a9e88ffe20…5b84` | `-0049.png` `c6ff1421…0a87` | same record, `A B C` |
| Control | `k1.bin` = `org.bin` (`6aaf1f88…`) | 3 / `a63d846ca30b24c8…c5a7` | `-0050.png` `87689e8d…a6f3` | Q8, unchanged |

States are archived as `exp0020p2-slot{1,2,3}`. An enlarged crop of `-0048.png`
(ignored `crop_0048.png`) shows `A`, `B`, `C`.

**H2: `CONFIRMED`** for codes `0041-0043`: they display A, B, and C in quote cells.
They render **faint**, because ASCII glyphs are 8x8 gradient shapes (values 2-8, top
half of the cell, no body `1` or shadow `F`), which the quote color table shows as
pale tones.

### Further atlas finding (`SUPPORTED`; display not tested)

The font also has **full-width** Latin glyphs in the quote style (body `1` plus
shadow `F`), checked against the known punctuation codes (`08DD` `！`, `08DF` `!!`):

| Characters | Codes |
| --- | --- |
| `A-Z` | `0x08E8-0x0901` |
| `a-z` | `0x0902-0x091B` |
| `0-9` | `0x091C-0x0925` |
| Full-width punctuation | around `0x08A9-0x08DF` |

They are recorded in `data/text/font_codes.json`.

## Conclusion

FONT-001's acceptance criteria are met:

- the font source and format are identified and validated (79/79 glyphs);
- Latin codes are confirmed by a live display test with a control.

For English, the full-width set (`0x08E8+`) is the stronger candidate and needs its
own live display test.

Layout constraint for English (`HYPOTHESIS`, to test later): a quote is 2 × 19
cells at one glyph per cell, so at most 38 full-width characters.

## Uncertainty and Alternatives

- Only `0041-0043` were displayed; the rest of the ASCII range and the full-width
  set are atlas-only.
- Both patched runs selected record 0; other records were covered by `EXP-0015`.
- The font's disc source and load path are unknown, so editing glyphs for better
  English would need a new investigation.

