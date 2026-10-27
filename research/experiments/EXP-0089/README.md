# EXP-0089: The Mech-Gouki select code

Task: SPECIAL-004
Status: DONE
Confidence: CONFIRMED (select code and unlocks, in play; record 107's English,
forced trial); SUPPORTED (a Versus clear also sets `0x06017AA8`, by
disassembly only)

## Observation

- **The claim to test:** the user's GameFAQs copy says that after a Survival
  clear, holding Start while choosing Akuma twice gives Mech-Gouki.
- **The first attempt failed** (`EXP-0081`, US build with the boss fight
  unlocked): Akuma could not be chosen a second time.

## Hypothesis

The select screen has its own Mech-Gouki rule, with a condition the earlier
attempt did not meet.

## Static Result (Saturn `MM.BIN`, original image)

### The secret-character routine

The routine starts at `0x06051CD4`. The confirm paths of both picks call it:
point at `0x0604ED02`, partner at `0x0604F026`.

- **Inputs:** start buttons `r11 + 0xCC2E` (bit 0 = player 1, bit 1 =
  player 2), pads `0xCC2A`/`0xCC30` (player 1) and `0xCC2C`/`0xCC32`
  (player 2), punch/kick mask `0x0770`.
- **Start must be held:** the routine continues only while the player's
  Start bit is set.
- **The map of secret characters** (cursor → secret, character × 2):

  | Cursor | Secret |
  | --- | --- |
  | Blackheart (16) | Metal Zangief (40) |
  | Hulk (6) | Dark Sakura (42) |
  | Dhalsim (24) | Shadow (44) |
  | Vega (28) | U.S. Agent (46) |
  | Omega Red (12) | Mephisto (48) |
  | Spider-Man (14) | Armored Spider-Man (50) |

  Each swap is skipped if the player's team word already holds that secret
  character. With `0x0601801C` = 0 and `0x06017AA8` ≠ 0, that check uses a
  dummy word instead.
- **Gouki (30):**
  1. the per-player counter (`0x06017CEE` for player 1, `0x06017CEF` for
     player 2) goes up by 1;
  2. if `0x06017AB4` ≠ 0 and the counter is now 2, the character becomes
     Mech-Gouki (38), written to the cursor and both team words.
- **Counter reset:** both counters are zeroed when the select screen starts
  (`0x0604D79A`).
- **Matches known codes:** the map agrees with the codes the user used in
  `EXP-0078` (Blackheart → Metal Zangief, Dhalsim → Shadow).

### Who sets `0x06017AB4`

The routine at `0x060989F8` runs at the end of a mode. `0x0601801C` and
`0x06018024` are set when a game starts, by the title menu's action
handlers (table `0x0607A610`, dispatcher `0x0607A5C0`):

| Action | Mode | `801C` | `8024` |
| --- | --- | --- | --- |
| 2/3 | Arcade (player 1/2) | 0 | 0 |
| 4 | Versus | 0 | 0 |
| 6/7 | Survival (player 1/2) | `FF` | 0 |
| 8/9 | MECH-GOUKI NOW!! (`EXP-0075`: Start/A on menu index 5) | `FF` | `FF` |

At the end of the mode:
- **`801C` ≠ 0, `8024` = 0 (Survival):** sets `0x06017AB0` = 1, which
  unlocks MECH-GOUKI NOW!! (`EXP-0075`; the release presets it).
- **`801C` ≠ 0, `8024` ≠ 0 (MECH-GOUKI NOW!!):** sets `0x06017AB4` = 1,
  which makes Mech-Gouki selectable.
- **`801C` = 0 (Arcade, Versus):** sets `0x06017AA8` = 1, and
  `0x06017AAC` = 1 under further conditions.

No other code writes `0x06018024`. `0x06017AB0` and `0x06017AB4` are
cleared at boot (`0x0601DC48`/`0x0601DC4C` literals).

### The static prediction (before the play test)

1. Clear Survival, which unlocks MECH-GOUKI NOW!!. The release presets
   this.
2. Clear the MECH-GOUKI NOW!! fight, which sets `0x06017AB4`.
3. At character select, hold Start and pick Gouki, then hold Start and pick
   Gouki again: the second pick becomes Mech-Gouki.

