# EXP-0054: Inventory and Scope of the Name Art and Voice (Vega/Gouki/Mech-Gouki)

Task: LOC-002
Status: IN_PROGRESS (2026-10-25). Inventory done; voice identification and
the VS-screen art source are left.
Confidence:
- **CONFIRMED:** life-bar, speaker-label, menu, and sound-test sources; US art
  present on the disc; the life-bar swap (by replay).
- **SUPPORTED:** the win-banner mechanism.
- **UNKNOWN:** the VS-screen art source and the voice.

## Observation

`LOC-001` asks for both name conventions. The user noted that the voice says
"Vega", and asked whether PS1 assets would be easier to transfer than arcade
assets.

## Method

- **Replays:** states from earlier recordings (`end024v` `f00009368`
  VS/fight, `f00008316` win, `end026` `f00005806` page) replayed on
  `build/ui001`, with screenshots and VDP1 dumps (`local/loc002`).
- **Font matching:** sprites matched to quote-font codes with
  `tools/memory/vdp1_commands.py`.
- **Searches:** ASCII and 16-bit code searches over every disc file (raw and
  LZSS).
- **Feasibility trial:** BISON's life-bar cells (`0x763`-`0x765`) copied over
  VEGA's (`0x760`-`0x762`) in a test font, transplanted into the cart RAM of a
  copy of `f00009368` (method from `EXP-0053`), then replayed into the fight.

## Results

- **Life bars:**
  - Label cells in the quote font, in two styles: bold `0x740`-`0x7AF` and
    italic `0x7B0`-`0x7FF`.
  - Both sets hold GOUKI and AKUMA, and VEGA and BISON. MECH-GOUKI is at
    `0x568` and CYBER-AKUMA near `0x5C0`.
  - Rendering: `local/loc002/name_rows.png` (`269cc2b6…`).
  - **Trial:** the life bar shows BISON (`bison_lifebar.png`, `7be3bdf7…`;
    frame `3647e292…`).
- **Win banner:**
  - Large 2×2 letter glyphs (`0x2E0`-`0x35F`; for example V = `0x32E`, E =
    `0x2EC`, G = `0x300`, A = `0x2E4`, each with a lower half at +`0x10`).
  - So the name is spelled from letters.
  - The source string table is not located: no ASCII "VEGA" next to the other
    names, and no code-string match.
- **Ending speaker labels:**
  - Small ASCII glyphs (V `0x56`, e `0x65`, g `0x67`, a `0x61`).
  - The source is `ME.PAC` `0xB164`: 16-character ASCII fields (also in
    `ME.SHX`). It holds Vega, Gouki, Mech-Gouki, …, Akuma, and Bison.
- **Menus:** `MM.BIN` `0x24EC0`: "PRESS START BUTTON", "ARCADE MODE",
  "VERSUS MODE", "SURVIVAL MODE", "MECH-GOUKI NOW!!", "OPTION MODE".
- **Sound test:** `MM.BIN` `0x61BA`, a list of 20-character fields:
  "18.VEGA", "22.GOUKI", and others.
- **VS screen:**
  - Names are part of the VS sprite mosaic (banks `0x50xx`-`0x51xx`), not
    quote-font codes. The screenshot composite is `screens.png`
    (`f2c9dbce…`).
  - The name-row tiles are in no file raw or as LZSS. The only matches were
    a near-blank tile everywhere and backdrop tiles in `BG*.PAC`.
  - Likely source: `SEL.PAC`, `SEL2.PAC`, or `SELCMP.PAC` (unknown archive
    layouts).
- **Selector:**
  - The code choosing JP or US labels is not found. The labels are drawn
    through the generic glyph cache (caller `0x0601CDE2`, code in R3).
  - Static searches for label code tables found only coincidental matches.
- **Audio:**
  - `.ADP` files (71, 41.9 MB) are music streams: `M01_OPEN`, `M02_SELE`,
    `M04_VS`, `M05_WIxx`, and others.
  - Candidates for voices: `CMNSE.PAC` (common sound effects) and `PLxx.PAC`
    (per character). The layouts are not decoded.
  - Which clip says "Vega" needs listening.

## Conclusion

- Most US-name surfaces need **no imported assets**. The art (life bars) or
  text (speaker labels; menu and sound-test text; win-banner letters) is
  already on the Saturn disc.
- Only the VS-screen names (if no US version exists in `SEL*.PAC`) and the
  voice may need outside assets. The PS1 is the recommended first source to
  check (`docs/localization_plan.md`).

## Next Experiments

1. **Voice:** the user identifies where "Vega" is spoken (character select,
   VS screen, win, or announcer). Then trace the sound command at that moment
   (an SCSP or sound-driver write log) to the sample.
2. **VS screen:** log the SCU DMA source of the VS name tiles at VS-screen
   load (as in `EXP-0051`) to find the RAM buffer, then the file.
3. **Selector:** trace how the life-bar object picks its label cells, which
   could give a single switch.
4. **Win banner:** trace the letter-code source at banner creation.

## Uncertainty

- The trial used a font transplanted into a state, not a cold boot.
- Character select and other screens were not checked for names.
