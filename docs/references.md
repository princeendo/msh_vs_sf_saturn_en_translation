# References and Evidence Rules

References are evaluated by the authority of the document, not the authority of its
host. A third-party mirror of an official Sega document remains a primary document;
the mirror's catalog description is only secondary metadata.

## Reference Roles

- Official English arcade/CPS-II release: primary translation oracle.
- English PlayStation release: secondary translation oracle.
- Japanese Saturn X-Men vs. Street Fighter: technical evidence only when a specific
  experiment warrants comparison; never a modification target.
- Mednafen upstream material: emulator provenance and documented behavior.
- Platform documentation: technical claims only with recorded source details.

References do not establish structural equivalence between games, releases, or
platforms.

## Sega Saturn Architecture

All URLs in this section were accessed on 2026-08-24. The PDFs remain external and
are not committed.

### Sega, *Saturn Overview Manual*

- Issuer: SEGA; inspected English copy distributed through Sega of America, Inc.
- Release: temporary version 1, June 6, 1994.
- Document number: `ST-103-R1-040194`.
- Third-party PDF mirror:
  <https://antime.kapsi.fi/sega/files/ST-103-R1-040194.pdf>
- Mirror file identity: 707,231 bytes; SHA-256
  `0d44855f9ce5a62cbcd08895c1bf647b409651968c420c2b6a96399be1ce5a82`.
- Relevant sections: Chapter 2 sections 2.1 through 2.3; Chapter 3 sections
  3.1 through 3.7.
- Supported claims: the main system has two SH-2 processors and 2 MiB of main RAM;
  the SCU connects and controls the CPU-bus, A-bus, and B-bus; VDP1 performs sprite
  and primitive drawing into frame buffers; VDP2 handles scroll/background display,
  priority, and final composition; the sound block contains an MC68EC000, SCSP, and
  512 KiB sound RAM; SMPC performs system and peripheral control; the CD subsystem
  has its own SH-1 and 512 KiB buffer RAM; a cartridge interface is present.
- Limits: this is explicitly a temporary overview. It does not identify MSHvSF data
  structures or use of any hardware region.

### Sega, *SCU User's Manual*

- Issuer: SEGA; inspected English copy distributed through Sega of America, Inc.
- Release: Third version; internal version history dates Version 3 to July 15, 1994.
- Document number: `ST-97-R5-072694`; the mirror filename zero-pads this as
  `ST-097-R5-072694.pdf`.
- Third-party PDF mirror:
  <https://antime.kapsi.fi/sega/files/ST-097-R5-072694.pdf>
- Independent archival item: <https://archive.org/details/237-r-1>, ARK
  `ark:/13960/t7hr4p074`; its `SCUum.pdf` is byte-identical to the PDF above.
- Mirror file identity: 1,702,622 bytes; SHA-256
  `d56a86087f10c61d0bafaf5dfa0de134f92fe413e6e40f69a656df5192ccc8d3`.
- Relevant sections: Chapter 1 section 1.1, Figures 1.1 and 1.2; section 1.2,
  Figures 1.3 through 1.5; Chapter 2 section 2.1.
- Supported claims: the SCU contains CPU, A-bus, and B-bus interfaces plus DMA,
  interrupt, and DSP controllers; WRAM-L, WRAM-H, backup RAM, IPL ROM, and SMPC
  are on the CPU-bus side; CD and cartridge media connect through the A-bus; VDP1,
  VDP2, and SCSP connect through the B-bus. Figures 1.3 and 1.5 support the work-RAM
  ranges and cache-through aliases recorded in `docs/saturn_memory_map.md`.
- Limits: the map is diagrammatic. Address boundaries were checked against rendered
  page images rather than accepted from OCR alone.

### Sega, *SEGA Saturn SCU Final Specifications: Precautions*

- Issuer: SEGA; inspected English copy distributed through Sega of America, Inc.
- Release: Version 1, issued October 16, 1994 according to the revision history.
- Document number: `ST-210-110194`.
- Third-party PDF mirror:
  <https://antime.kapsi.fi/sega/files/ST-210-110194.pdf>
- Mirror file identity: 326,397 bytes; SHA-256
  `7842694c3fb747a9db921ac73e2454741d960fe40c2289fc515a2cb2feb7abdb`.
