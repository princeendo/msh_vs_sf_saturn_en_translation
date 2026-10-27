# EXP-0090: The arcade win-quote fonts by region, and their Saturn copies

Task: REF-012
Status: DONE
Confidence: CONFIRMED (one shared glyph set; code ranges and pitch by region;
the Saturn font holds the same glyphs; digit codes); HYPOTHESIS (why the
pitch differs)

## Observation

- The user saw the US/EU arcade draw win quotes in a different font from the
  Japanese set (`REF-012`).
- `EXP-0051` found the US caption font close in style to the Saturn credits
  font, but narrower, and did not locate its glyph data.

## Hypothesis

The US and Japanese sets draw win quotes from different tiles. The task
allows three outcomes: same tiles, different tiles, or different code ranges.

## Controlled Change

None to game data. In MAME, only screenshots and memory reads, plus write
taps on the quote pointer and index (`EXP-0031`) for one capture. On the
Saturn, one forced trial wrote one dialogue record in work RAM.

## Prediction

If the fonts differ by tiles, the two sets load different graphics ROMs or
draw from disjoint tile ranges with different code-to-tile rules.

## Inputs and Provenance

- **MAME:** 0.289 (Homebrew), pinned driver `local/mame_src/cps2.cpp`
  (`a8c09ef8…`), sets `mshvsfu` and `mshvsfj` from
  `local/arcade_roms/mshvsf/` (`references/mshvsf/arcade/README.md`),
  default EEPROM in `local/mame_arcade/nvram`.
- **Saturn:** source image `references/mshvsf/saturn_jp/README.md` (track 01
  read only); checkpoint `local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs`
  (`f42218550c0fb23c…`, made from the source image, `EXP-0039`).

## Tools and Environment

- `tools/reference/mame_timeline.lua` gains a `share <tag> <path>` verb. It
  dumps a MAME memory share such as `:cps_a_regs`, because the CPS-A
  registers are write-only and read back as 0 through the program space.
- New `tools/reference/cps2_gfx.py`:
  - rebuilds the `gfx` region from a zip (`ROM_LOAD64_WORD`);
  - unshuffles it in 2 MiB banks, as MAME's `cps2_gfx_decode` does;
  - renders 16 × 16 tiles to a PNG.

  Tests: `tests/unit/test_cps2_gfx.py`.
- Existing: `tools/text/font.py` (Saturn quote font), `tools/mednafen/write_trial`.

## Procedure

1. **Reach a win quote with no play.**
   - The timeline does two coins, Start, and Button 1 twice.
   - The vitality words `0xFF3E50`/`0xFF4844` are forced to 0 from frame 5,600
     to 7,800.
   - In stage 1 that KOs the player, so the CPU team's quote shows: in
     `mshvsfu`, Spider-Man's at frame 10,260; in `mshvsfj`, Blackheart's at
     10,800.
   - Two runs of each gave byte-identical frames.
2. **Dump at the quote frame:**
   - program space `0x900000-0x92FFFF` (VRAM) and `0x700000-0x70FFFF`
     (object RAM);
   - the shares `:cps_a_regs`, `:cps_b_regs` and `:output`.
3. **Read the layers** from the CPS-A bases (both sets: scroll1 `0x908000`,
   scroll2 `0x90C000`, scroll3 `0x910000`), then the object list.
4. **Render tiles** with `cps2_gfx`, and compare them with the Saturn quote
   font (`MEMFIX.PAC` entry 4, `FONT-001`) by code.
5. **Saturn trial.**
   - Box 4's record (WRAM-L `0x0022BA40`, `EXP-0089`) was replaced with
     arcade text codes: "I need to refill my" / "Narrow ABC abc 0123".
   - The checkpoint's own original font was used.
6. **Digit check in the arcade.**
   - From frame 9,900, the quote pointer `0xFF9E4A` was forced to
     `0x0021DC80` (slot 22 block) and the index `0xFF9E66` to 1.
   - That quote holds code `0x0138`.

## Actual Result

### One glyph set, two code ranges

