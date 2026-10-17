# EXP-0022: English Layout Capacity in Win Quotes

Task: `LAYOUT-001`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED (font source and load path; pair glyph display); HYPOTHESIS (alternate layout set)

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

## Actual Result: Phase A (2026-10-17)

The font image is the 206,656 bytes of cart RAM at `0x0278CF60` in state A
(`ab60af86…`, unvalidated region, but `EXP-0020` reproduced all 79 glyphs from it).

**Search.** 64-byte fragments at font offsets 0, 0x10, 0x390, 0x8000, 0x10000,
0x20000, and 0x30000 were searched across the 414 extracted files plus 52 decoded
PACs. Every one was found in `MEMFIX.PAC`, at file offsets with the same relative
spacing.

**Full comparison.** `MEMFIX.PAC[0x6A558:0x6A558+206656]` **equals the font image
byte for byte**. The file is LSN 3,954, 1,744,100 bytes, SHA-256 `fdbc871a…65d9`.

**`MEMFIX.PAC` container** (big-endian):

- **Header.** Thirteen `(word0, size)` pairs, with the 13th `(0, 0)` as terminator
  (0x68 bytes).
- **Entries.** Twelve entries follow back to back, uncompressed (`word0` = 0). Their
  sizes are `4FEF0 EBB0 96A0 23B0 32740 86BC0 360 3BC0 18A44 22512 40000 7614`.
- **Entry 4.** Starts at `0x6A558` with size `0x32740` = 206,656: the font.
- **Size check.** The entries end at `0x1A9CE2`; the file is `0x1A9CE4` (2 trailing
  bytes).

Elsewhere in the file, 88 of 107 sampled 64-byte chunks of `MEMFIX.PAC` also occur
in cart RAM, consistent with the file being loaded largely verbatim into the cart.
The loader was not traced.

**Phase A conclusion.** `CONFIRMED`: the font image is stored verbatim as
`MEMFIX.PAC` entry 4. That this entry is the source loaded into cart RAM is
`SUPPORTED` (byte equality; the loader is not traced). Phase A2 (a cart write
breakpoint) is not needed.

## Actual Result: Phase B (partial)

`tools/sh2/disasm.py` (new, with tests) was used on WRAM-H of `EXP-0010` C1
(`9482880a…`).

- **Pointer literals.** `0x060ED900` at `0x060AF7F8` and `0x060ED800` at
  `0x060AF7F4` (and `0x060AEE00`) are in code that writes 16-bit entries through
  R6/R7 with GBR-relative counters (`@(26,gbr)`, `@(30,gbr)`, `@(6,gbr)`,
  `@(10,gbr)`).
- **Calls.** Subroutines are called via `trapa #62` followed by an inline address
  (`060AF81E`), with `trapa #63` as a return or end marker. That is an unusual
  convention and is not yet traced.
- **Two constant sets**, chosen by a flag at `@(r0=0xCC90, r11)`:
  - `add #38,r8` vs `add #50,r8` (38 = 19 × 2 bytes; 50 = 25 × 2);
  - `mov #16` vs `mov #12` stored to `@(6,gbr)`;
  - `mov #17` vs `mov #23` stored to `@(24,gbr)`.

  This is consistent with an alternate denser text layout (12-pixel step, about 25
  cells per line). It is `HYPOTHESIS`: neither the flag's meaning nor any use of
  the second set has been observed.
- **Selection code.** The routine before the buffer writer (`0x060AF820-0x060AF8C8`)
  increments and wraps a byte counter at `@(76,r12)` against byte tables at
  `0x060AF8E8`/`0x060AF908`. So `EXP-0014`'s reading of `#76` as the record stride
  is withdrawn; there, `#76` is a struct field offset. The routine looks like quote
  selection, which may bear on `EXP-0010`'s Q3 non-recurrence (`HYPOTHESIS`).

## Phase C Refinement (pre-registration update)

Because the font is an uncompressed entry inside `MEMFIX.PAC` (852 sectors, 796
bytes of slack), growing the entry would shift later entries. The smallest change
is therefore a same-size glyph replacement:

- overwrite the 128 bytes of one existing **raw** glyph (raw codes:
  `0x0090-0x009E`, `0x02C5`, `0x02C7`, `0x02CB`, `0x02CD`, `0x02CF`, `0x02E7`,
  `0x02ED`, `0x02EF`, `0x0301`, `0x0323`, `0x0326`, `0x0340`, `0x0700`, `0x0708`,
  `0x0725`) with a two-letter quote-style pair glyph;
- reference that code from a quote record.

Delivery: rebuild `MEMFIX.PAC` with only that 128-byte span changed, using a
generalized `patch_image`, together with a `MC09.PAC` table patch that uses the
code. Both go into one derived image via the `DISC-002` pipeline, booted cold.

Side effect to record: the replaced raw glyph's original use (for example the
`0x009x` continue-screen artwork) will show the pair glyph instead.

## Phase C Build and Offline Checks (2026-10-17)

### Pair glyph

`tools/text/glyph_patch.py` (new, with tests) builds the glyph:

- **Ink.** Ink from full-width `T` (`0x08FB`) and `h` (`0x0909`), squeezed 2:1
  horizontally and placed side by side.
- **Style.** Body `1` with a recomputed shadow `F` at +1 column, +1 row, and +1
  diagonal.
- **Placement.** Written over raw glyph **`0x0725`** (font address `0x027A509A`,
  `MEMFIX.PAC` file offset `0x82692`). 127 of 128 bytes changed. Original and
  modified bytes are in `build/exp0022c/memfix_patch.json` (`f1edd602…`).

