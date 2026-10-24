# EXP-0036: Roster Image Live Check (Cyclops, Zangief, Captain America, Dhalsim)

Task: RE-046
Status: DONE (2026-10-24)
Confidence: CONFIRMED (run 2, `build/re046_roster`)

## Observation

`EXP-0035` built the 17-character official-English roster image (`build/re045`,
track 01 `f5044e8a…`) and reviewed it offline. Only Ryu and Ken have been verified
live (`EXP-0033`, `EXP-0028`).

## Hypothesis

The roster image works at runtime for characters beyond Ryu and Ken, including
files with blocks left untouched (`MC02`, `MC0C`). The game reads each
character's compiled table from the expected slot base, and all 16 records
display their paired English.

## Controlled Change

No new build. The runs use `build/re045` exactly as reviewed.

## Plan (agreed with the user, 2026-10-24)

| Session | Team (point first) | KO 1 (team slot 1) | KO 2 (team slot 2, tag in) |
| --- | --- | --- | --- |
| 1 | Cyclops, Zangief | Cyclops | Zangief |
| 2 | Captain America, Dhalsim | Captain America | Dhalsim |

Coverage:
- Marvel (Cyclops, Captain America) and Capcom (Zangief, Dhalsim) fighters.
- Both team slots.
- One-line records (Cyclops entries 0 and 2).
- Dropped placeholders: Zangief has four, including one at line 2 cell 0.
- Irregular files whose other blocks stay untouched (`MC02`, `MC0C`).

## Prediction

| Character | File | Expected table base |
| --- | --- | --- |
| Cyclops (slot 1) | `MC01` | `0x0020AC50` |
| Zangief (slot 2) | `MC0D` | `0x0021C7F4` |
| Captain America (slot 1) | `MC02` | `0x0020D6D8` |
| Dhalsim (slot 2) | `MC0C` | `0x0021AA88` |

- For each character, all 16 forced records pass `verify_records.py --compile-dir
  build/re045`: pointer, cart-RAM font, WRAM-L table, display buffer, and screen.
- Records 8-15 tie with 0-7, and every screenshot reads as the paired English.

**Refuted if:** any KO uses another file's table or base, any record fails, or any
screenshot shows wrong, blank, or garbled text.

## Actual Result

### Run 1 (2026-10-24): reset to the BIOS while the fight loaded

- **What happened.** Session 1 on `build/re045` (`f5044e8a…`): the game dropped to
  the Saturn BIOS CD-player screen while the first fight loaded, after the user
  picked Cyclops, Zangief, Manual, and Turbo.
- **Not the image in general.** The image ran attract demos for 3+ minutes
  without resetting, and a character-select checkpoint idles without resetting.
- **Not the game on its own.** On the untouched original image the same picks
  reached the fight. A rolling save-state loop (every second) captured the
  stage-map moment just before the fight load (`preload_stagemap_f5429.mc`,
  SHA-256 `afd4ce1c…`). The opponents were Dan and Sakura.

### Diagnosis (no further gameplay)

New tool `tools/mednafen/replay_state.py`. Loading a state saved on one image,
while another is mounted, replays that moment with all later disc reads from the
mounted image.

1. **Reproduced and isolated.**
   - From the stage-map state, `build/re045` reaches the BIOS within about 2-4 s;
     the original reaches the fight.
   - Single-file images (original plus one roster file) show that only
     `MC12.PAC` (Dan, an opponent here) resets. `MC10.PAC` and `MEMFIX.PAC`
     alone are fine.
2. **Decoding is correct.**
   - Work RAM-L dumps show Dan's file decoded at `0x00230000`, byte-identical to
     our decoder's output; only the table cells differ from the original.
   - Restoring Dan's two dropped placeholders did not help (`DISPROVEN` as the
     cause).
3. **Mechanism trace.**
   - No exception vector fired, and the only SMPC writes were the routine
     controller poll.
   - Halting on the first BIOS-ROM instruction showed the threaded-code
     interpreter (`trapa #63` handler at `0x060195A0`, `jmp @r0` to the next
     address) jumping to 0. Just before, it had read the pointer `0xA100EA20` from
     `r6 + 64`.
4. **First divergence.**
   - Work RAM is identical until frame 141 after the state load. Then 6 bytes
     differ in the file-read descriptor at `0x0603E8E9`
     (`MC12    PAC`, size `0x5814`): it holds the PAC header's declared compressed
     length + 8. Original: `0x5801`. Roster: `0x56EE`.
   - Per-variant data: files declaring within 3 bytes of the original length
     worked; those declaring 270-400 bytes less reset.
5. **Single-variable test (CONFIRMED).**
   - The roster `MC12` with only its two header length words restored
     (`0x80005801`, `0x000057F9`), the stream unchanged and zero-padded, reaches
     the fight.
   - The game decodes it byte-identically, with nothing written past the decoded
     length.

### Fix

- `build_pac` now accepts a declared length. `pac_patch.patch` keeps the
  original declared compressed length, zero-padding a shorter stream up to it.
  Tests are added.
- The rebuilt roster image `build/re046_roster` (track 01 `351254c4…`) declares
  the original length in all 17 files, passes every compiler check, and reaches
  the fight from the stage-map state.