- Relevant sections: sections 1 and 3, especially items 04 and 05.
- Supported claims: SCU-DMA may use WRAM-H but not WRAM-L; SCU register access
  must use cache-through addresses. The document also supersedes parts of the base
  SCU manual, so detailed DMA or register work must consult it rather than the base
  manual alone.

### Sega, *Developer's Documentation, Electronic Version*

- Publisher: SEGA Enterprises Co., Ltd.
- Release: document version 2.50, second edition, issued August 1997; page date
  August 25, 1997.
- Third-party HTML mirror: <https://www.infochunk.com/saturn/segahtml_en/>.
- Relevant sections: Hardware Manual index; *Saturn Overview Manual*; *SCU User's
  Manual*; Hardware Manual errata at
  <https://www.infochunk.com/saturn/segahtml_en/xhistory/ver250/hard.htm>.
- Supported claims: this later Sega corpus identifies its publication state and
  records corrections to the overview and SCU manuals, including the revised SCU
  map labels and DMA precautions.
- Limits: the HTML conversion contains conspicuous translation and transcription
  defects. Use the original English PDFs for exact content of their 1994 publication
  states, but apply later Sega errata and final-specification notices where they
  explicitly supersede those states.

## Conflicts And Uncertainty

- The 1994 overview's Table 2.1 says `DMA 2 ch`, while its detailed Table 3.2 says
  three CPU channels and one DSP channel. The SCU manual also describes four total
  channels, and the final-specification notice says at most two may be used
  concurrently with guaranteed priority. These statements describe different things
  or publication states; `DMA 2 ch` is not used as a channel-count fact here.
- The 1994 SCU PDF cover says `Third version`, its number contains `R5`, and its
  internal history calls the July 15, 1994 state `Version 3`. These identifiers are
  preserved without inferring a reconciliation.
- The 1997 corpus incorporates later corrections and labels the SCU manual third
  edition dated November 1, 1996. It is not treated as identical to the 1994 PDF.
- The SCU manual defines 1 Kbyte as 1,024 bytes and 1 Mbit as 1,048,576 bits. The
  one-MiB work-RAM sizes are also fixed independently by their address boundaries.
  This project uses `MiB` and `KiB` when normalizing byte capacities.
- No collected platform reference establishes where MSHvSF stores or renders text.

## SH-2 Architecture And Debugging

All URLs in this section were accessed on 2026-08-24. The PDFs remain external and
are not committed. These are processor references only; neither source identifies an
MSHvSF address, data structure, or execution path.

### Hitachi, *SuperH RISC Engine SH-1/SH-2 Programming Manual*

- Issuer: Hitachi America Ltd.
- Release: September 3, 1996; no document number is visible in the inspected copy.
- Third-party PDF mirror: <https://antime.kapsi.fi/sega/files/h12p0.pdf>.
- Mirror file identity: `h12p0.pdf`; 1,034,304 bytes; SHA-256
  `03364fae725c23980ae76d75f266f760844a6ce4e4ec54b7c40897b180be5d44`.
- Relevant sections: section 2, Register Configuration; section 3, Data Formats;
  sections 4.1 through 4.3, Instruction Features and Addressing Modes; section 5,
  Instruction Set; branch descriptions in sections 6.6 through 6.13 and 6.25,
  6.26, 6.50, and 6.51; section 7, Pipeline Operation; appendix A, Instruction
  Code.
- Supported claims: the programmer-visible state includes sixteen 32-bit general
  registers plus `SR`, `GBR`, `VBR`, `MACH`, `MACL`, `PR`, and `PC`; `R15` is the
  hardware stack pointer during exception handling; instructions are fixed-width
  16-bit values; the documented addressing modes define how effective addresses are
  calculated; byte and word memory loads are sign-extended; and delayed branches
  execute their slot instruction before transferring control. The manual defines its
  architectural `PC` as the fourth byte after the current instruction, a convention
  that must not be assumed to match a debugger's display label.
- Limits: the manual covers both SH-1 and SH-2, so CPU-specific tables must be checked
  before applying an instruction. It describes processor semantics, not a Saturn bus
  map or emulator interface.

### Hitachi, *SH7604 Hardware Manual*

- Issuer: Hitachi, Ltd.; published by its Customer Service Division.
- Release: document `ADE-602-085C`, revision 4.0, September 19, 2001; first edition
  March 1995 and fourth edition September 2001.
- Third-party PDF mirror: <https://antime.kapsi.fi/sega/files/sh7604.pdf>.
- Mirror file identity: `sh7604.pdf`; 2,211,720 bytes; SHA-256
  `262cfff2abec2fa0cef5c5475495d6a4da390eff107ed3a75575827467daab9f`.
