# Repository Architecture

This repository separates reproducible tooling and factual metadata from local,
copyrighted, or machine-specific evidence.

## Tracked Areas

- `docs/`: scope, protocols, confirmed discoveries, and unresolved questions.
- `tools/`: reusable Python 3.12+ extraction and analysis tools.
- `tests/`: tests using only synthetic or freely distributable fixtures.
- `research/experiments/EXP-NNNN/`: records for significant controlled experiments.
- `data/translations/`: reviewed, evidence-backed text correspondences.
- `references/`: provenance records and guidance, not copyrighted source material.
- `vendor/mednafen/`: Mednafen provenance, patches, and build instructions if authorized.

## Local Or Generated Areas

- Original disc images and BIOS files remain outside the repository or in an ignored
  local path and are immutable.
- Derived disc builds belong under ignored `build/` paths and must never overwrite a
  source image.
- Screenshots, save states, memory dumps, traces, extracted game contents, and
  emulator binaries are local binary evidence and must be ignored.
- Track hashes, addresses, schemas, commands, tool versions, and derived factual
  metadata needed to reproduce analysis.

## Workflow Boundaries

Run Python through `./invenv.sh`. Follow task dependencies and milestone gates before
starting research. At most one reverse-engineering experiment may be `IN_PROGRESS`.
`docs/discoveries.md` is reserved for reproducible `CONFIRMED` findings.
