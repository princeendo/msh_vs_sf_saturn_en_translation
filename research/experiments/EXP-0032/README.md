# EXP-0032: PS1 English Win Quotes Are Byte-Identical to the Arcade's

Task: REF-005
Status: DONE
Confidence: CONFIRMED (data identity). The PS1 on-screen display was not captured.

## Observation

The PS1 disc (`SLUS-00793`, Redump-verified in `REF-011`) has 241 ISO 9660 files on
a Mode 2 track. Most are arcade-style data (`.A0`, `.SE`, `.DSP`, `.TTT`, `.ARC`).

## Hypothesis

The PS1 port stores Ryu's English win quotes in a readable form that can be
compared directly with the arcade table (`EXP-0029`).

## Controlled Change

None. Read-only search of the disc's Form 1 files (XA audio files excluded).

## Prediction

If the PS1 reuses the arcade text, some encoding of Ryu's lines will be found. A
whole-block comparison will then show whether the wording differs.

## Inputs and Provenance

- `Marvel Super Heroes vs. Street Fighter (USA).bin`: 552,894,048 bytes, SHA-1
  `6e50ac0d…3ec3721a` (Redump 12632), in the ignored
  `local/disc_images/mshvsf_ps1_us/`.
- Arcade `mshvsfu` (`references/mshvsf/arcade/README.md`) and pinned MAME 0.289
  `cps2.cpp`.

## Tools and Environment

- `tools/disc/iso9660.py`, extended to read Mode 2 Form 1 user data. It reports
  Form 2 (XA) files as unreadable instead of aborting.
- `tools/reference/ps1_text.py` (new) and Python 3.12.13.

## Procedure and Actual Result

1. **ASCII search.** Searching all Form 1 files (52.1 MB) for Ryu words found no
   win-quote hits. "challenge" occurs only in opening-demo text.
2. **Encoding.** The arcade 16-bit codes, **little-endian**, matched in
   `DAT/SELECT.BIN` (and in `DAT/SEL.ARC`, 44 bytes later). A relative search for
   "discipline" found base `0x161` (= arcade `a`), little-endian, and no other
   base.
3. **Whole-block comparison.** Each of the 26 arcade English slot blocks (8 × 100
   bytes) was byte-swapped and found **in full** in `SELECT.BIN` (SHA-256
   `c78b1502…`), at stride `0x320` from `0x0F8EC`. Ryu's slot 9 is at `0x1150C`.
   Slots 20, 21, and 25 resolve to the same blocks as 13, 16, and 7, as in the
   arcade. The output is in `references/mshvsf/ps1_us/arcade_en_comparison.json`.
4. **Extra PS1 blocks.** At `0x1376C` and `0x13A8C` there are two further
   all-Latin `0x320` blocks that match no arcade block. They sit where slots 20 and
   21 would fall at that stride. Their text was not read: secret characters are
   out of scope (`SPECIAL-001`).
5. **Japanese table.** The Saturn/arcade Japanese Ryu table does not occur on the
   US PS1 disc.

## Conclusion

**CONFIRMED:** the US PS1 release's English data for Ryu's 8 win quotes is
byte-identical to the arcade's, and so is the data for every arcade slot. For
Ryu, the PS1 English equals the arcade English (`ps1_us_text` = `arcade_us_text`).
It adds no discriminating wording evidence.

## Uncertainty and Alternatives

- The PS1 display was not captured. The PS1 could select, wrap, or render
  differently. The data identity makes different wording unlikely, but it does not
  prove what is drawn on screen. A capture would need a PS1 emulator setup, which
  was judged not useful for `REF-005`'s purpose.
- **HYPOTHESIS:** the two extra blocks give the PS1 its own English quotes for two
  secret characters (perhaps Mech-Zangief and Dark Sakura). They are untested and
  deferred to `SPECIAL-001`.
- The PS1's own selection logic and pointer table were not traced.

## Reproduction

```bash
./invenv.sh python -m tools.reference.ps1_text --ps1-track "local/disc_images/mshvsf_ps1_us/Marvel Super Heroes vs. Street Fighter (USA).bin" --driver /tmp/cps2.cpp --archive local/arcade_roms/mshvsf/mshvsfu.zip
```
