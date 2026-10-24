# EXP-0040: Disc Source of Ryu's Ending Text

Task: END-004
Status: DONE (2026-10-24)
Confidence: CONFIRMED (the source of the text records). The relocation account of
the non-text differences is SUPPORTED.

## Observation

`EXP-0039` found the ending text as live WRAM-L code records:
- post-boss dialogue: `0x0022AE14`/`0x0022AE60` and `0x0022B9F4`/`0x0022BA40`;
- ending pages: `0x00233664` + `0x4C`·k.

They arrive between run 1 frames 53,481 and 53,651 (the `STAGE-08` transition).
The last state without them is kept as `before_stage08_load.mcs`
(`bed2673fb2e47201…`).

## Hypothesis

A disc read during the `STAGE-08` transition writes these records, and an
offline decode of the identified file reproduces their RAM bytes exactly. No
file name, container, or compression was assumed.

## Controlled Change

None. Read only:
- write breakpoints (log, then halt) replayed from `before_stage08_load.mcs`
  with no input;
- offline extraction and decoding of files from the untouched image.

## Prediction

The writer's context identifies a file. Its decode equals the RAM records byte
for byte.

**Refuted if:** the records are written by a routine with no disc input, or no
decode reproduces them.

## Inputs and Provenance

- **Image:** untouched, track 01 `8274307f9562d2da…`.
- **Emulator:** agent build `fe0edb99f1ffe63a…`.
- **Files** (from the untouched track by LSN, hashes equal to
  `references/mshvsf/saturn_jp/iso9660_files.json`):

  | File | LSN | Size | SHA-256 |
  | --- | --- | --- | --- |
  | `ME.PAC;1` | 3,924 | 60,692 | `77210963cab27db6…` |
  | `MC13.PAC;1` | 11,100 | 31,036 | `05263ab681ac2da2…` |

- **RAM:** `EXP-0039` dumps, plus the halt dumps
  `local/end004/halt/dialogue_workraml.bin` (`11df8d297228bd95…`) and
  `pages_workraml.bin` (`3808c9ffe5fe4830…`).

## Tools and Environment

- `tools/mednafen/replay_state.py --bp` (log mode).
- A one-off agent script for the halts, which:
  1. loads the state;
  2. sets `bpmode halt` and a write breakpoint;
  3. waits for the halt;
  4. saves the registers, WRAM-L, and WRAM-H.
- `tools/disc/pac_lzss.py` (`DISC-001`).
- `tools/text/code_search.py`.

## Procedure

```bash
CUE="local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
  local/end001/checkpoints/before_stage08_load.mcs local/end004/bp_write \
  --steps 12 --step-frames 30 \
  --bp write:0022AE14-0022AE15,2022AE14-2022AE15,00233664-00233665,20233664-20233665
./invenv.sh python -m tools.disc.pac_lzss local/end004/disc/MC*.PAC --out-dir local/end004/decoded
./invenv.sh python -m tools.text.code_search \
  "09AD 0B18 082D 09F4 0B8E 080B 0C3C 084B 081E 080B 08A9" local/end004/disc/ME.PAC
```

- The halts used the same breakpoints in halt mode, one target per load. The
  context blocks were read from the halt dumps of WRAM-H.
- `local/end004/disc/` holds files cut from the untouched track by LSN
  (2,352-byte Mode 1 sectors, user data at `+16`), each checked against the
  listing hash.

## Actual Result

### Writers

| Record | First write (replay frame) | PC | Kind | Context |
| --- | --- | --- | --- | --- |
| Dialogue `0x0022AE14` | 221 | `0603E446` (`mov.b r0,@r9`) | The in-game LZSS decompressor of `DISC-001`/`EXP-0018`, PR `0603E380` | R4 = `0x0603E478`. File header word `0x8000792B`; destination `0x00220000` |
| Page `0x00233664` | 233 | `0603E04E` | A longword copy from WRAM-H `0x0603F000`, PR `0603E324` | R4 = `0x0603E8E8`. File header word `0x0000ED02`; destination `0x00230000` |

- Each context's header word equals word 1 of one file's header:
  - `MC13.PAC` word 1 = `0x8000792B`;
  - `ME.PAC` word 1 = `0x0000ED02`.
