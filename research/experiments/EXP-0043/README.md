# EXP-0043: What Selects the Post-Boss Dialogue and the Ending

Task: END-005
Status: DONE (2026-10-24)
Confidence: CONFIRMED (partner-only Saturn run; indexing model predicted and
met on two further arcade teams). The KO character's effect is untested.

## Observation

- **`EXP-0037`:** Ryu (point) + Gouki on the untouched Saturn image showed
  four dialogue boxes and Ryu's three pages.
- **`EXP-0041` Part 2:** Ryu + Ken on marker image C (uncontrolled) showed:
  - the same pages;
  - the same box 4;
  - box 3 the same, apart from the inserted name;
  - boxes 1-2 different.
- **`EXP-0042`:** the arcade English partner lines are indexed by partner slot
  and by 26 + point slot.

## Hypothesis

**H1 (pre-registered in `EXP-0037`):** the post-boss dialogue depends on the
partner, while the ending pages depend only on the point character.

**H2 (formed after the Saturn run, then tested by prediction).** `MC13`'s
120-record table is 16 Cyber-Akuma win quotes plus 52 two-record dialogue
entries:
- boxes 1-2 are records 16 + 2 × (partner slot): the partner speaks, and
  `0x0000` names the point character;
- boxes 3-4 are records 16 + 2 × (26 + point slot): the point speaks, and
  `0x0000` names the partner.

This parallels the English one-record partner lines.

## Controlled Change

| Run | Image or set | Team (point + partner) | Changed vs `EXP-0037` |
| --- | --- | --- | --- |
| Saturn | Untouched image, from `select_after_continue.mcs` (`50fc3951…`) | Ryu + Ken | The partner only |
| Arcade A | `mshvsfj`, `mshvsfu` (forced-stage route, `EXP-0042`) | Ryu + Chun-Li | The partner (H2 prediction) |
| Arcade B | `mshvsfj`, `mshvsfu` | Gouki + Captain America | Both, with the order reversed (H2 prediction; the planned partner was Ryu, see Deviations) |

## Prediction

- **Saturn (H1).** Ending pages 1-3 are pixel-identical in the text box to
  `EXP-0037`, and the dialogue differs.
- **H2, Ryu + Chun-Li (slot 11):**
  - Japanese boxes 1-2 are `MC13` records 38-39, and boxes 3-4 are records
    86-87;
  - English: record 11, then record 35.
- **H2, Gouki (slot 15) + Captain America (slot 2):**
  - Japanese boxes 1-2 are records 20-21, and boxes 3-4 are records 98-99;
  - English: record 2, then record 41;
  - the pages are Gouki's ending, not Ryu's.

## Inputs and Provenance

- **Saturn:** untouched image (track 01 `8274307f…`); agent build
  `fe0edb99…`; `session_recorder.py` → `local/end005/rec`.
- **Arcade:** sets and driver as in `EXP-0042`; MAME 0.289;
  `tools/reference/arcade_ending_route.py`.
  - New `--point` option, and the partner presets `chunli` and
    `captain_america` (the latter observed with point Gouki).
  - Timelines: Chun-Li `74ff8f4d…`, Gouki + Captain America `c0292c5c…`.
- **`MC13`:** decoded `9eb9b7c6…`, with its table at `0xA06C` (`EXP-0034`).

## Tools and Environment

- `tools/text/glyph_match.py`: Saturn on-screen codes.
- `tools/text/code_search.py`: finds the records in `MC13`.
- `tools/reference/arcade_ending_route.py`.
- `tools/common/png.py`: text-box diffs (x 20-331; dialogue y 20-59, page y
  180-219).

## Procedure

1. Saturn: the agent loaded `select_after_continue.mcs` on the untouched image
   and started the recorder.
   - Attempt 1: Ryu + Ken lost to Mech-Gouki, so the agent restored the state.
   - Attempt 2: Ryu + Ken won, with Ryu landing the KO; Ken never tagged in.
2. Text-box diffs of every screenshot from frame 14,500 to 17,400 against:
   - the `EXP-0037` Ryu/Gouki boxes and pages;
   - the `EXP-0041` image-C Ryu/Ken boxes.
3. Glyph-match states taken during boxes 1-4 (`f00014759`, `f00015101`,
   `f00015272`, `f00015446`). Search `MC13` for the codes.
4. Arcade runs:

   ```bash
   ./invenv.sh python -m tools.reference.arcade_ending_route --partner chunli --end 12600
   ./invenv.sh python -m tools.reference.arcade_ending_route --point gouki --partner captain_america --end 13000
   ```

   Each was run with the MAME command of `EXP-0042`, on `mshvsfj` and
   `mshvsfu`.

## Actual Result

### Saturn, Ryu + Ken (untouched): H1 confirmed

- **Continue.** Both attempts went from select to `STAGE-08` against
  Mech-Gouki. These are two more observations that a continue keeps the boss
  stage (`EXP-0037`).
