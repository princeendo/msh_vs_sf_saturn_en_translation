# EXP-0050: The Saturn's Names in the English Text (Mech-Gouki, Gouki)

Task: END-026
Status: DONE (2026-10-25)
Confidence: CONFIRMED (offline and live, for both changes). The naming policy
itself is provisional (`LOC-001`).

## Observation

- `EXP-0049`, credit 6: the Saturn's VS screen labels the boss "MECH-GOUKI"
  (`local/end024v/rec/shots/f00009412.png`, `14d5ba76…`).
- Vega's first ending page used the US arcade's name: "behind the Cyber
  Akuma!!".
- The user asked for:
  - "Cyber Akuma" → "Mech-Gouki" (2026-10-25);
  - then "AKUMA" → "GOUKI" wherever it appears, as a provisional decision to
    revisit (`LOC-001`, `docs/localization_plan.md`).

## Hypothesis

A text override in the spec generator changes exactly the roster lines that
name these characters. The image still fits, builds deterministically, and
shows the new names live. Only the files holding those lines, the font, and
pair codes moved by the font change.

## Controlled Change

`tools/text/official_endings.py`, applied in order:
- `TEXT_OVERRIDES = {"Cyber Akuma": "Mech-Gouki", "Akuma": "Gouki"}`, applied
  to the official English pages and dialogue lines and, with
  `--with-win-quotes`, to the win quotes before they are centred;
- `NAME_OVERRIDES` gains `15: "GOUKI"`. GOUKI and AKUMA are the same length,
  so the length byte is unchanged.

Two steps, each built and checked on its own:

| Step | Override | Build | Track 01 |
| --- | --- | --- | --- |
| 1 | "Cyber Akuma" → "Mech-Gouki" | `build/end026` | `61ced9f9…` |
| 2 | plus "Akuma" → "Gouki", and GOUKI | `build/end027` | `2a5b26b7…` |

## Census (step 2 spec, `local/end027/roster_image.json`, `04ccb452…`)

No roster line other than these names the three characters:

| Where | Before | After |
| --- | --- | --- |
| `MM.BIN` `0x7D5A4` (name, slot 15) | AKUMA | GOUKI |
| `MC0F.PAC` `0xA658` records 7 and 15 (Gouki's win quote) | "only Akuma!" | "only Gouki!" |
| `ME.PAC` `0x2F54` record 1 (Wolverine, page 2) | "Akuma! You know who I am!" | "Gouki! You know who I am!" |
| `ME.PAC` `0x3CFC` record 0 (Vega, page 1) | "behind the Cyber Akuma!!" | "behind the Mech-Gouki!!" |
| `ME.PAC` `0x3DE0` records 0-1 (Gouki, pages 1-2) | "Akuma! Don't boast of", "me! Get ready Akuma!!" | Gouki in both |
| `ME.PAC` `0x40D8` record 0 (Dan, page 1) | "made a fool of me, Akuma!" | "…, Gouki!" |

## Prediction

- Only the lines above change. Lines on the same page or in the same quote set
  may move by half a character, because the centring shifts are chosen over
  the whole set.
- Every check passes, two builds are identical, and the renders read as
  intended.
- Live: Vega's page 1 shows "Mech-Gouki". A Gouki + Ryu credit shows GOUKI
  inserted and Gouki's pages with "Gouki".

## Actual Result

### Step 1 (`build/end026`)

- **Spec diff:** Vega's page 1 line, and one half-character shift on page 2.
- **Build:** all checks true; two builds identical; 500 pair glyphs.
  - Versus the VEGA image (`e721a167…`), only `ME.PAC` (`76efa714…`),
    `MEMFIX.PAC` (`0ad5870b…`), and `MM.BIN` (`4bd76533…`) change.
  - `MM.BIN` changes because the name entries are written in pair codes,
    which the new font allocation moves.
  - The win-quote files and `MC13` are unchanged.
- **Live, from one cold boot** (`local/end026/rec`), Vega + Ryu:
  - The dialogue boxes are identical to `EXP-0049` credit 6.
  - Page 1 shows "Ha! I have the technology / behind the Mech-Gouki!!"
    (`f00005776`, `6466dc4f…`); pages 2 and 3 follow.

### Step 2 (`build/end027`)

- **Spec diff:** exactly the census lines.
  - The new win-quote text changed the shared centring shifts, so three
    other characters' win-quote lines moved by half a character: "Green or
    Gray?" (`MC03`), "Practice and you can" (`MC0C`), and "Are you feeling
    dizzy?" (`MC0D`).
- **Build:** all checks true; two builds identical; 500 pair glyphs.
  - Pair codes moved, so most win-quote PAC files differ byte-wise.
  - The renders differ only for `MC03`, `MC0C`, `MC0D`, `MC0F`, and `ME.PAC`
    `0x2F54`, `0x3DE0`, and `0x40D8`. All of them were read and are correct.
- **Regression:**
  - `m8_roster` was re-baselined: spec `04ccb452…`, track 01 `2a5b26b7…`.
  - `end010` was re-baselined: its spec changes only in the slot-15 name
    entry, AKUMA → GOUKI. Spec `776d16d2…`.
  - The previous hashes are kept under `previous`. All six references pass.
- **Live, from one cold boot of `build/end027`** (`local/end027/rec`): the user
  picked Gouki + Ryu, and the driver forced the boss (KO at frames
  13432-13609).

  | Frame | Screen | SHA-256 |
  | --- | --- | --- |
  | `f00013144` | VS screen art: "RYU / GOUKI" vs "MECH-GOUKI" | `0268cc2d…` |
  | `f00014483` | "GOUKI, / you are a great fighter." | `1e483a3d…` |
  | `f00014958` | "The fight is all we have, / RYU." | `0dcf9686…` |
  | `f00015519` | "Gouki! Don't boast of / your victory just yet..." | `43efa842…` |
  | `f00015756` | "Apocalypse transformed / me! Get ready Gouki!!" | `ac3d1db5…` |
  | `f00015992` | "Ouch. That hurt." | `ec97df0a…` |

  Composite: `local/end027/credit_gouki.png` (`b4a00091…`). GOUKI is inserted
  in 3 cells, like AKUMA.

## Conclusion

**CONFIRMED.** The text overrides change exactly the census lines. The image
fits and builds deterministically, and the Saturn's names show live: VEGA,
GOUKI, and Mech-Gouki. The VS screen shows "GOUKI" and "MECH-GOUKI", so the
English text now matches the Saturn's own art.

## Uncertainty and Alternatives

- **Provisional policy.** The decision follows the Saturn's art and voice, not
  the US arcade. Reverting means emptying the two override tables and
  rebuilding (`docs/localization_plan.md`).
- **Win quote not seen live.** "only Gouki!" is one of eight random quotes, so
  it was checked offline only.
- **Excluded slots** (0, 17, 19-25) keep their Japanese names in the name
  table. Their lines are not in scope.

## Reproduction

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --out local/end027/roster_image.json
./invenv.sh python -m tools.text.caption_compiler local/end027/roster_image.json \
  --out-dir build/end027
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --report docs/regression_report.md
```

Live: cold-boot the image, start `tools.mednafen.ending_driver`, and pick the
team (the user works the menus only).
