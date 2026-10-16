# Known Unknowns

These questions are unresolved unless a later entry links to reproducible evidence.

## Environment

- Which remaining M0 runtime observations, beyond the confirmed local configuration
  strategy, are needed for a complete stock Mednafen acceptance?
- Are stock debugger facilities sufficient for the planned controlled experiments?
  `EXP-0007` confirmed paused WRAM and VRAM dumps, but the stock memory editor has no
  cartridge-RAM address space.
- Is cartridge-RAM extraction from save states correct? `EXP-0008` validated WRAM and
  VDP VRAM only, because no stock debugger reference exists for the cart.
- How does stock Mednafen label the SH-2 program counter, expose Saturn address
  aliases, and implement breakpoints relative to the SH7604 hardware semantics?
- Which CPU selections does the stock debugger expose for Saturn? (Memory-editor
  address spaces are recorded in `docs/mednafen.md` from `EXP-0007`.)
- Do Saturn read/write breakpoints observe only CPU accesses, or also DMA and device
  activity, and at what point relative to the access do they stop?
- Which game code paths access the 4 MiB cartridge RAM, and how can its contents be
  read without a debugger address space?

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
- What selects the post-fight win quote? `EXP-0009` showed it varies after a pre-KO
  checkpoint and is not determined by kill move or opponent alone. Is it timing or
  RNG, and does an exact-input replay reproduce the same quote?
- The user reports that the win quote always belongs to the team member who landed
  the KO. Does a Ken KO from the same Ryu/Ken checkpoint show a Ken quote under the
  same joint portrait? (Untested; every `EXP-0009` KO was Ryu's.)

## Cross-Release Evidence

- Which official English line corresponds to each Japanese caption?
- Do any reference releases share behavior relevant to a specific experiment?

Record competing explanations and the smallest discriminating experiment in
`research_log.md`. Move only confirmed answers to the appropriate technical document
and `docs/discoveries.md`.
