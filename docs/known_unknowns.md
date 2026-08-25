# Known Unknowns

These questions are unresolved unless a later entry links to reproducible evidence.

## Environment

- Which stock Mednafen runtime configuration satisfies the remaining M0 acceptance
  requirements beyond the verified `EMU-002` build?
- Are stock debugger facilities sufficient for the planned controlled experiments?
- How does stock Mednafen label the SH-2 program counter, expose Saturn address
  aliases, and implement breakpoints relative to the SH7604 hardware semantics?
- Which CPU selections and memory-editor address spaces does the selected stock
  Mednafen build expose for Saturn, and which can be dumped reproducibly?
- Do Saturn read/write breakpoints observe only CPU accesses, or also DMA and device
  activity, and at what point relative to the access do they stop?

## Target Data

- What is the verified target source-image identity and disc layout?
- What image-container format, session/track layout, sector representation, ISO 9660
  tree, extents, and IP fields does the exact target source contain?
- Which disc material must be preserved outside ordinary file contents for a
  deterministic, bootable rebuild?
- Where are Ryu post-fight captions stored on disc and during execution?
- What encoding, boundaries, indirection, compression, or transformation is used?
- What constraints apply to replacement text?

## Runtime Path

- When is caption data loaded, copied, selected, and rendered?
- Which memory regions and code paths participate?
- What deterministic checkpoint best isolates one caption change?

## Cross-Release Evidence

- Which official English line corresponds to each Japanese caption?
- Do any reference releases share behavior relevant to a specific experiment?

Record competing explanations and the smallest discriminating experiment in
`research_log.md`. Move only confirmed answers to the appropriate technical document
and `docs/discoveries.md`.
