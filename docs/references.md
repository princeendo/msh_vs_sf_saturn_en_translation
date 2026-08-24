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
- The archive was retrieved only to record provenance and was not committed, built,
  or selected. Exact release selection, license recording, source verification, and
  build configuration remain `EMU-001` and `EMU-002` work.

## Bibliography Fields

Record title, author or publisher when available, release or revision, publication
date when available, stable URL or local catalog identifier, access date, relevant
section, and the claim it supports. For software or source archives, also record the
upstream URL, version or commit, filename, size, SHA-256, license, and retrieval date.

## Local Materials

Keep copyrighted images, manuals, dumps, screenshots, and extracted contents outside
version control. `references/` may contain provenance records, permitted notes, and
links, but not unauthorized copies.
