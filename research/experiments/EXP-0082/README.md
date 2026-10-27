# EXP-0082: Apocalypse's pre-fight exchanges in official English

Task: SPECIAL-004
Status: DONE (built; seen in play from a cold boot, Saturn-name build)
Confidence: CONFIRMED (Saturn-name build); SUPPORTED (US build, replay only)

## Observation

- In the `EXP-0081` play session, three Japanese boxes appeared at the top of
  the screen before the stage-7 fight against Apocalypse: Ryu's line and two
  of Apocalypse's (`f00014237.png`, `f00014363.png`, `f00014479.png`).
- Rendered with the quote font, `MC00.PAC`'s three "unidentified" census
  tables (`0x392E`, `0x3D7A`, `0x404E`) hold these lines, but their 76-byte
  slices start mid-sentence, so the census boundaries were wrong.

## Hypothesis

The exchanges are one fixed-size block per roster slot that equals an arcade
Japanese block, and the US arcade has an English block of the same shape, so
each Saturn box can take the English box at the same slot and position.

## Controlled Change

`tools/text/official_endings.py --boss-exchanges` adds one spec table:
`MC00.PAC` `0x3634`, 78 records, record `3·slot + box` = US arcade English box
`0x2203F4 + 300·slot + 100·box`. Nothing else in the spec changes, except that
the Saturn-name text override adds Bison → Vega (no other built text contains
"Bison").

## Prediction

Saturn block = arcade Japanese block byte for byte; every English box reads as
whole lines; the font fits; every compiler and regression check passes; in
play, the boxes before the stage-7 fight show the English.

## Inputs and Provenance

Saturn image (manifest hashes), `MC00.PAC` decoded; arcade `mshvsfu`,
`mshvsf`, `mshvsfj` (`local/arcade_roms/mshvsf/`); MAME `cps2.cpp`. Recorder
state `local/special004/play/rec/states/f00013746.mcs` (the stage map before
the stage-7 fight, saved on the previous US build `3d2a13d2…`).

## Tools and Environment

`tools/text/official_endings.py`, `tools/text/caption_compiler.py`,
`tools/regression/reference_builds.py`, `tools/disc/make_patch.py` (xdelta3
3.2.2), `tools/mednafen/replay_state.py` (patched Mednafen 1.32.1, agent
interface). Python 3.12.13.

## Procedure

1. Find every copy of Apocalypse's closing line ("見るがよい…", codes
   `0020 0020 09FC 084A 080B 0847`) in decoded `MC00`. Measure the spacing.
2. Search the arcade programs for each 76-byte Saturn box.
3. Decode the US arcade English (`tools.reference.cps2_text.decode_code`) and
   find the block with the same slot structure; check line breaks.
4. Generate both release specs with `--boss-exchanges`; rebaseline both
   release references; run all nine references; make both patches.
5. Replay the stage-map state on the new images (`replay_state`, 30-frame
   steps).

## Actual Result

- **Layout:** the closing line recurs every 228 bytes from `0x36CC` to
  `0x4D10` (gaps of 456 where a slot has its own closing line). So the block
  is 26 slots × 3 boxes × 76 bytes at `0x3634`-`0x4D5C`, right after
  Apocalypse's win quotes (`0x3174` + 16 × 76). Box 0 is the challenger's
  line, box 1 Apocalypse's reply, box 2 his closing line.
- **Arcade Japanese:** the whole block equals `0x2164B8`-`+5928` in
  `mshvsfu`, `mshvsf` and `mshvsfj`. No 32-bit pointer to it was found.
- **Arcade English:** 25-code lines with no separators, 100 bytes a box, 300
  a slot, from `0x2203F4`. All 78 boxes read as whole, centred lines.
  Slot sharing matches the Japanese: slots 0 and 1 (a Cyclops exchange,
  probably left from X-Men vs. Street Fighter), Captain America and U.S.
  Agent (own replies), Spider-Man and Armor Spider-Man. Slots 19, 20, 21 and
  22 reuse other slots' English while the Japanese has its own lines for 20
  and 22.
