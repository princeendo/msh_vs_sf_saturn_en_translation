# EXP-0042: Arcade Reference for Ryu's Ending and Post-Boss Dialogue

Task: END-006
Status: DONE (2026-10-24)
Confidence:
- CONFIRMED: the arcade Japanese records equal the Saturn's; the English ending
  pages exist and were seen on screen; the English post-boss dialogue is a
  different two-line scene.
- SUPPORTED: the English partner-line indexing (one prediction met).

## Observation

`EXP-0037` to `EXP-0041` established Ryu's ending on the Saturn:
- a post-boss dialogue (`MC13.PAC`; Ryu/Gouki boxes 1-4);
- three ending pages (`ME.PAC`);
- all as 19 × 2 quote-font code records.

The arcade is the primary translation oracle (`GATE-TRANSLATION`). Its ending
text was unexamined.

## Hypothesis

The arcade sets hold the same Japanese ending records, and the US/EU sets show
official English for the same scenes. The arcade text format was not assumed to
be the Saturn's (rule 14); only byte comparisons and screens count.

A second hypothesis, formed to reach the ending without play: the arcade keeps
the stage index and the boss's vitality at the Saturn's offsets, with
`0x060F` → `0xFF`. This follows the `RE-023` correspondence (`…F249C`).

## Controlled Change

No ROM change. Read-only ROM search, and MAME runs that force two RAM words:

| Run | Set | Partner | Forced |
| --- | --- | --- | --- |
| j1 | `mshvsfj` | Ken | Stage word `0xFF4880` = `0x0607` throughout; vitality `0xFF3E50`/`0xFF4844` = 0 from frame 5600 |
| j2, US, EU | `mshvsfj`, `mshvsfu`, `mshvsf` | Ken | The same, but stage released at 7100 and vitality at 8100 |
| Gouki runs | `mshvsfu`, `mshvsfj` | Gouki (cursor Up, Right) | As j2 |

## Prediction

- **ROM.** The seven Saturn records (boxes 1-4, pages 1-3) occur verbatim in
  each arcade program.
- **Language tables.** A pointer table of ending pages exists with parallel
  English tables.
- **MAME.** Forcing the stage word gives a first fight against Mech-Gouki;
  forcing vitality ends it; releasing both lets the ending play.
- **Gouki run** (made after the Ken runs, from the partner-line layout): Ryu's
  ending in `mshvsfu` shows "You are worthy" + RYU (record 15), then "We shall
  meet again" + AKUMA (record 35).

## Inputs and Provenance

- **Sets:** `mshvsf.zip` `5fae509a…`, `mshvsfu.zip` `32f4cb99…`, `mshvsfj.zip`
  `3f541827…` (`references/mshvsf/arcade/README.md`), plus the keys and
  `qsound.zip` (`REF-009`).
- **Driver:** pinned MAME 0.289 `cps2.cpp` (`local/mame_src/cps2.cpp`,
  `a8c09ef8…`).
- **MAME:** 0.289 (Homebrew), the `mame_timeline.lua` autoboot script, and the
  default EEPROM in `local/mame_arcade/nvram`.
- **Rebuilt programs:** `build_program`, `local/end006/<set>_program.bin`.

  | Set | Program SHA-256 |
  | --- | --- |
  | `mshvsf` | `b21726cf…` |
  | `mshvsfu` | `3f04821c…` |
  | `mshvsfj` | `b2612676…` |

  They differ in code, not in the ending data below.
- **Saturn side:**
  - `MC13.PAC` decoded `9eb9b7c6…`, table at `0xA06C`, `EXP-0034`;
  - `ME.PAC` `77210963…`;
  - run 1 states (`EXP-0037`) for the RAM offsets.

## Tools and Environment

- New `tools/reference/arcade_endings.py`: reads a slot's ending pages (four
  languages) and the English partner lines into an ignored JSON.
- New `tools/reference/arcade_ending_route.py`: writes the forced-stage and
  forced-vitality timeline; with `--partner gouki`, it reproduces the Gouki run
  timeline.
- Tests: `tests/unit/test_arcade_endings.py`.
- `tools/reference/cps2_text.py` (`decode_code`, `build_program`).

## Procedure

```bash
for s in mshvsfj mshvsfu mshvsf; do
  ./invenv.sh python -m tools.reference.arcade_endings local/arcade_roms/mshvsf/$s.zip \
    --driver local/mame_src/cps2.cpp --point 9 --partner 15 --out local/end006/${s}_ryu_gouki.json
done
./invenv.sh python -m tools.reference.arcade_ending_route --partner gouki --end 12600 \
  > local/end006/mame/mshvsfu_gouki/timeline.txt
MAME_TIMELINE=local/end006/mame/mshvsfu_gouki/timeline.txt mame mshvsfu \
  -rompath local/arcade_roms/mshvsf -video none -sound none -nothrottle -skip_gameinfo -nomouse \
  -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram \
  -snapshot_directory local/end006/mame/mshvsfu_gouki/snap -homepath local/mame_arcade \
  -autoboot_script tools/reference/mame_timeline.lua
```

- The Ken runs used the default route (`--partner ken`, `--end 16000`).
- The stage counter came from WRAM-H of run 1 states `f00037068`, `f00047158`,
  `f00050061`, and `f00055019`.
- The vitality came from states `f00062885`, `f00065104`, `f00068520`, and the
  post-KO state.

## Actual Result

### Saturn RAM offsets (searched before the MAME runs)

- **Stage index.** One WRAM-H byte stepped with the stages: `0x060F4881` = 4, 5,
  6, 7 for stages 5-8, and 7 at the post-continue select. The word
  `0x060F4880` reads `0x0607` at stage 8.
