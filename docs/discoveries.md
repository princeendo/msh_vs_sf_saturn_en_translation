# Confirmed Discoveries

## EMU-004: Stock MSHvSF Boot Endpoint

Confidence: **CONFIRMED**

Experiment: `EXP-0001`

Stock Mednafen 1.32.1 reaches a stable, visibly rendered MSHvSF Saturn title
screen from the recorded untouched Japanese source image using the project-local
runtime root and selected BIOS aliases. The observed runtime log identifies
software `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`.

Source identity is the 13-component manifest in
`references/mshvsf/saturn_jp/README.md`; every component hash matched before and
after the run. The stock binary is
`vendor/mednafen/build/src/mednafen`, 21,322,536 bytes, SHA-256
`ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`. The
canonical Japanese and North American/European BIOS aliases are unchanged from
the hashes recorded in `docs/mednafen.md`.

The ignored endpoint screenshot is
`local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0001.png`,
352x240, 22,616 bytes, SHA-256
`4c19283ec7c84b6b7690fa526e3323a7e0121efa75fa5fa9c6e88bf3c24f0d85`. The
retained ignored launch log is 4,190 bytes, SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`.

Reproduction uses the launch command and host input sequence recorded in
`research/experiments/EXP-0001/README.md`. This confirms the baseline boot
endpoint only; it does not close `EMU-005`, validate every input, or establish
that the source-image CUE warnings are irrelevant to later experiments.

This file contains only durable findings rated **CONFIRMED** by a controlled,
reproducible experiment. Environment setup, observations, hypotheses, supported
claims, visual similarity, and isolated byte matches do not qualify.

## EMU-005: Forced 4 MiB Cartridge Operation

Confidence: **CONFIRMED**

Experiment: `EXP-0002`

With the untouched MSHvSF Saturn source image and stock Mednafen 1.32.1, forcing
`ss.cart=extram4` selects `Cart: 4MiB Extended RAM` for software `T-1238G`. Three
cold launches reproduced the same selection and reached the rendered MSHvSF title
screen with `PRESS START BUTTON` after the recorded input sequence.

The source identity is the 13-component manifest in
`references/mshvsf/saturn_jp/README.md`; all component hashes matched before and
after. The stock binary is the unchanged
`vendor/mednafen/build/src/mednafen`, 21,322,536 bytes, SHA-256
`ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.

