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

## EXP-0036: Patched PAC Files Must Keep Their Declared Compressed Length

Confidence: **CONFIRMED** (for `MC12.PAC` loaded as an opponent; the mechanism is
`HYPOTHESIS`)

Experiment: `EXP-0036` (task `RE-046`)

- **Finding.** When a re-encoded `MC12.PAC` declares a compressed length about 270
  bytes or more shorter than the original, loading it as a CPU opponent sends the
  game to the BIOS.
- **Test.** Restoring only the header length words (`+0x04` = `0x80000000 |
  (length + 8)`, `+0x10` = length) to the original values, with the stream
  zero-padded, fixes it. The game decodes such a file correctly.
- **Evidence.** The file-read descriptor at WRAM-H `0x0603E8E9` holds the
  declared length + 8. The reset follows a threaded-interpreter jump to 0.
- **Fix.** `tools/disc/pac_patch.py` now always declares the original compressed
  length when the new stream is shorter.
- **Reproduce.** See `research/experiments/EXP-0036/README.md`; the tool is
  `tools/mednafen/replay_state.py`.

## EXP-0036: The 17-Character Roster Image Works Live

Confidence: **CONFIRMED**

Experiment: `EXP-0036` run 2 (task `RE-046`)

- **Finding.** On `build/re046_roster` (track 01 `351254c4…`), Cyclops (`MC01`),
  Zangief (`MC0D`), Captain America (`MC02`), and Dhalsim (`MC0C`) each read their
  own compiled table at the predicted base. All 16 records of each display the
  paired official English.
- **Evidence.** One KO per character, then 64 forced records from post-KO
  checkpoints. All 68 captures pass `verify_records.py`: pointer, screen, cart
  font, WRAM-L table, and display buffer. All screenshots were read.
- **Scope.** Marvel and Capcom fighters, both team slots, one-line records,
  dropped placeholders, and files with untouched extra blocks.
- **Reproduce.** `research/experiments/EXP-0036/README.md`, Reproduction.

## EXP-0036: A Second Win-Quote State

Confidence: **CONFIRMED** (layout and use; what selects it is unknown)

Experiment: `EXP-0036` run 2

- **Finding.** The quote pointer routine runs with `r12` = `0x060F9E16` (`RE-023`)
  or `0x060F9ED6`. Each state holds the table base at `r12 + 0x34` and the index
  word at `r12 + 0x50`, so the second uses `0x060F9F0A` and `0x060F9F26`.
- **Evidence.** In three KOs the first state held `0x0607FD0C` / 0, while the
  second held the predicted base and an index that gives the stored pointer.
  Forcing `0x060F9F26` after setter `060AF282` moved the pointer as predicted, and
  48 forced records verified through it.
- **Use.** `ko_capture.py --quote-state` and `verify_records.py` handle both.

## END-002: Ryu's Ending Text Is VDP1 Sprites of Quote-Font Glyphs

Confidence: **CONFIRMED** (dialogue box 1 and ending page 1 of Ryu's run; box 2
through the routine log)

Experiment: `EXP-0038`

- **Finding.** The post-boss dialogue and the ending-page text are drawn by VDP1
  normal sprites (16 × 16, 4 bpp, color mode 0), one per cell, on a
  19-cell × 2-line grid at x = 26 + 16k.
  - Dialogue: color word `0x6030`, VDP1 y 14/30.
  - Page: color word `0x61F0`, y 178/194.
  - Screenshot row = VDP1 y + 8.
- **Glyphs.** Each glyph cell is a byte-exact quote-font cell. All 40 glyph cells
  matched one code each (font base `0x0278CF60`, the pointer at `0x0601D8E4`).
- **Build path.** The `FONT-001` routine at `0x0601CE00` builds each glyph, with
  its code in R3, the VDP1 destination in R9, and caller return `0x0601CDE2`.
  Glyphs pass through the staging cell `0x0601CEEC`. Each distinct glyph is
  uploaded once per screen.
- **Evidence.** Zeroing one VDP1 cell removed exactly that glyph:
  - box 1, line 2 cell 6: 69 px, the same after 2 and after 60 frames;
  - page 1, line 1 first glyph: 150 px;
  - nothing else in either box changed (no-write controls).
- **Codes.** They follow the known scheme: hiragana `0x0800+n`, katakana in
  Shift-JIS order, ・ `0x08AE`, 、 `0x08A9`, 。 `0x08AA`.
- **Limits.**
  - Where the codes come from, the disc source, and line capacity are unknown.
  - Pages 2-3 and boxes 3-4 were not inspected.
  - The cart-RAM extraction is still unvalidated outside the matched glyph
    bytes.
- **Reproduce.** `research/experiments/EXP-0038/README.md`, Procedure.

## END-003: Ryu's Ending Dialogue Is a Live Code Table with a Name Placeholder

Confidence: **CONFIRMED** (boxes 1-2 and the placeholder); boxes 3-4 and the
pages are located but not live-tested

Experiment: `EXP-0039`

- **Finding.** The post-boss dialogue is read live from WRAM-L records of 38
  big-endian 16-bit quote-font codes (2 lines × 19 cells, 76 bytes), padded
  with `0x0020`, with line positions explicit in the record.
  - Ryu/Gouki box 1 is at `0x0022AE14` and box 2 at `0x0022AE60`.
  - Boxes 3-4 (`0x0022B9F4`, `0x0022BA40`) and the three ending pages
    (`0x00233664` + `0x4C`·k) were located with all 13 line positions matching
    the screen.
