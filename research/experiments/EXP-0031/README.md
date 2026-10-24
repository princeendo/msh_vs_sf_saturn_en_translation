# EXP-0031: Pairing Saturn Ryu Captions With Arcade English by Game Logic

Task: REF-003, REF-004
Status: DONE
Confidence: CONFIRMED

## Observation

- The Saturn Ryu table (`MC09.PAC`, decoded `0x91AC`) has 16 Japanese records of
  2 × 19 codes. The arcade English slot 9 has 8 entries of 2 × 25 codes
  (`EXP-0029`, `EXP-0030`).
- Japanese codes on both platforms are 16-bit values in the `0x08xx` range.
- The arcade quote pointer is at `0xFF249C` and the Saturn's at `0x060F249C`. The
  arcade index is at `0xFF9E66` and the Saturn's at `0x060F9E66` (`RE-023`).
- The Saturn uses record size 100 under a flag (`RE-023`), and 100 is the arcade
  English entry size.

## Hypothesis

The arcade program contains the Saturn's Ryu table unchanged. The arcade's own
selection code then defines which English entry is shown in the state that shows
Japanese record `k`.

## Controlled Change

None to game files. Two interventions on the selected index only:

- a MAME write tap forcing the stored index;
- a debugger breakpoint setting the pre-mask value in D0.

## Prediction

1. The Saturn record lines occur in the arcade program as one contiguous,
   byte-identical table.
2. In English, the stored index is a function `f(k)` of the 16-way value `k`, which
   the code makes explicit.
3. Forced indexes display the corresponding entries on screen.

## Inputs and Provenance

- `MC09.PAC` (extracted; SHA-256
  `6c096573622a515ceb81436dacbe9ed732adab11fde87a43c4e497e4b56a0016`) and
  `MEMFIX.PAC` from the recorded Saturn source.
- Arcade sets `mshvsf`, `mshvsfu`, and `mshvsfj` with keys and `qsound.zip`
  (`references/mshvsf/arcade/README.md`).

## Tools and Environment

- MAME 0.289 (Homebrew), headless. With `-debug -debugger none`, MAME's debugger
  runs Lua-issued commands (`dasm`, `bpset`).
- `tools/reference/mame_timeline.lua` gained new verbs: `force16`, `unforce`,
  `logwrites`, and `debug`.
- `tools/reference/quote_pairing.py`, `tools/text/quote_render.py`, and
  `tools/reference/arcade_route.py`.

## Procedure and Actual Result

1. **Table identity.** Every line of Saturn records 0-15 occurs once in the arcade
   program, in order, at `0x20EDB0`-`0x20F246`.
   - The 16 × 76-byte table at `0x20EDAC` is byte-identical to the Saturn table in
     all three sets (Saturn table SHA-256 `6aaf1f88…715c3023`).
   - It is slot 9 of a 26-entry Japanese pointer table at `0x20BFAC` (entry at
     `0x20BFD0`), just before the English, Spanish, and Portuguese tables
     (`0x20C014`, `0x20C07C`, `0x20C0E4`).
2. **Writer of the index.** A `logwrites` tap on `0xFF9E66` during natural Ryu wins
   showed the index store at `mshvsfu` PC `0x07036A` (value 6) and `mshvsfj` PC
   `0x07038C` (value 14).
3. **Selection routine** (MAME `dasm` of decrypted opcodes; `mshvsfu`
   `0x070328`-`0x070380`; `mshvsfj` and `mshvsf` are the same code a few bytes
   later):
   - Take a random value (`jsr $192C`). The flag `(-$37CD,A5)` selects a per-slot
     word table instead.
   - In Japanese only, a value of 39 after `& 0x3F` selects a special record
     (`0x213E6C`).
   - Mask: index = value `& 0x0F`.
   - If the language word `(-$3370,A5)` is non-zero, read the index through the
     byte table at `0x0703CA` (`mshvsfu`). That table is `00 01 02 03 04 05 06 07 00
     01 02 03 04 05 06 07` in all three sets.
   - Store the index at `+0x50` (`0xFF9E66`). Choose the pointer table by language
     from `0x20BFAC`, `0x20C014`, `0x20C07C`, `0x20C0E4`, and store
     `table[slot]` at `+0x34` (`0xFF9E4A`).
   - In the raw ROM, this region is still encrypted; the game reads these
     PC-relative tables through the decrypted opcode space.
