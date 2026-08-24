# Research Directory

This directory organizes controlled reverse-engineering work.

## Structure

- `experiments/EXP-NNNN/`: tracked records for significant experiments.
- Local screenshots, save states, memory dumps, and traces: ignored binary evidence.

Do not create empty evidence placeholders. Create an experiment directory when an
experiment is ready to record, and include only files containing actual observations,
procedures, results, or permitted metadata.

Keep source images, BIOS files, extracted game contents, binary patches containing
copyrighted data, screenshots, save states, dumps, traces, and emulator binaries out
of version control. Track hashes, sizes, commands, tool versions, checkpoint
instructions, addresses, offsets, and derived factual metadata needed to reproduce
the work.

Use `research_log.md` for chronological outcomes, including failures. Put only
reproducible confirmed findings in `docs/discoveries.md`.