- **Text-box diffs:**

  | Screen | vs `EXP-0037` Ryu/Gouki | vs `EXP-0041` image-C Ryu/Ken |
  | --- | --- | --- |
  | Pages 1-3 | 0 px each | — |
  | Box 4 | 0 px | 0 px |
  | Box 3 | 298 px, the name cells only | 0 px |
  | Boxes 1-2 | No match (different lines) | 0 px |

  - The page screenshots are byte-identical to `EXP-0037`'s (`d24d4863…`,
    `8697d315…`, `312498fe…`).
  - Box screenshots: `f00014728` `6f33c2d2…`, `f00015016` `bd4098c7…`,
    `f00015251` `65f2eb70…`, `f00015477` `7943769c…`.
- **Records.** All 62 glyph cells of boxes 1-4 matched quote-font codes.
  - Boxes 1-2 are `MC13` records 36-37 (decoded `0xAB1C`/`0xAB68`). Box 1
    line 2 holds `0x0000` at cell 7, shown as the point character's name.
  - Boxes 3-4 are records 86-87, the same records as Ryu/Gouki's boxes 3-4.

### Arcade: H2 predictions met

- **Ryu + Chun-Li.**
  - `mshvsfj`: boxes 1-2 read as records 38-39, with the point's name at the
    placeholder (`f08070` `4f1cb309…`, `f08370` `797c06b6…`). Then boxes 3-4
    with "Chun-Li" at the placeholder, then Ryu's three pages.
  - `mshvsfu`: "Ha ha ha! We did it, RYU!" (record 11, `f08070` `e2dab657…`),
    then "We shall meet again CHUN-LI." (record 35), then the English pages.
- **Gouki + Captain America.**
  - `mshvsfj`: boxes 1-2 read as records 20-21, with Gouki's name at the
    placeholder (`f07920` `a9b5026b…`). Boxes 3-4 read as records 98-99, with
    Captain America's name at the placeholder.
  - `mshvsfu`: "Good job, AKUMA." (record 2, `f07920` `d27bb019…`), then "The
    fight is all we have, CAPTAIN AMERICA." (record 41, `f08100` `4403d9d3…`).
  - Both sets: then a different ending, Gouki's, followed by the credits.

### Summary of the model

| Team | Boxes 1-2 (partner speaks) | Boxes 3-4 (point speaks) | English | Pages |
| --- | --- | --- | --- | --- |
| Ryu + Gouki (`EXP-0037`) | 46-47 = 16 + 2·15 | 86-87 = 16 + 2·(26 + 9) | 15, 35 | Ryu's |
| Ryu + Ken | 36-37 = 16 + 2·10 | 86-87 | 10, 35 | Ryu's |
| Ryu + Chun-Li | 38-39 = 16 + 2·11 | 86-87 | 11, 35 | Ryu's |
| Gouki + Captain America | 20-21 = 16 + 2·2 | 98-99 = 16 + 2·(26 + 15) | 2, 41 | Gouki's |

## Conclusion

- **H1 CONFIRMED.** On the untouched Saturn image, changing only the partner
  leaves Ryu's ending pages pixel-identical and changes the dialogue. The pages
  follow the point character (also shown by Gouki's point run in the arcade).
- **H2 CONFIRMED.** The dialogue is two record pairs. The partner's pair is
  chosen by the partner's slot, and the point's pair by 26 + the point's slot.
  In each pair, `0x0000` names the other character. The English partner lines
  use the same indices, one record each.
  - The formula was formed from two Saturn teams. It then predicted two further
    arcade teams exactly. The arcade Japanese records are byte-identical to
    `MC13`'s (`EXP-0042`).
- **For `END-010` (Ryu point):**
  - Ryu's own pair (records 86-87) is shared by every partner.
  - Each partner's pair (16 + 2·p) changes.
  - The English mapping is direct:
    - English record p → partner pair 16 + 2·p;
    - record 26 + 9 → Ryu's pair 86-87.
  - How one English line fills a two-box pair is the open design question.

## Deviations

- The planned order-swap run (Gouki + Ryu) picked Captain America as partner,
  because the cursor path observed with point Ryu does not hold for point
  Gouki. It was kept as an H2 test with new slots for both roles, and the
  preset was renamed `captain_america`.
- The KO character was not varied. In the Saturn run Ryu landed the KO, and
  the forced-vitality arcade KO happens with the point character. The KO
  character's effect stays open (`docs/known_unknowns.md`).

## Uncertainty and Alternatives

- Records 54/55 and 106/107 (the pairs of slots 19 and 26 + 19, Cyber-Akuma)
  do not match the arcade block (`EXP-0042`). They are presumably unused,
  because Cyber-Akuma cannot be a team member here. That is not tested.
- Secret and special characters (`SPECIAL-001`) were not tested.
- The arcade forced-vitality route gives a "PERFECT" KO. The dialogue and pages
  matched the Saturn's natural wins for the shared teams, so the route does not
  appear to change selection.

## Reproduction

See Procedure. Checkpoint: `local/end001/checkpoints/ryu_ken_post_boss_ko.mcs`
(`18995e6d449c114a…`, untouched image, Ryu/Ken at the KO) replays the Ryu/Ken
dialogue and pages with no input.
