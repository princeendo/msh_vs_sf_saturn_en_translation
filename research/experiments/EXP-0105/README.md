# EXP-0105: How the Options menu is built (OPT-002 study, menu half)

Task: OPT-002 (study first)
Status: DONE
Confidence: CONFIRMED (code read from validated WRAM; the AUDIO / SOUND TEST
labels checked against the shots); HYPOTHESIS (every cost below: nothing was
built or run)

## Observation

- `OPT-002` asks for menu switches for build options. The user asked
  (2026-11-02) whether a sub-menu holding all of them is feasible.
- `EXP-0097` found the settings table, the backup-RAM bytes and the menu text,
  but not the menu code, the row count, or how BUTTON CONFIG is entered.

## Hypothesis

The Options screen is driven by a per-row table in `MM.BIN`. Adding a row, or a
screen like BUTTON CONFIG, is a matter of that table plus a few hooks, not a
new menu engine.

## Controlled Change

None. This is a static read of code already in RAM.

## Prediction

The code that draws the rows and moves the cursor reads a table of row
records. BUTTON CONFIG is a state of the same routine.

## Inputs and Provenance

- **States:** the `EXP-0097` session on the US release image (track 01
  `0c3f72bb…`), `local/loc006/play/rec/states`:
  - `f00003213.mcs` (`aa1844a1…0ca3`): OPTION MODE. Extracted WRAM-H
    `063a17b3…3097`, WRAM-L `73dc0f10…a04b`;
  - `f00005994.mcs`: BUTTON CONFIG;
  - `f00011611.mcs`: OPTION MODE again.

  The extracted regions go to `local/opt002/dumps/<state>/`. WRAM extraction
  is validated (`EMU-020` V2, byte-identical to agent reads).
- **Code check:** `0x0601DB00`-`0x0601F820` is identical in all three states
  except the byte `0x0601DFF4`. That byte is a data copy of DIFFICULTY,
  written by `0x0601DFDE`.
- **Shots:** `local/loc006/play/rec/shots/f00004753.png`, `f00004775.png`,
  `f00005055.png`.
- `MM.BIN` loads raw at `0x06018B00` (`docs/discoveries.md`). Its directory
  entry in RAM gives 848,396 bytes, so it spans `0x06018B00`-`0x060E7D0C`.
  The menu, the file loader and the save code are all in it.

## Tools and Environment

- `tools.memory.mcs_extract`, `tools.sh2.disasm`, Python 3.12 via
  `./invenv.sh`.
- `wram_free.py` (this directory).

## Procedure

1. Extract WRAM from the three states.
2. Search WRAM-H for longs that point into the menu text (`0x0601E700`-
   `0x0601F200`) and into the settings (`0x06017AA0`-`0x06017AE0`).
3. Disassemble `0x0601DB00`-`0x0601E7A0` and follow the calls.
4. Dump the row table and the label records.
5. `wram_free.py` over 474 recorded states (`local/loc006`, `local/re049`,
   `local/re050`).

## Actual Result

### 1. The menu is a state machine

- **`0x06017A84`** is the screen:
  - 0 = OPTION MODE;
  - 1 and 2 = BUTTON CONFIG;
  - 3 = backup save/load;
  - 99 = leaving.
- **The dispatcher (`0x0601DD14`)** calls each state's input routine and
  then its draw routine, by comparisons on `0x06017A84`.
- **OPTION MODE:**
  - input: `0x0601DEAE`;
  - values: `0x0601E520`;
  - labels: `0x0601DDEC`.
- **BUTTON CONFIG:**
  - input: `0x0601E1E8` / `0x0601E22C`;
  - draw: `0x0601E624`.
  - It is entered by the BUTTON CONFIG row's handler `0x0601E0D6`. On A or C
    that handler draws the screen title (`0x0601DE40`), sets `0x06017A84` to
    1 and clears both button cursors.
  - Start returns to the menu through `0x0601E212`, which redraws the labels
    and sets the state to 0.
- **Init (`0x0601DB5C`)** sets the defaults and reads the console's
  stereo/mono setting into `0x06017AA0`. It also sets the boss unlock
  `0x06017AB0` to 1, which is `OPT-001`'s patch at `MM.BIN` `0x50E4`.

### 2. Rows are table driven

`0x0601E954` has 16 bytes per row, 10 rows, with the row labels directly
after it:

