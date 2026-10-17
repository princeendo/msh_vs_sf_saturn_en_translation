# EXP-0021: Live Display of Full-Width Latin Codes in a Win Quote

Task: `FONT-002`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0020` decoded the quote font (`tools/text/font.py`, 79/79 known glyphs exact).
The atlas shows full-width Latin glyphs in the quote style (body `1` plus shadow `F`):

| Characters | Codes |
| --- | --- |
| A-Z | `0x08E8-0x0901` |
| a-z | `0x0902-0x091B` |
| 0-9 | `0x091C-0x0925` |

None of these codes has been displayed in a quote yet. The ASCII codes displayed
but were faint.

## Hypothesis

Codes `08F9 0900 08FC 0902 091D` display as full-width, solid `R Y U a 1` (one per
cell), with the same weight and shadow as the Japanese quote text.

## Controlled Change

The variable is line-1 cells 0-4 of all 16 Ryu quote records (80 writes), loaded
at state A into workraml `000091AC-0000966B`.

- Patch `ryu.bin` = `fw-ryu-patched.bin`, SHA-256 prefix `dcd1d3b1ce488d95`.
- Manifest `fw-ryu-manifest.json`, prefix `ad23b71c5991fb3c`.
- Control `org.bin`, prefix `6aaf1f8883642a17`, identical to `fw-ryu-original.bin`.

## Prediction

- **Patched runs:** cells 0-4 of line 1 show `R Y U a 1`, matching the
  decoder-rendered prediction (ignored
  `research/memory_dumps/exp0020/atlas/predicted_RYUa1.png`), solid and shadowed.
  The rest of the quote is unchanged.
- **Control:** the quote is unmodified.

## Procedure

As in `EXP-0020` Phase 2, with load file `ryu.bin`/`org.bin` and verification dumps
`f1.bin`/`f2.bin` (patched) and `c1.bin` (control).

| Run | Slot |
| --- | ---: |
| Patched 1 | 1 |
| Patched 2 | 2 |
| Control | 3 |

The previous contents of slots 1-3 are archived.

## Actual Result (2026-10-17)

| Run | Verification dump | Slot / state SHA-256 | Screenshot | Shown |
| --- | --- | --- | --- | --- |
| Patched 1 | `f1.bin` = `ryu.bin` (`dcd1d3b1…`) | 1 / `793c728a12c16c87…3382` | `-0051.png` `0f1f9eae…5449` | `RYUa1くれ、ケン…` (record 0) |
| Patched 2 | `f2.bin`: first 1,216 bytes = `ryu.bin` (see note) | 2 / `1001da4f20bd8faa…d21f` | `-0052.png` `904d3543…3d1b` | `RYUa1前達と闘えてよかった…` (record 15, Q9) |
| Control | `c1.bin` = `org.bin` (`6aaf1f88…`) | 3 / `8caa228f0a495141…43d0` | `-0053.png` `432ef9d7…966a` | `もっと闘え！…` (Q5), unchanged |

- **Dump typo.** `f2.bin` is 1,296 bytes, because the dump end address was mistyped
  (80 bytes too long). Its first 1,216 bytes equal `ryu.bin`.
- **Saved states.** Extracted WRAM-L of slots 1 and 2 equals `ryu.bin` over the
  table range. Slot 3 equals `org.bin`.
- **Archive.** States are archived as `exp0021-slot{1,2,3}`.
- **Appearance.** The five cells show full-width, solid, shadowed `R Y U a 1`,
  matching the decoder-rendered prediction and the Japanese text's style. The rest
  of each quote is unchanged.

## Conclusion

`CONFIRMED`: codes `08F9` (R), `0900` (Y), `08FC` (U), `0902` (a), and `091D` (1)
display as full-width quote-style Latin glyphs. Two patched runs on two different
records match the prediction, and the control is unchanged. This supports the
range rules A-Z `0x08E8-0x0901`, a-z `0x0902-0x091B`, and 0-9 `0x091C-0x0925`.

## Uncertainty and Alternatives

- Only 5 of the 62 full-width codes were displayed. The others rest on the atlas.
- English capacity is at most 2 × 19 full-width characters per quote. Whether
  longer text or packing two letters per cell is possible is untested.
