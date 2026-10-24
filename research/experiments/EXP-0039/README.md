# EXP-0039: Ryu's Ending Text in Work RAM

Task: END-003
Status: DONE (2026-10-24)
Confidence: CONFIRMED (the live source of box 1, box 2, and the name
placeholder). Box 3-4 and page records are SUPPORTED: they are located with
exact positions, but were not live-tested.

## Observation

`EXP-0038` showed that the ending glyphs are quote-font cells built by
`0x0601CE00` from 16-bit codes. The codes of box 1, box 2, and page 1 are known
from glyph matches and the R3 log. Where the game reads them from was unknown.
Box 1's line 2 had no contiguous match in a first search.

## Hypothesis

While the scene plays, the dialogue and page text are held in work RAM as the
same 16-bit codes, one per character. The game reads them from there.

Formed from the first search result and tested separately: a `0x0000` code in a
record is a name placeholder, filled from a name table.

## Controlled Change

| Step | Change |
| --- | --- |
| Search | None. Read only: the known code sequences in WRAM-L/H of ten checkpoints (including two mid-run states), with `?` wildcards for kanji whose codes were not yet known |
| T1 | Box 2 record cell 1, WRAM-L `0x0022AE62`: `0970` → `08F9` (full-width R, `FONT-002`) |
| T2 | Box 1 record line 2 cell 6, WRAM-L `0x0022AE46`: `0000` → `08F9` |
| T3 | Ryu's name entry, WRAM-H `0x06095FE4`: `089C 0897 0858` → `08F9 0900 08FC` (R Y U) |
| Controls | The same load and frames with no write: 540 frames for box 1, 760 frames for box 2 |

Each trial is one write into `ryu_gouki_post_boss_ko.mcs`, made before any box
is shown, using `tools/mednafen/write_trial.py`.

## Prediction

- **Search.** Each line's code sequence occurs once, inside fixed records.
- **T1.** Box 2 shows R in cell 1, and nothing else changes.
- **T2.** Line 2 shows R in cell 6 then ・・・, and the name is gone.
- **T3.** Box 1's name reads RYU, and nothing else changes.

**Refuted if:** the sequences are absent, or a write changes nothing or changes
other cells.

## Inputs and Provenance

- **Image:** untouched, track 01 `8274307f9562d2da…`.
- **Emulator:** agent build `fe0edb99f1ffe63a…`.
- **Checkpoints:** `EXP-0037` (hashes there), plus run 1 states `f00037068`,
  `f00050061`, and the bisection states `f00052456`-`f00055019`.
- **Dumps** (`mcs_extract`, `local/end003/dumps/`; WRAM extraction is validated):

  | Dump | SHA-256 |
  | --- | --- |
  | `ryu_gouki_post_boss_ko/wram_l.bin` | `7156ab0c97771d3c…` |
  | `ending_dialogue_box1/wram_l.bin` | `cac503e672897323…` |
  | `ending_page1/wram_l.bin` | `101c53e11816f9aa…` |
  | `select_after_continue/wram_l.bin` | `34df8207e21181d7…` |
  | `ending_dialogue_box1/wram_h.bin` | `dcc3c33ac7862f00…` |

## Tools and Environment

- New `tools/text/code_search.py` (test `tests/unit/test_code_search.py`):
  word-aligned big-endian code sequences with `?` wildcards; reports bus
  addresses for `wram_l`/`wram_h` dumps.
- `tools/mednafen/write_trial.py` (`EXP-0038`).

## Procedure

```bash
./invenv.sh python -m tools.text.code_search \
  "0970 080B 09F8 082A 0823 0803 0825 080E 084A 0827 082E 0829 08AE 08AE 08AE 08AE" \
  local/end003/dumps/*/wram_l.bin local/end003/dumps/*/wram_h.bin
./invenv.sh python -m tools.text.code_search \
  "09AD 0B18 082D 09F4 0B8E 080B 0C3C 084B 081E 080B 08A9" local/end003/dumps/*/wram_l.bin
./invenv.sh python -m tools.text.code_search \
  "083D 081E ? 0827 ? 0822 0825 080E 084B 08DD" local/end003/dumps/ending_page1/wram_l.bin
CUE="local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue"
S=local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $S local/end003/trial/box1_control.png --frames 540
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $S local/end003/trial/box1_placeholder_R.png \
  --frames 540 --write workraml:2AE46:08F9
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $S local/end003/trial/box2_control.png --frames 760
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $S local/end003/trial/box2_cell1_R.png \
  --frames 760 --write workraml:2AE62:08F9
./invenv.sh python -m tools.mednafen.write_trial "$CUE" $S local/end003/trial/box1_name_RYU.png \
  --frames 540 --write workramh:95FE4:08F9090008FC
```

The load-time bisection extracted WRAM-L from run 1 states between frames
50,061 and 59,979, and checked them for page 1's line 1.

## Actual Result

### Search: fixed 19 × 2 records

Every line was found once in WRAM-L, as plain big-endian codes inside 76-byte
records (two lines × 19 cells), padded with `0x0020`:

| Screen | Record (WRAM-L) | Line starts (cell) | Screen start cell (`EXP-0037` ink → (x − 28) / 16) |
| --- | --- | --- | --- |
| Box 1 | `0x0022AE14` | 5, 6 | 5, 6 |
| Box 2 | `0x0022AE60` (= box 1 + `0x4C`) | 1 | 1 |
| Box 3 | `0x0022B9F4` | 5, 5 | 5, 5 |
| Box 4 | `0x0022BA40` (= box 3 + `0x4C`) | 6, 5 | 6, 5 |
| Page 1 | `0x00233664` | 5, 3 | 5, 3 |
| Page 2 | `0x002336B0` (+ `0x4C`) | 2, 4 | 2, 4 |
| Page 3 | `0x002336FC` (+ `0x4C`) | 1 | 1 |