- **Name placeholder.** Code `0x0000` inserts a character name from a WRAM-H
  name table (32-byte entries; Ryu's codes are at `0x06095FE4`).
- **Load time.** The tables load with the final stage (`STAGE-08`) and are
  identical through the ending.
- **Evidence.** Single writes into `ryu_gouki_post_boss_ko.mcs`, before the
  scene, each against a no-write control:
  - box 2 cell 1 `0970` → `08F9`: only that cell changed, showing R;
  - box 1's `0x0000` → `08F9`: R then ・・・ with no name;
  - Ryu's name entry → R Y U: box 1 showed RYU.
- **Limits.**
  - What selects the records, and which name fills a placeholder, are unknown.
  - The table bases may move with team or load order.
  - The disc source is unknown.
- **Reproduce.** `research/experiments/EXP-0039/README.md`, Procedure.

## END-004: Disc Sources of Ryu's Ending Text (`MC13.PAC` and `ME.PAC`)

Confidence: **CONFIRMED** (the text records); the relocation account of the
non-text differences is `SUPPORTED`

Experiment: `EXP-0040`

- **Post-boss dialogue.** Comes from `MC13.PAC;1` (LSN 11,100, 31,036 bytes,
  `05263ab6…0b00`), the final boss's (slot 19) quote file.
  - The in-game LZSS decompressor (PC `0603E446`, `DISC-001` format) decodes
    it to WRAM-L `0x00220000` at the `STAGE-08` transition.
  - The decode (61,042 bytes, `9eb9b7c6…be2a`) holds the four Ryu/Gouki records
    at `0xAE14`, `0xAE60`, `0xB9F4`, and `0xBA40`, byte-identical to RAM.
- **Ending pages.** Come from `ME.PAC;1` (LSN 3,924, 60,692 bytes,
  `77210963…8b8d`), copied raw from file offset `0x10` to WRAM-L `0x00230000`
  (writer PC `0603E04E`).
  - Ryu's three page records are at file offsets `0x3674`, `0x36C0`, and
    `0x370C`, identical to RAM in every state checked.
- **Evidence.** Write breakpoints replayed from `before_stage08_load.mcs` (no
  input) caught both writers.
  - Their loader contexts carry each file's header word 1: `0x8000792B` and
    `0x0000ED02`.
  - The remaining RAM/file differences are pointer fields, where RAM = file +
    base + `0x40`, apart from 30 unexplained non-text longwords in the
    `ME.PAC` region.
- **Limits.**
  - The record indexing in both files is unmapped.
  - Whether edited files load and display is untested (`END-007`).
- **Reproduce.** `research/experiments/EXP-0040/README.md`, Procedure.

## END-007: Edited Ending Files Load and Display from a Derived Image

Confidence: **CONFIRMED** (disc to RAM for both files; on screen live for the
`ME.PAC` page marker)

Experiment: `EXP-0041`

- **Finding.** Two kinds of edit build from the untouched source with
  `patch_image`:
  - a same-size raw edit of `ME.PAC` (file offset `0x367E`, `09AD` → `08F9`);
  - a full LZSS re-encode of `MC13.PAC` (decoded `0xAE62`, `0970` → `08F9`),
    keeping the declared length `0x7923` and zero-filling to 31,036 bytes.
- **Load.** Each image loads the edited file at the `STAGE-08` transition.
  Replayed from `before_stage08_load.mcs` for 600 frames, the loaded regions
  (`0x00220000-0x0022EE71`, `0x00230000-0x0023ED03`) equal the untouched
  image's, except the marker word. The same holds for both edits together.
- **Display.** The marker word displays as R in exactly its cell: page 1
  (145 px) here, box 2 in `EXP-0039`.
- **No re-read.** Neither file is re-read between the KO and the ending.
- **Track 01 hashes:** A `f2f8f673…`, B `d525e356…`, C (both) `276bd6c7…`.
- **Live (Part 2).** Image C from `before_stage08_load.mcs`, with Ryu beating
  Mech-Gouki (team Ryu/Ken). Page 1 showed R in exactly the marker cell:
  - 145 px vs the untouched run, byte-identical to the RAM-trial screenshot;
  - pages 2-3 unchanged.
- **Limits.**
  - The `MC13` marker was seen in RAM only, because Ryu/Ken shows other boxes
    1-2.
  - The splice re-encode does not fit `MC13`'s 1 byte of slack; use `--full`.
- **Reproduce.** `research/experiments/EXP-0041/README.md`, Procedure.

## END-006: Arcade Reference for Ryu's Ending

Confidence: **CONFIRMED** (records, screens); the English partner-line indexing
is `SUPPORTED`

Experiment: `EXP-0042`

- **Japanese records.** The Saturn's Ryu ending pages and Ryu/Gouki dialogue
  records are byte-identical in `mshvsf`, `mshvsfu`, and `mshvsfj`.
  - Pages: Japanese table `0x20C14C`, slot 9 → `0x2153CC`.
  - Dialogue: block `0x217BE0` = Saturn `MC13` records 16-119.
- **English pages.** Official English exists for Ryu's three ending pages:
  table `0x20C1B4`, slot 9 → `0x21F580`, 2 × 25 cells. They were seen on
  screen in `mshvsfu` and `mshvsf`.
- **English dialogue.** It does not translate the Japanese four-box dialogue.
  It shows two generic lines from the 52-record partner table at `0x22226C`,
  each naming the other character with `0x0000`.
  - Ryu/Ken: records 10 and 35.
  - Ryu/Akuma: records 15 and 35. This was predicted, then seen.
- **No-play route.** The arcade stage word `0xFF4880` and the boss vitality
  `0xFF3E50`/`0xFF4844` are at the Saturn's WRAM-H offsets (`0x060F` →
  `0xFF`). Forcing them reaches any ending in MAME with no play.
- **Limits.** Only Ryu, with Ken and Gouki, was observed. The indexing code is
  not traced.
- **Reproduce.** `research/experiments/EXP-0042/README.md`, Procedure.

## END-005: What Selects the Post-Boss Dialogue and the Ending

Confidence: **CONFIRMED** (point and partner roles); the KO character's effect is
untested

Experiment: `EXP-0043`

- **Pages.** The ending pages follow the point character.
  - On the untouched Saturn image, Ryu + Ken (only the partner changed from
    `EXP-0037`) showed Ryu's three pages, byte-identical screenshots included.
  - A Gouki-point arcade run showed Gouki's ending.
- **Dialogue.** `MC13`'s 120-record table is 16 Cyber-Akuma win quotes plus 52
  two-record entries:
  - boxes 1-2 are records 16 + 2 × (partner slot), spoken by the partner;
  - boxes 3-4 are records 16 + 2 × (26 + point slot), spoken by the point;
  - in each, `0x0000` names the other character.
  - Ryu's own pair (records 86-87) is shared by every partner.
- **English.** The partner lines (`EXP-0042`) use the same indices, one record
  each.
- **Evidence.**
  - Saturn: Ryu + Ken boxes are records 36-37 and 86-87.
  - Predicted and met in MAME (`mshvsfj`, `mshvsfu`):
    - Ryu + Chun-Li: records 38-39 and 86-87; English 11 and 35.
    - Gouki + Captain America: records 20-21 and 98-99; English 2 and 41.
