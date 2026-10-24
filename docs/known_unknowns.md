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
    A second partner-name path (flag `r11+0xCC8E`) has name lengths 15, 4, 9, 3, 3,
    … consistent with English names (`EXP-0025`, `HYPOTHESIS`). Is there a latent
    alternate text mode, and does the disc contain English text for it?
  - Does quote selection use the counter at `@(76,r12)`? This may explain Q3's
    non-recurrence. (`RE-023` / `EXP-0024`.)
  - Which full-width codes hold English punctuation (`?`, `.`, `,`, `'`, `-`)?
    Only `!` (`0x08DD`) is known. The caption compiler accepts letters, digits,
    space, and `!` until these are identified.
  - How large is `MC09.PAC`'s compressed-size margin for real English text? The
    `RE-022` pangram stress set left 155 bytes after a full re-encode.
  - Do free codes `0x00B2-0x00FF`, `0x0190-0x01DF`, and `0x0260-0x02AF` display
    like `0x00A8-0x00B1`? Only the latter were shown on screen (`EXP-0023`).
  - Ryu's table is unchanged as the second team member (at slot-2 base
    `0x002191AC`) and with other partners (`EXP-0027`). Open: versus mode
    (port 2 is unbound); whether `0x060F9E4A` briefly holds the other member's
    base; whether `0x002091AC` holds Ken's table in V1. What does the record 0 `0000`
    placeholder render beside Latin text? (`RE-025`. `RE-024` answered the last
    question: katakana ケン inline after the Latin text.)
  - What is the WRAM-H list at `0x06094FD8`? It held per-team table pointers
    (`0x002091AC`/`0x0021A59C`, or `0x002191AC`/`0x0020A59C`), but `0x99000E99`
    in its second entry with partner Gouki (`EXP-0027` V2). Must the partner-name
    table (`0x06095EC4`) be localized for English? What is the undrawn extra
    39th display entry?
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
- Do the local European (`mshvsf`), US (`mshvsfu`), and Japanese (`mshvsfj`) arcade
  sets contain the same post-fight quotes? `REF-008` found sourced but uncaptured
  claims (RC-1 to RC-6 in `references/mshvsf/arcade/README.md`):
  - Norimaro is selectable only in Japan, yet international ROMs hold his
    translated English, Spanish, and Portuguese win quotes (RC-1, RC-2).
  - The secret characters have unique quotes only in Japan (RC-3).
- Which display languages does each local set offer? All three store identical
  English, Spanish, and Portuguese quote text (`EXP-0029`); what selects one is
  untested.
- Slot order matches the name list for 7 observed slots, including Ryu = 9
  (`EXP-0030`). Still open: how are the 8 quotes in a slot chosen? How is the
  arcade Japanese text (`0x08xx`) encoded, and where is its quote table? Do inputs
  held at a quote screen skip it?
- Do the arcade's 8 quotes per character relate to the Saturn's 16 Ryu records?
  The counts differ; nothing is assumed.
- Do the European and US English wordings agree line for line?
- Which arcade ROM members hold post-fight text, and in what form? Answered for
  Latin text by `EXP-0029` (`mvs.07b`, 16-bit codes); still open for Japanese.
- Answered (`REF-009`): with the keys and `dl-1425.bin`, all three sets verify
  and boot in MAME 0.289. Still open: how is the arcade language setting chosen
  (RC-7), and does the European set offer more than English?

Record competing explanations and the smallest discriminating experiment in
`research_log.md`. Move only confirmed answers to the appropriate technical document
and `docs/discoveries.md`.