- Relevant sections: section 2, CPU; section 4, Exception Handling; section 5,
  Interrupt Controller; sections 6.1 through 6.3, User Break Controller; section
  7.1.5, Address Map; sections 8.3 through 8.5, Cache; and appendix B, List of
  Registers.
- Supported claims: exception entry saves `SR` and `PC` through `R15` and obtains the
  handler from the vector table; the SH7604 user-break controller has two channels and
  can compare address, instruction-fetch versus data-access cycle, read versus write,
  operand size, and, on channel B, data; it can request a break before or after an
  instruction's execution; and a data-access break does not identify an exact
  instruction as precisely as an instruction-fetch break. The manual also documents
  cache and DMA effects that can make a CPU-only explanation incomplete.
- Limits: this later revision documents the SH7604 device and its self-debugging
  hardware, not Mednafen's debugger implementation. Whether stock Mednafen exposes,
  emulates, or bypasses these facilities is unverified. The hardware manual's generic
  SH7604 address map must not replace Sega's Saturn memory map.

### Source Selection And Uncertainty

- Antime's documentation index identifies both official vendor manuals under its
  Renesas Technology section. The authority comes from the documents' Hitachi
  publication identities, not from the mirror.
- The index also lists SuperH assembler and simulator/debugger manuals. They were not
  needed for the processor claims above, and their tool-specific behavior is not used
  as evidence for Mednafen.
- The 1996 programming manual and 2001 fourth-edition hardware manual agree on the
  debugger-relevant register, alignment, branch-delay, and exception concepts sampled
  here. The later hardware revision may include post-Saturn errata or features; no
  revision-specific claim is transferred to target behavior without measurement.

## Saturn CD And Filesystem

All URLs in this section were accessed on 2026-08-24. The Sega PDFs remain external
and are not committed. These references define platform formats and interfaces; they
do not show which permitted features MSHvSF uses or how a local image container maps
tracks and sectors.

### Sega, *Disc Format Standards Specification Sheet*

- Issuer: SEGA; inspected English copy distributed through Sega of America, Inc.
- Release: version 1.0, copyright 1995.
- Document number: `ST-040-R4-051795`.
- Third-party PDF mirror:
  <https://antime.kapsi.fi/sega/files/ST-040-R4-051795.pdf>.
- Mirror file identity: 436,835 bytes; SHA-256
  `066dccf08feb72713f78d371dcaf749cf9aa9ed9264c51629c0fc85d5770f1d2`.
- Relevant sections: 1.0, Disc Format Overview; 2.1 through 2.4, physical
  organization, track layout, position keys, and sectors; 3.1 through 3.4, logical
  format; and 4.1 through 4.8, boot system.
- Supported claims: a conforming Game-CD is single-session and uses a Mode 1 track
  first, followed by any Mode 2 Form 1/Form 2 tracks and then CD-DA tracks; Game-CD
  logical structure conforms to ISO 9660; `LSN = FAD - 150`; Mode 1 and Mode 2 Form 1
  sectors have 2,048 user-data bytes, while Mode 2 Form 2 has 2,324; LSN 0 through 15
  form the system area and ISO 9660 volume descriptors begin at LSN 16; and the system
  area's IP contains System ID, security code, area code group, and application initial
  program. Directory records carry extent location, data length, flags, and file
  identifier, and a file may be interleaved rather than physically contiguous.
- Limits: the document describes a mastered Game-CD, not `.cue`, `.bin`, CHD, or
  other image-container semantics. Its sample mastering scripts are examples, not
  evidence of target layout. It does not establish MSHvSF track count, filenames,
  extents, sector modes, interleaving, IP fields, first-read file, or rebuild method.

### Sega, *Boot ROM User's Manual*

- Issuer: SEGA; inspected English copy distributed through Sega of America, Inc.
- Release: copyright 1995.
- Document number: `ST-079B-R3-011895`.
- Third-party PDF mirror:
  <https://antime.kapsi.fi/sega/files/ST-079B-R3-011895.pdf>.
- Mirror file identity: 247,170 bytes; SHA-256
  `ee2c05e29091ab7aac76624612b1f2eabd17335e8590883d549ab2d7e3a8ea7b`.
