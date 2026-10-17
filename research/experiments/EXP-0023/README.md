# EXP-0023: Expand Quote-Font Capacity for Many Pair Glyphs

Task: `FONT-003`
Date: 2026-10-17
Status: IN_PROGRESS
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

## Actual Result: Phase A (2026-10-17)

### Measured layout

- **Header** (16 bytes): `00…00 00000C60`. The last word, `0x0C60`, is the code
  count (codes `0x000-0xC5F`).
- **Block table** (224 longs at 0x010): the 198 blocks below the count hold the
  running data offset (relative to 0x010). The 26 blocks at or above it hold 0.
- **Size table** (0xE00 bytes at 0x390): raw glyphs always use `0x80`.
- **Data** fills the entry exactly (end = 0x32730 relative to 0x010), with no slack.

### Repacker

`tools/text/font_pack.py` (new, with tests): unpack all 3,584 codes, then pack
with the canonical column-run encoder.

```bash
./invenv.sh python -m tools.text.font_pack research/extracted_files/mshvsf_saturn_jp/MEMFIX.PAC
```

The rebuild is **byte-identical** to `MEMFIX.PAC` entry 4: 206,656 bytes, SHA-256
`3d8e9a26a2021d8ba44e0b920930a1e338785d96606a573cfbc0364bffc44efb`. Counts:
2,842 compressed, 30 raw, 712 empty.

**H-A: `CONFIRMED`.**

## Actual Result: Phase B

`tools/text/quote_census.py` (new) finds runs of at least 4 consecutive 76-byte
records whose words are all blank (`0020`), placeholder (`0000`), or non-empty
font codes (at least 3 text cells and 1 blank per record). Validated on
`MC09.PAC`: exactly one table, 16 records at `0x91AC`.

### All 23 decoded `MC*.PAC`

Report `census_mc.json`, SHA-256 prefix `00e58009`:

| Files | Tables found |
| --- | --- |
| `MC01`, `03`-`06`, `09`-`0B`, `0D`-`12`, `14`-`16` | one 16-record table each |
| `MC07` | 15 records |
| `MC02`, `MC08` | two 16-record tables each |
| `MC0C` | 4 + 8 + 8 records |
| `MC00` | 26 + 14 + 9 + 43 records |
| `MC13` | 120 records |

The union is **700 codes**.

### Other files

Report `census_other.json`, prefix `809f0303`. Other decoded PACs and raw
non-audio/non-ST2 files:

| File | Record-shaped runs |
| --- | --- |
| `ME.PAC`, `ME.SHX` | 15, 17, 40, 25 |
| `MM.BIN` | 5, 6, 4, 4, 7, 46 |

The union is **516 codes**. The combined union is **839** of 2,872 non-empty glyphs.

### Reclaimable space

`unseen_codes.json`, prefix `32e513ae`. Non-empty glyphs in no found table,
excluding ASCII `0x20-0x7E` and full-width punctuation, Latin, and digits
`0x8A9-0x925`, total 1,922 glyphs and 131,307 bytes:

| Code range | Glyphs | Bytes |
| --- | ---: | ---: |
| `0x00xx` | 52 | 2,929 |
| `0x01xx-0x03xx` | 571 | 38,860 |
| `0x04xx-0x07xx` | 959 | 57,944 |
| `0x08xx` | 19 | 1,339 |
| Kanji `0x0926-0x0C5F` | 321 | 30,235 |

The `0x01xx-0x07xx` ranges contain UI artwork (for example "PRESS START",
"INSERT COIN", stylized digits; `EXP-0020` atlas) drawn by non-table code, so
"unseen" there does **not** imply unused. Kanji are plausibly text-only. 504 of
825 kanji are used by the found tables, and **321 kanji (30,235 bytes) are unseen,
enough for about 817 pair glyphs** at 37 bytes.

**H-B: `SUPPORTED`.** The win-quote code set is measured. "Unused" is an
inference limited to record-shaped text: endings or story text in another format
would not be detected.

## Phase A-B Conclusion

- The font can be repacked losslessly at the same size.
- A low-risk reclaim set (unseen kanji) funds about 800 pair glyphs, comfortably
  more than one character's English quote set.
- The broader set (about 131 KB) needs a UI-usage census first.

Phase C (cold boot):

- repack with a declared sacrificial set drawn from the unseen kanji;
- add at least 8 new pair glyphs in free codes below `0x0C60` (for example
  `0x00A8+`), so the header is unchanged;
- show them in a Ryu quote and sample unchanged glyphs.

## Phase C Build and Offline Checks (2026-10-17)

### Font repack

`tools/text/pair_font.py` (new, with tests) unpacks entry 4, composes pair glyphs
with `glyph_patch.compose` from the full-width Latin glyphs, and stores them at
consecutive free codes. It then empties sacrificial glyphs, highest code first,
from the unseen kanji (`0x0926-0x0C5F` in `unseen_codes.json`), only until the
repack fits. The rest of the entry is zero-filled to 206,656 bytes, so the header
(code count `0x0C60`) and every other `MEMFIX.PAC` entry are unchanged.

```bash
./invenv.sh python -m tools.text.pair_font research/extracted_files/mshvsf_saturn_jp/MEMFIX.PAC \
  --text "Is that all you got!" --first-code 0x00A8 \
  --candidates research/memory_dumps/exp0023/unseen_codes.json \
  --out build/exp0023c/MEMFIX.PAC --manifest build/exp0023c/font_manifest.json
```