The first attempt (`EXP-0081`) never cleared the MECH-GOUKI NOW!! fight, so
`0x06017AB4` was 0. Whether the second Start-held pick of Gouki is allowed
(no duplicate block before the routine) was not settled statically. The play
test below shows it is blocked until `0x06017AA8` is set.

## Correction to `EXP-0075`

- **Not saved data:** `0x0601801C` and `0x06018024` are mode flags set at
  game start.
- **Survival clear confirmed:** the boss-fight unlock follows a Survival
  clear, which `EXP-0075` had only assumed.
- **Session only:** the flags are cleared at boot, so the unlocks last for
  the session (HYPOTHESIS: they are not restored from backup memory).

## Play Test (2026-10-27, user at the controls)

### Setup

- **Image:** US release image, track 01 `39ae78b3…`.
- **Controller:** the user's PS4 controller.
- **Recorder:** `local/sp004/play/rec`.
- **Driver:** `tools/mednafen/mechgouki_driver.py --ko-boss`, logging to
  `local/sp004/play/driver.log`.
  - It logs every change of `AB0`, `AB4`, `AA8`, the mode flags, the Gouki
    counters and the team words.
  - It zeroes the boss's vitality once in MECH-GOUKI NOW!!.
  - Agent writes made by hand are noted in the log.

### Results, in frame order

1. **Boot:** `AB0` = 1 at frame 2,196, which is the release preset.
2. **MECH-GOUKI NOW!! (Ryu and U.S. Agent):**
   - mode flags `FF`/`FF` at frame 8,608;
   - the CPU team was `0026 0026` (Mech-Gouki, alone);
   - the driver knocked out the boss at frame 9,606;
   - **`AB4` = 1 at frame 11,283**, at the end of the mode.
3. **Arcade with `AA8` = 0, three attempts** (frames 20,748-29,652):
   - each Start-held pick of Gouki moved the counter to 1;
   - the partner cursor then skipped Gouki (`0x1E`), so the second pick
     never happened and the counter stayed at 1.
   - This matches the user's failed attempts. Without `0x06017AA8`, the
     partner select excludes the point character (`0x0604F566`).
4. **`AA8` forced to 1 by the agent** (frame 43,299), then a new Arcade
   game:
   - hold Start and pick Gouki: counter 1 (frame 45,112);
   - hold Start and pick Gouki again: the team words become `0026 0026` at
     frame 45,253 and the counter becomes 2;
   - the VS screen shows MECH-GOUKI alone against Dan and Sakura
     (`f00045735.png` `17b7b386…`).
5. **`AA8` reset to 0 by the agent** (frame 47,711) to see whether the
   Arcade clear sets it:
   - the user won stage 1;
   - `tools/mednafen/ending_driver.py --after-stage 1` sent the game to
     stage 8 and knocked out the boss (frames 69,008-70,617);
   - **stage 8 is a Mech-Gouki mirror:** CPU team `0026 0026` (frame
     70,046); the VS screen shows two Mech-Goukis (`f00070153.png`
     `dcbe7e70…`);
   - **`AA8` = 1 at frame 72,468**, at the end of the Arcade run.

### Mech-Gouki's ending

- **Post-boss dialogue:** a red Gouki stands beside the two Mech-Goukis. The
  boxes show, in order:
  1. a row of dots (`f00071498.png` `116cc6ce…`);
  2. a shorter row of dots;
  3. a row of dots;
  4. 作られし者よ・・・ (`f00072311.png` `3f03d123…`), the Japanese the
     user reported.
- **Where it comes from:** the four boxes are `MC13` records 54, 55, 106 and
  107. That is slot 19's partner pair and point pair (`EXP-0043`), since
  Mech-Gouki plays alone.
  - They are the Saturn's own records, not the arcade block (`EXP-0042`).
  - Rendered offline from the original `MC13.PAC` (`05263ab6…`):
    `local/sp004/dialogue/slot19.png` (`125446c4…`).
  - Records 54, 55 and 106 are only dots. Only record 107 is text.
- **No official English:** the US arcade's slot-19 partner lines are generic
  ("You are worthy {0000}.", "The fight is all we have, {0000}.") and do not
  correspond.
