# EXP-0087: English for the post-loss story lines

Task: TXT-002
Status: DONE
Confidence: CONFIRMED (forced trial; cold-boot play check of one record)

## Observation

- **What they are:** `MM.BIN` story records 16-41, one per roster slot,
  replace the CPU winner's win quote after a loss on a 1-in-64 roll.
- **The problem:** they exist only in Japanese, and the release showed them
  untranslated (`EXP-0085`).
- **The draft:** `data/translations/story_lines.json` has a draft English
  for every record, with the Japanese source checked by SHA-256.
- **Placeholder:** Chun-Li's record 27 keeps the winner's teammate's name
  (`{P}`).

## Hypothesis

Building records 16-41 from the draft, with `{P}` allowed at any cell, puts
every line on screen in English. The teammate's name is inserted where
`{P}` stands.

## Controlled Change

- **Generator:** `tools/text/official_endings.py --story-lines PATH`
  (`story_tables`).
  - It builds records 16-41 that have lines (25 records). Slot 19's record 35
    is symbol noise and keeps its original cells.
  - The table is marked `placeholder: anywhere`.
  - `secret_tables` now shares `translation_tables`.
- **Centring:** `official_captions.centred` and `line_pairs` accept `{P}`:
  - the name counts as two cells when centring, as `box_line` assumes;
  - the text after it starts a new cell, as the compiler splits it.
  - Lines without `{P}` are unchanged (all nine references pass).
- **References:** the release references gain
  `--story-lines data/translations/story_lines.json`.

## Prediction

Both release references rebuild deterministically. Each record shows in
English on the post-loss screen, and record 27 shows a name in place of
`{P}`.

## Actual Result

### Build

- **Specs:** Saturn names `95878ac6…`, American names `cb968668…`. The fonts
  have room for the new pairs.
- **References:** both rebaselined; nine of nine pass.

| Variant | Track 01 | xdelta | `.ssp` |
| --- | --- | --- | --- |
| Saturn names | `a1e3a0bcaafb47cd5417f71dca2e6e79e4d9f4a7afb10b7f2f5ff9e179993e2d` | 644,163 bytes, `2c6d4c9a…` | 561,626 bytes, `3df297ee…` |
| American names | `0f430c0afde618d9748b636501ab46f8a8cf48ffed73eaec3ff219799b3698cb` | 644,944 bytes, `d67f8743…` | 561,628 bytes, `e2493367…` |

- Both formats round-trip. `saturn-patcher-egui` gives both track 01 hashes.

### Saturn trial (`verify_story.sh`)

- **The checkpoint:** state `f00019422` of the `EXP-0081` play session
  (Apocalypse beats the player), with the built US image's font transplanted
  into its cart RAM (`tools/memory/mcs_patch.py`).
- **After loading, written to work RAM:**
  - the built `MM.BIN` records 16-41;
  - `0009` over the `bf` after the roll (`0x060AF228`);
  - the story base literal at `0x060AF250` moved so that slot 0 reads record
    R.
- **Result:** all 78 writes survived. Contact sheets:
  `local/txt002/verify/sheet_a.png` (`96f9b6eb…`, records 16-28) and
  `sheet_b.png` (`7d34cc56…`, records 29-41).
  - Every built record shows its English, two lines centred in the box. For
    example, record 16 (`cbdb2040…`): "Give your body to Apocalypse! / I'll
    grant power fit for a new age!".
  - Record 35 shows its original symbols (`d7960e75…`), as intended.
  - Record 27 showed "Oh? アポカリプス, didn't you see" (`07a6943b…`).
    - **Why:** the forced winner is Apocalypse, who fights alone, so the
      name inserted is slot 0's, which the release leaves in Japanese.
    - **The fix for the trial:** slot 13's (Zangief's) name entry and length
      byte were copied over slot 0's in RAM. Record 27 then read "Oh?
      ZANGIEF, didn't you see / Rogue back there just now?" (`89baac95…`).

### Cold-boot play check (2026-10-27, user at the controls)

- **Setup:**
  - US release image, track 01 `0f430c0a…` (built with `--story-lines
    --official-hints`);
  - your PS4 controller;
  - recorder `local/txt002/play2/rec`;
  - driver `tools/mednafen/continue_driver.py`. It forces the story-line
    branch and steps the hint map 0-7, one per CONTINUE?. It writes only
    `0x060AF228` and the 16-byte map.
- **Eight losses to the stage-1 CPU team** (Blackheart and Zangief):
  - **Story line:** every post-loss screen showed Blackheart's record 24 in
    English, "Now, a devil or a reaper... / which shall I introduce you to?"
    (`f00008493.png` `c0081ff0…`).
  - **Hints:** each CONTINUE? showed hints 0-7 in order, page 1 at countdown
    8 and page 2 by countdown 5. For example:
    - hint 0 `f00008731.png` `18a77987…` and `f00009019.png` `71cd2a4e…`;
    - hint 2 page 2 "for the Cross-Over / Combination move!" `027b645f…`;
    - hint 7 `f00064952.png` `d136d228…` and `f00065252.png` `1cfac482…`.
  - The driver log (`local/txt002/play2/driver.log`) records each hint's
    creation frame.
- **After Start, page 2 stays on the team screen until character select.**
  The user saw it on every continue. The US arcade does the same: MAME
  `mshvsfu`, coin and Start after page 2; its team screen still shows "Your
  partner will / assist you." (`local/txt002/play2/sheet_arcu.png`). So it is
  the arcade's own behaviour.
  - Not checked: whether the Japanese original keeps its single page there
    too. A comparison run mistimed its inputs.

## Conclusion

**CONFIRMED** (forced trial):
- The release shows the post-loss story lines in English.
- `{P}` inserts a name mid-line, and the line stays centred.

## Uncertainty and Alternatives

- **Cold boot:** only record 24 (Blackheart, the stage-1 winner) was seen
  in play. The other 24 records were seen only in the forced trial.
- **Whose name in normal play:** the winner's teammate (`EXP-0085`, arcade).
  For Chun-Li this is always a playable character with an English name,
  because bosses fight alone. Slot 0's Japanese name was reachable only
  because the trial forced Chun-Li's line onto a solo boss.
- **The text is a new translation,** not official: no English exists for
  these records.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
bash research/experiments/EXP-0087/verify_story.sh      # all 26 records
RECORDS=27 bash research/experiments/EXP-0087/verify_story.sh
```