- Relevant sections: 1.0, Introduction; 2.0, Boot ROM Process Flow; 3.0, SEGA SATURN
  Logo Display and Game Startup; and 4.0, Troubleshooting.
- Supported claims: the boot ROM checks whether inserted media is recognized as a
  Saturn Game-CD while displaying the logo and starts the game only when the required
  boot code is recognized.
- Limits: the manual explicitly describes a non-Japanese boot ROM and warns that
  Japanese units differ. It establishes neither target boot behavior nor which BIOS
  behavior Mednafen reproduces; those require the exact BIOS and runtime evidence.

### Sega, *System Library User's Guide*

- Issuer: SEGA; inspected English copy distributed through Sega of America, Inc.
- Release: copyright 1994; the inspected copy archives pages 1 through 20 and directs
  readers to `ST-162-R1-092994` for revised System Program and SMPC material.
- Document number: `ST-162-062094`.
- Third-party PDF mirror:
  <https://antime.kapsi.fi/sega/files/ST-162-062094.pdf>.
- Mirror file identity: 875,729 bytes; SHA-256
  `3fc11970edae90fcbafd47966637a0deb2a941b6e7cb335da451bc7acee8d1ad`.
- Relevant component and sections: *CD Communication Interface User's Manual*,
  sections 1.1 through 1.3, interface and functions; 2.1 and 2.2, terminology and disc
  layout; 3.1 through 3.4, communication and transfer; 4.1 through 4.3, drive; 5.1
  through 5.5, CD block; and 6.1 through 6.2.3, ISO 9660 file system.
- Supported claims: the host exchanges commands, responses, and sector data with the
  CD block through its hardware interface; the CD block addresses media by FAD and
  can expose TOC/session information; its ISO 9660 service reads directory records,
  retains file information, and reads file sectors through selectors and buffer
  partitions; and it supports multisession media generally, using the last session's
  volume descriptor for its file-system service.
- Limits: documented hardware or library capability does not prove that MSHvSF uses
  the library or a specific command path. The CD block's generic multisession support
  does not override the Game-CD mastering rule prohibiting multisession.

### ISO, *ISO 9660:1988*

- Issuer: International Organization for Standardization.
- Release: edition 1, April 1988; corrected English version September 1988; withdrawn
  in 2023 and revised by ISO/IEC 9660:2023.
- Catalog record: <https://www.iso.org/standard/17505.html>.
- Relevant material: public abstract and general information. The full standard was
  not acquired for this task.
- Supported claim: ISO 9660:1988 specifies CD-ROM volume and file structure,
  including descriptors, file placement, file attributes, and record structures.
- Limits: field-level statements here are cited to Sega's Saturn-specific format
  document, not inferred from ISO's public abstract or the later 2023 revision.

### Scope Boundaries And Apparent Conflict

- `ST-040-R4-051795` prohibits multisession for a conforming Saturn Game-CD.
  `ST-162-062094` documents that the CD drive and CD-block file-system interface can
  handle multisession media generally. These statements have different scopes and are
  retained together; neither is evidence that the target disc is multisession.
- The format standard says files may be interleaved and the CD block can select by
  FAD and subheader. Therefore an ISO extent alone is not sufficient evidence of a
  byte offset in an arbitrary image container.
- No source above identifies the target release's tracks, files, extents, sector
  modes, boot fields, image-container layout, checksums, or rebuild constraints.

## Mednafen Debugger

All URLs in this section were accessed on 2026-08-24. This is an upstream
documentation baseline, not evidence from a local build or target runtime.

### Mednafen Team, *Debugger Documentation*

- Upstream page: <https://mednafen.github.io/documentation/debugger.html>.
- Publication identity: last updated November 25, 2023; valid as of Mednafen
  `1.32.0-UNSTABLE`.
- Retrieved HTML identity: 9,827 bytes; SHA-256
  `13545a2e06adee0ce172f47952a5ca9617ab87ceb074d6cbfde61100c7cfd53d`.
- Relevant sections: Notes and Cautions; Quick Key Reference; Memory Poking; Read and
  Write Breakpoints.
- Supported claims: the `ss` module is listed among modules with at least basic
  debugger functionality; the debugger documents CPU run/step, register and address
  editing, PC/read/write breakpoints, watches, memory pokes, memory-space selection,
  and memory dump/load operations. The dump prompt accepts either an inclusive
  `start_address end_address filename` range or `start_address +count filename`.
