# EXP-0093: An opt-in build flag for grammar fixes to official hints

Task: TXT-004
Status: DONE
Confidence: CONFIRMED (both variants build; every corrected page seen on the
Saturn by forced trial)

## Observation

- The user finds some official English hard to read (2026-10-27), starting
  with CONTINUE? hint 0: "When Air Combo starts to / move hits the opponent, /
  put the lever ↑ to chase / him and execute a combo!".
- The release builds the 16 official hint pages with `--official-hints`
  (`EXP-0086`).

## Hypothesis

A flag can replace chosen official pages with corrected lines, while:
- the release default stays official;
- every corrected line still fits its box;
- the font still fits.

## Controlled Change

- **New `data/translations/grammar_fixes.json`:** five corrected pages.
  - Each names the official page it replaces by the SHA-256 of the page's
    decoded lines joined with a newline, so the official text is not copied.
  - Each gives a reason.
- **`tools/text/official_endings.py`:**
  - `--fix-grammar PATH` (needs `--official-hints`);
  - `grammar_fixes()`;
  - `official_hint_table(..., fixes=)`, which refuses a page whose hash
    differs;
  - the spec gains `"grammar_fixes": true`.

  Tests are in `tests/unit/test_official_endings.py`.

| Page (hint) | Corrected lines | Reason (short) |
| --- | --- | --- |
| 0 (0) | "When an Air Combo starter / hits the opponent," | "starts to move" garbles "starting move" |
| 1 (0) | "push the lever ↑ to chase / them and execute a combo!" | "push the lever"; the opponent may be anyone |
| 4 (2) | "At Level 2 or higher, / enter ↓↘→ HP+HK" | "When Level 2" has no subject |
| 8 (4) | "Press HP+HK together for / the Cross-Over Attack!" | no verb; capitalised as on page 5 |
| 12 (6) | "←↙↓ P before landing / for a safe fall!" | article |

The other eleven pages are unchanged. The wording is a draft for the user's
review.

## Prediction

- With the flag, each spec differs from the release spec only in the
  corrected lines and the flag field.
- Both variants build.
- The corrected pages show on the Saturn.

## Inputs and Provenance

- Release options as in `EXP-0091`, plus `--fix-grammar
  data/translations/grammar_fixes.json`.
- Arcade `mshvsfu.zip`, driver `a8c09ef8…`.
- Source image `references/mshvsf/saturn_jp/README.md`.

## Procedure

1. `bash local/txt004/gen.sh local/txt004/spec`: the `EXP-0091` generator
   command with the flag added.
2. `diff` each spec against the release spec (`local/ui003/spec/`).
3. `bash research/experiments/EXP-0093/verify_grammar.sh`:
   - builds the American-names image with `caption_compiler`
     (`build/txt004`);
   - forces hints 0, 2, 4 and 6 on the `EXP-0086` play state;
   - screenshots page 1 at frame 850 and page 2 at frame 1,180.
4. The Saturn-names image was built the same way (`build/txt004_saturn`).

## Actual Result

- **Specs** (with the flag):

  | Variant | Spec | Track 01 |
  | --- | --- | --- |
  | Saturn names | `1fde4bf114e6210078ef5bf6d2deaa7f0e57e4fe054324464179c75eb51a09f7` | `99067ff4f45ee9504f6b822450a5a6c4b6b9cdcbc1b112d5ecb4349890e3e3f4` |
  | American names | `4dd19378180d73fba841e228eb6e8673eb28c63a6794a5cc8367745432372e36` | `a47d2ba8bc667614a96913d72d8fcf099a3cb1547f91f52989775c4417ed371e` |

  Each differs from the release spec (`EXP-0091`) in the eight corrected
  lines and the `grammar_fixes` field only.
- **Font:** both images built, so the font still fits.
- **On the Saturn** (American names; contact sheet
  `local/txt004/verify/sheet.png`):

  | Hint | Page 1 (`f850`) | Page 2 (`f1180`) |
  | --- | --- | --- |
  | 0 | "When an Air Combo starter / hits the opponent," `03d73570…` | "push the lever ↑ to chase / them and execute a combo!" `a464cdeb…` |
  | 2 | "At Level 2 or higher, / enter ↓↘→ HP+HK" `1fbb8bac…` | unchanged, `aa5deb00…` as in `EXP-0086` |
  | 4 | "Press HP+HK together for / the Cross-Over Attack!" `d77f7f17…` | unchanged, `ebfb5014…` |
  | 6 | "←↙↓ P before landing / for a safe fall!" `0f6a5c2e…` | unchanged ("Outsmart your opponent!"), `3f379430…` |

### Other official English (reviewed, not changed)

Every distinct built record was read: 405, from win quotes, dialogue,
endings and `MM.BIN`. Candidates for the same treatment, for the user to
decide:

- **Win quotes:**
  - typos: "mediate" for "meditate" (Dhalsim); "lose it's appeal"; "this
    worlds riches"; "the X-men";
  - missing commas: "stand a chance fool", "Perish you insignificant", "Rest
    easy soldier";
  - "Break, burn, freeze...." has four dots;
  - "With discipline comes / the rewards" should be "come".
- **Partner lines:**
  - missing commas: "That was easy right...", "Your reign of madness / ends
    here Apocalypse!";
  - "See Ya" should be "See ya".
- **Endings:**
  - "I'm glad to see / you're safe. Tiger!" should be "safe, Tiger!";
  - missing commas: "Welcome home Zangief.", "Welcome back brother!", "than
    before my son.", "How about it Ryu?", "Good luck then Ryu.";
  - "Our home made borshch" should be "homemade";
  - "for safe keeping" should be "safekeeping";
  - "he's our...!!" starts a sentence, so "He's".

## Conclusion

**CONFIRMED:**
- `--fix-grammar` builds both variants and changes only the corrected
  lines;
- every corrected page shows on the Saturn;
- the release default is unchanged, because the flag is off and no
  reference uses it.

## Uncertainty and Alternatives

- **Wording:** the corrections are drafts and need the user's review.
- **No regression reference:** none was added for the flag; the spec and
  track hashes above document it. A reference could be added if the user
  adopts the fixes.
- **Saturn names on screen:** that image was built, but its pages were not
  shown. Its hint records are the same text.

## Reproduction

```bash
COMMON="--driver local/mame_src/cps2.cpp --archive local/arcade_roms/mshvsf/mshvsfu.zip \
  --roster data/text/m5_roster.json --with-win-quotes --glyph-style credits --caption-palette gold \
  --ui-english --attract-captions --secret-roster data/text/secret_roster.json \
  --secret-translations data/translations/secret_characters.json \
  --story-lines data/translations/story_lines.json --official-hints \
  --fix-grammar data/translations/grammar_fixes.json --boss-exchanges"
./invenv.sh python -m tools.text.official_endings $COMMON --names us --out local/txt004/spec/m8_roster_gold_us.json
./invenv.sh python -m tools.text.official_endings $COMMON --out local/txt004/spec/m8_roster_gold.json
bash research/experiments/EXP-0093/verify_grammar.sh
```
