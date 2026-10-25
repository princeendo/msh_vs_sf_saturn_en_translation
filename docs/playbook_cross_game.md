# Cross-Game Agent Playbook: Repeating This Localization on X-Men vs. Street Fighter (Saturn)

Task: `DOC-020`. Written 2026-10-25, after M8 and `REL-001` of the Marvel Super
Heroes vs. Street Fighter (MSHvSF) project.

This file is meant to be copied into a **new** repository for the Japanese Sega
Saturn release of X-Men vs. Street Fighter (XvSF). It records how the MSHvSF
work was done, why, in what order, with which tools, and what failed. It is a
method, not a map: **nothing in it is a fact about XvSF.**

## How to Read This File

### The labelling rule

Every game fact below is an **MSHvSF fact**. It is marked like this:

> **MSHvSF:** the claim (evidence: `EXP-NNNN` or a `docs/discoveries.md`
> heading, in the MSHvSF repository).
> **Verify on XvSF:** the question to answer, and the smallest experiment.

- An MSHvSF fact tells you **where to look first** on XvSF, and **what kind of
  experiment** answered it. It never tells you the answer.
- Offsets, addresses, file names, code ranges, record sizes, compression
  formats, font formats, table layouts, slot numbers and renderer behaviour are
  all per-game. Re-derive each one on XvSF from an untouched XvSF image.
- Two Capcom games on one platform, from one year, can share an engine, or not.
  Treat any similarity as a **HYPOTHESIS** until an XvSF experiment confirms it.
  A matching byte sequence or a matching screen is not confirmation
  (`AGENTS.md`, "Required Method").
- Evidence pointers name MSHvSF repository paths. Copy this file together with
  a pointer to that repository, or keep both checkouts side by side.

### The rules this follows

MSHvSF `AGENTS.md` rules 13-15 and 25 apply in full:

- never assume XvSF and MSHvSF share structures, offsets, encodings, functions,
  memory addresses, or renderer behaviour (rule 13);
- never assume CPS-II, PlayStation and Saturn structures are identical
  (rule 14);
- reference releases are evidence and translation oracles, not templates
  (rule 15);
- XvSF is not modified from the MSHvSF repository (rule 25). XvSF work happens
  in its own repository, with its own `AGENTS.md`, `TASKS.md`, and research log.

### What XvSF material the MSHvSF repository already holds

These are **intake records**, made read-only in the MSHvSF project. They
describe the files on this machine, not the game's internals. Re-hash
everything at the start of the XvSF project.

| Material | Record | Status there |
| --- | --- | --- |
| Saturn JP data track (`T-1226G V1.002 19970925`, ISO plus 40 MP3 tracks) | `references/xmvsf/saturn_jp/README.md` | Identity **SUPPORTED** by the IP header only. Not a preservation image: it cannot be matched to MAME's CHD hashes. Running it in Mednafen is untested. |
| PS1 US (`SLUS`, MAME `psx.xml` `xmvsf`) and PS1 JP EX Edition | `references/xmvsf/ps1/README.md` | US identity **CONFIRMED** against MAME 0.289; JP EX **UNKNOWN**. |
| 11 arcade zips, 6 keys | `references/xmvsf/arcade/README.md`, `manifest.json` | 10 of 11 sets verify in MAME 0.289 (`xmvsfb.key` missing); `xmvsfu` and `xmvsfjr2` boot. Zips use older set names; a renamed copy folder exists. |
| Prior art | `docs/references.md`, "X-Men vs. Street Fighter (Saturn) and Related Prior Art" (`DOC-007`) | No public XvSF Saturn translation or internals research was found. Sources say XvSF needs the 4 MB cart (HSS-0167): an outside claim, not tested. |

**Verify on XvSF, first:**

