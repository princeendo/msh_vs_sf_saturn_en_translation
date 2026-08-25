# Dependency-Controlled Research Plan

This is an evidence gate, not a generic backlog. `AGENTS.md` is authoritative.
Statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and `REJECTED`.
At most one reverse-engineering experiment may be `IN_PROGRESS`.

## Current State

- Current milestone: **M0**, research environment bootstrap.
- Current active task: `EMU-002`.
- Reverse-engineering experiments in progress: none.
- Next research task: `EMU-002`.
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

- **Status:** `READY`
- **Milestone:** M0
- **Dependencies:** EMU-002.
- **Blockers:** None.
- **Objective:** Isolate runtime configuration, saves, screenshots, and logs from user-global state.
- **Rationale:** Hidden global settings make observations irreproducible.
- **Acceptance criteria:** Launch and reset procedures use an ignored local root; sanitized stable settings can be recorded; secrets and unstable identifiers are excluded.
- **Outputs:** `docs/mednafen.md`, ignored `local/mednafen/`.
- **Notes:** Configuration values must be tested rather than assumed.

### EMU-004 - Boot MSHvSF Saturn successfully

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-003, ENV-007.
- **Blockers:** Emulator/configuration and identified legal BIOS/game inputs are unavailable.
- **Objective:** Reach a documented normal game screen using the recorded inputs.
- **Rationale:** Later evidence is invalid without a reproducible baseline boot.
- **Acceptance criteria:** Exact command/configuration and observed endpoint are recorded; source hashes remain unchanged; local screenshot evidence and metadata are captured.
- **Outputs:** Experiment record, launch procedure, ignored screenshot.
- **Notes:** Boot alone does not verify cartridge or input.

### EMU-005 - Verify 4 MB RAM cartridge configuration

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-004.
- **Blockers:** No verified baseline boot exists.
- **Objective:** Confirm the required 4 MB cartridge operates in the research configuration.
- **Rationale:** Memory observations must use the correct runtime hardware model.
- **Acceptance criteria:** A controlled observation validates cartridge operation; setting, expected result, observed result, and uncertainty are recorded.
- **Outputs:** Experiment record, validated configuration guidance.
- **Notes:** A configuration value alone is not proof.

### EMU-006 - Configure fightpad

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-003, EMU-004.
- **Blockers:** The physical device/OS identity is unknown and no verified game boot exists.
- **Objective:** Map one identified physical fightpad to Saturn controls locally.
- **Rationale:** Manual checkpoint capture depends on reliable controls.
- **Acceptance criteria:** Device and connection are documented without unnecessary identifiers; D-pad, A/B/C/X/Y/Z, L/R, and Start mappings are configured.
- **Outputs:** Ignored local configuration, mapping draft in `docs/mednafen.md`.
- **Notes:** Runtime validation occurs in `EMU-007`.

### EMU-007 - Document fightpad mapping

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-006.
- **Blockers:** No configured mapping exists.
- **Objective:** Validate and document every required input in game.
- **Rationale:** Configuration labels do not prove intended runtime behavior.
- **Acceptance criteria:** Expected and observed behavior are recorded for all mapped controls and useful emulator shortcuts, including save/load, screenshot, pause, frame advance, and slot selection where available.
- **Outputs:** Verified mapping table and input experiment record.
- **Notes:** Unavailable shortcuts remain explicit rather than invented.

### EMU-008 - Verify screenshot capture

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-004, EMU-005.
- **Blockers:** Verified boot and cartridge operation are incomplete.
- **Objective:** Capture reproducible visual evidence from a described scene.
- **Rationale:** M1 and M2 require before/after evidence.
- **Acceptance criteria:** Capture action, state, configuration, filename, size, hash, and local storage are recorded; image remains ignored.
- **Outputs:** Screenshot experiment, procedure, ignored evidence.
- **Notes:** A screenshot does not prove binary provenance.

