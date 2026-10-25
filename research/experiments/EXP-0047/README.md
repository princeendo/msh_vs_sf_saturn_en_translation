# EXP-0047: Name-Length Growth, and Where English Names Would Reach Japanese Text

Task: END-022
Status: DONE (2026-10-24; the side-effect policy is a user decision, recorded in
`TASKS.md`)
Confidence: CONFIRMED (growth and the role of the length table); census
CONFIRMED for the known tables, SUPPORTED for the sweep.

## Observation

- `EXP-0044` showed that the game inserts as many cells per name as the
  `MM.BIN` name-length table says, and it shrank RYU's (3 → 2).
- `EXP-0046` found that several roster names need more cells in English than
  in Japanese (BISON: 2 → 3). Growth was untested.
- A combined roster image will put English names in the global name table, so
  any placeholder left in Japanese text would show an English name.

## Hypothesis

- **G (growth):** a name entry longer than its Japanese original, with its
  length raised to match, is inserted in full, and the following text shifts
  right.
- **L (control of the length table):** with the length left unchanged, the
  same longer entry is truncated to the old length.

## Controlled Change

RAM writes on the untouched image, from `ryu_ken_post_boss_ko.mcs`, captured on
box 3 (Ryu's line, which inserts the partner's name, ケン):

| Run | Name entry (WRAM-H `0x06096004`) | Length (`0x060AF8F2`) |
| --- | --- | --- |
| G0 (control) | ケン (unchanged) | 2 (unchanged) |
| G1 | ABCD (`08E8 08E9 08EA 08EB`, full-width, in the untouched font) | 4 |
| G2 | ABCD | 2 (unchanged) |

## Prediction

- G1 shows "ABCD、", with the rest shifted right by two cells.
- G2 shows "AB、".
- Only line 1 changes.

## Procedure

- A one-off agent script for each run: load the state, apply the writes, run
  to frame 990, then take a screenshot every 30 frames until frame 1080
  (`local/end022/g*`).
- The census:

  ```bash
  ./invenv.sh python -m tools.text.placeholder_census --out data/text/placeholder_census.json
  ```

## Actual Result

### Growth

| Run | Line 1 of box 3 | Diff vs G0 inside the box | Screenshot (`t01050`) |
| --- | --- | --- | --- |
| G0 | ケン、 | — | `eff1b986…` |
| G1 | ＡＢＣＤ、 | 447 px, x 107-177, y 23-36 | `438f2989…` |
| G2 | ＡＢ、 | 242 px, x 107-136, y 23-36 | `e5444714…` |

Line 2 is unchanged in both trials.

### Placeholder census (`data/text/placeholder_census.json`, metadata only)

**100 placeholders in total.** A roster image (the M5 win quotes plus all 17
roster endings) would make 69 of them English: roster win quotes drop their
placeholders (`RE-042`), and roster dialogue pairs are replaced. That leaves
**31 in Japanese text.** In detail:

| Where | Sites | When a player sees it |
| --- | --- | --- |
| Win quotes of excluded characters: Norimaro (17), and slots 20, 21, 22, 24 | 13 | Only when playing those characters |
| `MC13` dialogue pairs of excluded slots (0, 17, 20-25, as partner or point) | 16 | Only on teams that include them |
| `MM.BIN` `0x7CD90`, in a Japanese text table (683 cells, `0x7CC86`-`0x7D1DC`) | 1 | Unknown: see below |
| `MC11` `0x36B6` | 1 | Not text: an offset table, inspected; a false positive of the sweep |

`ME.PAC` (Japanese ending pages) has no placeholders. Other sweep hits (`SEL`,
`SEL2`, `PL05`, `MVDEMOF6.ST2`, `MEMFIX` font data, `MC06`) were inspected
and are data; the final sweep rule (at most two zero cells near a site)
excludes them.

### The `MM.BIN` Japanese text table

- `MM.BIN` (the resident program) holds about 28 records of Japanese dialogue.
  The lines include ones about Gambit and Rogue, which are not playable.
- The same text is in the arcade programs at `0x213F82`-`0x2147EC`, just before
  the Japanese ending pages, in all three sets. It is referenced from code (one
  pointer, `0x0B03BA` → `0x214748`), not from a per-language table.
- **No English counterpart was found:** there are no Gambit or Rogue lines in
  the English text.
- Where it is shown is not identified.

## Conclusion

- **CONFIRMED:**
  - names can grow;
  - the name-length table alone sets how many cells are inserted (truncating if
    it is too small);
  - insertion shifts only its own line.

  So every roster name can be set, BISON included.
- **The side effect is bounded.** With a roster image, English names would
  appear inside Japanese text in:
  - lines of excluded characters (Norimaro, secret characters, Apocalypse);
  - one line of an unidentified Japanese-only text table in `MM.BIN`.

  Roster-only play shows no English name in Japanese text, unless that
  `MM.BIN` line is shown during it.

## Uncertainty and Alternatives

- **Sweep coverage.** The sweep finds placeholders inside runs of 16-bit
  quote-font text. Text in another encoding would be missed.
- **Which name appears.** In excluded characters' lines, the name inserted is
  the other team member's, which could be a roster name in English.
- **The `MM.BIN` table.** Its screen and trigger are unknown. Identifying it
  is a new backlog task (`TXT-001`).

## Reproduction

See Procedure. Everything runs from the untouched image, with no gameplay.