- **Same graphics ROMs:** all eight `gfx` ROMs (`mvs.13m`-`mvs.20m`) have the
  same names and CRCs in `mshvsfu`, `mshvsfj` and the parent `mshvsf`.
  Tile data cannot differ by region.
- **Win quotes are sprites:**
  - scroll1 is empty;
  - scroll2 and scroll3 hold the same backgrounds in both sets;
  - the text is single-tile objects in the second object bank (`0x708000`),
    palette attribute `0x001E`.
- **Tile = `0x15000` + text code in both sets:**
  - each object's code word is `0x5000` + the text code, and y bit 13 adds
    `0x10000` (MAME: `code + ((y & 0x6000) << 3)`);
  - the US line "I need to refill my web-" is objects `5148 5020 516E …`,
    the codes found in `mshvsfu`'s program at `0x21B570` (and three other
    places);
  - the Japanese line's objects `5A33 5809 583D …` are the text codes at
    `0x20EBE8` in `mshvsfj`.

| | US (`mshvsfu`) | Japanese (`mshvsfj`) |
| --- | --- | --- |
| Text codes | `0x0120`-`0x01FF` (Latin) | `0x03FA`-`0x0B3A` seen (kana, kanji) |
| Tiles | `0x15120`-`0x151FF` | `0x153FA`-`0x15B3A` seen |
| Glyph | 8 px wide, gold gradient, slant | 16 × 16, white |
| Pitch | 12 px (x `0x068`, `0x074`, …) | 16 px (x `0x06A`, `0x07A`, …) |
| Cells per line | 25 (x `0x068`-`0x188`) | 19 (x `0x06A`-`0x18A`) |

- **So the "different font" is a different code range** of one shared glyph
  set, drawn at a different pitch. Screens:
  - US `mshvsfu_f10260.png` (`a8eb00cf…`);
  - Japanese `mshvsfj_f10800.png` (`83d091fb…`).
- **The narrow Latin block, tiles `0x15100`-`0x151FF`** (`latin_15100.png`
  `07dd0e9d…`), holds:
  - ASCII punctuation, digits, A-Z and a-z;
  - accented Latin-1 letters at `0x190`-`0x1DF`;
  - arrows, ©, ®.

  Every A-Z, a-z and digit glyph fits in columns 0-7 of its cell.
- **Tiles `0x15200`-`0x153FF`** (`jp_15200.png` `523da74a…`) hold:
  - a wide gold slanted Latin font at codes `0x200`-`0x25F`: digits at
    `0x200`, A at `0x210`, a at `0x231`. These are the codes of the Saturn
    credits font (`EXP-0051`);
  - large title letters and logos;
  - kanji from `0x3F8`.

### The Saturn quote font holds the same glyphs

Compared by code, with arcade tile `0x15000 + c` against Saturn glyph `c`:

- **Same shape:**
  - every code in `0x100`-`0x18F` (one empty in both) and `0x1E0`-`0x1FF`;
  - `0x200`-`0x259`, `0x25B`-`0x25F` and `0x2B0`-`0x2FF`;
  - `0x800`-`0xBFF` except `0x8BF`.
- **Pens:** Saturn pen = arcade pen + 1 throughout `0x120`-`0x18F` (11
  distinct pens). The Saturn's transparent pen is 0, the arcade's is 15.
