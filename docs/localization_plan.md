# Localization Plan: Character Names Across Text, Art, and Audio

Status: **provisional** (user decisions, 2026-10-25). The final policy is
`LOC-001` (`TASKS.md`). Rationale and history: `research_log.md`, 2026-10-25
entries; `EXP-0049`, `EXP-0050`.

## The Problem

The Saturn release is the Japanese one. Its art and voice use the Japanese
names. The official English we reuse comes from the US arcade, which uses the
US names. Only three roster-relevant names differ:

| Slot | Arcade English name (`0x2236BC`) | Saturn name | Where the Saturn shows it |
| --- | --- | --- | --- |
| 14 | BISON | Vega | VS screen, life bar, win screen, ending speaker labels ("Vega"); voice (user observation) |
| 15 | AKUMA | Gouki | VS screen "GOUKI" (`EXP-0050` frame `f00013144`, `0268cc2d…`) |
| 19 (boss) | CYBER-AKUMA | Mech-Gouki | VS screen "MECH-GOUKI" (`EXP-0049` frame `f00009412`, `14d5ba76…`), life bar |

The other 23 arcade English names match the Saturn's Latin names, as far as
seen. Slots 20-25 (secret characters) are excluded and not checked.

Changing text is cheap. Changing art or voice is not:
- the art formats are not decoded;
- the voice sample format and locations are unknown;
- English-name voice clips would need a source.

## Current Provisional Decision: the Saturn's Names in Text

The English text follows the Saturn's art and voice. Art and audio are not
changed. Implemented in `tools/text/official_endings.py`:
- `NAME_OVERRIDES = {14: "VEGA", 15: "GOUKI"}`: the inserted names;
- `TEXT_OVERRIDES`: "Cyber Akuma" → "Mech-Gouki", then "Akuma" → "Gouki",
  applied to the ending pages, the dialogue, and the combined image's win
  quotes.

Every place this touches in the roster image (`local/end027/roster_image.json`):

| Where | Text now |
| --- | --- |
| `MM.BIN` name table, slot 14 | VEGA |
| `MM.BIN` name table, slot 15 | GOUKI |
| Gouki's win quote (`MC0F.PAC` records 7 and 15) | "There is no good or evil, / only Gouki!" |
| Wolverine's ending, page 2 (`ME.PAC` `0x2F54`) | "I know you're watching me / Gouki! You know who I am!" |
| Vega's ending, page 1 (`0x3CFC`) | "Ha! I have the technology / behind the Mech-Gouki!!" |
| Gouki's ending, pages 1-2 (`0x3DE0`) | "Gouki! Don't boast of…", "…Get ready Gouki!!" |
| Dan's ending, page 1 (`0x40D8`) | "…made a fool of me, Gouki!" |

**To revert to US names:** empty both override tables, rebuild, re-baseline
`m8_roster` and `end010`, and do one cold-boot check.

## Options for the Final Policy

| Option | Text | Art | Audio | Cost and risk |
| --- | --- | --- | --- | --- |
| A. Saturn names everywhere (current) | Vega, Gouki, Mech-Gouki | unchanged | unchanged | None beyond text. Western players may expect US names. |
| B. US names everywhere | Bison, Akuma, Cyber-Akuma | edited on every screen that shows them | announcer clips replaced | Needs art and audio reverse engineering, plus a source for the clips. |
| C. US names in text only | Bison, Akuma, Cyber-Akuma | unchanged | unchanged | Inconsistent on screen. Rejected for Vega on 2026-10-25. |

## Questions for the User (`LOC-001`)

1. A or B?
2. If B: is audio in scope, and from which source? Candidates are unverified:
   the US arcade set or a US home release. Whether one exists with these
   clips, and whether using it is acceptable, are open questions.
3. Which names should excluded characters (Norimaro, the secret characters,
   Apocalypse) use, if they ever come into scope?

## Evidence to Collect Before Deciding (smallest experiments)

1. **Art inventory.** From recorded sessions, list every screen that shows a
   regional name: character select, VS screen, life bar, win screen, ending
   speaker labels, and any other. Most frames already exist under `local/`.
2. **Audio inventory.** Listen to the character-select and VS screens for
   spoken names, for each of the three characters, and record which names are
   voiced.
3. **Only if option B:** a census of disc files for art and audio formats.
   This is new reverse engineering, not started.
