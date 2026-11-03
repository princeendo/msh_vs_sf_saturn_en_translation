# EXP-0115: All four switches in play, on the release image (OPT-006)

Task: OPT-006 (with OPT-004, OPT-005)
Status: DONE
Confidence: CONFIRMED (the user: "Nothing was out of the ordinary.", and
RAM from 117 recorded states); the ending sites are not reached

## Observation

`EXP-0114` checked GRAMMAR FIXES and the new saved slot on a cold boot and a
checkpoint. The acceptance criteria need play, a reset with the settings
kept, and the Mech-Gouki unlock left alone.

## Controlled Change

None beyond the release image: `m8_roster_gold_us` with `--options-submenu
--names-switch --grammar-switch`, spec `204b624e…`, track 01 `3812bdc1…`.

## Procedure

- **Session:** the user, 2026-11-02, followed the OPT-006 step table:
  - NAMES SATURN and GRAMMAR FIXES ON, then an F10 reset;
  - EXTRA OPTIONS again;
  - Arcade fights;
  - GRAMMAR FIXES OFF and more fights.
- **Recording:** `local/opt006/play/rec`, 117 states (frames 207-34,098).
- **Timeline:** in each state, the saved slot `0x06017ADC`, the Mech-Gouki
  unlock `0x06017AB4`, and each setting's sites (resident, the four slots,
  ME) were compared with the release image's site table.

## Actual Result

| State | `0x06017ADC` | `0x06017AB4` | NAMES sites | GRAMMAR sites |
| --- | --- | --- | --- | --- |
| f2889 | `4E530000` | 0 | 20 resident American | 5 resident official |
| f3769 | `4E530001` | 0 | 20 Saturn | 5 official |
| f4063 | `4E530003` | 0 | 20 Saturn | 5 fixed |
| f4652-f6125 | (the reset; boot data) | | | |
| f6714 | `4E530003` (from the save) | 0 | 20 Saturn | 5 fixed |
| f7886 | `4E530003` | 0 | 20 Saturn | 5 fixed, 6 slot fixed |
| f24781 | `4E530001` | 0 | 20 Saturn | 5 official |
| f27115 | `4E530001` | 0 | 20 Saturn, 2 slot Saturn (MC0F) | 5 official, 4 slot official |

- **No other writes:** no site held the other setting's variant while its
  file was loaded. `0x06017AB4` stayed 0 throughout.
- **No ending:** ME never loaded.
- **The user:** "Nothing was out of the ordinary."

## Conclusion

**CONFIRMED:**
- both switches change their own sites independently, both ways, in play;
- they survive a reset through BACK UP (AUTO) and the marked slot
  `0x06017ADC`;
- the game's Mech-Gouki unlock is untouched.

## Uncertainty and Alternatives

- **The ending's `ME.PAC` sites** (names and fixes) were never loaded in
  any session.
- **Real hardware:** not yet tested (the user's disc).

## Reproduction

The timeline script follows `EXP-0113`'s, with the site table read by
`research/experiments/EXP-0112/switch_watch.site_table(memfix, 12288, 4)`.