### EMU-009 - Verify save/load states

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-005, EMU-007, EMU-008.
- **Blockers:** Runtime, controls, and screenshots are not validated.
- **Objective:** Repeatedly return to an equivalent documented checkpoint.
- **Rationale:** Differential experiments need controlled starting conditions.
- **Acceptance criteria:** Save/load actions, slot/path, hashes, timing caveats, and at least two repeat observations are recorded; state files remain ignored and are not diffed as RAM.
- **Outputs:** Save-state experiment and checkpoint procedure.
- **Notes:** Equivalent visible state need not imply byte-identical RAM.

### EMU-010 - Verify debugger access

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-005, EMU-009.
- **Blockers:** Deterministic stock runtime is unavailable.
- **Objective:** Enter, operate, and exit the stock interactive debugger against MSHvSF.
- **Rationale:** M1 requires developer-level memory inspection and controlled writes.
- **Acceptance criteria:** Exact invocation/actions demonstrate pause/resume and read-only inspection; source/configuration identities are linked; no caption conclusion is drawn.
- **Outputs:** Debugger smoke-test experiment.
- **Notes:** Do not modify Mednafen.

### EMU-011 - Document debugger workflow

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-010.
- **Blockers:** Interactive access has not been observed.
- **Objective:** Record exact stock actions for memory reads/writes, dumps, registers, stepping, and breakpoints as available.
- **Rationale:** Later experiments must be reproducible by another session.
- **Acceptance criteria:** Each command is tied to the tested version and observed outcome; unsupported or unreliable actions are explicit.
- **Outputs:** `docs/mednafen.md` capability/runbook update.
- **Notes:** Documentation is not evidence until actions are tested.

### EMU-012 - Determine stock Mednafen memory-workflow sufficiency

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-011, DBG-011.
- **Blockers:** Stock debugger and checkpoint/dump workflow have not been exercised end to end.
- **Objective:** Decide whether repeatable memory dump/read/write workflows needed for M1 are satisfactory.
- **Rationale:** Custom emulator work is prohibited until a concrete stock limitation is demonstrated.
- **Acceptance criteria:** A capability matrix records each requirement, experiment, result, reliability, and blocker; conclusion is `SUPPORTED` by observed workflows.
- **Outputs:** Sufficiency decision in `docs/mednafen.md` and `research_log.md`.
- **Notes:** Insufficiency does not itself authorize modification.

### EMU-020 - Evaluate agent automation limitations

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-012.
- **Blockers:** Stock capability assessment is incomplete.
- **Objective:** If needed, document current versus required capability, why stock is inadequate, smallest modification, maintenance cost, and alternatives.
- **Rationale:** Any custom interface must solve a demonstrated problem with minimal scope.
- **Acceptance criteria:** The review either rejects modification or proposes one minimal, explicitly authorized follow-up; upstream provenance and patch workflow requirements are stated.
- **Outputs:** `docs/mednafen_agent_interface.md`, decision log.
- **Notes:** No Mednafen edit occurs in this task.

## Phase D: Reference Text

### REF-001 - Choose initial Ryu post-fight quote

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DOC-006, EMU-007.
- **Blockers:** Quote-reference provenance and a reliable route to captions are unavailable.
- **Objective:** Select one ordinary Ryu caption with reproducible Japanese and official English contexts.
- **Rationale:** M1 needs one fixed subject rather than broad quote work.
- **Acceptance criteria:** Selection rationale, release contexts, route, and unresolved correspondence questions are recorded without inventing a match.
- **Outputs:** Structured draft under `data/translations/`.
- **Notes:** Ryu remains preferred unless evidence justifies another fighter.

### REF-002 - Capture Japanese Saturn screenshot

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** REF-001, EMU-008, EMU-009.
- **Blockers:** Quote selection and capture workflow are incomplete.
- **Objective:** Capture the selected Japanese caption in a deterministic scene.
- **Rationale:** Exact visible evidence anchors transcription and memory analysis.
- **Acceptance criteria:** Release/run/state identity, capture method, image hash, and visible context are recorded; screenshot remains ignored.
- **Outputs:** Local screenshot and tracked metadata.
- **Notes:** Do not infer storage from appearance.

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
- **Dependencies:** REF-003, DOC-006.
- **Blockers:** Japanese context and authoritative English-reference access are incomplete.
- **Objective:** Establish the official arcade English counterpart using contextual evidence.
- **Rationale:** The project uses official text where available.
- **Acceptance criteria:** Exact text, formatting, release provenance, context, evidence, and correspondence confidence are recorded; unsupported matches are rejected.
- **Outputs:** Updated translation record and reference evidence.
- **Notes:** Matching character alone is insufficient evidence.

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