- Documented cautions: save states and power/reset while in step mode may cause
  significant malfunctions or glitches in the Saturn module; PC breakpoints are
  checked against the PC at instruction start; branch history is reliable while the
  CPU debugger view is inactive only when at least one breakpoint is installed; and
  high-level poke is not implemented for every system.
- Limits: the page does not enumerate Saturn CPU selections, register presentation,
  memory-editor address-space names, address aliases, graphics-viewer support,
  breakpoint timing, dump behavior at boundaries, or high-level-poke support. It does
  not say whether Saturn read/write breakpoints observe CPU, DMA, or device accesses.

### Mednafen Team, *General Documentation*

- Upstream page: <https://mednafen.github.io/documentation/mednafen.html>.
- Publication identity: last updated March 19, 2024; valid as of Mednafen `1.32.1`.
- Retrieved HTML identity: 142,106 bytes; SHA-256
  `897f6cbd6659d5f53360549a6f2c172164d23b4f3d36db87385071f024098b09`.
- Relevant sections: Key Assignments; Global Settings Reference, especially
  `debugger.autostepmode`; Screen Snapshots; Debugger link.
- Supported claims: `Left Alt+D` is the default debugger toggle;
  `debugger.autostepmode` can enter step mode after loading a game; and snapshots and
  save states are separate general facilities.
- Limits: the general page links to the debugger documentation but does not update its
  stated `1.32.0-UNSTABLE` validity or certify debugger behavior in a particular build.

### Mednafen Team, *Sega Saturn Documentation*

- Upstream page: <https://mednafen.github.io/documentation/ss.html>.
- Publication identity: last updated March 19, 2024; valid as of Mednafen `1.32.1`.
- Retrieved HTML identity: 100,442 bytes; SHA-256
  `43d0a4a7cfb165b61e38ce2f50d58fd72e7510dd222b267c2bf5304667404c6f`.
- Relevant sections: Introduction; Firmware/BIOS; Internal Databases, Cart.
- Supported claims: the Saturn module is under active development, has save-state
  support, and its internal cart database identifies MSHvSF Japan product `T-1238G`
  as requiring 4 MiB extended RAM.
- Limits: the page contains no Saturn-specific debugger command or address-space
  reference. Database identification and documented requirements are not a local boot
  or debugger test.

### Release Provenance Boundary

- Upstream releases page: <https://mednafen.github.io/releases/>. It lists Mednafen
  `1.32.1`, dated April 5, 2024.
- Candidate source archive URL:
  <https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz>.
- Retrieved candidate archive identity: `mednafen-1.32.1.tar.xz`; 3,571,236 bytes;
  SHA-256 `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`.
- The archive was retrieved only to record provenance and was not committed or built.
  `EMU-001` selects this exact source release; license recording and source/build
  verification remain bounded by the selection and `EMU-002` work.

## Saturn Localization Projects

These repositories were inspected on 2026-08-24 at immutable commits. They are
method references, not evidence of MSHvSF structures. Source archives were retrieved
only for identity and inspection and are not committed.

### `coregee/devil_summoner_tools`

- Repository and revision:
  <https://github.com/coregee/devil_summoner_tools/tree/1e1483fb72584ad5dc39f07dff5e2ef5750dd69a>.
- Revision date: 2026-08-24.
- Retrieved archive: 4,977,408 bytes; SHA-256
  `1a008b377254b3df84ab8149bf259bfa031298178abf8e7d8a895ecdedfdda9d`.
- License: project-authored source and documentation are 0BSD. The repository's
  `LICENSE` explicitly excludes game-derived JSON text, modified images, preview
  screenshots, and future game-derived assets; third-party fonts retain their terms.
- Relevant technique: manifest every source track by exact size and SHA-256; restore
  extraction state from verified originals; publish rebuilt media transactionally;
  guard binary patches with expected original bytes and overlap checks; and verify
  unchanged tracks, ISO records, changed-sector bounds, and Mode 1 EDC/ECC.
- Limits: the documented Saturn repacker has its own allocation and relocation limits.
  Every address, format, font, engine patch, and loader behavior is specific to
  *Devil Summoner*. Only material inside the explicit 0BSD scope is reusable.

### `ralfguth/langrisser3-english`

- Repository and revision:
  <https://github.com/ralfguth/langrisser3-english/tree/bee5a495eba18bbec0872faa552df47f4370f040>;
  tag `v0.7.2` points to the inspected commit.
