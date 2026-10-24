# Agent Briefing

A short, cited entry point for agent sessions (task `DOC-008`). Every line points to
its authority; read the linked entry before acting on a claim. `AGENTS.md` and
`TASKS.md` govern; this file never overrides them. Last reviewed 2026-10-24.

Labels follow `docs/research_protocol.md`. **Project discoveries** (what this
repository proved about the exact target) are kept apart from **platform and
reference facts** (what outside documents say).

## Where Things Stand

- Milestone M4 is complete (2026-10-24): Ken works through the generalized
  mechanism (`RE-030`, `EXP-0028`).
- M5 (`RE-040`) is broken down into `RE-041` to `RE-047`. `RE-041` is done
  (`EXP-0034`): Saturn file `MCnn` = arcade slot `nn`, with 18 files ordinary and
  5 irregular. `RE-043` is done: the 17-character roster is in
  `data/text/m5_roster.json`, and exclusions are in `docs/coverage_exceptions.md`.
  `RE-042` is done (all 17 paired, `data/text/roster_pairing.json`). Next is
  `RE-044` (roster spec and font capacity), now done: it fits, using 90 reused
  kanji codes plus alignment. `RE-045` is done: the roster image (`EXP-0035`) is
  built and reviewed offline. `RE-046` is done (`EXP-0036`): four characters
  verified live. `RE-047` is done: `tools/regression/reference_builds.py` rebuilds
  the reference images against `data/regression/reference_builds.json`
  (report: `docs/regression_report.md`). **M5 is complete (2026-10-24).**
- M6 has started. `END-001` is done (`EXP-0037`):
  - final-boss checkpoints are in `local/end001/checkpoints/`;
  - Ryu's run shows a four-box post-boss dialogue plus three ending pages;
  - `END-002` is done (`EXP-0038`): the ending text is VDP1 sprites of
    byte-exact quote-font glyphs, built by `0x0601CE00` from 16-bit codes;
  - `END-003` is done (`EXP-0039`): the text is a live WRAM-L table of 19 × 2
    code records (`0x0000` = name placeholder from a WRAM-H name table),
    loaded with `STAGE-08`;
  - `END-004` is done (`EXP-0040`): the dialogue is in LZSS `MC13.PAC` (the
    boss's file, at `0x00220000`), and the pages are in raw `ME.PAC` (at
    `0x00230000`).

  - `END-007` is done (`EXP-0041`): marker images built from the untouched
    source load the edited `ME.PAC`/`MC13` with nothing else changed, and the
    page marker showed in a live run.

  Next are `END-005` (needs gameplay) and `END-006` (no gameplay).
- `GATE-TRANSLATION` passed on 2026-10-24 (user GO). Ryu's win-quote captions may
  carry English; other characters need their own pairing verification first.
  `TR-001` is done: Ryu's official-English image is verified live (EXP-0033).
- The win-quote English policy is decided: Saturn record `k` uses official arcade
  English entry `k & 7` (`data/translations/README.md`).

## Project Discoveries (Saturn Target)

All are **CONFIRMED** in `docs/discoveries.md` unless marked otherwise.

- **Environment.** Stock Mednafen 1.32.1 boots `T-1238G` with the 4 MiB extended-RAM
  cart (EMU-004, EMU-005). Save/load checkpoints work (EMU-009).
- **Debugger and dumps.** The debugger gives pause, dump, write, and write
  breakpoints (EMU-010, EMU-011). `tools/memory/mcs_extract.py` matches debugger
  dumps for WRAM-L, WRAM-H, VDP1, and VDP2 only (DBG-012).
- **Agent interface.** A minimal frontend patch drives Mednafen headlessly
  (`docs/mednafen_agent_interface.md`, `EMU-021`).
- **Ryu quote table.** 16 records × 38 big-endian 16-bit codes (two 19-cell lines;
  `0x0020` = blank). At runtime they are at WRAM-L `0x002091AC`; writing there
  changes the caption (RE-012).
- **Disc source.** LZSS `MC09.PAC` is decoded to WRAM-L `0x00200000` at character
  select, with the table at decoded `0x91AC` (DISC-001).
  - Same-size re-encoding and image rebuild reproduce edits from an untouched
    source (DISC-002, M2).
  - Ken's table is in `MC0A.PAC` at `0xA59C`, verified live with Ryu in one image
    (RE-030). It is byte-identical to the arcade Japanese slot 10.
- **Font.**
  - The quote font is stored verbatim as `MEMFIX.PAC` entry 4 and loaded into cart
    RAM (FONT-001, LAYOUT-001 A).
  - Full-width Latin `0x08E8`-`0x0925` displays (FONT-002).
  - Two-letter pair glyphs display (LAYOUT-001 C).
  - A same-size font repack adds pair glyphs at `0x00A8+` (FONT-003).
- **Selection.**
  - The index is a word at `0x060F9E66`, and the record pointer goes to
    `0x060F249C` (RE-023). A second quote state at `0x060F9ED6` (index
    `0x060F9F26`, base `0x060F9F0A`) is used in some KOs (EXP-0036);
    `ko_capture --quote-state` picks the one to force.
  - Records can be forced. Table bases move with team slot (`0x002191AC` for slot 2,
    RE-025).
- **Pipeline.** `tools/text/caption_compiler.py` builds marker images; all 16 Ryu
  records were verified live (RE-024).
