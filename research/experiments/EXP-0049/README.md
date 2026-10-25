# EXP-0049: Live Sample of the Combined Roster Image

Task: END-024
Status: DONE (2026-10-25)
Confidence: CONFIRMED for the five sampled endings on the `c06cf0ef…` image,
and for the Vega ending and a win quote on the VEGA image (`e721a167…`).

## Observation

`EXP-0048` built the combined roster image `build/end023` (track 01
`c06cf0ef…`) and reviewed it offline. Only Ryu's ending had been seen live
(`EXP-0044`, `EXP-0045`).

## Hypothesis

From one cold boot of the combined image, every sampled roster ending shows:
- the arcade's two English partner lines, with the right characters' English
  names inserted;
- the character's official English pages.

The sample covers the longest name, a name longer than its Japanese, the
longest and shortest page counts, slot 18, and Marvel and Capcom partners.

## Controlled Change

None to the image. Live play of `build/end023/image_a`, with:
- the user working the menus;
- `tools/mednafen/ending_driver.py` holding the stage word at stage 8 and
  zeroing the boss vitality (`EXP-0042` offsets);
- `session_recorder.py` (a screenshot each second, a state every 6 s;
  `local/end024/rec`).

| Credit | Point + partner | Checks |
| --- | --- | --- |
| 1 | Captain America + Ryu | Longest name (8 cells); 6 pages |
| 2 | Zangief + Spider-Man | 6-page Capcom ending; Marvel partner |
| 3 | Bison + Hulk | Name longer than the Japanese (2 → 3 cells) |
| 4 | Sakura + Wolverine | 2 pages |
| 5 | Dan + Chun-Li | Slot 18 |

## Prediction

For each credit:
- block 1 = the partner's line (record p), with the point character's English
  name;
- block 2 = the point character's reply (record 26 + point), with the
  partner's name;
- then that character's official English pages, in order.

## Actual Result

Each credit showed two dialogue blocks of about 420-490 frames, then the pages.
Every frame was segmented by box content, and one frame per block or page was
read (composites in `local/end024/credit*.png`).

| Credit | Block 1 | Block 2 | Pages | Composite |
| --- | --- | --- | --- | --- |
| 1 | "CAPTAIN AMERICA, / you are a great fighter." | "We make a good team / RYU." | 6, official English, in order | `331a1e82…` |
| 2 | "We've done it, / ZANGIEF." | "I say Good-bye to you, / SPIDER-MAN." | 6 | `cff5c7d6…` |
| 3 | "Wasn't that fun, / BISON?" | "Our game is at its end, / HULK." | 3 | `0d0d6b5b…` |
| 4 | "Ya did good, / SAKURA." | "On to better challenges, / WOLVERINE." | 2 | `13af06a2…` |
| 5 | "Ha ha ha! We did it, / DAN!" | "See Ya / CHUN-LI." | 5 (the last is an empty box) | `8311ce2f…` |

- **All predictions met.** The names are inserted at their English lengths:
  CAPTAIN AMERICA in 8 cells, and BISON grown from 2 to 3.
- **Speaker labels** above the page boxes (for example "Mother", "Vega",
  "Captain America") are original artwork.
- **Dan's last page:** an "END" picture with an empty box.
  - In `mshvsfj` the box holds the single kanji 完 ("The End"). In `mshvsfu`
    it is empty: the arcade English record is blank. The same holds for
    Norimaro (excluded).
  - Checked by the no-play MAME route (`--point dan`): the build reproduces the
    official English exactly.
- **Centring:** CAPTAIN AMERICA's line sits right of centre, because lines are
  centred for a two-cell name. It is still inside the box.

### Failed approach (recorded so it is not retried)

- A `--warmup-ko` driver option tried to win the ordinary first fight (to show
  a win quote) by zeroing `0x060F3E50`/`0x060F4844`. In a two-against-two fight
  those words do not hold the opponent's vitality; they did only in the
  one-character boss fight.
- Credit 1's first attempt lost stage 1. A manual test also zeroed
  `0x060F3E5A`, and the user's team then lost at once (`ko_test.png`
  `9c7c65aa…`). That word is probably a player-side vitality.
- The option was removed. The opponent's vitality in ordinary fights is
  unknown.

### VEGA (user decision during the session)

- The user noted that the Saturn calls the dictator **Vega** (art labels,
  character select, voice). Changing the art and audio to Bison was rejected
  as out of proportion and a sourcing question.
- `official_endings.py` gains `NAME_OVERRIDES = {14: "VEGA"}`. "Bison" appears
  in no page, win quote, or dialogue line in scope, so only the name entry
  changes. VEGA is 2 cells, like the Japanese name, so the length is unchanged.
- **Rebuild** `build/end024_vega`, track 01 `e721a16798832147…`:
  - two builds identical; all checks true;
  - only `MEMFIX.PAC` and `MM.BIN` differ from `c06cf0ef…`;
  - `MC13`, `ME.PAC`, and the win-quote files are unchanged.
- **`m8_roster` re-baselined** (previous: `c06cf0ef…`); all six references
  pass.
### VEGA image, live (credit 6)

- **Session:** one cold boot of `build/end024_vega/image_a` (the font changed),
  with the recorder (`local/end024v/rec`).
- **Win-quote spot check.** The user picked Vega + Ryu (Manual + Turbo) and won
  stage 1 by playing. The win-quote screen showed the official English "You
  were foolish / to challenge me!" (`MC0E.PAC` record 7 in the spec).
  Screenshot `f00008932` `3b8a6763…`.
- **Ending.** The driver was armed only after the win (frame 9093). The boss
  fight started at frame 9613, and the driver stopped writing at frame 9786.
  Then:

  | Frames | Box |
  | --- | --- |
  | 10632-11115 | "VEGA, / you are a great fighter." (`46e269bf…`) |
  | 11167-11607 | "Our game is at its end, / RYU." (`c409ebf0…`) |
  | 11668-11847 | "Ha! I have the technology / behind the Cyber Akuma!!" |
  | 11909-12156 | "Go forth! Show the world / Shadaloo's true power!!" |
  | 12208-12634 | "Yes, boss." |

  Composite: `local/end024v/credit6.png` (`f136a0e4…`).
- **Result:** VEGA is inserted in 2 cells, and the pages are unchanged from
  credit 3, as predicted.

## Conclusion

**CONFIRMED.** The combined image shows official English endings with correct
names, including the longest name, a grown name, and the VEGA override. The M5
win quotes still work in it.

## Uncertainty and Alternatives

- **Twelve roster endings were checked offline only.** The pipeline and the
  record identity are the same as for the six live ones.
- **One win quote was seen live** in the combined image. The other win-quote
  files are byte-identical to the live-verified roster image.

## Reproduction

Cold-boot the image; then, per credit:
- the user goes to character select;
- run `./invenv.sh python -m tools.mednafen.ending_driver --log …`;
- the user picks the team and presses nothing more.

For a win quote, start the driver only after the user has won the first fight.
Segment frames by box content and read one frame per block or page.
