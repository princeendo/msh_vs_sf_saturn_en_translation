# EXP-0013: Locate the Glyph Font and Quote Character Codes

Task: `DBG-014`
Date: 2026-10-15
Status: DONE
Confidence: DISPROVEN (resident font as cells); SUPPORTED (16-bit quote codes)

## Observation

In `EXP-0012`, VDP1 sprites with color word `0x61E0` draw each quote from 16x16
4 bpp glyph cells (128 bytes each), with one cell per distinct character. Cells for
characters shared between quotes are byte-identical. That implies a font source and
a per-quote character sequence upstream.

## Hypothesis

The glyph cells are copied verbatim from a font table resident in WRAM or cartridge
RAM during the quote screen. Searching for a cell's exact 128 bytes finds it inside
that table.

## Controlled Change

None: this is a search over the existing `EXP-0010` states. Different quotes (C1,
C2, C2b) serve as replicates. Cartridge RAM extraction is not validated
(`EXP-0008`), so any cart hit is evidence of `HYPOTHESIS` strength only.

## Prediction

1. Each non-blank glyph cell from C1, C2, and C2b occurs verbatim in WRAM or cart
   RAM.
2. All hits fall inside one region at addresses `base + index * 128`.
3. If (1) holds, writing each Q10 character as its glyph index gives a code sequence.
   That sequence (as 8- or 16-bit values) occurs in memory in C1 and not in C2 or
   C2b.

If (1) fails, the font is stored in another format (for example 1 bpp or
compressed) and converted before upload. Alternative-format searches are then
recorded as a follow-on hypothesis within this experiment.

## Tools

- `tools/memory/vdp1_sprites.py`: glyph cells and reading order.
- `tools/text/search.py`: exact byte searches.
- `tools/text/pattern_search.py` (new, with tests): searches for runs of values
  that match a symbol equality pattern with literals.

## Actual Result

### Font search (primary hypothesis)

The non-blank unique glyph cells (C1: 22, C2: 23, C2b: 15) were searched verbatim in
WRAM-L, WRAM-H, and cart RAM. Only **one** cell per state matched, always in
WRAM-H at `0x0601CEEC`, and it was always the quote's last rendered glyph:

- C1: VDP1 `0x4BE80`
- C2: `0x4BC00`
- C2b: `0x4B800`

That is consistent with a single-cell staging buffer. Glyph pixels are mostly
nibble `1` (body) and `F` (a shadow offset by one pixel). Two further searches found
nothing (0 hits):

- 1 bpp body masks (nibble == 1), 16x16, shifted 0-2 px, in WRAM and cart;
- six-row slices of the six densest glyphs per state (C1 and C2), shifted
  −4..+4 px, MSB and LSB bit order, 16-bit rows (216 patterns).

### Character sequences (follow-on)

Rendered glyph identities, in reading order over 2 rows × 19 cells, gave each quote
a 38-cell pattern with blanks. The patterns reproduce each quote's visible
character count and repeats: まだまだ, a triple ・・・, and `!!` as a single cell.
In total there are 44 distinct characters.

`pattern_search` (16-bit, blanks as literal `0x0020`) over WRAM-L of the **pre-KO**
state A found each pattern exactly once:

| Quote | State | WRAM-L address | Table record index |
| --- | --- | --- | ---: |
| Q8 | C2 | `0x00209290` | 2 |
| Q10 | C1 | `0x0020940C` | 7 |
| Q11 | C2b | `0x0020953C` | 11 |

Facts about the table:

- **Records.** Each record is 38 big-endian 16-bit codes (76 bytes, 2 lines × 19
  cells, `0x0020` = blank). The records are contiguous; a walk found 15 records at
  `0x002091F8-0x0020966B`, with code range `0x0401-0x0C42`.
- **Same in every state.** The table is byte-identical in A, C1, C1′, C2, and C2b.
- **Consistent codes.** All 44 glyph identities map to one code each across the
  three quotes, so shared characters have equal codes.
- **Kana codes follow Shift-JIS order.** All 46 kana in the three quotes (agent
  reading, unreviewed) match:
  - hiragana: `0x0800 + (Shift-JIS second byte − 0x9F)`, for example い `0803`,
    の `082D`, を `0851`;
  - katakana: `0x0853 + (second byte − 0x40)`, minus 1 above `0x7F`, for example
    ツ `0876` and ヤ `0896`.
- **Other symbols.** Observed codes include ・ `08AE`, ！ `08DD`, and `!!` `08DF`.

Per-screen buffer: WRAM-H `0x060ED80A` holds the **current** quote as 38 entries of
`(0x5000 | code, 0x0002)`, 152 bytes. It is present in C1, C1′, C2, and C2b at the
same address with each state's own codes, and absent (zeros) in A. The bytes just
before it read `0026 0025 060ED900`.

Derived files are in ignored `research/memory_dumps/exp0013/`:

| File | SHA-256 |
| --- | --- |
| `glyph_seq.json` | `705d28d2…542d` |
| `C1_table_hits.json` | `fa25c195…c9ee` |
| `C2_table_hits.json` | `c763a02c…46dd` |
| `C2b_table_hits.json` | `d1f93cb6…6ab5` |

The `*_pattern.txt` files hold the tool inputs.

## Conclusion

The hypothesis is `DISPROVEN`: the font is not resident in WRAM or cart RAM as 4 bpp
cells or as an uncompressed 1 bpp bitmap.

`SUPPORTED` (strong; no mutation yet):

- Ryu's win quotes are held in WRAM-L as fixed 38-cell records of 16-bit glyph
  codes. The record for Q10 is at `0x0020940C`.
- The current quote is copied into a WRAM-H buffer at `0x060ED80A`.
- Each glyph is rendered through a staging cell at `0x0601CEEC` into VDP1 VRAM.

The code space is a custom font index. Its kana order follows Shift-JIS.

## Uncertainty and Alternatives

- Causality is untested. Changing a code in the WRAM-L record, or in the WRAM-H
  buffer before rendering, and observing the screen is `RE-012` (M1), gated by
  `GATE-M0`.
- Kanji codes (`0x0401-0x0C42`) have no derived rule. Their order and font source
  are unknown.
- The table's full extent and record count beyond the 15 contiguous records, and
  whether it holds only Ryu's quotes, are unknown. How it gets into WRAM-L (it is
  present before the KO) is `DISC-001` work.
- The transcriptions used for the kana check are unreviewed (`REF-003`).

## Reproduction

```bash
O=research/memory_dumps/exp0013
./invenv.sh python -m tools.text.pattern_search \
  research/memory_dumps/ab60af86089a9575/wram_l.bin "$(cat $O/C1_pattern.txt)" \
  --base 0x00200000
```

Patterns come from `tools.memory.vdp1_sprites --color-word 0x61E0 --json`, read in
`(y, x)` order. Each distinct glyph cell (by SHA-256) becomes a symbol, and each
blank cell becomes `=0x20`.
