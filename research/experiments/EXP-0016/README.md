# EXP-0016: Inspect the Source Disc Data Track and ISO 9660 Directory

Task: `DISC-010` (prerequisite for `DISC-001` file mapping)
Date: 2026-10-17
Status: READY
Confidence: HYPOTHESIS

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

## Actual Result

Pending.
