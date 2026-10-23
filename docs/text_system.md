# Text System

## Status

The MSHvSF Saturn text system is **UNKNOWN**. No encoding, storage structure, pointer
scheme, compression method, buffer lifecycle, font mapping, or renderer path is
confirmed.

`SUPPORTED` (not confirmed) candidates for post-fight win quotes are recorded in
`research/experiments/EXP-0012` and `EXP-0013`:

- VDP1 sprite glyph cells;
- 16-bit glyph-code records in a WRAM-L table;
- a per-screen WRAM-H buffer.

They move here only after a controlled mutation confirms them (`RE-012`).

## Confirmed Components

### Ryu win-quote table (WRAM-L)

- **Role.** It is the source of the displayed post-fight win quote: writing codes
  here before the quote screen changes the displayed glyphs.
- **Scope.** Confirmed for a Ryu/Ken vs Vega arcade fight, line-1 cells 0-2 of
  records Q8 (`0x00209290`) and Q5 (`0x002094F0`), and codes `0801`, `0803`,
  `0805` = `あ`, `い`, `う`.
- **Source image.** The 13-component manifest in
  `references/mshvsf/saturn_jp/README.md`.
- **Experiments.** `EXP-0013` (structure, `SUPPORTED`), `EXP-0014` (write
  workflow), `EXP-0015` (mutation, `CONFIRMED`).
- **Addresses.** Records are 76 bytes: 38 big-endian 16-bit codes, two lines of 19
  cells, with `0x0020` as a blank cell. There are 16 records at
  `0x002091AC-0x0020966B`.
- **Original bytes.** Listed per write in `re012-aiu-manifest.json` (summarized in
  `EXP-0015`).
- **Reproduction.** See `EXP-0015`.
- **Limitations.**
  - The full code mapping is not confirmed. Kana in Shift-JIS order is
    `SUPPORTED`; the kanji order is unknown.
  - The `0000` partner-name placeholder is a `HYPOTHESIS`.
  - The per-screen WRAM-H buffer (`0x060ED80A`), the builder code (PC
    `0x060AF8C6`), and the VDP1 glyph path are `SUPPORTED` but not separately
    confirmed.
  - Disc source (`CONFIRMED`, `EXP-0018`): LZSS-compressed `MC09.PAC`, decoded to
    WRAM-L `0x00200000` when Ryu is picked. The table is decoded offset
    `0x91AC`. The decoder is `tools/disc/pac_lzss.py`.
  - Disc patching (`CONFIRMED`, `EXP-0019`): re-encoding `MC09.PAC` at the same size
    with `tools/disc/pac_patch.py` and `tools/disc/patch_image.py` reproduces code
    changes in-game from a rebuilt image.
  - Font (`CONFIRMED`, `EXP-0020`): a compressed glyph table in cart RAM (base
    pointer at `0x0601D8E4`), decoded by `tools/text/font.py`. ASCII-shaped Latin
    glyphs exist at codes `0x0020-0x007E` (display `SUPPORTED`, pending a test).

## Caption Compiler (`RE-022`)

`tools/text/caption_compiler.py` builds a derived image from a caption spec
(`data/captions/caption_spec.schema.json`), reading both inputs from the untouched
source track:

```bash
./invenv.sh python -m tools.text.caption_compiler data/captions/ryu_markers.json \
  --out-dir build/re022_markers            # files, two images, all checks
./invenv.sh python -m tools.text.caption_compiler SPEC --out-dir build/X --capacity
```

- Lines are cut into two-letter pair glyphs. Distinct pairs go to free codes
  (`0x00A8+`), and unseen kanji are emptied only as needed.
- `{P}` keeps a record's `0000` placeholder, only at the cell where the
  original has one (Ryu record 0, cell 8; Ken records 11 and 12, cells 26 and 25).
- Schema `mshvsf-captions/2` lists several tables (`file`, decoded `table`
  offset). Pairs are shared across them in one font. Known tables: `MC09` Ryu
  `0x91AC`; `MC0A` Ken `0xA59C`.
- Outputs go to `OUT/files/`, `OUT/image_{a,b}/`, `OUT/records.png` (offline
  render), and `OUT/compile_manifest.json`.

## Questions to Resolve

- Where and when does the first Ryu post-fight caption enter memory?
- What bytes represent it, and how are boundaries determined?
- Is the displayed content stored directly, transformed, or assembled?
- Which code or data path selects and renders it?
- What size or layout constraints govern a safe replacement?

Resolve one question at a time with controlled experiments. Record hypotheses and
failures in `research_log.md`; add only reproducible confirmed behavior here.

## Future Finding Format

For each confirmed component, record its role, scope, source-image hash, experiment,
addresses or offsets, original bytes, interpretation, reproduction steps, and known
limitations. Never import assumptions from another game, release, or platform.
