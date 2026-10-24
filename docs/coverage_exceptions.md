# Win-Quote Coverage and Exceptions (M5)

The register for `RE-043`. Scope was decided by the user on 2026-10-24:

> Use the 17-character roster: the 14 ordinary playable characters plus Captain
> America, Blackheart and Dhalsim (their own blocks only). Exclude Norimaro,
> secrets, Shadow and bosses; accept that Spider-Man's English also covers Armored
> Spider-Man.

The evidence for every file is `EXP-0034` (`data/text/coverage_manifest.json`):
Saturn file `MCnn` holds arcade slot `nn`'s Japanese block, byte-identical.

## In Scope

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

## Exceptions

Nothing listed here may be translated or modified in M5.

| Item | Evidence | Reason | Owner |
| --- | --- | --- | --- |
| `MC00` slot 0 (Apocalypse), plus three extra tables (`0x392E`, `0x3D7A`, `0x404E`) | irregular file; block inside a 26-record table at `0x3106` | boss; extra tables unidentified | `SPECIAL-001` |
| `MC02` slot 23 block (`0xDF68`) | second whole block in `MC02` | secret character | `SPECIAL-001` |
| `MC08` slot 24 block (`0xBE5C`) | second whole block in `MC08` | secret character | `SPECIAL-001` |
| `MC0C` 4-record table (`0x3B88`) | matches no arcade slot | content unknown | a future investigation task, to be created only when needed |
| `MC11` slot 17 (Norimaro) | ordinary file | special case (`AGENTS.md` rule 24) | `SPECIAL-001` |
| `MC13` slot 19 (Cyber-Akuma), inside a 120-record table that also holds one slot-15 record | irregular file | boss; extra content unidentified | `SPECIAL-001` |
| `MC14` slot 20 (second Zangief entry) | ordinary file | secret character | `SPECIAL-001` |
| `MC15` slot 21 (second Sakura entry) | ordinary file | secret character | `SPECIAL-001` |
| `MC16` slot 22 (Shadow) | ordinary file | secret character | `SPECIAL-001` |
| Endings and any other text surface | not in `MCnn` win-quote tables | outside post-fight scope | `END-001` (M6) |

The two PS1-only English blocks (`EXP-0032`) belong to these exceptions, if they
belong anywhere. They stay with `SPECIAL-001`.

## Rules for M5 Tasks

- Generators and compilers take the roster file as their only source of targets.
  A table not listed there is never written.
- Check every M5 build to confirm that bytes outside the roster blocks are
  unchanged in each touched file, including the untouched blocks listed above.
- Changing the roster requires a user decision recorded here.
