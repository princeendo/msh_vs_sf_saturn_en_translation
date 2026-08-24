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

## SH-2 Architecture And Debugging References

The following processor references were accessed on 2026-08-24. The PDFs remain
external and are not committed. They are platform references only; neither source
identifies MSHvSF code or data addresses.

### Hitachi/Renesas, *SH-1/SH-2 Programming Manual*

- Issuer: Hitachi Semiconductor; the mirror identifies the later vendor as Renesas
  Technology.
- Stable mirror: <https://antime.kapsi.fi/sega/files/h12p0.pdf>.
- Mirror filename: `h12p0.pdf`; 1,034,304 bytes; SHA-256
  `03364fae725c23980ae76d75f266f760844a6ce4e4ec54b7c40897b180be5d44`.
- Relevant areas: programmer-visible registers; instruction descriptions; addressing
  modes; condition-code behavior; delayed branches; exceptions and interrupts; and
  programmer-visible memory-access rules.
- Supported claims: SH-2 debugger interpretation must account for the general
  registers, `PC`, `PR`, `GBR`, `VBR`, `MACH`, `MACL`, and `SR`; instruction operands
  use the documented addressing modes; branch instructions with delay slots require
  instruction-flow interpretation beyond the branch address; and exception/interrupt
  handling uses the documented vector and status-register mechanisms.
- Limits: the mirror does not provide a verified publication edition in its catalog
  entry, and the manual is not a Saturn game debugger manual. These claims guide
  processor interpretation only.

### Hitachi/Renesas, *SH7604 Hardware Manual*

- Issuer: Hitachi Semiconductor; the mirror identifies the later vendor as Renesas
  Technology.
- Stable mirror: <https://antime.kapsi.fi/sega/files/sh7604.pdf>.
- Mirror filename: `sh7604.pdf`; 2,211,720 bytes; SHA-256
  `262cfff2abec2fa0cef5c5475495d6a4da390eff107ed3a75575827467daab9f`.
- Relevant areas: SH7604 memory map and bus interface; interrupt controller; DMA
  controller; cache and address behavior; and CPU peripheral registers.
- Supported claims: hardware-level debugger interpretation must distinguish CPU
  execution state from peripheral state, treat DMA and interrupt-controller
  registers according to documented access rules, and preserve the documented
  distinction between CPU-visible addresses and peripheral/register behavior.
- Limits: this hardware manual describes the SH7604 device, not the complete Saturn
  bus map or MSHvSF implementation. Saturn-specific mappings remain governed by the
  Sega references above and measured runtime evidence.

### Related mirror index

- Antime's Saturn documentation index identifies the two manuals under its
  `Renesas Technology` section and also lists the *SuperH RISC Engine Assembler,
  User's Manual* and *SuperH RISC Engine Simulator/Debugger, User's Manual*.
- The assembler and simulator/debugger manuals are not used as primary claims here:
  their exact editions and applicable host/tool versions were not independently
  established during this task. They remain candidates if a later experiment needs
  assembler syntax or simulator-specific behavior.

## Bibliography Fields

Record title, author or publisher when available, release or revision, publication
date when available, stable URL or local catalog identifier, access date, relevant
section, and the claim it supports. For software or source archives, also record the
upstream URL, version or commit, filename, size, SHA-256, license, and retrieval date.

## Local Materials

Keep copyrighted images, manuals, dumps, screenshots, and extracted contents outside
version control. `references/` may contain provenance records, permitted notes, and
links, but not unauthorized copies.
