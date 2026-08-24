# Agent Operating Contract

This file is authoritative for every AI-agent session in this repository. The
project is an empirical reverse-engineering investigation, not a speculative
implementation exercise.

## Required Method

Use this cycle for each investigation:

```text
OBSERVE -> FORM ONE HYPOTHESIS -> DESIGN A DISCRIMINATING EXPERIMENT
        -> RUN IT -> RECORD RESULT -> ACCEPT / REJECT / REFINE
        -> UPDATE DOCUMENTATION
```

Use confidence labels precisely:

- **UNKNOWN**: no meaningful conclusion yet.
- **HYPOTHESIS**: plausible explanation with insufficient experimental evidence.
- **SUPPORTED**: evidence is consistent, but alternatives remain.
- **CONFIRMED**: a controlled experiment produced the predicted result and is
  reproducible.
- **DISPROVEN**: evidence contradicts the hypothesis.

Plausibility, visual similarity, a matching byte sequence, or an analogous game
is not confirmation.

## Mandatory Rules

1. Never modify original disc images. Derived builds go under `build/` and patch
   commands default to a distinct output path.
2. Record SHA-256, size, filename, and release description for every source-image
   component before research.
3. Never treat a hypothesis as fact or invent missing addresses, offsets, text,
   citations, correspondences, commands, or results.
4. Test one controlled hypothesis at a time when practical. Prefer experiments
   that change exactly one variable.
5. Document every confirmed discovery in `docs/discoveries.md` with evidence and
   reproduction instructions.
6. Record plausible but disproven hypotheses in `research_log.md` so future agents
   do not unknowingly retry them.
7. Do not bypass a blocker or dependency in `TASKS.md`.
8. Do not begin a later milestone because it appears easy. Nothing past M1 begins
   before M1 is confirmed; no generalization begins before M2 works from an
   untouched source image.
9. Preserve exact commands, tool versions, inputs, outputs, and hashes required to
   reproduce results.
10. Prefer reusable scripted extraction and analysis over undocumented manual work.
11. Support visible game modifications with before/after screenshots or equivalent
    evidence and a deterministic checkpoint.
12. For every binary modification, record original bytes, modified bytes, file
    offset or memory address, purpose, expected result, and observed result.
13. Never assume XvSF and MSHvSF share structures, offsets, encodings, functions,
    memory addresses, or renderer behavior.
14. Never assume CPS-II, PlayStation, and Saturn structures are identical.
15. Use reference releases as evidence and translation oracles, not templates.
16. Before modifying Mednafen, complete `EMU-012` and document why stock Mednafen
    is insufficient in `EMU-020`.
17. If Mednafen modification is authorized, make the smallest useful change and
    preserve upstream URL, version/revision, patches, rationale, and build steps.
18. Python 3.12+ is the default implementation language. Avoid large dependencies
    without a demonstrated need.
19. Run Python tooling through `./invenv.sh`; do not rely on an activated shell.
20. Update `TASKS.md` and `research_log.md` before ending a substantial session.
21. Never commit copyrighted game images, BIOS files, extracted game contents,
    save states, memory dumps, screenshots, or emulator binaries.
22. Keep binary evidence locally under ignored paths. Commit hashes, addresses,
    scripts, schemas, small synthetic fixtures, and derived factual metadata.
23. Do not work on endings before the post-fight pipeline is proven and generalized.
24. Do not work on Norimaro or other special cases before the ordinary-character
    pipeline is mature and a task explicitly permits it.
25. Do not modify XvSF.

## Task Discipline

Allowed statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and
`REJECTED`. Keep at most one reverse-engineering experiment `IN_PROGRESS`. Code or
notes alone do not make a task `DONE`; all acceptance criteria must be supported by
evidence. If prerequisites change, update dependencies and blockers before work.

When blocked, state the unknown, available evidence, competing explanations, and
the smallest discriminating experiment. Do not respond with speculative systems or
premature abstractions.

## Artifact Discipline

Significant experiments use `research/experiments/EXP-NNNN/`, based on the template
in `research/experiments/README.md`. Do not create empty evidence files. Every
experiment records the observation, hypothesis, single change, prediction, actual
result, conclusion, and uncertainty.

Save states are checkpoints, not analyzable RAM snapshots. Dump identical Saturn
memory regions from each checkpoint into stable raw files before differential
analysis. Begin with WRAM-L `0x00200000-0x002FFFFF` and WRAM-H
`0x06000000-0x060FFFFF`; expand only if evidence warrants it.

`docs/discoveries.md` contains only durable `CONFIRMED` findings. Put hypotheses and
failures in `research_log.md`; put unresolved questions in
`docs/known_unknowns.md`.

## Session Closeout

Before ending substantial work:

1. Run relevant tests, lint, formatting, and typing checks.
2. Record commands and outcomes in `research_log.md`.
3. Update task status only when acceptance criteria are met.
4. Identify the next unblocked task without beginning a gated milestone.
5. Check that no copyrighted or machine-local artifact is staged for commit.
6. After each successfully completed user-requested task, run the relevant
   verification, inspect the status and diff, stage only intended files, create
   a concise commit, and push it to the configured upstream branch. Never force-
   push or commit prohibited artifacts or secrets; report an unavailable
   upstream or failed push as a blocker.