- **Limits.** The KO character was not varied. Records 54/55 and 106/107
  (Cyber-Akuma's pairs) do not match the arcade block.
- **Reproduce.** `research/experiments/EXP-0043/README.md`, Procedure.

## END-010: Ryu's Ending in Official English (M7)

Confidence: **CONFIRMED**

Experiment: `EXP-0044`

- **Finding.** A deterministic image built from the untouched source (track 01
  `b481a4c6…`, reference `end010`) shows Ryu's ending in official arcade
  English on a cold boot:
  - the three pages (`ME.PAC`);
  - the partner and point lines, split at their line breaks across each
    two-box pair (`MC13` records 36-37, 46-47, 86-87);
  - RYU, KEN, and AKUMA as names.

  It was verified live with Ken and with Gouki as partner.
- **Mechanisms confirmed on the way:**
  - A blank dialogue record is shown as an empty box, not skipped.
  - `0x0000` inserts the name at any cell, shifting the rest right.
  - The name table is `MM.BIN` `0x7D3C0` + 32·slot (two leading blank cells),
    and the name-length table is `MM.BIN` `0x96DE8` + slot (cells inserted per
    name). `MM.BIN` is loaded raw at WRAM-H `0x06018B00` at boot.
  - The quote font is loaded into cart RAM after boot and stays resident; it is
    not reloaded at stage 8.
- **Pitfall.** Replaying a state on a font-changed image shows empty glyphs.
  Live checks of font changes need a cold boot.
- **Tools.**
  - `tools/text/official_endings.py` (spec);
  - `caption_compiler.py` schema v3 (raw files, fields, patches, placeholders
    anywhere);
  - `tools/mednafen/ending_driver.py` (forced stage 8 and boss KO on the
    Saturn).
- **Limits.** Only the Ken and Gouki partner lines are localized. The English
  names also replace names inserted in other Japanese text in this image.
- **Reproduce.** `research/experiments/EXP-0044/README.md`, Procedure.

## EXP-0045: Identical Records in a Dialogue Pair Show as One Block

Confidence: **CONFIRMED**

Experiment: `EXP-0045`

- **Finding.** When both records of a post-boss dialogue pair hold identical
  text, nothing on screen changes at the hand-over. The whole frame is
  byte-identical across it, so the pair reads as one block lasting both boxes'
  time (about 480 frames). With different text, the box switches in one frame
  with no blank frame.
- **Use.** `official_endings.py --dialogue-layout whole` (the default) shows
  each English line whole, one block per speaker. This is the `end010`
  reference (track 01 `ba3fb3ce…`).
- **Reproduce.** `research/experiments/EXP-0045/README.md`.

## END-022: Name Insertion Follows the Length Table, and Names Can Grow

Confidence: **CONFIRMED**

Experiment: `EXP-0047`

- **Finding.** A `0x0000` placeholder inserts exactly as many cells as the
  `MM.BIN` name-length table gives for that slot (WRAM-H `0x060AF8E8` + slot).
  - Ken's entry grown to four cells, with length 4, showed "ＡＢＣＤ、".
  - The same entry with length 2 showed "ＡＢ、".
  - Only the placeholder's own line shifts.
- **Census.** `data/text/placeholder_census.json` lists 100 placeholders.
  - A roster image makes 69 English and leaves 31 in Japanese text.
  - All but one of those 31 belong to excluded characters.
  - The exception is one line in a Japanese-only `MM.BIN` table (`0x7CD90`;
    `TXT-001`).
- **Reproduce.** `research/experiments/EXP-0047/README.md`.

## END-023: Combined Roster Image (Win Quotes and All Roster Endings), Offline

Confidence: **CONFIRMED** (offline build; live sample in `END-024`)

Experiment: `EXP-0048`

- **Finding.** `official_endings.py --roster data/text/m5_roster.json
  --with-win-quotes` and `caption_compiler.py` build one deterministic image
  from the untouched source (track 01 `c06cf0ef…`, reference `m8_roster`). It
  holds:
  - the 17 M5 win-quote tables: PAC files byte-identical to the verified
    roster image;
  - the 17 roster endings in official English: 75 pages, and all roster
    partner and point pairs in the `whole` layout;
  - the roster's English names and name lengths.
- **Font:** 501 pair glyphs, reusing 253 of 321 candidate kanji codes.
- **Reproduce.** `research/experiments/EXP-0048/README.md`.

## END-024: Combined Roster Endings Verified Live

Confidence: **CONFIRMED** (six sampled endings and a win quote)

Experiment: `EXP-0049`

- **Finding.** From one cold boot of the combined image (`c06cf0ef…`), five
  roster endings showed the arcade English partner lines with correct English
  names, then their official English pages:
  - Captain America + Ryu;
  - Zangief + Spider-Man;
  - Bison + Hulk;
  - Sakura + Wolverine;
  - Dan + Chun-Li.
- **Names.** CAPTAIN AMERICA (8 cells) and BISON (grown from 2 to 3 cells) were
  inserted correctly.
- **VEGA image** (user decision; track 01 `e721a167…`, reference
  `m8_roster`): from a cold boot, Vega's stage-1 win quote showed the official
  English, and Vega + Ryu's ending showed "VEGA, / you are a great fighter.",
  "Our game is at its end, / RYU.", and Vega's three English pages. So the M5
  win quotes still work in the combined image.
- **Dan's last page** is empty in the official English (the Japanese shows 完).
  The build matches the arcade.
- **Limit.** The ending driver's KO offsets (`0x060F3E50`/`0x060F4844`) hold
  vitality only in the one-character boss fight, not in ordinary
  two-against-two fights.
- **Reproduce.** `research/experiments/EXP-0049/README.md`.

## END-026: The Saturn's Names in the English Text

Confidence: **CONFIRMED** (the mechanism and the live result; the naming policy
itself is provisional, `LOC-001`)

Experiment: `EXP-0050`

- **Finding.** `TEXT_OVERRIDES` ("Cyber Akuma" → "Mech-Gouki", then "Akuma"
  → "Gouki") and `NAME_OVERRIDES` (14: VEGA, 15: GOUKI) in
  `tools/text/official_endings.py` change exactly the roster lines that name
  these characters:
  - two name entries;
  - Gouki's win quote;
  - pages of Wolverine's, Vega's, Gouki's, and Dan's endings.
- **Build and live result.** The image is `2a5b26b7…` (reference `m8_roster`).
  From a cold boot it showed "GOUKI, / you are a great fighter.", Gouki's
  pages with "Gouki", and Vega's page with "Mech-Gouki".
- **The Saturn's own art.** The VS screen labels the characters "GOUKI" and
  "MECH-GOUKI" (frames `0268cc2d…`, `14d5ba76…`).
- **Side effect.** Centring shifts are chosen over a whole quote set, so a text
  change can move unrelated lines by half a character. That is harmless; the
  renders were read.
- **Reproduce.** `research/experiments/EXP-0050/README.md`.

## END-025: Ending Coverage of the Roster Image

Confidence: **CONFIRMED**

Experiment: none (a scripted census and comparison, `tools/text/ending_coverage.py`)

- **Finding.** In the arcade page tables:
  - slot 0 (Apocalypse) shares slot 1's (Cyclops) pages in both the Japanese
    and English tables;
  - slot 19 shares slot 18's (Dan) Japanese pages;
  - the US arcade's English slot 17 (Norimaro) points to Dan's English;
  - English slots 19-25 point to one block.

  The Saturn `ME.PAC` records equal the arcade Japanese ones for every slot
  with a known extent.
- **Untouched exclusions.** Against the `m8_roster` image (`2a5b26b7…`),
  every byte outside the roster's targets is unchanged in `ME.PAC`, the
  decoded `MC13`, and `MM.BIN`.
- **Register.** `docs/coverage_exceptions.md` (Endings); data in
  `data/text/ending_coverage.json`.
- **Reproduce.**

  ```bash
  ./invenv.sh python -m tools.text.ending_coverage --driver local/mame_src/cps2.cpp \
    --archive local/arcade_roms/mshvsf/mshvsfu.zip \
    --built-track "build/end027/image_a/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
    --out data/text/ending_coverage.json
  ```

## FONT-010: The Staff-Credits Font Is Part of the Quote Font

Confidence: **CONFIRMED**

Experiment: `EXP-0051`

- **Finding.** The staff credits draw quote-font codes `0x1E0`-`0x25F`
  (`MEMFIX.PAC` entry 4, compressed): `A`-`Z` at `0x210`-`0x229`, `a`-`z` at
  `0x231`-`0x24A`, digits at `0x200`-`0x209`, and punctuation around them.
  - They use the same glyph routine as captions (`0x0601CE00`). Each glyph is
    built in `0x0601CEEC` and copied to VDP1 VRAM by SCU DMA (`0x0601BABC`:
    R9 = source, R10 = destination, R11 = count).
  - Cells are 16 × 16 4 bpp, one letter per cell: values 1-9 are a gradient,
    `B` the outline.
  - Credits palette: `1` (240,240,0) to `9` (240,112,0), and `B` (32,0,96).
- **Evidence.** 121 of 121 glyph sprites on a credits screen equal quote-font
  glyphs (`tools/memory/vdp1_commands.py --font`). A replayed screenshot
  equals the recorded frame (`6fc4e105…`).
- **Side finding.** `TESTFIX.DAT` holds an 8 × 8 ASCII font (VDP2 VRAM `0x400`
  during the credits) and a partial 16 × 16 set of the same art. The credits
  do not draw from it.
- **Reproduce.** `research/experiments/EXP-0051/README.md`.

## FONT-011: Caption Palettes, Credits-Style Pairs, and Gold Captions

Confidence: **CONFIRMED** (silver and gold, live; palettes; capacity)

Experiment: `EXP-0052`

- **Palettes.**
  - CRAM is kept in two WRAM-H copies (`0x060C7C24`, `0x060C8C24`) and copied
    to CRAM each frame by SCU DMA. A sprite's `colr & 0x7FF` is its CRAM
    index.
  - Captions use banks `0x1E0` (win quote), `0x030` (dialogue), and `0x1F0`
    (pages). All hold the credits layout in grey: 1-9 run from white to
    (112,112,112), `B` is (16,16,0), `F` is black.
  - Bank `0x010` holds the credits' gold on every screen checked.
- **Colour word.** `colr = (attr & 0x7000) | ((attr & 0x1F) << 4)` (writer
  `0x0601CB72`). The request list at `0x060EDA20` carries caption palette
  numbers `0x1E`, `0x03`, and `0x1F`.
- **Silver build.** `glyph_style: credits` (two shading bands, 4-connected
  outline, hand-drawn `I`/`M`/`W`/`m`/`w`/`!`/`'`/`‼`) fits the font and
  displays live: `build/font011`, `9246148f…`, reference
  `m8_roster_credits`.
- **Gold captions.** The message-window initialiser in `MM.BIN` stores each
  caption kind's palette byte (object +72, which the emitter `0x06073354`
  reads, low five bits) as an immediate:
  - win quote `0x961E3` = `0x9E`;
  - ending page `0x961FB` = `0x9F`;
  - post-boss dialogue `0x96233` = `0x83`;
  - Apocalypse's pre-fight boxes `0x9621D` = `0x96` (`EXP-0082`; RAM trial,
    then seen gold in a cold-boot run of the build).

  Setting each to `0x81` selects gold bank 1. Verified live on `3a6c485c…`
  (reference `m8_roster_gold`).
