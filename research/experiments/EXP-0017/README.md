# EXP-0017: Search the Disc for the Verbatim Ryu Quote Table

Task: `DISC-001`
Date: 2026-10-17
Status: BLOCKED (requires `EXP-0016` / `DISC-010`)
Confidence: HYPOTHESIS

## Observation

- `EXP-0015` confirmed that the WRAM-L table at `0x002091AC-0x0020966B` (16 records ×
  76 bytes = 1,216 bytes) drives the displayed win quote.
- The table is absent at the title screen (`EXP-0006` and `EXP-0007` states).
  It is byte-identical at the same address in both `EXP-0009` fights (vs Vega, vs
  Sakura) and in all `EXP-0010` states. So it is loaded between the title and the
  first fight and persists across fights.
- No copy of a record exists in WRAM-H or in cart RAM (unvalidated extraction) at
  the title screen or during fight 1.
- The record format (38 × 16-bit big-endian codes, `0x0020` blanks, a `0000` name
  placeholder) has low entropy, unlike the high-entropy WRAM-H block from
  `EXP-0011`.

## Hypothesis

The table is stored verbatim (uncompressed, same byte order and record layout) in
the track 01 user data.

## Controlled Change

None. This is a read-only search of the `EXP-0016` user-data stream and of each
extracted file. Searches:

1. the full 1,216-byte table;
2. each 76-byte record individually;
3. the longest blank-free code run per record (for example Q11 line 2, 18 codes),
   to catch storage without fixed padding;
4. the same patterns with 16-bit byte order swapped.

## Prediction

If the hypothesis holds:

- the full table occurs exactly once, inside one ISO 9660 file extent;
- every record also matches, at offsets 76 bytes apart;
- the result maps to a file path and byte offset.

If only searches (3) or (4) match, the storage layout or byte order differs, and
that is recorded as a refinement. If nothing matches, the table is transformed on
disc (for example compressed, encoded, or generated), and the hypothesis is
`DISPROVEN`. The next step is then the dynamic trace below.

## Planned Follow-On (`EXP-0018`, only if needed)

Run a dynamic trace with a write breakpoint on `0x002091AC-0x0020966B`. Start from a
new checkpoint taken before the table exists (character select with Ryu/Ken), then
start a match. The breaking PC and source registers identify the copy or
decompression routine and its input buffer. Repeated breakpoints on that buffer
lead back to the CD read and its sector/file.

This needs the user at the keyboard and the `EXP-0014` runbook.

## Actual Result

Pending.
