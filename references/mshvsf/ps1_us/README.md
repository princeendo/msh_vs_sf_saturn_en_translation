# MSHvSF PlayStation US

Permitted provenance and task-oriented notes for the secondary English reference
belong here. Treat implementation details as unrelated unless tested.

Candidate release identity: US PlayStation `SLUS-00793`, Fighters Edge, English,
NTSC-U. Redump disc 12632 records one 552,894,048-byte Data/Mode 2 track with SHA-1
`6e50ac0d4dfc5eaf2ddd0da3cabde19e0ec3721a`; full CRC-32 and MD5 provenance is in
`docs/references.md`.

Use only a legal, fully hash-matched copy for direct quote capture. Record wording and
formatting as evidence for this port only; do not infer arcade wording, Saturn storage,
or Japanese-English correspondence from a PS1 match.

## Local Image (`REF-011`, 2026-10-24)

The user supplied `Marvel Super Heroes vs. Street Fighter (USA).7z`
(272,946,485 bytes, SHA-256
`ab593ab36859d0bb24443bd011e7ad048706b67d8fdfc7be884d2f0231d50ff1`). It was
extracted unchanged into the ignored `local/disc_images/mshvsf_ps1_us/`.

| File | Size | SHA-256 | Match |
| --- | ---: | --- | --- |
| `Marvel Super Heroes vs. Street Fighter (USA).bin` | 552894048 | `a0e20ce8739e66a2192d132bae5e47d2ccfdc9eacc754bd1cb5d93db7d9ee0f3` | Redump 12632 and MAME `psx.xml` `mshvsf`: CRC `94eb061c`, MD5 `a182cf46…f5246b`, SHA-1 `6e50ac0d…3ec3721a` |
| `Marvel Super Heroes vs. Street Fighter (USA).cue` | 110 | `3e0acc0f129d376a6ecdceaac5467eeef16c740a99c78233a329c6cc9e4f2f1f` | — |

Identity is **CONFIRMED**: size, CRC-32, MD5, and SHA-1 all match the recorded
fingerprint. `REF-005` can use it.

## Win-Quote Text (`EXP-0032`)

- `DAT/SELECT.BIN` holds the arcade's 26 English win-quote slot blocks
  byte-identical, in little-endian code order.
- The per-slot offsets and hashes are in
  [`arcade_en_comparison.json`](arcade_en_comparison.json) (no text).
- For Ryu, the PS1 English equals the arcade English.
