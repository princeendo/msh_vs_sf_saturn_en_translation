# EXP-0016: Inspect the Source Disc Data Track and ISO 9660 Directory

Task: `DISC-010` (prerequisite for `DISC-001` file mapping)
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

## Observation

The CUE descriptor (`references/mshvsf/saturn_jp/README.md` identity) declares:

- `TRACK 01 MODE1/2352`, `INDEX 01 00:00:00`;
- tracks 02-12 as `AUDIO`.

Track 01 is 452,397,792 bytes, which is 192,346 raw sectors of 2,352 bytes. No
sector, IP, or filesystem property of this image has been measured yet
(`docs/disc_layout.md`). Platform expectations (Mode 1 user data of 2,048 bytes,
system area at LSN 0-15, ISO 9660 descriptors from LSN 16) come from
`docs/references.md` and are not observations of this image.

## Hypothesis

Track 01 consists entirely of valid Mode 1 raw sectors. Its first sector is LSN 0,
and its 2,048-byte user data holds an ISO 9660 primary volume descriptor at LSN 16
whose directory tree enumerates the game's files with extent LSNs and byte
lengths.

## Controlled Change

None. This is a read-only inspection of the immutable source; source hashes are
verified before and after.

## Prediction

1. Every sector has the 12-byte sync pattern and mode byte `0x01`. Header
   minute/second/frame values decode to FAD = sector index + 150 (LSN = index).
2. User data at LSN 16 begins with type `0x01` and `CD001`. The logical block size
   is 2,048, and the root directory parses without error.
3. Every file extent lies within track 01, and extents do not overlap.

## Tooling (to build)

`tools/disc/iso9660.py`, read-only, with synthetic tests:

- read a Mode 1/2352 BIN by LSN and validate sync, mode, and header address;
- concatenate 2,048-byte user data;
- parse the PVD and walk the directories;
- emit JSON listing each file's path, extent LSN, byte length, flags, and
  SHA-256 of its extracted bytes.

Extracted file contents go only to ignored `research/extracted_files/`. Only factual
metadata (names, LSNs, sizes, hashes) is tracked.

## Command

```bash
./invenv.sh python -m tools.disc.iso9660 \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
  --check --extract research/extracted_files/mshvsf_saturn_jp \
  --user-stream research/extracted_files/mshvsf_saturn_jp_track01_user.bin \
  > research/extracted_files/exp0016_report.json
```

Python 3.12.13 via `./invenv.sh`. Source identity (13 components) matched the
manifest before and after the run.

## Actual Result

Sector check:

- 452,397,792 bytes = 192,346 sectors.
- `bad_sync` 0, `non_mode1` 0, `address_mismatch` 0.
- Header FAD runs from 150 to 192,495, so LSN = sector index = FAD − 150.

Primary volume descriptor at LSN 16:

| Field | Value |
| --- | --- |
| System ID | `SEGA SEGASATURN` |
| Volume ID | `MSH_VS_STREET_FIGHTER` |
| Logical block size | 2,048 |
| Root directory | LSN 20, 20,480 bytes |
| Volume space size | 216,839 blocks |

The volume space size exceeds track 01's 192,346 sectors. That is recorded as an
observation, not interpreted.

Directory:

- 414 entries, all files, with no subdirectories.
- The first extent is `MVS_CPY.TXT;1` at LSN 30, and the last is `MVDEMOFF.ST2;1` at
  LSN 191,957.
- Every extent lies within track 01. Extents do not overlap, and no file uses
  interleave (file unit size and gap are 0).
- By extension: 235 `ST2`, 79 `PAC`, 71 `ADP`, 14 `BIN`, 3 `I16`, 3 `TXT`, 2 `DAT`,
  and one each of `CPK`, `MAP`, `TSK`, `PRS`, and `SHX`.

Outputs:

- Tracked metadata: `references/mshvsf/saturn_jp/iso9660_files.json`, with each
  file's path, LSN, size, flags, and SHA-256 (no contents).
- Ignored:
  - the extracted files (376 MB);
  - the user-data stream (393,924,608 bytes, SHA-256 `dea7bd65f668…fd0adef`);
  - the full report (SHA-256 `f58e0553944c…c817550a`).

## Conclusion

`CONFIRMED`. Track 01 is a clean Mode 1/2352 track, LSN = index, with a flat ISO 9660
filesystem of 414 non-interleaved files. Any user-data offset can be mapped to a
file and file offset as `(offset // 2048 − extent LSN) × 2048 + offset % 2048`.

## Uncertainty and Alternatives

- EDC/ECC bytes were not verified.
- The system area (LSN 0-15) and IP fields were not parsed.
- The volume-space-size discrepancy is unexplained.