## Phase E: Checkpoints And Memory Analysis

### DBG-001 - Capture state A before fight end

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** REF-003, EMU-009.
- **Blockers:** Selected scene and validated save-state workflow are unavailable.
- **Objective:** Save a reproducible checkpoint shortly before the fight ends.
- **Rationale:** State A supplies the pre-caption comparison baseline.
- **Acceptance criteria:** Route, timing, run/configuration, save hash, screenshot metadata, and two reload observations are recorded.
- **Outputs:** Ignored save/screenshot and tracked checkpoint metadata.
- **Notes:** The compressed save state is not a RAM dump.

### DBG-002 - Capture state B after KO/before caption

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-001.
- **Blockers:** State A and practical transition timing are unavailable.
- **Objective:** Capture the transition before the caption is fully displayed, if practical.
- **Rationale:** An intermediate state may distinguish loading from display changes.
- **Acceptance criteria:** A repeatable state and timing are recorded, or evidence documents why it is impractical and authorizes the three-state strategy.
- **Outputs:** Checkpoint metadata and local evidence, or documented rejection.
- **Notes:** Do not force a noisy checkpoint merely to satisfy four-state nomenclature.

### DBG-003 - Capture state C with caption fully visible

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-001, REF-003.
- **Blockers:** Reproducible route and selected transcription are incomplete.
- **Objective:** Save a stable checkpoint with the target caption fully visible.
- **Rationale:** This is the primary M1 mutation checkpoint.
- **Acceptance criteria:** Scene identity, timing, save hash, screenshot metadata, and two reload observations are recorded.
- **Outputs:** Ignored save/screenshot and tracked checkpoint metadata.
- **Notes:** Ensure the selected visible text matches `REF-003`.

### DBG-004 - Capture state D after caption disappears

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-003.
- **Blockers:** State C is unavailable.
- **Objective:** Capture a repeatable checkpoint immediately after caption disappearance.
- **Rationale:** Disappearing data can help rank runtime candidates.
- **Acceptance criteria:** State, timing, hash, screenshot metadata, and repeatability are recorded; if impractical, the three-state fallback is justified.
- **Outputs:** Checkpoint metadata and local evidence, or documented rejection.
- **Notes:** Checkpoint practicality is an experimental result.

### DBG-005 - Capture screenshots for each checkpoint

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-001, DBG-002, DBG-003, DBG-004.
- **Blockers:** The final checkpoint set is not established.
- **Objective:** Tie every used checkpoint to visible evidence.
- **Rationale:** Dump comparisons need scene and timing context.
- **Acceptance criteria:** Each retained state has screenshot filename, size, SHA-256, capture action/order, and run identity; binaries remain ignored.
- **Outputs:** Local screenshots and tracked evidence manifest.
- **Notes:** Rejected optional states need no fabricated screenshot.

### DBG-006 - Create Python utility to dump defined memory regions

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** ENV-004, EMU-011.
- **Blockers:** The tested stock debugger export mechanism is unknown.
- **Objective:** Script repeatable acquisition of explicitly defined address ranges where stock facilities permit it.
- **Rationale:** Identical raw ranges are required for meaningful differential analysis.
- **Acceptance criteria:** The utility validates address/length and output path, defaults away from tracked/source paths, records metadata, has synthetic tests where practical, and documents any unavoidable manual debugger step.
- **Outputs:** `tools/memory/` utility, tests, usage documentation.
- **Notes:** Do not invent an emulator interface.

### DBG-007 - Dump WRAM-L for each state

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-005, DBG-006.
- **Blockers:** Checkpoints and dump utility/workflow are unavailable.
- **Objective:** Export `0x00200000-0x002FFFFF` identically from every retained state.
- **Rationale:** Stable raw dumps, not compressed save files, support comparison.
- **Acceptance criteria:** Every dump has expected/actual size, SHA-256, exact command/action, checkpoint linkage, and repeat acquisition; binaries remain ignored.
- **Outputs:** Local WRAM-L dumps and tracked metadata.
- **Notes:** Validate the supplied range against collected platform references before interpreting it.