- **Reproduce.** `research/experiments/EXP-0052/README.md`.

## UI-001/UI-002: English UI Labels from the Game's Own Art

Confidence: **CONFIRMED** (EASY live; JOIN IN by replay with a transplanted
font)

Experiment: `EXP-0053`

- **Finding.** The player-2 prompt and the mode panel are quote-font UI art
  cells:
  - "対戦者求む!" is `0x45B`-`0x45F`;
  - "簡単操作" has four shading copies (`0x424`, `0x428`, `0x42C`, `0x43A`;
    four cells each), matching "EASY" copies `0x6A6`, `0x6A8`, `0x6AA`,
    `0x6AC`.

  The font also holds the arcade's English UI art: "JOIN IN" (`0x496`-
  `0x499`), "INSERT COIN", "GAME OVER", and life-bar names in both
  conventions (VEGA/BISON, GOUKI/AKUMA, MECH-GOUKI/CYBER-AKUMA).
- **Fix.** `--ui-english` adds `glyph_copies` (verified by the compiler):
  "JOIN IN" replaces the prompt, and EASY replaces each "簡単操作" copy.
- **Side finding.** In a recorded state, cart RAM `0x0278CF60`-`+0x32740` (the
  quote font) equals the built font byte for byte. That validates
  `mcs_extract`'s cart-RAM extraction for this region.
- **Reproduce.** `research/experiments/EXP-0053/README.md`.

## LOC-005: Sound Banks and Their ADPCM Decoder

Confidence: **CONFIRMED** (the decoder reproduces the game's channel state;
the bank layout fits every bank payload exactly)

Experiments: `EXP-0055`, `EXP-0056`

- **Container.** A `.PAC` file of this kind starts with (u32 flag, u32 size)
  pairs ended by (0, 0). The payloads follow back to back. A flag of
  `0xFFFFFFFF` means the entry has no payload. LZSS-compressed PACs use a
  different header.
- **Bank.** A payload holds:
  - a u32 clip count;
  - one (u16 tag, u16 length) entry per clip. The clip ID is `tag & 0x3FF`;
    `tag >> 10` is a flag field that is not interpreted;
  - the clip data, concatenated in table order.

  Count, table and lengths add up to the payload size exactly in all 28 banks
  found:
  - `CMNSE.PAC` payload 0 (88 clips);
  - `SEL.PAC` payload 1 = `SEL2.PAC` payload 0 (66 clips);
  - `MEMFIX.PAC` payloads 8 and 9;
  - payload 1 or 2 of each `PLxx.PAC`.
- **Decoder.** The SH-2 mixer decodes the clips at `0x0600D420`, high nibble
  first. It is not IMA, OKI or Yamaha:
  - `d = step * (n & 7) >> 2`;
  - `pred ± d`, with no clamp;
  - `step = step * MUL[n & 7] >> 16`, clamped to `0x80`-`0x6000`, where `MUL`
    (16.16, at `0x0600D46C`) is 0.9, 0.9, 0.9, 0.9, 1.2, 1.6, 2.0, 2.4;
  - a clip starts at predictor 0 and step `0x80`.
- **Mixer.**
  - 16 channels with 44-byte records, from the pointer at `0x06012B6C`.
  - The active mask is at `0x060132D4`.
  - Each sample is doubled into rings that play at 24,031 Hz, so clips play
    at 12,015.5 Hz.
