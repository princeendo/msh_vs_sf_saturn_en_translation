# EXP-0100: Cold-boot play check of the final American-names image

Tasks: UI-007, REF-012, TXT-005, UI-006 (release confirmation)
Status: DONE
Confidence: CONFIRMED (seen in play from a cold boot)

## Observation

- Several release changes had been seen only through forced records or RAM
  writes on saved states:
  - TAUNT (`EXP-0099`);
  - the arcade letters in hints, post-boss captions and ending pages
    (`EXP-0096`).

## Hypothesis

A cold boot of the final image shows each change in normal play.

## Inputs and Provenance

- **Image:** `build/regression/m8_roster_gold_us` (reference
  `m8_roster_gold_us` at commit `002db78`), track 01 `c6f1fbd0…`.
- **Session (2026-10-28):** the user, 1P, from a cold boot:
  - Options → BUTTON CONFIG;
  - an Arcade run with a loss and a continue, played through to the ending
    and the staff credits.
  - Recorder `local/final/play/rec`: 1,139 shots to frame 66,786.
  - `bp_log` at `060AF724`.

## Procedure and Actual Result

`pick.py` stacks the shot nearest after chosen frames. Every sheet was read.

| What | Shots | Seen |
| --- | --- | --- |
| Button config | f3011-f3131 (`sheet_bc.png` `b35c73ba…`; `f3071` `7b615f02…`) | R-BUTTON reads TAUNT on both sides; no CHOUHATU |
| Win quotes | f9527, f13741 (`sheet1.png` `7552e732…`) | "Fight for what you / believe. Now die for it!" (Akuma); "I'd never date someone / as weak as you!" (the CPU's Sakura). Arcade letters, gold |
| CONTINUE? hint | f14029 | "When Level 2 or higher, / enter ↓↘→ HP+HK" (the digit fixed by `TXT-005`) |
| Post-boss captions | f56333-f56808 | "You are worthy / RYU.", "We shall meet again / AKUMA." |
| Ryu's ending | f57165-f58336 (`sheet2.png` `fdf0da29…`; `f57165` `b2d65464…`) | "Through countless years, / Ryu's journey continues." and the next two pages |
| Staff credits, licence screen, score ranking | f59039-f66734 | unchanged, as expected |

The user reported nothing wrong. The announcer's name calls were heard by
the user only; there is no recording of them.

## Conclusion

**CONFIRMED** in play from a cold boot: TAUNT, the arcade letters in win
quotes, the hint, the post-boss captions and the ending pages, and the
fixed digit, all in the final American-names image.

## Uncertainty and Alternatives

- **Not run:** the Saturn-names image. It differs only in the name
  surfaces checked in `EXP-0064`/`EXP-0074`.
- **Not reached:** the Cyber Akuma call.

## Reproduction

```bash
# Mednafen (agent build) on the image above, recorder and bp_log as EXP-0094, then
./invenv.sh python research/experiments/EXP-0100/pick.py local/final/sheet2.png 57100 57700 58300
```
