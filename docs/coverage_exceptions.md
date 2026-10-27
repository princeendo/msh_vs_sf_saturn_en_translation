# Coverage and Exceptions

Two registers: win quotes (M5) and endings (M8).

## Win Quotes (M5)

The register for `RE-043`. Scope was decided by the user on 2026-10-24:

> Use the 17-character roster: the 14 ordinary playable characters plus Captain
> America, Blackheart and Dhalsim (their own blocks only). Exclude Norimaro,
> secrets, Shadow and bosses; accept that Spider-Man's English also covers Armored
> Spider-Man.

The evidence for every file is `EXP-0034` (`data/text/coverage_manifest.json`):
Saturn file `MCnn` holds arcade slot `nn`'s Japanese block, byte-identical.

### In Scope

The 17 characters are listed in `data/text/m5_roster.json`: slots 1-16 and 18.
That covers every structurally ordinary playable character, plus three irregular
files whose own blocks are targeted directly:

| File | In scope | Left untouched |
| --- | --- | --- |
| `MC02` | slot 2 (Captain America) at `0xD6D8` | slot 23 block at `0xDF68` |
| `MC08` | slot 8 (Blackheart) at `0xAA24` | slot 24 block at `0xBE5C` |
| `MC0C` | slot 12 (Dhalsim) at `0xAA88` | unmatched 4-record table at `0x3B88` |

**Accepted side effect.** Slot 25 (the second Spider-Man entry, Armored Spider-Man)
uses `MC07`'s block, which slot 7 also uses, on both platforms. Translating
Spider-Man therefore gives slot 25 the same English. The arcade's English release
shares these quotes in the same way (`EXP-0029`).

### Exceptions

Nothing listed here may be translated or modified in M5.

| Item | Evidence | Reason | Owner |
| --- | --- | --- | --- |
| `MC00` slot 0 (Apocalypse), plus three extra tables (`0x392E`, `0x3D7A`, `0x404E`) | irregular file; block inside a 26-record table at `0x3106` | boss; win quotes built (`EXP-0081`); the extra tables are its pre-fight exchanges, not yet built | `SPECIAL-004` |
| `MC02` slot 23 block (`0xDF68`) | second whole block in `MC02` | secret character: since 2026-10-26 official English (`SPECIAL-003`) | `SPECIAL-003` |
| `MC08` slot 24 block (`0xBE5C`) | second whole block in `MC08` | secret character: since 2026-10-26 official English (`SPECIAL-003`) | `SPECIAL-003` |
| `MC0C` 4-record table (`0x3B88`) | matches no arcade slot | content unknown | a future investigation task, to be created only when needed |
| `MC11` slot 17 (Norimaro) | ordinary file | special case (`AGENTS.md` rule 24): since 2026-10-26 official English (`SPECIAL-002`, `EXP-0079`) | `SPECIAL-002` |
| `MC13` slot 19 (Cyber-Akuma), inside a 120-record table that also holds one slot-15 record | irregular file; the extra content includes the post-boss dialogue records (`EXP-0040`) | boss; Cyber-Akuma's own quotes stay excluded | `SPECIAL-001` (quotes); the post-boss dialogue records are ending text: see Endings (M8) |
| `MC14` slot 20 (second Zangief entry) | ordinary file | secret character: since 2026-10-26 translated (`SPECIAL-003`, `EXP-0078`) | `SPECIAL-003` |
| `MC15` slot 21 (second Sakura entry) | ordinary file | secret character: since 2026-10-26 translated (`SPECIAL-003`) | `SPECIAL-003` |
| `MC16` slot 22 (Shadow) | ordinary file | secret character: since 2026-10-26 official English (`SPECIAL-003`) | `SPECIAL-003` |
| Endings and any other text surface | not in `MCnn` win-quote tables | outside post-fight scope | `END-001` (M6) |

The two PS1-only English blocks (`EXP-0032`) belong to these exceptions, if they
belong anywhere. They stay with `SPECIAL-001`.

### Rules for M5 Tasks

- Generators and compilers take the roster file as their only source of targets.
  A table not listed there is never written.
- Check every M5 build to confirm that bytes outside the roster blocks are
  unchanged in each touched file, including the untouched blocks listed above.
- Changing the roster requires a user decision recorded here.

## Endings (M8)