- **Ending pages:** "Congratulations!", "You've defeated the game / with a
  secret character!" (`f00072603.png` `e7548ae6…`, `f00072715.png`
  `ce721c75…`), then the credits.
  - These are `ME.PAC` `0x467C` records 0-2, which are already English on the
    Japanese disc (`local/sp004/dialogue/me467c.png` `3f4ce800…`).
  - So Mech-Gouki does not get Dan's pages. The Japanese table's slot-19
    pointer (`docs/coverage_exceptions.md`) is not what the Saturn uses here.

### Record 107 in English

- **Change:** a new table in `data/translations/secret_characters.json`:
  - `MC13.PAC` `0xA06C`, record 107;
  - source SHA-256 `6d7748c0…`;
  - lines `""`, "You who were created...".
- **Line 2, as in the original.** It is a new, faithful translation, the
  policy the user chose for records 42-43 (`EXP-0088`).
- **Records 54, 55 and 106 are kept.**

### Forced trial of record 107 (`verify_dialogue.sh`)

- **Build:** both release references rebuilt with the new record:
  - specs: Saturn names `a824a86e…`, American names `d79c2fce…`;
  - nine of nine references pass;
  - only `MC13.PAC` and track 01 change; the font gains no new pairs.

| Variant | Track 01 | xdelta | `.ssp` |
| --- | --- | --- | --- |
| Saturn names | `5999ca63d263d51815198230cd24e9516cfe4efacc26ccf8ee87af5eb8e7dd88` | 644,505 bytes, `587d3f1d…` | 563,100 bytes, `6623b523…` |
| American names | `d6bdd2e019b44b1f9b6430f25fe5bca43b4d9c71c1aa4d32e12398f6df6786f6` | 645,267 bytes, `420bc7af…` | 563,258 bytes, `7566715b…` |

- **The checkpoint:** `EXP-0039`'s `ryu_gouki_post_boss_ko.mcs`
  (`f42218550c0fb23c…`), with the built US image's font transplanted into
  its cart RAM.
- **The write:** the built record 107 replaces box 4's record (WRAM-L
  `0x0022BA40`). The write survived.
- **Result:** box 4 shows "You who were created...", centred on line 2, as
  in the original (`local/sp004/verify/box4_f1100.png` `c020f16e…`).
- **Not checked:** `saturn-patcher-egui` on the new `.ssp` files.
  `make_ssp`'s own applier round-trips both.

## Conclusion

- **CONFIRMED (in play): the Mech-Gouki select code.**
  1. Clear Survival, which unlocks MECH-GOUKI NOW!! (`0x06017AB0`). The
     release presets this.
  2. Clear MECH-GOUKI NOW!!, which sets `0x06017AB4`.
  3. Clear Arcade (or Versus, by disassembly), which sets `0x06017AA8`.
     Without it, the partner select skips the point character.
  4. At character select, hold Start and pick Gouki, then hold Start and
     pick Gouki again. Mech-Gouki then plays alone.
- **CONFIRMED (in play): Mech-Gouki's Arcade run.**
  - Stage 8 is a Mech-Gouki mirror.
  - The post-boss scene shows `MC13` records 54, 55, 106 and 107.
  - The ending pages are the disc's generic English ones (`ME.PAC` `0x467C`
    records 0-2), not Dan's.
- **CONFIRMED (forced trial):** record 107 shows its new English.

## Uncertainty and Alternatives

- **Not seen in a real run:** the new line was seen only in the forced
  trial, not in a full Mech-Gouki run.
- **Unlocks in the play test:** the boss KOs, and the first setting of
  `0x06017AA8`, came from the agent. The Arcade clear that set it on its own
  was itself a Mech-Gouki run.
- **The unlocks last only for the session:** they are cleared at boot
  (HYPOTHESIS: not restored from backup memory).
- **The translation is new,** not official text.

## Reproduction

```bash
# The play test: release US image under the agent build, then
./invenv.sh python -m tools.mednafen.mechgouki_driver --ko-boss --log local/sp004/play/driver.log
./invenv.sh python -m tools.mednafen.ending_driver --after-stage 1 --log local/sp004/play/ending_driver.log
# The rebuild (release references) and the forced trial of record 107:
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
bash research/experiments/EXP-0089/verify_dialogue.sh
```
