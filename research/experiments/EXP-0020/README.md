# EXP-0020: Find Latin Glyphs in the Quote Font and the Codes That Select Them

Task: `FONT-001`
Date: 2026-10-17
Status: READY
Confidence: HYPOTHESIS

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

## Actual Result

Pending.
