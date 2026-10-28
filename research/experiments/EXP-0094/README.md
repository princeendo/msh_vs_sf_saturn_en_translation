# EXP-0094: What selects the win-quote task slot; the language word on a real quote

Task: RE-049 (and the `REF-012` follow-up lead)
Status: DONE (this experiment); RE-049 stays open
Confidence: CONFIRMED (the slot follows the pool layout; side and match number
are each not sufficient); DISPROVEN (setting the language word gives a
12-pixel quote); UNKNOWN (what the extra task is)

## Observation

- `EXP-0036`: the quote routine (`060AF724`) ran with r12 = `0x060F9E16` for
  Cyclops and `0x060F9ED6` for Zangief, Captain America and Dhalsim. All four
  were user KOs.
- The candidates (`docs/known_unknowns.md`): the winning side, the match
  number, or the team's state after a lost round.
- The routine is translated 68000 code. r12 is the running task, a 0xC0-byte
  slot in a pool (`…9A56, 9B16, …, 9E16, 9ED6`).

## Hypothesis

The win scene creates its tasks from the top of the pool down, and the quote
task takes the highest free slot. It gets `9E16` when another task still
holds `9ED6`, and `9ED6` otherwise.

## Inputs and Provenance

- **Image:** US release image as built at commit `2bd969c`
  (`build/regression/m8_roster_gold_us/build/image_a`, track 01 `0c3f72bb…`).
- **Session (2026-10-27):** the user on 1P with the PS4 controller.
  - Arcade, Ryu and Ken. The user won stage 1, then lost stage 2 on
    purpose.
  - Recorder `local/re049/play/rec`: 83 states, kept 600.
  - `bp_log --kind pc --range 060AF724-060AF725`.

## Procedure and Actual Result

### 1. The session (pc log of `060AF724`, from the agent's `events.log`)

| Frame | r12 | r0 (record pointer) | What |
| --- | --- | --- | --- |
| 8,009 | `0x060F9E16` | `0x00209458` (`0x002091AC` + 76 × 9) | the user's KO |
| 13,272 | `0x060F9ED6` | `0x00229BF0` | the CPU's KO |
| 13,576, 13,959 | `0x060F9A56` | `0x060952E4`, `0x06095330` (hint records 8, 9) | CONTINUE? hint pages |

So the hints run through the same routine, in another slot.

### 2. The pool around each quote (WRAM-H from recorder states)

- **Just after each quote** (f8151 and f13318), the scene's tasks match by
  their script pointers at +`0x34`. In the CPU's scene each sits one slot
  higher:

  | Task (+`0x34`) | User win | CPU win |
  | --- | --- | --- |
  | `0607FD24` | `9B16` | `9BD6` |
  | two `0607FBxx` tasks | `9BD6`, `9C96` | `9C96`, `9D56` |
  | `0607FD0C` | `9D56` | `9E16` |
  | quote (table + index) | `9E16` (`0x002091AC`, 9) | `9ED6` (`0x00229B58`, 2) |
  | other | `9ED6`: flag 1, `…00FF`, no +`0x34` | — |

- **Write log of the slots' first longs** (`alloc_log.py`, write breakpoints in
  log mode, f7809 → +260 frames and f12972 → +360 frames):
  - in the user's win, code at `0605F964` ran as the task at `9ED6`
    (`R12` = `9ED6`) throughout the scene setup;
  - in the CPU's win it did not run. Otherwise the same allocators
    (`06047AC0`, `06047BB6`, `06047CC6`, the pool clear at `060490E8`) wrote in
    the same order.

### 3. Trials through the agent (`slot_trial.py`)

| Trial | State | Change | r12 at `060AF724` |
| --- | --- | --- | --- |
| A | f7980 (user win) | none | `9E16` (pointer `0x00209458`, as in play) |
| B | f7980 | slot `9ED6` zeroed | no quote; the game dropped to the BIOS CD player (`B_stuck.png` `f66605a4…`) |
| C | f13145 (CPU win) | none | `9ED6` (pointer `0x00229BF0`) |
| D | f13145 | f7980's `9ED6` task copied into slot `9ED6` | `9ED6` |