| Row | Max | Label record | Setting | Handler | Screen |
| --- | --- | --- | --- | --- | --- |
| 0 | 7 | `0x0601E9F4` | `0x06017AB8` | `0x0601DFDE` | DIFFICULTY |
| 1 | 1 | `0x0601EA06` | `0x06017ABC` | `0x0601E154` | TIME LIMIT |
| 2 | 7 | `0x0601EA18` | `0x06017AC0` | `0x0601E188` | GAME SPEED |
| 3 | 1 | `0x0601EA2A` | `0x06017AC4` | `0x0601DFD8` | VS SHORT CUT |
| 4 | 1 | `0x0601EA3C` | `0x06017AA0` | `0x0601DFF6` | AUDIO |
| 5 | 46 | `0x0601EA4E` | `0x06017AC8` | `0x0601E020` | SOUND TEST |
| 6 | 0 | `0x0601EA60` | `0x06017AA4` | `0x0601E0D6` | BUTTON CONFIG. |
| 7 | 2 | `0x0601EA86` | `0x06017ACC` | `0x0601E100` | BACK UP |
| 8 | 1 | `0x0601EA98` | `0x06017AD0` | `0x0601E16C` | VS POWER GAGE |
| 9 | 1 | `0x0601EAAA` | `0x06017AD4` | `0x0601E172` | COMBO GAGE |

- **Input:**
  - left and right step the setting from 0 to Max and wrap;
  - then the handler runs every frame for the current row;
  - `0x06017A88` is the cursor and `0x06017A94` the current row's record.
- **The last row is not in the table.** `0x0601DEC2` loads 7, raised to 8 if
  `0x06017AA8` is set and to 9 if `0x06017AAC` is set.
- **Visibility:**
  - VS POWER GAGE is shown only when `0x06017AA8` ≠ 0, and COMBO GAGE only
    when `0x06017AAC` ≠ 0 (labels `0x0601DE0C`-`0x0601DE26`, values
    `0x0601E57C`-`0x0601E5A2`);
  - BACK UP is shown only when `0x06017A98` = 0.
  - The code at `0x06098A94`-`0x06098AB6` sets both flags on game-progress
    conditions (not traced) and then calls the save routine `0x0601A284`.
- **Values (`0x0601E520`)** are drawn one hard-coded call per row to
  `0x0601E4EC`, a generic routine:
  - `r8` = setting, `r9` = table of value strings, `r10` = cursor, `r4` =
    row;
  - it picks the highlight colour when the row is the cursor's.

### 3. Every string carries its screen position

- Each label and value string starts with `x, y` in 8-pixel cells and is
  drawn by `trapa #48` with function `0x33`.
- **Layout:**
  - rows sit at x = 6, y = 6, 8, …, 24 (COMBO GAGE at 24);
  - PRESS START BUTTON TO EXIT is at y = 26 (`0x0601E8FE`, blinked with
    the blank record `0x0601E921`);
  - the title OPTION MODE is at `0x0601E944` (`0A 02 01`).
- **Label strings:**
  - the labels of rows 0-7 are one string at `0x0601E79C`, with `\r` and a
    new position before each row;
  - VS POWER GAGE (`0x0601E8B8`) and COMBO GAGE (`0x0601E8DB`) are separate
    strings.
- **Room:** with COMBO GAGE shown, an 11th row would need y = 26, which
  moves PRESS START to y = 28 (pixels 224-231 of 240). Not tried.

### 4. BUTTON CONFIG reuses generic routines

- **Draw:** `0x0601E624` draws 16 values through the same `0x0601E4EC`, with
  cursors `0x06017A8C` (P1) and `0x06017A90` (P2) and button tables at
  `0x06017AD8` and `0x06017B00`.
- **Input:** `0x0601E27C` is parameterised:
  - `r11` = row table, `r12` = pad, `r13` = cursor, `r14` = settings base;
  - rows are fixed at 0-7;
  - a row whose handler field is 0 just stores the new value
    (`0x0601E310`).

### 5. Saving

- The save routine walks a copy list at `0x0601A344`. One entry copies
  `0x80` bytes from `0x06017AA8`, so these are saved with BACK UP:
  - the two unlock flags;
  - the boss unlock `0x06017AB0`;
  - `0x06017AB4`;
  - every setting from `0x06017AB8` to `0x06017AD4`;
  - both button maps up to `0x06017B27`.
- AUDIO (`0x06017AA0`) and the BUTTON CONFIG row's `0x06017AA4` are outside
  the block. AUDIO comes from the console setting.