- **Placement.** All 13 line starts match the screen, so placement is explicit
  in the record: leading `0x0020` cells, not computed centering. This answers
  `EXP-0037`'s layout question.
- **Page 3** is 18 codes. Its "bracket gaps" were whitespace inside the 「」
  glyphs (`0x08C4`, `0x08C5`). The local transcription was corrected
  (`5718880a…`).
- **Neighbours.** The records next to these hold other characters' dialogue and
  ending text (other names, other lines). These are tables, not a single
  ending. Their extents and indexing are not established.
- **Name placeholder.** Box 1 line 2 cell 6 and box 3 line 1 cell 5 hold
  `0x0000` where the screen shows a name: Ryu's name in box 1, Gouki's in box 3.
  The glyphs after it shift right by the name's length minus one. `0x0000` also
  occurs in neighbouring records.
- **Name table.** WRAM-H holds one, from about `0x06095FC0`: 32-byte entries of
  codes with two leading `0x0020`, for example Ryu's at `0x06095FE0` (codes
  from `0x06095FE4`), then Ken's and Chun-Li's. It also shows that `0x08A8` is
  the long-vowel mark ー.
- **No other copies.** No second copy of box 2's or page 1's sequence exists in
  WRAM-L/H. The WRAM-L slot table at `0x00260E5E` (`EXP-0038`) holds slot
  numbers, not codes.

### When the tables load

| State (frame) | Tables present | Ryu name entry |
| --- | --- | --- |
| `f00037068`, `f00050061` | no | yes |
| `f00053481` (stage map after Apocalypse) | no | — |
| `f00053651` (`STAGE-08` map / VS screen) | yes | — |
| Continue, select, fight, and ending checkpoints | yes, byte-identical records | yes |

The records are identical between the post-KO and box 1 states. They arrive
during the transition into `STAGE-08`, while the team was still Ryu/Ken. Even
so, they already include Gouki's lines for the Ryu/Gouki dialogue, so the
loaded data is not chosen by the current partner.

### Live trials (inside the box, x 18-333)

| Trial | Differing px | Bounding box | Seen |
| --- | --- | --- | --- |
| T1, box 2 cell 1 → R | 119 | x 43-56, y 23-36 (cell 1) | R in place of the first kanji; the rest unchanged |
| T2, box 1 placeholder → R | 288 | x 125-212, y 39-52 (line 2, cells 6-11) | R then ・・・ at cells 7-9; no name |
| T3, Ryu's name entry → R Y U | 303 | x 125-168, y 39-52 (cells 6-8) | RYU・・・ |

- Every write read back and survived the frames.
- The glyphs uploaded correctly even though the VRAM slots were assigned before
  the write (`EXP-0038`).

Screenshots (`local/end003/trial/`):

| Screenshot | SHA-256 |
| --- | --- |
| `box1_control.png` | `9898a71ea17302a0…` |
| `box1_placeholder_R.png` | `44057cf3870fd14d…` |
| `box1_name_RYU.png` | `b87a79909751b730…` |
| `box2_control.png` | `38ea9a4ece67ca6c…` |
| `box2_cell1_R.png` | `2b25099e507bf785…` |

## Conclusion

- **CONFIRMED.** The post-boss dialogue reads 16-bit quote-font codes live from
  fixed 76-byte records (19 cells × 2 lines, `0x0020` padding, explicit
  positions) in WRAM-L. Box 1 is at `0x0022AE14` and box 2 at `0x0022AE60`.
- **CONFIRMED.** A `0x0000` code is a name placeholder, filled from a WRAM-H
  name table (Ryu's entry is at `0x06095FE4`).
- **SUPPORTED** (located with exact positions, not live-tested):
  - boxes 3-4 at `0x0022B9F4`/`0x0022BA40`;
  - the ending pages at `0x00233664` + `0x4C`·k for k = 0-2.
- The tables load with `STAGE-08`, between frames 53,481 and 53,651 of run 1.
- **For M7:** because the text is a plain code table with explicit positions,
  English can be placed by the same means as win quotes (codes, pair glyphs,
  alignment). That is a plan, not yet a result. It needs the disc source
  (`END-004`) and a capacity check.

## Uncertainty and Alternatives

- **Placeholder selection.** What chooses which name fills `0x0000` (Ryu in box
  1, Gouki in box 3)? The addressee, the other team member, or a per-record
  field are all possible. It is untested, and belongs with `END-005`.
- **Record selection.** How the game selects records (boxes 1-2 and 3-4 lie
  `0xBE0` bytes apart; the pages are elsewhere), and the table bases and
  indexing, are unknown.
- **Load addresses.** The tables could move with the team or the load order, as
  win-quote bases move with team slot (`RE-025`). Only one run was observed.
- **Disc file.** Which file loads at the `STAGE-08` transition, and whether it
  is compressed, is unknown (`END-004`).

## Reproduction

The last state without the tables, `f00053481.mcs`, is kept as
`local/end001/checkpoints/before_stage08_load.mcs` (`bed2673fb2e47201…`) for
`END-004`.


See Procedure. Everything runs from `EXP-0037` checkpoints with no gameplay.
