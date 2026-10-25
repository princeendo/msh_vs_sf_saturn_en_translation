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
- Why does a shorter declared PAC compressed length break the opponent load
  (`EXP-0036`)? The fix is confirmed; the mechanism is not. It may be a buffer
  layout or read plan derived from the length. The size threshold (about 3 bytes
  shorter worked, 270+ failed) is also unknown.
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
  - What selects the quote state? The pointer routine runs with `r12` =
    `0x060F9E16` or `0x060F9ED6` (base at `+0x34`, index at `+0x50`, `EXP-0036`).
    Cyclops's KO used the first; the Zangief, Captain America, and Dhalsim KOs
    used the second. Candidates: the winning side (1P/2P), the match number, or
    the team's state after a lost round. Discriminating test: one session with known sides, logging `r12` at
    `060AF724` for KOs from each side.
  - Can lowercase descenders (`p`, and possibly `g`, `q`, `y`) be drawn more
    clearly in the pair glyphs? In `EXP-0036`, `p` sits on the baseline with a
    short stem. It is legible and cosmetic only.
  - What is the WRAM-H list at `0x06094FD8`? It held per-team table pointers
    (`0x002091AC`/`0x0021A59C`, or `0x002191AC`/`0x0020A59C`), but `0x99000E99`
    in its second entry with partner Gouki (`EXP-0027` V2). Must the partner-name
    table (`0x06095EC4`) be localized for English? What is the undrawn extra
    39th display entry?
  - Do the other `MCxx.PAC` files hold other characters' quote tables? Yes:
    `MCnn` holds arcade slot `nn`'s table (`EXP-0034`). Runtime use is confirmed
    for `MC09`, `MC0A`, `MC01`, `MC02`, `MC0C`, and `MC0D` (`EXP-0036`).
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

## Endings (M6, from `EXP-0037`)

Nothing about win quotes may be assumed for endings (`AGENTS.md` rules 13-14).
Ryu's run showed a four-box post-boss dialogue at the top of the frozen stage,
then three ending pages (a picture panel and a bottom text box).

- **Selection.** Answered (`EXP-0043`): pages follow the point character. The
  dialogue is the partner's pair (16 + 2·partner slot) plus the point's pair
  (16 + 2·(26 + point slot)), and `0x0000` names the other character. Still
  open:
  - Does the KO character (partner instead of point) change anything?
  - Are Cyber-Akuma's pairs (records 54/55, 106/107) used?
- **Renderer.** Answered for box 1 and page 1 (`EXP-0038`, discoveries
  `END-002`): VDP1 sprites of byte-exact quote-font glyphs, built by
  `0x0601CE00` from 16-bit codes. Still open: whether pages 2-3, boxes 3-4, and
  other characters' endings use the same path; what the `0x50xx`/`0x51xx` tiles
  behind the page 1 text box are; and which layer draws the logo background.
- **Text in RAM.** Answered (`EXP-0039`): plain 16-bit codes in WRAM-L 19 × 2
  records, loaded with `STAGE-08`. Still open:
  - What selects the records, and what are the table bases and indexing?
  - Do the bases move with team or load order?
  - What fills the slot table at `0x00260E5E`?
  - Which name fills a `0x0000` placeholder (Ryu in box 1, Gouki in box 3)?
- **Capacity.** Ending lines use the same 19-cell grid as win quotes, and the
  longest seen is 16 glyphs. Can a line use all 19 cells, and can a box hold
  more than two lines? How many distinct glyphs fit in the per-screen VRAM
  slots (relevant for composed pair glyphs)?
