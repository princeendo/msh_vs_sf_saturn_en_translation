# Research Protocol

## Required Cycle

```text
OBSERVE -> FORM ONE HYPOTHESIS -> DESIGN A DISCRIMINATING EXPERIMENT
        -> RUN IT -> RECORD RESULT -> ACCEPT / REJECT / REFINE
        -> UPDATE DOCUMENTATION
```

Prefer one changed variable per experiment. A visual resemblance, matching byte
sequence, or analogy to another release is not confirmation.

## Confidence Labels

- **UNKNOWN**: no meaningful conclusion yet.
- **HYPOTHESIS**: plausible but insufficiently tested.
- **SUPPORTED**: consistent evidence remains compatible with alternatives.
- **CONFIRMED**: a controlled, reproducible experiment produced the prediction.
- **DISPROVEN**: evidence contradicts the hypothesis.

## Before Research

Record each source-image component's filename, byte size, SHA-256, and release
description. Preserve originals unchanged. Record exact tool versions, commands,
inputs, and relevant configuration.

## Experiment Record

Significant experiments use `research/experiments/EXP-NNNN/` and record the task,
observation, one hypothesis, controlled change, prediction, procedure, actual result,
conclusion, uncertainty, and reproducibility details. Do not create empty evidence
placeholders.

For a binary modification, also record original bytes, modified bytes, file offset or
memory address, purpose, expected result, and observed result. Visible modifications
require before/after screenshots or equivalent evidence and a deterministic
checkpoint.

## Results

- Put reproducible `CONFIRMED` findings in `docs/discoveries.md`.
- Put hypotheses, failures, and disproven ideas in `research_log.md`.
- Put unresolved questions in `docs/known_unknowns.md`.
- Update task status only after all acceptance criteria have evidence.

Keep copyrighted and machine-local binary evidence ignored. Commit only permitted
metadata, scripts, schemas, and small synthetic fixtures.
