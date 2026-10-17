# EXP-0017: Search the Disc for the Verbatim Ryu Quote Table

Task: `DISC-001`
Date: 2026-10-17
Status: DONE
Confidence: DISPROVEN

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

Inputs:

- The 1,216-byte table `0x002091AC-0x0020966B` from state A's validated WRAM-L
  extraction (`research/memory_dumps/ab60af86089a9575/wram_l.bin`).
- The `EXP-0016` user-data stream, 393,924,608 bytes, SHA-256 `dea7bd65…fd0adef`.

Searched with Python `bytes.find`, mapping offsets to files via
`references/mshvsf/saturn_jp/iso9660_files.json`:

1. the full table;
2. each of the 16 records (76 bytes);
3. each record's longest run without `0x0020`/`0x0000` (up to 18 codes);
4. all of the above with 16-bit byte order swapped.

**Hits: 0 of 66 patterns.** Because no file is interleaved (`EXP-0016`), every file's
bytes are contiguous in the stream, so this also covers the contents of each file.

A follow-on check (separate hypothesis: the disc stores plain text that is
converted at load) searched 12 short fragments from the agent's unreviewed
readings in Shift-JIS, EUC-JP, and UTF-16BE. The fragments included `まだまだお前達は`,
`技を極めろ`, `会いに来た`, `だった`, and `ケン`. **Hits: 0.**

Observation for the next experiment: state A's WRAM-H holds exactly one big-endian
pointer to the table start, `002091AC` at **`0x06094FD8`**.

- The neighbouring 4-byte entries are either placeholders of the form
  `99 00 NN 99` (`NN` increasing) or WRAM-L addresses: `00229FF0` at `0x06094FCC`,
  `0021A59C` at `0x06094FDC`, and `00239BDC` at `0x06094FEC`.
- At the `EXP-0007` title state the entry is `00000000`.
- In both `EXP-0009` fights it is `002091AC`, while some neighbouring entries
  differ between fights.

The interpretation as a loaded-resource slot table is a `HYPOTHESIS`.

## Conclusion

`DISPROVEN`: the quote table is not stored verbatim on disc. Neither its records,
its long code runs, nor a byte-swapped form occur in the track 01 user data. Plain
Shift-JIS, EUC-JP, or UTF-16BE storage of the tested fragments is also not
supported.

The table is therefore produced at load time from a transformed source, for example
compressed data or a different encoding. That is the subject of the dynamic trace
in `EXP-0018`.

## Uncertainty and Alternatives

- **Transcription.** The fragments are unreviewed readings; misreadings would cause
  false negatives in the encoding check only.
- **Not searched.** CD-DA tracks and the region of the volume beyond track 01
  (volume space size 216,839) were not searched.
- **Untested sources.** The table could also be generated from smaller pieces, such
  as per-line strings in another layout. Only the tested layouts are excluded.