- **Name calls** (`EXP-0057`: mixer log plus user listening to single
  clips).
  - `PL0E` bank #18 (`0x286`, also select-bank #48) says "Vega". The game
    plays it on the win screen, 116 frames after the banner.
  - The same bank's #1 (`0x04F`, also select-bank #4) says "Bison". It was
    not seen played.
  - `PL0F` bank #1 (`0x048`, select-bank #3) says "Gouki"; bank #23
    (`0x338`, select #62) says "Akuma".
  - `PL13` (Mech-Gouki) bank #2 (`0x082`, select #12) says "Mech Gouki"; #1
    (`0x05B`, select #7) says "Cyber Akuma".
  - So the disc holds both naming conventions for all three characters.
  - The character-select voices are `0x133` (Vega) and `0x1D1` (Gouki). They
    are the characters' own voices, not names.
- **Name-call table** (`EXP-0058`).
  - `MEMFIX.PAC` payload 7 (file `0x123BB8`) is loaded as-is into sound RAM
    at `0x6510`.
  - It holds table A: 23 ten-byte records at sound RAM `0x73B6` (file
    `0x124A5E`), indexed by character, whose first word is the sound ID.
  - Indexes 14, 15 and 19 hold "Vega" `0x286`, "Gouki" `0x048` and "Mech
    Gouki" `0x082`. Indexes 20-22 hold the US calls `0x04F`, `0x338` and
    `0x05B`.
  - Setting entry 14 to `0x04F` (sound RAM `0x7442`) makes the win screen
    play "Bison" on the same frame, with nothing else changed.
  - A parallel 16-byte table B (`0x74AC`, file `0x124B54`) holds the same IDs.
    It did not affect the win call; its use is unknown.
- **Evidence.** Replaying each active channel from its start reproduces the
  stored predictor and step exactly: 24 of 24 active channels in 38 states of
  the `END-024` recording. Every mismatch (73 of 575 records) is an inactive,
  stale record.
- **Reproduce.**

  ```bash
  ./invenv.sh python -m tools.audio.channel_check <state>
  ./invenv.sh python -m tools.audio.sound_bank --file '*'
  ```

  The second command exports every bank to WAV under `local/audio/`.
  Details are in `research/experiments/EXP-0055/README.md` and
  `EXP-0056/README.md`.

## LOC-003: Two Name Variants from One Switch

Confidence: **CONFIRMED** (deterministic builds; the cold-boot table read)

Experiment: `EXP-0059`

- **Switch.** `official_endings --names saturn|us`.
  - `saturn` (the default) reproduces the `m8_roster_gold` spec byte for
    byte.
  - `us` drops the Vega/Gouki name and text overrides and adds six
    `MEMFIX.PAC` name-call edits (`US_VOICE_PATCHES`, `EXP-0058`), each
    checked against the original bytes.
- **Builds.** Reference `m8_roster_gold_us`: track 01 `e1337dbf…`, release
  patch `82208a8c…` (155,248 bytes). All 9 references pass from the
  untouched source.
- **Live check.** After a cold boot, the US image's sound RAM name-call tables
  hold `0x004F`, `0x0338` and `0x005B` at entries 14, 15 and 19. The Saturn
  image holds `0x0286`, `0x0048` and `0x0082`.
- **Not yet:**
  - the name art (`LOC-004`) is unchanged;
  - the US calls have not been heard in play beyond `EXP-0058`'s replay.
- **Reproduce.** `research/experiments/EXP-0059/README.md`.

## LOC-004: US Life-Bar Names and Speaker Labels

Confidence: **CONFIRMED** (replays; AKUMA from the glyph cache and an offline
render)

Experiment: `EXP-0060`

- **Life bars.**
  - The fight HUD draws bold quote-font cells: VEGA `0x760`-`0x762`, GOUKI
    `0x750`-`0x752`, MECH-GOUKI `0x568`-`0x56D`.
  - The US variant copies the font's own BISON `0x763`-`0x765`, AKUMA
    `0x753`-`0x755` and CYBER-AKUMA `0x5D9`-`0x5DE` over them. BISON and
    CYBER-AKUMA were seen in a replay.
  - AKUMA is 50 px wide and GOUKI's sprite 48 px, so 2 px are clipped.
- **Speaker labels.**
  - `ME.PAC` `0xB164` fields 14, 15 and 19 become "Bison", "Akuma" and
    "Cyber Akuma".
  - The table's RAM copy (WRAM-L `0x0023B234`) drives the label, which is
    drawn when the page opens. Writing "Bison" before the page showed
    "Bison".
- **Not used anywhere seen:** the italic label set and the first MECH-GOUKI
  copy `0x562`-`0x567`. The VS-screen names are a sprite mosaic.
- **Reproduce.** `research/experiments/EXP-0060/README.md`.

## LOC-004: US Names in the Sound Test and Menu

Confidence: **CONFIRMED** (cold-boot RAM and pointers; not seen on screen)

Experiment: `EXP-0061`

- `MM.BIN` loads at `0x06018B00`. The US variant changes three same-length
  ASCII strings:
  - `0x6341` "18.VEGA" → "18.BISON";
  - `0x639D` "22.GOUKI" → "22.AKUMA" (20-character fields);
  - `0x24F03` " MECH-GOUKI NOW!!" → "CYBER-AKUMA NOW!!".
- The menu lists point at `0x0603DA03`, the slot start.
- `ME.PAC` is `ME.SHX` in a 16-byte container header. The payload loads at
  WRAM-L `0x230000`.
- **Reproduce.** `research/experiments/EXP-0061/README.md`.

## LOC-004: The Win-Banner Name Records

Confidence: **CONFIRMED** (replay and cold-boot RAM)

Experiment: `EXP-0062`

- **Sprites.**
  - The banner letters are sprite patterns `0x5000 + code`. The code is a
    2×2 large letter in the quote font, top-left at `0x2E0 + 2 * (i % 8) +
    0x20 * (i // 8)`, with `i = ASCII - 63` (A = `0x2E4`).
  - They are drawn by the generic sprite emitter `0x0601C9C4`, not the glyph
    cache.
- **Records.**
  - Each name is a record in `MM.BIN`: `0002 000A n`, a u32 spacing-table
    pointer, then n+1 (pattern, `1100`) pairs stored right to left.
  - Records exist for every character, plus SHADOW, U.S.AGENT, MEPHISTO,
    BISON, AKUMA, CYBER-AKUMA and CHARLIE.
- **Pointers.**
  - The record pointer for character index i is at `MM.BIN` `0x9FBF8 + 12i`.
    VEGA (14) is at `0x9FCA0`, GOUKI (15) at `0x9FCAC`, MECH-GOUKI (19) at
    `0x9FCDC`. BISON, AKUMA and CYBER-AKUMA are entries 23-25.
  - Pointing entry 14 at BISON (`0x060B8BCE`) made the banner read BISON /
    RYU / WIN.
- **Loading.** That part of `MM.BIN` loads at about frame 1800 after a cold
  boot (`0x060B87A0` = load `0x06018B00` + `0x9FCA0`).
- **Reproduce.** `research/experiments/EXP-0062/README.md`.

## LOC-004: The VS-Screen Name Records

Confidence: **CONFIRMED** (replay and cold-boot RAM)

Experiment: `EXP-0063`

- **Font.** The VS-screen names are letter sprites from the staff-credits font
  (patterns `0x5000 + code`; A = `0x210`, hyphen `0x20F`), at an 11 px pitch.
  They are not `SEL*.PAC` art, as `EXP-0054` had supposed.
- **Records.**
  - Each name is an `MM.BIN` record: u16 0, u16 n, u16 0, a u32 spacing
    pointer, then n patterns, right to left.
  - The record pointer for character index i is at `MM.BIN`
    `0x66536 + 12i`. VEGA (14) is at `0x665DE`, GOUKI (15) at `0x665EA`,
    MECH-GOUKI (19) at `0x6661A`.
  - BISON, AKUMA and CYBER-AKUMA records exist as entries 23-25, as in the
    banner table.
- **Trial.** Pointing Vega's entry at BISON (RAM `0x0607F0DE` =
  `0x0607F3B2`) before the VS screen made it read BISON. The control reads
  VEGA.
- **Reproduce.** `research/experiments/EXP-0063/README.md`.

## LOC-004/LOC-005: The American-Name Build in Play

Confidence: **CONFIRMED** (a cold boot, user play, a live mixer log and
screenshots)

Experiment: `EXP-0064`

- With Gouki and Vega, the US build calls "Akuma" (`0x338`) and "Bison"
  (`0x04F`) at character select, and "Akuma" on the win screen. No Japanese
  name call was started.
- Character select (BISON), the VS screen (BISON / AKUMA vs CYBER-AKUMA), the
  life bars (AKUMA vs CYBER-AKUMA), the win banner (AKUMA / BISON / WIN) and
  the post-boss dialogue (BISON) all show the US names.
- **Reproduce.** `research/experiments/EXP-0064/README.md`.

## LOC-004: Life-Bar Label Records (Both Player Sides)

Confidence: **CONFIRMED** (replay trials, cold-boot RAM)

Experiment: `EXP-0065`; supersedes the glyph-copy method of `EXP-0060`.

- **Records.** The life-bar name labels are `MM.BIN` records of 8 sprite
  patterns (`0x5000` + quote-font code; `0x5020` is blank), indexed by
  character:
  - player 1 at `0x32CA4 + 16i` (bold, left-aligned);
  - player 2 at `0x32E74 + 16i` (italic, right-aligned).
- **US records.** Entries 26 (AKUMA, 4 cells `0x753`-`0x756`), 27 (BISON) and
  28 (CYBER-AKUMA) are already on the disc. Copying them over 15, 14 and 19
  shows the US labels at full width on both sides.
- **Reproduce.** `research/experiments/EXP-0065/README.md`.

- **Seen in play** (`EXP-0074`): from a cold boot of the release image, a
  Gouki-vs-Gouki fight shows full-width AKUMA on player 1's bar (2 px wider
  than the earlier clipped label) and the italic AKUMA on player 2's.

## UI-003: Attract-Mode Teaser Captions

Confidence: **CONFIRMED** (cold-boot capture, write breakpoints, exact data
match)

Experiment: `EXP-0066`

- **Captions.** Each attract cycle (about 3,146 frames) shows four Japanese
  captions on black:
  - ヴァリアブル / ヒーロー / バトル;
  - 広がれ!! / ヒーロー / ワールド;
  - 第2弾!!;
  - 解き放て! / 友情パワー.

  There is also a Norimaro screen with Japanese brush lettering.
- **Rendering.** The captions are 4bpp VDP2 cell tiles (VRAM `0x6000`+), not
  VDP1 sprites or movie frames. They are DMA'd from WRAM-H `0x06086020`,
  where an LZ decompressor (`0x06021F0C`) writes them.
- **Source.** The compressed stream is in each of `MVSOP0`-`MVSOP7.ST2`
  (`MVSOP0` at `0x500EB`).
- **Reproduce.** `research/experiments/EXP-0066/README.md`.

## UI-003: Attract Streams, Graphics LZ, and Caption Maps

Confidence: **CONFIRMED** (the decoder reproduces RAM; the pages render as on
screen)

Experiment: `EXP-0068`

- **`.ST2` container.**
  - Header sector: up to eight u32 section sizes. `MVSOP*` has A (map
    streams), B (events) and C (one graphics block).
  - Then 0x800-byte sectors. `MISS`-tagged ones carry 0x7FC bytes of a
    graphics stream; other sectors are interleaved.
  - Tool: `tools/disc/st2_stream.py`.
