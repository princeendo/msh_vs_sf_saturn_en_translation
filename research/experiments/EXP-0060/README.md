# EXP-0060: US life-bar names and speaker labels for the American-name variant

Task: LOC-004 (first part: art and labels already on the disc)
Status: DONE (this part; the VS screen and win banner remain)
Confidence: CONFIRMED (the HUD draws the copied cells; the speaker field
drives the label); not yet seen in play for AKUMA

## Observation

- `EXP-0054`: the life-bar names are quote-font cells, and the font holds the
  US art too. The speaker labels are 16-character ASCII fields in `ME.PAC`
  `0xB164`, indexed by character; "Akuma" (37) and "Bison" (38) are already
  in the table.
- `EXP-0059` built the US variant with US text and voice, but Japanese art.

## Hypothesis

Copying the US label cells over the cells the HUD draws, and setting speaker
fields 14, 15 and 19 to the US names, makes the life bars and speaker labels
show the US names, with no code change.

## Controlled Change

`official_endings --names us` adds:

| Change | Targets | Sources / new data |
| --- | --- | --- |
| glyph copies (quote font) | VEGA `0x760`-`0x762` | BISON `0x763`-`0x765` |
| | GOUKI `0x750`-`0x752` | AKUMA `0x753`-`0x755` |
| | MECH-GOUKI `0x568`-`0x56D` | CYBER-AKUMA `0x5D9`-`0x5DE` |
| `ME.PAC` patches (16 bytes each, with expect) | field 14 `0xB244` "Vega" | "Bison" |
| | field 15 `0xB254` "Gouki" | "Akuma" |
| | field 19 `0xB294` "Mech-Gouki" | "Cyber Akuma" |

`--names saturn` is unchanged: its spec is still `7ce7820a…`.

## Prediction

- In a fight with Vega and Mech-Gouki, the life bars read BISON and
  CYBER-AKUMA.
- An ending page whose speaker is field 14 reads "Bison".

## Inputs and Provenance

- Glyph-call logs (agent `bp pc 0601CE00`, R3 = code):
  - `local/loc002/pc_glyph` (EXP-0054, Vega vs Mech-Gouki);
  - `end027` `f00013440` (Gouki + Ryu, the stage map before a fight; the
    game caches the next fight's labels);
  - `font011` `f00003062` (the VS screen build-up, 450 frames).
- Replays on `build/loc004_us/image_a` (and the regression image):
  - `end024v` `f00009368`, with the US font transplanted into its cart RAM;
  - `end026` `f00005456` / `f00005806` (Vega ending, speaker "Vega").

## Tools and Environment

- `official_endings` / `caption_compiler` (the existing `glyph_copies` and
  `patches` with expect).
- Patched Mednafen 1.32.1 agent; scratch scripts for glyph logs, font
  transplant, RAM poke and screenshots.

## Procedure

1. Map the label cells:
   - render `0x740`-`0x7FF` and `0x560`-`0x5DF` with a cell grid, and print
     the cell edges;
   - take from glyph logs which cells the game draws: VEGA `0x760`-`0x762`,
     GOUKI `0x750`-`0x752`, MECH-GOUKI `0x568`-`0x56D`, plus life-bar pieces
     (`0x561`, `0x5D1`, `0x5DF`, `0x744`/`0x745`).
2. Check widths:
   - BISON fits 3 cells (the `EXP-0054` trial);
   - CYBER-AKUMA (`0x5D9`+4 to `0x5DE`+15) fits 6 cells;
   - AKUMA starts at column 0 and ends 2 px into `0x756`, so 2 px of its
     last A's foot are clipped.
3. Build the US spec, compile, re-baseline `m8_roster_gold_us`, run all
   references, and remake the patch.
4. Life bars: transplant the US font into a copy of `end024v` `f00009368`,
   replay 450 frames into the fight, screenshot and zoom.
5. Speaker label: load `end026` `f00005456`, write "Bison" into the
   `ME.PAC` table copy in WRAM-L (`0x0023B234`, field 14), run 380 frames to
   the page, screenshot. Repeat without the write as a control.
6. Look for other uses of the label art: log glyph calls through the VS
   screen build-up from `font011` `f00003062`.

## Actual Result

- **Build:**
  - The US spec is `781f70ee…`. Every compiler check is true. `ME.PAC`: 48
    patched bytes, 20 changed, all within the three fields.
  - All 9 references pass. `m8_roster_gold_us` track 01 is `49e002df…` (was
    `e1337dbf…`).
  - Patch `0e055dbc…`, 155,520 bytes, with a passing round trip.
- **Life bars** (`local/loc004/zoom_vega.png`): P1 reads **BISON** and P2
  reads **CYBER-AKUMA**.
- **Labels before and after** (offline render from both builds' fonts,
  `local/loc004/labels_before_after.png`): VEGA→BISON, GOUKI→AKUMA (last
  2 px clipped), MECH-GOUKI→CYBER-AKUMA.
- **Speaker:**
  - With the write, the page label reads **"Bison"**
    (`speaker_after2.png`). Without it, "Vega".
  - Writing at `f00005806` (page already shown) did not change it: the label
    is drawn when the page opens.
- **VS screen:** no quote-font label codes are drawn. Its names are the
  sprite mosaic (`EXP-0054`). The italic label set and the first MECH-GOUKI
  copy (`0x562`-`0x567`) were not seen drawn anywhere, so they are left
  unchanged.

## Conclusion

- **CONFIRMED:** the cells the fight HUD draws now hold the US art. The
  BISON and CYBER-AKUMA life bars are seen in a replay. The `ME.PAC` speaker
  field drives the ending speaker label. The US variant shows US names in
  its life bars and speaker labels.
- **Limitation:** AKUMA is 2 px wider than GOUKI's 3-cell sprite. The fix
  needs the sprite width (its table was not found) or redrawn art.

## Uncertainty and Alternatives

- The AKUMA life bar was not seen live: the replay's Gouki team never tags in
  without input. Its cells are confirmed by the glyph cache; the art by the
  offline render.
- The speaker test wrote the RAM copy. The built image's `ME.PAC` carries the
  same bytes (the compiler checks them), but it was not loaded from disc in a
  replay.
- Uses of the italic set and the first MECH-GOUKI copy are unknown. If a
  screen uses them, it still shows the Japanese names.
- **Procedural error, corrected:** a background glyph scan ran a second
  Mednafen on the same agent directory while replays ran. The scan results
  and replays from that window (`scan_all.log`, early `shots_gouki`,
  `shots_dlg`, `shots_page`) are discarded. The checks above were rerun with
  one emulator.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold_us
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.json
```

The replays used scratch agent scripts:
- font transplant: replace cart RAM `0x0278CF60`, `0x32740` bytes, in a
  copy of the state;
- RAM write and screenshot: the steps above.

Evidence images are in `local/loc004/`: `zoom_vega.png`,
`labels_before_after.png`, `speaker_before2.png`, `speaker_after2.png`.
