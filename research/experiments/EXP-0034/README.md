# EXP-0034: Saturn Quote Files Map One-to-One onto Arcade Character Slots

Task: RE-041
Status: DONE
Confidence: CONFIRMED (byte identity, all three arcade sets; name-table order)

## Observation

- The `EXP-0023` census found 23 Saturn quote files (`MC00`-`MC16`): 17 with one
  16-record table and 6 irregular.
- Only `MC09` = Ryu (slot 9) and `MC0A` = Ken (slot 10) were mapped (`EXP-0031`,
  `RE-030`).
- The arcade Japanese pointer table (`0x20BFAC`) has 26 slots of 16 × 76-byte
  blocks; slots 7 and 25 share one block.

## Hypothesis

Each Saturn file carries the arcade Japanese block of one slot, byte-identical.
The file index equals the arcade slot.

## Controlled Change

None. Read-only comparison of decoded Saturn files with arcade program data.

## Prediction

`MCnn` contains slot `nn`'s whole block. Irregular files carry additional blocks
or tables.

## Inputs and Provenance

- `MC00.PAC`-`MC16.PAC` and `MEMFIX.PAC`, extracted from the recorded Saturn
  source. File SHA-256 values are in `data/text/coverage_manifest.json`.
- Arcade `mshvsf`, `mshvsfu`, `mshvsfj` (`references/mshvsf/arcade/README.md`) and
  the pinned MAME 0.289 `cps2.cpp`.

## Tools

`tools/reference/slot_census.py` (new; tests in `tests/unit/test_slot_census.py`)
and `quote_census.find_tables`, run with Python 3.12.13.

## Actual Result

Every one of the 23 files contains the whole block of the arcade slot with the
same number, at the offsets in `data/text/coverage_manifest.json`. The result is
identical for all three arcade sets.

- **Ordinary (18 files):** exactly one whole block, with every Saturn table
  inside it.
  - `MC01`, `MC03`-`MC06`, `MC09`-`MC0B`, `MC0D`-`MC12`, `MC14`-`MC16`.
  - `MC07`'s block is shared by arcade slots 7 and 25.
- **Irregular (5 files):**

  | File | Content |
  | --- | --- |
  | `MC00` | slot 0 inside a 26-record table, plus 14-, 9- and 43-record tables |
  | `MC02` | slots 2 and 23 |
  | `MC08` | slots 8 and 24 |
  | `MC0C` | slot 12, plus an unmatched 4-record table at `0x3B88` |
  | `MC13` | slot 19 inside a 120-record table that also contains one slot-15 record |

- **Name table.** The Saturn name table (WRAM-H `0x06095EC4`, 26 entries, read
  from the `EXP-0028` Ken state and rendered offline) lists the arcade name list's
  characters in the same order. Entry `n` = slot `n`; for example 14 = ベガ
  (Bison), 17 = ノリマロ, 25 = スパイダーマン.
- **Census misalignment.** `find_tables` sometimes starts a table one word early
  (`MC0A`, `MC0D`, `MC10`, `MC11`, `MC14`, `MC15`). It also split `MC0C`'s and
  `MC07`'s blocks (`EXP-0023` listed `MC07` as 15 records). The whole-block search
  is authoritative.

## Conclusion

**CONFIRMED:** the Saturn quote file index equals the arcade character slot and the
Saturn name-table index. Each file's Japanese win quotes are the arcade's,
byte-identical. Structural classes are recorded; character roles (boss, secret,
special) are left to `RE-043`.

## Uncertainty and Alternatives

- Byte identity of the Japanese tables shows the content source. Each Saturn
  file's runtime use is only confirmed for `MC09` and `MC0A`.
- The extra tables in irregular files (`MC00`, `MC0C`, `MC13`) are unidentified.
  They may be boss dialogue or other text.
- The name table was read from a derived image's state. Those builds change only
  `MC09`, `MC0A`, and `MEMFIX` entry 4, not the name table's source.

## Reproduction

```bash
./invenv.sh python -m tools.reference.slot_census research/extracted_files/mshvsf_saturn_jp/MC*.PAC --memfix research/extracted_files/mshvsf_saturn_jp/MEMFIX.PAC --driver /tmp/cps2.cpp --archive local/arcade_roms/mshvsf/mshvsfj.zip
```