- **Graphics LZ** (`0x06021EDA`):
  - u32 compressed size, u32 size;
  - flags MSB first: 0 = literal; 1 = word `w`, copying `(w & 0xF) + 3` bytes
    from `(w >> 4) - 0x1000` back.
- **Caption layer.** NBG2 plane A page 0 (VRAM `0x70000`): 2x2-cell 4bpp
  characters, 2-word pattern names, colour offset 6. The vertical scroll
  selects ヴァリアブル… or 第2弾!! on the same page.
- **Map path.** Section A goes through a bit-flag LZ (`0x06022750`) into a
  ring at `0x06028020`, then a word LZ (`0x0602234C`) into the
  index/attribute arrays (`0x06037020`/`0x06039020`), then the macro-cell
  builder (`0x0601FD70`, 32x32 px per index) into `0x06050000`, then DMA.
- **Sources.** Captions 1-2 are in section C. Captions 3-4 are each in one
  stream block. Every one of the eight `MVSOP` files carries all four.
- **Reproduce.** `research/experiments/EXP-0068/README.md`.

## UI-003: English Attract Captions in the Existing Tiles

Confidence: **CONFIRMED** (offline round trips; cold-boot captures of the
built image against two baseline runs)

Experiment: `EXP-0071`

- **Palette command** (handler from `0x060221F8`): records of
  `[u16 index delta][u16 count][count words]`, the index running on from the
  previous record's end, until a `0xFF` byte; lines touched are marked dirty
  at `0x0603D048 + line`.
- **Colour words** are `0xFRGB`. The converter (`0x0601FFD8`) writes
  `table[word]` from a 64K-entry table at `0x06060000`: nibble n gives the
  5-bit level [0, 2, 4, 6, 8, 10, 12, 14, 17, 19, 21, 23, 25, 27, 29, 31],
  and the top nibble is a brightness. The banner colours (CRAM `0x11`-`0x1E`)
  convert exactly.
- **Caption palettes.** NBG2 lines 0x600 (grey) and 0x610 (red) are set by a
  full 0x800-word load (`0000 0800`) at the start of each caption scene.
  Each `MVSOP` script has five such ramp loads: the 1st, 3rd and 5th start
  the caption slots; the 2nd starts the Spider-Man scene, and the 4th starts
  the Akuma/Chun-Li scene, which fades the ramps into its lightning colours.
  Caption colour 1 is the background of every caption page.
- **Palette slots are shifted by one:** the converter writes array word k to
  CRAM slot k + 1 of the line, so caption colour c shows word c - 1.
- **Build route** (superseded for layout by `EXP-0073`, which builds new
  caption maps; the palette recolour below is still used).
  `tools/disc/attract_captions.py`, with the layout in
  `data/ui003/attract_captions.json`:
  - paints the win-banner letters into the caption characters (banner colour
    n → caption colour n + 1; shared characters must receive identical
    pixels);
  - sets words 1-14 of both lines in the three caption loads;
  - re-encodes section A and the caption blocks in place, keeping each
    stream block's header size;
  - section C may grow into its own zero padding.

  `official_endings --attract-captions` adds the result as expect-checked
  patches.
- **Oracles agree.** The US arcade (`EXP-0067`) and the PS1 US release
  (`EXP-0072`) show the same three captions in the colour set `F206`,
  `FFF0`-`FF80` and `F0CC`, which is the Saturn win-banner set the captions
  now use.
- **Reproduce.** `research/experiments/EXP-0071/README.md` and
  `research/experiments/EXP-0072/README.md`.

## UI-003: Attract Script Frames and Caption Macro Maps

Confidence: **CONFIRMED** (all eight scripts parse to their end; the static
replay reproduces the extracted caption pages; cold-boot capture)

Experiment: `EXP-0073`

- **Frame format** (`0x06021FE4`): a big-endian command word per frame (0 =
  idle, `0xFFFF` = end); bits 0-3 scroll deltas, 4 palette, 5-7 word-LZ map
  updates (`0x0602F020`, `0x06033020`, `0x06037020`), 8 object list, 9 deltas,
  10 a flag. Parser: `tools/disc/st2_stream.py` `script_frames`.
- **Caption pages** are 32x32 macro cells (`0x0601FD70`): index word k and
  attribute word 0x1000 + k of the NBG2 arrays; index i names characters
  `base + 16 * i` + 0/4/8/12; each half page is 16x8 cells, column by column.
- **Caption slots** (same frames in every file): slot 1 builds at frame 257
  (ヴァリアブル…, then 第2弾!! at 294) and clears at 315; slot 3 (解き放て!)
  734-753; slot 5 (広がれ!!) 1044-1063.
- **Macro origins differ per file** (slot 3 and slot 5); they are derived by
  matching caption macros against a save-state-verified file.
- **Result.** The arcade's three English captions, with its wording, line
  breaks and centring, built by `tools/disc/attract_captions.py`
  (`data/ui003/attract_captions.json`).
- **Reproduce.** `research/experiments/EXP-0073/README.md`.

## OPT-001: The Boss-Fight Unlock

Confidence: **CONFIRMED** (disassembly; controlled cold-boot RAM read; play)

Experiment: `EXP-0075`

- The title menu's Survival row switches to MECH-GOUKI NOW!! (menu index 5)
  with L/R. The menu code (`0x0603D644`) forces index 5 back to 3 while the
  word at `0x06017AB0` is 0.
- The word is cleared at boot (`MM.BIN` `0x0601DBE4`, `mov #0,r0`) and set to 1
  by `0x06098A1A` from saved data. Starting it at 1 (`E000` → `E001` at file
  offset `0x50E4`) unlocks the boss fight from a cold boot.
- Build option: `official_endings --unlock-boss-fight` (default on).
- **Reproduce.** `research/experiments/EXP-0075/README.md`.

## LOC-007: Secret-Character Names Match Across Releases

Confidence: **CONFIRMED** (static reads of the Saturn, both arcade sets and
the PS1 US)

Experiment: `EXP-0076`

- Saturn life-bar labels 20, 21 and 25 reuse ZANGIEF, SAKURA and SPIDER-MAN;
  the banner and VS tables hold no variant-specific name (name IDs 20-22:
  SHADOW, U.S.AGENT, MEPHISTO; 26: an unused CHARLIE banner).
- The US and Japanese arcade sets share one English name table (ZANGIEF,
  SAKURA, SHADOW, U.S.AGENT, MEPHISTO, SPIDER-MAN after CYBER-AKUMA) and the
  Saturn's ASCII speaker table ("Metal Zangief", "Sakura", "Shadow").
- The PS1 US game text matches; only its executable's ranking/menu lists say
  MECH-ZANGIEF, DARK SAKURA and ARMORED SPIDER-MAN.
- **Reproduce.** `research/experiments/EXP-0076/README.md`.

## SPECIAL-002: Norimaro's Win Quotes Have Official English

Confidence: **CONFIRMED** (static reads of the Saturn, three arcade sets and
the PS1 US)

Experiment: `EXP-0079`

- The Saturn's `MC11` table at `0xA158` is byte-identical to the arcade
  Japanese slot 17; record `k` pairs with English entry `k & 7`.
- The English block for slot 17 is its own (shared with no other slot) and
  identical in `mshvsfu`, `mshvsf` and `mshvsfj`, and on the PS1 US
  (`SELECT.BIN` `0x12E0C`). Records 1, 3, 9, 10 and 15 carry name
  placeholders.
- The arcade's English partner lines (`0x22226C`, records 17 and 43) cover
  slot 17. His ending pages (`ME.PAC` `0x3F5C`, 5 records) have no official
  English.
- **Reproduce.** `research/experiments/EXP-0079/README.md`.

## UI-004: The CONTINUE? Hints Are an MM.BIN Record Table

Confidence: **CONFIRMED** (VDP1 glyph match of a recorded state; disc and
arcade searches)