- **Source.** Answered (`EXP-0040`): the dialogue is in `MC13.PAC` (LZSS, the
  boss's file), and the pages are in `ME.PAC` (raw from `0x10`). Still open:
  - How are both files indexed (which records per character or team)?
  - What do `ME.PAC`'s header and its 30 non-relocation differences mean?
  - Is the relocation rule (file + base + `0x40`) right, given it is inferred
    from deltas only?
  - Does an edited file load and display? Answered (`EXP-0041`): yes, with
    nothing else changed. The page marker showed live; the `MC13` marker was
    confirmed in RAM.
  - Are `ME.PAC` and `MC13` re-read after a continue? (The load sequence
    repeats and opens `END.PAC`.) What does `END.PAC` hold?
- **Font.** Answered: the glyphs are quote-font cells (`EXP-0038`), and the
  composed pair glyphs display in endings unchanged (`EXP-0044`, `EXP-0049`).
- **Layout.** Answered (`EXP-0039`): positions are explicit `0x0020` cells in
  19 × 2 records, and page 3's "gaps" are bracket-glyph whitespace. Still open:
  whether a third line or text past cell 18 is possible.
- **Speakers.** Answered (`EXP-0043`): boxes 1-2 are the partner's lines, and
  boxes 3-4 the point character's.
- **Continue.** Continuing after a final-boss loss went to character select and
  then `STAGE-08` (`SUPPORTED`, one run). Does that hold for every pick order and
  side?
- **Arcade.** Answered for Ryu (`EXP-0042`): the Japanese records are identical,
  and English exists for the pages. The dialogue is replaced in English by two
  generic partner lines. Still open:
  - other characters' endings;
  - the partner-line indexing beyond two partners;
  - Saturn `MC13` records 54/55 and 106/107, which do not match the arcade
    block;
  - how to handle the dialogue in English (a user decision).

- **Localization (M7, `EXP-0044`).** Ryu's ending is done. Still open:
  - What else inserts names (`0x0000`)? Answered by the census (`EXP-0047`).
    Still open: where the Japanese-only `MM.BIN` text table (`0x7CC86`) is
    shown (`TXT-001`).
  - What are the 92 WRAM-H bytes (`0x06010A94`, `0x060EFA91…`) that differ
    after a cold boot of the built image?
  - When exactly is the quote font loaded (after the title, before stage 1)?
  - Do all English partner lines and pages fit? Answered for the roster
    (`EXP-0046`): every roster line and page fits, with the longest name
    inserted.

## Endings: Open After M8 (`END-025`)

The roster's endings are localized and verified (`EXP-0048`-`EXP-0050`). These
remain open; none blocks the roster image.

- **KO character.** Does it change anything when the partner, not the point
  character, lands the final KO? Every run so far had the point character's
  ending, but the partner-KO case was not controlled.
- **Ordinary-fight vitality.** Where is the opponents' vitality in
  two-against-two fights? `0x060F3E50`/`0x060F4844` hold it only in the
  one-character boss fight (`EXP-0049`). There is no forced KO for ordinary
  fights, so live win-quote checks need a manual win.
- **Long-name centring.** Dialogue lines are centred for a 2-cell name, so
  CAPTAIN AMERICA (8 cells) sits right of centre, inside the box (`EXP-0049`).
  Is a per-name centring worth doing? It would need records per point and
  partner pair, or runtime help.
- **Dan's last page.** It is empty in the official English (the Japanese shows
  完). Optional: add "THE END" text. That would be a new translation, not the
  official English.
- **Live coverage.** 7 of the 17 roster endings were seen live: Captain
  America, Zangief, Vega, Sakura, Dan, and Gouki in combined images, and Ryu
  in `end010`. One win quote (Vega's) was seen in a combined image. The rest
  were checked offline (records, renders, same pipeline).
- **Excluded slots** (`docs/coverage_exceptions.md`, Endings):
  - the extent of the shared `ME.PAC` block at `0x467C` (slots 23-25), and of
    the arcade English block shared by slots 19-25;
  - why `MC13` records 54/55 and 106/107 differ from the arcade;
  - whether slots 0 and 19 can ever show their (shared) pages.

## Fonts (`FONT-011`)

- Which code generates the grey caption palette banks (`0x1E0`, `0x030`,
  `0x1F0`)? CPU write breakpoints and DMA logs never see the write. This no
  longer blocks gold, which uses a palette-number change instead
  (`EXP-0052`).
- What else uses the message-window initialiser's kinds `0x0C`, `0x24`, and
  `0x5C`? Any such window now shows gold too.
- How much per-glyph tuning do squeezed credits glyphs need (`I`, `!`, `l`,
  `i`, `j`, `1`)?
- Do CPU write breakpoints cover VDP1 VRAM at all? None fired, even on the
  command table, and there was no positive control (`EXP-0051`).
- What uses `TESTFIX.DAT`'s fonts?

## Localization: Names (`LOC-001`)

- Which screens show the regional names (Vega, Gouki, Mech-Gouki) as art?
  Seen so far: the VS screen, the life bars, the win screen, and the ending
  speaker labels. The full inventory is not done.
- Does the announcer speak character names, and which ones? The user reports
  the voice says "Vega". It is not checked per character.
- In what format, and in which files, are the art and voice samples stored?
  Is there any acceptable source of US-name voice clips? Only needed if the
  user chooses US names (`docs/localization_plan.md`).

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
- Answered for Ryu (`EXP-0031`): Saturn record `k` pairs with arcade English entry
  `k & 7` by game logic. Still open:
  - Does the Saturn keep the arcade's English remap and data path vestigially (the
    `0xCC90` flag and 100-byte records in `RE-023`)? Does the disc hold dormant
    English text, as Vampire Savior's does (`DOC-007` idea only)?
  - Do the other characters' Saturn tables match the arcade Japanese tables byte
    for byte? Answered by `EXP-0034`: yes, for all 23 files (file `nn` = slot
    `nn`). Still open: what the extra tables in `MC00`, `MC0C`, and `MC13` are.
  - Decided by the user on 2026-10-24: use the paired official English (record
    `k` gets entry `k & 7`). Still open: how 25-character English lines fit
    19-cell Saturn lines.
  - Do the two PS1-only English blocks (`EXP-0032`) belong to secret characters,
    and are they official English for lines the arcade never translated? This is
    deferred to `SPECIAL-001`.
- Do the European and US English wordings agree line for line?
- Which arcade ROM members hold post-fight text, and in what form? Answered for
  Latin text by `EXP-0029` (`mvs.07b`, 16-bit codes); still open for Japanese.
- Answered (`REF-009`): with the keys and `dl-1425.bin`, all three sets verify
  and boot in MAME 0.289. Still open: how is the arcade language setting chosen
  (RC-7), and does the European set offer more than English?

Record competing explanations and the smallest discriminating experiment in
`research_log.md`. Move only confirmed answers to the appropriate technical document
and `docs/discoveries.md`.