The successful runtime log is 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`. The ignored
host captures and exact commands are recorded in `EXP-0002`. This finding is
limited to cartridge configuration and operation sufficient for the tested boot
path; it does not establish direct cartridge RAM read/write or address-boundary
behavior.

## EMU-009: Repeated Save/Load Checkpoint

Confidence: **CONFIRMED**

Experiment: `EXP-0006`

Stock Mednafen 1.32.1 saved and restored a documented MSHvSF title/menu checkpoint
in two cold observations. Each run advanced to the mode-selection screen, then
returned to the title scene after `F7`; the second run used a distinct state slot.

The ignored slot-0 state is 3,173,150 bytes with SHA-256
`e54380cfca308b1058f92d2840bde73e4c13d01bd9e4b8c864be82a3730b66db`. The ignored
slot-1 state is 3,244,032 bytes with SHA-256
`88e8945770bf26667e9006aff476b4d5dab7f7eaef93fa471ceced343dc93d80`. State files
are checkpoint artifacts, not RAM dumps, and were not decompressed or diffed.

The source image matched the 13-component manifest before and after both runs. The
stock binary and BIOS aliases were unchanged. Both run logs were 4,248 bytes with
SHA-256 `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c` and
reported `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`.

The title background and attract mode are time-dependent, so an immediate screenshot
after `F7` is required when the title scene is the checkpoint criterion. The exact
screenshots, temporary host mapping, and reproduction procedure are recorded in
`research/experiments/EXP-0006/README.md`.

## EMU-010: Stock Debugger Access and Repeatable Dumps

Confidence: **CONFIRMED**

Experiment: `EXP-0007`

Stock Mednafen 1.32.1 opens its debugger against the untouched MSHvSF Saturn source
(`Option+D` on this Mac host). CPU-view `S` pauses and `R` resumes emulation. During
a frame-advance pause (`Option+A`), the memory editor (`Option+3`) dumped High Work
RAM, Low Work RAM, VDP1 VRAM, and VDP2 VRAM to files. Two High Work RAM dumps were
byte-identical, SHA-256
`cdc1593260a18e98c3feae4e124bd9b93852176baefe91ec724e834be85ec2f0`. The inclusive
re-dumps `wram-c.bin` (High Work RAM, SHA-256
`5e7c2347ddf805da44fddafe7f663bbb23d8896a7014bcbea9a4f4790f94ead0`) and
`wraml-b.bin` (Low Work RAM, SHA-256
`0cb95fbf577923bfc2729e5d5303b2200a6ea9e9d77dcbdde39dddbecd4f9a5c`) are exactly
1,048,576 bytes and match the earlier dumps' first 1 MiB.

The memory editor lists 13 address spaces, recorded in `docs/mednafen.md`, and none
is cartridge RAM. Work RAM spaces are offset-based. The source image, stock binary
(`ca9bec5f…2587`), and BIOS aliases matched their recorded hashes. Exact commands,
artifacts, and limits are in `research/experiments/EXP-0007/README.md`. This does not
establish that a save state's contents equal these dumps, or any caption location.

## DBG-012: Validated Save-State Region Extraction

Confidence: **CONFIRMED**

Experiment: `EXP-0008`

`tools/memory/mcs_extract.py` parses stock Mednafen 1.32.1 Saturn save states. With
its default `saturn` byte order (each stored 16-bit element swapped on this
little-endian host), it reproduced the stock debugger dumps of the same paused
instant byte for byte:

| Region | Base | Size | SHA-256 (EXP-0007 slot 2) |
| --- | --- | ---: | --- |
| WRAM-H | `0x06000000` | 1,048,576 | `5e7c2347ddf805da44fddafe7f663bbb23d8896a7014bcbea9a4f4790f94ead0` |
| WRAM-L | `0x00200000` | 1,048,576 | `0cb95fbf577923bfc2729e5d5303b2200a6ea9e9d77dcbdde39dddbecd4f9a5c` |
| VDP1 VRAM | `0x05C00000` | 524,288 | `173764195179ce178ff8475c7c82d51dd17bd7e3014fa2e025f58d2a18a8894d` |
| VDP2 VRAM | `0x05E00000` | 524,288 | `fa94f7ca4c62267bf05f97a492ef91c3f82aa6a3b7ec676215446b7724360b0f` |

The input state is 3,848,175 bytes, SHA-256
`2c735816da8fcb2dbcc63b62da05454a07994f3f08ba56239fbe5fa829c65eb9`. The unswapped
stored order differed from every dump. Repeated extraction was byte-identical. Under
`AGENTS.md`, these four regions may now be acquired from save states.

Cartridge RAM (`0x02400000`, 4 MiB) is extracted with the same method but is **not**
validated; the stock debugger has no reference for it. Reproduction commands are in
`research/experiments/EXP-0008/README.md`.

## EMU-011: Stock Debugger Write, Revert, and Write Breakpoints

Confidence: **CONFIRMED**

Experiment: `EXP-0014`

With stock Mednafen 1.32.1 and the untouched MSHvSF source, frozen by frame advance
at state A (slot 5, SHA-256 `ab60af86…dce6`), the memory editor's `L` command wrote
a 1,140-byte file into Low Work RAM `0x000091F8-0x0000966B`. Dumps verified each
step:

- after the write: `08a1a3aa1d9d759ff9dc849e227fa2bf79df6175f49cf37ca8453466c0ab06bf`,
  equal to the loaded file;
- after loading the original back:
  `78fd5a38c1e545ca04a6bf3d5f460c57d100821c2a7a8d35d20345cb083ebce3`, equal to the
  pre-write dump.

A CPU write breakpoint on `060ED80A-060ED8A1 260ED80A-260ED8A1` fired during a
replay from state A, before the quote was drawn. The debugger opened at PC
`0x060AF8C6`.

Commands and limits are in `docs/mednafen.md` (EMU-011 runbook). This confirms the
workflow only; what the written bytes mean is `RE-012` work.

## RE-012: Ryu Win-Quote Table in WRAM-L Drives the Displayed Caption

Confidence: **CONFIRMED**

Experiment: `EXP-0015` (structure from `EXP-0013`, workflow from `EXP-0014`)

During a Ryu/Ken vs Vega arcade fight (stock Mednafen 1.32.1, untouched source),
WRAM-L holds Ryu's win quotes as 16 records of 38 big-endian 16-bit glyph codes
(76 bytes each). The records cover `0x002091AC-0x0020966B`: two lines of 19 cells,
with `0x0020` as a blank cell.

Loading a patch into state A (slot 5, SHA-256 `ab60af86…dce6`) changed line-1 cells
0-2 of the 15 records at `0x002091F8-0x0020966B` to `0801 0803 0805`. The patch was
loaded with the memory editor `L` command into `0x000091F8-0x0000966B` and verified
by dump (`08a1a3aa…ab06bf`). After the KO, the displayed quote showed `あ い う` in
those cells in all three patched runs that selected a patched record:

- Q8 at `0x00209290`, twice (`-0039.png`, `-0043.png`);
- Q5 at `0x002094F0` (`-0044.png`), with the original `もっ` replaced.

Two controls loading the original bytes showed unmodified quotes. Original and
modified bytes for all 45 writes are in the `re012-aiu-manifest.json` record
described in `EXP-0015`.

Scope: line-1 cells 0-2 of two records, codes `0801`, `0803`, and `0805`
(`あ`, `い`, `う`). Other code meanings, the partner-name placeholder (`0000` at
`0x002091BC`), and the disc source of the table are not confirmed here.

## DISC-001: Ryu Quote Table Source Is LZSS-Compressed `MC09.PAC`

Confidence: **CONFIRMED**

Experiment: `EXP-0018` (with `EXP-0016` disc layout)

Picking Ryu at character select decompresses `MC09.PAC;1` into WRAM-L
`0x00200000`. The file is at LSN 8,246, 25,128 bytes, SHA-256
`6c096573622a515ceb81436dacbe9ed732adab11fde87a43c4e497e4b56a0016`.

- **Layout.** A 0x18-byte header; big-endian word 4 = compressed length
  `0x620D`, word 5 = decompressed length `0xB548`.
- **Stream.** LZSS from `0x18`. Flags are MSB-first, 0 = literal byte, 1 = two-byte
  match with length `(v & 0xF) + 3` and source `pos − 0x1000 + ((v >> 4) & 0xFFF)`.
- **Quote table.** The `RE-012` table is decoded offset `0x91AC-0x966B`.

Evidence:

- A write breakpoint on the table halted inside the in-game decompressor (PC
  `0x0603E446`), whose context names `mc09.pac`.
- Its 2 KB input buffer equals file bytes `0x4800-0x4FFF`.
- `tools/disc/pac_lzss.py` decodes the file to 46,408 bytes (SHA-256
  `6a6d8119…065a`), consuming exactly `0x620D` stream bytes. The output equals WRAM-L
  for all 37,292 bytes written at the breakpoint, and for the table in the pre-KO
  state.

Limits: the other header words, the trailing bytes, and any integrity check are
unknown. Disc patching is not yet tested.

## DISC-002: Marker Caption Reproduced from a Rebuilt Disc Image (M2)

Confidence: **CONFIRMED**

Experiment: `EXP-0019`

`tools/disc/pac_patch.py` re-encoded `MC09.PAC` using the `EXP-0018` LZSS format:

- The original stream was kept for its first 20,411 bytes, and the rest was
  re-encoded.
- The header became `00000000 8000620A 00000000 00000000 00006202 0000B548`.
- The file was zero-filled to its original 25,128 bytes (SHA-256 `c9b6fcce…`).
- The decoded payload carries `0801 0803 0805` in line-1 cells 0-2 of all 16 Ryu
  quote records.

`tools/disc/patch_image.py` wrote a derived image under `build/`:

- Track 01 SHA-256 `742aa0bdeb109a32c868e192f4ab539f3c818495b721020a468e15ae0ba23730`.
- Only LSN 8,246 and 8,255-8,258 changed, all with regenerated EDC/ECC. The
  generator reproduces all 192,346 source sectors exactly.
- All other files and tracks are byte-identical to the source.
- Builds are deterministic.

A cold boot in stock Mednafen 1.32.1 showed `あいう` at the start of Ryu's win quote
in two independent wins (Q2 and Q6). Saved-state WRAM-L held exactly the patched
table. The source image was unchanged.

Limits: tested only in Mednafen and only with same-size placement.

## FONT-001: Quote Font Location and Format

Confidence: **CONFIRMED**

Experiment: `EXP-0020` (Phase 1b)

Win-quote glyphs are drawn by a routine at WRAM-H `0x0601CE00` (code in R3) into a
staging cell at `0x0601CEEC`. It reads a font whose base pointer is at
`0x0601D8E4`, which was `0x0278CF60` (cartridge RAM) in the tested session.

- **Glyph location.** A block table at base+16 (one long per 16 codes) and a size
  table at base+16+`0x380` (one byte per code).
- **Size byte.** Negative means a raw 128-byte cell, and zero means empty.
- **Compression.** Positive sizes use a two-stage mask, column-major run fill.
  `tools/text/font.py` decodes it.

Decoding state A's cart RAM reproduces all 79 known quote glyph cells byte for
byte, including the drop shadow.

Phase 2 confirmed that ASCII codes `0041-0043` display as `A B C` in a quote, with
two patched runs and an unchanged control. They are faint 8x8 gradient glyphs.
Full-width quote-style Latin (`0x08E8-0x0925`) exists in the font (atlas). The disc
source of the font is unknown.

## FONT-002: Full-Width Latin Glyph Codes Display in Win Quotes

Confidence: **CONFIRMED**

Experiment: `EXP-0021`

A live WRAM-L table patch (line-1 cells 0-4 of all 16 Ryu records =
`08F9 0900 08FC 0902 091D`) showed full-width, shadowed `R Y U a 1` in Ryu's win
quote. This held on two different records (`-0051.png`, `-0052.png`), and the
control was unchanged.

The ranges A-Z `0x08E8-0x0901`, a-z `0x0902-0x091B`, and 0-9 `0x091C-0x0925` are
recorded in `data/text/font_codes.json`. The other codes in these ranges are atlas
evidence only.

## LAYOUT-001 Phase A: Quote Font Stored Verbatim in `MEMFIX.PAC`

Confidence: **CONFIRMED** (storage and load path; load path confirmed by `EXP-0022`
Phase C)

Experiment: `EXP-0022`

`MEMFIX.PAC;1` (LSN 3,954, 1,744,100 bytes, SHA-256 `fdbc871a…65d9`) is a container:

- a header of 13 `(0, size)` pairs ending with `(0, 0)`, 0x68 bytes;
- 12 uncompressed entries back to back.

Entry 4 (offset `0x6A558`, size `0x32740` = 206,656 bytes) is byte-identical to the
quote font image in cart RAM at `0x0278CF60` (`EXP-0020`). Changing it on disc
changes the in-memory font (`EXP-0022` Phase C). The loader routine itself is not
traced.

## LAYOUT-001 Phase C: Two-Letter Pair Glyph Displays in Win Quotes

Confidence: **CONFIRMED**

Experiment: `EXP-0022`

A derived image rebuilt from the untouched source showed the pair glyph legibly in
Ryu's win quotes in two independent cold-boot wins, on records Q6 and Q11. The
image had two changes:

- **`MEMFIX.PAC`:** raw font glyph `0x0725` (file offset `0x82692`, 128 bytes)
  replaced with a quote-style `Th` pair glyph;
- **`MC09.PAC`:** fully re-encoded so line-1 cell 0 of all 16 Ryu records uses
  `0x0725`.

Only LSN 4,214 and 8,246-8,258 changed, all with valid EDC/ECC. The saved states'
cart font and quote table matched the patch.

Route: pair glyphs give up to 76 characters per quote. Storing many pairs needs a
font-storage expansion that has not been tested.

## FONT-003 Phase A: Quote Font Image Layout (Lossless Repack)

Confidence: **CONFIRMED**

Experiment: `EXP-0023`

The quote font image (`MEMFIX.PAC` entry 4) is laid out as:

- a 16-byte header whose last word is the code count `0x0C60`;
- 224 block-table longs (running data offset relative to 0x010 for blocks below the
  count, 0 above);
- a 0xE00-byte size table (0 empty, `0x80` raw, else compressed length);
- glyph data in code order, filling the entry exactly.

`tools/text/font_pack.py` unpacks and repacks it **byte-identically** (SHA-256
`3d8e9a26…4efb`). That validates the format model and the canonical encoder.

## FONT-003 Phase C: Same-Size Font Repack Adds Displayable Pair Glyphs

Confidence: **CONFIRMED**

Experiment: `EXP-0023`

A repack of the quote font (`MEMFIX.PAC` entry 4) at the same size (206,656
bytes):

- adds 10 new pair glyphs at free codes `0x00A8-0x00B1`;
- empties 4 kanji (`0x0C5E`, `0x0C5D`, `0x0C5C`, `0x0C54`) that the census found
  in no record-shaped text;
- zero-fills the remaining 46 bytes;
- leaves the header (code count `0x0C60`) unchanged.

It was booted cold from a derived image with that font and `MC09.PAC` line 1 of
all 16 Ryu records set to those codes. Two independent wins showed `Is that all
you got!` with the original line-2 Japanese intact. Saved-state cart RAM and
WRAM-L matched the built font and table byte for byte.

- Source `MEMFIX.PAC` `fdbc871a…65d9` became `90ff759c…3137`.
- `MC09.PAC` became `a4a0e2c1…d870`.
- Derived track 01 is `5f5ef651…8d46`. Only LSN 4166-4267 (excluding 4169-4170)
  and 8246, 8255-8258 changed, all with valid EDC/ECC.
- Reproduce: the commands in `EXP-0023` "Phase C Build" (`tools/text/pair_font.py`,
  `tools/disc/pac_patch.py`, `tools/disc/patch_image.py`).

Limitation: other uses of the sacrificed kanji (menus, story, endings) are not
yet ruled out.

## RE-021: Offline Quote Renderer and Ryu Record Map

Confidence: **CONFIRMED** (renderer; 6 RAM-backed labels)

Experiment: `EXP-0024`

`tools/text/quote_render.py` draws a record from decoded `MC09.PAC` and the font
image:

- 2 lines x 19 cells on a 16-pixel grid;
- line-1 cell 0 at `(26, 186)` in a 352x240 Mednafen screenshot;
- body nibble 1 drawn as `(240,240,240)`.

Its body-pixel matcher picked the RAM-known record in 10 of 10 test screenshots,
across four builds (IoU 0.83-0.89, margin at least 0.63).

RAM-backed labels:

| Label | Record |
| --- | ---: |
| Q2 | 5 |
| Q5 | 11 |
| Q6 | 1 |
| Q8 | 3 |
| Q10 | 8 |
| Q11 | 12 |

`EXP-0019`'s "Q2, record 4" is corrected to record 5, per that experiment's own
saved-state display buffer. Records are 0-based, at decoded `0x91AC + 76·r`.

The matcher-only labels (`SUPPORTED`, not confirmed) are Q1 = 13, Q3 = 2, Q4 = 10,
Q7 = 9, and Q9 = 15. All data is in `data/text/ryu_quote_records.json`.

## RE-023: Win-Quote Record Selection and Forcing

Confidence: **CONFIRMED**

Experiment: `EXP-0025` (agent interface, `EMU-021`)

- **Index.** At PC `060AF282` the game stores the quote index as a word at WRAM-H
  `0x060F9E66` (normally `@(2,gbr) & 0x0F`).
- **Pointer.** The routine at `060AF6E0` stores the record pointer to
  `0x060F249C`, as table base (`@0x060F9E4A`, `0x002091AC` for Ryu) plus
  76 × index (100 when `r11+0xCC8E` is set). The text builder renders that
  record.
- **Evidence.** Breakpoint logs and screenshot matching agree in a natural run
  (index 0). Overwriting the index right after `060AF282` (agent `onhit`) showed
  exactly records 6, 7, and 14 from a post-KO checkpoint, with no input.
- **Partner name.** Record 0's `0000` placeholder rendered as the partner's
  name (ケン with Ken as partner), consistent with the name-expansion routine.
- **Open.** The source of `@(2,gbr)`, the special value 39 (table
  `0x06095544`), and the `0xCC90` remap stay `HYPOTHESIS`.

## RE-024: All 16 Ryu Records Display Compiled Captions

Confidence: **CONFIRMED**

Experiment: `EXP-0026`

- **Build.** `tools/text/caption_compiler.py` built the marker image
  (`data/captions/ryu_markers.json` → track 01 `fd007d13…`) from the untouched
  source.
- **Result.** After one cold boot and one KO, all 16 records were forced (agent
  `onhit 060AF282`) and verified:
  - pointer;
  - screen match: pixel-exact for records 1-15;
  - cart-RAM font, WRAM-L table, and display buffer.
- **Glyphs.** All 51 pair glyphs at `0x00A8-0x00DA` render as compiled.
- **Record 0.** The `0000` placeholder renders the partner name in katakana
  (ケン) directly after Latin text. Line 1 keeps 19 display entries.
- **Reproduce.** `EXP-0026` Procedure: `ko_capture.py` once with a KO, then 16
  forced runs and `verify_records.py`.

## RE-025: Ryu's Captions Across Team Contexts

Confidence: **CONFIRMED**

Experiment: `EXP-0027`

- **V1.** With Ryu as the **second** team member, his `MC09.PAC` table is decoded
  to WRAM-L **`0x002191AC`** (slot 2), not `0x002091AC` (slot 1). The pointer
  routine takes the base from the text structure (`0x060F9E4A`). All 16 marker
  records verified from that base.
- **V2.** With partner Gouki, the base and table are unchanged. Record 0's
  placeholder expands to ゴウキ (name-table entry 15), as Ken gives ケン
  (entry 10).
- **Implication.** The disc caption pipeline works in every tested context. Fixed
  RAM addresses do not.
- **Not tested.** Versus mode.

## REF-008: Local Arcade ROM Set Identities

Confidence: **CONFIRMED** (identity only; no game behavior)

Task: `REF-008` (reference audit, not a reverse-engineering experiment)

- **Finding.** The local `mshvsf.zip`, `mshvsfu.zip`, and `mshvsfj.zip` are the
  MAME 0.289 sets `mshvsf` (Europe 970625), `mshvsfu` (USA 970827), and `mshvsfj`
  (Japan 970707). All 20 ROM files in each zip match by name, size, CRC-32, and
  SHA-1, and no other set in the family matches more than 18 of 21.
- **Gap.** Each zip lacks its 20-byte CPS-II key file (`<set>.key`). MAME 0.289
  `-verifyroms` rejects all three sets for that key and for the shared QSound ROM
  `dl-1425.bin` (observed 2026-10-23).
- **Sources.** Zip hashes are in `references/mshvsf/arcade/README.md`. The driver
  `cps2.cpp` is pinned at commit `f34f02505e32c1993c6a782b6814232cbfc74e36`,
  977,277 bytes, SHA-256 `a8c09ef8…e861602`.
- **Reproduce.** The commands are in `references/mshvsf/arcade/README.md`
  (`tools/reference/mame_audit.py`, Python 3.12.13). The output is
  `references/mshvsf/arcade/mame0289_audit.json`.
- **Limits.** Identity only. This says nothing about the text these sets display.

## EXP-0029: Arcade Win-Quote Text Layout in Raw Program ROM

Confidence: **CONFIRMED** for the data layout; display is not yet observed

Experiment: `EXP-0029`

- **Finding.** In all three local arcade sets, the Latin-script win quotes
  (English, Spanish, Portuguese) are stored unencrypted in `mvs.07b`. Each
  character is one 16-bit code: `0x0161`+ is `a`-`z`, `0x0140`+ is `A`-`Z`,
  `0x0020` is a space, and punctuation and accents use the codes listed in the
  experiment.
- **Table.** The pointer table at program `0x20C014` has 78 longwords: 3 languages
  × 26 slots. Each points to a `0x320`-byte block of 8 quotes × 2 lines × 25 codes.
- **Same in every region.** The text digest (`5ede5615…`) and quote-table digest
  (`29db2b67…`) are identical for `mshvsf`, `mshvsfu`, and `mshvsfj`. The Japanese
  set therefore holds the same English text.
- **Reproduce.** Rebuild with `tools/reference/cps2_text.py`; the commands and full
  hashes are in `research/experiments/EXP-0029/README.md`.
- **Limits.** Data only. The slot-to-character mapping (Ryu = slot 9) is
  `SUPPORTED`, not confirmed. Wording becomes a quote source only after a MAME
  capture (`REF-010`).

## EXP-0030: Arcade Win Quotes on Screen Come From the Decoded Table

Confidence: **CONFIRMED**

Experiment: `EXP-0030` (task `REF-010`)

- **Finding.** In MAME 0.289, the arcade win-quote screen draws its two lines
  directly from the `EXP-0029` table. That includes the centering spaces.
- **Pointer.** While a quote is shown, work RAM `0xFF249C` holds the displayed
  entry's ROM address.
- **Ryu.** Ryu's quotes are slot 9 (`0x21BA20`). Quotes 6 and 7 were captured on
  `mshvsfu`, and quote 6 is pixel-identical on `mshvsf`.
- **Slots.** Slots 5, 6, 11, 12, 13, and 16 were also seen, matching the name
  list.
- **Reproduce.** The route is scripted with `tools/reference/arcade_route.py` and
  `tools/reference/mame_timeline.lua`. Snapshot hashes, pointer values, and
  commands are in `research/experiments/EXP-0030/README.md`.
- **Limits.** Six of Ryu's eight quotes and the other 19 slots are not observed on
  screen. English only. The quote-selection rule is unknown.

## EXP-0031: Saturn Ryu Records Pair With Arcade English by Game Logic

Confidence: **CONFIRMED**

Experiment: `EXP-0031` (tasks `REF-003`, `REF-004`)

- **Identity.** The Saturn `MC09.PAC` Ryu table (decoded `0x91AC`, 16 × 76 bytes)
  is byte-identical to the arcade Japanese Ryu table at `0x20EDAC`. That table is
  slot 9 of the Japanese pointer table at `0x20BFAC`, the same in all three arcade
  sets.
- **Selection.** The arcade selection routine (`mshvsfu` `0x070328`) masks a random
  value to a 16-way index `k`. In non-Japanese languages it remaps `k` through
  `00-07 00-07`, so English shows slot 9 entry `k & 7`.
- **Tested.** Breakpoint-set pre-mask values 12 and 9 gave index 4 and 1 (US) and
  12 and 9 (JP). Forced indexes displayed all 8 English entries and all 16
  Japanese records.
- **Result.** Saturn records `k` and `k + 8` correspond to official arcade English
  entry `k & 7`; Q10 (record 8) corresponds to entry 0.
- **Not a translation claim.** The pairing is game logic only.
- **Reproduce.** Run `tools/reference/quote_pairing.py`; metadata is in
  `data/text/ryu_arcade_pairing.json`.

## EXP-0032: PS1 English Win-Quote Data Equals the Arcade's

Confidence: **CONFIRMED** (data identity; PS1 display not captured)

Experiment: `EXP-0032` (task `REF-005`)

- **Finding.** The US PS1 release (`SLUS-00793`, Redump 12632) stores win quotes
  in the arcade's 16-bit codes, little-endian, in `DAT/SELECT.BIN`. All 26 arcade
  English slot blocks occur byte-identical; Ryu's slot 9 is at `0x1150C`.
- **Extra blocks.** Two all-Latin blocks with no arcade counterpart follow
  (`0x1376C`, `0x13A8C`).
- **Reproduce.** Run `tools/reference/ps1_text.py`. The comparison is in
  `references/mshvsf/ps1_us/arcade_en_comparison.json`.

## EXP-0033: Ryu's Official-English Win Quotes From a Rebuilt Image

Confidence: **CONFIRMED**

Experiment: `EXP-0033` (task `TR-001`)

- **Finding.** A deterministic image rebuilt from the untouched source shows all
  16 Ryu win quotes in the paired official arcade English (record `k` = entry
  `k & 7`).
- **Verified live.** All 16 records were checked: pointer, cart-RAM font, WRAM-L
  table, display buffer, and screen (IoU 1.0). Records 8-15 are pixel-identical to
  records 0-7 by design.
- **Punctuation.** `.` and `,` use the font's full-width period (`0x08AB`) and
  comma (`0x08AC`) inside pair glyphs.
- **Build.** Track 01 SHA-256 `2941a9c5…4719`.
- **Reproduce.**
  - Generate the spec from the local arcade ROM with
    `tools/text/official_captions.py` (the text is not committed).
  - Build with `tools/text/caption_compiler.py`.
  - Verify as in `research/experiments/EXP-0033/README.md`.

## RE-030: Ken Through the Generalized Caption Mechanism (M4)

Confidence: **CONFIRMED**

Experiment: `EXP-0028` Phase B

- **Finding.** One rebuilt image (`build/exp0028a`, track 01 `c3990fa5…`) holds
  compiled Ryu (`MC09`, `0x91AC`) and Ken (`MC0A`, `0xA59C`) tables with one
  shared pair font.
- **Verified live.** After one session (Ken KO, then Ryu KO), all 32 forced
  records verified in RAM and on screen. The bases were `0x0020A59C` for Ken
  (slot 1) and `0x002191AC` for Ryu (slot 2).
- **Placeholders.** Ken's line-2 placeholders (records 11 and 12) expand to the
  partner's name (リュウ). Ryu's record 0 gives ケン.
- **Reproduce.** See `research/experiments/EXP-0028/README.md` ("Resume: Phase B"
  steps and "Phase B Result").

## EXP-0034: Saturn Quote File Index Equals Arcade Character Slot

Confidence: **CONFIRMED**

Experiment: `EXP-0034` (task `RE-041`)

- **Finding.** Each of the 23 Saturn quote files `MC00`-`MC16` contains arcade
  slot `nn`'s whole 16-record Japanese block, byte-identical in all three arcade
  sets.
- **Name table.** The Saturn name table (WRAM-H `0x06095EC4`) orders the same 26
  characters as the arcade slots.
- **Classes.** 18 files are structurally ordinary (one block); 5 are irregular
  (`MC00`, `MC02`, `MC08`, `MC0C`, `MC13`).
- **Reproduce.** Run `tools/reference/slot_census.py`. The manifest is
  `data/text/coverage_manifest.json`.

## RE-042: Official-English Pairing for the 17-Character Roster

Confidence: **CONFIRMED** (byte identity; the remap is `EXP-0031`'s
slot-independent routine)

Task: `RE-042`

- **Finding.** For all 17 roster characters (`data/text/m5_roster.json`), the
  Saturn quote table is byte-identical to the arcade Japanese slot.
- **English.** The paired English block is identical in the US, EU, and JP arcade
  sets and present in the PS1 release. Record `k` pairs with entry `k & 7`.
- **Placeholders.** None of the 17 English blocks contains a `0000` placeholder.
- **Reproduce.** Run `tools/reference/roster_pairing.py`. The output is
  `data/text/roster_pairing.json` (hashes only).

## EXP-0035: 17-Character Official-English Roster Image (Offline)

Confidence: **CONFIRMED** (build and offline render; live check pending,
`RE-046`)

Experiment: `EXP-0035` (task `RE-045`)

- **Finding.** One deterministic image (track 01 `f5044e8a…`) holds the paired
  official English for all 17 roster characters in one shared font: 338 pairs,
  of which 90 reuse kanji codes.
- **No collateral changes.** Only the roster PACs and `MEMFIX` change, and the
  register's untouched blocks are byte-identical.
- **Renders.** All are legible.
- **Reproduce.** See `research/experiments/EXP-0035/README.md`.

## Entry Requirements

Each future entry must include:

- concise finding and scope;
- confidence label;
- experiment identifier;
- source and artifact hashes;
- exact reproduction commands and tool versions;
- predicted and observed results;
- relevant offsets, addresses, and bytes when measured;
- limitations and links to permitted evidence metadata.