Patched `MEMFIX.PAC` SHA-256 prefix: `70e4f95fd72f5aa6`. The ignored preview
`build/exp0022c/pair_preview.png` shows a legible `Th`.

### Raw-glyph inventory (for side effects)

| Codes | Content |
| --- | --- |
| `0x0090-0x009E` | Dither or gradient tiles |
| `0x02C5-0x0326` | Large stylized digit pieces |
| `0x0340`, `0x0700`, `0x0708`, `0x0725` | Artwork fragments |

`0x0725` was chosen as the least likely to appear during a fight or win screen. Its
original use is unknown.

### Quote table

`MC09.PAC` patch: decoded `0x91AC + 76·r` (line-1 cell 0 of all 16 records) =
`0x0725` (16 writes).

- **Splice failed.** The splice re-encode exceeded the file size by 4 bytes (25,132
  vs 25,128).
- **Full re-encode.** `tools/disc/pac_patch.py --full` (new option, tested) was used
  instead. Stream: 24,658 bytes. File: 25,128 bytes, with **446 zero-fill bytes**.
  That is a deviation from `EXP-0019`'s splice and its 14-byte fill.
- **Hashes.** Patched file `3a99ecb1…`, decoded `3af26268…`, manifest
  `c96c8d95…`.

### Image

`tools/disc/patch_image.py` now accepts repeated `--file`/`--data` pairs (tested).
It was run twice into `build/mshvsf_exp0022c_{a,b}`.

- Changed sectors: LSN **4,214** (`MEMFIX.PAC`, one sector) and **8,246-8,258**
  (all of `MC09.PAC`).
- Builds identical. Track 01 SHA-256 `40f250fe5b2caa56…787e`.
- Tracks 02-12 and the CUE are byte-identical to the source.
- Build manifest `c3de51c1…`.

### Offline verification

- `iso9660 --check` reports 0 errors, 414 files. Only `MEMFIX.PAC` and `MC09.PAC`
  differ.
- `sector` verify: 0 of 192,346 invalid.
- Decoded `MC09.PAC` differs from the original in exactly the 16 target cells, all
  `0x0725`.
- In the decoded font, only glyph `0x0725` changed, and it equals the pair cell. No
  other `MEMFIX.PAC` byte changed.
- Source identity unchanged.

### Boot prediction

On a cold boot of the derived image, Ryu's win quote shows `Th` in line-1 cell 0,
solid with a shadow, with the rest of the quote unchanged. The `EXP-0015`/`EXP-0021`
runs on the original image are the controls.

## Phase C Result: Cold Boot (2026-10-17)

The derived image `build/mshvsf_exp0022c_a` was booted cold in stock Mednafen 1.32.1:

- process 76746;
- log `local/mednafen/logs/layout001-exp0022c-boot.log`, reporting `T-1238G` and
  `Cart: 4MiB Extended RAM`.

The user played arcade mode (Ryu/Ken), won twice with Ryu landing the KO, and
reported no glitches. No save state was loaded.

| Win | Screenshot | State | Shown |
| --- | --- | --- | --- |
| 1 | `-0054.png` `96f09973…f21c` | slot 7 `f043430b5c2c687c…8919` | `Thうした、もっと打て！…` (Q6; `ど` replaced by the pair glyph) |
| 2 | `-0055.png` `78a6beba…5afd` | slot 8 `724b2288ab7039dd…048e` | `Th` then `おれは・・・` (Q11; blank cell 0 replaced) |

From both states:

- cart RAM font glyph `0x0725` equals the composed pair cell;
- WRAM-L `0x002091AC-0x0020966B` equals the patched decoded table.

States are archived as `exp0022c-slot{7,8}`. Source identity was unchanged.

## Conclusion

`CONFIRMED`:

- **(1) Font load path.** `MEMFIX.PAC` entry 4 is the source of the cart-RAM quote
  font. Changing it on disc changes the in-memory font, which upgrades Phase A's
  load path from `SUPPORTED`.
- **(2) Pair glyph.** A custom two-letter quote-style pair glyph, written over a raw
  glyph and referenced from the quote table, displays legibly in Ryu's win quote
  from a rebuilt image. This held on two records in two independent wins.
- **(3) Re-encoding.** Fully re-encoding `MC09.PAC` with 446 zero-fill bytes is
  accepted by the game.

## Capacity Model and Recommended Route

**Route R1 (pair glyphs): viable and recommended.**

- Capacity is 2 × 19 cells × 2 letters = **76 characters per quote**, mixing pair
  glyphs and full-width glyphs as needed.
- **Main constraint: glyph storage.**
  - Same-size replacement is limited to the 30 raw glyphs, whose original uses are
    unknown.
  - Scaling to many distinct pairs needs new storage. Options: grow `MEMFIX.PAC`
    entry 4 (which shifts entries 5-11 and may move their cart load addresses), or
    recompress existing glyphs to free space.
  - That is a separate investigation. The loader's use of the `MEMFIX` header is
    untested.
- Free codes are plentiful: 712 empty codes, including runs of 88, 80, 80, and 417.

**Route R2 (layout change): deferred.** Phase B found a flag-selected alternate
constant set (38 vs 50 line offset, 16 vs 12, 17 vs 23), which is `HYPOTHESIS`.
It would also need solid half-width glyphs and a new record format.

**Not yet known:** how many distinct pairs the official English needs
(`REF-004`/`GATE-TRANSLATION`).

## Remaining Uncertainty

- The original use of raw glyph `0x0725` is unknown, so its replacement's side
  effect was not observed.
- Only one pair glyph was tested.
- The pair glyph's compressed form is untested; it was stored raw.

