# EXP-0011: First WRAM Comparison of Win-Quote Checkpoints

Task: `DBG-007`, `DBG-008`, `DBG-009`, `DBG-010`, `DBG-011`
Date: 2026-10-15
Status: DONE
Confidence: DISPROVEN

## Observation

`EXP-0010` produced quote-screen states from one pre-KO checkpoint:

| Role | Slot | Quote |
| --- | ---: | --- |
| C1 | 7 | Q10 |
| C1′ | 0 | Q10, a few frames later |
| C2 | 6 | Q8 |
| C2b | 8 | Q11 |

`EXP-0008` validated save-state extraction of WRAM-L and WRAM-H. The thumbnails show
the same portrait and layout in every C state, so the visible difference is the
quote text. WRAM is analyzed first, as `AGENTS.md` requires. VDP VRAM and cart RAM
are out of scope unless WRAM yields no candidate.

## Hypothesis

During the quote screen, the visible quote is present in WRAM-L or WRAM-H as
Shift-JIS bytes.

## Controlled Change

The variable is the displayed quote (C1 vs C2 vs C2b). C1 vs C1′ is the control for
time-only change; offsets that differ there are excluded from the candidate set.

## Prediction

1. Diff: after excluding C1/C1′ changes, C1 vs C2 and C1 vs C2b each leave
   changed ranges, and some ranges are common to both comparisons.
2. Search: Shift-JIS encodings of short Q10 fragments occur in C1 and C1′ but not
   in C2 or C2b. Q8 fragments occur only in C2, and Q11 fragments only in C2b. The
   matches fall inside or next to a common diff range.

The fragments are the agent's unreviewed reading of the thumbnails, with several
per quote to reduce the effect of misreading. A misreading would cause a false
negative, not a false positive.

## Inputs and Provenance

The `EXP-0010` states were extracted with `tools.memory.mcs_extract` (validated
regions only) to ignored `research/memory_dumps/<state sha256[:16]>/`.

### DBG-007 / DBG-008 Acquisition

Command per state:
`./invenv.sh python -m tools.memory.mcs_extract <state>`. A repeat run used
`--out-dir <scratch> --region wram_l --region wram_h`. Every file is 1,048,576
bytes, as expected, and every repeat was byte-identical (`cmp`). WRAM-L is at base
`0x00200000` and WRAM-H at `0x06000000`, per `docs/saturn_memory_map.md`.

| Role | State SHA-256 | WRAM-L SHA-256 | WRAM-H SHA-256 |
| --- | --- | --- | --- |
| A | `ab60af86…dce6` | `8feacb429d33938560241d1694e4f0068545a1e46c3a7d9304a33a68646bd84c` | `df29e13f5c2194a8729964c9421f3129c9de5da9720ea4cdd96728bb8e0a79f2` |
| C1 | `9482880a…47ce` | `338065f74151a5ce93ba17884278b7acdeea7437a2a2a6ddfda1ab47e2f5ed85` | `88fa9343a627228c83b2cf1816ef5ce64b3501e5a96300af7aea0f80ef6a2acd` |
| C1′ | `f02c7177…f93c` | `338065f74151a5ce93ba17884278b7acdeea7437a2a2a6ddfda1ab47e2f5ed85` | `66068efc348e5cc7f6a666024280243875eb8d4f5703e7d333f444d1ff8f43ff` |
| C2 | `5534ad9e…3878` | `cd8c321495cbdc29be2c7bd4029641cef96caccf50987924ca45920c327776c6` | `b4e59f64e8cce4cdb0a3977a45caafd0255ac86737bb6c79ad524371b93d1301` |
| C2b | `072497f2…10bf` | `79a7a2ad0e2cbedbc8a3a305b1533c606c3da1aea447c8dcff74996f963f3205` | `517eac08a6098adb72735b67986e6e0d7ec9b052caa9142d9a6c21626a7ba6e4` |

## Tools

- `tools/memory/diff.py` (`DBG-009`): contiguous changed ranges with optional
  control-pair exclusion. JSON output follows
  `tools/memory/diff_result.schema.json`.
- `tools/text/search.py` (`DBG-010`): exact hex and explicitly encoded text
  patterns, with addresses, context, and input hashes.

## Actual Result

### Diffs

Control C1 vs C1′:

- WRAM-L: 0 changed bytes.
- WRAM-H: 6,263 changed bytes in 2,378 ranges.

Comparisons with the C1/C1′ control excluded:

| Region | Pair | Raw changed | Excluded | Changed | Ranges |
| --- | --- | ---: | ---: | ---: | ---: |
| WRAM-L | C1 vs C2 | 1,192 | 0 | 1,192 | 357 |
| WRAM-L | C1 vs C2b | 1,332 | 0 | 1,332 | 330 |
| WRAM-H | C1 vs C2 | 20,203 | 6,263 | 14,932 | 5,208 |
| WRAM-H | C1 vs C2b | 19,750 | 6,263 | 14,482 | 4,946 |