- **Boss vitality.** It is at `0x060F3E50` (mirror `0x060F4844`): 144 at fight
  start, 85, then 2 just before the final KO, and 0 after it.

### ROM: Japanese records are byte-identical

- **Saturn records in all three programs.** All seven occur verbatim:
  - pages at `0x2153CC` + `0x4C`·k;
  - boxes 3-4 at `0x2190A8`/`0x2190F4`;
  - boxes 1-2 at several places, including `0x2184C8`/`0x218514`.
- **The `MC13` table.** Saturn records 0-15 are arcade `0x211D2C`
  (Cyber-Akuma's Japanese win quotes, slot 19). Records 16-119 are one
  contiguous arcade block of 104 records from `0x217BE0`, which is exactly 319
  records past the slot-19 base. Records 55 and 107 have no arcade match, and
  54/106 match `0x210B5C`. Not resolved.
- **Ending-page pointer tables.** Four 26-slot tables, one per language:

  | Language | Table | Ryu (slot 9) |
  | --- | --- | --- |
  | Japanese | `0x20C14C` | `0x2153CC`, the Saturn pages |
  | English | `0x20C1B4` | `0x21F580` |
  | Spanish | `0x20C21C` | `0x229CD0` |
  | Portuguese | `0x20C284` | `0x2334C4` |

  The non-Japanese entries are 300 bytes: three pages of 2 × 25 cells. The
  Japanese pages equal the Saturn `ME.PAC` records byte for byte.
- **Identical across sets.** The extracted reports are byte-identical across the
  three sets: Ryu/Ken `bb970bc7…`, Ryu/Gouki `8f1ee992…`.
- **English partner lines.** From `0x22226C`: 52 records of 100 bytes, each a
  short line with the `0x0000` name placeholder. There is no English record
  corresponding to the Japanese four-box dialogue.

### MAME: no-play route to the ending

- **j1.** Forcing the stage word gave a Ryu/Ken first fight on `STAGE-08`
  against Mech-Gouki. Forced vitality gave an immediate KO ("PERFECT"). With the
  stage still forced, the game looped stage 8.
- **j2** (stage and vitality released):
  - Japanese post-boss dialogue: the same Ryu/Ken lines as the Saturn Ryu/Ken
    run (`EXP-0041` Part 2);
  - then Ryu's three Japanese pages, then the staff credits.
- **US and EU (Ryu/Ken).** Both show the same English scenes:

  | Scene | US screenshot | Text |
  | --- | --- | --- |
  | Box 1 | `f08270`, `dc6804d7…` | "RYU, you're not bad." (record 10, Ken's slot) |
  | Box 2 | `f08870`, `8dff719a…` | "We shall meet again KEN." (record 35 = 26 + 9, Ryu's slot) |
  | Pages 1-3 | Page 2 `f09620` `072d3473…`; page 3 `f10220` `27fd240c…` | The English text read from `0x21F580`, 2 × 25 cells, centered |

  Frame hashes differ between US and EU, but the content reads the same.
- **Gouki runs: prediction met.**
  - `mshvsfu`: "You are worthy RYU." (record 15, Gouki's slot; `f08550`
    `f8bdb41f…`), then "We shall meet again AKUMA." (`f09150` `72d20c08…`).
    Gouki is named AKUMA in English.
  - `mshvsfj`: the four Japanese boxes and three pages exactly as on the Saturn
    Ryu/Gouki run.

## Conclusion

**CONFIRMED.**
- The arcade Japanese ending and dialogue records for Ryu are byte-identical to
  the Saturn's, in all three sets.
- **Official English exists for Ryu's three ending pages:** English table
  `0x20C1B4`, slot 9; read from ROM and seen on screen in `mshvsfu` and
  `mshvsf`.
- **The English release does not translate the Japanese post-boss dialogue.** It
  shows two generic lines from a 52-record partner table, each naming the other
  character. One of them depends on the partner.

**SUPPORTED** (two partners, one prediction met): the English partner lines are
indexed as partner record = partner slot, and point reply = 26 + point slot.

**CONFIRMED** in MAME: the arcade stage and vitality words sit at the Saturn
offsets with `0x060F` → `0xFF` (`0xFF4880`, `0xFF3E50`/`0xFF4844`). This makes
any character's arcade ending reachable with no play.

## Gaps for M7 (decisions, not taken here)

- **Pages.** The official English for the three pages is ready, on 25-cell
  lines. The Saturn records have 19 cells, so the pages need pair glyphs, as for
  win quotes (`FONT-003`).
- **Dialogue.** There is no official English for the Saturn's four Japanese
  boxes. Options for the user:
  1. adopt the arcade's two English lines, with a different structure (two
     boxes instead of four) and team-dependent text;
  2. use a non-official translation, which needs a `GATE-TRANSLATION`-style
     decision;
  3. leave the dialogue in Japanese.
- **Names.** English uses its own names (AKUMA for Gouki). The Saturn name
  table (`EXP-0039`) is Japanese.

## Uncertainty and Alternatives

- Only Ryu with Ken and with Gouki were seen. Other partners and point
  characters were not.
- Records 54/55/106/107 of the `MC13` table do not map cleanly to the arcade
  block.
- The forced vitality gives a "PERFECT" round start. It did not change the
  dialogue or pages compared with the Saturn's natural wins, but other
  conditions (who lands the KO) were not varied.
- The arcade code that indexes the dialogue block (`0x217BE0`) and the partner
  lines was not traced.

## Reproduction

See Procedure. The reports and screenshots stay in ignored `local/end006/`.