Experiment: `EXP-0080`

- The hint box under the CONTINUE? countdown is 38 VDP1 sprites (color word
  `0x6010`) of quote-font codes, read from a 16-record table at `MM.BIN`
  `0x7C584` (WRAM-H `0x06095084`; `MM.BIN` loads at `0x06018B00`). `MM.BIN`
  holds that address at `0x96890` and `0x96BAC`-`0x96BB4`.
- Joystick arrows are quote-font codes `0x01E2` ↑, `0x01E4` →, `0x01E5` ↘,
  `0x01E6` ↓, `0x01E7` ↙, `0x01E8` ← (inside the credits font).
- The arcade sets hold the same Japanese table (`0x2139AC`). Correction
  (`EXP-0085`): the arcade also holds official English hints, at `0x2239FC`
  (see TXT-001 below). The earlier "no English hints" search was wrong.
- **Reproduce.** `research/experiments/EXP-0080/README.md`.

## SPECIAL-004: The Bosses' Win Quotes Have Official English

Confidence: **CONFIRMED** (static pairing; seen in play in the US build)

Experiment: `EXP-0081`

- Apocalypse's 16 win-quote records are at `MC00.PAC` `0x3174` and
  Mech-Gouki's at `MC13.PAC` `0xA06C`. Each is byte-identical to arcade
  Japanese slot 0 (`0x20C2EC`) or slot 19 (`0x211D2C`) in `mshvsfu`, `mshvsf`
  and `mshvsfj`. Each slot has its own English block (`0x219E00`,
  `0x21D960`), with record `k` paired to entry `k & 7`.
- In play, each boss shows its English quote after it beats the player.
  Apocalypse is the stage-7 boss.
- **Reproduce.** `research/experiments/EXP-0081/README.md`.

## SPECIAL-004: Apocalypse's Pre-Fight Exchanges Have Official English

Confidence: **CONFIRMED** (byte identity with three arcade sets; seen in play
from a cold boot in both name variants)

Experiment: `EXP-0082`

- `MC00.PAC` `0x3634`-`0x4D5C` holds 26 roster slots × 3 boxes × 76 bytes:
  the challenger's line, Apocalypse's reply and his closing line, shown at the
  top of the screen before the stage-7 fight for the lead character's slot.
  The census tables `0x392E`, `0x3D7A` and `0x404E` were misaligned slices
  of it.
- The block equals arcade Japanese `0x2164B8` in `mshvsfu`, `mshvsf` and
  `mshvsfj`. The US arcade's English has the same layout from `0x2203F4`:
  100 bytes a box (two 25-code lines), 300 a slot.
- **Reproduce.** `research/experiments/EXP-0082/README.md`.

## REL-003: The Attract Streams Can Be Spliced in Place

Confidence: **CONFIRMED** (round trips; all regression references; cold-boot
capture)

Experiment: `EXP-0083`

- Both stream codecs (graphics LZ: a flag byte per 8 tokens; section A: LSB-
  first flag bits fetched as needed) can resume the original compressed
  stream after a re-encoded run, as long as the run ends where an original
  flag byte starts.
- A run can usually be given exactly the original byte length, by padding
  with literals or growing over neighbouring groups, so later sectors are
  unchanged. On the raw track, each changed 2,048-byte sector also changes
  304 bytes of EDC/ECC.
- The English captions change 7 of 2,064 script frames and about 25 KB of
  each 238 KB caption block. The release patches are 642,747 and 644,202
  bytes (from 2.95 MB).
- **Reproduce.** `research/experiments/EXP-0083/README.md`.

## REL-002: An .ssp Is a ZIP of Per-File BSDIFF40 Patches

Confidence: **CONFIRMED** (in-place applier and the official patcher's own
code, both variants)

Experiment: `EXP-0084`

- **Format:** an `.ssp` is a ZIP. Each `NAME._DFR` is a BSDIFF40 patch of
  file `NAME`.
  - **Required by the official patcher (v1.95, decompiled):** `version.txt`
    (first two parts compared; `1.0` means its old text format) and
    `driveOrder.txt` (`PATH,INDEX,XAMODE` per ISO entry, by extent).
  - **Required by `saturn-patcher-egui`:** `changes.md5` (`NAME:MD5` of each
    original file). The official patcher writes it but never reads it.
  - **Optional `ip.bin`:** replaces the image's system area in the official
    patcher. It is left out here.
- **Official patcher:** it rebuilds the ISO from the extracted, patched
  files in `driveOrder.txt` order.
- **egui:** it patches root files in place and regenerates EDC/ECC.
- **Release patches:** `tools/disc/make_ssp.py` writes 560,868-byte
  (`eb809034…`, Saturn names) and 560,981-byte (`1a7f0f32…`, American
  names) patches.
  - `saturn-patcher-egui` (commit `20837e06…`) applied to the untouched
    track 01 gives `e820f6e1…` and `a6572495…`: the release hashes.
  - macOS `/usr/bin/bspatch` reproduces all 34 patched files of each.
- **The official patcher's own code** (v1.95 core libraries on macOS):
  - **Unmodified:** its loader and bsdiff apply all 34 file patches exactly,
    in both variants.
  - **Its rebuild:** with one path-separator byte changed for macOS, it
    keeps every file at its original LSN with the release contents. Only
    LSN 16 (volume space size 216,839 → 218,484) differs from the release
    track 01.
  - **Audio:** it re-lays the CD audio tracks, with or without a patch.
  - **Boot:** the rebuilt image cold-boots into the English attract
    captions and the title screen.
- **Reproduce.** `research/experiments/EXP-0084/README.md`.

## TXT-001: The MM.BIN Story Lines Are a Rare Post-Loss Win Quote

Confidence: **CONFIRMED** (arcade read trace with a forced roll; Saturn RAM
trial on the release image)

Experiment: `EXP-0085`

- **When it shows:** `MM.BIN` records 16-41 (`0x7CA44` + 76 × n) are a rare
  alternative to the winner's win quote, on the screen after the CPU beats
  the player and before CONTINUE?. The winner's line is normally a random
  win quote of the winning character.
- **The trigger:** in the Japanese region (`0xCC90` = 0), a 1-in-64 roll
  (`and #0x3F`, `cmp/eq #39`) shows record 16 + the winner's slot instead.
  - Saturn code: `MM.BIN` `0x060AF1F2`; arcade: `0x070336`.
  - The arcade's other regions skip the roll, so these records have no
    English.