- `0x06017AB4` is set to 0 at init (`0x0601DBE8`). No other reference to it
  was found among WRAM-H longs (HYPOTHESIS: an unused saved slot; register-
  offset uses would not show).

### 6. Correction to `EXP-0097`

- `EXP-0097` named `0x06017AC8` AUDIO and left `0x06017AA0` unidentified.
- The row table and the shots show the reverse:
  - `0x06017AA0` is AUDIO. It changed at f4758, and the shot at f4753
    already shows MONAURAL;
  - `0x06017AC8` is the SOUND TEST track (max 46). It changed at f5035, and
    the shot at f5055 shows 02 PLAYER SELECT.
- In the backup bytes, the slot `EXP-0097` read as "audio" is the SOUND TEST
  track.

### 7. RAM zero in every recorded state (`wram_free.py`, 474 states)

| Region | Start | Size |
| --- | --- | --- |
| WRAM-L | `0x0022FA00` | `0x600` |
| WRAM-L | `0x0023E000` | `0x2000` |
| WRAM-L | `0x0028E500` | `0x31700` (202,496 bytes) |
| WRAM-L | `0x002FC800` | `0x3800` (the end of WRAM-L) |
| WRAM-H | `0x060E9000` | `0x1000` |
| WRAM-H | `0x060ED100` | `0x500` |
| WRAM-H | `0x060EED00` | `0xC00` |
| WRAM-H | `0x060EFC00` | `0x400` |
| WRAM-H | `0x060FA000` | `0x2000` |
| WRAM-H | `0x060FE500` | `0x400` |

These are candidates for new code, not proof of free memory. The 474 states
do not cover every scene, and XvSF's first build hung when its routine landed
on live memory. A write log over a full session must confirm a region before
use.

## Conclusion

**CONFIRMED (code read):**
- The Options menu is a table-driven state machine.
- Rows, values and positions are data in `MM.BIN`.
- BUTTON CONFIG is a second state of the same machine, built from generic
  routines.

**HYPOTHESIS: costs, nothing built:**

| Option | What it takes |
| --- | --- |
| **One switch in the COMBO GAGE row** | In-place edits only, with no new routine:<br>• label text and value strings;<br>• the row's setting pointer moved to a saved slot (`0x06017AB4` if it is unused, or `0x06017AB0` for the boss unlock);<br>• its handler pointed at the empty `0x0601E16C`;<br>• the `0x06017AAC` tests (three places) made always-true, and the `0x06017AA8` tests too, or the cursor can stop on a hidden row 8.<br>The value is saved with BACK UP: SAVE. |
| **An 11th row** | All of the above for a new row record, which means moving the row table (one literal, `0x0601DFD4`). Also:<br>• a new label draw and value draw: hooks into `0x0601DDEC` and `0x0601E520`, so new code;<br>• the cursor maximums;<br>• PRESS START moved to y = 28. |
| **A sub-menu (a new state)** | New code in a confirmed free region:<br>• a row handler that enters the state;<br>• a dispatcher hook;<br>• glue that calls `0x0601E27C` (8 rows) and `0x0601E4EC`;<br>• exit through `0x0601E212`.<br>Plus its own title, labels and value strings, and a saved slot per switch. The `0x80` save block is full, so beyond `0x06017AB4`, extra switches would share bits or need another saved area. |

What each switch *does* is a separate cost (`EXP-0106`).

## Uncertainty and Alternatives

- **No dynamic check:**
  - the dispatcher and handlers were read, not stepped;
  - the 11th-row and PRESS START positions were not drawn;
  - the backup checksum (`EXP-0097`) is still untested.
- **`0x06017AB4`:** "unused" rests on a search for pointer literals only.
- **Unlock conditions:** what sets `0x06017AA8` and `0x06017AAC` was not
  traced.
- **Overscan:** y = 28 is visible in Mednafen; a real TV may crop it.

## Reproduction

```bash
for f in 00003213 00005994 00011611; do
  ./invenv.sh python -m tools.memory.mcs_extract \
    local/loc006/play/rec/states/f$f.mcs --region wram_h --region wram_l \
    --out-dir local/opt002/dumps/f$f
done
./invenv.sh python -m tools.sh2.disasm --base 0x06000000 \
  --start 0x0601DB00 --end 0x0601E7A0 local/opt002/dumps/f00003213/wram_h.bin
./invenv.sh python research/experiments/EXP-0105/wram_free.py \
  local/loc006/play/rec/states local/re049/play/rec/states local/re050/play/rec/states
```