### Run 2 (2026-10-24): all four characters pass

- **Image.** `build/re046_roster` (track 01 `351254c4…`). It differs from
  `build/re045` only in PAC headers and padding: all 17 decoded tables, `MEMFIX`,
  and all 17 offline renders are byte-identical, and all 78 manifest checks are
  true.
- **Gameplay.** Two sessions, as planned; four user KOs. `ko_capture.py` saved a
  post-KO checkpoint for each (ignored, `local/mednafen/agent/runs/re046-*`):

  | KO | `postko.mc` SHA-256 |
  | --- | --- |
  | Cyclops | `a776ae09…` |
  | Zangief | `3d190193…` |
  | Captain America | `548e935c…` |
  | Dhalsim | `b00df2a1…` |

- **A second quote state.** For Zangief, Captain America, and Dhalsim the capture
  read the table base `0x0607FD0C` and index 0 from `0x060F9E4A` / `0x060F9E66`,
  yet the pointers fell inside the predicted tables. The log showed the pointer
  routine (`060AF724`) running with `r12` = `0x060F9ED6`, not `0x060F9E16`
  (Cyclops).
  - Hypothesis: a second state with the same layout, base at `r12 + 0x34` and
    index at `r12 + 0x50`.
  - Test: reading `0x060F9F0A` / `0x060F9F26` from each quote state gave exactly
    the predicted bases (`0x0021C7F4`, `0x0020D6D8`, `0x0021AA88`) and indices
    13, 6, and 14. Pointer = base + 76 × index in all four runs.
  - A forced write of 0 to `0x060F9F26` after the setter `060AF282` (which wrote
    the natural 13) moved Zangief's pointer to the table base.
  - Tools: `ko_capture.py` now arms both index words, reports the state that
    produced the pointer (`quote_state`), and forces the `--quote-state` index.
    `verify_records.py` reads the base and index from the matching state.
  - What selects the state is open (`docs/known_unknowns.md`).
- **Natural captures.** Cyclops record 3, Zangief 13, Captain America 6, and
  Dhalsim 14. All pass every check; 13 and 14 tie with their identical records
  5 and 6.
- **Forced captures.** 64 runs (16 per character), each loaded from that
  character's checkpoint with no gameplay. `verify_records.py --compile-dir
  build/re046_roster` passes all 68 captures (64 forced plus 4 natural; report
  `local/re046/verify_run2.json`, SHA-256 `f97540a7…`):

  | Character | Quote state | Table base | File | Result |
  | --- | --- | --- | --- | --- |
  | Cyclops | `0x060F9E16` | `0x0020AC50` | `MC01` | 16/16 |
  | Zangief | `0x060F9ED6` | `0x0021C7F4` | `MC0D` | 16/16 |
  | Captain America | `0x060F9ED6` | `0x0020D6D8` | `MC02` | 16/16 |
  | Dhalsim | `0x060F9ED6` | `0x0021AA88` | `MC0C` | 16/16 |

  - Every check passes in every run: pointer, cart-RAM font, WRAM-L table, and
    display buffer. Screen IoU is 1.0 for the forced record, or for its identical
    twin (records 8-15 tie with 0-7).
  - No placeholder glyphs appear, so the dropped placeholders (including
    Zangief's four) leave nothing behind.
- **Screens.** I read all 68 screenshots. Each shows the spec's paired English,
  including the one-line records (Cyclops 0, 2, and 6; Captain America 3;
  Dhalsim 6), with nothing blank or garbled.
- **Cosmetic.** The pair glyphs draw lowercase `p` with its descender cut short,
  so it sits on the baseline ("Freedom prevails!"). It is legible and identical in
  the offline renders, so it is a font-design matter, not a runtime fault
  (`docs/known_unknowns.md`).

## Conclusion

`CONFIRMED`. The roster image shows its compiled official English at runtime for
Marvel and Capcom fighters, in both team slots, from files with untouched extra
blocks (`MC02`, `MC0C`), and with dropped placeholders. Each KO used its own
file's table at the predicted base. A patched PAC file must keep its declared
compressed length (run 1).

## Uncertainty

- Four characters were verified live. The other 13 rest on offline equivalence:
  same mechanism, decoded tables equal to the compiled ones, renders reviewed.
- What selects the second quote state is unknown.
- The declared-length mechanism (why a shorter length breaks the load) is
  `HYPOTHESIS`; the fix is confirmed.

## Reproduction

1. Build `build/re046_roster` from the `RE-044` spec (`local/re044/
   roster_official_en.json`, `b2c097fa…`) with `caption_compiler.py`, as in
   `EXP-0035`. Track 01 should be `351254c4…`.
2. Start the patched Mednafen on that image. For each character, run
   `ko_capture.py --checkpoint --out-dir <run>` and play one KO with that
   character.
3. For each record `i` from 0 to 15, run `ko_capture.py --state <run>/postko.mc
   --out-dir <run>-rNN --force-index i --setter-pcs 060AF282 --quote-state <r12>`.
   `<r12>` is the `quote_state` that the natural capture reports.
4. `verify_records.py --compile-dir build/re046_roster <runs>`, then read every
   `quote.png`.