- **The placeholder** `{P}` (Chun-Li's record 27) inserts the winner's
  teammate.
- **Seen:**
  - arcade `mshvsfj` with the roll forced: Blackheart's record 24, and
    record 27 with "ザンギエフ";
  - Saturn US release image (`a6572495…`) with the branch forced:
    Apocalypse's record 16 in Japanese, in place of his English win quote.
- **Other English in the arcade:**
  - **Hints:** official English CONTINUE? hints at `0x2239FC`: 12 hints of
    two 100-byte records each, reached through the index map at
    `0x070448`. `mshvsfj` and `mshvsfu` are identical there.
  - **Records 42-44** (Vega's orders) have the English line "I've finally
    tracked you down! Now, you're mine!" at `0x2243C0`.
- **Correction:** `EXP-0047`'s code pointer at `0x0B03BA` is a value in a
  BCD powers-of-two table, not a reference to this table.
- **Reproduce.** `research/experiments/EXP-0085/README.md`.

## UI-006: The Saturn Can Page Its CONTINUE? Hints Like the US Arcade

Confidence: **CONFIRMED** (forced trial; cold-boot play check of all eight
hints)

Experiment: `EXP-0086`

- **Two pages per hint:** the US arcade shows each English hint as two
  100-byte records, page 1 then page 2 after `0x180` frames (`0x07012A`).
  The creator maps the random index onto even records (`0x070448`).
  - Both steps are skipped in the Japanese region, and the Saturn kept them
    behind the same test: creator `bt` at `0x060AF348` (`MM.BIN` `0x96848`),
    handler `bt` at `0x060AEE8C` (`0x9638C`), map at `0x060AF3A0`
    (`0x968A0`).
- **The release change:**
  - two `nop`s;
  - a map onto records 0-14;
  - the arcade's English pages 0-15 (hints 0-7) in the 16 hint records,
    with `0x0129` drawn as "+".
  - Each hint then shows word for word on two pages; all eight were seen
    forced, with all six arrows.
- **No other free space:** every `0x9999` padding run in `MM.BIN` is work
  memory at run time. Hints 8-11 do not fit.
- **Reproduce.** `research/experiments/EXP-0086/README.md`.

## TXT-002: The Post-Loss Story Lines Show in English

Confidence: **CONFIRMED** (forced trial of all 25 records; cold-boot play
check of record 24)

Experiment: `EXP-0087`

- **Built:** `--story-lines` builds `MM.BIN` records 16-41 from
  `data/translations/story_lines.json`, with `{P}` allowed at any cell.
  Record 35 (symbol noise) keeps its original cells.
- **Seen:** with the 1-in-64 branch forced and the story base moved, all 25
  built records show their English on the post-loss screen.
- **Placeholder:** record 27's `{P}` inserts a name mid-line, centred
  ("Oh? ZANGIEF, didn't you see").
- **Reproduce.** `research/experiments/EXP-0087/README.md`.

## TXT-003: Vega's Orders Are Shown When the CPU Fields a Secret Character

Confidence: **CONFIRMED** (arcade read trace with a forced CPU team);
Saturn by matching code

Experiment: `EXP-0088`

- **When they show:** story records 42-44 appear in the intro when the CPU's
  point character is Shadow (42), Metal Zangief (43) or Dark Sakura (44, a
  row of dots).
  - Vega steps in for the first two.
  - Nothing is shown when the player uses them.
- **Team words:** at arcade `0xFF48B0` and Saturn `0x060F48B0` (character ×
  2): player, then CPU.
- **Saturn:** the same routine (`0x060AF5A0`/`A8`/`B0`), called from
  `MC16`/`MC14`/`MC15`, with an extra flag test (`0x0601801C` = 0).
- **No other readers:** none reaches records 45-47, and record 39's other
  reader is an arcade-only scene.
- **Reproduce.** `research/experiments/EXP-0088/README.md`.

## SPECIAL-004: The Mech-Gouki Select Code and His Arcade Ending

Confidence: **CONFIRMED** (user play test of the US release image; record
107's English by forced trial)

Experiment: `EXP-0089`

- **Unlock chain (session words, cleared at boot):**
  - a Survival clear sets `0x06017AB0` (MECH-GOUKI NOW!! in the menu; the
    release presets it);
  - a MECH-GOUKI NOW!! clear sets `0x06017AB4` (seen at frame 11,283);
  - an Arcade clear sets `0x06017AA8` (seen at frame 72,468). Without it the
    partner select skips the point character, so Gouki cannot be picked
    twice.
- **The code:** at character select, hold Start and pick Gouki, then hold
  Start and pick Gouki again. The routine at `0x06051CD4` counts the picks
  (`0x06017CEE`/`EF`) and writes Mech-Gouki (`0x26`) to both team words; he
  plays alone.
- **His Arcade run:**
  - stage 8 is a Mech-Gouki mirror (CPU team `0026 0026`);
  - the post-boss scene shows `MC13` records 54, 55, 106 (dots) and 107,
    Gouki's 作られし者よ・・・, now "You who were created...";
  - the ending pages are the disc's generic English (`ME.PAC` `0x467C`
    records 0-2), then the credits.
- **Reproduce.** `research/experiments/EXP-0089/README.md`.

## REF-012: The Arcade Win-Quote Fonts Are One Glyph Set; the Saturn Has It Too

Confidence: **CONFIRMED** (MAME captures and memory dumps of `mshvsfu` and
`mshvsfj`; offline tile comparison; one Saturn forced trial)

Experiment: `EXP-0090`

- **Regions:**
  - all mshvsf sets load the same graphics ROMs (`mvs.13m`-`mvs.20m`, same
    CRCs);
  - win quotes are single 16 × 16 sprites, tile = `0x15000` + text code;
  - the US set uses the narrow Latin range (`0x120`-`0x1DF`) at a 12-pixel
    pitch, 25 cells a line;
  - the Japanese set uses kana and kanji codes at 16 pixels, 19 cells.
- **The Saturn quote font** (`MEMFIX.PAC` entry 4) has the same glyph shapes
  at the same codes for `0x100`-`0x18F`, `0x1E0`-`0x1FF`, most of
  `0x200`-`0x2FF`, and `0x800`-`0xBFF`, with pen + 1. A forced Saturn record
  of arcade codes shows the narrow letters, one per 16-pixel cell.
- **Digits are ASCII + `0x100`** (`0x130` = "0"): the arcade shows code
  `0x138` as "8" ("before 8 am..."), and the Saturn shows `0x12F`-`0x132` as
  ")012". `EXP-0078`'s base `0x12F` was wrong; `TXT-005` (`EXP-0091`) fixed
  the decoder and the release text.
- **Reproduce.** `research/experiments/EXP-0090/README.md`.

## LOC-006: The Options Settings Table, Its Backup-RAM Copy, and the Menu Text

Confidence: **CONFIRMED** (one recorded session at the Options menu; each
change matched against the screen)

Experiment: `EXP-0097`

- **Settings:** a table of longs in WRAM-H:

  | Address | Setting | Values |
  | --- | --- | --- |
  | `0x06017AB8` | DIFFICULTY | 1 = ★★, 2 = ★★★ |
  | `0x06017ABC` | TIME LIMIT | 1 = ON, 0 = OFF |
  | `0x06017AC0` | GAME SPEED | 0 = ★, 1 = ★★ |
  | `0x06017AC4` | VS SHORT CUT | 0 = OFF, 1 = ON |
  | `0x06017AC8` | AUDIO | 0 = STEREO, 1 = MONAURAL |
  | `0x06017ACC` | BACK UP | 0 = AUTO |
  | `0x06017AD0` | VS POWER GAGE | 0 = NORMAL, 1 = FULL |

  Each value changes at the moment the screen shows the change, and holds
  until the next change.
- **Backup RAM:** leaving the menu writes the low byte of each setting to
  the Mednafen `.bkr` file at offsets `0x19F`-`0x1B7`, every 4 bytes, in
  table order. Four bytes at `0x2B0` also change, consistent with a checksum
  (not tested).
- **Menu text:** plain ASCII in `MM.BIN`:
  - rows at `0x5C9F`, 35 bytes each. There are 11, including COMBO GAGE,
    which the menu does not show;
  - value strings at `0x5FDE`-`0x6667`;
  - the button-config screen at `0x6676`-`0x6A36`, whose " CHOUHATU" column
    header (`0x69EE`) is romanised Japanese.
- **Reproduce.** `research/experiments/EXP-0097/README.md`.

## REF-012 Addendum: Arcade Code `0x122` Draws "!?"

Confidence: **CONFIRMED** (arcade tile `0x15122` read from the `mshvsfu`
graphics ROMs; the Saturn quote font's code `0x122`)

Experiment: `EXP-0096`

- The arcade tile for text code `0x122` and the Saturn font's code `0x122`
  are the same glyph: a narrow "!" beside a narrow "?". `RE-044` had read it
  off a MAME screen as a double exclamation.
- `cps2_text` still decodes it as one "‼" symbol, so cell counts stay as
  they are. Under `--glyph-style arcade`, the pair builder takes that code's
  own glyph, so the two lines that use it ("star setting", "the rough stuff")
  get "!?" as in the arcade. They were not shown on the Saturn.

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
