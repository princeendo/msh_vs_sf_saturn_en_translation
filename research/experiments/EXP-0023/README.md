# EXP-0023: Expand Quote-Font Capacity for Many Pair Glyphs

Task: `FONT-003`
Date: 2026-10-17
Status: READY
Confidence: HYPOTHESIS

## Question

How can hundreds of pair glyphs be stored? `EXP-0022` showed one works, but the
only in-place slots are the 30 raw glyphs.

## Observations (2026-10-17, state A unless noted)

- **`MEMFIX.PAC` placement.** The 12 entries load to these destinations, found by
  64-byte probes:

  | Entry | Destination | Size |
  | ---: | --- | --- |
  | 0 | cart `0x02722830` | |
  | 1 | cart `0x02772720` | |
  | 2 | cart `0x027812D0` | |
  | 3 | cart `0x0278A970` | |
  | 4 (font) | cart `0x0278CF60` | 206,656 |
  | 5 | cart `0x02400000` | |
  | 9 | WRAM-L `0x002D7800` | |
  | 10 | cart `~0x027BF6A0` | 256 KB, ending about 2.4 KB before the cart end |
  | 11 | WRAM-H, partial match | |
  | 6, 7, 8 | not found | |

  Entries 0-3 are contiguous in the cart; entry 4 starts 0x240 after entry 3's end.
- **Fixed address tables.** Two tables in WRAM-H hold these destinations as
  literal longs: `0x06040274-0x060402A0` and `0x06041260-0x0604128C`, the latter
  including `0x027BF6A0`. A per-entry structure at `0x0601D7F4…` (font at
  `0x0601D8E0`, `{1, 0x0278CF60, 0, 0xB5D0, …}`) also holds them. Destinations are
  therefore table-driven, not computed by packing entries. Growing entry 4 would
  overwrite entry 10 unless the tables are changed. Even then there is only about
  2.4 KB of cart headroom (`HYPOTHESIS` about code behavior; the loader is not
  traced).
- **Disc space.** Track 01 has **no free sectors between files**; `MEMFIX.PAC`
  (LSN 3,954, 852 sectors) is followed directly by `PL00.PAC`. There are **150 free
  sectors** after the last file (LSN 192,196-192,345).
- **Recompression gives nothing.**
  - All 2,842 compressed glyphs are already stored at the size of a minimal
    column-run encoding (the stored size minus the canonical size totals 0 bytes).
  - The 30 raw glyphs would grow if compressed (4,164 vs 3,840 bytes).
- **Pair glyph size.** The `Th` pair glyph compresses to **37 bytes**.
- **Kanji space.** Codes `0x0926-0x0C5E` hold 825 kanji glyphs, **76,664 bytes**.
  Kana, symbols, and Latin use the rest.

## Hypotheses (one per phase)

### Phase A (offline): lossless font repacker

**H-A.** Rebuilding the font image from its decoded glyphs gives an image
byte-identical to `MEMFIX.PAC` entry 4 (206,656 bytes). The rebuild uses the
canonical encoder, original code order and raw/compressed choices, and regenerated
block and size tables.

- **Why first.** This proves the font layout model completely before any
  capacity change.
- **Tooling.** `tools/text/font_pack.py`: an encoder, a block and size table
  writer, and a raw-glyph policy (raw if the canonical size exceeds 127 or the
  original was raw), with tests.

### Phase B (offline): usage census

**H-B.** Glyph codes used by win quotes are a small subset of the font, and other
text uses are measurable.

- **Win quotes.** Find every 38-cell quote record in all 23 decoded `MC*.PAC`
  files, using the `EXP-0013` record shape (76 bytes, codes in the `0x00xx`,
  `0x04xx`, and `0x08xx-0x0Cxx` ranges, `0x0020` blanks), and list the codes they
  use.
- **Other text.** Count the same codes elsewhere, for example in other decoded
  PACs, as a hint of other text users.
- **Output.**
  - Per code: used in win quotes / not seen.
  - The byte total of glyphs never seen in any found text, which is the reclaimable
    space under a declared risk.

### Phase C (live, cold boot): same-size repack with many pair glyphs

**H-C.** A font repacked to exactly 206,656 bytes displays every new glyph and every
unchanged original glyph correctly. In it:

- N pair glyphs (for example N = 64, enough for a full English Ryu quote set) are
  added at free codes in fully empty blocks (`0x0D00+`);
- space is reclaimed by emptying a declared set of sacrificial glyphs, chosen
  from Phase B as "not seen in any found text", with the list recorded.

**Delivery:** same-size `MEMFIX.PAC` and `MC09.PAC` replacement via `patch_image`;
no table or address change.

**Prediction:**

- The repacked font decodes, offline, to exactly the intended glyph set.
- In game, a quote patched to show at least 8 different new pair glyphs renders
  them all.
- A sample of unchanged original glyphs (kana and kanji in other Ryu quotes) still
  renders. The sacrificed codes are not visible on the tested path.

**Risk:** a sacrificed glyph used by untested text (menus, story, endings) would
show blank. The list is recorded for later census.

### Phase D (deferred)

Only needed if Phase C's capacity is insufficient for the official English:

- grow the font with table and address changes (cart headroom about 2.4 KB);
- or add a second font region with a hook in the glyph routine `0x0601CE00`.

Both require tracing the loader and address tables.

## Decision Rule

| Evidence | Decision |
| --- | --- |
| Phase A fails | Stop and refine the font model |
| Phase B shows large reclaimable space | Phase C at scale |
| Phase B shows little | Phase D |

## Actual Result

Pending.
