# Dependency-Controlled Research Plan

This is an evidence gate, not a generic backlog. `AGENTS.md` is authoritative.
Statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and `REJECTED`.
At most one reverse-engineering experiment may be `IN_PROGRESS`.

## Current State

- **M4 completed on 2026-10-24** (`RE-030`, `EXP-0028` Phase B): Ken works
  through the same generalized mechanism, with all 32 Ryu and Ken records verified
  live from one image. M3 was completed on 2026-10-17.
- Reverse-engineering experiments in progress: none.
- **M6 started on 2026-10-24.** `END-001` is done (`EXP-0037`): the final-boss
  checkpoint is made, and Ryu's ending was observed (a post-boss dialogue plus
  three ending pages). `END-002` is done (`EXP-0038`): the ending text is VDP1
  sprites of byte-exact quote-font glyphs, built by the `FONT-001` routine
  from 16-bit codes. `END-003` is done (`EXP-0039`): the text is a live WRAM-L
  table of 19 × 2 code records with a `0x0000` name placeholder, loaded with
  `STAGE-08`. `END-004` is done (`EXP-0040`): the dialogue comes from LZSS
  `MC13.PAC` (the boss's file), and the pages from raw `ME.PAC`. The next tasks
  are:
  - `END-007` is done (`EXP-0041`): edited `ME.PAC`/`MC13` load from a derived
    image, and the page marker showed live;
  - `END-006` is done (`EXP-0042`): official English exists for Ryu's pages,
    but not for the four-box dialogue (the arcade English shows two generic
    partner lines);
  - `END-005` is done (`EXP-0043`): pages follow the point character. The
    dialogue is a partner pair (16 + 2·partner slot) plus a point pair
    (16 + 2·(26 + point slot)) in `MC13`; English uses the same indices.
- **M7 completed on 2026-10-24** (`END-010`, `EXP-0044`). Ryu's ending shows
  the official arcade English from a deterministic image built from the
  untouched source:
  - the three pages;
  - the two partner lines, for Ken and for Gouki;
  - the English names.

  It was verified live from a cold boot and pinned in the regression baseline
  (`end010`). At the user's request, the dialogue now shows each English line
  whole, one block per speaker (`EXP-0045`). Next is `END-020` (M8), now
  `READY`.
- **M8 completed on 2026-10-25** (`END-020`, `END-025`). Every roster ending
  (17 characters) shows the official arcade English, with English names, from
  one deterministic image built from the untouched source (`m8_roster`, track
  01 `2a5b26b7…`). That image also holds the M5 win quotes. The register of
  exclusions and accepted side effects is `docs/coverage_exceptions.md`
  (Endings). The remaining unknowns are in `docs/known_unknowns.md`.
  - `REL-001` is done (2026-10-25): an xdelta3 patch (`00c3906a…`, kept
    local) and `release/README.md`, reproduced from a fresh clone.
  - **New requests (2026-10-25):**
    - credits font for the captions: `FONT-010` (`READY`, high), then
      `FONT-011`;
    - US-name art and voice, and two name variants: `LOC-002` (`READY`,
      medium) to `LOC-006` (stretch);
    - player-2 prompt and "EASY" label in English only: `UI-001` and `UI-002`
      are done (`EXP-0053`): "JOIN IN" and "EASY" art copied from the game's
      own font. They are in the release image (`7a3917d1…`);
    - a cross-game agent playbook for XvSF: `DOC-020` (done,
      `docs/playbook_cross_game.md`).
  - `FONT-010` is done (`EXP-0051`): the credits font is quote-font codes
    `0x1E0`-`0x25F`. `FONT-011` is done (`EXP-0052`): captions use the credits
    font in gold, and the release patch is the gold image (`e213140a…`).
- M8 history: started on 2026-10-24 (`END-020`). `END-021` is done (`EXP-0046`): all
  17 roster endings match the arcade reference and fit. One font holds the
  endings plus the M5 win quotes (454 pairs). `END-022`'s experiments are done
  (`EXP-0047`): names can grow, and the length table controls the insertion.
  The user accepted English names inside the Japanese text a roster image
  leaves (31 sites, almost all for excluded characters). `END-023` is done
  (`EXP-0048`): one deterministic image holds the M5 win quotes (files
  unchanged) and all 17 roster endings (`m8_roster`). `END-024` is done
  (`EXP-0049`): six sampled endings and a win quote verified live. At the
  user's request the dictator is VEGA. `END-026` is done (`EXP-0050`):
  following the Saturn's art, the text also uses GOUKI and Mech-Gouki
  (`build/end027`, `2a5b26b7…`). This is provisional: the final naming policy
  is `LOC-001` (`docs/localization_plan.md`). `END-025` is done: coverage,
  regression, and unknowns.
- **M5 completed on 2026-10-24** (`RE-040`). The user lifted M6's blocker the
  same day. Low-priority win-quote follow-ups
  (`RE-048` to `RE-050`, `REL-001`) and the arcade font comparison (`REF-012`)
  are recorded in the backlog.
- M5 history: its breakdown was defined on 2026-10-24 as
  `RE-041` to `RE-047`. The next task is `RE-041` (offline census of quote files
  against arcade slots), done 2026-10-24 (`EXP-0034`): file `nn` = arcade slot
  `nn`. `RE-043` is done (17-character roster, `docs/coverage_exceptions.md`). Next
  was `RE-042`, now done (all 17 paired; placeholders dropped). `RE-044` is done:
  the roster spec fits, with 90 reused kanji codes and per-line alignment.
  `RE-045` is done (`EXP-0035`): the deterministic roster image is reviewed
  offline. `RE-046` is done (`EXP-0036`): Cyclops, Zangief, Captain America, and
  Dhalsim pass all 16 records live on `build/re046_roster`, after a load reset was
  fixed (keep the declared PAC length). `RE-047` is done: the reference images
  rebuild against a committed hash baseline (`docs/regression_report.md`).
  **M5 was completed on 2026-10-24.**
- `REF-008` is done (2026-10-23): the arcade sets are identified, and regional
  claims are recorded. `EXP-0029` decoded the arcade English win quotes straight
  from ROM data (Ryu = slot 9, `SUPPORTED`). `REF-009` is done (2026-10-24): all
  three sets verify and boot in MAME 0.289. `REF-010` is done (2026-10-24,
  `EXP-0030`): the decoded arcade quotes match the screen, and Ryu's are slot 9.
  `REF-003`, `REF-004`, and `REF-006` are done (2026-10-24, `EXP-0031`). Saturn Ryu
  record `k` pairs with official arcade English entry `k & 7` by game logic.
  DOC-007, DOC-008, and REF-005 are done (`EXP-0032`: PS1 English equals the
  arcade's). `GATE-TRANSLATION` passed on 2026-10-24 (user GO). `TR-001` is done
  (`EXP-0033`): an image showing all 16 Ryu win quotes in official English was
  verified live.
- Hard gate: no M1 experiment may begin until `GATE-M0` is `DONE`.

## Milestones

| ID | Required outcome |
| --- | --- |
| M0 | Mednafen runs; MSHvSF boots with 4 MB RAM cartridge; fightpad, screenshots, save states, debugger, documentation, and Python tooling work. |
| M1 | One Ryu post-fight caption is visibly modified in live Saturn RAM. |
| M2 | The same Ryu caption is reproducibly modified from an untouched source image. |
| M3 | Multiple Ryu captions are handled programmatically. |
| M4 | A second fighter works through the same generalized mechanism. |
| M5 | Ordinary post-fight captions can be localized systematically. |
| M6 | Investigation of ending text begins only after M5. |
| M7 | One Ryu ending is localized. |
| M8 | A general ending-localization pipeline works. |
| M9 | Special cases such as Norimaro may be investigated. |

## Phase A: Repository And Environment

### ENV-001 - Create Python uv project

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Define an installable Python 3.12+ project managed by uv.
- **Rationale:** Research tools need a reproducible runtime and dependency declaration.
- **Acceptance criteria:** `pyproject.toml` declares the project, Python floor, build backend, and development dependency group; `uv.lock` is committed after synchronization.
- **Outputs:** `pyproject.toml`, `uv.lock`.
- **Notes:** Lockfile generation is verified under `ENV-004` before session closeout.

### ENV-002 - Implement setup_venv.sh

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001.
- **Blockers:** None.
- **Objective:** Create or update all project dependency groups with uv.
- **Rationale:** Developers must not need manual environment activation.
- **Acceptance criteria:** The executable script locates the repository, checks for uv, runs `uv sync --all-groups`, and is safely rerunnable.
- **Outputs:** `setup_venv.sh`.
- **Notes:** Runtime success is recorded by `ENV-004`.

### ENV-003 - Implement invenv.sh

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001.
- **Blockers:** None.
- **Objective:** Execute arbitrary commands in the project environment.
- **Rationale:** Every Python tool and check must use one documented entry point.
- **Acceptance criteria:** The executable script locates the repository, checks for uv, requires a command, delegates through `uv run`, and preserves its exit code.
- **Outputs:** `invenv.sh`.
- **Notes:** Runtime success is recorded by `ENV-004`.

### ENV-004 - Add linting, formatting, typing, and tests

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001, ENV-002, ENV-003.
- **Blockers:** None.
- **Objective:** Validate the scaffold with pytest, Ruff, and strict mypy.
- **Rationale:** File presence alone does not prove a usable research instrument.
- **Acceptance criteria:** Setup, tests, lint, format check, typing, wrapper executability, and a synthetic source-hash CLI exercise succeed; exact versions and outcomes are logged.
- **Outputs:** Tests, tool configuration, `research_log.md` verification entry.
- **Notes:** mypy is the selected type checker. Validation commands and versions are recorded in `SESSION-0001`.

### ENV-005 - Create repository documentation skeleton

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Establish concise scope, protocol, architecture, emulator, technical, evidence, and unknowns documents.
- **Rationale:** Future sessions need stable locations for facts, questions, and procedure.
- **Acceptance criteria:** All documentation named in `README.md` exists, speculation is excluded from discoveries, and significant-experiment guidance exists.
- **Outputs:** `README.md`, `AGENTS.md`, `docs/`, `research/experiments/README.md`.
- **Notes:** A skeleton does not complete the reference-collection tasks below.

### ENV-006 - Create .gitignore and copyrighted-data safeguards

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Keep copyrighted, machine-local, and generated binary artifacts out of version control.
- **Rationale:** Legal safety and source immutability are part of reproducibility.
- **Acceptance criteria:** Ignore rules cover images, BIOS, extracted contents, screenshots, save states, dumps, traces, emulator binaries/configuration, derived builds, caches, and secrets while allowing metadata and synthetic fixtures.
- **Outputs:** `.gitignore`, artifact guidance.
- **Notes:** Staged files must still be audited at every substantial closeout.

### ENV-007 - Record immutable source identities

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-004.
- **Blockers:** None.
- **Objective:** Record filename, size, SHA-256, and description for the BIOS and every source-image component without modifying them.
- **Rationale:** All later observations must identify their exact immutable inputs.
- **Acceptance criteria:** The checked source-hash utility records every component; before/after hashes match; only metadata is tracked.
- **Outputs:** Source identity records; ignored or external source files.
- **Notes:** BIOS files were supplied and recorded in `docs/mednafen.md`. The MSHvSF
  Saturn JP image is copied to ignored `local/disc_images/mshvsf_saturn_jp/`, and its
  CUE plus all twelve BIN components are recorded in
  `references/mshvsf/saturn_jp/README.md`. Multi-file images require one record per
  component, not only the descriptor.

## Phase B: Documentation Corpus

### DOC-001 - Collect Sega Saturn architecture references

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None.
- **Objective:** Identify authoritative references for the Saturn architecture and initial memory regions.
- **Rationale:** Platform claims must be traceable to sources rather than prior assumptions.
- **Acceptance criteria:** Citations, versions/editions, access dates, relevant sections, and supported claims are recorded; uncertain or conflicting claims remain explicit.
- **Outputs:** `docs/references.md`, `docs/saturn_memory_map.md`.
- **Notes:** `SESSION-0003` records source identities, exact sections, validation,
  conflicts, and reproduction commands. No manuals are committed.

### DOC-002 - Collect SH-2 references

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None.
- **Objective:** Identify authoritative SH-2 architecture, instruction, and debugging references.
- **Rationale:** Future execution tracing requires precise processor semantics.
- **Acceptance criteria:** Sources and task-oriented summaries cover only verified concepts needed for debugger work, with citations and remaining unknowns.
- **Outputs:** `docs/references.md`, `docs/code_map.md`.
- **Notes:** `SESSION-0004` records source identities, task-oriented SH-2 and
  hardware-debugging summaries, verification, and the explicit boundary against
  inferring target addresses or Mednafen behavior.

### DOC-003 - Collect Saturn CD/filesystem references

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None.
- **Objective:** Collect references for Saturn boot media, CD block behavior, ISO9660, tracks, and filesystem handling.
- **Rationale:** M2 needs documented disc semantics before extraction or rebuilding.
- **Acceptance criteria:** Authoritative citations and concise summaries distinguish filesystem facts from target-image observations.
- **Outputs:** `docs/references.md`, `docs/disc_layout.md`.
- **Notes:** `SESSION-0005` records official source identities, task-oriented format
  and CD-block summaries, the scope-specific multisession distinction, and
  verification. No target data was inspected.

### DOC-004 - Collect Mednafen debugger documentation

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None.
- **Objective:** Record documented stock debugger commands and limits for the selected-version evaluation.
- **Rationale:** Capability hypotheses should come from exact upstream documentation and then be experimentally tested.
- **Acceptance criteria:** Source provenance and concise command summaries are recorded; documented capability is not mislabeled as observed capability.
- **Outputs:** `docs/references.md`, `docs/mednafen.md`.
- **Notes:** `SESSION-0006` records upstream page and candidate-archive identities,
  the documented command baseline and cautions, verification, and the boundary
  against claiming selected-build behavior. Version selection remains `EMU-001`.

### DOC-005 - Collect relevant Saturn localization projects

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None.
- **Objective:** Catalog legally usable projects that can inform specific Saturn localization experiments.
- **Rationale:** Prior work may suggest tools or tests but cannot establish MSHvSF structures.
- **Acceptance criteria:** Each entry records provenance, license, exact relevant technique, and limits on transferability.
- **Outputs:** `docs/references.md`, `references/projects/` notes where useful.
- **Notes:** `SESSION-0007` records immutable revisions, archive identities,
  license scopes, bounded techniques, excluded leads, and verification. No project
  behavior is transferred to MSHvSF.

### DOC-006 - Collect known MSHvSF English quote references

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** Runtime evidence may later require legal access to official releases.
- **Objective:** Identify candidate authoritative sources for official arcade and PS1 English post-fight text.
- **Rationale:** The target wording must not be invented or taken from an unsourced transcription.
- **Acceptance criteria:** Provenance and reliability are recorded; no Japanese-English correspondence is asserted without evidence.
- **Outputs:** `docs/references.md`, permitted reference notes.
- **Notes:** `SESSION-0008` records two original US arcade revisions, the distinct
  modern Capcom reissue, the US PlayStation fingerprint, source reliability, and
  verification. Selecting and verifying one Ryu quote remains `REF-001` through
  `REF-005` work.

### DOC-007 - Collect known XvSF Saturn translation/research references

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None for bibliography research.
- **Objective:** Catalog relevant predecessor research for later, question-driven comparison.
- **Rationale:** XvSF can suggest a discriminating experiment but cannot answer an MSHvSF question by analogy.
- **Acceptance criteria:** Sources, provenance, licenses, potential relevance, and strict non-transfer assumptions are recorded.
- **Outputs:** `docs/references.md`, permitted reference notes.
- **Notes:** Do not modify or begin comparative analysis of XvSF here.
- **Evidence (2026-10-24):** `docs/references.md` "X-Men vs. Street Fighter (Saturn)
  and Related Prior Art".
  - No XvSF Saturn translation or internals research exists publicly.
  - The sources found are recorded with dates, reliability, and licenses (none
    grant reuse). Blocked sites are listed, and no block was bypassed.
  - Non-transfer is stated, and three experiment ideas are recorded as ideas only.

### DOC-008 - Create concise internal Markdown summaries for agent use

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DOC-001, DOC-002, DOC-003, DOC-004, DOC-005, DOC-006, DOC-007.
- **Blockers:** None.
- **Objective:** Summarize task-relevant facts with links back to authoritative references.
- **Rationale:** Agents need concise, citable context rather than bulk documents.
- **Acceptance criteria:** Summaries identify supported claims, citations, conflicting evidence, and unresolved questions without overstating confidence.
- **Outputs:** Updated technical files under `docs/`.
- **Notes:** Keep discovery claims separate from platform/reference summaries.
- **Evidence (2026-10-24):** New `docs/agent_briefing.md`, linked from `README.md`.
  - It is a cited summary with separate sections for project discoveries (Saturn
    and arcade) and platform/reference facts.
  - It also lists conflicting or corrected evidence, open questions, tools, and
    pitfalls.
  - Stale status lines in `docs/text_system.md`, `docs/code_map.md`, and
    `docs/saturn_text_hacking.md` now point to their confirmed entries. One
    overstatement was caught in review: Ken's live check is still on hold.

## Phase C: Stock Mednafen Bootstrap

### EMU-001 - Select and document exact Mednafen version

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None.
- **Objective:** Select one unmodified upstream release/revision for evaluation.
- **Rationale:** Build and runtime evidence require exact provenance.
- **Acceptance criteria:** Upstream URL, version/revision, retrieval date, rationale, expected host requirements, and license are recorded without claiming runtime success.
- **Outputs:** `docs/mednafen.md`, `vendor/mednafen/README.md`.
- **Notes:** `SESSION-0010` selects the unmodified `1.32.1` source archive, records its
  release provenance, archive hash, GPL-2 license, expected Saturn host requirements,
  and macOS-arm64 source-build rationale. Selection does not authorize source
  modification. Build identity and runtime behavior remain `EMU-002` onward.

### EMU-002 - Download/build stock Mednafen

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-001, DOC-004.
- **Blockers:** None.
- **Objective:** Acquire and build pristine Mednafen with reproducible commands.
- **Rationale:** Runtime observations must be tied to a known binary.
- **Acceptance criteria:** Source identity, download/build commands, tool versions, options, binary hash, and smoke-test result are recorded; source and binaries remain ignored.
- **Outputs:** Local stock source/build; provenance and commands in `vendor/mednafen/README.md`.
- **Notes:** `SESSION-0011` built the unmodified `1.32.1` archive on macOS arm64,
  recorded the exact toolchain, dependencies, configure/build commands, binary hash,
  and isolated `-help` smoke test. No local patch was applied. Source and binaries
  remain ignored.

### EMU-003 - Create project-local Mednafen configuration strategy

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-002.
- **Blockers:** None.
- **Objective:** Isolate runtime configuration, saves, screenshots, and logs from user-global state.
- **Rationale:** Hidden global settings make observations irreproducible.
- **Acceptance criteria:** Launch and reset procedures use an ignored local root; sanitized stable settings can be recorded; secrets and unstable identifiers are excluded.
- **Outputs:** `docs/mednafen.md`, ignored `local/mednafen/`.
- **Notes:** `SESSION-0012` confirmed the project-local base directory, loaded settings,
  runtime save-data placement, diagnostic-log placement, and cold relaunch procedure.
  Snapshot and interactive save-state hotkeys were not automated in this host session
  and remain separate verification work.

### EMU-004 - Boot MSHvSF Saturn successfully

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003, ENV-007.
- **Blockers:** None.
- **Objective:** Reach a documented normal game screen using the recorded inputs.
- **Rationale:** Later evidence is invalid without a reproducible baseline boot.
- **Acceptance criteria:** Exact command/configuration and observed endpoint are recorded; source hashes remain unchanged; local screenshot evidence and metadata are captured.
- **Outputs:** Experiment record, launch procedure, ignored screenshot.
- **Notes:** Boot alone does not verify cartridge or input.

### EMU-005 - Verify 4 MB RAM cartridge configuration

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-004.
- **Blockers:** None.
- **Objective:** Confirm the required 4 MB cartridge operates in the research configuration.
- **Rationale:** Memory observations must use the correct runtime hardware model.
- **Acceptance criteria:** A controlled observation validates cartridge operation; setting, expected result, observed result, and uncertainty are recorded.
- **Outputs:** Experiment record, validated configuration guidance.
- **Notes:** `EXP-0002` forced `ss.cart=extram4` for three cold observations.
  Each run reported `T-1238G`, `Cart: 4MiB Extended RAM`, and reached the
  rendered MSHvSF title screen. Source hashes matched before and after. This
  confirms the tested runtime path, not direct cartridge RAM read/write behavior.

### EMU-006 - Configure fightpad

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003, EMU-004.
- **Blockers:** None.
- **Objective:** Map one identified physical fightpad to Saturn controls locally.
- **Rationale:** Manual checkpoint capture depends on reliable controls.
- **Acceptance criteria:** Device and connection are documented without unnecessary identifiers; D-pad, A/B/C/X/Y/Z, and Start mappings are configured. L/R are explicitly out of scope for this task because the selected Mednafen device models did not provide usable bindings and the target checkpoint work does not require them.
- **Outputs:** Ignored local configuration, mapping draft in `docs/mednafen.md`.
- **Notes:** The physical device is an 8BitDo M30 in wired macOS mode. macOS presents
  it to SDL as `PS4 Controller`; Mednafen records joystick ID
  `0xecccd365fc40db2f0006000c00010000`. The ignored local profile preserves keyboard
  fallbacks and maps the required Saturn controls. Runtime shortcut validation remains
  in `EMU-007`.

### EMU-007 - Document fightpad mapping

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-006.
- **Blockers:** None. The Mac host has no reliable physical Pause/Break key; this
  shortcut is explicitly recorded as unavailable in the experiment evidence.
- **Objective:** Validate and document every required input in game.
- **Rationale:** Configuration labels do not prove intended runtime behavior.
- **Acceptance criteria:** Expected and observed behavior are recorded for all mapped controls and useful emulator shortcuts, including save/load, screenshot, pause, frame advance, and slot selection where available.
- **Outputs:** Verified mapping table and input experiment record.
- **Notes:** `EXP-0004` records user-observed in-game behavior for the physical M30
  required controls and available shortcuts. Retained keyboard fallbacks are out of
  scope. Pause/Break was unavailable on the Mac host and was not inferred from a
  conflicting temporary binding.

### EMU-008 - Verify screenshot capture

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-004, EMU-005.
- **Blockers:** None.
- **Objective:** Capture reproducible visual evidence from a described scene.
- **Rationale:** M1 and M2 require before/after evidence.
- **Acceptance criteria:** Capture action, state, configuration, filename, size, hash, and local storage are recorded; image remains ignored.
- **Outputs:** Screenshot experiment, procedure, ignored evidence.
- **Notes:** A screenshot does not prove binary provenance.

### EMU-009 - Verify save/load states

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-005, EMU-007, EMU-008.
- **Blockers:** None.
- **Objective:** Repeatedly return to an equivalent documented checkpoint.
- **Rationale:** Differential experiments need controlled starting conditions.
- **Acceptance criteria:** Save/load actions, slot/path, hashes, timing caveats, and at least two repeat observations are recorded; state files remain ignored and are not diffed as RAM.
- **Outputs:** Save-state experiment and checkpoint procedure.
- **Notes:** `EXP-0006` confirmed two cold save/load cycles using slots 0 and 1.
  The title/menu checkpoint returned after a visible mode-selection transition.
  State files remain ignored and were not diffed as RAM; animated title timing is
  recorded as a caveat.

### EMU-010 - Verify debugger access

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-005, EMU-009.
- **Blockers:** None.
- **Objective:** Enter, operate, and exit the stock interactive debugger against MSHvSF.
- **Rationale:** M1 requires developer-level memory inspection and controlled writes.
- **Acceptance criteria:** Exact invocation/actions demonstrate pause/resume and read-only inspection; source/configuration identities are linked; no caption conclusion is drawn.
- **Outputs:** Debugger smoke-test experiment.
- **Notes:** `EXP-0007` confirmed `Option+D` debugger entry, CPU-view `S`/`R`
  pause/resume, the listed memory-editor address spaces, and repeatable dumps of
  High/Low Work RAM and VDP1/VDP2 VRAM during a frame-advance pause. The stock
  editor has no cartridge-RAM address space. No caption conclusion is drawn.

### EMU-011 - Document debugger workflow

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-010.
- **Blockers:** None.
- **Objective:** Record exact stock actions for memory reads/writes, dumps, registers, stepping, and breakpoints as available.
- **Rationale:** Later experiments must be reproducible by another session.
- **Acceptance criteria:** Each command is tied to the tested version and observed outcome; unsupported or unreliable actions are explicit.
- **Outputs:** `docs/mednafen.md` capability/runbook update.
- **Notes:** Documentation is not evidence until actions are tested. `EXP-0014`
  confirmed `L` write, `D` read-back, revert, register display, and a CPU write
  breakpoint (fired at PC `0x060AF8C6`). The runbook is in `docs/mednafen.md`.
  Untested: read breakpoints, PC breakpoints, edit mode, and pokes. The CPU-view
  memory pane is a `0xAA` stub.

### EMU-012 - Determine stock Mednafen memory-workflow sufficiency

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-011, DBG-011.
- **Blockers:** None.
- **Objective:** Decide whether repeatable memory dump/read/write workflows needed for M1 are satisfactory.
- **Rationale:** Custom emulator work is prohibited until a concrete stock limitation is demonstrated.
- **Acceptance criteria:** A capability matrix records each requirement, experiment, result, reliability, and blocker; conclusion is `SUPPORTED` by observed workflows.
- **Outputs:** Sufficiency decision in `docs/mednafen.md` and `research_log.md`.
- **Notes:** Insufficiency does not itself authorize modification.

- **Evidence:** capability matrix in `docs/mednafen.md` (2026-10-17). Stock is
  sufficient for manual M1/M2 work and insufficient for agent-driven M3
  experiments (`SUPPORTED`).
### EMU-020 - Evaluate agent automation limitations

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-012.
- **Blockers:** None (`EMU-012` done).
- **Objective:** If needed, document current versus required capability, why stock is inadequate, smallest modification, maintenance cost, and alternatives.
- **Rationale:** Any custom interface must solve a demonstrated problem with minimal scope.
- **Acceptance criteria:** The review either rejects modification or proposes one minimal, explicitly authorized follow-up; upstream provenance and patch workflow requirements are stated.
- **Outputs:** `docs/mednafen_agent_interface.md`, decision log.
- **Notes:** No Mednafen edit occurs in this task.

### EMU-021 - Implement and validate the minimal agent interface

- **Status:** `DONE`
- **Milestone:** M3 (tooling)
- **Dependencies:** EMU-020 and the user's authorization (2026-10-17).
- **Blockers:** None.
- **Objective:** Build the authorized frontend patch so the agent can drive
  memory, breakpoints, halts, states, and screenshots without manual typing.
- **Acceptance criteria:**
  - The patch is tracked and reproduces the built tree.
  - The stock tree and binary are unchanged.
  - V1-V3 pass (done 2026-10-17).
  - V4: a breakpoint log of a real quote transition matches `EXP-0025` Part 1
    (PC `060AF724`/`060AF728`, R1 `060F249E`).
- **Outputs:** `vendor/mednafen/patches/0001-agent-interface.patch`,
  `tools/mednafen/agent.py`, `tools/mednafen/ko_capture.py`,
  `docs/mednafen_agent_interface.md`.

## Phase D: Reference Text

- **Evidence:** `docs/mednafen_agent_interface.md` (2026-10-17). It proposes a
  minimal frontend-only patch, which the user explicitly authorized on
  2026-10-17. Implementation is tracked in `EMU-021`.
- **Evidence:** V4 passed (2026-10-17). The log-mode breakpoint run matched the
  manual halts, and a no-input replay from the post-KO checkpoint was exact.
  See `docs/mednafen_agent_interface.md`.

### REF-001 - Choose initial Ryu post-fight quote

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DOC-006, EMU-007, REF-007.
- **Blockers:** None. `EXP-0009` observed nine Ryu quotes (Ryu landed every KO)
  under a joint Ryu/Ken portrait; slots 3 and 4 are usable pre-KO checkpoints.
- **Objective:** Select one ordinary Ryu caption with reproducible Japanese and official English contexts.
- **Rationale:** M1 needs one fixed subject rather than broad quote work.
- **Acceptance criteria:** Selection rationale, release contexts, route, and unresolved correspondence questions are recorded without inventing a match.
- **Outputs:** Structured draft under `data/translations/`.
- **Notes:** Ryu remains preferred unless evidence justifies another fighter.
  Selected `ryu_q3` (`data/translations/ryu_post_fight_q3.json`) on technical
  grounds: it appeared against both opponents in `EXP-0009`. The record states the
  route and the open REF-004 correspondence questions; no wording or match is
  asserted. `EXP-0010` could not reproduce Q3 from state A, so the working subject
  moved to Q10 (`data/translations/ryu_post_fight_q10.json`).

### REF-002 - Capture Japanese Saturn screenshot

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** REF-001, EMU-008, EMU-009.
- **Blockers:** None.
- **Objective:** Capture the selected Japanese caption in a deterministic scene.
- **Rationale:** Exact visible evidence anchors transcription and memory analysis.
- **Acceptance criteria:** Release/run/state identity, capture method, image hash, and visible context are recorded; screenshot remains ignored.
- **Outputs:** Local screenshot and tracked metadata.
- **Notes:** Do not infer storage from appearance. `EXP-0010` captured Q10 from
  slot-7 reloads (`-0037.png`, `-0038.png`) and its save-time thumbnail.

### REF-003 - Transcribe Japanese text

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** REF-002.
- **Blockers:** None.
- **Objective:** Record exactly what is visibly displayed, including line breaks and punctuation.
- **Rationale:** Encoding searches require a reviewable transcription.
- **Acceptance criteria:** Transcription is independently reviewed against evidence; ambiguities and unreadable glyphs remain explicit.
- **Outputs:** Updated translation record.
- **Notes:** Transcription does not imply Shift-JIS encoding.
- **Evidence (2026-10-24, `EXP-0031`):**
  - All 16 Ryu records were transcribed from the offline render. A separate
    agent's blind transcription is identical on all 32 lines.
  - Every line's cell count, blank cells, hiragana, and punctuation were
    machine-checked against the codes, with 0 mismatches.
  - All 16 records were also seen on the arcade `mshvsfj` screen (byte-identical
    table).
  - Q10 (record 8) is in `data/translations/ryu_post_fight_q10.json`. The full set
    stays in the ignored `local/ref003/`.

### REF-004 - Identify corresponding arcade English quote

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** REF-003, DOC-006, REF-009.
- **Blockers:** None.
- **Objective:** Establish the official arcade English counterpart using contextual evidence.
- **Rationale:** The project uses official text where available.
- **Acceptance criteria:** Exact text, formatting, release provenance, context, evidence, and correspondence confidence are recorded; unsupported matches are rejected.
- **Outputs:** Updated translation record and reference evidence.
- **Notes:** Matching character alone is insufficient evidence. The user reports
  that US and EU arcade ROMs with English text are available locally. Record their
  identities against the MAME catalog before use. The sets (EU, US, and JP) are now
  in `local/arcade_roms/mshvsf/`; see `references/mshvsf/arcade/README.md`. Their
  audit and regional-difference documentation is `REF-008`. `EXP-0029` decoded the
  arcade English win quotes from ROM data. Ryu's quotes are slot 9, block
  `0x21BA20`, and are capture-backed by `REF-010` (`EXP-0030`). Pairing them with
  Saturn Japanese captions is still open. Because Saturn quote
  selection varies after the KO (`EXP-0009`), correspondence may need memory-level
  evidence, such as a quote index, rather than a reproduced context.
- **Evidence (2026-10-24, `EXP-0031`):** The correspondence is index-based and
  `CONFIRMED`:
  - The Saturn Ryu table is byte-identical to the arcade Japanese Ryu table.
  - The arcade selection code maps a 16-way index `k` to English slot 9 entry
    `k & 7`, using a remap table checked by breakpoint and forced-index tests.
  - So Saturn records `k` and `k + 8` pair with official English entry `k & 7`.
    Record 8 (Q10) pairs with entry 0, recorded in the Q10 translation record.
  - The pairing metadata is `data/text/ryu_arcade_pairing.json`.
  - The English entries are separate rewrites, not translations. Whether to use
    the paired English or translate by meaning is a policy decision for
    `GATE-TRANSLATION`.

### REF-005 - Record PS1 English equivalent if useful

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** REF-004.
- **Blockers:** None. The legal `SLUS-00793` image is now held and matches the
  Redump fingerprint (`REF-011`; `local/disc_images/mshvsf_ps1_us/`).
- **Objective:** Record the official PS1 wording and differences when it adds useful evidence.
- **Rationale:** A secondary rendering can clarify language but not Saturn implementation.
- **Acceptance criteria:** Provenance, exact text/context, comparison, and uncertainty are recorded, or a documented decision explains why it is not useful.
- **Outputs:** Updated translation record.
- **Notes:** Do not infer shared binary structures.
- **Evidence (2026-10-24, `EXP-0032`):**
  - The US PS1 `DAT/SELECT.BIN` holds all 26 arcade English slot blocks,
    byte-identical in little-endian code order. Ryu's slot 9 is at `0x1150C`.
  - So Ryu's PS1 English equals the arcade English (Q10 record updated). This
    adds no new wording evidence.
  - The PS1 display was not captured (documented as not useful here).
  - Two extra PS1-only English blocks (likely secret characters) are deferred to
    `SPECIAL-001`.

### REF-006 - Capture Japanese arcade material if useful

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** REF-004.
- **Blockers:** None.
- **Objective:** Use Japanese arcade evidence only if it discriminates competing quote correspondences.
- **Rationale:** Additional reference work should answer a specific question.
- **Acceptance criteria:** The question, provenance, context comparison, result, and remaining uncertainty are recorded, or the task is `REJECTED` as unnecessary.
- **Outputs:** Reference experiment and translation-record update if run.
- **Notes:** This is optional evidence, not a gate when unnecessary.
- **Evidence (2026-10-24, `EXP-0031`):** The question was which English line the
  game shows for each Saturn record.
  - Japanese arcade material settled it: the `mshvsfj` table identity, its 16
    on-screen records, and the region-shared selection routine with its remap.

### REF-007 - Observe win-quote selection behavior

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-009.
- **Blockers:** None.
- **Objective:** Determine empirically what changes which post-fight win quote
  appears. Candidates include replay timing, finisher, opponent, the winning
  teammate, and stage.
- **Rationale:** Differential checkpoints need two different quotes from the same
  winner in otherwise similar scenes. Selection behavior is unknown and must not
  be assumed.
- **Acceptance criteria:**
  - From one pre-KO checkpoint, at least five replays vary only KO timing or
    finisher, and each records winner, opponent, quote screenshot hash, and quote
    identity.
  - At least one controlled change of opponent or stage is recorded the same way.
  - The observed selection behavior is stated with a confidence label.
- **Outputs:** Experiment record, ignored screenshots and states, and
  `research_log.md` entry.
- **Notes:** The project's planned team is Ryu/Ken. Record which teammate's
  portrait and quote appear. `EXP-0009` disproved a fixed-at-checkpoint quote: one
  pre-KO state gave up to six quotes. Neither the kill move nor the opponent alone
  determines the quote. Ryu/Ken wins show a joint portrait. Per the user, the quote
  belongs to whoever landed the KO (Ryu in every replay); this is untested for Ken.

### REF-008 - Document the local arcade ROM sets and their regional differences

- **Status:** `DONE`
- **Milestone:** M0 (reference documentation; no reverse engineering)
- **Dependencies:** DOC-006.
- **Blockers:** None.
- **Objective:** Before any arcade quote is captured, establish exactly what each
  local arcade set is and what text each one can be expected to contain.
- **Rationale:** The user supplied European, US, and Japanese sets
  (`references/mshvsf/arcade/README.md`). They may not hold the same quotes. The
  user has heard that only the Japanese set has Norimaro and secret-character
  quotes. If that is not documented first, a missing line could be misread as
  "no official English".
- **Acceptance criteria:**
  - Each set is audited against the pinned MAME 0.289 catalog: set name, title,
    version label, and per-member CRC-32 and SHA-1, with a scripted, reproducible
    command and its output.
  - Any extra file MAME needs, such as a key, is recorded or ruled out.
  - Regional content differences (characters, quote availability, language) are
    listed from cited sources. Each is labelled `HYPOTHESIS` until it is observed
    in a captured frame.
  - The text-bearing ROMs and encoding remain `UNKNOWN` unless a recorded
    experiment shows otherwise.
  - Follow-up capture tasks are proposed with the regions they need, and no
    capture is started here.
- **Outputs:** `references/mshvsf/arcade/README.md`, `docs/references.md`,
  `docs/known_unknowns.md`, and a `research_log.md` entry.
- **Notes:** Documentation only. Do not extract, translate, or modify Norimaro or
  secret-character content (`SPECIAL-001`, M9).
- **Evidence (2026-10-23):**
  - `tools/reference/mame_audit.py` checked every set against the pinned
    `cps2.cpp` (SHA-256 verified). Output: `references/mshvsf/arcade/mame0289_audit.json`.
  - Identities are `CONFIRMED`: `mshvsf` (Europe 970625), `mshvsfu`
    (USA 970827), and `mshvsfj` (Japan 970707). Each matches 20/21 files, has
    no unexpected files, and matches no other set.
  - Each zip lacks its 20-byte `.key` file. MAME later confirmed the refusal
    (`REF-009` notes).
  - Regional claims RC-1 to RC-6 are recorded as `HYPOTHESIS`, with sources, in
    `references/mshvsf/arcade/README.md` and `docs/references.md`. The TCRF arcade
    page was read from Wayback snapshot `20261011115711`, with user approval. It
    added RC-7 and RC-8.
  - Text location and form remain `UNKNOWN`.
  - Follow-up proposed: `REF-009`. Captures stay under `REF-004`, which also needs
    `REF-003`.

### REF-009 - Pin a MAME build and complete the arcade sets for capture

- **Status:** `DONE`
- **Milestone:** M0 (reference tooling; no reverse engineering)
- **Dependencies:** REF-008.
- **Blockers:** None. The user supplied the keys and `qsound.zip` on 2026-10-24.
  Agents must not download ROM or key files.
- **Objective:** Make the local European, US, and Japanese sets run in a pinned,
  recorded MAME build, so `REF-004` can capture English quotes.
- **Rationale:** Wording counts as evidence only from a captured frame of an
  identity-verified set (`docs/references.md`).
- **Acceptance criteria:**
  - MAME version, source or binary provenance, and SHA-256 are recorded.
  - Key file hashes match MAME 0.289, and `-verifyroms` output passes for all three
    sets.
  - Each set boots to its title screen, and a screenshot hash is recorded locally.
  - The missing `mshvsfu1` (USA 970625) needed by the capture protocol is either
    supplied and audited, or its absence is recorded as a limit.
- **Outputs:** `references/mshvsf/arcade/README.md`, `research_log.md` entry.
- **Notes:** Keys and ROMs stay in the ignored `local/arcade_roms/mshvsf/`.
- **Progress (2026-10-23):**
  - MAME 0.289 was installed with `brew install mame` (bottle
    `mame--0.289.arm64_tahoe`; `/opt/homebrew/Cellar/mame/0.289/bin/mame` SHA-256
    `6d40df87963c58cdd3857d203e186af854fea49ae03b2ab555e30ef1029636d9`;
    `mame -version` prints `0.289 (unknown)`). It matches the audited driver
    version.
  - `mame -rompath local/arcade_roms/mshvsf -verifyroms mshvsf mshvsfu mshvsfj`
    reports 0 of 3 sets OK. Each lacks `<set>.key` and `dl-1425.bin` (24,576
    bytes).
- **Evidence (2026-10-24):**
  - The key and `dl-1425.bin` hashes match MAME 0.289. They are copied to the
    ignored `local/arcade_roms/mshvsf/<set>/` and `qsound.zip`; the zips are
    unchanged.
  - `-verifyroms`: 3 of 3 OK.
  - All three sets boot headless to the title screen
    (`tools/reference/mame_snap_frames.lua`). Frame-3000 snapshot hashes are in
    `references/mshvsf/arcade/README.md`. A repeat `mshvsfu` run reproduced them
    bit for bit.
  - No `mshvsfu1` is held; that is recorded as a limit.

### REF-010 - Confirm the arcade win-quote slot mapping on screen

- **Status:** `DONE`
- **Milestone:** M0 (reference text; no reverse engineering)
- **Dependencies:** REF-009, EXP-0029.
- **Blockers:** None.
- **Objective:** Turn the `EXP-0029` ROM-data quotes into capture-backed official
  English. Confirm that slot order follows the name list (Ryu = slot 9), and that
  displayed lines match the decoded blocks.
- **Rationale:** Data in ROM is not proof of display. Wording becomes evidence only
  from a captured frame.
- **Acceptance criteria:**
  - In `mshvsfu`, at least two Ryu win quotes and one quote from a different slot
    are captured. Each matches its decoded block line for line, or the differences
    are recorded.
  - The capture records MAME version, settings (including language and region),
    route, and screenshot hashes.
  - The European set is compared on at least one of the same quotes.
- **Outputs:** Experiment record, `references/mshvsf/arcade/README.md`, and
  translation-record updates under `REF-004`.
- **Notes:** Keep Norimaro and secret-character captures out of scope
  (`SPECIAL-001`).
- **Evidence (2026-10-24, `EXP-0030`):**
  - Scripted MAME routes (`tools/reference/arcade_route.py` and
    `mame_timeline.lua`) reached Ryu's win screen on `mshvsfu`.
  - Slot 9 quotes 6 and 7 matched line for line. RAM `0xFF249C` held each entry's
    address, and the snapshots are deterministic.
  - The European `mshvsf` showed quote 6 pixel-identically.
  - Winners in slots 5, 6, 11, 12, 13, and 16 matched the name list.
  - Settings: default EEPROM (2 coins per credit; Easy and Normal timed out),
    English.

### REF-011 - Intake second arcade batch, PS1 image, and XvSF material

- **Status:** `DONE`
- **Milestone:** M0 (reference provenance; no reverse engineering)
- **Dependencies:** REF-008.
- **Blockers:** None.
- **Objective:** Identify and record every newly supplied reference file before use.
- **Rationale:** `AGENTS.md` rule 2 requires identity records before research.
- **Acceptance criteria:** Each file is copied unchanged to an ignored path, with
  SHA-256 recorded and identity checked against MAME 0.289 or Redump where
  possible. Gaps are explicit.
- **Outputs:** `references/mshvsf/arcade/README.md`,
  `references/mshvsf/arcade/v2_manifest.json`,
  `references/mshvsf/ps1_us/README.md`, `references/xmvsf/*/README.md`,
  `references/xmvsf/arcade/manifest.json`.
- **Evidence (2026-10-24):**
  - All 11 MAME `mshvsf` sets match by SHA-1. 6 of 11 verify in MAME after
    reusing held keys (including `mshvsfu1`); 5 lack `mshvsfa.key`,
    `mshvsfb.key`, or `mshvsfh.key`.
  - The MSHvSF US PS1 image matches Redump 12632 exactly.
  - 11 XvSF arcade zips match MAME 0.289 under older set names; no XvSF keys are
    held.
  - The XvSF US PS1 image matches MAME `psx.xml`. The JP EX Edition is not in
    `psx.xml` (identity unverified).
  - The XvSF Saturn file is a lossy rip (ISO plus MP3 audio) whose header reads
    `T-1226G V1.002` (Doukonban).
  - Follow-up (2026-10-24): five user-supplied XvSF keys match MAME 0.289. With
    copies under 0.289 names (`local/arcade_roms/xmvsf_mame0289/`), 10 of 11 XvSF
    sets verify (only `xmvsfb.key` is missing), and `xmvsfu` and `xmvsfjr2` boot.
  - The Saturn rip's data track holds all 236 files intact. A Redump image is
    needed only if an experiment needs verified identity or emulation.
- **Notes:** XvSF material is reference-only (rules 13 and 25). An MSHvSF PS1
  image is a PlayStation port, and its structures are not Saturn facts (rule 14).

## Phase E: Checkpoints And Memory Analysis

### DBG-001 - Capture state A before fight end

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** REF-001, EMU-009.
- **Blockers:** None. `EXP-0009` slots 3 and 4 are candidate pre-KO states but
  lack screenshots and reload records.
- **Objective:** Save a reproducible checkpoint shortly before the fight ends.
- **Rationale:** State A supplies the pre-caption comparison baseline.
- **Acceptance criteria:** Route, timing, run/configuration, save hash, screenshot metadata, and two reload observations are recorded.
- **Outputs:** Ignored save/screenshot and tracked checkpoint metadata.
- **Notes:** The compressed save state is not a RAM dump.

### DBG-002 - Capture state B after KO/before caption

- **Status:** `BACKLOG`
- **Milestone:** M0
- **Dependencies:** DBG-001.
- **Blockers:** None. Deferred by `EXP-0010`; revisit if the C-set comparison fails.
- **Objective:** Capture the transition before the caption is fully displayed, if practical.
- **Rationale:** An intermediate state may distinguish loading from display changes.
- **Acceptance criteria:** A repeatable state and timing are recorded, or evidence documents why it is impractical and authorizes the three-state strategy.
- **Outputs:** Checkpoint metadata and local evidence, or documented rejection.
- **Notes:** Do not force a noisy checkpoint merely to satisfy four-state nomenclature.

### DBG-003 - Capture state C with caption fully visible

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-001.
- **Blockers:** State A is unavailable.
- **Objective:** Save a stable checkpoint with the target caption fully visible.
- **Rationale:** This is the primary M1 mutation checkpoint.
- **Acceptance criteria:**
  - Scene identity, timing, save hash, screenshot metadata, and two reload
    observations are recorded.
  - A same-quote control state (C1′), replayed from state A, is captured the same
    way.
  - When `REF-007` shows how, a different-quote state (C2) from the same winner is
    also captured.
- **Outputs:** Ignored save/screenshot and tracked checkpoint metadata.
- **Notes:** This capture supplies the screenshot for `REF-002`. `REF-003`
  transcribes it, so transcription follows capture rather than gating it.
  `EXP-0010` used A = slot 5, C1 = slot 7 (Q10), C1′ = slot 0, C2 = slot 6 (Q8),
  and C2b = slot 8 (Q11).

### DBG-004 - Capture state D after caption disappears

- **Status:** `BACKLOG`
- **Milestone:** M0
- **Dependencies:** DBG-003.
- **Blockers:** None. Deferred by `EXP-0010`; revisit if the C-set comparison fails.
- **Objective:** Capture a repeatable checkpoint immediately after caption disappearance.
- **Rationale:** Disappearing data can help rank runtime candidates.
- **Acceptance criteria:** State, timing, hash, screenshot metadata, and repeatability are recorded; if impractical, the three-state fallback is justified.
- **Outputs:** Checkpoint metadata and local evidence, or documented rejection.
- **Notes:** Checkpoint practicality is an experimental result.

### DBG-005 - Capture screenshots for each checkpoint

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-001, DBG-003. (DBG-002 and DBG-004 were deferred to
  `BACKLOG` by `EXP-0010`.)
- **Blockers:** None. `EXP-0010` records save-time thumbnail hashes for A, C1, C1′,
  C2, and C2b.
- **Objective:** Tie every used checkpoint to visible evidence.
- **Rationale:** Dump comparisons need scene and timing context.
- **Acceptance criteria:** Each retained state has screenshot filename, size, SHA-256, capture action/order, and run identity; binaries remain ignored.
- **Outputs:** Local screenshots and tracked evidence manifest.
- **Notes:** Rejected optional states need no fabricated screenshot.

### DBG-006 - Create save-state memory-region extractor

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-004, EMU-010.
- **Blockers:** None.
- **Objective:** Script repeatable acquisition of defined Saturn memory regions by
  parsing stock Mednafen 1.32.1 save states. Regions are WRAM-L, WRAM-H, 4 MiB
  cartridge RAM, VDP1 VRAM, and VDP2 VRAM.
- **Rationale:** `EXP-0007` showed that the stock debugger can dump only through
  hand-typed in-window prompts, and that it exposes no cartridge-RAM space. Save
  states contain these regions and can be processed without manual steps.
- **Acceptance criteria:**
  - The state layout is implemented from cited `state.cpp` behavior.
  - Region names, sizes, and element widths are checked, and outputs default to an
    ignored path and never overwrite inputs.
  - Raw Saturn-order files are emitted with a JSON manifest (input hash, region,
    base address, size, SHA-256).
  - Synthetic tests, ruff, and mypy pass.
- **Outputs:** `tools/memory/mcs_extract.py`, tests, usage documentation.
- **Notes:** Extracted data is not trusted until `DBG-012` validates each region.
  The tool exists with 11 synthetic tests and parses the real `EXP-0007` state.

### DBG-012 - Validate save-state extractor against debugger dumps

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-006, EMU-010.
- **Blockers:** None.
- **Objective:** Test whether extracted regions equal stock debugger dumps of the same
  paused instant.
- **Rationale:** `AGENTS.md` permits extracted data only for regions validated byte
  for byte.
- **Acceptance criteria:**
  - Using the `EXP-0007` slot-2 state and its paused dumps, each of WRAM-H, WRAM-L,
    VDP1 VRAM, and VDP2 VRAM is compared and the result recorded.
  - Byte-order hypotheses are tested explicitly, not assumed.
  - Cartridge RAM's validation status is stated (no stock debugger dump exists).
- **Outputs:** `EXP-0008`, `research_log.md`, and `docs/discoveries.md` entries for
  confirmed regions.
- **Notes:** A match confirms extraction only, not caption meaning. `EXP-0008`
  confirmed WRAM-H, WRAM-L, VDP1 VRAM, and VDP2 VRAM byte for byte. The unswapped
  order is disproven. Cartridge RAM remains `HYPOTHESIS`.

### DBG-007 - Dump WRAM-L for each state

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-005, DBG-012.
- **Blockers:** Checkpoints and validated extraction are unavailable.
- **Objective:** Export `0x00200000-0x002FFFFF` identically from every retained state.
- **Rationale:** Stable raw dumps, not compressed save files, support comparison.
- **Acceptance criteria:** Every dump has expected/actual size, SHA-256, exact command/action, checkpoint linkage, and repeat acquisition; binaries remain ignored.
- **Outputs:** Local WRAM-L dumps and tracked metadata.
- **Notes:** Validate the supplied range against collected platform references before interpreting it.

### DBG-008 - Dump WRAM-H for each state

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-005, DBG-012.
- **Blockers:** Checkpoints and validated extraction are unavailable.
- **Objective:** Export `0x06000000-0x060FFFFF` identically from every retained state.
- **Rationale:** Both initially prioritized work-RAM regions must be tested before expansion.
- **Acceptance criteria:** Every dump has expected/actual size, SHA-256, exact command/action, checkpoint linkage, and repeat acquisition; binaries remain ignored.
- **Outputs:** Local WRAM-H dumps and tracked metadata.
- **Notes:** No subrange is presumed to contain captions.

### DBG-009 - Create memory diff tooling

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-004, DBG-007, DBG-008.
- **Blockers:** Validated paired dumps do not exist.
- **Objective:** Report contiguous changed/unchanged ranges and byte counts in human-readable and JSON forms.
- **Rationale:** Structured results are more reproducible than per-byte terminal output.
- **Acceptance criteria:** Equal-size/range validation, base addresses, input hashes, deterministic contiguous regions, optional unchanged ranges, JSON schema, and synthetic tests are implemented.
- **Outputs:** `tools/memory/` diff tool and tests.
- **Notes:** Results report facts, not candidate meaning.

### DBG-010 - Create binary/Shift-JIS search tooling

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-004. (`REF-003` gates claims from a search, not the
  tool; dependency amended in `EXP-0011`.)
- **Blockers:** None.
- **Objective:** Search exact byte patterns and user-specified encoded strings in dumps/files.
- **Rationale:** Shift-JIS is the first hypothesis, not a built-in conclusion.
- **Acceptance criteria:** Tool supports raw patterns, explicit encodings including Shift-JIS, multiple/no matches, base address, JSON output, input hashes, hexdump context, and synthetic tests.
- **Outputs:** `tools/text/` search tool and tests.
- **Notes:** Entropy/candidate ranking is added only when a demonstrated experiment needs it.

### DBG-011 - Compare checkpoint memory dumps

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-007, DBG-008, DBG-009, DBG-010.
- **Blockers:** Dumps and analysis tools are unavailable.
- **Objective:** Compare C1 vs C2 (different quote) and C1 vs C1′ (same-quote noise control) first, then A->B->C->D where useful, and run the first Shift-JIS search hypothesis.
- **Rationale:** Controlled temporal differences can rank candidate caption representations.
- **Acceptance criteria:** One significant experiment records exact inputs/hashes, one hypothesis, comparisons/searches, predicted and actual results, stable versus noisy observations, conclusion, and next discriminating experiment.
- **Outputs:** Experiment record, JSON summaries, `research_log.md` update.
- **Notes:** A match is at most `SUPPORTED` until a controlled visible mutation confirms causality.
  `EXP-0011` found no Shift-JIS quote fragments in WRAM (`DISPROVEN`). It ranked
  quote-dependent, time-stable candidates: WRAM-L 16-bit sequential entries and a
  WRAM-H high-entropy block at `0x06014CB5-0x0601677B`. The next step is a VRAM
  comparison (`DBG-012`'s validated regions).

### DBG-013 - Compare VDP VRAM across quote checkpoints

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-011, DBG-012.
- **Blockers:** None.
- **Objective:** Locate quote-dependent, time-stable bytes in VDP1 and VDP2 VRAM
  for C1, C1′, C2, and C2b. Test whether the `EXP-0011` WRAM-L 16-bit entries index
  those VRAM tiles.
- **Rationale:** `EXP-0011` disproved Shift-JIS text in WRAM, and its WRAM-L
  entries are consistent with text rendered into tiles. `AGENTS.md` allows VRAM
  expansion with this recorded rationale.
- **Acceptance criteria:** One experiment records inputs and hashes, one hypothesis,
  control-excluded diffs, the predicted and actual results, and the next
  discriminating experiment.
- **Outputs:** Experiment record and `research_log.md` entry.
- **Notes:** No meaning is assigned without a controlled test. `EXP-0012`: VDP2
  VRAM is identical across quotes (`DISPROVEN`). The quote is drawn by VDP1 sprites
  (color word `0x61E0`) from per-character 16x16 4 bpp glyph cells that are
  byte-identical across quotes for shared characters (`SUPPORTED`).

### DBG-014 - Locate the glyph font and quote character codes

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DBG-013.
- **Blockers:** None.
- **Objective:** Find where the 128-byte glyph cells come from (a font in WRAM, or
  in cart RAM, which is unvalidated). Derive candidate character codes from glyph
  indices, and test whether the Q10, Q8, and Q11 code sequences occur in memory.
- **Rationale:** Per-character glyph reuse implies an upstream character sequence,
  which is the representation a translation must change.
- **Acceptance criteria:** One experiment records exact glyph byte searches, the
  font hypothesis, code derivation, sequence searches across quote states, and the
  predicted and actual results.
- **Outputs:** Experiment record and `research_log.md` entry.
- **Notes:** A sequence match is at most `SUPPORTED` until a mutation test (M1).
  `EXP-0013`: no resident font was found. Quotes are 38-cell records of 16-bit codes
  in a WRAM-L table (Q10 at `0x0020940C`), with the current quote copied to WRAM-H
  `0x060ED80A` (`SUPPORTED`).

## M0 Gate

### GATE-M0 - Confirm environment and checkpoint prerequisites

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001, ENV-002, ENV-003, ENV-004, ENV-005, ENV-006, ENV-007, EMU-001, EMU-002, EMU-003, EMU-004, EMU-005, EMU-006, EMU-007, EMU-008, EMU-009, EMU-010, EMU-011, REF-001, REF-002, REF-007, DBG-001, DBG-003, DBG-005, DBG-006, DBG-007, DBG-008, DBG-009, DBG-010, DBG-011, DBG-012, DBG-013, DBG-014.
- **Blockers:** None. Accepted 2026-10-17: every dependency is `DONE`. States B and
  D are deferred (`EXP-0010`); REF-006 is optional. The tested write, revert, and
  breakpoint workflow (`EXP-0014`) leaves no known workflow blocker for M1
  evidence.
- **Objective:** Make an explicit go/no-go decision before the first live RAM mutation.
- **Rationale:** Partial setup must not be mistaken for permission to start M1.
- **Acceptance criteria:** Every dependency is `DONE`; optional `REF-006`, state B, and state D have either evidence or documented rejection/fallback; no unresolved workflow blocker can invalidate M1 evidence.
- **Outputs:** M0 acceptance entry and updated current state.
- **Notes:** Do not waive failed criteria to advance the milestone.
  **Amended 2026-10-15 at the user's direction:** the gate now covers only the
  technical prerequisites for a live RAM mutation (`RE-012`): the debugger
  workflow (`EMU-011`) plus validated extraction and checkpoints. Reference and
  documentation tasks (DOC-007, DOC-008, REF-003, REF-004, REF-005) moved to
  `GATE-TRANSLATION`. EMU-012 and EMU-020 no longer gate M1. They remain required
  before any Mednafen modification (`AGENTS.md` rule 16). B and D are deferred to
  `BACKLOG` per `EXP-0010`, and REF-006 is optional. See the `research_log.md`
  entry for the decision.

### GATE-TRANSLATION - Confirm reference and translation prerequisites

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** DOC-007, DOC-008, REF-003, REF-004, REF-005.
- **Blockers:** None.
- **Objective:** Make an explicit go/no-go decision before any task writes or
  proposes English replacement text.
- **Rationale:** The source quote must be reviewed and the official English must be
  established before translation work. They are not needed to test whether a RAM
  location drives the display.
- **Acceptance criteria:** Every dependency is `DONE`. Optional `REF-006` has
  evidence or a documented rejection.
- **Outputs:** Gate acceptance entry.
- **Notes:** Created 2026-10-15 by splitting the original GATE-M0.
- **Gate acceptance (2026-10-24):**
  - The user's decision is **GO**, in their words: "Pass GATE-TRANSLATION: go.
    Record the acceptance and allow Ryu's captions to use the paired official
    English."
  - Checked at acceptance: DOC-007, DOC-008, REF-003, REF-004, and REF-005 are all
    `DONE`; optional REF-006 has evidence (`EXP-0031`).
  - Scope: Ryu's win-quote captions may now carry English replacement text, under
    the policy below.
  - Other characters still need their own pairing verification first. Endings and
    special cases remain gated (`END-001`, `SPECIAL-001`).
- **Policy decision (user, 2026-10-24):** Saturn win-quote record `k` uses the
  official arcade English entry `k & 7`, the line the arcade shows in the same
  selection state (`EXP-0031`). Each English line appears for two Saturn records
  (`k` and `k + 8`), even where the meanings differ.
  - The policy applies to Ryu now. Other characters follow it only after their
    table identity and remap are verified the same way.
  - `preferred_english` is filled from `arcade_us_text` now that the gate has
    passed (done for Q10).
  - Measured constraint: the paired English lines are up to 25 characters, and a
    Saturn line has 19 cells. Fitting them depends on the pair-glyph work
    (`LAYOUT-001`, `FONT-003`).

### TR-001 - Build Ryu's official-English win-quote captions

- **Status:** `DONE`
- **Milestone:** M3 follow-up. It applies the confirmed Ryu caption pipeline to
  approved text; no new mechanism is investigated.
- **Dependencies:** GATE-TRANSLATION, RE-022, RE-024, FONT-003, REF-004.
- **Blockers:** None.
- **Objective:** Produce a derived image in which each Ryu record `k` displays
  official arcade English entry `k & 7` (`EXP-0031` pairing, gate policy).
- **Rationale:** This is the first real-text use of the pipeline, and the gate has
  passed for Ryu.
- **Acceptance criteria:**
  - The caption spec maps all 16 records to their paired entries and keeps record
    0's `{P}` placeholder handling explicit.
  - `caption_compiler.py --capacity` passes, with the pair-glyph and font budget
    recorded.
  - A fresh image builds deterministically from the untouched source.
  - All 16 records are verified live (forced records, `verify_records.py`).
  - Line-wrapping choices for lines longer than 19 cells are recorded against the
    arcade's own line breaks.
- **Outputs:** Caption spec, build manifest, experiment record, and translation
  records.
- **Notes:**
  - Arcade lines are up to 25 characters; a Saturn line has 19 cells.
  - Decide before committing whether the spec, which holds 8 official English
    lines, is "minimal text" under `data/translations/README.md`, or stays local
    with only hashes committed.
  - The Ken work (`RE-030`, M4) stays on hold until resumed.
- **Evidence (2026-10-24, `EXP-0033`):**
  - The spec is generated from the local arcade ROM by
    `tools/text/official_captions.py`. Only the tool and hashes are committed (spec
    SHA-256 `aa7fa863…04eb`). This resolves the "minimal text" question.
  - Arcade line breaks are kept and centred in whole blank cells; no wrapping was
    needed (two characters per cell).
  - Capacity: 95 pairs in 248 free codes, 3,669 bytes. The build is deterministic
    (track 01 `2941a9c5…`).
  - All 16 records were verified live after one user KO, IoU 1.0.
  - Supporting changes: `.` → `0x08AB` and `,` → `0x08AC` in `pair_font.py` and
    the schema. `verify_records.py` now accepts code-identical screen ties.

## Gated Reverse Engineering

### RE-012 - Identify and modify runtime buffer for one Ryu quote

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** GATE-M0.
- **Blockers:** None. `GATE-M0` was accepted on 2026-10-17.
- **Objective:** Identify the runtime representation responsible for the selected Ryu caption and visibly change it with one controlled RAM mutation.
- **Rationale:** This is the minimum causal proof linking runtime bytes to the caption.
- **Acceptance criteria:** Candidate range is identified; exact original/modified bytes and address are recorded; mutation changes the intended visible caption while unrelated content is assessed; before/after screenshots and deterministic checkpoint are recorded; the result repeats from a clean checkpoint; experiment, log, and confirmed discovery are updated.
- **Outputs:** `research/experiments/EXP-NNNN/`, local evidence, `research_log.md`, `docs/discoveries.md`.
- **Notes:** Do not claim whether bytes are source text, glyph indices, or an intermediate buffer without a separate experiment.
  Candidates from `EXP-0013`: the Q10 record at WRAM-L `0x0020940C` (76 bytes,
  resident before the KO), and the per-screen buffer at WRAM-H `0x060ED80A`.
  Mutation pre-registered in `EXP-0015`: line-1 cells 0-2 of all 15 table records
  set to `0801 0803 0805`, with the prediction that `あいう` is shown whichever
  quote appears. **Result:** `CONFIRMED` in three of three patched runs that
  selected a patched record (Q8 twice, Q5 once); both controls were unmodified. M1
  was reached on 2026-10-17. The table is 16 records from `0x002091AC`; the first
  holds a `0000` partner-name placeholder (`HYPOTHESIS`).

### DISC-001 - Trace confirmed Ryu runtime caption to disc source

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** RE-012.
- **Blockers:** None. M1 was confirmed by `RE-012` / `EXP-0015`.
- **Objective:** Determine what populates the confirmed runtime bytes and identify the source file, offset/structure, and transformations.
- **Rationale:** A RAM mutation is not a reproducible disc localization.
- **Acceptance criteria:** Controlled tracing links runtime data to source; pointers, lengths, compression, checksums, and alignment are tested as applicable; all factual offsets/bytes and uncertainty are recorded.
- **Outputs:** Source-trace experiment and confirmed documentation where warranted.
- **Notes:** A string-like disc match alone is insufficient. Plan, one hypothesis
  at a time:
  1. `EXP-0016` / `DISC-010`: track and ISO 9660 inspection.
  2. `EXP-0017`: verbatim search for the 1,216-byte table and its records.
  3. If (2) is negative, `EXP-0018`: write-breakpoint trace of the table load from
     a pre-match checkpoint.

  Known so far: the table is absent at the title screen and present, identical, in
  every in-fight state. `EXP-0017` (`DISPROVEN`): the table is not stored verbatim
  on disc, and plain Shift-JIS/EUC/UTF-16 fragments were not found. WRAM-H
  `0x06094FD8` holds the only pointer to it. Next: `EXP-0018` (live trace; needs a
  pre-load checkpoint and the user). `EXP-0018` (`CONFIRMED`): the table is
  LZSS-compressed in `MC09.PAC` (stream at `0x18`, length `0x620D`, output
  `0xB548`), decoded to WRAM-L `0x00200000` when Ryu is picked. Table = decoded
  offset `0x91AC`. Decoder: `tools/disc/pac_lzss.py`.

### DISC-010 - Document source disc data track and ISO 9660 layout

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** ENV-007, DOC-003.
- **Blockers:** None.
- **Objective:** Measure the track 01 sector format and ISO 9660 directory of the
  untouched source, and build reusable read-only tooling for it.
- **Rationale:** Any disc offset found for the quote table must map to a named file
  extent before patching. `docs/disc_layout.md` records no measurements yet.
- **Acceptance criteria:**
  - Sector validation, PVD fields, and the file list (path, extent LSN, length,
    hash) are recorded with tool version, command, and source hashes, unchanged
    before and after.
  - `tools/disc/iso9660.py` has synthetic tests.
- **Outputs:** `EXP-0016`, `tools/disc/iso9660.py`, and `docs/disc_layout.md`
  findings.
- **Notes:** Extracted contents stay in ignored `research/extracted_files/`.
  `EXP-0016`: 192,346 valid Mode 1 sectors; a flat ISO 9660 filesystem with 414
  non-interleaved files; the file list is in
  `references/mshvsf/saturn_jp/iso9660_files.json`.

### DISC-002 - Reproduce the M1 marker from a patched disc

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** DISC-001.
- **Blockers:** None.
- **Objective:** Rebuild a derived image from the untouched, identity-verified source
  into `build/`, with `MC09.PAC` re-encoded so its quote table carries the M1
  marker (line-1 cells 0-2 = `0801 0803 0805`, all 16 records). A cold boot of the
  derived image must reproduce `あいう` in Ryu's win quotes.
- **Rationale:** M2 proves a deterministic source-to-visible-output pipeline. The
  M1 marker isolates the pipeline (LZSS re-encoding, PAC header, sector EDC/ECC, and
  ISO placement) from translation questions.
- **Acceptance criteria:**
  - **Source safety.** The tool validates source hashes, never overwrites
    originals, and writes only under `build/`.
  - **Byte records.** For every change, the decoded offset, original and modified
    codes, and resulting PAC/LSN/sector changes are recorded.
  - **Round trip.** Re-encoding round-trips (`decode(encode(x)) == x`), and no match
    reaches before the output start.
  - **Sector integrity.** Rebuilt sectors have regenerated EDC/ECC, validated by
    the same routine that reproduces every original sector's EDC/ECC.
  - **No collateral changes.** All other files and sectors are byte-identical to
    the source.
  - **Determinism.** Two builds produce identical hashes.
  - **Runtime.** A cold boot of the derived image shows `あいう` in at least two
    independent Ryu wins, with screenshots. The original image is the control.
  - **Closeout.** Source hashes are unchanged, and tests, experiment, log, and
    discoveries are updated.
- **Outputs:** Encoder and image-patch tooling with synthetic tests, a local
  derived image and evidence, and tracked metadata and documentation.
- **Notes:** Amended 2026-10-17 at the user's direction: no English text is needed.
  English captions moved to `DISC-020` behind `GATE-TRANSLATION`. Do not generalize
  during M2. Design: `EXP-0019`. **Result:** `CONFIRMED` on 2026-10-17. The rebuilt
  image showed `あいう` in two independent Ryu wins; only MC09.PAC sectors changed.
  M2 reached.

### FONT-001 - Identify Latin glyphs in the quote font and their codes

- **Status:** `DONE`
- **Milestone:** M3 (prerequisite for `DISC-020`)
- **Dependencies:** DBG-013, DBG-014, DISC-001, EMU-011.
- **Blockers:** None.
- **Objective:** Determine whether the win-quote font contains Latin letters and
  digits, and which 16-bit codes select them.
- **Rationale:** English captions need displayable glyphs. No Latin glyph has been
  observed in any quote, and the font's location and code mapping are unknown.
- **Acceptance criteria:**
  - The font source is identified with its format and index↔code rule, validated
    on held-out known glyphs; or the experiment documents why the source could
    not be found and what limits that places.
  - At least one candidate Latin code is confirmed by a live display test with a
    control, or the font is shown to have no Latin glyphs.
- **Outputs:** `EXP-0020`, an ignored font atlas, a code table (factual metadata),
  and a `research_log.md` entry.
- **Notes:** Phase 1 is offline. Phase 1b and Phase 2 need the user at the
  keyboard.
  **Result (`EXP-0020`):**
  - The font is compressed in cart RAM (base pointer `0x0601D8E4`), decoded
    exactly by `tools/text/font.py`.
  - ASCII codes `0x41-0x43` display, but faint (8x8 gradient).
  - Full-width quote-style A-Z `0x08E8-0x0901`, a-z `0x0902-0x091B`, and 0-9
    `0x091C-0x0925` exist (atlas; display untested).
  - Code table: `data/text/font_codes.json`.

### FONT-002 - Confirm full-width Latin display in win quotes

- **Status:** `DONE`
- **Milestone:** M3 (prerequisite for `DISC-020`)
- **Dependencies:** FONT-001.
- **Blockers:** None.
- **Objective:** Confirm that the quote-style full-width Latin codes
  (`0x08E8-0x0925`) display correctly in Ryu's win quote.
- **Rationale:** ASCII glyphs display only faintly. The full-width set matches the
  quote style and is the candidate for English.
- **Acceptance criteria:** A live display with a control shows the predicted
  glyphs for uppercase, lowercase, and digit codes, with evidence and hashes
  recorded.
- **Outputs:** `EXP-0021` and a `data/text/font_codes.json` confidence update.
- **Notes:** `EXP-0021` (`CONFIRMED`): `RYUa1` was displayed solid and full-width on
  two records; the control was unchanged.

### LAYOUT-001 - Determine English capacity of win quotes

- **Status:** `DONE`
- **Milestone:** M3 (prerequisite for `DISC-020`)
- **Dependencies:** FONT-002, DISC-002.
- **Blockers:** None.
- **Objective:** Establish whether a win quote can show more than 38 full-width
  characters, through pair glyphs (two Latin letters per cell) or a layout change,
  and choose the English route.
- **Rationale:** Full-width Latin works (`EXP-0021`), but 2 × 19 cells may be too
  small for official English quotes.
- **Acceptance criteria:**
  - The font's disc source is located, or the experiment documents why not.
  - The layout constants and buffer limits are recorded.
  - At least one custom pair glyph displays in a live quote with a control, or a
    documented failure analysis is given.
  - A capacity model and a recommended route are recorded.
- **Outputs:** `EXP-0022` and its tooling.
- **Notes:** Phases A and B are offline; Phase C needs the user.
  **Result (`EXP-0022`):**
  - The font is `MEMFIX.PAC` entry 4 (load path confirmed).
  - A pair glyph (`Th`) displays from a rebuilt image (`CONFIRMED`).
  - Recommended route: pair glyphs, for 76 characters per quote.
  - Layout-change constants are `HYPOTHESIS` only.
  - Open: storage for many pair glyphs (grow `MEMFIX` entry 4 or recompress).

### FONT-003 - Expand quote-font capacity for many pair glyphs

- **Status:** `DONE`
- **Milestone:** M3 (prerequisite for `DISC-020` at scale)
- **Dependencies:** LAYOUT-001.
- **Blockers:** None.
- **Objective:** Make room for hundreds of pair glyphs without breaking existing
  text: a lossless font repacker, a usage census, and a same-size repack with
  many pair glyphs, live-tested.
- **Rationale:** Only 30 raw glyphs can be replaced in place. Growing the font is
  constrained by table-driven cart destinations, about 2.4 KB of cart headroom,
  and a full disc.
- **Acceptance criteria:**
  - The repacker reproduces `MEMFIX.PAC` entry 4 byte for byte.
  - The census of win-quote codes is recorded.
  - A same-size repack with at least 8 new pair glyphs displays them and sampled
    original glyphs from a cold boot, with the sacrificed codes recorded.
- **Outputs:** `EXP-0023`, `tools/text/font_pack.py`, `tools/text/quote_census.py`,
  `tools/text/pair_font.py`, and a census report.
- **Evidence:** `EXP-0023` Phase C cold boot (2026-10-17): 10 pair glyphs shown in
  two wins, with the original glyphs intact and 4 sacrificed kanji recorded.
- **Notes:** Growth or a second font region is deferred to Phase D.

### DISC-020 - Reproduce one official-English Ryu caption from a patched disc

- **Status:** `DONE` (closed 2026-10-24 as superseded by `TR-001`)
- **Milestone:** M2
- **Dependencies:** DISC-002, FONT-001, FONT-002, LAYOUT-001, GATE-TRANSLATION.
- **Blockers:** None. All dependencies are `DONE`.
- **Closure:** `TR-001` (`EXP-0033`) exceeded this task. Mednafen booted the
  derived image `build/tr001` from scratch, and all 16 Ryu records showed their
  official English, with provenance in
  `data/translations/ryu_post_fight_q10.json` and the pairing records. The
  current rebuild is the `tr001` reference in `docs/regression_report.md`.
- **Objective:** Using the confirmed `DISC-002` pipeline, replace one Ryu quote
  with its verified official English wording and reproduce it from a cold boot.
- **Rationale:** This is the first translation deliverable. It depends on
  reference provenance (`REF-003` to `REF-005`) and on which glyph codes exist for
  Latin text.
- **Acceptance criteria:** Same as `DISC-002`, with the expected English caption
  as the visible result and its provenance recorded.
- **Outputs:** Patched build, evidence, and translation record.
- **Notes:** Whether the font has Latin glyphs, and which codes select them, is
  unknown. Investigate it as its own experiment before this task.

### RE-020 - Handle multiple Ryu captions programmatically

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** DISC-002.
- **Blockers:** None. M2 was confirmed by `DISC-002` / `EXP-0019`.
- **Objective:** Extend the confirmed mechanism to multiple Ryu captions through
  structured data and tooling.
- **Rationale:** Generalization begins only after untouched-source reproduction.
- **Acceptance criteria:**
  - Detailed subtasks are added from M2 evidence (done: `RE-021`-`RE-025`).
  - Multiple Ryu cases build and verify reproducibly (`RE-022`, `RE-024`).
  - Shared and variant behavior are experimentally supported (`RE-025`).
- **Outputs:** M3 experiments, structured records, justified tooling.
- **Notes:**
  - Do not include another fighter yet.
  - M3 test captions are **record-identifying markers** (for example
    `RYU 07 LINE A`), not translations, so M3 does not depend on
    `GATE-TRANSLATION`. Official English is substituted only after that gate.
  - **Evidence the plan builds on (all `CONFIRMED`):**
    - Ryu's table: 16 records × 38 cells in decoded `MC09.PAC` at `0x91AC`
      (`EXP-0018`). Only record 0 holds the `0000` placeholder.
    - Same-size `MC09.PAC` re-encoding, both splice (`EXP-0019`) and full
      (`EXP-0022`).
    - Full-width Latin (`EXP-0021`).
    - Pair glyphs (`EXP-0022`) and same-size font repack with sacrificed unseen
      kanji (`EXP-0023`).
  - **Main unknowns for M3:**
    - How a record is selected. Selection is random-looking (`EXP-0009`); the
      counter `@(76,r12)` is a `HYPOTHESIS`. Live coverage of 16 records by
      chance alone would need about 50 wins.
    - What `0000` renders beside Latin text.
    - Whether the table is used the same way when Ryu is not on point, with
      another partner, or in another mode.
    - Which observed quote (`Q1`-`Q11`, observation labels) is which record.
- **Evidence (M3 complete, 2026-10-17):**
  - `RE-021`-`RE-025` are DONE.
  - Multiple records build reproducibly (`RE-022`) and display verified
    (`EXP-0026`).
  - Shared and variant behaviour are confirmed (`EXP-0027`).

### RE-021 - Map Ryu quote records and render them offline

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** FONT-003.
- **Blockers:** None.
- **Objective:** Give each of the 16 records a stable identity (record index
  `0-15`), and render any record (original or patched) offline in the game's
  2 × 19 layout.
- **Rationale:** Observation labels (`Q1`-`Q11`) are not record indices. An offline
  renderer lets every build be checked visually before a boot, and lets screenshots
  be matched to records without a debugger.
- **Acceptance criteria:**
  - A tested renderer (`tools/text/quote_render.py`) draws a record from a decoded
    PAC plus a font image. Its output for at least two records matches existing
    cold-boot screenshots by glyph sequence (a WRAM-H display buffer `0x060ED80A`
    match, as in `EXP-0023`).
  - A mapping from `Q` labels to record indices is recorded, with evidence for
    each pair: committed hashes and indices only, not text.
  - Placeholder and line-length metadata for all 16 records are recorded.
- **Outputs:** Tool and tests, mapping metadata, and preview PNGs (ignored).
- **Notes:** Offline only; no live session.
- **Evidence:** `EXP-0024` (2026-10-17). Renderer `CONFIRMED` on 10 of 10
  RAM-known screenshots. Mapping in `data/text/ryu_quote_records.json`. Records
  0, 6, 7, and 14 have never been seen.

### RE-022 - Build a caption compiler for Ryu's table

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** RE-021.
- **Blockers:** None (`RE-021` done).
- **Objective:** One command turns a structured caption file (record index →
  line 1, line 2) plus the untouched source into a derived image.
- **Rationale:** `EXP-0023` hand-assembled one phrase. M3 needs all 16 records
  built and verified reproducibly from data.
- **Acceptance criteria:**
  - **Input schema** (JSON, committed with fixtures). Per line, the compiler:
    - validates the character set;
    - enforces 19 cells per line (38 characters with pairs);
    - keeps a declared `0000` placeholder cell only where the record has one.
  - **Output:**
    - deduplicated pair glyphs at free codes;
    - sacrifices drawn only from the declared unseen-kanji set, each one
      recorded;
    - `MEMFIX.PAC` and `MC09.PAC` (splice, with full re-encode as fallback);
    - an image built by `patch_image`;
    - a manifest of every code, sacrifice, and hash.
  - **Verification built in:**
    - the font and decoded table differ only where intended;
    - the iso check and sector verify pass;
    - two builds are identical;
    - offline renders are written for all 16 records.
  - **Capacity report:** distinct pairs, bytes, and sacrifices for a worst-case
    stress set (all 16 records at full length).
- **Outputs:** `tools/text/caption_compiler.py` (reusing `pair_font`, `pac_patch`,
  and `patch_image`), tests, and a schema.
- **Notes:** No English translation text. Markers and synthetic stress text only.
- **Evidence (2026-10-17):**
  - `tools/text/caption_compiler.py` with 7 tests, and
    `data/captions/caption_spec.schema.json`.
  - Marker image `build/re022_markers/image_{a,b}`: 51 pairs, 21 kanji
    sacrificed, splice re-encode. All checks pass, both builds and a rerun are
    identical, and track 01 is `fd007d13…`.
  - Stress set: 227 pairs and 101 sacrifices; it fits only with the full
    re-encode, leaving 155 bytes of `MC09.PAC` slack.
  - Recorded in `research_log.md`. The live display test is `RE-024`.

### RE-023 - Identify the win-quote selection mechanism (EXP-0025)

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** RE-021.
- **Blockers:** None (`RE-021` done; screenshots can be scored with
  `quote_render --match`).
- **Objective:** Test whether the routine at `0x060AF820-0x060AF8C8`, with its byte
  counter `@(76,r12)` and the tables at `0x060AF8E8`/`0x060AF908`, chooses the
  record.
- **Rationale:** Forcing a chosen record makes live verification of all 16 records
  practical, and may explain `EXP-0010`'s Q3 non-recurrence.
- **Hypothesis (original, `DISPROVEN` by code reading in `EXP-0025`):** writing
  value `v` to the counter makes record `f(v)` display. The counter is in fact the
  partner-name glyph counter. The replacement hypothesis, a record pointer at WRAM-H
  `0x060F249C` written during the KO-to-quote transition, is tested in
  `EXP-0025` Part 1.
- **Discriminating test:**
  - break before the routine;
  - set the counter to two different predicted values in replays from one
    checkpoint;
  - compare the shown record with the prediction.
  - Control: the same replay without a write.
- **Acceptance criteria:** the prediction holds for at least 3 distinct values,
  with the control, or the hypothesis is recorded as `DISPROVEN` with the
  evidence.
- **Outputs:** `EXP-0025`, a debugger runbook (step table) for forcing a record.
- **Notes:** The forcing is a debug harness only. It never ships in a build.
- **Evidence:** `EXP-0025` (2026-10-17). Index store at `060AF282` (word
  `0x060F9E66`); pointer at `0x060F249C`. Forcing indices 6, 7, and 14 from the
  post-KO checkpoint showed exactly those records (`CONFIRMED`).

### RE-024 - Verify all 16 Ryu records from one compiled image (EXP-0026)

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** RE-022, RE-023.
- **Blockers:** None (`RE-022`, `RE-023` done). It can run fully automated
  with `tools/mednafen/ko_capture.py --force-index` from the post-KO checkpoint.
- **Objective:** Cold-boot a compiled image where each record shows its own marker
  caption on both lines. Confirm every record live.
- **Acceptance criteria:**
  - All 16 records are seen on screen, by forcing (`RE-023`) or naturally. Each
    has a screenshot, state, and RAM check (cart font, WRAM-L table, display
    buffer).
  - Record 0's placeholder behavior beside Latin text is recorded.
  - The image is rebuilt from the untouched source twice, identically.
- **Fallback:** if `RE-023` is `DISPROVEN`, natural wins until at least 8
  distinct records are seen. Then all 16 are verified in RAM, with the rest
  marked as offline evidence.
- **Outputs:** `EXP-0026` and the build manifest.
- **Evidence:** `EXP-0026` (2026-10-17). All 16 marker records were forced and
  verified on screen and in RAM from one cold-booted marker image. Records 1-15
  are pixel-exact. Record 0 shows ケン after the Latin text.

### RE-025 - Test variant contexts for Ryu's captions (EXP-0027)

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** RE-024.
- **Blockers:** None (`RE-024` done). Variants still need gameplay for each
  new context (team order, partner, mode); forcing then makes each check
  automatic.
- **Objective:** Decide which behavior is shared and which varies, using the
  `RE-024` image.
- **Variants (one change each, against the Ryu-on-point, Ken-partner, arcade
  baseline):**
  - V1: Ryu is the second team member but lands the KO.
  - V2: a partner other than Ken (record 0 placeholder name).
  - V3: versus mode instead of arcade, if it shows win quotes.
- **Acceptance criteria:** each variant has a prediction (same table and same
  markers, or a different source), a result with screenshot, state, and RAM
  check, and a confidence label. Any second source is recorded as a new unknown.
- **Outputs:** `EXP-0027`. Closes `RE-020` together with `RE-024`.
- **Notes:** Ken-landed KOs are outside M3 (another fighter's table).
- **Evidence:** `EXP-0027` (2026-10-17). V1 (Ryu second): table at `0x002191AC`;
  16/16 records verified. V2 (partner Gouki): base `0x002091AC`; 16/16; the
  placeholder shows ゴウキ. V3 (versus) was not tested (no port 2 bindings).

### RE-030 - Apply generalized mechanism to a second fighter

- **Status:** `DONE` (2026-10-24)
- **Milestone:** M4
- **Dependencies:** RE-020.
- **Blockers:** None.
- **Objective:** Demonstrate the same evidence-backed mechanism for one ordinary second fighter.
- **Rationale:** A second fighter tests whether Ryu-specific assumptions were generalized prematurely.
- **Acceptance criteria:** Fighter selection and detailed tests are based on M3 evidence; fresh builds and visible results reproduce; exceptions remain explicit.
- **Outputs:** M4 experiment and documentation updates.
- **Notes:** Exclude special cases.
- **Plan (`EXP-0028`):**
  - Fighter: **Ken** (`MC0A.PAC`, table at decoded `0xA59C`).
  - Phase A, offline: multi-file caption compiler with a shared font;
    per-file table offsets; line-2 placeholders; Ryu + Ken marker image.
  - Phase B, live: one session, team Ken + Ryu, KO with Ken, then KO with Ryu.
- **Evidence (2026-10-24, `EXP-0028` Phase B):**
  - From the image `build/exp0028a` (track 01 `c3990fa5…`, rebuilt identically
    today), one user session gave a Ken KO (natural record 10, `MC0A` at
    `0x0020A59C`, slot 1) and a Ryu KO (natural record 11, `MC09` at `0x002191AC`,
    slot 2).
  - All 16 records per fighter were forced and verified (`verify_records.py`: 34
    of 34 OK, including the natural captures).
  - Ken's records 11 and 12 expand to リュウ (name entry 9), and Ryu's record 0 to
    ケン (entry 10). Ken's one-line records 0, 1, and 13 stay one-line.
  - Every screenshot was read. All predictions held, so no Ryu-specific
    assumption survived.
  - Separately, Ken's Saturn table is byte-identical to the arcade Japanese slot
    10 (`data/text/ken_arcade_pairing.json`).
    Then 32 forced records are verified automatically.

### RE-040 - Systematize ordinary post-fight localization

- **Status:** `DONE` (2026-10-24; `RE-041` to `RE-047` are all `DONE`)
- **Milestone:** M5
- **Dependencies:** RE-030, RE-041, RE-042, RE-043, RE-044, RE-045, RE-046, RE-047.
- **Blockers:** None.
- **Objective:** Build and validate the ordinary-character post-fight workflow.
- **Rationale:** Roster-scale work requires evidence-backed coverage and regression controls.
- **Acceptance criteria:** Detailed tasks define scope, translation provenance, binary traceability, deterministic builds, representative visible verification, exceptions, and regression tests. M5 is complete when `RE-041` to `RE-047` are `DONE`.
- **Outputs:** Ordinary-caption data, tools, coverage manifest, experiments, regression report.
- **Notes:** Endings and special cases remain prohibited.
- **Breakdown (2026-10-24):** each criterion maps to a task.

  | Criterion | Task |
  | --- | --- |
  | Scope | `RE-041` coverage census |
  | Translation provenance | `RE-042` per-character pairing |
  | Exceptions | `RE-043` exceptions register |
  | Binary traceability, deterministic builds | `RE-044` roster spec and capacity; `RE-045` roster image |
  | Representative visible verification | `RE-046` |
  | Regression tests | `RE-047` |

  - Facts it builds on: 23 Saturn quote files `MC00`-`MC16`. The `EXP-0023`
    census found one ordinary 16-record table in each of `MC01`, `MC03`-`MC06`,
    `MC09`-`MC0B`, `MC0D`-`MC12`, and `MC14`-`MC16` (17 files).
  - `MC00`, `MC02`, `MC07`, `MC08`, `MC0C`, and `MC13` are irregular.
  - `MC09` = Ryu = arcade slot 9 and `MC0A` = Ken = slot 10 are confirmed. Any
    other file-to-character mapping is a `HYPOTHESIS` until `RE-041`.

### RE-041 - Census Saturn quote files against arcade character slots

- **Status:** `DONE`
- **Milestone:** M5
- **Dependencies:** RE-030, REF-004.
- **Blockers:** None. Offline only.
- **Objective:** Establish, for every `MC*.PAC`, which character it belongs to and
  whether it is an ordinary 16 × 76 table.
- **Rationale:** Scope must come from evidence, not from the file index or an
  assumed roster order.
- **Acceptance criteria:**
  - For each of the 23 files, every census table is searched against all 26
    arcade Japanese slots (`0x20BFAC`) for byte identity.
  - The name table is cross-checked where possible.
  - Each file is classified as ordinary (one identical 16-record table), partial,
    irregular, or unmatched, with evidence.
  - Results go to a committed metadata manifest (hashes, offsets, slots; no text).
- **Outputs:** `data/text/coverage_manifest.json`, an experiment record, and an
  extension of `tools/reference/quote_pairing.py` for multi-slot search.
- **Notes:** No file is called a character until it matches. Arcade slots
  17-25 are Norimaro, bosses, and secret characters; a match there is an
  exception for `RE-043`, not scope.
- **Evidence (2026-10-24, `EXP-0034`):**
  - Every `MCnn` holds arcade slot `nn`'s whole Japanese block, byte-identical in
    all three sets. The Saturn name table lists the same 26 characters in arcade
    slot order.
  - Structurally ordinary (18): `MC01`, `03`-`07`, `09`-`0B`, `0D`-`12`,
    `14`-`16`.
  - Irregular (5): `MC00`, `MC02` (+ slot 23), `MC08` (+ slot 24), `MC0C` (+ a
    4-record table), and `MC13` (a 120-record table).
  - The manifest is `data/text/coverage_manifest.json`.

### RE-042 - Record per-character pairing for the ordinary roster

- **Status:** `DONE`
- **Milestone:** M5
- **Dependencies:** RE-041, RE-043.
- **Blockers:** None. The roster is `data/text/m5_roster.json` (17 characters).
- **Objective:** Apply the `GATE-TRANSLATION` policy to each ordinary character:
  Saturn record `k` gets official English entry `k & 7` of the matched slot.
- **Rationale:** The policy requires per-character verification (table identity
  plus the slot-independent remap, `EXP-0031`).
- **Acceptance criteria:**
  - Each ordinary character has pairing metadata like
    `data/text/ryu_arcade_pairing.json`.
  - English-entry presence and identity are checked in the US and EU sets, and
    against the PS1 (`EXP-0032`), with differences listed.
  - Records with `0000` placeholders are listed per character.
  - Whether to drop each placeholder is decided case by case: TR-001 dropped
    Ryu's; English has none.
- **Outputs:** Pairing metadata per character; `data/translations/README.md`
  update.
- **Notes:** Provenance stays generator-based: text is read from the local arcade
  ROM at build time, and only hashes are committed.
- **Evidence (2026-10-24):** `tools/reference/roster_pairing.py` (with tests)
  wrote `data/text/roster_pairing.json`.
  - All 17 roster tables are byte-identical to their arcade Japanese slots, and
    each record `k` pairs with English entry `k & 7`.
  - Every English block is identical across `mshvsfu`, `mshvsf`, and `mshvsfj`,
    and found in PS1 `SELECT.BIN`. There are no differences to list.
  - 33 placeholder cells are listed per character. The official English has none
    (0 cells), so every placeholder is dropped. The decision is recorded per cell
    in `data/text/m5_roster.json`.

### RE-043 - Maintain the exceptions register

- **Status:** `DONE`
- **Milestone:** M5
- **Dependencies:** RE-041.
- **Blockers:** None.
- **Objective:** List every quote file or character excluded from M5, with the
  reason and the gated task that may take it up.
- **Rationale:** Exceptions must stay explicit (`AGENTS.md` rule 24).
- **Acceptance criteria:**
  - Each irregular, partial, or unmatched file, and each Norimaro, boss, or
    secret-character slot, is listed with its evidence. Each points to
    `SPECIAL-001`, `END-001`, or a named follow-up.
  - No exception is translated or modified in M5.
- **Outputs:** A section in `docs/text_system.md` (or a dedicated doc), linked from
  the coverage manifest.
- **Input from `RE-041` (a proposal, not a decision):**
  - Structurally ordinary, but special by role: `MC11` (slot 17, Norimaro),
    `MC14` and `MC15` (slots 20 and 21, secret palette swaps), and `MC16` (slot 22,
    Shadow).
  - Bosses: `MC00` (slot 0) and `MC13` (slot 19), both irregular.
  - Irregular but playable: `MC02` (Captain America + U.S. Agent), `MC08`
    (Blackheart + Mephisto), and `MC0C` (Dhalsim + a 4-record table). Each needs
    an in-or-out decision.
- **Evidence (2026-10-24):**
  - The user chose the 17-character roster (slots 1-16 and 18; Captain America,
    Blackheart, and Dhalsim by their own blocks only). Norimaro, secret
    characters, Shadow, and bosses are excluded. Slot 25 sharing Spider-Man's
    English is accepted.
  - The register is `docs/coverage_exceptions.md`; the roster is
    `data/text/m5_roster.json`.

### RE-044 - Build the roster caption spec and check font capacity

- **Status:** `DONE` (2026-10-24)
- **Milestone:** M5
- **Dependencies:** RE-042, RE-043, TR-001.
- **Blockers:** None.
- **Objective:** Generate one schema-v2 spec covering every ordinary character,
  and show that its pair glyphs fit one shared font.
- **Rationale:** All characters share one font (`EXP-0028`). The unseen-kanji
  budget is about 817 pairs (`EXP-0023`); a single character used 95.
- **Acceptance criteria:**
  - `tools/text/official_captions.py` emits a v2 spec from the coverage manifest:
    each file, table offset, and slot.
  - `caption_compiler.py --capacity` reports distinct pairs, bytes, and free codes
    for the whole roster.
  - If it does not fit, a documented decision follows (pair-alignment
    optimization, a wider reclaim set after a UI-usage census, or splitting), and
    no build happens until it fits.
  - Every character outside a-z, A-Z, 0-9, space, `!`, `.`, and `,` is mapped to a
    font glyph chosen by shape, or rejected with evidence.
- **Outputs:** The generator extension, a capacity report, and character-map
  additions with their evidence.
- **Progress (2026-10-24):**
  - **Character map.** The roster English needs `' ? - "` and `‼`, plus two
    arcade codes. Those codes were identified on the arcade screen by forcing the
    quote pointer: `0x0122` = `‼` and `0x0160` = `"` (`EXP-0029` addendum).
  - Glyphs chosen by bitmap shape: `?` → `0x08DC`, `'` → `0x08B9` (’), `"` →
    `0x08BB` (”, one glyph for both sides, like the arcade), `-` → `0x08CB`
    (centred bar), and `‼` → `0x08DF`. They are in `pair_font.py` and the schema.
  - **Spec.** `official_captions.py --roster` emits a v2 spec (17 tables, 272
    records) to the ignored `local/re044/`.
  - **Capacity: does not fit.** There are 405 distinct pairs but 248 free codes.
    Bytes are fine (17,179 needed of 30,235 reclaimable); the code count is the
    binding limit.
  - Per-line alignment (shifting a line's pairing by one character) reduces the
    pairs to 338 (greedy estimate). That is still too many, so a decision is
    needed:
    - **(A)** reuse unseen-kanji codes in place as pair codes (proven display
      range; same content risk as today's sacrifice); or
    - **(B)** raise the font code count to use `0x0C60`-`0x0DFF` (untested; needs
      a live experiment).
- **Decision (user, 2026-10-24):** "Use option A: reuse unseen-kanji codes in place
  as pair codes, plus the per-line alignment optimization to keep the kanji
  footprint small."
- **Result (2026-10-24):**
  - `official_captions.py` chooses a deterministic per-line 0/1 shift (greedy),
    and `pair_font.build` / `caption_compiler` reuse sacrificial kanji codes in
    place, only when pairs exceed free codes.
  - The new font check `reused_codes_in_kanji_range` passes, and the existing
    checks are unchanged for reused codes. Tests cover both changes.
  - Regression: the TR-001 spec (`aa7fa863…`) and images `tr001` (`2941a9c5…`)
    and `exp0028a` (`c3990fa5…`) rebuild byte-identically.
  - Capacity: 338 distinct pairs (down from 405) = 248 free codes + 90 reused
    kanji codes; 13,992 of 30,235 bytes. It **fits**.
  - The roster spec SHA-256 is `b2c097fa…f334` (ignored `local/re044/`).

### RE-045 - Build the ordinary-roster image deterministically

- **Status:** `DONE` (2026-10-24, `EXP-0035`)
- **Milestone:** M5
- **Dependencies:** RE-044.
- **Blockers:** None.
- **Objective:** Produce one derived image with every ordinary character's official
  English.
- **Rationale:** Binary traceability and determinism must hold at roster scale.
- **Acceptance criteria:**
  - Two builds are byte-identical, and every compiler check is true for every
    file.
  - Only target cells, pair codes, and sacrificed glyphs change, all recorded.
  - Offline renders of every record are reviewed against the spec.
  - Output hashes are recorded.
- **Outputs:** The `build/` image (ignored), compile manifest hashes, and an
  experiment record.
- **Evidence (2026-10-24, `EXP-0035`):**
  - Two identical builds (track 01 `f5044e8a…`); every font, table, and image
    check is true.
  - Only the 17 roster PACs and `MEMFIX` differ. The exception blocks are
    byte-identical, records `k + 8` equal records `k`, and no placeholders
    remain.
  - All renders were reviewed and are legible, including the new punctuation.

### RE-046 - Verify a representative set of characters live

- **Status:** `DONE` (2026-10-24, `EXP-0036`)
- **Milestone:** M5
- **Dependencies:** RE-045.
- **Blockers:** None. The roster image is `build/re046_roster` (`EXP-0036`), which
  decodes identically to `build/re045` (`EXP-0035`).
- **Objective:** Show on screen that the roster image works across the layout
  variants found in `RE-041`, with minimal user gameplay.
- **Rationale:** Live checks catch runtime effects that offline checks miss, such
  as slot bases, placeholders, and font loading.
- **Acceptance criteria:**
  - A representative subset, chosen from `RE-041` features, is verified. It
    covers at least one Marvel and one Capcom fighter, a placeholder layout other
    than Ryu's and Ken's, a one-line record, and both team slots. All 16 records
    of each are forced and pass `verify_records.py`, and every screenshot is read.
  - Every other ordinary character is verified offline: decoded PAC tables equal
    the compiled tables, and renders equal the spec.
  - The gameplay plan is agreed with the user before the session.
- **Outputs:** An experiment record and the verification report.
- **Progress (2026-10-24):**
  - Run 1 on `build/re045` reset to the BIOS at the fight load. Diagnosed without
    more gameplay: the opponent Dan's `MC12` declared a shorter compressed length.
  - Fixed in `pac_patch.py` (keep the original declared length).
  - The rebuilt roster `build/re046_roster` (`351254c4…`) passes the replay test.
  - Run 2: four KOs, then 64 forced records with no gameplay. All 68 captures pass
    `verify_records.py`, and all screenshots were read. Coverage: Marvel and
    Capcom, both team slots, one-line records, dropped placeholders, and the
    irregular files `MC02` and `MC0C`.
  - The other 13 characters: decoded tables, `MEMFIX`, and renders are identical
    to the `EXP-0035` review, and all 78 manifest checks are true.
  - New: a second quote state (`r12 = 0x060F9ED6`); `ko_capture.py` and
    `verify_records.py` handle both.
- **Notes:** Each live character needs a KO with that character, which costs user
  time. Automating character select (for example, agent input injection) would be
  a Mednafen change. It needs separate user authorization and an `EMU-020`-style
  justification, so it is not assumed here.

### RE-047 - Add regression controls for the roster pipeline

- **Status:** `DONE` (2026-10-24)
- **Milestone:** M5
- **Dependencies:** RE-045.
- **Blockers:** None. The roster reference is `build/re046_roster` (`EXP-0036`).
  The declared-length change gives `tr001` and `exp0028a` new hashes, so they need
  re-baselining.
- **Objective:** Keep confirmed outputs from drifting as the pipeline grows.
- **Rationale:** Roster changes must not silently alter Ryu, Ken, or earlier
  builds.
- **Acceptance criteria:**
  - Tests with synthetic fixtures cover the v2 generator, multi-slot pairing, and
    any new glyph mappings.
  - A local-only check (skipped when sources are absent) rebuilds the reference
    images (`re022_markers`, `exp0028a`, `tr001`, roster) and compares their
    recorded hashes.
  - A regression report lists every reference hash and its last check.
- **Outputs:** Tests, a regression script, and a regression report in `docs/`.
- **Result (2026-10-24):**
  - Synthetic tests: a two-character v2 roster spec that the compiler accepts
    (shared alignment), pairing through each slot's own pointers, and the caption
    schema accepting exactly the mapped characters (distinct punctuation codes).
  - `tools/regression/reference_builds.py` with the committed baseline
    `data/regression/reference_builds.json`. It checks each spec hash (and, with
    the pinned `cps2.cpp`, regenerates arcade-derived specs first), rebuilds from
    the untouched source, and compares track 01, every patched file, and every
    compiler check. Re-baselining needs `--write-baseline --reason`; the replaced
    hash is kept under `previous`.
  - Local-only test `tests/integration/test_reference_builds.py`: skipped unless
    the source image is present and `MSHVSF_REGRESSION=1` (about one minute).
  - Re-baselined `re022_markers`, `exp0028a`, and `tr001` for the `EXP-0036`
    declared-length fix after checking the cause: only the PAC header words at
    `+0x04` and `+0x10` change; streams, sizes, and decoded data are identical,
    and the PAC header sector equals the source again. The roster rebuild equals
    `build/re046_roster` exactly.
  - Report: `docs/regression_report.md` (all four pass).
  - Spec regeneration also passes: with the pinned driver
    (`local/mame_src/cps2.cpp`, SHA-256 `a8c09ef8…`), `official_captions.py`
    regenerates the `tr001` and roster specs byte-identical to their recorded
    hashes.

## Low-Priority Win-Quote Follow-ups

These are accounted for, not scheduled. None blocks M6. Take one up only when
the user asks or when it unblocks other work.

### RE-048 - Improve lowercase descenders in pair glyphs

- **Status:** `BACKLOG`
- **Priority:** low
- **Milestone:** M5 polish
- **Dependencies:** RE-045.
- **Blockers:** None.
- **Objective:** Make `p` (and check `g`, `q`, `y`) read clearly in the composed
  pair glyphs.
- **Rationale:** In `EXP-0036`, `p` sits on the baseline with a cut-short stem
  ("Freedom prevails!"). It is legible but looks like a small capital.
- **Acceptance criteria:** Offline renders of every affected roster line show
  clear descenders. The font still fits the entry, and the regression baseline
  is re-baselined with a recorded reason.
- **Outputs:** Glyph change, renders, and an experiment record.
- **Notes:** Cosmetic only; it may interact with `REF-012`.

### RE-049 - Identify what selects the second win-quote state

- **Status:** `BACKLOG`
- **Priority:** low
- **Milestone:** M5 polish
- **Dependencies:** RE-046.
- **Blockers:** None.
- **Objective:** Explain when the quote routine uses `r12 = 0x060F9E16` versus
  `0x060F9ED6` (`EXP-0036`).
- **Rationale:** The tools already handle both states, so this is understanding,
  not a fix.
- **Acceptance criteria:** A discriminating test (for example, KOs from known
  1P/2P sides, logging `r12` at `060AF724`) confirms or rejects each candidate in
  `docs/known_unknowns.md`.
- **Outputs:** Experiment record and a discoveries or research-log entry.
- **Notes:** Needs one short gameplay session.

### RE-050 - Spot-check more roster characters live

- **Status:** `BACKLOG`
- **Priority:** low
- **Milestone:** M5 polish
- **Dependencies:** RE-046.
- **Blockers:** None.
- **Objective:** Add live evidence for characters verified only offline (13 of
  17).
- **Rationale:** `RE-046` covered the layout variants, so the rest rest on
  offline equivalence. More live checks add confidence, not new coverage.
- **Acceptance criteria:** Each chosen character passes all 16 records with
  `verify_records.py`, and every screenshot is read.
- **Outputs:** Experiment record.
- **Notes:** Each character costs one user KO.

### REL-001 - Package the roster image as a distributable patch

- **Status:** `DONE` (2026-10-25)
- **Priority:** low
- **Milestone:** M5 polish (packages the M8 image)
- **Dependencies:** RE-047, END-025.
- **Blockers:** None.
- **Objective:** Produce a patch file (no game data in the repository) that turns
  the untouched source image into the roster image.
- **Rationale:** The repository holds tools and hashes only; users need a patch
  to apply.
- **Acceptance criteria:** Applying the patch to a source image with the recorded
  hashes reproduces the reference track 01 exactly, and the patch holds no
  copyrighted payload beyond what the chosen format requires.
- **User decisions (2026-10-25):**
  - the format is xdelta3 (VCDIFF);
  - the patch stays local (under `build/`, not committed);
  - a README describes the assets someone must supply to rebuild it;
  - installing xdelta3 3.2.2 with Homebrew was approved.
- **Evidence:**
  - `tools/disc/make_patch.py` (new, with tests). The old note named this
    path, but no disc patch tool existed; `tools/memory/make_patch.py` patches
    RAM dumps.
  - The tool checks the source against `references/mshvsf/saturn_jp/README.md`
    and the built track 01 against reference `m8_roster`. Only BIN tracks may
    differ.
  - Fixed flags `-e -9 -S none -A -f`: no secondary compressor, no
    application header, Adler-32 per window.
  - The patch is encoded twice (byte-identical), then decoded with
    `xdelta3 -d`.
  - Result: `mshvsf_saturn_en_m8.Track01.xdelta`, 155,717 bytes, SHA-256
    `00c3906a…`. Only track 01 changes; tracks 02-12 and the CUE are
    identical. Record: `release/m8_roster.json`.
  - **User-side check:** a copy of the original image patched with the
    xdelta3 CLI matches every one of the 13 components of the live-verified
    `build/end027` image.
  - **Fresh-clone check:** a new clone given only the disc image,
    `mshvsfu.zip`, and the downloaded `cps2.cpp` passed all six references
    and produced the identical patch and record.
  - The font-candidate list moved from the ignored
    `research/memory_dumps/exp0023/` into `data/text/font_candidates.json`
    (code numbers only, same hash `32e513ae…`), so a clone can build.
  - Instructions: `release/README.md` (apply, assets to supply, rebuild).
- **Not tested:** graphical patchers (Delta Patcher, xdelta UI, Rom Patcher
  JS).

### REF-012 - Compare the arcade win-quote fonts across regions

- **Status:** `BACKLOG`
- **Priority:** low
- **Milestone:** Reference (no Saturn change)
- **Dependencies:** REF-008, REF-009.
- **Blockers:** None.
- **Objective:** Test the user's observation that the US/EU arcade sets draw win
  quotes with a different font from the Japanese set, and judge whether that font
  could serve the Saturn captions.
- **Rationale:** The Saturn captions use pair glyphs composed from the Japanese
  full-width font (`FONT-003`). A purpose-made Latin font might read better and
  fit more text.
- **Acceptance criteria:**
  - The font used for win quotes in each set is located and identified (tiles,
    codes, cell size), with evidence (ROM offsets, MAME captures).
  - JP vs US/EU differences are recorded: same tiles, different tiles, or
    different code ranges.
  - Saturn fit is assessed against the quote font's cell format and capacity
    (`FONT-001`, `LAYOUT-001`).
  - Reuse is presented as a user decision with its trade-offs (provenance and
    legal posture, like `GATE-TRANSLATION`). Nothing is adopted in this task.
- **Outputs:** Reference README and metadata; no committed glyph data.
- **Notes:** The difference is unconfirmed (`HYPOTHESIS`). Do not assume that the
  arcade tile format matches the Saturn font format.

### END-001 - Begin ending-text investigation

- **Status:** `DONE` (2026-10-24, `EXP-0037`)
- **Milestone:** M6
- **Dependencies:** RE-040 (`DONE`).
- **Blockers:** None. The user lifted the former blocker ("the ordinary post-fight
  pipeline is not mature") on 2026-10-24, after M5 was completed (`AGENTS.md`
  rule 23).
- **Objective:** Observe ending text and design the first independent discriminating experiments.
- **Rationale:** Ending storage/rendering must not be inferred from captions.
- **Acceptance criteria:** Detailed tasks are created from observations; hypotheses and checkpoint needs are explicit; no structural equivalence is assumed.
- **Outputs:** M6 observations, task breakdown, unknowns, experiment designs.
- **Notes:** M6 begins investigation; it does not imply a working ending patch.
- **Checkpoint plan (user, 2026-10-24):** in arcade mode, reach the final boss
  and lose, then save a state at the continue screen or the character select it
  leads to. Later sessions can then pick other characters for endings without
  replaying the run.
  - `HYPOTHESIS` to verify first: continuing from the final stage returns to
    character select and keeps the final-boss stage, so a new pick fights only
    the boss.
  - Save states are local checkpoints (ignored), not RAM evidence (`AGENTS.md`).
  - Start with Ryu (`END-010` targets a Ryu ending), and treat the ending's text,
    storage, and renderer as unknown.
- **Evidence (2026-10-24, `EXP-0037`):**
  - The run used the untouched image, because the roster image changes the
    quote font, which the ending might share. The user played Ryu/Ken, lost to
    Mech-Gouki, then continued with Ryu/Gouki and won.
    `tools/mednafen/session_recorder.py` recorded screenshots and states with no
    hotkeys.
  - The continue result is `SUPPORTED` (one run): continuing went to character
    select and then straight to `STAGE-08` against Mech-Gouki.
    `select_after_continue.mcs` holds on select with no input for at least 50 s.
  - The run showed two text scenes after the boss:
    - a four-box post-boss dialogue at the top of the frozen stage, after the
      partner Gouki drops in;
    - three ending pages, each with a picture panel and a bottom text box.
  - Measured: 13-row glyphs, a 16-px pitch and line pitch, and line starts on a
    16-px grid (x ≡ 12 mod 16), but not simple centering. Timing and checkpoint
    hashes are in `EXP-0037`. The transcription is local only.
  - Storage, encoding, renderer, and font are all still `UNKNOWN`. The task
    breakdown is `END-002` to `END-006` below; `END-010` depends on it.

### END-002 - Identify the video path that draws ending text

- **Status:** `DONE` (2026-10-24, `EXP-0038`)
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None. No gameplay is needed (`EXP-0037` checkpoints).
- **Objective:** Establish whether the dialogue and the ending-page glyphs are
  VDP1 sprites, VDP2 layer cells, or parts of bitmaps.
- **Rationale:** The renderer decides what a patch must change: glyph codes,
  tile data, or images. The win-quote renderer may not be assumed.
- **Acceptance criteria:**
  - One hypothesis at a time, as designed in `EXP-0037`. First test "one VDP1
    sprite per glyph" on `ending_dialogue_box1.mcs`: passive VDP1/VDP2
    extraction (validated regions), then a single active change (skip only the
    candidate commands), with before/after screenshots.
  - The same check on `ending_page1.mcs`, since the pages may differ.
  - The result records either the glyph source address (character data) for
    the next task, or the refuted alternatives.
- **Outputs:** Experiment record, local dumps and screenshots.
- **Notes:** If VDP1 is refuted, test VDP2 as a separate hypothesis.
- **Evidence (2026-10-24, `EXP-0038`; `CONFIRMED`, discoveries `END-002`):**
  - Dialogue box 1 and page 1 are VDP1 normal sprites (16 × 16, 4 bpp), one per
    cell, on a 19 × 2 grid at x = 26 + 16k. Color words: `0x6030` (dialogue)
    and `0x61F0` (page).
  - All 40 glyph cells are byte-exact quote-font cells (base `0x0278CF60`).
    The `FONT-001` routine `0x0601CE00` builds each one, with the code in R3,
    the VDP1 destination in R9, and caller return `0x0601CDE2`.
  - **Glyph source:** quote-font codes, decoded per screen into VDP1 VRAM
    (box 1 from `0x0A700`, page 1 from `0x0BD00`).
  - **Active change.** Zeroing one character cell (not skipping commands)
    removed exactly that glyph on both screens, and the box was otherwise
    unchanged. Reason for the deviation: a cell write tests the same claim, and
    the game does not rebuild glyph cells during a screen, so it persists. A
    command list is likely rebuilt every frame.
  - Not inspected: pages 2-3, boxes 3-4, and the background layer (presumably
    VDP2).

### END-003 - Search work RAM for the ending text structure

- **Status:** `DONE` (2026-10-24, `EXP-0039`)
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None. No gameplay is needed.
- **Objective:** Test whether the visible dialogue and page text exist in work
  RAM as one fixed-width value per character.
- **Rationale:** An encoding-agnostic hit gives an address to trace to the disc,
  with no code table assumed.
- **Acceptance criteria:**
  - Run `tools/text/pattern_search.py` over WRAM-L and WRAM-H from the dialogue
    and page checkpoints, at 8- and 16-bit widths. The patterns come from the
    repeat structure in the local transcription (`EXP-0037` design: the box 1
    pattern, plus the name that box 1 shares with pages 1 and 2).
  - Each hit is checked for consistency: the same symbol has the same value
    across boxes and pages.
  - A no-hit result is recorded as evidence against per-character text in RAM.
  - Cart RAM is searched only with the rationale recorded, because its
    extraction is unvalidated.
- **Outputs:** Experiment record with hit addresses and values, or the negative.
- **Notes:**
  - Compare hits with the win-quote codes only afterwards, as a separate test.
  - Review the local transcription independently (as in `REF-003`) before
    trusting the patterns.
  - Since `EXP-0038`, the codes of box 1, box 2, and page 1 are known from the
    glyph matches and the R3 log. A direct search for those 16-bit sequences
    (for example box 2's
    `0970 080B 09F8 082A 0823 0803 0825 080E 084A 0827`) is now a sharper first
    test. The structure-only search remains the fallback if codes are
    transformed.
  - The pre-filled slot table at WRAM-L `0x00260E5E` (R1 in `EXP-0038`) is not
    the text, so do not mistake it for a hit.
- **Evidence (2026-10-24, `EXP-0039`; boxes 1-2 and the placeholder are
  `CONFIRMED`, discoveries `END-003`):**
  - Every line was found once in WRAM-L as plain big-endian codes, in 76-byte
    records of 19 × 2 cells with explicit positions. All 13 line starts match
    the screen.
    - Dialogue: `0x0022AE14`/`0x0022AE60` and `0x0022B9F4`/`0x0022BA40`.
    - Pages: `0x00233664` + `0x4C`·k.
  - Code `0x0000` is a name placeholder, filled from a WRAM-H name table (Ryu
    at `0x06095FE4`).
  - Three single-write trials met their predictions: box 2 cell, box 1
    placeholder, and Ryu's name entry.
  - The tables load at the `STAGE-08` transition (run 1, frames
    53,481-53,651) and include Gouki's lines while the team was Ryu/Ken.
  - Pattern-only search was not needed: the direct code search hit. The
    corrected local transcription is `5718880a…`.

### END-004 - Locate the disc source of Ryu's ending text

- **Status:** `DONE` (2026-10-24, `EXP-0040`)
- **Milestone:** M6
- **Dependencies:** END-002 or END-003.
- **Blockers:** None. Trace starts:
  - `EXP-0039`: the tables arrive in WRAM-L between frames 53,481 and 53,651 of
    run 1 (the `STAGE-08` transition). Records sit at `0x0022AE14`,
    `0x0022B9F4`, and `0x00233664`.
  - A write breakpoint on one of these addresses, replayed from a run 1 state
    at or before frame 53,481 (kept as
    `local/end001/checkpoints/before_stage08_load.mcs`, `bed2673fb2e47201…`), finds the writer with no gameplay.
  - `EXP-0038`: the glyph routine `0x0601CE00`, returning to `0x0601CDE2`.
- **Objective:** Find which disc file supplies the dialogue and the ending-page
  text, and in what format.
- **Rationale:** M7 must change the source image, not live RAM (as M2 did for
  captions).
- **Acceptance criteria:**
  - A write breakpoint (log mode), replayed with no input from
    `ryu_gouki_post_boss_ko.mcs`, finds the writer. The trace leads back to a
    disc read.
  - The file is named with its ISO 9660 entry.
  - An offline decode that reproduces the RAM bytes exactly shows the format
    (compression, layout).
- **Outputs:** Experiment record, decoder evidence, and a discoveries entry if
  confirmed.
- **Notes:** Do not assume `MCnn`, PAC, or LZSS until observed.
- **Evidence (2026-10-24, `EXP-0040`; `CONFIRMED`, discoveries `END-004`):**
  - Dialogue: `MC13.PAC` (slot 19, the final boss's quote file), LZSS
    (`DISC-001` format), decoded to `0x00220000` by PC `0603E446`. Ryu/Gouki
    records are at decoded offsets `0xAE14`, `0xAE60`, `0xB9F4`, and `0xBA40`.
  - Pages: `ME.PAC`, raw from file offset `0x10`, copied to `0x00230000` by PC
    `0603E04E`. Ryu's pages are at file offsets `0x3674`, `0x36C0`, and
    `0x370C`.
  - The text records are byte-identical to the decode and the file. The other
    differences are relocated pointers (RAM = file + base + `0x40`), plus 30
    unexplained non-text longwords in `ME.PAC`'s region.
  - Both files load at the `STAGE-08` transition. The loader contexts carry
    each file's header word 1, while their name fields both read `me.pac`.

### END-007 - Verify that edited ending files load and display (marker build)

- **Status:** `DONE` (2026-10-24, `EXP-0041`)
- **Milestone:** M6
- **Dependencies:** END-004.
- **Blockers:** None. Part 2 used one user boss fight, because a no-input
  replay cannot win it.
- **Objective:** Show that a derived image built from the untouched source,
  with one marker change per file, displays the changes in Ryu's ending.
- **Rationale:** `EXP-0040` names the files, but only a rebuilt image proves
  that the disc copy is the one used, with no other copy, checksum, or length
  check. This is the ending equivalent of M2.
- **Acceptance criteria:**
  - One variable per build:
    - (a) a same-size change in `ME.PAC` (one code in page 1, raw);
    - (b) one code in `MC13`'s box 2 record, LZSS re-encoded with the
      `EXP-0036` declared-length rule.
  - Each build goes under `build/`, and each records its source and output
    hashes and its original and modified bytes.
  - Replay a pre-load checkpoint on each image (no input) and screenshot the
    box or page, against an untouched-image control.
  - Nothing outside the marker cell changes in the box or page.
- **Outputs:** Experiment record, build metadata, and a discoveries entry if
  confirmed.
- **Notes:**
  - Markers only (for example full-width `R`, `FONT-002`). No translated text
    before `END-005`, `END-006`, and the `END-010` scope decision.
  - Replaying a state saved on the untouched image onto a derived image works
    for win quotes (`EXP-0036`). It may not hold if the files were already
    loaded, so start before the `STAGE-08` load.
- **Evidence (2026-10-24, `EXP-0041` Part 1; `CONFIRMED`, discoveries
  `END-007 Part 1`):**
  - Builds A (`ME.PAC`), B (`MC13.PAC`, full re-encode, declared length kept),
    and C (both). Each track 01 hash is recorded. The other tracks and the CUE
    are identical to the source.
  - Replayed from `before_stage08_load.mcs` (600 frames), the loaded
    `MC13`/`ME.PAC` regions equal the untouched run's, except each marker word.
  - The RAM marker displays in exactly its cell (page 1 here; box 2 in
    `EXP-0039`). Neither file is re-read after the KO.
  - Deviation: the criterion "replay a pre-load checkpoint and screenshot the
    box or page" cannot be met without gameplay, because the boss fight lies
    between the load and the ending. It is replaced by the composed
    load-and-display evidence above, plus Part 2.
- **Part 2 (2026-10-24, `CONFIRMED`):** image C from `before_stage08_load.mcs`.
  Ryu (team Ryu/Ken) beat Mech-Gouki on the second try, after the agent
  restored the state.
  - Page 1 showed R in exactly the marker cell: 145 px vs the untouched run,
    byte-identical to the RAM-trial screenshot.
  - Pages 2-3 were unchanged.
  - The Ryu/Ken dialogue uses other boxes 1-2, so the `MC13` marker is
    confirmed in RAM only (as anticipated).
  - Checkpoint: `ryu_ken_post_boss_ko_imageC.mcs` (`b1ef3827ba0b31be…`). Its
    RAM holds the markers.

### END-005 - Identify what selects the post-boss dialogue and the ending

- **Status:** `DONE` (2026-10-24, `EXP-0043`)
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None. Needs one user gameplay session per team.
- **Objective:** Separate the effects of the point character, the partner, and
  the KO character on the dialogue and on the ending pages.
- **Rationale:** M7 needs to know which text belongs to "Ryu's ending" and
  whether the dialogue is team-specific.
- **Acceptance criteria:**
  - The first run changes only the partner: from `select_after_continue.mcs`,
    pick Ryu (point) + Ken and beat the boss with Ryu.
  - Prediction (`EXP-0037`): the ending pages are identical in the text boxes,
    and the dialogue differs or is absent. The result is recorded either way.
  - Later runs swap the order or the KO character, one variable each.
  - Each run also records whether the boss stage was kept, as a second
    observation of the continue result.
- **Outputs:** Experiment record, new checkpoints, and screenshots that have
  been read.
- **Notes:** Ask the user only for the boss fight. The recorder captures
  everything else.
- **Observation (2026-10-24, `EXP-0041` Part 2; `SUPPORTED`, not a controlled
  run):** Ryu (point) + Ken beat Mech-Gouki on marker image C. Compared with
  the untouched Ryu/Gouki run (`EXP-0037`):
  - ending pages 1-3 are identical in the text box, apart from the page marker;
  - dialogue box 4 is identical;
  - box 3 differs only in the placeholder name (the partner's);
  - boxes 1-2 are other lines.

  This fits "pages depend on the point character; boxes 1-2 depend on the
  partner; the box 3 placeholder names the partner". Two variables differ
  (partner and image), so the controlled partner-only run on the untouched
  image is still this task's first criterion. A Ryu/Ken post-KO checkpoint now
  exists (`ryu_ken_post_boss_ko_imageC.mcs`, image C RAM).
- **Evidence (2026-10-24, `EXP-0043`; `CONFIRMED`, discoveries `END-005`):**
  - Controlled run on the untouched image, from `select_after_continue.mcs`.
    Ryu + Ken won on the second attempt, with Ryu landing the KO.
    - The pages are pixel-identical to `EXP-0037`.
    - Box 4 is identical, and box 3 differs only in the name.
    - Boxes 1-2 are other lines: `MC13` records 36-37.
    - The continue kept the boss stage again, twice.
  - Indexing model, predicted and met in MAME: Ryu + Chun-Li, and Gouki +
    Captain America.
    - Partner pair: 16 + 2·partner slot. Point pair: 16 + 2·(26 + point slot).
    - English uses the same indices, one record each.
    - Pages follow the point character.
  - Not met: varying the KO character (deviation recorded). The planned order
    swap became Gouki + Captain America, because the cursor path differs by
    point character.
  - Checkpoint: `ryu_ken_post_boss_ko.mcs` (`18995e6d…`, untouched image).

### END-006 - Arcade reference for Ryu's ending and the post-boss dialogue

- **Status:** `DONE` (2026-10-24, `EXP-0042`)
- **Milestone:** M6 (reference; no Saturn change)
- **Dependencies:** END-001, REF-009.
- **Blockers:** None.
- **Objective:** Capture the arcade Japanese and official English versions of
  the same ending pages and dialogue.
- **Rationale:** The arcade is the primary translation oracle
  (`GATE-TRANSLATION`); the PS1 release is secondary.
- **Acceptance criteria:**
  - Scripted MAME runs reach Ryu's ending in `mshvsfj` and in
    `mshvsfu`/`mshvsf`, with a Ryu/Gouki team if one is reachable.
  - The screens are compared to the Saturn transcription.
  - The English source is located in ROM if possible (as in `EXP-0029`).
  - Gaps are recorded: lines with no English, and team-dependent dialogue.
- **Outputs:** Reference metadata and hashes. The text stays local.
- **Notes:** Do not assume the arcade text format equals the Saturn's
  (rule 14).
- **Evidence (2026-10-24, `EXP-0042`; `CONFIRMED`, discoveries `END-006`):**
  - The Saturn Japanese records (pages, and Ryu/Gouki boxes 1-4) are
    byte-identical in all three sets. The page tables are Japanese `0x20C14C`,
    English `0x20C1B4`, Spanish `0x20C21C`, and Portuguese `0x20C284` (Ryu =
    slot 9).
  - The MAME no-play route (forced stage 8 and boss vitality, at the Saturn's
    offsets) reached Ryu's ending in all three sets. It ran with Ken and, in
    `mshvsfu`/`mshvsfj`, with Gouki.
  - The English pages exist and were seen. The English dialogue is two generic
    partner lines (52-record table `0x22226C`), not a translation of the four
    Japanese boxes. The Ryu/Akuma lines were predicted, then seen.
  - Gap: no official English for the Saturn's four-box dialogue. Options are
    recorded in `EXP-0042` for the `END-010` scope decision.

### END-010 - Localize one Ryu ending

- **Status:** `DONE` (2026-10-24, `EXP-0044`; M7 complete)
- **Milestone:** M7
- **Dependencies:** END-001, END-002, END-004, END-005, END-006, END-007.
- **Blockers:** None. The dependencies are done: `END-005` (`EXP-0043`) maps the
  dialogue records. Ryu's pair is records 86-87, shared by every partner, and
  each partner p has the pair 16 + 2·p. The scope is decided (user,
  2026-10-24).
- **Objective:** Reproduce one Ryu ending localization from untouched source.
- **Rationale:** One complete case is required before generalizing endings.
- **Acceptance criteria:** Live/source behavior is experimentally established; official text provenance, exact modifications, deterministic build, and visible verification are documented.
- **Outputs:** M7 experiments, tools, local evidence, confirmed discoveries.
- **Notes:** Do not generalize from the first ending in this task.
  - **Scope (user decision, 2026-10-24):** "use the arcade's two official
    English partner lines for the post-boss dialogue, and the official English
    for the three ending pages."
    - Pages: English table `0x20C1B4`, slot 9 (`EXP-0042`), three records of
      2 × 25 cells into the three 2 × 19 Saturn page records.
    - Dialogue: the partner's line (record = partner slot) and Ryu's reply
      (record 35), from the table at `0x22226C`. The placeholder `0x0000`
      stays, filled from the name table.
    - Open design question for this task, to be decided by experiment, not
      assumed: the Saturn shows four boxes (two partner-specific, then two
      shared Ryu boxes, `EXP-0041`), and the English has two lines.
      - `EXP-0043` gives the mapping: English record p → `MC13` pair
        16 + 2·p (boxes 1-2), and English record 35 → `MC13` pair 86-87
        (boxes 3-4, Ryu).
      - How to show one line where the Saturn shows two boxes is untested. A
        blank record's behavior is unknown.
    - Names: English uses its own names (AKUMA for Gouki). The Saturn name
      table (WRAM-H, `EXP-0039`) holds Japanese names, and changing it may
      affect other screens. That is untested.
  - Route, from `EXP-0038` to `EXP-0040`:
    - pages are raw codes in `ME.PAC`, so they can be edited in place;
    - the dialogue is in LZSS `MC13.PAC` and needs a re-encode;
    - both use quote-font codes in 19 × 2 records, so composed pair glyphs
      (`FONT-003`) are a candidate for English.
  - `MC13` is the boss's quote file. Its win quotes stay with `SPECIAL-001`;
    only the dialogue records are in scope.
- **Evidence (2026-10-24, `EXP-0044`; `CONFIRMED`, discoveries `END-010`):**
  - **Pre-build trials:** a blank box is shown (not skipped), and `0x0000`
    works at any cell. The name table is in `MM.BIN` (`0x7D3C0`) and loads at
    boot.
  - **Build** (`caption_compiler.py` schema v3, spec from
    `official_endings.py`):
    - `MEMFIX` font: 81 pairs;
    - `MC13`: records 36-37, 46-47, 86-87;
    - `ME.PAC`: Ryu's pages;
    - `MM.BIN`: names and name length.
    - Track 01 `b481a4c6…`; two builds identical; all checks true.
  - **Live from a cold boot** (the user worked the menus;
    `tools/mednafen/ending_driver.py` forced stage 8 and the KO):
    - Ryu + Ken: "RYU," / "you're not bad." / "We shall meet again" / "KEN.".
    - Ryu + Gouki: "You are worthy" / "RYU." / "We shall meet again" /
      "AKUMA.".
    - Both: the three official English pages.
    - The first build left a blank cell after "RYU". That was traced to the
      name-length table (`MM.BIN` `0x96DE8`) and fixed.
  - **Regression:** reference `end010` regenerates the spec from the ROM and
    rebuilds to the same hash.
  - **Pitfall:** a state replay keeps the old quote font, because it is loaded
    after boot and stays resident. Live checks of font changes need a cold
    boot.
- **Layout revision (2026-10-24, user request, `EXP-0045`; `CONFIRMED`):**
  - Each English line is now shown whole in both boxes of its pair. Identical
    records hand over with no visible change (frame-level test), so the
    dialogue reads as two blocks of about 8 s each.
  - The `end010` reference was re-baselined to `ba3fb3ce…` (only `MC13.PAC`
    changes). It was verified by replaying the `EXP-0044` cold-boot states on
    the new image, for Ryu + Ken and Ryu + Gouki.

### END-020 - Generalize ending-localization pipeline

- **Status:** `DONE` (2026-10-25; M8 complete, via `END-021` to `END-026`)
- **Milestone:** M8
- **Dependencies:** END-010, END-021, END-022, END-023, END-024, END-025.
- **Blockers:** None. Ryu's ending is localized reproducibly (`EXP-0044`).
- **Objective:** Validate a general ordinary-character ending workflow.
- **Rationale:** One ending cannot establish format coverage or capacity constraints.
- **Acceptance criteria:** Representative variation is tested; structured translations, deterministic builds, visible verification, and explicit exceptions support a general pipeline.
- **Outputs:** M8 tools, data, experiments, coverage and regression records.
- **Evidence:**
  - Variation: `END-021` census, all 17 roster slots; capacity measured.
  - Names: `END-022`, including growth and the side-effect policy.
  - Deterministic combined build: `END-023`, `m8_roster`.
  - Live sample: `END-024`, `END-026`, 6 roster endings in combined images
    (plus Ryu in M7), including the longest name, a grown name, 2- to 6-page
    endings, and Marvel and Capcom partners.
  - Exceptions and regression: `END-025`.
- **Notes:** Special cases remain excluded.
  - Starting points from M6/M7:
    - `official_endings.py` takes any point and partner slots;
    - `caption_compiler.py` v3 builds raw and LZSS ending files;
    - `ending_driver.py` reaches any ending live from a cold boot, with menus
      only;
    - `arcade_ending_route.py` reaches any arcade ending with no play.
  - Open items:
    - all 52 partner and point lines, and the remaining name and
      name-length entries;
    - combining with the M5 roster image in one spec;
    - the name side effect on Japanese text that still uses placeholders;
    - other characters' page capacity and dialogue line lengths;
    - the KO character's effect.

### END-021 - Census and capacity of the roster's endings

- **Status:** `DONE` (2026-10-24, `EXP-0046`)
- **Milestone:** M8
- **Dependencies:** END-010.
- **Blockers:** None.
- **Objective:** Check that every roster ending matches the arcade reference,
  has official English that fits, and that one font can hold it all.
- **Acceptance criteria:** A committed census (metadata only) and a measured
  capacity for the endings and for endings plus the M5 win quotes.
- **Evidence:**
  - `data/text/ending_census.json` (`tools/text/ending_census.py`): all 17
    slots are consistent (page counts, record identity, line fit). 75 pages;
    longest name 8 cells.
  - Capacity, combined with the M5 win quotes: 454 distinct pairs, using 206 of
    the 321 candidate kanji codes and 19,303 of 30,235 bytes. It fits.
  - At most 25 distinct glyphs per English page (Japanese pages use up to 34).

### END-022 - Name table: length growth and side effects

- **Status:** `DONE` (2026-10-24, `EXP-0047`; user decision recorded)
- **Milestone:** M8
- **Dependencies:** END-021.
- **Blockers:** None.
- **Objective:**
  - Test that a name-length increase works (BISON: 2 → 3 cells).
  - Find every text that inserts names (`0x0000`) and would show English names
    in a combined image.
- **Acceptance criteria:**
  - One RAM trial grows a name and its length on a post-KO checkpoint (for
    example, Ken's entry at 4 cells). The predicted shift and fit are observed,
    against a control.
  - An offline census lists every `0x0000` in the Saturn text tables (MC files,
    `MC13`, `ME.PAC`) that a combined image would leave in Japanese.
  - Each case is decided with the user: accept English names in Japanese text,
    or exclude it.
- **Evidence (2026-10-24, `EXP-0047`):**
  - **Growth `CONFIRMED`.** Ken's entry grown to four cells with length 4
    showed "ＡＢＣＤ、". With the length left at 2, it was truncated to
    "ＡＢ、". Only the name's line shifts.
  - **Census** (`tools/text/placeholder_census.py` →
    `data/text/placeholder_census.json`): 100 placeholders. A roster image
    makes 69 English and leaves 31 in Japanese text:
    - 13 in excluded characters' win quotes;
    - 16 in `MC13` pairs of excluded slots;
    - 1 in an unidentified Japanese-only text table in `MM.BIN` (`0x7CD90`;
      arcade `0x213F82`-`0x2147EC`; no English counterpart);
    - 1 false positive (an `MC11` offset table).
  - **Decision needed.** English names will show inside those Japanese lines,
    because the name table is global. Roster-only play is unaffected, except
    possibly the one `MM.BIN` line.
- **User decision (2026-10-24):** "Accept English names inside the remaining
  Japanese lines (excluded characters and the one MM.BIN line)."

### END-023 - Combined roster image (win quotes and endings)

- **Status:** `DONE` (2026-10-24, `EXP-0048`)
- **Milestone:** M8
- **Dependencies:** END-022.
- **Blockers:** None (`END-022` done).
- **Objective:** One deterministic image from the untouched source, holding:
  - the 17 M5 win-quote tables;
  - the 17 roster endings (pages, all roster partner and point pairs, `whole`
    layout);
  - the roster's English names and name lengths.
- **Acceptance criteria:**
  - A generator writes the combined v3 spec from the local ROM, with no text
    committed.
  - Two builds are identical, and all compiler checks are true.
  - Offline renders of every changed record are reviewed.
  - A regression reference is added.
- **Evidence (2026-10-24, `EXP-0048`; `CONFIRMED` offline):**
  - `official_endings.py --roster … --with-win-quotes` writes the combined
    spec.
  - Build `build/end023`: track 01 `c06cf0ef…`; two builds identical; all
    checks true.
  - 501 pair glyphs. The win-quote PAC files are byte-identical to the
    verified roster image's.
  - The 75 page and 68 dialogue records were rendered and read.
  - Regression reference `m8_roster` added; all six pass.

### END-024 - Live verification sample of the combined image

- **Status:** `DONE` (2026-10-25)
- **Milestone:** M8
- **Dependencies:** END-023.
- **Blockers:** None.
- **Objective:** Verify a representative sample live, from one cold boot.
- **Acceptance criteria:**
  - Endings for at least: Captain America (longest name, 6 pages), a 6-page
    Capcom ending (Zangief), Bison (name growth), Sakura (2 pages), and Dan
    (slot 18).
  - The partners cover Marvel and Capcom.
  - A win-quote spot check confirms that M5 still works in the combined image.
  - The user works only the menus; `ending_driver.py` forces stage 8 and the
    KO. The font stays resident, so all can run from one boot.
  - Every screenshot is read.
- **Evidence (2026-10-25, `EXP-0049`):**
  - From one cold boot of `c06cf0ef…`, five credits (Captain America + Ryu,
    Zangief + Spider-Man, Bison + Hulk, Sakura + Wolverine, Dan + Chun-Li) all
    showed the predicted English blocks with correct names (CAPTAIN AMERICA in
    8 cells; BISON grown to 3), then their official English pages.
  - Dan's last page is an empty box, as in the arcade English (the Japanese has
    完). That is faithful.
  - A first-fight forced KO failed: the boss vitality offsets do not apply to
    two-against-two fights. The option was removed.
- **User decision (2026-10-25):** the dictator's name is **VEGA**, as in the
  Saturn's art and voice. Text only; the art and audio are not changed.
  - Rebuilt as `build/end024_vega` (`e721a167…`). Only `MEMFIX.PAC` and
    `MM.BIN` change.
  - `m8_roster` was re-baselined.
- **VEGA image, one cold boot of `e721a167…`:**
  - The user won stage 1 with Vega + Ryu. Vega's win quote showed the
    official English ("You were foolish / to challenge me!", `MC0E.PAC`
    record 7).
  - Then the driver forced the boss and KO: "VEGA, / you are a great
    fighter." then "Our game is at its end, / RYU.", and Vega's three English
    pages.
  - Every acceptance criterion is met.

### END-025 - Coverage, exceptions, and regression for endings

- **Status:** `DONE` (2026-10-25)
- **Milestone:** M8
- **Dependencies:** END-024 (done).
- **Blockers:** None.
- **Objective:** Close M8.
- **Acceptance criteria:**
  - `docs/coverage_exceptions.md` lists the excluded endings and dialogue pairs
    (slots 0, 17, 19-25) with reasons.
  - The regression report includes the combined reference.
  - Remaining unknowns are recorded, such as the KO character's effect, the
    opponent's vitality in two-against-two fights, the CAPTAIN AMERICA
    centring, and whether Dan's empty last page should get "THE END".
- **Evidence (2026-10-25):**
  - `tools/text/ending_coverage.py` → `data/text/ending_coverage.json`
    (`00ba0672…`, metadata only). It lists every slot's pages, the slots that share
    them, the dialogue records, and arcade identity.
    - Excluded slots: 0, 17, 19-25.
    - Against the `m8_roster` image (`2a5b26b7…`), every byte outside the
      roster's targets is unchanged in `ME.PAC`, the decoded `MC13`, and
      `MM.BIN`.
  - `docs/coverage_exceptions.md` gains an Endings (M8) register:
    - scope;
    - accepted side effects: slot 0 shares Cyclops's pages, and slot 19
      shares Dan's Japanese pages;
    - exceptions with owners;
    - rules.
  - `docs/regression_report.md`: all six references pass, including
    `m8_roster` and `end010`, re-baselined in `EXP-0050`.
  - `docs/known_unknowns.md` gains "Endings: Open After M8".

### END-026 - Use the Saturn's names in the English text (Mech-Gouki, Gouki)

- **Status:** `DONE` (2026-10-25)
- **Milestone:** M8
- **Dependencies:** END-024.
- **Blockers:** None.
- **Objective:** Follow the Saturn's art and voice in the English text, as
  already done for VEGA. "Cyber Akuma" becomes "Mech-Gouki", and "Akuma" or
  "AKUMA" becomes "Gouki" or "GOUKI".
- **User decisions (2026-10-25):**
  - "Cyber Akuma" → "Mech-Gouki", because the Saturn's VS screen shows
    MECH-GOUKI.
  - "AKUMA" → "GOUKI" wherever it appears, for now.
  - Both are **provisional**: art and audio stay Japanese-release, and the
    final naming policy is `LOC-001` (`docs/localization_plan.md`).
- **Acceptance criteria:**
  - Every roster occurrence is changed (census in `EXP-0050`).
  - Deterministic build; all checks pass; renders read.
  - `m8_roster` and `end010` re-baselined; all references pass.
  - Live cold-boot checks of the Mech-Gouki page and of GOUKI (name and page
    text).
- **Evidence (`EXP-0050`):**
  - `build/end026` showed Vega's page "behind the Mech-Gouki!!" live.
  - `build/end027` (`2a5b26b7…`, reference `m8_roster`) showed:
    - "GOUKI, / you are a great fighter.";
    - Gouki's pages, with "Gouki";
    - the VS screen's own "GOUKI" and "MECH-GOUKI".
  - All references pass.

### LOC-001 - Final character-name policy across text, art, and audio

- **Status:** `BACKLOG`
- **Priority:** decide before a release (`REL-001`)
- **Milestone:** Reference
- **Dependencies:** END-026.
- **Blockers:** A user decision, after the evidence below.
- **User direction (2026-10-25):** build both conventions as parallel
  variants, both in English (`LOC-003`). Scope the art and voice (`LOC-002`
  to `LOC-005`); an in-game switch is a stretch goal (`LOC-006`). What remains
  here is which variant is the default and how releases present the two.
- **Objective (original):** Choose between:
  - the Saturn's names everywhere (current, text only);
  - US names everywhere (text, art, and announcer audio).

  Record the decision. The questions, the options, and every affected text
  site are in `docs/localization_plan.md`.
- **Rationale:** The text can follow either convention cheaply. Art and voice
  cannot (user, 2026-10-25: changing the names in text alone would need voice
  samples to stay consistent).
- **Acceptance criteria:**
  - An inventory of the screens and voice lines that show or speak the three
    regional names (Vega, Gouki, Mech-Gouki), with evidence.
  - A user decision recorded in `data/translations/README.md`.
  - If the decision changes the current text, the overrides are updated,
    rebuilt, and verified.
  - If it requires art or audio work, new tasks are created with their own
    experiments. Nothing is started without approval.

### FONT-010 - Identify the credits font and compare it with the US caption font

- **Status:** `DONE` (2026-10-25, `EXP-0051`)
- **Priority:** high (user)
- **Milestone:** Polish
- **Dependencies:** FONT-003.
- **Blockers:** None.
- **Objective:** Locate the font the staff credits use and describe it. Test the
  user's observation that it closely resembles the font the US arcade uses for
  post-fight captions and endings.
- **Observation (2026-10-25):**
  - The credits after the Vega ending (`local/end026/rec`, e.g. `f00009966`,
    `6fc4e105…`) draw a gold, gradient-shaded, slanted Latin font. It has
    upper and lower case, and is narrower than the full-width cells.
  - The captions and endings use pair glyphs composed from the quote font's
    white full-width Latin glyphs (`FONT-003`).
- **Acceptance criteria:**
  - The credits font is located with evidence: disc file and offset, or the
    VRAM/VDP1 or VDP2 source; tile format and size; palette; character set and
    code mapping.
  - It is compared with the US arcade caption font (MAME capture; see
    `REF-012`). Record whether they are similar, the same, or different.
  - Fit is assessed for the quote font's 16 × 16 4bpp cells: two characters
    per cell, colours or palette, lower case, and any glyphs missing for the
    official English.
  - Adoption is presented as a user decision, with the colour choice: keep
    white, or use the credits' gold. Nothing is adopted here.
- **Evidence (`EXP-0051`):**
  - The credits draw quote-font codes `0x1E0`-`0x25F` (`MEMFIX.PAC` entry 4,
    compressed):
    - `A`-`Z` at `0x210`, `a`-`z` at `0x231`, digits at `0x200`;
    - punctuation mapped in `tools/text/credits_font.py`.
  - They use the captions' own glyph routine (`0x0601CE00`, SCU DMA from
    `0x0601CEEC`): 16 × 16 4 bpp cells, one letter per cell, values 1-9
    gradient and `B` outline.
  - Credits palette: yellow to orange, with a purple outline. The caption bank
    `0x6030` uses only white `1` and black `F`.
  - Same style as the US arcade caption font (gold gradient, outline, slant),
    but twice as wide.
  - One glyph per cell does not fit 25-character lines. Two squeezed per cell
    fit (same capacity) and look like the arcade, with some thin glyphs
    needing tuning.
  - Mockups: `local/font010/`.

### FONT-011 - Compose caption and ending pair glyphs from the credits font

- **Status:** `DONE` (2026-10-25, `EXP-0052`)
- **Priority:** high (user)
- **Milestone:** Polish
- **Dependencies:** FONT-010 (done).
- **Blockers:** None for silver. Gold is blocked: the caption palette is
  generated at run time by code not yet found.
- **User decisions (2026-10-25):**
  - credits font, squeezed, in gold, with thin glyphs tuned;
  - then "Both: build silver, then dig".
- **Progress (`EXP-0052`):**
  - `glyph_style: credits` was added end to end.
  - The silver build is `build/font011` (`9246148f…`, reference
    `m8_roster_credits`). It was verified live: a win quote, the dialogue,
    and Ryu's pages.
  - Two shading bands with a 4-connected outline fit; the full gradient does
    not (40,852 bytes against 30,235).
  - Capital `W` still needs another design pass.
  - **Gold done (route 1):** three palette immediates in `MM.BIN` (`0x961E3`,
    `0x961FB`, `0x96233`, each set to `0x81`) put win quotes, ending pages, and
    dialogue in gold bank 1.
    - Option `--caption-palette gold`, reference `m8_roster_gold`
      (`3a6c485c…`).
    - Verified live: win quote, dialogue, and Ryu's pages. The change also
      colours excluded characters' Japanese windows gold.
  - **Capital `W` redesigned** and verified live; the gold image is now
    `e213140a…`.
  - **The release patch is now gold** (user request): `release/README.md`,
    record `release/m8_roster_gold.json` (`94b27498…`).
- **Objective:** Build the pair glyphs from the credits font instead of the
  white full-width glyphs, for win quotes and endings.
- **Acceptance criteria:**
  - `pair_font.py` gains a glyph-source option. The old source stays available,
    and the regression references keep their meaning.
  - A new combined reference is created: deterministic, all checks true, the
    capacity fits, and every changed render is read.
  - Before/after screenshots from a cold boot of one win quote and one ending.
  - `release/README.md` and the patch are updated.

### UI-002 - Make the "EASY" mode label English only

- **Status:** `DONE` (2026-10-25, `EXP-0053`)
- **Priority:** not set by the user
- **Milestone:** Polish
- **Dependencies:** None (shares method with `UI-001`).
- **Blockers:** None.
- **Objective:** The user reports that the "EASY" mode label on the mode
  select screen alternates with Japanese text. Show English only.
- **Acceptance criteria:** The same as `UI-001`:
  - frame-by-frame capture of both phases;
  - the source identified (glyph codes or art);
  - the US arcade behaviour recorded;
  - a fix chosen with the user;
  - built from the untouched source, with before/after frames and
    regression.
- **Notes:** The mode select screen appears in recordings (for example
  `local/end027/rec` around the character select). "PRESS START" was found to
  be quote-font sprites (bank `0x7000`, `EXP-0052`); check whether these
  labels are too.

### LOC-002 - Inventory and scope the name art and voice (Vega/Gouki/Mech-Gouki)

- **Status:** `DONE` (2026-10-25, `EXP-0054`)
- **Priority:** medium (user)
- **Milestone:** Reference
- **Dependencies:** END-026.
- **Blockers:** None.
- **Objective:** Find out what it would take to show the US names (Bison,
  Akuma, Cyber-Akuma) in the art and voice, and report the cost.
- **Progress (`EXP-0054`):**
  - The US art and text already exist on the Saturn disc for the life bars
    (BISON/AKUMA/CYBER-AKUMA cells; a BISON swap shown by replay), the ending
    speaker labels (`ME.PAC` table has "Akuma" and "Bison"), and the
    win-banner letters.
  - Menu and sound-test names are plain ASCII in `MM.BIN`.
  - Unknown: the VS-screen name art source (probably `SEL*.PAC`).
  - Voice: the announcer says names at character select and in the win
    announcement. Sound is software-mixed; the clips are most likely in the
    common bank `CMNSE.PAC`, whose format is not decoded.
  - Sourcing view in `docs/localization_plan.md`: PS1 first, if imports are
    needed.
- **Acceptance criteria:**
  - Every screen that shows a regional name as art is listed, with frames:
    character select, VS screen, life bars, win screen, ending speaker labels,
    and any other.
  - Every voice line that speaks one is listed, with timing.
  - For each item: the source file and format if found, or the next
    discriminating experiment.
  - A cost and risk estimate per item, plus the audio sourcing question
    (no source is assumed). Recorded in `docs/localization_plan.md`.

### LOC-003 - Two name variants as parallel patch paths

- **Status:** `DONE` (2026-10-25, `EXP-0059`). The switch is
  `official_endings --names saturn|us`. References: `m8_roster_gold` and
  `m8_roster_gold_us`. Patches are explained in `release/README.md`. The US
  variant is a preview until `LOC-004` replaces the name art. Its voice
  already uses the American name calls (`EXP-0058`).
- **Priority:** medium (user)
- **Milestone:** Polish
- **Dependencies:** LOC-002 (for the US variant's art and voice).
- **Blockers:** The US variant is not consistent until `LOC-004` (and
  `LOC-005`, if audio is in scope) is done.
- **Objective (user request, 2026-10-25):** Offer two builds, both translated
  to English:
  - the Saturn's Japanese-release names (Vega, Gouki, Mech-Gouki; current);
  - the American names (Bison, Akuma, Cyber-Akuma).
- **Acceptance criteria:**
  - One switch selects the variant: the text overrides now, the art and voice
    later.
  - Both variants build deterministically from the untouched source, and each
    has its own regression reference and patch (`make_patch --stem`).
  - `release/README.md` explains the choice.
- **Notes:** The text part is small: `NAME_OVERRIDES` and `TEXT_OVERRIDES`
  per variant. The first step can be text-only, built but not released until
  the art (and the voice, if in scope) match.

### LOC-004 - Replace the name art for the American-name variant

- **Status:** `READY` (2026-10-25: `LOC-003` is done)
- **Priority:** medium (user)
- **Milestone:** Polish
- **Dependencies:** LOC-002 (done), LOC-003.
- **Blockers:** none (`LOC-003` done, `EXP-0059`). Per `EXP-0054`, the work
  splits as follows:
  - life bars: copy the US cells already in the font;
  - speaker labels: the `ME.PAC` table already has Akuma and Bison;
  - menus and sound test: ASCII edits;
  - win banner: find its name string table;
  - VS screen: decode `SEL*.PAC`; if no US art exists, source it, PS1
    first.
- **Objective:** Redraw or re-letter each name graphic found by `LOC-002`, in
  the variant build only.
- **Acceptance criteria:** Each replaced graphic is documented (original and
  new bytes, offsets), with before/after screenshots from a cold boot and a
  regression reference.

### LOC-005 - Replace the announcer's name lines for the American-name variant

- **Status:** `READY` (2026-10-25: built into the US variant, `EXP-0059`; only the in-play listening check remains)
- **Priority:** medium (user)
- **Milestone:** Polish
- **Dependencies:** LOC-002, LOC-003.
- **Blockers:**
  - **done:** the switch is built into the US variant (`EXP-0059`,
    `US_VOICE_PATCHES`), and a cold boot loads the American calls. Remaining:
    hear "Bison", "Akuma" and "Cyber Akuma" in play, on the win screen and
    at character select (gameplay by the user);
  - a user decision on doing it. A clip source and an encoder are no longer
    needed.
- **Objective:** If approved, make the voice say the US names in the variant
  build.
- **Acceptance criteria:**
  - The sample format and locations are documented.
  - The clip source has user-approved provenance.
  - Before/after evidence and regression.

### LOC-006 - In-game option to switch the name variant (stretch)

- **Status:** `BACKLOG`
- **Priority:** stretch (user: "would be incredible", likely a very large
  effort)
- **Milestone:** Polish
- **Dependencies:** LOC-003, LOC-004, and LOC-005 if audio is included.
- **Blockers:** Feasibility unknown.
- **Objective:** Add an Options-menu entry that switches the names at run time.
- **Acceptance criteria (feasibility first):**
  - Where options are stored (RAM and backup RAM), and how the menu is drawn
    and laid out.
  - Whether both variants' text, names, art, and audio can be resident, or
    where they would be loaded from.
  - The code hooks needed. This would be the project's first SH-2 code patch,
    so it needs new tooling.
  - A cost estimate for the user before any implementation.

### UI-001 - Make the player-2 "PRESS START" prompt English only

- **Status:** `DONE` (2026-10-25, `EXP-0053`)
- **Priority:** not set by the user
- **Milestone:** Polish
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** The user reports that the top-right player-2 prompt alternates
  "PRESS START" with Japanese text. Show English only.
- **Observation (2026-10-25):** 1-second recordings of a stage-1 fight
  (`local/end024v/rec`) show only "PRESS START" and blank frames. So the
  alternation, if present, is faster or happens at other times. It is
  unconfirmed.
- **Acceptance criteria:**
  - A frame-by-frame capture from a saved state confirms and records the
    Japanese text, its cadence, and where it appears.
  - Its source is identified (font codes, sprite, or VDP2 art; compare the
    `EXP-0023` UI artwork codes) with evidence.
  - The US arcade set's behaviour at the same moment is recorded as the oracle
    (MAME).
  - The fix is chosen with the user: English text in its place, or "PRESS
    START" in both phases. It is built from the untouched source, with
    before/after frames and a regression reference.

### DOC-020 - Write a cross-game agent playbook (for an XvSF project)

- **Status:** `DONE` (2026-10-25)
- **Priority:** not set by the user
- **Milestone:** Documentation
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** A detailed agent file for repeating this process on X-Men vs.
  Street Fighter (Saturn). It describes:
  - the design decisions and their rationale;
  - the order of investigation and its decision points;
  - the tools and how they were validated;
  - the pitfalls and failed approaches;
  - the user's localization decisions.
- **Acceptance criteria:**
  - Every MSHvSF fact is labelled as such, with its evidence pointer. Each one
    becomes an investigation point ("verify on XvSF: …") and is never
    asserted for XvSF (`AGENTS.md` rules 13-15, 25).
  - It covers:
    - environment (the Mednafen agent interface, recorder, driver, locking);
    - source identity;
    - the win-quote path (RAM search, then file, LZSS, font, pair glyphs);
    - endings (renderer, tables, dialogue indexing, names);
    - capacity;
    - regression;
    - release patching;
    - names and localization policy;
    - working with the user (manual steps, gameplay only).
  - It lives in this repository (`docs/`) and is ready to copy into a new
    project.
- **Notes:** This does not start XvSF work, and XvSF remains unmodified here.
- **Evidence (2026-10-25):** `docs/playbook_cross_game.md`.
  - Every game fact is marked **MSHvSF**, with its evidence pointer
    (`EXP-*`, a discoveries heading, or a log entry), followed by a
    "Verify on XvSF" point. The only XvSF statements are the intake records
    already in `references/xmvsf/`, cited as records of the held files.
  - It covers environment and tools (agent interface, recorder, ending
    driver, client lock, replay limits, cold boot for font changes), source
    identity, the win-quote path, endings, capacity, regression, release,
    names, the user's decisions, working with the user, pitfalls, and a
    consolidated XvSF checklist.
  - It is self-contained apart from the MSHvSF evidence pointers, so it can
    be copied into a new XvSF repository.
  - Documentation only: no tool, data, or XvSF file changed.

### TXT-001 - Identify the Japanese-only text table in MM.BIN

- **Status:** `BACKLOG`
- **Priority:** low (one name placeholder; the text is not otherwise in scope)
- **Milestone:** Reference
- **Dependencies:** END-022.
- **Blockers:** None.
- **Objective:** Find where and when the Japanese dialogue table in `MM.BIN`
  (`0x7CC86`-`0x7D1DC`; arcade `0x213F82`-`0x2147EC`, used by code at
  `0x0B03BA`) is shown, and whose name its placeholder inserts.
- **Rationale:** It is the only placeholder in Japanese text that roster-only
  play might show with an English name (`EXP-0047`). No English counterpart
  exists in the arcade sets.
- **Acceptance criteria:** A write or read breakpoint, or an arcade trace,
  identifies the screen and trigger. The finding is recorded with evidence.

### SPECIAL-001 - Investigate Norimaro and other approved special cases

- **Status:** `BACKLOG`
- **Milestone:** M9
- **Dependencies:** END-020.
- **Blockers:** Ordinary caption and ending pipelines are not mature; no special case is authorized.
- **Objective:** Define and investigate separately approved cases lacking straightforward official equivalents.
- **Rationale:** Special cases need independent translation and technical evidence.
- **Acceptance criteria:** Each case receives explicit scope approval, legal/reference provenance, independent experiments, exact modifications, reproducible output, and regression evidence.
- **Outputs:** M9 task breakdown, experiments, translations, patch metadata.
- **Notes:** Norimaro is named as a possible case, not pre-authorized work.
