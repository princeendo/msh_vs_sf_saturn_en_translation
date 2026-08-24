# Experiment Records

Significant experiments use the next available `EXP-NNNN/` directory. Keep at most
one reverse-engineering experiment `IN_PROGRESS`, and follow task dependencies.

## Required Record

Create a non-empty `README.md` for the experiment using this structure:

```markdown
# EXP-NNNN: Short title

Task: TASK-ID
Status: READY | IN_PROGRESS | DONE | REJECTED
Confidence: UNKNOWN | HYPOTHESIS | SUPPORTED | CONFIRMED | DISPROVEN

## Observation

## Hypothesis

## Controlled Change

## Prediction

## Inputs and Provenance

## Tools and Environment

## Procedure

## Actual Result

## Conclusion

## Uncertainty and Alternatives

## Reproduction
```

Record exact commands, versions, relevant configuration, source and output hashes,
and deterministic checkpoint instructions. Test one hypothesis and change one
variable when practical.

For binary changes, include original bytes, modified bytes, file offset or memory
address, purpose, expected result, and observed result. For visible changes, record
before/after evidence or an equivalent observation. Binary evidence remains ignored;
the experiment record stores its filename, size, SHA-256, description, and local
path convention.

Do not mark an experiment `DONE` until its task acceptance criteria are evidenced.
Record disproven plausible hypotheses in `research_log.md`.
