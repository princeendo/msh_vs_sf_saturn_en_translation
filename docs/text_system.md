# Text System

## Status

The MSHvSF Saturn text system is **UNKNOWN**. No encoding, storage structure, pointer
scheme, compression method, buffer lifecycle, font mapping, or renderer path is
confirmed.

`SUPPORTED` (not confirmed) candidates for post-fight win quotes are recorded in
`research/experiments/EXP-0012` and `EXP-0013`:

- VDP1 sprite glyph cells;
- 16-bit glyph-code records in a WRAM-L table;
- a per-screen WRAM-H buffer.

They move here only after a controlled mutation confirms them (`RE-012`).

## Questions to Resolve

- Where and when does the first Ryu post-fight caption enter memory?
- What bytes represent it, and how are boundaries determined?
- Is the displayed content stored directly, transformed, or assembled?
- Which code or data path selects and renders it?
- What size or layout constraints govern a safe replacement?

Resolve one question at a time with controlled experiments. Record hypotheses and
failures in `research_log.md`; add only reproducible confirmed behavior here.

## Future Finding Format

For each confirmed component, record its role, scope, source-image hash, experiment,
addresses or offsets, original bytes, interpretation, reproduction steps, and known
limitations. Never import assumptions from another game, release, or platform.
