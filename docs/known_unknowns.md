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
  `EXP-0014`: a CPU write breakpoint fired on a CPU store (`mov.w r0,@r6`). DMA
  visibility is still untested.
- Which game code paths access the 4 MiB cartridge RAM, and how can its contents be
  read without a debugger address space?

## Target Data

- What is the verified target source-image identity and disc layout?
- What image-container format, session/track layout, sector representation, ISO 9660
  tree, extents, and IP fields does the exact target source contain?
- Which disc material must be preserved outside ordinary file contents for a
  deterministic, bootable rebuild?
- Where are Ryu post-fight captions stored on disc? (During execution: WRAM-L
  `0x002091AC-0x0020966B` drives the display, `CONFIRMED` by `EXP-0015`.) What
  loads that table, and is it per character, per partner, or per match?
  `EXP-0018` (`CONFIRMED`): it is LZSS-compressed in `MC09.PAC`, decoded at
  character select. Open questions:
  - Do PAC header words 1-3 or the trailing bytes act as size or integrity checks?
  - Does the game accept a re-encoded file of a different length? (Same-size
    re-encoding with 14 fill bytes works, per `EXP-0019`.)
  - Full-width quote-style Latin displays correctly (`EXP-0021`, `CONFIRMED` for
    the tested codes). ASCII codes display only faintly.
  - Pair glyphs work (`EXP-0022`), for up to 76 characters per quote. The font
    repacks losslessly (`EXP-0023`). About 321 kanji (30 KB) are unseen in any
    record-shaped text table, enough for about 800 pair glyphs. Is any other text
    format (endings, story) using those kanji? Which UI code uses the
    `0x01xx-0x07xx` artwork glyphs? (`EXP-0023` Phase C emptied `0x0C5E`,
    `0x0C5D`, `0x0C5C`, `0x0C54` and used free codes `0x00A8-0x00B1`; no other
    use of either set has been checked.)
  - Does the alternate layout constant set (12-pixel step, about 25 cells per
    line), selected by a flag at `r11+0xCC90`, exist and work for quotes?
  - Does quote selection use the counter at `@(76,r12)`? This may explain Q3's
    non-recurrence.
  - Do the other `MCxx.PAC` files hold other characters' quote tables?
- Is `0000` in a quote record a partner-name placeholder, and how is the name
  chosen and laid out?
- What encoding, boundaries, indirection, compression, or transformation is used?
  `EXP-0011`: the visible quotes are not present as Shift-JIS bytes in WRAM on the
  quote screen. Quote-dependent candidates are WRAM-L 16-bit sequential entries
  and a high-entropy WRAM-H block. `EXP-0012`: the quote is drawn by VDP1 sprites
  from per-character 16x16 4 bpp font glyph cells (`SUPPORTED`). `EXP-0013`: quotes
  are 16-bit custom glyph codes (kana in Shift-JIS order) in a WRAM-L table
  (`SUPPORTED`). Where is the font stored, what is the kanji code order, and how
  is the table loaded from disc?
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
