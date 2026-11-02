# EXP-0110: Cold-boot check of the EXTRA OPTIONS sub-menu (OPT-004)

Task: OPT-004
Status: DONE
Confidence: CONFIRMED (cold boot, the user's session, RAM from recorded
states, screenshots, and the user's report)

## Observation

`EXP-0109` showed the sub-menu working on a checkpoint that mixed two builds.
The acceptance criteria need a cold boot of the built image, with the
settings kept across a reset and their effect seen.

## Hypothesis

From a cold boot of the `--options-submenu` image:
- EXTRA OPTIONS opens the sub-menu;
- BOSS FIGHT and COMBO GAUGE change and are saved by BACK UP (AUTO);
- they survive a reset;
- BOSS FIGHT controls the title menu's CYBER-AKUMA NOW!!.

## Controlled Change

The image under test: the US release spec plus `--options-submenu`
(`local/opt002/specs/us_submenu.json`, `16e32fc6…7192`), track 01
`28303246…0fe7`. That is the only difference from the US release.

## Prediction

The settings change, survive a reset, and the title menu follows BOSS FIGHT.

## Inputs and Provenance

- **Session:** the user, 2026-11-02, in Mednafen with their own settings.
  - A new save file for this disc:
    `….9ab88c2be228a4e3acd3fe30b001c2f1.bkr`, `076b8730…` after the session.
    The user's other saves were untouched; the 0.1.0 image's save was copied
    to `local/opt004/play/` first.
  - Recorder `local/opt004/play/rec`: screenshots every second, states every
    5 seconds.
- **The recorder:** it stopped at a pause (a repeated frame number) and was
  fixed and restarted (commit `39d46d8`). Frames 10,249-10,275 have no
  screenshots.

## Procedure

The user followed the `OPT-004` step table:
1. OPTION MODE, then EXTRA OPTIONS: COMBO GAUGE to FULL and BOSS FIGHT to
   LOCKED.
2. Leave; reset the game.
3. Back to EXTRA OPTIONS: BOSS FIGHT to UNLOCKED; the title menu.
4. An Arcade fight.

Each state's WRAM-H was extracted (`mcs_extract`), and the menu state,
cursor, `0x06017AB0`, `0x06017AD4`, `0x06017AA8` and the combo effect
`0x06049D34` were listed wherever they changed.

## Actual Result

| State frame | Menu state | Cursor | BOSS FIGHT `AB0` | COMBO `AD4` | Effect `49D34` | Note |
| --- | --- | --- | --- | --- | --- | --- |
| f2002 | boot | | 1 | 0 | 0 | boot defaults (`OPT-001`'s unlock) |
| f4657 | 2 | 8 | 1 | 1 | 1 | in the sub-menu, COMBO GAUGE FULL |
| f4954 | 0 | 8 | 1 | 1 | 1 | back on OPTION MODE |
| f7015 | 0 | 8 | 0 | 1 | 1 | BOSS FIGHT LOCKED (entered again between samples) |
| f11099 | | | | | | reset |
| f12881 | boot | | 0 | 1 | 6→1 | the saved settings replace the boot defaults |
| f13469 | 2 | 8 | 0 | 1 | 1 | the sub-menu shows LOCKED / FULL (`f00013496.png`) |
| f14057 | 0 | 8 | 1 | 1 | 1 | BOSS FIGHT UNLOCKED again |

- **OPTION MODE:** EXTRA OPTIONS "PRESS A OR C BUTTON" at row 8. There is no
  VS POWER GAUGE row, since `0x06017AA8` is 0 on a new save
  (`f00006700.png`).
- **The title menu after the unlock:** the SURVIVAL row reads CYBER-AKUMA
  NOW!! (`f00014164.png`).
- **The user, with BOSS FIGHT locked:** "Yes, it stayed hidden" (L/R on
  SURVIVAL MODE).
- **The Arcade fight with COMBO GAUGE FULL:** it played normally
  (`f00016052.png`, `f00019314.png`). Its visible effect was not identified.

## Conclusion

**CONFIRMED (cold boot):**
- the sub-menu opens and changes BOSS FIGHT and COMBO GAUGE;
- COMBO GAUGE drives the game's own effect variable;
- both settings are saved by BACK UP (AUTO) and survive a reset. The saved
  value replaces the boot-time `OPT-001` unlock;
- BOSS FIGHT controls CYBER-AKUMA NOW!! in both positions.

## Uncertainty and Alternatives

- **COMBO GAUGE FULL's effect in a fight** is the game's own and was not
  identified.
- **Not run:** BACK UP: SAVE (NON-AUTO) and LOAD; the Saturn-names image (it
  gets the same `MM.BIN` writes, and every expected byte is the same in both
  variants, `OPT-004`).
- **VS POWER GAUGE unlocked:** shown only on the checkpoint (`EXP-0109`), not
  on this new save.

## Reproduction

```bash
# the image: EXP-0109's spec, compiled with tools.text.caption_compiler
# the timeline: for each state in local/opt004/play/rec/states,
#   mcs_extract --region wram_h, then read the addresses above
```