4. **Breakpoint test.** A breakpoint on the mask instruction set D0 before
   masking:

   | Set | Pre-mask D0 | Stored index | Pointer | Screen |
   | --- | ---: | ---: | --- | --- |
   | `mshvsfu` | 12 | 4 | `0x21BBB0` | English entry 4 |
   | `mshvsfu` | 9 | 1 | `0x21BA84` | (not inspected) |
   | `mshvsfj` | 12 | 12 | `0x20F13C` | Japanese record 12 |
   | `mshvsfj` | 9 | 9 | `0x20F058` | (not inspected) |

5. **Forced indexes** (write tap on `0xFF9E66`, all values 0-15 per set):
   - `mshvsfu` pointer = `0x21BA20 + 100k`. Values 0-7 displayed all eight English
     entries, matching the `EXP-0029` decode line for line. Values 8-15 run into
     slot 10's block, because forcing bypasses the remap.
   - `mshvsfj` pointer = `0x20EDAC + 76k`. All 16 Japanese records displayed and
     matched the transcription. Record 0's placeholder showed ケン (partner Ken).
6. **REF-003 transcription.**
   - Records 0-15 were rendered offline with `quote_render.py` (ignored
     `local/ref003/ryu_records_0_15.png`).
   - Two transcriptions were made: the main session's, and a separate agent's that
     never saw the first. They are identical on all 32 lines.
   - A script checked every line's cell count, blank cells, hiragana (codes
     `0x0800+n` = U+3041+n), and punctuation (`08A9` 、, `08AA` 。, `08AE` ・, `08BD`
     …, `08DD` ！, `08DF` ‼) against the codes. Zero mismatches.
   - Katakana and kanji rest on the two matching visual readings. 力 and 一 were
     chosen from context.
7. **Pairing.** `quote_pairing.py` produces the same report (SHA-256 `720a78df…`)
   for all three sets. It is committed as metadata and hashes in
   `data/text/ryu_arcade_pairing.json`. Full text is only in the ignored
   `local/ref003/ryu_pairing_full_text.json`.

## Conclusion

**CONFIRMED** (predictions 1-3):

- Saturn Ryu record `k` is byte-identical to arcade Japanese record `k`.
- In the same selection state, the arcade shows English slot 9 entry `k & 7`.
- So, by the game's own logic: Saturn records `k` and `k + 8` both correspond to
  official arcade English entry `k & 7`.
- The Q10 subject (record 8) corresponds to entry 0.

This is a **game-logic** correspondence, not a translation claim.

## Uncertainty and Alternatives

- **Not translations.** On a reading of both texts, the English entries are
  separate rewrites, not translations of either Japanese record they pair with.
  For example, record 8's meaning is closer to entry 4 than to its paired entry 0.
  That is a judgment, not evidence. Choosing between the official paired English
  and a meaning-based English is a project policy decision.
- **Saturn selection.** That the Saturn selects records with the same mask (and
  keeps any remap) is `SUPPORTED`: `RE-023` found the same index address, the
  special value 39, and the `0xCC90` flag. It is not confirmed. The pairing does
  not depend on it, because the record identity is byte-level.
- **Not established:**
  - the random routine `$192C`;
  - the `(-$37CD,A5)` per-slot path;
  - the special record `0x213E6C`.
- **Coverage.** Only Ryu (slot 9) was paired. The tool takes `--slot` and table
  offsets for other characters, whose Saturn PAC files differ.

## Reproduction

```bash
./invenv.sh python -m tools.reference.quote_pairing --saturn-pac research/extracted_files/mshvsf_saturn_jp/MC09.PAC --driver /tmp/cps2.cpp --archive local/arcade_roms/mshvsf/mshvsfu.zip
```

Forced index `k` on the US route (frame 10300) or JP route (frame 8450; loop end
8400): add `10300 force16 0xff9e66 k` (or `8450 …`) to an `arcade_route.py`
timeline. Pre-mask breakpoint: add
`10300 debug bpset 070356,1,{d0=c; go}` (`mshvsfu`; `070378` on `mshvsfj`) and run
MAME with `-debug -debugger none`. Disassembly: `dasm <file>,70300,140` through
`manager.machine.debugger:command`.