The register for `END-025`. The scope is the same 17-character roster
(`data/text/m5_roster.json`, slots 1-16 and 18), now as point characters and
partners. Evidence: `EXP-0046` (census), `EXP-0048` (combined build), `EXP-0049`
and `EXP-0050` (live), and `data/text/ending_coverage.json`
(`tools/text/ending_coverage.py`, metadata only).

### In Scope

For each roster slot `s`, the combined image (reference `m8_roster`) replaces:

- its Japanese ending pages in `ME.PAC` with the official English pages
  (75 records in total);
- its two `MC13` dialogue pairs (partner index `s`, point index `26 + s`;
  records `16 + 2s`, `17 + 2s`, `68 + 2s`, `69 + 2s`) with the arcade's
  English partner lines;
- its `MM.BIN` name entry and name-length byte.

`ending_coverage.py --built-track` checked track 01 `2a5b26b7…`. Every byte
outside these targets is unchanged in `ME.PAC`, the decoded `MC13`, and
`MM.BIN`.

### Accepted Side Effects (Shared Pointers)

Both arcade page tables give some slots the same pointer. The Saturn's records
equal the arcade Japanese ones (`EXP-0042`, `EXP-0046`), so these slots share
whatever the roster's pages say.

| Slot | Shares pages with | Consequence |
| --- | --- | --- |
| 0 (Apocalypse) | slot 1 (Cyclops), in both the Japanese and English tables | Slot 0 shows Cyclops's English pages, as in the arcade English. |
| 19 (Cyber-Akuma / Mech-Gouki) | slot 18 (Dan), in the Japanese table | Slot 19's pointer reaches Dan's English pages. In the arcade English table, slot 19 points to a different block instead. |

Neither slot is in the roster, and no session so far has reached either one
as a point character. Whether the game can is not tested.

### Exceptions

Nothing listed here may be translated or modified in M8.

| Item | Location | Reason | Owner |
| --- | --- | --- | --- |
| Slot 0 dialogue pairs | `MC13` records 16, 17, 68, 69 | boss | `SPECIAL-001` |
| Slot 17 (Norimaro): pages, dialogue, name | `ME.PAC` `0x3F5C` (5 records); `MC13` 50, 51, 102, 103; `MM.BIN` slot 17 | special case (`AGENTS.md` rule 24). The US arcade's English page table points slot 17 at Dan's pages, so the pages have no English of their own. Since 2026-10-26 (`SPECIAL-002`, `EXP-0079`, release builds only): pages translated, dialogue official, name set. | `SPECIAL-002` |
| Slot 19 (Cyber-Akuma / Mech-Gouki): dialogue, name | `MC13` 54, 55, 106, 107 (these do not equal the arcade block, `EXP-0042`); `MM.BIN` slot 19 | boss; records unmatched | `SPECIAL-001` |
| Slots 20-22 (second Zangief entry, second Sakura entry, Shadow) | `ME.PAC` `0x4254` (5), `0x43D0` (3), `0x44B4` (6); `MC13` 56-61, 108-113; `MM.BIN` | secret characters. Since 2026-10-26 (`SPECIAL-003`, `EXP-0078`, release builds only): pages translated, dialogue official, names set. | `SPECIAL-003` |
| Slots 23-25 (U.S. Agent, Mephisto, second Spider-Man entry) | `ME.PAC` `0x467C`-`0x4844` (6 records; 0-2 already English); `MC13` 62-67, 114-119; `MM.BIN` | secret characters. Since 2026-10-26 (`SPECIAL-003`): records 3-5 translated, dialogue official, names set. | `SPECIAL-003` |
| `MC13` records 0-15 | Cyber-Akuma's win quotes | already an M5 exception | `SPECIAL-001` |
| `MM.BIN` Japanese text table | `0x7CC86`-`0x7D1DC` | screen unknown; one name placeholder (`EXP-0047`) | `TXT-001` |

**Names in the remaining Japanese text.** The name table is global. Excluded
characters' lines that insert a roster name show it in English (user decision,
2026-10-24, `EXP-0047`).

### Rules for Ending Work

- Generators take the roster file as their only source of targets.
- Check every ending build with `ending_coverage.py --built-track`. Every
  `outside_unchanged` must be true.
- Changing the roster or the names requires a user decision recorded here or
  in `docs/localization_plan.md` (names: `LOC-001`).
