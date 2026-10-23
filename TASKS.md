# Dependency-Controlled Research Plan

This is an evidence gate, not a generic backlog. `AGENTS.md` is authoritative.
Statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and `REJECTED`.
At most one reverse-engineering experiment may be `IN_PROGRESS`.

## Current State

- Current milestone: **M4**: a second fighter through the same mechanism. M3 was
  completed on 2026-10-17 (`RE-020`; `EXP-0026`, `EXP-0027`).
- Reverse-engineering experiments in progress: none.
- Current active task: `RE-030`. `EXP-0028` Phase A is done; **Phase B is on hold
  at the user's request (2026-10-23)**. Resume steps are in
  `research/experiments/EXP-0028/README.md`, under "Resume: Phase B".
- Next research task: `EXP-0028` Phase B: one session, team Ken + Ryu, KO with
  Ken, then KO with Ryu. Full English still waits on `GATE-TRANSLATION`.
- `REF-008` is done (2026-10-23): the arcade sets are identified, and regional
  claims are recorded. Arcade capture needs `REF-009` (MAME plus key files), which
  is blocked on user-supplied files.
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

- **Status:** `READY`
- **Milestone:** M0
- **Dependencies:** ENV-005.
- **Blockers:** None for bibliography research.
- **Objective:** Catalog relevant predecessor research for later, question-driven comparison.
- **Rationale:** XvSF can suggest a discriminating experiment but cannot answer an MSHvSF question by analogy.
- **Acceptance criteria:** Sources, provenance, licenses, potential relevance, and strict non-transfer assumptions are recorded.
- **Outputs:** `docs/references.md`, permitted reference notes.
- **Notes:** Do not modify or begin comparative analysis of XvSF here.

### DOC-008 - Create concise internal Markdown summaries for agent use

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DOC-001, DOC-002, DOC-003, DOC-004, DOC-005, DOC-006, DOC-007.
- **Blockers:** The source corpus has not been collected and evaluated.
- **Objective:** Summarize task-relevant facts with links back to authoritative references.
- **Rationale:** Agents need concise, citable context rather than bulk documents.
- **Acceptance criteria:** Summaries identify supported claims, citations, conflicting evidence, and unresolved questions without overstating confidence.
- **Outputs:** Updated technical files under `docs/`.
- **Notes:** Keep discovery claims separate from platform/reference summaries.

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

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** REF-002.
- **Blockers:** No verified screenshot exists.
- **Objective:** Record exactly what is visibly displayed, including line breaks and punctuation.
- **Rationale:** Encoding searches require a reviewable transcription.
- **Acceptance criteria:** Transcription is independently reviewed against evidence; ambiguities and unreadable glyphs remain explicit.
- **Outputs:** Updated translation record.
- **Notes:** Transcription does not imply Shift-JIS encoding.

### REF-004 - Identify corresponding arcade English quote

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** REF-003, DOC-006, REF-009.
- **Blockers:** Japanese context and authoritative English-reference access are incomplete.
- **Objective:** Establish the official arcade English counterpart using contextual evidence.
- **Rationale:** The project uses official text where available.
- **Acceptance criteria:** Exact text, formatting, release provenance, context, evidence, and correspondence confidence are recorded; unsupported matches are rejected.
- **Outputs:** Updated translation record and reference evidence.
- **Notes:** Matching character alone is insufficient evidence. The user reports
  that US and EU arcade ROMs with English text are available locally. Record their
  identities against the MAME catalog before use. The sets (EU, US, and JP) are now
  in `local/arcade_roms/mshvsf/`; see `references/mshvsf/arcade/README.md`. Their
  audit and regional-difference documentation is `REF-008`. Because Saturn quote
  selection varies after the KO (`EXP-0009`), correspondence may need memory-level
  evidence, such as a quote index, rather than a reproduced context.

### REF-005 - Record PS1 English equivalent if useful

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** REF-004.
- **Blockers:** Primary correspondence has not been established.
- **Objective:** Record the official PS1 wording and differences when it adds useful evidence.
- **Rationale:** A secondary rendering can clarify language but not Saturn implementation.
- **Acceptance criteria:** Provenance, exact text/context, comparison, and uncertainty are recorded, or a documented decision explains why it is not useful.
- **Outputs:** Updated translation record.
- **Notes:** Do not infer shared binary structures.