- **Official English (Ryu).** `tools/text/official_captions.py` generates the spec
  from the local arcade ROM. The rebuilt image shows all 16 records in official
  English, verified live (EXP-0033, TR-001).

## Project Discoveries (Arcade Reference)

- **Sets.** The local `mshvsf` (EU 970625), `mshvsfu` (US 970827), and `mshvsfj`
  (JP 970707) match MAME 0.289. The keys and `qsound.zip` were added later, and all
  three boot (REF-008, `references/mshvsf/arcade/README.md`).
- **Text in ROM.** Latin win quotes are unencrypted 16-bit codes in `mvs.07b`, read
  through 26-slot tables per language (JP `0x20BFAC`, EN `0x20C014`). They are
  identical in all sets (EXP-0029).
- **On screen.** Displayed quotes come from those tables, and `0xFF249C` holds the
  entry address (EXP-0030).
- **Pairing.** The Saturn Ryu table is byte-identical to the arcade Japanese
  table. The arcade remap shows English entry `k & 7` for index `k` (EXP-0031).
- **SUPPORTED, not confirmed.**
  - Arcade slots outside the seven observed (5, 6, 9, 11, 12, 13, 16) follow the
    name list.
  - The Saturn port shares the arcade selection logic (same RAM offsets
    `…F249C`/`…F9E66`).
  - Do not treat either as fact (`AGENTS.md` rule 14).

## Platform and Reference Facts

Authorities are cataloged in `docs/references.md`.

- **Memory map.** WRAM-L `0x00200000`-`0x002FFFFF` and WRAM-H
  `0x06000000`-`0x060FFFFF`, with cache-through aliases and the SCU-DMA caveat
  (`docs/saturn_memory_map.md`, from Sega SCU manuals).
- **SH-2.** Delay slots, sign extension, and PR/PC conventions
  (`docs/code_map.md`, Hitachi manuals).
- **Disc.** Game-CD layout, boot-ROM recognition, and ISO 9660
  (`docs/disc_layout.md`). The target's measured layout is recorded under
  `DISC-010`.
- **Mednafen.** Commands and debugger behavior documented upstream versus observed
  (`docs/mednafen.md`).
- **Prior Saturn localization projects.** Method references only, with license
  scope stated per project (`docs/references.md` "Saturn Localization Projects").
- **XvSF.** Predecessor research is cataloged for idea generation only, with no
  structure transfer. None was found that documents XvSF or MSHvSF Saturn internals
  (`docs/references.md` "X-Men vs. Street Fighter (Saturn) and Related Prior Art",
  `DOC-007`).
- **Official English sources.** Arcade (primary), PS1 `SLUS-00793` (secondary), the
  capture protocol, and regional claims RC-1 to RC-8 (`docs/references.md`).

## Conflicting or Corrected Evidence

- `EXP-0019`'s "Q2 = record 4" was corrected to record 5 (RE-021).
- A first arcade punctuation mapping (`!`/`,`) was swapped. Win quotes are not
  8-bit ASCII (EXP-0029; `research_log.md`).
- TCRF's "all secret characters borrow quotes" is too broad. Shadow, U.S. Agent, and
  Mephisto have their own English blocks (EXP-0029).
- Encryption claim corrected: CPS-II encryption covers opcodes, but PC-relative
  tables inside region code read through the decrypted space (EXP-0031).

## Open Questions

`docs/known_unknowns.md` is authoritative. The most action-relevant:

- How do 25-character paired English lines fit 19-cell Saturn lines (pair glyphs,
  wrapping)?
- Do other characters' Saturn tables match the arcade Japanese tables?
- Is cart-RAM extraction from save states correct (no debugger reference)?
- What do `@(2,gbr)`, the special value 39, and the `0xCC90` remap do on the Saturn?

## Tools Index

| Area | Tool | Use |
| --- | --- | --- |
| Disc | `tools/disc/pac_lzss.py`, `pac_patch.py`, `patch_image.py`, `iso9660.py` | Decode, re-encode, and rebuild |
| Memory | `tools/memory/mcs_extract.py` | Save-state regions (validated ones only) |
| Text | `tools/text/quote_render.py`, `caption_compiler.py`, `font_pack.py`, `glyph_match.py`, `code_search.py` | Render, compile, font, match glyph cells to codes, find code sequences |
| Mednafen | `tools/mednafen/agent.py`, `ko_capture.py`, `verify_records.py`, `replay_state.py`, `session_recorder.py`, `write_trial.py` | Headless runs, checks, gameplay recording, and write trials |
| Regression | `tools/regression/reference_builds.py` | Rebuild reference images, compare hashes |
| Arcade | `tools/reference/mame_audit.py`, `cps2_text.py`, `quote_pairing.py` | Identity, text, pairing |
| MAME | `tools/reference/mame_timeline.lua`, `arcade_route.py`, `mame_snap_frames.lua` | Scripted runs |

Run Python through `./invenv.sh`. Keep outputs containing game text or images under
ignored `local/` or `build/`.

## Recurring Pitfalls

- Fixed RAM addresses move with team slot; resolve table bases at runtime (RE-025).
- MAME: the arcade pointer persists after a quote screen, so find the first change.
  Held inputs appear to skip quote screens. Region builds shift code addresses.
- Sort frame-numbered files numerically.
- Never analyze compressed save states directly. Never commit game text beyond
  minimal translation records.
