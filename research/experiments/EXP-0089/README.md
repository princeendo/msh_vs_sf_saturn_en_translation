# EXP-0089: The Mech-Gouki select code

Task: SPECIAL-004
Status: IN_PROGRESS
Confidence: SUPPORTED (disassembly); the play test is pending

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

### So (HYPOTHESIS until the play test)

1. Clear Survival, which unlocks MECH-GOUKI NOW!!. The release presets
   this.
2. Clear the MECH-GOUKI NOW!! fight, which sets `0x06017AB4`.
3. At character select, hold Start and pick Gouki, then hold Start and pick
   Gouki again: the second pick becomes Mech-Gouki.

The first attempt (`EXP-0081`) never cleared the MECH-GOUKI NOW!! fight, so
`0x06017AB4` was 0. Whether the second Start-held pick of Gouki is allowed
(no duplicate block before the routine) is not settled statically.

## Correction to `EXP-0075`

- **Not saved data:** `0x0601801C` and `0x06018024` are mode flags set at
  game start.
- **Survival clear confirmed:** the boss-fight unlock follows a Survival
  clear, which `EXP-0075` had only assumed.
- **Session only:** the flags are cleared at boot, so the unlocks last for
  the session (HYPOTHESIS: they are not restored from backup memory).

## Planned Play Test

- **Setup:** US release image; `tools/mednafen/mechgouki_driver.py --ko-boss`
  logs the words and knocks out the boss; recorder on.
- **The user:**
  1. plays MECH-GOUKI NOW!! (KO by the driver), checking that `0x06017AB4`
     becomes 1;
  2. starts Arcade and enters the code;
  3. if the duplicate block stops the second pick, tries other orders.