- Revision date: 2026-08-24.
- Retrieved archive: 1,938,981 bytes; SHA-256
  `236294909f5c9e0cb4235af3514a3fcd71b7fdf321ae069d7d48aa858623cc72`.
- License: GPL-3.0-or-later for the stated project contributions. The README records
  separately licensed fonts and prior translation contributions.
- Relevant technique: build from a fingerprinted source Track 1; stage extraction,
  text/font generation, insertion, and disc publication; update ISO directory extents
  when files grow; recalculate raw Mode 1 EDC/ECC; preserve mixed-mode track topology;
  and validate text controls, layout, output naming, and track placement in tests.
- Limits: GPL implementation cannot be copied into an MIT-only derivative without
  satisfying GPL terms. Langrisser's successful file relocation does not establish
  MSHvSF loader behavior, and its track, file, encoding, font, and movie details are
  release-specific.

### `benclaff/culdcept_saturn_tools`

- Repository and revision:
  <https://github.com/benclaff/culdcept_saturn_tools/tree/098142497c4b86e7c30b1ff98a8fb6cc032525e1>.
- Revision date: 2026-05-22.
- Retrieved archive: 48,093 bytes; SHA-256
  `797e908786fe2a8ff8e6f7e0353c93b1d9cdbc4194fab9657c82889bedf48b23`.
- License: GPL-3.0-or-later.
- Relevant technique: extract typed text classes to structured records containing
  original text, translation fields, offsets, controls, and layout guidance; preserve
  untranslated entries; and reject replacements that exceed measured byte capacity.
- Limits: the project emits a patched game file rather than a complete rebuilt disc,
  does not generally recalculate pointer tables, and deliberately constrains text to
  original capacities. Its offsets and formats target Culdcept v1.04, not MSHvSF.

### `eadmaster/pcrown`

- Repository and revision:
  <https://github.com/eadmaster/pcrown/tree/26def6fd9c2f804fc30ec90c95afa98974cafa02>;
  tag `v1.1b2` points to the inspected commit.
- Revision date: 2025-07-31.
- Retrieved archive: 4,601,139 bytes; SHA-256
  `39e989c47321f3e74e154bdf9ae9e2eeb2aaf325095db5e39571f91d186dc2b1`.
- License: top-level GPL-2.0. The tree mixes source with third-party tools,
  translations, images, and derived material, so the top-level license is not treated
  as proof that every artifact is reusable.
- Relevant technique: a released Saturn pipeline extracts event data, enforces line
  fitting, rebuilds translated events, replaces files in raw media, applies font and
  graphics changes, and emits a binary delta. Its documentation notes that already
  loaded event data can remain cached, requiring a loading transition or cold path to
  test a disc edit.
- Limits: reuse only files with clear provenance and compatible terms. Event formats,
  line limits, and caching behavior are Princess Crown observations and can only
  motivate controlled MSHvSF experiments.

### Qualified And Excluded Leads

- `AngelouCurator/new-parm-archives-tools` at
  `1453906aef0e87eefe240ee976fbf6d53a071e63` documents original Python tooling for
  ISO walking, text injection, relayout, and emulator checkpoints. Retrieved archive:
  439,108 bytes; SHA-256
  `7d37c53e2a9efa33a6a1bfa9e0f36191f8ca1a7b3432070159e8cdc7402b20d2`.
  Its README says original code and documentation are MIT, while its `NOTICE` says
  MIT covers only the README, documentation, and issue templates. Because those
  scopes conflict and required upstream tools are unlicensed, no code is approved for
  reuse here without clarification. Its warning that synthesized sectors may lack
  valid EDC/ECC is a useful negative design lesson, not a recommended implementation.
- `DerekPascarella/Rabbit-EnglishPatchSaturn` at
  `2cafe00bd3bb59046b60a1add2bc04e0f8aed194` is a relevant released Saturn
  fighting-game translation, but no repository license was found. It may suggest
  questions about compression, integrity checks, and dialogue surfaces; its code,
  scripts, text, and assets are not reusable here absent permission.
- SegaXtreme's Saturn translation resource category is a discovery index, not a
  source-code license. A downloadable patch or project page without explicit reuse
  terms is not treated as reusable implementation.

### Transferable Process Only

The corpus supports using these process patterns without assuming target structure:

- hash every source component and reject an unexpected release;
- prove a no-edit extraction/rebuild round trip before changing text;
- guard every patch with expected original bytes and reject overlaps;
- preserve control tokens separately from translated prose and enforce measured byte,
  glyph, row, and pixel limits before writing;