- Obtain a preservation-grade image (Redump-style BIN/CUE, ideally verifiable
  against MAME's `xmvssf`/`xmvssfdou` CHD) before any emulator work. The
  intake note says the held rip suffices for file-level reading only.
- Record every component's filename, size, SHA-256 and release description
  before research (MSHvSF rule 2), as in MSHvSF
  `references/mshvsf/saturn_jp/README.md` (13 components).
- The intake note observed no `.PAC` or `MEMFIX` file names on the XvSF data
  track. So do not search XvSF for MSHvSF's file names; find XvSF's own files
  from runtime evidence (the method in "Win Quotes" below).

## Working With the User

These preferences were stated by the user during MSHvSF. Confirm they still
hold at the start of XvSF.

- **Ask only for gameplay.** On 2026-10-17 the user said the manual debugger
  workflow was too tedious ("super tired of all this tedious work"). They then
  authorized the Mednafen agent interface so the agent drives the emulator.
  Never ask the user to type debugger commands, load or dump memory, or relay
  screenshots. The user's job is to play: a KO, a team pick, a menu.
- **Plan each live experiment as one short gameplay session plus automation.**
  The typical shape: the user plays once to a moment; the agent records rolling
  states (`session_recorder.py`); later runs replay or force from that
  checkpoint with no input.
- **Give manual steps as a detailed table, last in the turn.** A numbered table
  with "Do this" and "What you should see" columns. Call the wrap-up with a
  recap only (no question), then write the table as the very last text. The
  user missed steps written above a question box. Say "left Option" for Alt
  chords. Never tell the user to press `F7` while the debugger is halted.
- **Verify screenshots yourself.** The user does not read Japanese. Read every
  capture; compare text-box crops or diff bounding boxes, never whole-frame
  hashes (see Pitfalls).
- **Record user decisions verbatim**, with the date, in `research_log.md` and
  the relevant policy file (`data/translations/README.md`,
  `docs/coverage_exceptions.md`, `docs/localization_plan.md`).
- **Ask before:** installing tools (Homebrew), downloading files, changing a
  gate, changing scope, choosing between capacity options, and any side effect
  on text outside scope. The user decided each of those in MSHvSF.
- **Commit and push** after each completed task (MSHvSF `AGENTS.md`, "Session
  Closeout"), staging only intended files.

## Design Decisions and Their Rationale

Each row is an MSHvSF decision. Propose the same default for XvSF, then confirm
it with the user and with XvSF evidence.

| Decision (MSHvSF) | Rationale | Evidence | Verify on XvSF |
| --- | --- | --- | --- |
| Empirical method, one hypothesis and one changed variable per experiment; confidence labels; experiments in `research/experiments/EXP-NNNN/` | Plausible guesses failed repeatedly (see Pitfalls). Every confirmed step is reproducible. | `AGENTS.md`, `docs/research_protocol.md` | Adopt unchanged. |
| Never modify the source image; every build goes under `build/`, from the untouched source, and is deterministic | Lets any result be rebuilt; lets regression compare hashes; keeps the evidence chain clean. | `tools/disc/patch_image.py` refuses output outside `build/` and unknown source hashes; `DISC-002` | Adopt unchanged. |
| Commit only scripts, schemas, hashes and metadata; keep game text, images, states, dumps and screenshots in ignored `local/` and `build/` | Copyright (`AGENTS.md` rules 21-22). Official English is read from the local arcade ROM at build time. | `data/translations/README.md` ("minimal text"); `release/README.md` | Adopt unchanged. |
| Stock Mednafen 1.32.1 first; modify it only after a documented insufficiency (`EMU-012`, `EMU-020`), minimally, frontend only | Keeps emulation identical to stock; the patch is about 600 lines, opt-in by environment variable. | `docs/mednafen_agent_interface.md` | Reuse the same patched binary if the version matches; re-run validations V1-V4 against XvSF states. |
| Save states are checkpoints, never RAM evidence; RAM comes from debugger dumps or from an extractor validated byte for byte against them | A compressed state is not a memory image; byte order was wrong in one variant. | `DBG-012` (`EXP-0008`) | Re-validate the extractor on XvSF states before using it. |
| Official English from the arcade (US set), not new translation | The user's policy; an official oracle exists for every in-scope line. | `data/translations/README.md` (2026-10-24) | Confirm the policy with the user; confirm XvSF's arcade English exists for each surface. |
| Pair Saturn records to arcade English **by game logic**, not by meaning | The arcade selection code decides which English entry corresponds to a Japanese record. | `EXP-0031` | Find XvSF's own selection and language remap in the arcade code. |
| Two Latin letters per 16-px glyph cell ("pair glyphs"), composed into free and sacrificed font codes | 19-cell lines hold up to 38 characters; arcade English lines were at most 25. | `LAYOUT-001` Phase C, `FONT-003` Phase C | Measure XvSF's cell grid, line length and font headroom first. |
| One shared font for all text in one image; joint allocation of pairs | The same font serves win quotes and endings. | `EXP-0038`, `EXP-0048` | Test whether XvSF surfaces share one font. |
| Scope by an explicit roster file; untouched blocks byte-checked in every build | Prevents silent collateral edits; makes exclusions auditable. | `data/text/m5_roster.json`, `docs/coverage_exceptions.md`, `tools/text/ending_coverage.py` | Adopt the method; the roster is a user decision. |
| Regression: every confirmed build is a reference rebuilt from the untouched image, hashes compared | Catches any generator or compiler drift. | `RE-047`, `docs/regression_report.md` | Adopt unchanged. |
| Release as an xdelta3 patch of the changed track, kept local, with a rebuild README | No game data is committed; a user-style apply and a fresh clone were tested. | `REL-001`, `release/README.md` | Adopt; check which tracks change. |
| Names follow the Saturn's own art and voice (provisional) | Text, art and voice stay consistent with no art or audio work. | `EXP-0050`, `docs/localization_plan.md`, `LOC-001` | Ask the user; inventory XvSF's regional names first. |

## Order of Investigation

The MSHvSF milestones, in order. Each one gated the next; do not start a later
one because it looks easy (MSHvSF `AGENTS.md` rule 8).

| ID | Outcome (MSHvSF) |
| --- | --- |
| M0 | Emulator, cart, pad, screenshots, states, debugger, docs and Python tooling work. |
| M1 | One caption changed in live RAM. |
| M2 | The same change reproduced from an untouched source image. |
| M3 | Many captions of one character handled by a program. |
| M4 | A second character through the same mechanism. |
| M5 | All ordinary win quotes, systematically. |
| M6-M8 | Endings: investigation, one ending, then all roster endings. |
| M9 | Special cases (Norimaro), only with explicit approval. |

Two gates were used (user decision, 2026-10-15, verbatim in MSHvSF
`research_log.md`, SESSION-0016): `GATE-M0` (technical prerequisites for the
first RAM mutation) and `GATE-TRANSLATION` (reference and translation
prerequisites, before English text goes on disc). Keep both.

### Phase 0: Environment and Source Identity

1. **Python project.** `uv`, Python 3.12+, `./setup_venv.sh` and `./invenv.sh`;
   `pytest`, `ruff check`, `ruff format --check`, strict `mypy`
   (`ENV-001`-`ENV-004`). `.gitignore` guards `local/`, `build/`, images,
   states and dumps (`ENV-006`).
2. **Source identity** (`ENV-007`): hash every component with
   `tools/disc/hash_source.py`. Re-check the hashes before and after each
   emulator run (every MSHvSF discovery records it).
3. **Stock emulator** (`EMU-001`-`EMU-011`): pin the version, build it under
   `vendor/`, keep a project-local configuration, and confirm in turn: boot,
   cartridge, pad, screenshots, states, debugger, dumps, writes and write
   breakpoints.
   > **MSHvSF:** stock Mednafen 1.32.1 boots `T-1238G` with
   > `ss.cart=extram4` forced, and the log says `Cart: 4MiB Extended RAM`
   > (`EMU-004`, `EMU-005`, `EXP-0001`, `EXP-0002`).
   > **Verify on XvSF:** the product code in the boot log, the cart the game
   > needs (sources say 4 MB; untested), and three cold boots to a stable
   > title screen.
4. **Extractor validation** (`DBG-006`, `DBG-012`).
   > **MSHvSF:** `tools/memory/mcs_extract.py` reproduces stock debugger dumps
   > of WRAM-H, WRAM-L, VDP1 VRAM and VDP2 VRAM byte for byte, with each
   > stored 16-bit element swapped; unswapped order is **DISPROVEN**.
   > Cart RAM is extracted but **not validated** (no debugger space)
   > (`DBG-012`, `EXP-0008`).
   > **Verify on XvSF:** repeat the same-instant comparison (debugger dump vs
   > state extraction) before using any extracted region as evidence. Keep
   > cart RAM at `HYPOTHESIS` unless a reference exists.
5. **Agent interface** (`EMU-012`, `EMU-020`, `EMU-021`): see "Tools" below.
   Re-run V1-V4 for XvSF; V4 needs one breakpoint whose expected hits are
   known from a manual halt.

### Phase 1: References and the Translation Oracle

Run this alongside Phase 2; it gates English text on disc, not RAM work.

1. **Arcade sets.** Identify each zip against a pinned MAME (MSHvSF: MAME
   0.289, driver `cps2.cpp` at commit `f34f0250…`, `REF-008`). Add keys and
   QSound; verify and boot headless (`REF-009`).
2. **Find the English text in ROM data.**
   > **MSHvSF:** Latin win quotes are unencrypted 16-bit codes in `mvs.07b`,
   > through a pointer table of 3 languages × 26 slots; each slot is 8 quotes
   > × 2 lines × 25 codes. Identical in EU, US and JP sets (`EXP-0029`).
   > Win quotes are not 8-bit ASCII; only credits and warnings are. The first
   > punctuation guess was swapped (`research_log.md`, 2026-10-23).
   > **Verify on XvSF:** where XvSF's English is, its encoding, its table
   > shape, and whether it differs by region. Test punctuation guesses
   > statistically (the case of the following word) before trusting them.
3. **Confirm on screen** that the decoded table is what the arcade draws, with
   a scripted MAME route (`tools/reference/mame_timeline.lua`,
   `arcade_route.py`) and a RAM pointer watch.
   > **MSHvSF:** work RAM `0xFF249C` holds the shown entry's address
   > (`EXP-0030`).
   > **Verify on XvSF:** find XvSF's equivalent by a two-state search in MAME.
4. **Pair by game logic.**
   > **MSHvSF:** the Saturn table is byte-identical to the arcade Japanese
   > slot. The arcade masks a random value to `k` (16-way) and, in non-Japanese
   > languages, remaps `00-07 00-07`, so Saturn record `k` pairs with English
   > entry `k & 7` (`EXP-0031`). The remap routine's address differs per region
   > build; PC-relative tables must be read from the decrypted opcode space.
   > **Verify on XvSF:** whether the Saturn tables equal the arcade Japanese
   > ones, how XvSF's arcade selects and remaps, and the region-specific
   > routine addresses. Force indexes in MAME to see every entry.
5. **Second English source.**
   > **MSHvSF:** the US PS1 release stores the arcade English blocks
   > byte-identically, plus two extra blocks (`EXP-0032`).
   > **Verify on XvSF:** compare the held XvSF PS1 US image with XvSF's arcade
   > English; do not assume identity.
6. **Gate.** The user decides the translation policy and gives the GO
   (`GATE-TRANSLATION`, 2026-10-24 in MSHvSF).

### Phase 2: Win Quotes (M1-M4)

Pick one character and one quote first (MSHvSF: Ryu, `REF-001`). Each step
below was a discriminating experiment; the decision points say what to do on
each outcome.

1. **Selection behaviour** (`REF-007`).
   > **MSHvSF:** the quote is not fixed per checkpoint, opponent or finisher;
   > one pre-KO state gave six different quotes (`EXP-0009`). An inference of
   > team-voiced quotes from the joint portrait was wrong: the quote belongs to
   > whoever landed the KO (user report, untested for a partner KO).
   > **Verify on XvSF:** replay one pre-KO state several times before
   > planning checkpoints.
2. **Checkpoints** (`DBG-001`-`DBG-005`): before the fight end, after the KO,
   caption visible, caption gone, with screenshots. Save under frame advance.
3. **Search RAM for the text** (`DBG-007`-`DBG-011`): dump WRAM-L and WRAM-H at
   each checkpoint, diff, and search.
   > **MSHvSF:** plain Shift-JIS is **not** in WRAM at the quote screen
   > (`EXP-0011`, **DISPROVEN** for the tested fragments).
   > **Verify on XvSF:** try plain encodings once; if they fail, move on.
4. **Find the renderer** (`DBG-013`).
   > **MSHvSF:** VDP2 is **DISPROVEN** as the text location; the quote is VDP1
   > sprites, one 16×16 4 bpp cell per distinct glyph, identified by color word
   > (`EXP-0012`, `tools/memory/vdp1_sprites.py`).
   > **Verify on XvSF:** walk VDP1 command lists and diff VDP2 across two
   > quotes. A game may draw text as VDP2 tiles instead (a forum post says some
   > *Street Fighter Zero 3* screens store text as tile graphics,
   > `docs/references.md`).
5. **Glyph identity to codes** (`DBG-014`).
   > **MSHvSF:** raw glyph cells and 1 bpp masks are not resident in RAM
   > (**DISPROVEN**; the font is compressed). Instead, each quote's 38-cell
   > **equality pattern** (which cells share a glyph) matched exactly one
   > place in WRAM-L: a table of 16-bit codes. Kana followed
   > `0x0800 + (SJIS2 − 0x9F)` (`EXP-0013`, `tools/text/pattern_search.py`).
   > **Verify on XvSF:** the equality-pattern search is encoding-independent
   > and should be tried before guessing any code scheme.
6. **M1: change the text in live RAM** (`RE-012`). Write a few known codes into
   the candidate table at a pre-KO checkpoint and see them on screen, with a
   no-write control.
   > **MSHvSF:** WRAM-L holds 16 records × 38 big-endian 16-bit codes (2 lines
   > × 19 cells, `0x0020` blank, `0x0000` a partner-name placeholder);
   > `あいう` appeared in the patched cells (`RE-012`, `EXP-0015`).
   > **Verify on XvSF:** record size, line count, cell count, blank code and
   > placeholder, all from XvSF RAM.
7. **Disc source** (`DISC-010`, `DISC-001`).
   > **MSHvSF:** the table is not stored verbatim on disc, in any byte order or
   > plain encoding (`EXP-0017`, **DISPROVEN**). A **write breakpoint on the RAM
   > table**, from a character-select checkpoint, halted inside the game's
   > decompressor, whose context named the file. The format was LZSS with
   > MSB-first flags (`DISC-001`, `EXP-0018`, `tools/disc/pac_lzss.py`).
   > **Verify on XvSF:** use the same breakpoint method; it finds the loader
   > whatever the format. Map the ISO 9660 layout first
   > (`tools/disc/iso9660.py`, `EXP-0016`).
8. **M2: reproduce from a rebuilt image** (`DISC-002`).
   > **MSHvSF:** the file was re-encoded and zero-filled to its original size,
   > then written in place with regenerated EDC/ECC; only its sectors changed;
   > builds are deterministic; a cold boot showed the marker (`EXP-0019`).
   > **Verify on XvSF:** the sector mode, whether same-size in-place
   > replacement suffices, and whether the loader checks sizes (see the
   > declared-length pitfall).
9. **Font** (`FONT-001`, `LAYOUT-001`, `FONT-003`).
   > **MSHvSF:** a write breakpoint on the glyph staging cell halted in the
   > glyph routine, which revealed the font base pointer and format (block
   > table, size table, raw or two-stage-mask compressed cells). The font is
   > stored verbatim as `MEMFIX.PAC` entry 4, loaded into cart RAM
   > (`EXP-0020`, `EXP-0022`). A lossless unpack/repack proved the format model
   > (`EXP-0023`, `tools/text/font_pack.py`).
   > **Verify on XvSF:** find the glyph routine the same way, then find the
   > font on disc by byte identity with the decoded RAM image. Prove the
   > format by a byte-identical repack before adding anything.
10. **Latin glyphs** (`FONT-002`).
    > **MSHvSF:** ASCII `0x41-0x43` displays only as faint 8×8 glyphs;
    > full-width quote-style Latin `0x08E8-0x0925` displays well (`EXP-0021`).
    > **Verify on XvSF:** which Latin codes exist and how they look on screen.
11. **Capacity route: pair glyphs** (`LAYOUT-001` Phase C, `FONT-003` Phase C).
    > **MSHvSF:** one 16-px cell holds a composed two-letter glyph. A same-size
    > repack added glyphs at free codes `0x00A8+` and emptied four kanji that a
    > census found in no record-shaped text (`EXP-0023`).
    > **Verify on XvSF:** free codes, sacrificable glyphs (census every text
    > surface first), and the font's byte budget.
12. **Offline renderer** (`RE-021`).
    > **MSHvSF:** `tools/text/quote_render.py` reproduces the screen from the
    > decoded table and font; a body-pixel matcher picks the shown record
    > (`EXP-0024`).
    > **Verify on XvSF:** the grid origin and pitch, from screenshots.
13. **Selection and forcing** (`RE-023`).
    > **MSHvSF:** a two-state search found the record pointer; a write
    > breakpoint on it found the index setter; the agent's `onhit` write right
    > after the setter forces any record from a post-KO checkpoint with no
    > input (`EXP-0025`). A second quote state exists, selected by an unknown
    > rule (`EXP-0036`).
    > **Verify on XvSF:** find the index and pointer; expect more than one
    > state; log the register that selects the state.
14. **M3: compiler** (`RE-022`, `RE-024`).
    > **MSHvSF:** `tools/text/caption_compiler.py` takes a JSON spec (lines as
    > text), allocates pair glyphs, repacks the font, re-encodes the files and
    > builds the image. All 16 records verified live by forcing
    > (`EXP-0026`, `tools/mednafen/verify_records.py`).
15. **Contexts and a second character** (`RE-025`, `RE-030`).
    > **MSHvSF:** the RAM table base moves with team slot; the file is the same
    > (`EXP-0027`). Ken worked through the same mechanism (`EXP-0028`).
    > **Verify on XvSF:** test the second team slot and a second character
    > before generalizing; resolve bases at runtime.

### Phase 3: Systematic Win Quotes (M5)

1. **Census files against arcade slots** (`RE-041`).
   > **MSHvSF:** quote file `MCnn` holds arcade slot `nn`'s whole Japanese
   > block, byte-identical; 18 files ordinary, 5 irregular (`EXP-0034`,
   > `tools/reference/slot_census.py`).
   > **Verify on XvSF:** match every Saturn text file to arcade slots by byte
   > identity; list irregular files.
2. **Roster and exceptions** (`RE-043`): a user decision, recorded in
   `docs/coverage_exceptions.md` with evidence per file. MSHvSF excluded bosses,
   secret characters and Norimaro (rule 24).
3. **Pairing per character** (`RE-042`, `tools/reference/roster_pairing.py`).
4. **Capacity** (`RE-044`).
   > **MSHvSF:** the roster needed 405 distinct pairs against 248 free codes.
   > The user chose option A (reuse unseen-kanji codes in place) plus a greedy
   > per-line 0/1 alignment shift, giving 338 pairs (90 reused codes). The
   > alternative (raise the font's code count) was not tested.
   > **Verify on XvSF:** count distinct pairs before building; present the
   > options to the user.
5. **Build, review offline, verify a sample live** (`RE-045`, `RE-046`):
   read every render sheet; pick characters that cover each structural class
   (both publishers, both team slots, irregular files).
6. **Regression** (`RE-047`): add each confirmed build as a reference.

### Phase 4: Endings (M6-M8)

Do not start until win quotes are proven and generalized (MSHvSF rule 23).
Assume **nothing** from win quotes; re-derive each fact.

1. **Reach and observe** (`END-001`).
   > **MSHvSF:** the user lost to the final boss and continued; continuing led
   > back to character select and then the final stage (**SUPPORTED**, one
   > run). `session_recorder.py` captured rolling states, so moments the user
   > cannot pause on became checkpoints (`EXP-0037`).
   > **Verify on XvSF:** how to reach the ending repeatably.
2. **Renderer** (`END-002`).
   > **MSHvSF:** ending text is VDP1 sprites of byte-exact quote-font glyphs,
   > built by the same glyph routine. Proven by zeroing one VDP1 cell and
   > seeing exactly that glyph vanish (`EXP-0038`, `tools/text/glyph_match.py`,
   > `tools/mednafen/write_trial.py`).
   > **Verify on XvSF:** match ending glyph cells to the decoded font; if they
   > do not match, the endings use another font or path.
3. **Text in RAM** (`END-003`).
   > **MSHvSF:** the code-sequence search found live 19 × 2 records, loaded
   > with the final stage; single writes before the scene changed exactly one
   > cell (`EXP-0039`, `tools/text/code_search.py`).
4. **Disc source** (`END-004`, `END-007`).
   > **MSHvSF:** the post-boss dialogue is in the boss's LZSS quote file
   > (`MC13.PAC`); the pages are raw in `ME.PAC`. Write breakpoints from a
   > before-load state caught both writers. Marker edits loaded and showed
   > (`EXP-0040`, `EXP-0041`).
   > **Verify on XvSF:** trace both writers; do not expect the dialogue to
   > live where the pages do.
5. **Arcade reference** (`END-006`).
   > **MSHvSF:** the arcade has official English pages but does not translate
   > the four-box Japanese dialogue; it shows two generic partner lines. Forcing
   > the stage word and the boss vitality in MAME reaches any ending with no
   > play (`EXP-0042`, `tools/reference/arcade_ending_route.py`).
   > **Verify on XvSF:** what English exists for each ending surface, and a
   > no-play MAME route.
6. **Indexing** (`END-005`).
   > **MSHvSF:** pages follow the point character. Dialogue records are
   > `16 + 2·partner slot` (partner's lines) and `16 + 2·(26 + point slot)`
   > (point's reply); English uses the same indices. Predicted, then met, in
   > MAME (`EXP-0043`).
   > **Verify on XvSF:** pre-register predictions for two team combinations
   > and check them in MAME.
7. **One ending** (`END-010`, M7).
   > **MSHvSF:** blank dialogue records show an empty box (not skipped);
   > `0x0000` inserts a name at any cell; the name table and a one-byte
   > name-length table live in `MM.BIN`, loaded raw at boot. A first live run
   > showed a blank cell after "RYU" until the length table was matched
   > (`EXP-0044`).
   > **Verify on XvSF:** placeholder behaviour, where names live, and whether
   > a length table drives insertion.
8. **Layout** (`EXP-0045`).
   > **MSHvSF:** two identical records in a dialogue pair hand over with no
   > visible change, so one English line can fill both boxes' time.
   > **Verify on XvSF:** test with a RAM copy and a frame-by-frame capture
   > before offering the user this layout.
9. **Generalize** (`END-021`-`END-025`, M8): census and capacity
   (`EXP-0046`), name growth and a placeholder census (`EXP-0047`), one
   combined image with win quotes and endings (`EXP-0048`), a live sample
   (`EXP-0049`), and a coverage register (`END-025`,
   `tools/text/ending_coverage.py --built-track`).
   > **MSHvSF:** the name table is global, so English names appear inside
   > Japanese lines left for excluded characters (user accepted, `EXP-0047`).
   > Some arcade slots share page pointers (`END-025`).
   > **Verify on XvSF:** every placeholder and every shared pointer, before
   > choosing a roster.

### Phase 5: Capacity, Regression, Release

- **Capacity per image.**
  > **MSHvSF:** the combined image holds 501 pair glyphs, reusing 253 of 321
  > candidate kanji codes (`EXP-0048`); the font budget was 30,235 bytes
  > (`RE-044`). The pairs of already-verified tables are allocated first, so
  > their files stay byte-identical when more text is added.
  > **Verify on XvSF:** the budget, and a stable allocation order.
- **Regression.** `tools/regression/reference_builds.py` regenerates each spec
  from the local arcade ROM, rebuilds from the untouched image, and compares
  every hash; `--write-baseline` only with a recorded reason.
- **Release** (`REL-001`).
  > **MSHvSF:** only track 01 changed. `tools/disc/make_patch.py` checks the
  > source hashes, encodes twice for determinism, and round-trips with
  > `xdelta3 -d`. Flags `-e -9 -S none -A -f` (plain VCDIFF). Tested with
  > xdelta3 3.2.2, a user-style apply and a fresh clone. The patch is never
  > committed.
  > **Verify on XvSF:** which tracks change, and the image format the release
  > targets (the held rip is ISO plus MP3, not BIN/CUE).

## Names and Localization Policy

> **MSHvSF:** the Saturn is the Japanese release; its art, labels and voice use
> Vega, Gouki and Mech-Gouki, while the arcade English uses BISON, AKUMA and
> Cyber-Akuma. The user chose, in order (2026-10-25): VEGA in the name table,
> then "Mech-Gouki" in text, then GOUKI "for now". This is **provisional**
> (`LOC-001`); the later direction is two parallel name variants (`LOC-002` to
> `LOC-006`). Implemented as `NAME_OVERRIDES` and `TEXT_OVERRIDES` in
> `tools/text/official_endings.py`, applied to every text surface
> (`EXP-0049`, `EXP-0050`, `docs/localization_plan.md`).

**Verify on XvSF:**

- Inventory every name the Saturn shows as art (select, VS, life bar, win
  screen, ending labels) and every name the announcer speaks, from recorded
  sessions.
- List where the arcade English names differ from those.
- Put the options (Saturn names, US names everywhere, US names in text only)
  to the user with their costs before building text.
- Keep overrides in one place in the generator so a reversal is a rebuild.

## The User's MSHvSF Localization Decisions

Ask the user to confirm or change each one for XvSF. Do not carry them over
silently.

| Decision | Date | Where recorded |
| --- | --- | --- |
| Win quotes: official arcade English, paired by game logic (record `k` → entry `k & 7`), even though each line appears twice; no meaning-based retranslation | 2026-10-24 | `data/translations/README.md` |
| Roster: 17 characters; bosses, secret characters and Norimaro excluded; Armored Spider-Man shares Spider-Man's English | 2026-10-24 | `docs/coverage_exceptions.md` |
| Capacity: reuse unseen-kanji codes in place, plus per-line alignment | 2026-10-24 | `research_log.md` (`RE-044`) |
| Endings: official English pages; the arcade's two English partner lines for the post-boss dialogue | 2026-10-24 | `data/translations/README.md` |
| Dialogue layout: each English line whole, one block per speaker (first split across boxes, `EXP-0044`; revised, `EXP-0045`) | 2026-10-24 | `data/translations/README.md` |
| English names in the name table, with the length table matched; English names accepted inside the remaining Japanese lines | 2026-10-24 | `data/translations/README.md`, `EXP-0047` |
| The Saturn's names (VEGA, GOUKI, Mech-Gouki), provisional; parallel variants requested | 2026-10-25 | `docs/localization_plan.md` |
| Release: xdelta3, patch kept local, rebuild README | 2026-10-25 | `release/README.md` |
| Later requests: the credits font for captions (`FONT-010`), English-only "PRESS START" (`UI-001`) | 2026-10-25 | `TASKS.md` |

## Tools and How Each Was Validated

All are MSHvSF tools, in the MSHvSF repository. Reuse the code; re-validate it
on XvSF. Anything that hard-codes an MSHvSF address, offset or file name must be
parameterized or rewritten.

| Tool | Purpose | Validation (MSHvSF) | Portability |
| --- | --- | --- | --- |
| `vendor/mednafen/patches/0001-agent-interface.patch` | File-based command protocol: read/write memory, breakpoints in halt or log mode, `onhit` writes after a hit, pause/step/frames, save/load state to a path, screenshots | V1-V4 (`docs/mednafen_agent_interface.md`): reads equal the validated extractor at the same instant; writes round-trip; logged hits match manual halts | Game-independent; re-run V1-V4 on XvSF |
| `tools/mednafen/agent.py` | Python client; holds an exclusive `flock` per command so several clients share one emulator | unit tests; used by every live experiment since `EXP-0025` | Game-independent |
| `tools/mednafen/session_recorder.py` | Rolling screenshots (1 s) and states (3 s), frame-named, ring-buffered, while the user plays | `EXP-0037`: checkpoints re-picked from the screenshots replayed as named | Game-independent |
| `tools/mednafen/replay_state.py` | Load a state on any image and capture steps, breakpoint logs or a halt dump | `EXP-0036`: isolated a BIOS reset to one file | Game-independent; see the replay limits |
| `tools/mednafen/write_trial.py` | Apply writes at a checkpoint, screenshot, report whether writes survived | `EXP-0038`, `EXP-0039` controls | Game-independent |
| `tools/mednafen/ko_capture.py`, `verify_records.py` | One human KO, then forced records, checked by pointer, screen, font, table and display buffer | `EXP-0025`, `EXP-0026`, `EXP-0036` | MSHvSF addresses inside |
| `tools/mednafen/ending_driver.py` | While the user works the menus: force the stage word to the final stage, then zero the boss vitality, then stop writing | `EXP-0044`, `EXP-0049` | MSHvSF addresses inside |
| `tools/memory/mcs_extract.py` | Regions from Mednafen Saturn states | `DBG-012` byte-identical to debugger dumps (cart unvalidated) | Re-validate |
| `tools/memory/diff.py`, `tools/text/search.py`, `pattern_search.py`, `code_search.py` | Diff dumps; search encodings, equality patterns, code sequences | synthetic tests; `EXP-0011`, `EXP-0013`, `EXP-0039` | Game-independent |
| `tools/memory/vdp1_sprites.py`, `tools/text/glyph_match.py` | Walk VDP1 command lists, render sprites; match cells to font codes | `EXP-0012`, `EXP-0038` | VDP1 is platform; colors and fonts are not |
| `tools/disc/iso9660.py`, `patch_image.py`, `hash_source.py` | ISO walk; same-size in-place rebuild with EDC/ECC; source hashing | `EXP-0016`, `DISC-002` (all source sectors regenerate exactly) | Platform-level; check XvSF's image format |
| `tools/disc/pac_lzss.py`, `pac_patch.py` | MSHvSF's LZSS container | `DISC-001`, `EXP-0036` | MSHvSF format; do not assume on XvSF |
| `tools/text/font.py`, `font_pack.py`, `pair_font.py`, `glyph_patch.py` | Decode, repack, add pair glyphs | byte-identical repack (`EXP-0023`) | MSHvSF format |
| `tools/text/caption_compiler.py` | Spec to image (schemas v1-v3: tables, raw files, fields, byte patches, placeholders) | `EXP-0026` through `EXP-0050` | Structure reusable; formats are MSHvSF's |
| `tools/text/official_captions.py`, `official_endings.py` | Specs from the local arcade ROM, with a Japanese-identity check before writing | `EXP-0033`, `EXP-0044`, `EXP-0048` | MSHvSF ROM layout |
| `tools/reference/*` (`mame_audit`, `cps2_text`, `mame_timeline.lua`, `arcade_route`, `arcade_ending_route`, pairing and census tools) | Arcade identity, text, scripted MAME runs, pairing | `REF-008` to `REF-010`, `EXP-0029` to `EXP-0034`, `EXP-0042` | MAME parts reusable; ROM offsets are MSHvSF's |
| `tools/regression/reference_builds.py`, `tools/disc/make_patch.py` | Rebuild references and compare; build the release patch | `RE-047`, `REL-001` | Reusable with a new baseline |

### Emulator limits learned the hard way (MSHvSF)

- **State replay keeps old RAM.** A state holds machine memory, not the disc. A
  replay on another image reads later files from the new image, which makes it
  a cheap test of a modified file loaded after the state (`EXP-0036`). But
  anything already resident stays old.
  > **MSHvSF:** the quote font loads after boot and stays in cart RAM, so a
  > replay on a font-changed image showed empty glyphs. Font changes need a
  > **cold boot** (`EXP-0044`).
  > **Verify on XvSF:** when each text asset loads and whether it is re-read.
- **Cart RAM.** The agent cannot write cart RAM (the `physical` space reads
  zeros there), and the stock debugger has no cart space (`EXP-0044`,
  `EXP-0007`).
- **Asynchronous pause.** After `loadstate`, the pause point varies, so
  separate launches differ in animation (1,865 px over idle fighters,
  `EXP-0038`). Compare inside the text box or by diff bounding box.
- **Replay steps drift.** `replay_state.py` steps are not exact frames; take
  timing from the live frame-named screenshots (`EXP-0037`).
- **Agent `read` length is decimal**, not hex (`EXP-0036` pitfalls).
- **`savestate` is refused while halted**; `PC` reads 0 when halted by `pause`
  (`docs/mednafen_agent_interface.md`).
- **Breakpoints on hot words** fire in initialization loops first; arm them
  late or filter by PC (`EXP-0025` Part 2).

## Pitfalls and Disproven Ideas (MSHvSF)

Do not retry these on XvSF without a new reason; but each is MSHvSF-specific,
so a quick XvSF check of the cheap ones is fine.

| Idea or mistake | Outcome | Evidence |
| --- | --- | --- |
| The quote is fixed per checkpoint or matchup | **DISPROVEN** | `EXP-0009` |
| Quotes are "team-voiced" (from a joint portrait) | Wrong; the KO character's quote | `EXP-0009` correction |
| Shift-JIS quote text in WRAM at the quote screen | **DISPROVEN** | `EXP-0011` |
| Quote text in VDP2 | **DISPROVEN** | `EXP-0012` |
| Resident font as raw cells or 1 bpp masks | **DISPROVEN** (compressed) | `EXP-0013`, `EXP-0020` |
| The caption table stored verbatim on disc | **DISPROVEN** (LZSS) | `EXP-0017` |
| A name counter selects the quote | **DISPROVEN** by code reading | `research_log.md`, `EXP-0025` design |
| Unswapped save-state byte order | **DISPROVEN** | `EXP-0008` |
| Arcade win quotes are 8-bit ASCII; first punctuation mapping | Both wrong | `EXP-0029` |
| A shorter declared compressed length is harmless | Wrong: loading as an opponent sent the game to the BIOS; keep the original declared length and zero-pad | `EXP-0036` |
| A splice re-encode fits any file | `MC13` had 1 byte of slack; use a full re-encode | `EXP-0041` |
| State replay verifies a font change | Wrong; cold boot needed | `EXP-0044` |
| The boss vitality offsets work for ordinary fights (`--warmup-ko`) | Wrong; the user's team lost; option removed | `EXP-0049` |
| Fixed RAM addresses for a character's table | Wrong; bases move with team slot | `EXP-0027` |
| Forcing the MAME quote pointer changes both lines | Only line 2 changed | `RE-044` log |
| The first non-zero MAME pointer dump is the shown entry | Wrong; it persists; find the first change | `EXP-0030` |
| One MAME route works on every region set | Wrong; program ROMs differ | `EXP-0030` |
| A breakpoint at the US routine address works on the JP set | Silently did nothing | `EXP-0031` |
| Contact-sheet tile order equals frame order | Wrong (`ffmpeg` glob vs `ls`); use an explicit list and numeric sort | `EXP-0037` |
| Arithmetic in pre-registered pointers | One slip caught by observation; compute, don't hand-add | `EXP-0025` |
| New tests written over an existing test file | Overwrote it; restored from git | `REL-001` log |
| Shell: `cat > file` with no input; zsh `$L:f`; output outside `build/` | Hang; modifier expansion; refused by `patch_image` | `RE-046`, `RE-047` logs |

## Consolidated "Verify on XvSF" Checklist

Use this as the starting `TASKS.md` backlog for the XvSF project, one task per
line, in this order.

1. Preservation image, component hashes, release description.
2. Pinned emulator boots XvSF with the right cart; three cold boots.
3. States, debugger dumps, writes, write breakpoints; extractor validated.
4. Agent interface V1-V4 on XvSF.
5. Arcade sets identified, keyed, booting; English text located and decoded;
   on-screen confirmation in MAME.
6. Selection behaviour of the post-fight text from one checkpoint.
7. Renderer: VDP1 sprites or VDP2 tiles.
8. RAM text: encoding, then equality-pattern search; one live RAM edit (M1).
9. Disc source by write breakpoint on the RAM text; format; rebuild (M2).
10. Font routine, font location on disc, format proven by lossless repack.
11. Latin glyphs on screen; capacity route (pair glyphs or other).
12. Record pointer, index setter, forcing; all quote states.
13. Saturn-to-arcade identity and game-logic pairing; PS1 comparison.
14. Translation policy and GO from the user.
15. Compiler and forced verification for one character (M3), then two (M4).
16. File census, roster and exceptions, capacity, roster image (M5).
17. Endings, only after M5: reach, renderer, RAM, disc, arcade English,
    indexing, names and lengths, layout, census, combined image, coverage.
18. Names: art and voice inventory; user's policy.
19. Regression references; release patch and README.

## Changelog

- 2026-10-25: first version (`DOC-020`).
