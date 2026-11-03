# EXP-0113: The NAMES switch in play, on the release image (OPT-005)

Task: OPT-005
Status: DONE
Confidence: CONFIRMED (the user's session: "Everything looked good!", and
RAM from 204 recorded states); the ending sites are not reached

## Observation

`EXP-0112` switched the 26 resident sites on a cold boot. The 6 sites in the
character slots (MC00 exchanges, MC0F win quotes) and the 10 in the ending's
`ME.PAC` area need gameplay, and what the switch looks and sounds like needs
a player.

## Hypothesis

On the release image, with NAMES SATURN, the VS screen, life bars, banners,
announcer, Vega's quotes and the stage-7 exchanges use the Saturn names, and
NAMES AMERICAN brings the American ones back.

## Controlled Change

None beyond the release image: `m8_roster_gold_us` with `--options-submenu
--names-switch`, spec `edf1f16a…`, track 01 `6669eb94…`.

## Procedure

- **Session:** the user, 2026-11-02, followed the OPT-005 step table in
  Mednafen with their own settings:
  - NAMES SATURN;
  - the title menu (MECH-GOUKI NOW!!);
  - Arcade with Vega and Gouki, to stage 7;
  - NAMES AMERICAN and another fight.
- **Recording:** `local/opt005/play/rec`, 204 states (frames 199-59,404),
  a screenshot every second.
- **Timeline:** for each state, WRAM-H and WRAM-L were extracted, and the
  release image's site table (from its `MEMFIX.PAC` tail) was compared:
  resident sites at their addresses, slot sites in all four slots, ME sites
  at `0x001FFFF0` + offset. Sound RAM is not in the states; `EXP-0112`
  covered it.

## Actual Result

| From state | NAMES | Resident (20 in WRAM-H) | Slot sites | ME sites |
| --- | --- | --- | --- | --- |
| f2596 | 0 | 20 American | none loaded | none |
| f3478 | 1 | 20 Saturn | none loaded | none |
| f4948 | 1 | 20 Saturn | 2 Saturn (MC0F, Vega's quotes) | none |
| f44559 | 1 | 20 Saturn | 6 Saturn (plus MC00, stage 7) | none |
| f53890 | 0 | 20 American | 2 American (MC0F) | none |

- No site ever held the other variant while its file was loaded.
- No ending was reached, so ME never loaded.
- **The user:** "Everything looked good!"

## Conclusion

**CONFIRMED:** on the release image, the NAMES switch changes every name
site that the session loaded:
- the resident `MM.BIN` text and pointers;
- the announcer calls (`EXP-0112`; the user heard nothing wrong);
- Vega's win quotes in a fight slot;
- the stage-7 exchanges.

It switches both ways, and the user saw and heard the right names.

## Uncertainty and Alternatives

- **The ending's 10 `ME.PAC` sites** (7 records, 3 speaker labels) were not
  loaded. They use the same routine at a fixed address
  (`0x001FFFF0` + offset, from the `sp004` credits states).
- **NAMES across a reset:** `0x06017AB4` is inside the `0x80`-byte save
  block (`EXP-0105`). Saving it was confirmed for BOSS FIGHT and COMBO
  GAUGE (`EXP-0110`) but not run for NAMES (SUPPORTED).

## Reproduction

```bash
# the release image: tools.regression.reference_builds --only m8_roster_gold_us
# the timeline: research/experiments/EXP-0112/switch_watch.site_table on its
#   MEMFIX.PAC, compared with each recorded state's extracted WRAM
```
