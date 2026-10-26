# EXP-0064: Cold-boot play-test of the American-name build

Task: LOC-004 and LOC-005 (verification in play)
Status: DONE
Confidence: CONFIRMED (cold boot, user input, live logs and screenshots)

## Observation

`EXP-0058`-`EXP-0063` verified the US variant's name surfaces in replays and by
cold-boot RAM reads. The acceptance criteria call for checks in play from a
cold boot.

## Hypothesis

From a cold boot of the US image, with Gouki (point) and Vega picked, the game
shows and says the US names everywhere it names those characters.

## Controlled Change

None to the build. Image `build/regression/m8_roster_gold_us/build/image_a`
(reference `m8_roster_gold_us`, track 01 `41ca8a9a…`), cold-booted.

## Prediction

- Character select calls "Akuma" and "Bison".
- The VS screen, life bars and win banner read AKUMA, BISON and CYBER-AKUMA.
- The win call is "Akuma".

## Inputs and Provenance

- The image above. The user played (2026-10-25): Arcade mode, Gouki then
  Vega.
- `tools/mednafen/ending_driver.py`, armed at boot: the first fight is the
  stage-8 boss, knocked out automatically at frame 5098.

## Tools and Environment

Patched Mednafen 1.32.1 agent with `-soundrecord`. All of the following shared
one emulator through the agent lock:
- `tools/mednafen/session_recorder.py` (screenshots every 0.5 s, states every
  3 s);
- `tools/audio/live_calls.py` (new: polls the mixer channels without pausing
  the game and flags name calls; cart clips are matched by length);
- the ending driver.

## Procedure

1. Launch Mednafen on the US CUE with `-soundrecord
   local/playtest_us/session.wav`. Start the driver, the recorder and the
   logger.
2. The user boots, selects Arcade, picks Gouki and then Vega, and chooses a
   speed. The driver jumps to and knocks out the boss.
3. Capture ran from boot to the post-boss dialogue (frames 937-6778, about
   2 minutes). Then `STOP` files ended the recorders.
4. Confirm the cart-RAM win call from the recorder state `f00005893`: the
   first 64 bytes at its start address, plus its length, against every bank.

## Actual Result

- **Name calls** (`local/playtest_us/calls/calls.jsonl`, `6806aae5…`):
  - frame 4073: `0x338` **"Akuma"** (data match, sound RAM), when Gouki is
    picked;
  - frame 4382: `0x04F` **"Bison"** (data match), when Vega is picked;
  - frame 5869: a 5,248-byte cart clip. From state `f00005893`, it is
    `pl0f_1#23` `0x338` **"Akuma"**, the win call, 97 frames before the
    banner. No "Vega", "Gouki" or "Mech Gouki" call was started.
- **Screens** (`local/playtest_us/rec/shots/`):
  - `f00004273` (`5cef5406…`): character select names Vega's portrait
    **BISON**;
  - `f00004849` (`b0216647…`): VS screen **BISON / AKUMA** vs
    **CYBER-AKUMA**;
  - `f00005220` (`ebdb22db…`): life bars **AKUMA** vs **CYBER-AKUMA** (the
    AKUMA label's 2 px clip is not visible at 1×);
  - `f00005966` (`209399fd…`): win banner **AKUMA / BISON / WIN**;
  - `f00006725` (`37188654…`): post-boss dialogue "The fight is all we have,
    **BISON**."
- **Audio:** `local/playtest_us/session.wav` (`2fec2842…`, 22.4 MB).

## Conclusion

**CONFIRMED in play from a cold boot:** the US build calls "Akuma" and
"Bison" at character select and "Akuma" on the win screen. Every name screen
reached reads AKUMA, BISON and CYBER-AKUMA. Before evidence for the Saturn
names comes from the same screens in earlier Saturn-name recordings
(`EXP-0054`, `EXP-0057`, `EXP-0062`, `EXP-0063`).

## Uncertainty and Alternatives

- Not reached in this run: the ending pages and speaker labels, which the
  RAM-write replay covered in `EXP-0060`; the sound test and the unlock
  message (`EXP-0061`, RAM only); the Mech-Gouki call; and the BISON life bar
  live (seen in an `EXP-0060` replay).
- The live logger can miss a clip shorter than its poll period (0.02 s).
  None of the name calls is that short.

## Reproduction

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" MEDNAFEN_AGENT_DIR="$PWD/local/mednafen/agent" vendor/mednafen/build-agent/src/mednafen -soundrecord "$PWD/local/playtest_us/session.wav" "$PWD/build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python -m tools.mednafen.ending_driver --log local/playtest_us/driver.log
./invenv.sh python -m tools.mednafen.session_recorder local/playtest_us/rec --shot-interval 0.5 --state-interval 3 --keep-states 120
./invenv.sh python -m tools.audio.live_calls local/playtest_us/calls
```

Run each in its own background shell, then play. `touch
local/playtest_us/rec/STOP local/playtest_us/calls/STOP` stops the recorder
and the logger.
