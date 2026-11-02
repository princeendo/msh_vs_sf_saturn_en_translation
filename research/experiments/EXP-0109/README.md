# EXP-0109: The EXTRA OPTIONS sub-menu works on a patched checkpoint (OPT-004)

Task: OPT-004
Status: DONE (development checkpoint); the cold-boot check is the user's
session
Confidence: SUPPORTED (a checkpoint mixing two builds; every step matched
the prediction)

## Observation

- `EXP-0105` mapped the Options state machine. State 2 is never set, so its
  input routine `0x0601E22C` is dead.
- `EXP-0107` and `EXP-0108`: code in the quote font's tail loads at a fixed
  cart address and runs there.
- The agent cannot press buttons. At the title, the pad words the menu reads
  (`0x0601A3F4`, `0x0601A3F8`) are not touched, so title navigation cannot
  be injected there.

## Hypothesis

`--options-submenu` (`tools/text/options_submenu.py`,
`data/opt004/submenu.s`) gives:
- OPTION MODE: row 8 EXTRA OPTIONS, always shown; row 9 VS POWER GAUGE,
  shown when unlocked;
- a sub-menu in state 2 with BOSS FIGHT (`0x06017AB0`) and COMBO GAUGE
  (`0x06017AD4`, applied by the game's `0x0601E172`);
- Start returns to OPTION MODE.

## Controlled Change

- **The image:** the US release spec plus `--options-submenu`
  (`local/opt002/specs/us_submenu.json`), compiled to `build/opt004/us_submenu`:
  - track 01 `28303246…0fe7`;
  - a 1,024-byte tail at `0x027BF2A0` with a 676-byte payload
    (`3b05c917…66f6`);
  - 120 kanji sacrificed;
  - 17 `MM.BIN` writes, each with an expect check (all passed).
- **The checkpoint:** `menu_drive.py` writes the spec's `MM.BIN` range
  (`0x0601DB00`-`0x0601EB00`) and the payload into the recorded OPTION MODE
  state `local/loc006/play/rec/states/f00003213.mcs`.
- **Presses:** written to the pad words right after the dispatcher's first
  instruction (`0x0601DD3E`) for one frame.

## Prediction

The screens and RAM values described in the hypothesis, step by step.

## Actual Result

- **Run 1 (VS POWER GAUGE unlocked in the state):**
  - OPTION MODE shows EXTRA OPTIONS at y = 22 with "PRESS A OR C BUTTON",
    and VS POWER GAUGE (new spelling) at y = 24 (`02-up.png`);
  - A/C: state 0 → 2, and the sub-menu draws its big-font title EXTRA
    OPTIONS (every letter exists), BOSS FIGHT UNLOCKED and COMBO GAUGE
    NORMAL, with PRESS START BUTTON TO EXIT (`03-ac.png`);
  - right, down, right: BOSS FIGHT LOCKED, COMBO GAUGE FULL, and the
    highlight follows the cursor (`06-right.png`);
  - Start: state 0 → OPTION MODE redrawn (`08-start.png`).
- **Run 2 (`--poke 06017AA8=00000000`, VS POWER GAUGE locked):**

  | Step | State | Main cursor | `AB0` | `AD4` | `0x06049D34` |
  | --- | --- | --- | --- | --- | --- |
  | start | 0 | 0 | 1 | 0 | 0 |
  | up (wraps) | 0 | 8 | 1 | 0 | 0 |
  | A/C | 2 | 8 | 1 | 0 | 0 |
  | right (BOSS FIGHT) | 2 | 8 | 0 | 0 | 0 |
  | down, right (COMBO GAUGE) | 2 | 8 | 0 | 1 | 1 |
  | down (wraps), left | 2 | 8 | 1 | 1 | 1 |
  | Start | 0 | 8 | 1 | 1 | 1 |
  | up / down / down | 0 | 7 / 8 / 0 | | | |

  The redrawn OPTION MODE has no VS POWER GAUGE row (`11-down.png`).

## Conclusion

**SUPPORTED:** on a checkpoint, the patch set and the payload behave as
designed:
- entry, input, drawing and exit work;
- both settings change, and COMBO GAUGE's effect variable follows;
- the cursor's last row follows the VS POWER GAUGE unlock.

## Uncertainty and Alternatives

- **Checkpoint only:** the state's font and other RAM come from the older US
  release, so a cold boot of the image is still needed. Its tail is placed
  by the boot loader (`EXP-0107`).
- **Not tested here:**
  - BACK UP keeping both settings;
  - the title menu with BOSS FIGHT LOCKED;
  - what COMBO GAUGE FULL does in a fight;
  - the 0x06017C0C alternate colours.
- **Injection:** presses are written once per frame at the dispatcher, a
  shortcut a real pad does not take.

## Reproduction

```bash
C="build/opt004/us_submenu/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python research/experiments/EXP-0109/menu_drive.py \
  local/loc006/play/rec/states/f00003213.mcs local/opt002/specs/us_submenu.json "$C" \
  local/opt004/run2 --poke 06017AA8=00000000 \
  20 up:15 ac:40 right:20 down:20 right:20 down:20 left:20 start:40 up:15 down:15 down:15
```