| Code | Pair | Code | Pair |
| --- | --- | --- | --- |
| `0x00A8` | `Is` | `0x00AD` | `l␣` |
| `0x00A9` | `␣t` | `0x00AE` | `yo` |
| `0x00AA` | `ha` | `0x00AF` | `u␣` |
| `0x00AB` | `t␣` | `0x00B0` | `go` |
| `0x00AC` | `al` | `0x00B1` | `t!` |

- 10 distinct pair glyphs, 341 bytes in total. All 10 codes were empty in the
  original font.
- **Sacrificed (4 unseen kanji, 387 bytes):** `0x0C5E`, `0x0C5D`, `0x0C5C`,
  `0x0C54`.
- Packed size is 206,610 bytes, with 46 zero-fill bytes.
- Font image `23c5c2f5…`, `MEMFIX.PAC` `90ff759c1cb8016f…`, manifest
  `d9fab066…`.
- Preview `build/exp0023c/pair_preview.png` (ignored) reads "Is that all you got!".

**Offline font check:**

- Changed bytes lie only inside entry 4 (`0x6A596-0x9CC96`).
- Unpacked, the only changed codes are the 10 pairs and the 4 sacrifices.
- Each pair equals its composed cell, the sacrifices are empty, and the header is
  identical.

### Quote table

`MC09.PAC`, all 16 records (decoded `0x91AC + 76·r`):

- line-1 cells 0-9 = `0x00A8-0x00B1`;
- line-1 cells 10-18 = `0x0020` (blank);
- line 2 (cells 19-37) unchanged as the control sample: 87 distinct original
  kana and kanji codes, none of them sacrificed.

`tools/disc/pac_patch.py` splice re-encode (304 writes, listed in
`build/exp0023c/mc09_writes.txt`, `565a4f5f…`):

- Stream kept unchanged up to byte 20,411 (decoded `0x91A4`). New stream 24,904
  bytes, with 200 zero-fill bytes.
- File `a4a0e2c1…`, decoded `21aa7d9d…`, manifest `a29c85a5…`.

### Image

`patch_image` was run twice with both files into `build/mshvsf_exp0023c_{a,b}`.

- Builds identical. Track 01 SHA-256 `5f5ef65134b47853587845272fcf4c9eba53eaa1245175c16ede5254a3298d46`.
- Tracks 02-12 and the CUE are byte-identical to the source.
- Changed sectors: LSN 4166-4168 and 4171-4267 (`MEMFIX.PAC` entry 4; 4169-4170
  hold unshifted glyph data) and 8246, 8255-8258 (`MC09.PAC`).
- Build manifest `f024958b…`.

### Offline verification

- `iso9660 --check`: 0 bad sync, mode, or address; 414 files. Only `MEMFIX.PAC`
  and `MC09.PAC` differ, and both equal the build inputs.
- `sector` verify: 0 of 192,346 invalid.
- Decoded `MC09.PAC` differs in 445 bytes, all inside the 304 target cells, and
  all of those cells hold the expected codes.
- Source identity unchanged.

### Boot prediction

On a cold boot, every Ryu win quote line 1 reads `Is that all you got!` (10 cells),
with the original Japanese line 2 intact. A line-1 blank or garbage cell
refutes H-C for that code.

## Phase C Result: Cold Boot (2026-10-17)

`build/mshvsf_exp0023c_a` booted cold in stock Mednafen 1.32.1 (process 79959,
log `local/mednafen/logs/font003-exp0023c-boot.log`, `T-1238G`, `Cart: 4MiB
Extended RAM`). The user played arcade mode (Ryu/Ken) and won twice with Ryu
landing the KO. No save state was loaded.

| Win | Screenshot | State (archived `exp0023c-slot{7,8}`) | Shown |
| --- | --- | --- | --- |
| 1 | `-0056.png` `a24f5db2…8e09` | slot 7 `9230247559018389…2876` | line 1 `Is that all you got!`; line 2 original Japanese of record 4 |
| 2 | `-0057.png` `8ac938ae…a85a` | slot 8 `9351f7d8775ea19f…86c9` | line 1 `Is that all you got!`; line 2 original Japanese of record 5 |

Records are 0-based (decoded `0x91AC + 76·r`). They were identified by matching
line 2 of the WRAM-H display buffer `0x060ED80A` to the table.

From both states (extractor regions `cart_ram`, `wram_l`, `wram_h`):

- The cart RAM font at `0x0278CF60` (206,656 bytes) equals the repacked image.
  Pair codes `0x00A8-0x00B1` decode to the composed cells, and the 4 sacrificed
  codes are empty.
- WRAM-L `0x002091AC-0x0020966B` equals the patched decoded table.
- The display buffer begins `50A8 … 50B1`, then `5020` blanks.

All 10 pair glyphs rendered legibly in the game's style. In both wins the
original kana and kanji on line 2 (two different records) rendered normally.

**H-C: `CONFIRMED`.** A same-size repack that adds glyphs at free codes below the
code count, funded by emptying unseen kanji, loads and displays correctly.

Limitations:

- Only 4 kanji were sacrificed. Whether untested text (menus, story, endings) uses
  them is still unknown, as is any other use of codes `0x00A8-0x00B1`.
- Only 2 of 16 records were seen live; the other 14 were verified offline and in
  RAM.

## Conclusion

`FONT-003` acceptance criteria are met:

- lossless repack (Phase A);
- census (Phase B);
- 10 new pair glyphs displayed from a cold boot, with the original glyphs intact
  and the sacrifices recorded (Phase C).

Capacity: the 321 unseen kanji fund about 800 pair glyphs. Phase D (growth or a
second font region) is not needed unless the full English set exceeds that.
