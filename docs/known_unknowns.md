# Known Unknowns

These questions are unresolved unless a later entry links to reproducible evidence.

## Environment

- Which stock Mednafen version and build satisfy the M0 acceptance requirements?
- Are stock debugger facilities sufficient for the planned controlled experiments?
- How does stock Mednafen label the SH-2 program counter, expose Saturn address
  aliases, and implement breakpoints relative to the SH7604 hardware semantics?

## Target Data

- What is the verified target source-image identity and disc layout?
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