- **One unknown code:** the US arcade's only use of `0x011E` is in Wolverine's
  line ("I'm taking you down{011E} piece by piece!"). The code has no entry in
  the decoder's table. The arcade writes a dash as `0x012A` ("Cyclops-
  Prepare"), and the Spanish block has a comma at this point ("te estoy
  desarmando, en piezas!"), so it is drawn as a comma (`EXCHANGE_CODE_TEXT`).
  This is an inference (HYPOTHESIS), not a reading of the glyph.
- **Build:** all nine regression references pass; both patches round-trip.
  `m8_roster_gold`: spec `bb7eaa90…`, track 01 `e0395c3e…`, patch `f2fbadef…`
  (2,952,111 bytes). `m8_roster_gold_us`: spec `1de75fd8…`, track 01
  `963063de…`, patch `9cf26c3b…` (2,953,555 bytes).
- **Replay on the new US image:** from the stage-map state, the three boxes
  read "I've looked forward to / meeting you Apocalypse...", "This is the end
  of your / journey warrior..." and "Now, let only the / strong survive!"
  (`local/special004/exch_us/step15.png` `e0728ecb8ca7aa38…`, `step20.png`
  `7e7badb4888e5ae8…`, `step24.png` `900df485167c2115…`).
- **Replay on the new Saturn-name image:** Apocalypse's two boxes were
  byte-identical to the US screenshots. Ryu's box showed wrong letters
  ("fo)ard", "oaocal…pse"; `step15.png` `370b02368ff1920c…`). The wrong
  cells are pairs whose codes differ between the builds. For example, the
  Saturn-name build draws "yp" with `0x0A2B`, which is "Ap" in the US build,
  and the screen showed "Ap". So the glyphs came from the font in cart RAM,
  which the state carried over from the old US build. This is the known
  pitfall that the quote font is loaded once after boot
  (`docs/discoveries.md`, END-010). The US replay's correct letters only show
  that the old and new US builds give these pairs the same codes. Neither
  replay checks the new fonts.
- **Font reload attempt (negative):** the agent's `physical` space does not
  reach cart RAM. Reads of `0x0278CF60` did not match either font, and
  writes did not stick, so the build's font cannot be written in after
  loading a state. The agent has no input injection, so a valid check needs a
  cold boot and a short play.

- **Cold-boot play check (Saturn-name build, track 01 `e0395c3e…`):** user
  at the controls; recorder `local/special004/play2/rec`;
  `ending_driver --after-stage 1 --stage 7 --no-ko` (armed at frame 6543,
  fight started at 7980). With Gouki as lead against Apocalypse, the three
  boxes read "I will unmake you / Apocalypse!" (`f00008030.png`
  `68e3b65fccdd9c26…`), "There is evil within you / Gouki..."
  (`f00008178.png` `7fae783a4911ba65…`) and "Now, let only the / strong
  survive!" (`f00008292.png` `a2fffee5dd9d8658…`), every letter correct. The
  box shows the lead character's exchange (slot 15 here; Ryu's, slot 9, in
  the `EXP-0081` session).

## Conclusion

**CONFIRMED** for the Saturn-name build: from a cold boot, the pre-fight
boxes show the US arcade's official English, with Saturn names. The US build
uses the same table and code, but its new font has only been seen through a
replay (old font), so it stays SUPPORTED.

## Uncertainty and Alternatives

- What `0x011E` looks like on the arcade screen (a comma is the inference).
- Only Ryu's and Gouki's exchanges have been seen on screen. Slots 0-1
  (Cyclops) are probably unreachable.
- The US build has not been cold-booted to this fight.

## Reproduction

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --glyph-style credits --caption-palette gold --ui-english \
  --attract-captions --secret-roster data/text/secret_roster.json \
  --secret-translations data/translations/secret_characters.json \
  --ui-translations data/translations/continue_hints.json --boss-exchanges \
  --names us --out local/ui003/spec/m8_roster_gold_us.json
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us
./invenv.sh python -m tools.mednafen.replay_state \
  "build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/special004/play/rec/states/f00013746.mcs local/special004/exch_us --steps 30 --step-frames 30
```