- The name field in both contexts reads `me.pac`, so it is not a reliable
  per-load name (it may be stale or belong to the queued file). Bit 31 of word
  1 matches compression: set for the LZSS file, clear for the raw one
  (`SUPPORTED`).

### Dialogue: `MC13.PAC`, LZSS, loaded at `0x00220000`

- `pac_lzss.py` decodes `MC13.PAC` to 61,042 bytes (SHA-256 `9eb9b7c6…be2a`),
  consuming all 31,011 stream bytes.
- **All four Ryu/Gouki dialogue records equal the decode exactly,** at decoded
  offsets `0xAE14`, `0xAE60`, `0xB9F4`, and `0xBA40`.
- Of the whole decode, 60,584 of 61,042 bytes equal WRAM-L from `0x00220000`.
  - The 458 differing bytes lie in 239 longwords where RAM = file + `0x00220040`
    (172 aligned).
  - The rest are the same relocated values split across a 2-byte boundary
    (deltas `0x22` / `0x400000`, 33 each).
  - So the differences are pointer fields relocated at load, not text.
- `MC13` is arcade slot 19, Cyber-Akuma (Mech-Gouki), the final boss (`EXP-0034`,
  `docs/coverage_exceptions.md`). Its "120-record table" with unidentified extra
  content is therefore where the post-boss dialogue lives.
- This also explains why the dialogue loads with `STAGE-08` and regardless of
  the player's partner: it is the boss's file, loaded at the third team slot's
  `0x00220000` base, as win-quote files load per slot (`RE-025`).

### Pages: `ME.PAC`, raw, loaded at `0x00230000`

- `ME.PAC` is not LZSS. At the page-copy halt, file bytes `0x10-0x3673` equal
  WRAM-L `0x00230000-0x00233663` exactly (the bytes copied so far).
- Page 1 line 1 is at file offset `0x367E`, so a file offset is RAM −
  `0x00230000` + `0x10`.
- **The three page records equal the file** at offsets `0x3674`, `0x36C0`, and
  `0x370C`, in all four states checked: select, post-KO, page 1, and page 3.
- Of the whole body (from `0x10`), 59,148 of 60,676 bytes equal WRAM-L from
  `0x00230000`.
  - Most differing longwords are relocated by `0x00230040` (377 aligned, plus
    split forms).
  - 30 longwords with other deltas (`0x5020`, `0x9`) are unexplained (not
    text).
- The records after Ryu's in the file are other characters' ending pages
  (`EXP-0039`).

### Not observed

No other write to the record addresses occurred in the 360 replay frames.

## Conclusion

**CONFIRMED.** Ryu's ending text comes from two disc files, both loaded at the
`STAGE-08` transition:

| Text | File | Format | Loaded at | Ryu's records in the file |
| --- | --- | --- | --- | --- |
| Post-boss dialogue | `MC13.PAC` (the final boss's quote file) | LZSS (`DISC-001` format) | `0x00220000` | Decoded offsets `0xAE14`, `0xAE60`, `0xB9F4`, `0xBA40` |
| Ending pages | `ME.PAC` | Raw from file offset `0x10` | `0x00230000` | File offsets `0x3674`, `0x36C0`, `0x370C` |

For M7, this means:
- Page text can be changed in place in an uncompressed file.
- Dialogue changes need an LZSS re-encode of `MC13`, as the win-quote pipeline
  already does. The `EXP-0036` declared-length rule applies.

This is inferred from the formats, not yet tested by a rebuilt image (that
belongs to `END-010`).

## Uncertainty and Alternatives

- `MC13`'s record layout beyond the four Ryu/Gouki records is not mapped: which
  records belong to which team, how they are indexed, and the "slot-15 record"
  of `EXP-0034`.
- `ME.PAC`'s header beyond word 1, its index, and its 30 non-relocation
  differences are not mapped.
- The relocation rule (file + base + `0x40`) is inferred from deltas, not from
  the loader code.
- Whether an edited file loads and displays (declared lengths, checksums, if
  any) is untested. That is the first `END-010` experiment.

## Reproduction

See Procedure. No gameplay is needed. The states and hashes are in `EXP-0037`
and `EXP-0039`.
