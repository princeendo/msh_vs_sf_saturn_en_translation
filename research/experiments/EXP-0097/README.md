# EXP-0097: Where the Options menu keeps its settings (LOC-006 feasibility)

Task: LOC-006 (feasibility, second part)
Status: DONE (this experiment); LOC-006 stays `BACKLOG`
Confidence: CONFIRMED (the settings table, the backup-RAM bytes, the menu
text); HYPOTHESIS (that the hidden COMBO GAGE row could carry a name switch)

## Observation

- `EXP-0095` left the menu, option-storage and code-hook questions to a
  session at the Options menu.
- The agent cannot send input, so the user changed each setting once, with a
  pause after each change.

## Hypothesis

Each setting is one value in work RAM that changes exactly when the screen
shows the change. Leaving the menu copies the values to backup RAM.

## Inputs and Provenance

- **Image:** the US release image (`build/regression/m8_roster_gold_us`,
  track 01 `0c3f72bb…`).
- **Session (2026-10-28):** the user, 1P. Title → OPTION MODE → one step
  right on each setting → BUTTON CONFIG → exit with Start.
  - Recorder `local/loc006/play/rec`: a state every second (235 states),
    a shot every half second (467 shots).
  - Backup RAM file
    `local/mednafen/sav/…40054e486221acf1e259bf6107e9c200.bkr`, copied before
    the session (`bfaab47c…`) and after (`9e72ddf5…`).

## Procedure

1. `stable_diff.py <states> 3000 3300 11890 12070`: bytes steady on the
   Options screen at the start and steady at a different value at the end.
2. The table found that way, read from every state (change log below).
3. Each change frame matched against the shots.
4. `cmp -l` of the backup RAM file before and after.
5. The menu strings searched in every file of track 01.

`option_bytes.py` (bytes stepping by one) found nothing useful, because the
same bytes also change at boot. It is kept as a record of the attempt.

## Actual Result

### 1. The settings table (WRAM-H, one long per setting)

| Address | Setting | Values seen | Change in the session |
| --- | --- | --- | --- |
| `0x06017AA0` | not identified | 0, 1 | 0 → 1 at f4758, between the short-cut and audio changes |
| `0x06017AB8` | DIFFICULTY | 1 = ★★, 2 = ★★★ | f3480 |
| `0x06017ABC` | TIME LIMIT | 1 = ON, 0 = OFF | f3870 |
| `0x06017AC0` | GAME SPEED | 0 = ★, 1 = ★★ | f4260 |
| `0x06017AC4` | VS SHORT CUT | 0 = OFF, 1 = ON | f4540 |
| `0x06017AC8` | AUDIO | 0 = STEREO, 1 = MONAURAL | f5035 |
| `0x06017ACC` | BACK UP | 0 = AUTO, 1 = another value | 0 → 1 at f11669, back to 0 at f11899 (the shot at f11686 shows the row changing) |
| `0x06017AD0` | VS POWER GAGE | 0 = NORMAL, 1 = FULL | f12067, just before exit (shot f12062 shows FULL) |

- Each change matches the shot taken at that moment, and the value stays
  until the next change.
- The SOUND TEST change (01 → 02) is not in this table.

### 2. Backup RAM

- 28 bytes of the 32,768-byte file differ.
- File offsets `0x19F`-`0x1B7`, every 4 bytes, hold the low byte of each
  setting in table order (difficulty 1 → 2, time 1 → 0, speed, short cut and
  audio 0 → 1, power gage 0 → 1).
- `0x1BC`-`0x1EF` hold the pointer `0x0601A3D0` in four places. It is also
  in the table at `0x06017AD8`.
- `0x2B0`-`0x2B3` change in a way consistent with a checksum (not tested).

### 3. The menu text (`MM.BIN`, plain ASCII, fixed-width fields)

- `0x5C9F`-`0x5E24`: the rows, each 35 bytes. There are 11 of them: the 9 on
  screen plus COMBO GAGE, which the menu does not show.
- `0x5E47`: OPTION MODE. `0x5EF6`-`0x5FAC`: the row labels again.
- `0x5FDE`-`0x6667`: the value strings: stars, OFF/ON, STEREO/MONAURAL,
  AUTO / SAVE (NON-AUTO) / LOAD (NON-AUTO), NORMAL/FULL.
- `0x61BA`-`0x65DC`: the sound-test titles (`LOC-004` already edits 18 and 22).
- `0x6676`-`0x6A36`: the BUTTON CONFIG screen. Its column header
  `0x69EE` " CHOUHATU" is romanised Japanese ("taunt"). It is the only
  non-English word seen in the session.

## Conclusion

**CONFIRMED:**
- The settings live in a table of longs at `0x06017AA0`.
- Leaving the menu writes the low bytes to backup RAM, with what looks like a
  checksum.
- The menu text is plain ASCII in `MM.BIN`, so a new row label or value
  strings are data edits.

**HYPOTHESIS, not tested:**
- The hidden COMBO GAGE row could carry a name-variant switch.
- If so, its slot would follow `0x06017AD0`.

## Uncertainty and Alternatives

- **Code hooks:** reading the value at run time and swapping the font and text
  (`EXP-0095`) needs code. That would still be the project's first SH-2 patch.
- **Unidentified values:** `0x06017AA0` was not identified. Whether the checksum
  covers the table was not tested.
- **COMBO GAGE:** what hides the row, and whether its slot exists in the table,
  were not traced.

## Reproduction

```bash
# Mednafen (agent build) on the US release image, then
./invenv.sh python -m tools.mednafen.session_recorder local/loc006/play/rec \
  --state-interval 1 --shot-interval 0.5 --keep-states 900
./invenv.sh python research/experiments/EXP-0097/stable_diff.py \
  local/loc006/play/rec/states 3000 3300 11890 12070
```