### DBG-008 - Dump WRAM-H for each state

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-005, DBG-006.
- **Blockers:** Checkpoints and dump utility/workflow are unavailable.
- **Objective:** Export `0x06000000-0x060FFFFF` identically from every retained state.
- **Rationale:** Both initially prioritized work-RAM regions must be tested before expansion.
- **Acceptance criteria:** Every dump has expected/actual size, SHA-256, exact command/action, checkpoint linkage, and repeat acquisition; binaries remain ignored.
- **Outputs:** Local WRAM-H dumps and tracked metadata.
- **Notes:** No subrange is presumed to contain captions.

### DBG-009 - Create memory diff tooling

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** ENV-004, DBG-007, DBG-008.
- **Blockers:** Validated paired dumps do not exist.
- **Objective:** Report contiguous changed/unchanged ranges and byte counts in human-readable and JSON forms.
- **Rationale:** Structured results are more reproducible than per-byte terminal output.
- **Acceptance criteria:** Equal-size/range validation, base addresses, input hashes, deterministic contiguous regions, optional unchanged ranges, JSON schema, and synthetic tests are implemented.
- **Outputs:** `tools/memory/` diff tool and tests.
- **Notes:** Results report facts, not candidate meaning.

### DBG-010 - Create binary/Shift-JIS search tooling

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** ENV-004, REF-003.
- **Blockers:** Validated environment and reviewed Japanese transcription are incomplete.
- **Objective:** Search exact byte patterns and user-specified encoded strings in dumps/files.
- **Rationale:** Shift-JIS is the first hypothesis, not a built-in conclusion.
- **Acceptance criteria:** Tool supports raw patterns, explicit encodings including Shift-JIS, multiple/no matches, base address, JSON output, input hashes, hexdump context, and synthetic tests.
- **Outputs:** `tools/text/` search tool and tests.
- **Notes:** Entropy/candidate ranking is added only when a demonstrated experiment needs it.

### DBG-011 - Compare checkpoint memory dumps

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** DBG-007, DBG-008, DBG-009, DBG-010.
- **Blockers:** Dumps and analysis tools are unavailable.
- **Objective:** Compare A->B, B->C, C->D, or justified three-state equivalents and run the first Shift-JIS search hypothesis.
- **Rationale:** Controlled temporal differences can rank candidate caption representations.
- **Acceptance criteria:** One significant experiment records exact inputs/hashes, one hypothesis, comparisons/searches, predicted and actual results, stable versus noisy observations, conclusion, and next discriminating experiment.
- **Outputs:** Experiment record, JSON summaries, `research_log.md` update.
- **Notes:** A match is at most `SUPPORTED` until a controlled visible mutation confirms causality.

## M0 Gate

### GATE-M0 - Confirm environment and checkpoint prerequisites

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** ENV-001, ENV-002, ENV-003, ENV-004, ENV-005, ENV-006, ENV-007, DOC-001, DOC-002, DOC-003, DOC-004, DOC-005, DOC-006, DOC-007, DOC-008, EMU-001, EMU-002, EMU-003, EMU-004, EMU-005, EMU-006, EMU-007, EMU-008, EMU-009, EMU-010, EMU-011, EMU-012, EMU-020, REF-001, REF-002, REF-003, REF-004, REF-005, DBG-001, DBG-003, DBG-005, DBG-006, DBG-007, DBG-008, DBG-009, DBG-010, DBG-011.
- **Blockers:** Listed M0 prerequisites are not all `DONE`.
- **Objective:** Make an explicit go/no-go decision before the first live RAM mutation.
- **Rationale:** Partial setup must not be mistaken for permission to start M1.
- **Acceptance criteria:** Every dependency is `DONE`; optional `REF-006`, state B, and state D have either evidence or documented rejection/fallback; no unresolved workflow blocker can invalidate M1 evidence.
- **Outputs:** M0 acceptance entry and updated current state.
- **Notes:** Do not waive failed criteria to advance the milestone.

