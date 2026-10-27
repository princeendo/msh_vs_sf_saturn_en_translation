# EXP-0083: Spliced attract streams (a smaller release patch)

Task: REL-003
Status: DONE
Confidence: CONFIRMED

## Observation

The release patches are about 2.95 MB each. They were about 157 KB before
the English attract captions (`EXP-0071`). Per-region xdelta of the
Saturn-name release image against the original (`local/rel003/breakdown.py`,
xdelta3 3.2.2 `-9`), for each `MVSOP*.ST2`:

| Region | Bytes changed | xdelta |
| --- | --- | --- |
| Section A (script) | 158-185 K of 164-193 K | 118-143 KB |
| Section C (one graphics block) | ~94 K of 100 K | ~77 KB |
| Stream (`MISS` sectors, two graphics blocks) | 185-203 K | 144-172 KB |
| Whole file | | 337-369 KB |

The eight files are about 2.83 MB of the 2.95 MB patch. The decoded data
changes much less (`local/rel003/decoded_diff.py`,
`local/rel003/script_shape.py`):

- script: 7 of 2,064 frames, about 12.7 KB, and 103-105 bytes shorter (the
  later frames shift);
- section C: 24.6 KB of 238 KB;
- each changed stream block: about 15.5 KB of about 250 KB.

So most of the patch is the re-encoder's different choices, not new content.

## Hypothesis

A splicing encoder can keep the original compressed bytes wherever its tokens
still decode to the new data and re-encode only the changed stretches. It
must resume exactly where an original flag byte starts. That gives valid
streams of the same decoded content and a much smaller patch.

## Controlled Change

`tools/disc/st2_encode.py`:

- `lz_splice`: graphics blocks. Original flag groups (a flag byte plus 8
  tokens) are kept if every token still decodes to the new data at its
  position. Each run of other groups is re-encoded with an optimal parse
  whose token count is a multiple of 8.
- `script_splice`: section A. Units run between points where the original's
  flag bits are used up. A unit is kept if it lies inside one run of
  unchanged frames (positions mapped across the shift) and its tokens
  decode to the new script. Gaps are re-encoded with an optimal parse whose
  flag bits fill whole bytes; the last gap ends with the end marker.
- `_fit`: if a spliced stream is longer than its room, kept units whose
  optimal re-encoding saves the most bits are re-encoded too, in steps of
  1/64, until it fits. A full re-encode fitted only because it compresses
  better than the original overall; English tiles compress worse than the
  Japanese ones.

`tools/disc/attract_captions.py` uses them in place of `lz_encode` and
`script_encode`. The decoded content is unchanged.

## Prediction

Every block and section A round-trip and fit; the decoded script and graphics
equal the previous build's; the patch shrinks by an order of magnitude; the
attract captions look the same from a cold boot.

## Inputs and Provenance

Original Saturn image (manifest hashes); release references `m8_roster_gold`
and `m8_roster_gold_us`; xdelta3 3.2.2; Python 3.12.13.

## Procedure

1. Unit tests: both splicers round-trip, return the original unchanged when
   nothing changes, and keep at least 80% of the original after a small edit
   (`tests/unit/test_st2_encode.py`).
2. `MVSOP0` alone (`local/rel003/one_file.py`): rebuild, compare the decoded
   script and section C with the release build, xdelta both.
3. Rebuild both release references (`local/rel003/rebaseline.sh`), run all
   nine regression references, make both patches.
4. Cold-boot attract capture (`tools/mednafen/frame_capture.py`).

## Actual Result

### Version 1: splice, later bytes shift

- **One file (`MVSOP0`):**
  - xdelta 369,174 → 40,457 bytes;
  - decoded script and section C equal to the release build's;
  - rebuild time 12 s, after computing match tables once per block (the
    first version took 119 s, recomputing them for each of ~9,100 segments);
  - a finer fit step (1/512) gave 40,262 bytes in twice the time, so the step
    stays at 1/64.