- treat file growth, pointer changes, and disc relayout as separate experiments;
- regenerate Mode 1 EDC/ECC instead of relying on emulator tolerance;
- verify ISO records, changed sectors, track topology, and unchanged audio; and
- cold-boot or cross a deterministic reload boundary after source-media changes.

No project above establishes MSHvSF encoding, offsets, pointers, compression,
renderer behavior, file relocation safety, or runtime caching.

## MSHvSF Official English Text Sources

This section identifies candidate official releases and the evidence needed to use
them. It does not adopt a quote transcription or assert correspondence with Japanese
Saturn text. Sources were accessed on 2026-08-24.

### US Arcade Revisions In MAME 0.289

- Catalog authority: MAME upstream signed tag `mame0289`, tag object
  `d0b7160e54874fa58f553614db373d73100d5ecb`, commit
  `f34f02505e32c1993c6a782b6814232cbfc74e36`, released 2026-07-30.
- Immutable source:
  <https://github.com/mamedev/mame/blob/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp>.
- Retrieved source identity: 977,277 bytes; SHA-256
  `a8c09ef83841d75b81a4b2ee8ac029ebf8eecb6a743b016abb33e3d46e861602`.
- `mshvsfu`: *Marvel Super Heroes Vs. Street Fighter (USA 970827)*. Distinguishing
  program files include `mvsu.03g` CRC-32 `0664ab15`, SHA-1
  `939fb1e3c06c33fc212b26ecfceac3180e108e9d`, and `mvsu.04g` CRC-32
  `97e060ee`, SHA-1 `787924e04508c83ecd4c3a872882d2be9e57eb50`.
- `mshvsfu1`: *Marvel Super Heroes Vs. Street Fighter (USA 970625)*. Distinguishing
  program files include `mvsu.03d` CRC-32 `ae60a66a`, SHA-1
  `1fa7e6534d02ec8059153705b1161a55b9cfe803`, and `mvsu.04d` CRC-32
  `91f67d8a`, SHA-1 `e95f7a3fb281e1bafdbe7a1b22532c4fab5ec89d`.
- MAME also catalogs a `970625 Phoenix Edition` as a bootleg. It is excluded as an
  official wording source.
- Reliability: the pinned MAME catalog provides reproducible set identities and ROM
  fingerprints. It does not transcribe, render, or establish any post-fight wording.
  `970625` and `970827` are program version labels, not proven retail dates. Whether
  the two revisions show identical quotes is unknown until both are captured.

### Official Arcade Context

- Capcom Coin-Op, Inc., *Marvel Super Heroes Vs. Street Fighter Operator's Manual*;
  manual `PM00201`, printed code `062897`, copyright 1997; Internet Archive item
  <https://archive.org/details/arcademanual_marvel-super-heroes-vs-street-fighter>,
  ARK `ark:/13960/t9d56vh3h`.
- Retrieved original PDF identity: 3,393,718 bytes; SHA-256
  `709fc6257bef27d07f01fc004adc20ff215fe6afb1eea742c03882318876f48e`;
  Archive metadata MD5 `190eff6a86099e5d03d880fe78b21965` and SHA-1
  `01b8609fb3958c1cef1f926b796b48a48a888256`.
- Reliability: the manual is primary evidence for an official US/Canada Capcom arcade
  product and its operator context. It does not identify either MAME program revision
  and contains no post-fight quote corpus.

### Capcom 2024 Reissue

- Official page:
  <https://www.capcom-games.com/marvel-vs-capcom-fc/en-us/title/marvel-vs-sf/>.
- Capcom labels the included release `JAPAN 970707 / USA 970707` and documents changes
  from the original, including a playable Cyber-Akuma mode and light reduction.
- Reliability: this is an official, legally available runtime source for its own
  `USA 970707` presentation. MAME 0.289 catalogs US `970625` and `970827`, not
  `970707`. The relationship among these builds is unresolved, so the reissue must be
  recorded as a third release rather than substituted for either original board set.

### US PlayStation Release

- Primary candidate: *Marvel Super Heroes vs. Street Fighter*, US PlayStation,
  `SLUS-00793`, Fighters Edge, English, NTSC-U.