## Gated Reverse Engineering

### RE-012 - Identify and modify runtime buffer for one Ryu quote

- **Status:** `BLOCKED`
- **Milestone:** M1
- **Dependencies:** GATE-M0.
- **Blockers:** M0 is not confirmed.
- **Objective:** Identify the runtime representation responsible for the selected Ryu caption and visibly change it with one controlled RAM mutation.
- **Rationale:** This is the minimum causal proof linking runtime bytes to the caption.
- **Acceptance criteria:** Candidate range is identified; exact original/modified bytes and address are recorded; mutation changes the intended visible caption while unrelated content is assessed; before/after screenshots and deterministic checkpoint are recorded; the result repeats from a clean checkpoint; experiment, log, and confirmed discovery are updated.
- **Outputs:** `research/experiments/EXP-NNNN/`, local evidence, `research_log.md`, `docs/discoveries.md`.
- **Notes:** Do not claim whether bytes are source text, glyph indices, or an intermediate buffer without a separate experiment.

### DISC-001 - Trace confirmed Ryu runtime caption to disc source

- **Status:** `BLOCKED`
- **Milestone:** M2
- **Dependencies:** RE-012.
- **Blockers:** No M1-confirmed runtime representation exists.
- **Objective:** Determine what populates the confirmed runtime bytes and identify the source file, offset/structure, and transformations.
- **Rationale:** A RAM mutation is not a reproducible disc localization.
- **Acceptance criteria:** Controlled tracing links runtime data to source; pointers, lengths, compression, checksums, and alignment are tested as applicable; all factual offsets/bytes and uncertainty are recorded.
- **Outputs:** Source-trace experiment and confirmed documentation where warranted.
- **Notes:** A string-like disc match alone is insufficient.

### DISC-002 - Reproduce same Ryu caption from patched disc

- **Status:** `BLOCKED`
- **Milestone:** M2
- **Dependencies:** DISC-001.
- **Blockers:** Disc source and constraints are not confirmed.
- **Objective:** Patch or rebuild from an untouched, identity-verified source into a distinct `build/` output and reproduce the M1 caption.
- **Rationale:** M2 proves a deterministic source-to-visible-output pipeline.
- **Acceptance criteria:** Tool validates source hashes and never overwrites originals; original/modified bytes and file offset/purpose are recorded; repeated builds are deterministic or understood; a fresh boot/checkpoint visibly reproduces the expected English caption; source hashes remain unchanged; tests, experiment, log, and discoveries are updated.
- **Outputs:** Patch/build tool, synthetic tests, local derived image/evidence, tracked metadata and documentation.
- **Notes:** Do not generalize during M2.

### RE-020 - Handle multiple Ryu captions programmatically

- **Status:** `BACKLOG`
- **Milestone:** M3
- **Dependencies:** DISC-002.
- **Blockers:** M2 is not confirmed.
- **Objective:** Extend the confirmed mechanism to multiple Ryu captions through structured data and tooling.
- **Rationale:** Generalization begins only after untouched-source reproduction.
- **Acceptance criteria:** Detailed subtasks are added from M2 evidence; multiple Ryu cases build and verify reproducibly; shared and variant behavior are experimentally supported.
- **Outputs:** M3 experiments, structured records, justified tooling.
- **Notes:** Do not include another fighter yet.

### RE-030 - Apply generalized mechanism to a second fighter

- **Status:** `BACKLOG`
- **Milestone:** M4
- **Dependencies:** RE-020.
- **Blockers:** Multiple Ryu captions are not handled programmatically.
- **Objective:** Demonstrate the same evidence-backed mechanism for one ordinary second fighter.
- **Rationale:** A second fighter tests whether Ryu-specific assumptions were generalized prematurely.
- **Acceptance criteria:** Fighter selection and detailed tests are based on M3 evidence; fresh builds and visible results reproduce; exceptions remain explicit.
- **Outputs:** M4 experiment and documentation updates.
- **Notes:** Exclude special cases.

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