- **Full build:** all nine references pass; patches round-trip. Saturn names
  2,952,126 → 932,677 bytes; US names 2,953,570 → 934,121 bytes (−68%).
- **Why not smaller:** the eight files' own deltas total only about 313 KB.
  The track patch works on raw 2,352-byte sectors, and each changed
  2,048-byte sector also changes its 304 bytes of EDC/ECC, which xdelta
  cannot predict. Re-encoded runs are shorter or longer than the bytes they
  replace, so everything after them in a section or block shifts:
  `MVSOP0` still changed 397 K bytes in 204 of its 1,315 sectors.

### Version 2: exact-length runs, nothing shifts

- **Change:** each re-encoded run must take exactly the original bytes up to
  the kept unit where it ends (`_lz_exact`, `_script_exact`). These use an
  interval DP of the fewest and most bytes per (position, flag state) and a
  greedy rebuild toward the target. A run grows over neighbouring groups
  until that is possible: graphics up to 1,024 groups after and 64-4,096
  before; script 64 units after, then ×4. Graphics blocks have no spare
  room, and one changed stretch in `MVSOP0`'s stream block `0xA12F4` covers
  11 KB of decoded data and needs far more bytes than the original. Only
  growing *backward* made it fit; growing forward over the whole block did
  not. `_fit` remains a last resort without exact runs.
- **One file (`MVSOP0`):** changed sectors 204 → 80, changed bytes 397 K →
  142 K, file xdelta 40,457 → 53,230 (the grown runs re-encode more bytes),
  rebuild 54 s.

- **Full build:** all nine references pass and both patches round-trip.
  Saturn names 701,266 bytes; US names 702,710. The eight streams change 618
  sectors (75-82 each) instead of about 1,600. Files' own deltas total 410,988
  bytes. The attract files are identical in both builds.

### xdelta window

- `make_patch` gains `-W 16777216` (xdelta3's largest input window). This
  lets later copies of repeated new data, such as the caption tiles that
  repeat in all eight streams, copy from earlier output: 701,266 → 642,747
  bytes. Zipping the patch saves only 4% (670,437), because the remaining
  bytes are new art and error-correction data.
- **Release patches:** `mshvsf_saturn_en_m8_gold.Track01.xdelta` 642,747
  bytes, `f7692948…` (track 01 `e820f6e1…`, spec `115f6cd3…`);
  `mshvsf_saturn_en_m8_gold_us.Track01.xdelta` 644,202 bytes, `3d23dcd8…`
  (track 01 `a6572495…`, spec `d441e9fc…`). Both round-trip with
  `xdelta3 -d`.

### Cold-boot attract check

- `frame_capture` on the Saturn-name image, frames 600-13,200 every 30 (the
  US image has the same attract files). It first failed: every agent
  `status` timed out after midnight, because Mednafen waits on vertical sync
  and the display was asleep. The silent home now sets `video.glvsync 0` and
  `video.blit_timesync 0` (`quiet_home`), after which the boot ran at about
  60 frames a second. While adding that, `str.splitlines()` broke a
  settings line holding byte 0x85, so `quiet_home` now splits on newlines
  only (tested).
- All three captions show in the banner colours, every loop:
  - "LEGENDARY / HEROES / UNITE AGAIN!!" (`f00002670.png`
    `f33f07476c4f3c43…`);
  - "NEW HEROES / JOIN / THE FIGHT!!" (`f00003450.png`
    `d85ec89abe4f4610…`);
  - "AMAZING / TEAM BATTLES!" (`f00006300.png` `ff536381e827fa72…`).
  The other scenes in the overview sheet look normal.

## Conclusion

**CONFIRMED:** re-encoding only the changed stretches, in exactly the
original number of bytes, gives valid attract streams with the same decoded
content. The release patches shrink by 78%.

## Uncertainty and Alternatives

- What remains is mostly new content: the English glyph tiles, the changed
  script frames, the neighbouring groups re-encoded to keep the length, and
  the error-correction bytes of each changed sector.
- Graphical VCDIFF patchers have not been tried with the 16 MiB window.