The JSON outputs are in ignored `research/memory_dumps/exp0011/`:

| File | SHA-256 |
| --- | --- |
| `wram_l_c1_vs_C2.json` | `9e9070c7…8685` |
| `wram_l_c1_vs_C2b.json` | `9b390d2a…6279` |
| `wram_h_c1_vs_C2.json` | `b68f8d26…4f81` |
| `wram_h_c1_vs_C2b.json` | `45c241f1…4198` |

Offsets distinct across all three quotes and stable between C1 and C1′:

- WRAM-L: 405 bytes, forming 35 ranges when merged with gaps up to 8.
- WRAM-H: 10,118 bytes, forming 977 merged ranges.

### Shift-JIS search

Fragments searched, from the agent's unreviewed reading:

- Q10: `一瞬の迷い`, `自分を信じろ`, `拳を鈍らせる`
- Q8: `お前達は強く`, `拳を交えたい`
- Q11: `おれより強い`, `会いに来た`
- Shared word: `強い`

Every fragment had **0 matches** in WRAM-L and WRAM-H of A, C1, C1′, C2, and C2b.
The single kanji `拳` (2 bytes) matched exactly 3 times in every dump, including A.
That is coincidental and not quote-dependent.

### Observations (facts; interpretations are `HYPOTHESIS`)

- **WRAM-L tile-map-like entries.** Several quote-dependent WRAM-L ranges hold
  big-endian 16-bit values with a constant high byte and sequential low bytes,
  separated by `FFFF`, for example:
  - `0x00256CD0` holds `0C F5 0C 28 …` in C1 and `0C 99 0C 28 …` in C2;
  - `0x00257862` holds `0D 6C 0D 6D …`;
  - `0x0025F0BA` holds `0C 5E 0C 5F …` in C1, `0C F3 …` in C2, and `FFFF` in C2b.

  In A these ranges are mostly `FFFF`. The pattern is consistent with a cell or
  tile map whose tiles are allocated sequentially, which would fit text rendered
  as graphics.
- **WRAM-H record chain.** From `0x06014798`, WRAM-H holds a chain of 28-byte
  records. Each has a next pointer, a field that steps through VDP2 VRAM addresses
  from `0x05E01800` by `0x800`, and a `0x800` length. The other record bytes differ
  between quotes without visible structure.
- **WRAM-H quote-dependent block.** `0x06014CB5-0x0601677B` (6,855 bytes) differs
  for every quote, is stable between C1 and C1′, and has 7.15-7.16 bits/byte of
  entropy. That is consistent with compressed data, but not shown to be.

## Conclusion

The hypothesis is `DISPROVEN` for the tested fragments: the visible quotes are not
present as Shift-JIS bytes in WRAM-L or WRAM-H on the quote screen.

`SUPPORTED`: quote-dependent and time-stable WRAM ranges exist. The strongest
structured candidates are the WRAM-L 16-bit sequential entries and the
high-entropy WRAM-H block. Their meaning is not established.

## Uncertainty and Alternatives

- The fragments are unreviewed agent readings. All eight failing together makes a
  pure misreading unlikely, but `REF-003` review is still required.
- Untested alternatives:
  - other character encodings (EUC-JP, UTF-16, or a custom code table);
  - text decoded to glyphs earlier and discarded before the saved instant (state B
    was deferred);
  - text held only in VDP VRAM, cart RAM, or the CD buffer;
  - pre-rendered text graphics stored compressed on disc.
- Different replay histories are confounded with different quotes in C1 vs C2.
  The C1/C1′ control covers only time-based change.

## Next Discriminating Experiments

1. Compare VDP2 and VDP1 VRAM across C1, C1′, C2, and C2b to locate the text
   pixels, and test whether the WRAM-L entries index those tiles. VRAM extraction
   is validated (`EXP-0008`).
2. Use a stock debugger write breakpoint on the WRAM-H block or the WRAM-L entries
   (`EMU-011`) to identify the writing code and its source buffer.
3. Tracing the WRAM-H block to a disc file is `DISC-001` (M2) work and stays gated
   behind M1.

## Reproduction

```bash
D=research/memory_dumps
./invenv.sh python -m tools.memory.diff $D/9482880a11269e5c/wram_l.bin \
  $D/5534ad9e464630d0/wram_l.bin --base 0x00200000 \
  --control $D/9482880a11269e5c/wram_l.bin $D/f02c7177dadcaa43/wram_l.bin --json
./invenv.sh python -m tools.text.search $D/9482880a11269e5c/wram_h.bin \
  --base 0x06000000 --text 一瞬の迷い --encoding shift_jis
```
