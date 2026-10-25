# EXP-0053: English-Only UI Labels (Player-2 Prompt and the EASY Mode Label)

Tasks: UI-001, UI-002
Status: DONE (2026-10-25)
Confidence:
- **CONFIRMED:** the sources of both labels, and the EASY fix (live, from a
  cold boot).
- **CONFIRMED by replay:** the "JOIN IN" fix, on a state with the new font
  transplanted.
- **UNKNOWN:** when the player-2 alternation appears.

## Observation

The user reported two labels that alternate English with Japanese:
- the top-right player-2 prompt ("PRESS START" / Japanese);
- the mode panel's "EASY" (Japanese alternating).

## Hypothesis

Both are drawn from quote-font UI art cells. They can be made English-only by
copying the game's own English art into the Japanese cells. That is a font
change only: no code, and no new art.

## Findings

### Sources

Sprites were listed with `tools/memory/vdp1_commands.py --font`, on
frame-by-frame captures.

- **Player-2 prompt:** in bank `0x7000` at y = 1, it alternates three phases:
  - "PRESS START": seven art cells, `0x480`-`0x486`, from x = 224;
  - blank;
  - "対戦者求む!" ("Challenger wanted!"): five cells, `0x45B`-`0x45F`, from
    x = 256 (`local/ui001/w2`, from state `font011 f00006227`).
- **Mode panel:** the right button alternates:
  - "簡単操作" ("simple controls"): four cells, `0x428`-`0x42B`, at x 62-110;
  - "EASY": two cells, `0x6A8`-`0x6A9`, at x 78-94.

  Captured live in `local/ui002/burst`. "簡単操作" has four shading copies
  (`0x424`, `0x428`, `0x42C`, `0x43A`), matched one to one by pixel values
  with four "EASY" copies (`0x6A6`, `0x6A8`, `0x6AA`, `0x6AC`).
- **English art in the font.** The quote font holds the arcade's English UI
  art:
  - "PRESS START", "FREE PLAY", "INSERT COIN", "JOIN IN" (`0x496`-`0x499`,
    clean cell boundaries), "GAME OVER", "NO CHALLENGERS", "CONTINUE",
    "PLEASE WAIT";
  - an italic "CHALLENGER";
  - life-bar name art in both conventions: "VEGA"/"BISON", "GOUKI"/"AKUMA",
    "MECH-GOUKI"/"CYBER-AKUMA" (relevant to `LOC-002`).
- **US arcade oracle** (`local/end006/mame/mshvsfu`): with no credits, the P2
  corner shows "INSERT COIN". The Saturn has no coins, and its second phase is
  "対戦者求む!".
- **When the alternation appears.** "対戦者求む!" appeared in only one of six
  recorded sessions: the silver session, from its stage-1 win onwards. The
  condition is unknown.

### Fix (user choices)

`official_endings --ui-english` adds a spec map `glyph_copies` (target to
source code, or null for empty). The compiler (`pair_font.build`) applies it
before packing, never sacrifices copy targets, and verifies each target
against its source (`copies_equal_sources`).

| Label | Cells | New content |
| --- | --- | --- |
| P2 prompt "対戦者求む!" | `0x45B`-`0x45F` | blank, then "JOIN IN" (`0x496`-`0x499`), right-aligned; the user chose "JOIN IN" over blank or "CHALLENGER" |
| "簡単操作", four shading copies | `0x424`-`0x427`, `0x428`-`0x42B`, `0x42C`-`0x42F`, `0x43A`-`0x43D` | blank, EASY, EASY, blank (the matching EASY copy) |

## Build

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --glyph-style credits --caption-palette gold --ui-english \
  --out local/ui001/spec/roster_gold_ui.json
./invenv.sh python -m tools.text.caption_compiler local/ui001/spec/roster_gold_ui.json \
  --out-dir build/ui001
```

- **Result:** spec `7ce7820a…`; track 01 `7a3917d1…`.
  - Every check is true, including `copies_equal_sources`.
  - 84 bytes of zero fill.
- **Regression:** `m8_roster_gold` now includes `--ui-english` and was
  re-baselined; 8 of 8 pass.
- **Release:** the patch was regenerated: 158,333 bytes, `7e7d7118…`.

## Results

- **EASY, live** (cold boot of `build/ui001`): over a 6-second capture
  (`local/ui001/burst_easy`, 100 frames), the button shows "EASY" in every
  frame (`easy_live.png`, `beb44d5f…`). Before the fix, it switched about
  every 0.6 s.
- **JOIN IN, live:** not seen. The alternation did not occur in this session
  (stage-1 win captured for 9 s: only "PRESS START" and blank).
- **JOIN IN, by replay:**
  1. The silver-session state `f00006227` shows the alternation.
  2. A copy of it had its cart-RAM font replaced by the new build's font
     entry.
  3. The state's original cart-RAM font equalled the silver build's font byte
     for byte. That validates cart-RAM extraction for this region (cart
     `0x0278CF60`, `0x32740` bytes).
  4. The replay on `build/ui001` shows "JOIN IN" in the alternate phase
     (`w3/s0001`, `a537ffca…`; zoom `f178a9d9…`).

## Uncertainty

- When the player-2 alternation appears is unknown.
- Any other screen that uses the replaced cells now shows the English art.
  None was found by shape search; `0x45B`-`0x45F` have no duplicates.
- The state transplant was a one-off test script. Edited states are local
  test artefacts, not evidence of a cold-boot path.
