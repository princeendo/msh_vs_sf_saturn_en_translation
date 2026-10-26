# EXP-0074: AKUMA life-bar labels on both sides from a cold boot

Task: LOC-004 (final verification)
Status: DONE
Confidence: CONFIRMED (cold boot, user input, screenshots)

## Observation

`EXP-0065` replaced the life-bar labels with the disc's own US label records
(full-width AKUMA for player 1, the italic set for player 2). It was verified
by replay trials and cold-boot RAM reads, not yet seen in a play-through.

## Hypothesis

From a cold boot of the current American-name release image, a fight with
Gouki on both sides shows AKUMA at full width on player 1's bar and the
italic, right-aligned AKUMA on player 2's.

## Controlled Change

None to the build. Image `build/regression/m8_roster_gold_us/build/image_a`
(reference `m8_roster_gold_us`, track 01 `db1ede9f…`), cold-booted. For this
run only, the keyboard drove controller port 2 (command-line overrides).

## Prediction

- Player 1's label reads AKUMA, about 2 px wider than in the `EXP-0064`
  capture (which clipped its last 2 px).
- Player 2's label reads AKUMA in the italic set, right-aligned.

## Inputs and Provenance

The user played on 2026-10-26: Versus mode; player 1 (controller) BISON and
AKUMA, player 2 (keyboard) SAKURA and AKUMA. The first round was Akuma
against Akuma.

## Tools and Environment

Patched Mednafen 1.32.1 agent; `tools/mednafen/session_recorder.py`
(screenshots every 0.5 s, 370 kept). Port-2 keyboard map: arrows, Return =
Start, Z/X/C = A/B/C, A/S/D = X/Y/Z (SDL scancodes 82, 81, 80, 79, 40, 29,
27, 6, 4, 22, 7).

## Procedure

1. Launch Mednafen on the US CUE with the port-2 overrides, and start the
   recorder.
2. The user plays to the first fight and lets it run for a few seconds.
3. Stop the recorder and Mednafen. Measure the green label pixels.

## Actual Result

- VS screen: BISON / AKUMA vs SAKURA / AKUMA.
- Fight (`local/loc004f/rec/shots/f00010535.png`, `1924da6e…`; zoom
  `labels_6x.png`, `61aa8695…`; full bar `hud_akuma_both.png`, `6f6b50d4…`):
  - player 1: **AKUMA**, green span x 25-73 (49 px). The `EXP-0064` capture
    of the earlier build spans x 25-71 (47 px): the clipped 2 px are back;
  - player 2: italic **AKUMA**, right-aligned, x 280-326.
- Partners' labels below the bars: BISON and SAKURA (`f00011106.png`,
  `c943bae1…`).
- **Side effect found:** Mednafen wrote the command-line port-2 settings into
  `local/mednafen/mednafen.cfg` on exit. The configuration was restored from
  the copy taken before the run (`local/loc004f/mednafen.cfg.before`); only
  the port-2 lines had changed.

## Conclusion

**CONFIRMED in play from a cold boot:** the record-based AKUMA labels show at
full width on player 1's bar and in the italic set on player 2's. This was
`LOC-004`'s last open item.

## Uncertainty and Alternatives

The labels sit partly behind the bar and the "NEW HERO" text, as every label
does in this layout (also in `EXP-0064`).

## Reproduction

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" MEDNAFEN_AGENT_DIR="$PWD/local/mednafen/agent" \
  vendor/mednafen/build-agent/src/mednafen \
  -ss.input.port2.gamepad.up "keyboard 0x0 82" -ss.input.port2.gamepad.down "keyboard 0x0 81" \
  -ss.input.port2.gamepad.left "keyboard 0x0 80" -ss.input.port2.gamepad.right "keyboard 0x0 79" \
  -ss.input.port2.gamepad.start "keyboard 0x0 40" -ss.input.port2.gamepad.a "keyboard 0x0 29" \
  -ss.input.port2.gamepad.b "keyboard 0x0 27" -ss.input.port2.gamepad.c "keyboard 0x0 6" \
  -ss.input.port2.gamepad.x "keyboard 0x0 4" -ss.input.port2.gamepad.y "keyboard 0x0 22" \
  -ss.input.port2.gamepad.z "keyboard 0x0 7" \
  "$PWD/build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python -m tools.mednafen.session_recorder local/loc004f/rec --shot-interval 0.5 --state-interval 3 --keep-states 80 --keep-shots 0
```

Back up `local/mednafen/mednafen.cfg` first and restore it afterwards.