- **Differ:** `0x190`-`0x1DF` (the arcade's accented letters), `0x25A`,
  `0x260`-`0x2AF` and `0x8BF`.

So the narrow US quote font is already on the Saturn disc, at the arcade's
own codes.

### The Saturn draws it at 16 px pitch

- **Trial result** (`narrow_f1100.png` `3ca333d0…`): the box shows the narrow
  glyphs, one per 16-pixel cell, with gaps: "I need to refill my" over
  "Narrow ABC abc )012".
- **Capacity:** a line holds 19 letters this way. Official English lines run
  to 25 characters, which is why the arcade uses 12 px.
- **Why the pitch differs is not known (HYPOTHESIS):** the arcade may choose
  it by language or by code, and the Saturn may draw every code at 16.

### Digits are ASCII + `0x100`

- **The Saturn trial:** codes `0x12F`-`0x132` showed ")012".
- **The arcade:** the forced slot-22 quote reads "I beat more people /
  before 8 am..." (`mshvsfu_f10230.png` `8a957884…`), with code `0x0138`.
- **So the digit base is `0x0130`:**
  - `EXP-0078`'s reading ("Level 3" = `0x0132`, base `0x012F`) is
    DISPROVEN;
  - the CONTINUE? hint reads "When Level 2 or higher," and the quote reads
    "before 8 am...".
- **The release builds** encode "Level 3" and "9 am" from the wrong base:
  `m8_roster_gold` spec lines 2380, 2436 and 4713. That is a text error,
  fixed under its own task.

## Conclusion

- **CONFIRMED:** the regions share one glyph set. The US/EU sets draw win
  quotes from the narrow Latin code range (`0x120`-`0x1DF`) at 12 px, and
  the Japanese set from kana and kanji codes at 16 px.
- **CONFIRMED:** the Saturn quote font contains the same narrow Latin glyphs
  at the same codes, and draws them at 16 px.
- **CONFIRMED:** arcade digits are ASCII + `0x100`.

### Saturn fit, as a user decision (nothing adopted)

1. **Keep the credits-font pairs (current release).**
   - They are gold, squeezed two per cell, and 38 letters a line.
2. **Pairs from the narrow arcade glyphs.**
   - Two 8-pixel glyphs fill one cell exactly, with no squeezing, so the
     letters keep their arcade shapes. The pitch is 8 px against the
     arcade's 12, so the letters touch.
   - Same capacity and pipeline as now; only the glyph source changes.
   - No new provenance question: the glyphs are already in the Saturn
     font.
   - Not rendered or tested yet.
3. **One glyph per cell at a 12-pixel pitch.**
   - This would match the arcade exactly, at 25 letters a line.
   - It needs an SH-2 code patch to the Saturn's text pitch, which has not
     been found. That would be the project's first such patch (as for
     `LOC-006`).
   - Many official lines would still need checking against 25 cells.

## Uncertainty and Alternatives

- **The EU set was not run.** `mshvsf` (Europe) loads the same graphics ROMs
  and shares the English blocks checked in `EXP-0078`. Its pitch was not
  observed.
- **The pitch rule** (by set, by language word or by code) was not traced in
  either program.
- **Capture coverage:** only the quote box was examined. Other text, such as
  hints and endings, likely uses the same routine but was not dumped.

## Reproduction

```bash
# Win-quote frame, both sets (timelines in local/ref012/<set>/; frames 10260 / 10800)
MAME_TIMELINE=local/ref012/mshvsfu/timeline_share.txt mame mshvsfu \
  -rompath local/arcade_roms/mshvsf -video none -sound none -nothrottle -skip_gameinfo -nomouse \
  -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram \
  -snapshot_directory local/ref012/mshvsfu/snap3 -homepath local/mame_arcade \
  -autoboot_script tools/reference/mame_timeline.lua
#   timeline: 3200/3230 Coin 1, 3320 Start, 4300/4360 Button 1,
#   5600 force16 0xFF3E50/0xFF4844 0, 7800 unforce, then dump/share at the quote frame
./invenv.sh python -m tools.reference.cps2_gfx --driver local/mame_src/cps2.cpp --set mshvsfu \
  --first 0x15100 --count 256 --out local/ref012/latin_15100.png local/arcade_roms/mshvsf/mshvsfu.zip
# Saturn trial (record = arcade codes of the two lines, big-endian, 38 cells)
./invenv.sh python -m tools.mednafen.write_trial \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs local/ref012/saturn/narrow.png \
  --frames 1500 --shot-at 900 --shot-at 1100 --shot-at 1300 \
  --write workraml:2BA40:$(cat local/ref012/saturn/narrow.hex)
# Arcade digit check: add to the mshvsfu timeline
#   9900 force16 0xFF9E4A 0x0021 ; 9900 force16 0xFF9E4C 0xDC80 ; 9900 force16 0xFF9E66 0x0001
```