### REF-006 - Capture Japanese arcade material if useful

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** REF-004.
- **Blockers:** The need for an additional correspondence test has not been established.
- **Objective:** Use Japanese arcade evidence only if it discriminates competing quote correspondences.
- **Rationale:** Additional reference work should answer a specific question.
- **Acceptance criteria:** The question, provenance, context comparison, result, and remaining uncertainty are recorded, or the task is `REJECTED` as unnecessary.
- **Outputs:** Reference experiment and translation-record update if run.
- **Notes:** This is optional evidence, not a gate when unnecessary.

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
  - Each zip lacks its 20-byte `.key` file. MAME is not installed, so the
    refusal is expected, not observed.
  - Regional claims RC-1 to RC-6 are recorded as `HYPOTHESIS`, with sources, in
    `references/mshvsf/arcade/README.md` and `docs/references.md`. The TCRF arcade
    page could not be read (bot check) and remains a lead.
  - Text location and form remain `UNKNOWN`.
  - Follow-up proposed: `REF-009`. Captures stay under `REF-004`, which also needs
    `REF-003`.

### REF-009 - Pin a MAME build and complete the arcade sets for capture

- **Status:** `BLOCKED`
- **Milestone:** M0 (reference tooling; no reverse engineering)
- **Dependencies:** REF-008.
- **Blockers:** No MAME build is installed, and the three CPS-II `.key` files are
  missing. The user must supply legal copies; agents must not download ROM or key
  files.
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

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DOC-007, DOC-008, REF-003, REF-004, REF-005.
- **Blockers:** Listed reference and documentation tasks are not all `DONE`.
- **Objective:** Make an explicit go/no-go decision before any task writes or
  proposes English replacement text.
- **Rationale:** The source quote must be reviewed and the official English must be
  established before translation work. They are not needed to test whether a RAM
  location drives the display.
- **Acceptance criteria:** Every dependency is `DONE`. Optional `REF-006` has
  evidence or a documented rejection.
- **Outputs:** Gate acceptance entry.
- **Notes:** Created 2026-10-15 by splitting the original GATE-M0.

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

- **Status:** `BLOCKED`
- **Milestone:** M2
- **Dependencies:** DISC-002, FONT-001, FONT-002, LAYOUT-001, GATE-TRANSLATION.
- **Blockers:** Translation prerequisites (`GATE-TRANSLATION`) and Latin glyph
  codes (`FONT-001`) are incomplete.
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

- **Status:** `IN_PROGRESS` (`EXP-0028` Phase A done 2026-10-23; Phase B on hold, see
  its "Resume: Phase B" section)
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
    Then 32 forced records are verified automatically.

### RE-040 - Systematize ordinary post-fight localization

- **Status:** `BACKLOG`
- **Milestone:** M5
- **Dependencies:** RE-030.
- **Blockers:** A second fighter has not validated the generalized mechanism.
- **Objective:** Build and validate the ordinary-character post-fight workflow.
- **Rationale:** Roster-scale work requires evidence-backed coverage and regression controls.
- **Acceptance criteria:** Detailed tasks define scope, translation provenance, binary traceability, deterministic builds, representative visible verification, exceptions, and regression tests.
- **Outputs:** Ordinary-caption data, tools, coverage manifest, experiments, regression report.
- **Notes:** Endings and special cases remain prohibited.

### END-001 - Begin ending-text investigation

- **Status:** `BACKLOG`
- **Milestone:** M6
- **Dependencies:** RE-040.
- **Blockers:** The ordinary post-fight pipeline is not mature.
- **Objective:** Observe ending text and design the first independent discriminating experiments.
- **Rationale:** Ending storage/rendering must not be inferred from captions.
- **Acceptance criteria:** Detailed tasks are created from observations; hypotheses and checkpoint needs are explicit; no structural equivalence is assumed.
- **Outputs:** M6 observations, task breakdown, unknowns, experiment designs.
- **Notes:** M6 begins investigation; it does not imply a working ending patch.

### END-010 - Localize one Ryu ending

- **Status:** `BACKLOG`
- **Milestone:** M7
- **Dependencies:** END-001.
- **Blockers:** Ending investigation has not established an actionable pipeline.
- **Objective:** Reproduce one Ryu ending localization from untouched source.
- **Rationale:** One complete case is required before generalizing endings.
- **Acceptance criteria:** Live/source behavior is experimentally established; official text provenance, exact modifications, deterministic build, and visible verification are documented.
- **Outputs:** M7 experiments, tools, local evidence, confirmed discoveries.
- **Notes:** Do not generalize from the first ending in this task.

### END-020 - Generalize ending-localization pipeline

- **Status:** `BACKLOG`
- **Milestone:** M8
- **Dependencies:** END-010.
- **Blockers:** No Ryu ending is localized reproducibly.
- **Objective:** Validate a general ordinary-character ending workflow.
- **Rationale:** One ending cannot establish format coverage or capacity constraints.
- **Acceptance criteria:** Representative variation is tested; structured translations, deterministic builds, visible verification, and explicit exceptions support a general pipeline.
- **Outputs:** M8 tools, data, experiments, coverage and regression records.
- **Notes:** Special cases remain excluded.

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