- Redump record: <http://redump.org/disc/12632/>; status records at least two dumps
  from original media. One Data/Mode 2 track: 235,074 sectors; 552,894,048 bytes;
  CRC-32 `94eb061c`; MD5 `a182cf4649be619c78c0aeb172f5246b`; SHA-1
  `6e50ac0d4dfc5eaf2ddd0da3cabde19e0ec3721a`.
- MAME corroboration: MAME 0.289 `hash/psx.xml` at the same pinned commit identifies
  software `mshvsf`, `SLUS-00793`, NTSC-U, Capcom Entertainment, and the matching raw
  track. Retrieved XML identity: 3,919,227 bytes; SHA-256
  `d5c9acd791513686a6e94061f2efb49f0c46d13260aa0465ade8ebe84a0fbc1f`.
- Official contextual corroboration: the ESRB record at
  <https://www.esrb.org/ratings/3836/marvel-super-heroes-vs-street-fighter/>
  identifies Capcom Entertainment and PlayStation/PS one. The scanned official English
  manual is archived at
  <https://archive.org/details/marvel_super_heroes_vs_street_fighter_english>, ARK
  `ark:/13960/t11p4rw4g`; retrieved PDF identity 6,452,890 bytes, SHA-256
  `ddaa9fb8f8974a034af26628caf55b544fceffa05ebbd627c966ed2ccb136840`,
  Archive metadata MD5 `1346d56b9ab54876f7607e185eff7bd2` and SHA-1
  `bb5f3bf52f4893df1acec56da063bfc4567755fd`.
- Reliability: these sources establish the release identity, not quote wording.
  Redump's executable and filesystem timestamps are build metadata, not retail dates.
  Secondary catalogs disagree on the exact February 1999 US retail day, which is not
  needed for quote provenance and remains unresolved.

### Transcription Leads Are Not Oracles

- Robert Iu's *Quotes and Dialog Guide*, version 1.01, July 13, 1999, is available at
  <https://gamefaqs.gamespot.com/arcade/583597-marvel-super-heroes-vs-street-fighter/faqs/704>.
  It explicitly says its source was the US PlayStation version and only supposes that
  it should be close to the arcade version.
- Reliability: it is a useful period candidate index, but records no serial, disc
  hash, screenshots, route, arcade revision, or per-line evidence. Copies shown under
  arcade, PlayStation, and Saturn categories are one document, not independent
  confirmations. It cannot establish arcade wording or Japanese-English
  correspondence.
- Community wikis, user-contributed trivia, unversioned gameplay videos, and emulator
  screenshots without input hashes are lead-only sources for the same reason.

### Evidence Hierarchy And Capture Protocol

- Release identity: use pinned MAME ROM definitions or a full Redump-compatible disc
  fingerprint.
- Exact wording: capture and independently transcribe a lossless frame from the
  identity-verified official release. A catalog or extracted byte string alone does
  not establish rendered case, punctuation, spacing, or line breaks.
- Context: record mode, character, partner, opponents, stage, round, finishing
  character, settings, route, checkpoint, and whether quote selection is deterministic.
- Arcade comparison: reproduce the context in both `mshvsfu` and `mshvsfu1`; record
  exact MAME version/commit, ROM audit, command line, settings, and screenshot hashes.
- PS1 comparison: use a legal `SLUS-00793` disc matching the complete track fingerprint
  above; treat the result as evidence for that port only.
- Correspondence: matching character or similar meaning is insufficient. Keep a
  Japanese-English pairing as `HYPOTHESIS` until context and selection behavior are
  reproducibly linked. If random selection cannot be controlled, alternatives remain.
- Store screenshots, ROMs, disc images, and states only under ignored local paths.
  Commit release identifiers, hashes, commands, context, transcriptions, and confidence.

`REF-001` may use lead-only lists to choose a candidate route but not to adopt wording.
`REF-002` and `REF-003` establish the Japanese visible source. `REF-004` establishes
the primary arcade wording and correspondence confidence through direct capture.
`REF-005` records the PS1 equivalent only when it adds discriminating evidence.

## Bibliography Fields

Record title, author or publisher when available, release or revision, publication
date when available, stable URL or local catalog identifier, access date, relevant
section, and the claim it supports. For software or source archives, also record the
upstream URL, version or commit, filename, size, SHA-256, license, and retrieval date.

## Local Materials

Keep copyrighted images, manuals, dumps, screenshots, and extracted contents outside
version control. `references/` may contain provenance records, permitted notes, and
links, but not unauthorized copies.
