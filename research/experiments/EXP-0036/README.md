# EXP-0036: Roster Image Live Check (Cyclops, Zangief, Captain America, Dhalsim)

Task: RE-046
Status: IN_PROGRESS (live sessions pending)
Confidence: HYPOTHESIS until the live runs

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

### Run 2

Pending: live sessions on `build/re046_roster`.
