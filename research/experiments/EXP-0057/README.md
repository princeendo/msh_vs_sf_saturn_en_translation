# EXP-0057: Which clips the game plays at character select and on the win screen

Task: LOC-005 (first blocker: confirm the name-call clips in game)
Status: IN_PROGRESS (waiting for the user to listen to the candidates)
Confidence: CONFIRMED (the clips the mixer starts in the replayed windows);
UNKNOWN (what each clip says)

## Observation

- `EXP-0056` recorded, from the user's listening, `PL0E` bank #1 (`0x04F`) as
  "Bison" and `PL0F` bank #1 (`0x048`) as "Gouki".
- The user first described the in-game line as "Vega", both at character
  select and on the win screen.
- The user's report placed the names "about 1 s after the clip started".
  Read against `shortlist.wav` instead of the full-bank catalogs, that points
  to different clips: Vega-bank #5 (`0x133`, at 1.79 s) and Gouki-bank #11
  (`0x1D1`, at 9.05 s).

## Hypothesis

If clip #1 is the name call heard in game, the mixer starts `0x04F` (or its
select-bank copy, #4) at character select or on the win screen.

## Controlled Change

None to the game. Replays of recorded states with a per-frame mixer log.

## Prediction

`0x04F` appears among the clips started in those windows.

## Inputs and Provenance

- Image: `build/ui001/image_a` (the release image). States hold the machine
  memory, and disc reads of the sound files are unchanged by the build.
- States from the `END-024` Vega + Ryu recording,
  `local/end024v/rec/states/`:
  - `f00003038`: character select, after the Vega pick (Ryu is on the
    cursor; the speed selector is open);
  - `f00008316`: the win banner;
  - `f00007963`: mid-fight.

## Tools and Environment

- `tools/audio/mixer_log.py` (new). It advances one frame at a time through
  the agent interface (patched Mednafen 1.32.1), reads the 16 mixer channel
  records, and matches each new start to a bank clip by its first 64 bytes and
  its length.
  - Sound RAM is read through the agent's `scspram` space.
  - Cart-RAM clips are read from one state saved at the end of the run.
- The agent has no controller-input command, so these windows run without
  input.

## Procedure

```bash
./invenv.sh python -m tools.audio.mixer_log "build/ui001/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" local/end024v/rec/states/f00008316.mcs local/loc005/win8316 --frames 450
./invenv.sh python -m tools.audio.mixer_log "build/ui001/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" local/end024v/rec/states/f00003038.mcs local/loc005/sel3038 --frames 900
./invenv.sh python -m tools.audio.mixer_log "build/ui001/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" local/end024v/rec/states/f00007963.mcs local/loc005/win --frames 800
```

## Actual Result

- **Win screen** (from `f00008316`, 450 frames): 116 frames after the state
  loads (emulator frame 243), channel 10 starts Vega-bank **#18 (`0x286`)**,
  which is also select-bank #48. The other starts are `CMNSE` #82 (`0x321`)
  and `MEMFIX` sounds. `0x04F` is not started.
- **Character select** (from `f00003038`, 900 frames): no new clip starts,
  because the screen waits for the speed choice. The record on the first
  frame shows that the clip just played was Vega-bank **#5 (`0x133`)** =
  select-bank #17. `0x04F` is not in any record.
- **Mid-fight** (from `f00007963`, 800 frames): without input the replay
  diverges into a continued fight (Zangief). No win plays. Only fight sounds
  start: `PL0D` (the opponent's bank) and `CMNSE`.

## Conclusion

- **Prediction not met.** The game played `0x133` at select and `0x286` on
  the win screen, not `0x04F`. Either the user's "Bison"/"Gouki" clips are
  `0x133` and `0x1D1` (the shortlist reading), or the in-game lines are other
  clips than the ones the user named.
- The `EXP-0056` name-call record is under review. The user is listening to
  single clips:
  - A: `0x04F`;
  - B: `0x133`, played at select;
  - C: `0x286`, played on the win screen;
  - D: `0x048`;
  - E: `0x1D1`, also in Mech-Gouki's bank.

## Uncertainty and Alternatives

- A recorded state preserves only the last clip each channel played. At
  select, an earlier name call could have been overwritten before
  `f00003038`.
- The win window starts at the banner. A clip that started before the banner
  is seen only as an initial record. Those records show Vega-bank #3 and #21.
- Gouki was not observed in game in this recording.

## Reproduction

The commands are listed under Procedure. The output is `starts.json` in each
`local/loc005/...` folder. The candidates the user is checking are in
`local/audio/confirm/`.
