# EXP-0076: Secret-character names across Saturn JP, US arcade and PS1 US

Task: LOC-007
Status: DONE
Confidence: CONFIRMED (static reads of all three releases' data); the
display of three blank life-bar labels is a HYPOTHESIS (see below)

## Observation

The user asked whether the secret characters' names differ between the
Japanese release and the US/EU releases, as Vega/Gouki/Mech-Gouki do.
`docs/coverage_exceptions.md` lists roster slots 20-25 as secret characters:
the second Zangief, the second Sakura, Shadow, U.S. Agent, Mephisto and the
second Spider-Man.

## Hypothesis

At least one secret character carries a different name on the Saturn JP than
in the US arcade or PS1 US release.

## Controlled Change

None (read-only comparison).

## Prediction

A name table entry for a secret character that differs between releases.

## Inputs and Provenance

- Saturn JP image (manifest hashes): `MM.BIN`, `ME.PAC` (and its copy
  `ME.SHX`), every file searched.
- US arcade `mshvsfu` and Japanese arcade `mshvsfj`
  (`local/arcade_roms/mshvsf/`), program rebuilt with
  `tools/reference/cps2_text.build_program` and the pinned `cps2.cpp`.
- PS1 US (Redump 12632), every readable file.

## Tools and Environment

Scratch search over all files: ASCII (upper, title and mixed case) and the
arcade 16-bit text codes (big-endian in the arcade program, little-endian on
the PS1, `tools/reference/cps2_text`); decoders for the `MM.BIN` banner, VS and
life-bar records (`EXP-0062`, `EXP-0063`, `EXP-0065`). Results:
`local/loc007/name_hits.json` (`d8ad5f6d…`), `ps1_hits.json` (`92c3b90a…`).
Python 3.12.13.

## Procedure

1. Read the Saturn's name surfaces by index: the `ME.PAC` speaker table
   (`0xB164 + 16i`), the win-banner (`0x9FBF8 + 12i`) and VS-screen
   (`0x66536 + 12i`) record tables, and the life-bar label tables (P1
   `0x32CA4 + 16i`, P2 `0x32E74 + 16i`).
2. Search all three releases for every form of the secret characters' names
   (ZANGIEF, METAL, MECH, SAKURA, DARK, SATSUI, SHADOW, CHARLIE, NASH, AGENT,
   MEPHISTO, SPIDER, ARMOR).

## Actual Result

| Slot | Character | Saturn JP: life bar / banner and VS / speaker | US and JP arcade text name table (`0x223938`-`0x2239E0`) | PS1 US game text | PS1 US menus (`SLUS_007.93`) |
| --- | --- | --- | --- | --- | --- |
| 20 | second Zangief | ZANGIEF / ZANGIEF record only / "Metal Zangief" | ZANGIEF | ZANGIEF | MECH-ZANGIEF |
| 21 | second Sakura | SAKURA / SAKURA record only / "Sakura" | SAKURA | SAKURA | DARK SAKURA |
| 22 | Shadow | blank / SHADOW / "Shadow" | SHADOW | SHADOW | SHADOW |
| 23 | U.S. Agent | blank / U.S.AGENT / — | U.S.AGENT | U.S.AGENT | U.S.AGENT |
| 24 | Mephisto | blank / MEPHISTO / — | MEPHISTO | MEPHISTO | MEPHISTO |
| 25 | second Spider-Man | SPIDER-MAN / SPIDER-MAN record only / — | SPIDER-MAN | SPIDER-MAN | ARMORED SPIDER-MAN |

- **Saturn.** The life-bar label records 20, 21 and 25 equal ZANGIEF's (13),
  SAKURA's (16) and SPIDER-MAN's (7); 22-24 are all blank (`0x5020`). The
  banner and VS tables are keyed by a name ID (20 SHADOW, 21 U.S.AGENT, 22
  MEPHISTO, 23-25 the unused US BISON, AKUMA, CYBER-AKUMA, 26 an unused
  CHARLIE banner record) and hold no variant-specific record. The slot →
  name-ID mapping was not found as a table.
- **Arcade.** The English name table is identical in `mshvsfu` and
  `mshvsfj`. Both also carry the Saturn's ASCII speaker table
  (`0x7155E`: "Metal Zangief", "Sakura", "Shadow") and a debug list
  (`0x20231`: "Metal Zangief", "Satsui Sakura", "Shadow"; `0xB6461`: Shadow
  as "NASH").
- **PS1 US.** Its game text keeps the arcade table (`SELECT.BIN`,
  `ENDING.BIN`, …) and the ASCII speaker table ("Metal Zangief",
  "Mech-Gouki"; `END.ARC`, `ENDING.BIN`). Only the executable's PS1-specific
  lists (`0x18708`-`0x18A24`, next to SCORE RANKING, VS RANKING and PLAYER
  SELECT) use MECH-ZANGIEF, DARK SAKURA and ARMORED SPIDER-MAN.

## Conclusion

**DISPROVEN** for the game data: every name a secret character shows on the
Saturn equals the US arcade's, which is the same in both arcade regions. The
full variant names MECH-ZANGIEF, DARK SAKURA and ARMORED SPIDER-MAN exist only
in the PS1 port's own ranking and menu lists, which the Saturn does not have.
No change is needed for either name variant. The one name that could be
changed by choice is the speaker label "Metal Zangief" (`ME.PAC` field 20),
which the arcade and the PS1 also use.

## Uncertainty and Alternatives

- The blank life-bar labels for Shadow, U.S. Agent and Mephisto (records
  22-24) are not seen in play; the game may draw no label for them, or take
  it from elsewhere (`docs/known_unknowns.md`).
- Whether any Saturn screen shows the speaker label "Metal Zangief" depends
  on the secret characters' endings (`SPECIAL-003`).

## Reproduction

The scratch search is summarised above; the decoders are the record formats of
`EXP-0062` (banner), `EXP-0063` (VS) and `EXP-0065` (labels).
