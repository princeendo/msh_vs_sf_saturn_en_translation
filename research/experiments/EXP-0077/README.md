# EXP-0077: Secret characters' post-fight text and endings: sources and oracles

Task: SPECIAL-003
Status: DONE (investigation; the build route needs a user decision)
Confidence: CONFIRMED (static reads of the US arcade program, the PS1 US
disc and the Saturn files)

## Observation

- `docs/coverage_exceptions.md` lists the secret characters (slots 20-25) as
  M5/M8 exceptions: win quotes in `MC14`-`MC16`, `MC02` (slot 23 block
  `0xDF68`) and `MC08` (slot 24 block `0xBE5C`); ending pages in `ME.PAC`
  (`0x4254`, `0x43D0`, `0x44B4`, and a shared block at `0x467C`); dialogue in
  `MC13` records 56-67 and 108-119.
- RC-3 (`references/mshvsf/arcade/README.md`): "the secret characters have
  unique quotes only in Japan". `EXP-0032` hypothesised that two PS1-only
  English blocks give two secret characters their own quotes.

## Hypothesis

Official English exists for every secret character's win quotes, ending pages
and partner lines, in the US arcade or the PS1 US.

## Controlled Change

None (read-only).

## Prediction

A distinct English block per secret slot in the arcade tables, or in the PS1's
extra blocks.

## Inputs and Provenance

US arcade `mshvsfu` (program rebuilt from the local zip and the pinned
`cps2.cpp`); PS1 US `DAT/SELECT.BIN` (`c78b1502…`); Saturn `MC0D`, `MC10`,
`MC14`, `MC15` (decoded with `tools/disc/pac_lzss.py`).

## Tools and Environment

`tools/reference/quote_pairing.pointer`, `tools/reference/arcade_endings`
(`page_span`, `latin`), Python 3.12.13. No game text is committed.

## Procedure

1. Group the arcade English win-quote table (`0x20C014`) by pointer for slots
   0-25.
2. Compare the PS1's extra blocks (`0x1376C`, `0x13A8C`) entry by entry with
   the arcade's.
3. Compare the Saturn's decoded `MC14`/`MC15` with `MC0D`/`MC10`.
4. Group the arcade ending page tables (Japanese `0x20C14C`, English
   `0x20C1B4`) by pointer; measure the shared English block; read the
   English partner lines (`0x22226C`) for slots 19-25.

## Actual Result

- **Win quotes (arcade English):** slots 20, 21 and 25 share Zangief's (13),
  Sakura's (16) and Spider-Man's (7) blocks. Slots 22 (Shadow), 23 (U.S.
  Agent) and 24 (Mephisto) have their own blocks (`0x21DC80`, `0x21DFA0`,
  `0x21E2C0`).
- **PS1 extras:** both blocks equal the arcade's Zangief and Sakura blocks in
  all 8 entries. They are duplicates stored at the slot-20/21 positions, not
  PS1-only English. `EXP-0032`'s hypothesis is **DISPROVEN**.
- **Saturn Japanese:** `MC14` and `MC15` differ from `MC0D` and `MC10` (55,276
  and 55,688 of the common bytes), so slots 20 and 21 have their own
  Japanese quotes, which no official English translates (RC-3 holds).
- **Ending pages:** the Japanese table has unique pages for slots 20 (5), 21
  (3) and 22 (6), and one block for 23-25 (the table's last pointer, extent
  unknown). The English table points slots 19-25 at one block (`0x22032C`)
  of two records: a generic message congratulating the player on beating the
  game with a secret character.
- **Partner lines:** the arcade has English partner and reply lines for every
  slot 19-25 (`0x22226C`, records `s` and `26 + s`).

## Conclusion

- **CONFIRMED:** official English exists for slots 22-24's win quotes and for
  every secret slot's partner lines.
- **CONFIRMED:** for slots 20-21's own quotes and for all secret ending pages,
  the only official English is a substitute: Zangief's and Sakura's quotes,
  and the generic two-record ending.
- **DISPROVEN:** PS1-only English for secret characters.

## Uncertainty and Alternatives

- The extent of the Japanese 23-25 ending block is unknown (last table
  pointer); the Saturn `ME.PAC` block at `0x467C` would show it.
- `MC13` records 56-67 and 108-119 are not yet compared with the arcade
  Japanese (slot 19's do not match, `EXP-0042`).
- How the Saturn's Japanese ending pages for slots 20-25 relate to the arcade
  Japanese is not yet checked byte for byte.

## Reproduction

Read `0x20C014`, `0x20C14C`, `0x20C1B4` and `0x22226C` of the `mshvsfu`
program with `tools/reference/quote_pairing.pointer` and
`tools/reference/arcade_endings.page_span`/`latin`; read `DAT/SELECT.BIN`
from the PS1 image with `tools/disc/iso9660.Track`.
