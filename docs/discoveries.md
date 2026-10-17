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