- **B** removed a live task the game needs, so it tests nothing.
- **D** is inconclusive: f13145 is before the scene starts (the whole pool
  is empty), and the scene clears the pool first (`060490E8`).

### 4. The language word on a real quote (`lang_trial.py`)

From f7980:
- **Control:** at +240 frames, Ryu/Ken's quote "To live is to fight, to /
  fight is to live!" with the `RE-048` descenders (`control_f240.png`
  `c12f71cb…`).
- **`0x060F4C90` = 1, and both words = 1:** the game dropped to the BIOS
  CD player (`lang4C90_f240.png` and `lang_both_f240.png`, both
  `e34e0d6a…`).

## Conclusion

- **CONFIRMED:**
  - which slot the quote gets follows the pool layout when the win scene
    starts: the scene's tasks shift up one slot when slot `9ED6` is free;
  - the winning side alone does not decide it (`EXP-0036` had user KOs in
    both slots);
  - the match number alone does not decide it either. `EXP-0036`'s second
    session got `9ED6` on its first KO, while this session got `9E16` on its
    first.
- **UNKNOWN:** what the task at `9ED6` (code `0605F964`) is, and when it
  survives into the win scene. A guess, not tested: a lingering effect from
  the KO, which would vary with how the KO happened.
- **DISPROVEN:** setting the language word yields a 12-pixel English quote.
  The game crashes, so the arcade-English path is not usable by a flag alone
  (the `REF-012` lead).
- The tools already handle both slots (`ko_capture.py`, `verify_records.py`),
  so nothing needs fixing.

## Uncertainty and Alternatives

- **Unclear `EXP-0036` sessions:** I am reading its two sessions as
  separate boots.
- **Untested candidate:** "team state after a lost round" was not tested
  directly. MSHvSF matches are single-round as played here.

## Addendum: the extra task across all six quotes

- **`EXP-0036`'s quote-time states** (`local/mednafen/agent/runs/re046-*/quote.mc`):
  - for Cyclops, a task with type word `0x00FF` (+`0x0C`) held `9ED6`, and
    the quote was in `9E16`;
  - for Zangief, Captain America and Dhalsim, no such task existed, and the
    quote was in `9ED6`.

  With this session's two quotes, the rule fits all six.
- **The task in this session** (f7980): type `0x00FF`, a pointer to
  `0x060F3800` at +`0x54` (a character object; vitality `0x060F3E50` lies
  inside it), and `0x00205EC4` at +`0x66` (WRAM-L). It first appears between
  f7809 and f7980.
- **Screenshots:**
  - that window (`ko_window.png` `5a657c98…`): K.O., the win banner, the
    VITAL/TIME/BONUS tally, then Ryu's sprite over the title logo;
  - before the CPU's quote (`cpu_window.png` `52121d3b…`): K.O., the win
    banner, then Chun-Li's sprite on black, with no tally and no logo.
- **HYPOTHESIS:** it is part of the winner-sprite screen in the scene with
  the logo, still alive when the quote scene sets up. Why the four
  `EXP-0036` user wins differ (Cyclops with it, three without) is not known.
  The screen's length or timing may vary by character.

## Reproduction

```bash
# Play: Mednafen (agent build) on the US image, then
./invenv.sh python -m tools.mednafen.session_recorder local/re049/play/rec --keep-states 600
./invenv.sh python -m tools.mednafen.bp_log local/re049/play/bp --kind pc --range 060AF724-060AF725
# Trials, with Mednafen (agent build) running:
./invenv.sh python research/experiments/EXP-0094/slot_trial.py
./invenv.sh python research/experiments/EXP-0094/alloc_log.py
./invenv.sh python research/experiments/EXP-0094/lang_trial.py
```
