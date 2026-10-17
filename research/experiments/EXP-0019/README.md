# EXP-0019: Reproduce the あいう Marker from a Rebuilt Disc Image

Task: `DISC-002` (M2)
Date: 2026-10-17
Status: READY
Confidence: HYPOTHESIS

## Observation

- **Live RAM.** `EXP-0015` confirmed that writing `0801 0803 0805` into line-1 cells
  0-2 of the WRAM-L quote records shows `あいう` on Ryu's win screen.
- **Disc source.** `EXP-0018` confirmed that this table is decoded offset
  `0x91AC-0x966B` of `MC09.PAC;1`:
  - LSN 8,246; 25,128 bytes; 13 sectors;
  - a 0x18-byte header, then LZSS: flags MSB-first, 0 = literal, 1 = two-byte match
    with length `(v & 0xF) + 3` and source `pos − 0x1000 + ((v >> 4) & 0xFFF)`;
  - decompressed when Ryu is picked.
- **PAC header pattern.** Across all 23 `MC*.PAC` files:
  - word 1 = `0x80000000 | (compressed length + 8)`;
  - words 0, 2, 3 = 0;
  - word 4 = compressed length, word 5 = decompressed length;
  - the file is padded with 0-3 bytes to a 4-byte multiple.
- **Disc placement.** `MC09.PAC` occupies LSN 8,246-8,258. `PL0A.PAC` starts at LSN
  8,259, with no free sectors between. The last MC09 sector has 1,496 unused bytes.
- **Sector EDC/ECC.** Sectors carry real EDC/ECC bytes (for example LSN 8,246 EDC
  `2de4b11d`).

## Hypothesis

A derived image that differs from the source **only** in `MC09.PAC` boots normally
and shows `あいう` in line-1 cells 0-2 of Ryu's win quotes. The new `MC09.PAC`
contains the original decoded payload with the marker codes written into all 16
quote records, re-encoded in the game's LZSS format, with a recomputed header, in
the same sectors with regenerated EDC/ECC.

## Controlled Change

The variable is the content of `MC09.PAC`. Exactly 48 decoded 16-bit codes change
(16 records × 3 cells), at decoded offset `0x91AC + 76·r + {0, 2, 4}`, to `0801`,
`0803`, and `0805`. Unlike `EXP-0015`, record 0 (`0x91AC`, the partner-name
template) is included, so every observed quote carries the marker.

Fixed:

- every other file and sector;
- the ISO 9660 directory (file size kept at 25,128 bytes; see Encoding);
- tracks 02-12 (copied byte for byte);
- the CUE text.

## Encoding Plan

1. **Splice.** Keep the original compressed stream unchanged up to the last
   flag-group boundary whose decoded output ends at or before `0x91AC`. Re-encode
   the remainder from that output position with a greedy/lazy LZSS encoder:
   window 4,096, lengths 3-18, no match reaching before output position 0.
2. **Header.** Recompute word 4 (new compressed length) and word 1
   (`0x80000000 | (word 4 + 8)`). Keep word 5 = `0xB548`.
3. **Size policy (A).** If header + stream ≤ 25,128 bytes, pad with zero bytes to
   exactly 25,128, so the directory record is unchanged. More than 3 trailing bytes
   would be a deviation from the observed 0-3, and is recorded.
4. **Size policy (B), only if (A) cannot fit.** Allow a file up to 26,624 bytes
   (13 sectors) and update the directory record length. That changes the root
   directory sector and is recorded as a second change.
5. **Verification.** `decode(encode)` must equal the expected patched payload.

## Image Build Plan

1. Verify all 13 source components against the manifest.
2. Copy track 01 to `build/mshvsf_disc002/` and rewrite only the user data of LSN
   8,246-8,258.
3. Regenerate EDC/ECC (ECMA-130 Mode 1). Before trusting the routine, run it over
   **every** source sector and require it to reproduce the existing EDC/ECC exactly.
4. Copy tracks 02-12 and the CUE unchanged into the same directory.
5. Build twice and compare hashes.

## Prediction

**Offline:**

- `tools.disc.iso9660` on the derived track lists the same 414 files, with every
  hash equal to the source except `MC09.PAC`.
- `pac_lzss` decodes the new `MC09.PAC` to exactly the expected patched payload.
- Only sectors in LSN 8,246-8,258 differ, all with valid EDC/ECC.
- The two builds are byte-identical.

**Runtime:**

- A cold boot of the derived CUE in stock Mednafen reaches the title screen and
  character select.
- With Ryu/Ken in arcade mode, each Ryu win quote shows `あいう` in line-1 cells
  0-2, with the rest of the quote unchanged. At least two independent wins are
  recorded with screenshots.
- WRAM-L `0x002091AC-0x0020966B` (extracted from a derived-image save state) equals
  the expected patched table.

**Alternatives:**

- If the game rejects the file (hang, crash, or garbled screen), a size or
  integrity check or a header word is involved. Record it and test one variable at
  a time.
- If the marker is absent but the game runs normally, the game is not loading this
  `MC09.PAC` copy as assumed.

## Tooling (to build, with synthetic tests)

- `tools/disc/pac_lzss.py`: add the encoder (splice and full) and a round-trip test.
- `tools/disc/sector.py`: Mode 1 EDC/ECC compute and verify, tested against real
  sectors.
- `tools/disc/patch_image.py`: verify source hashes, write a derived image with one
  file replaced in place (same-sector allocation), regenerate EDC/ECC, refuse
  outputs outside `build/` or overlapping a source path, and emit a JSON manifest of
  changed LSNs and hashes.

## Actual Result

Pending.
