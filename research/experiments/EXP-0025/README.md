# EXP-0025: Identify Ryu's Win-Quote Selection Mechanism

Task: `RE-023`
Date: 2026-10-17
Status: IN_PROGRESS (Part 1 pre-registered)
Confidence: HYPOTHESIS

## Question

Which code chooses the shown record of Ryu's quote table, and can a chosen record be
forced for live verification (`RE-024`)?

## Observations (offline, 2026-10-17)

### 1. The `@(76,r12)` counter is the partner-name glyph counter

The original `RE-023` hypothesis said this counter selects the quote. Static
reading of `0x060AF81E-0x060AF8D0` (from the `exp0023c-slot7` WRAM-H extraction)
contradicts it:

- **Normal codes.** `r0 = @r8` is the current quote word. If it is non-zero and
  `@(76,r12) == 0`, the routine emits `0x5000|code` and advances `r8` by 2.
- **Placeholders.** If the word is `0000`, or the counter is non-zero, the routine
  instead:
  - takes partner id `@(82,r10)`, with `r10` loaded from `r11+0xABBA`;
  - emits code `@(r9 + id·16 + 2·counter)` from a name table: `0x06095EC4`, or
    `0x06096204` when the word at `r11+0xCC8E` is non-zero;
  - increments the counter.
- **End of name.** When the counter equals the name length (a byte table at
  `0x060AF8E8`, or `0x060AF908` when the flag is set), the counter returns to 0
  and `r8` advances past the placeholder.
- **Check.** Name entry `id/2 = 9` in the `0x06095EC4` table decodes to katakana
  `089C 0897 0858` (リュウ, Ryu), matching file `MC09.PAC` = character 9.

So the counter expands the `0000` placeholder into the partner's name, one glyph per
cell. **The selection hypothesis is `DISPROVEN` by code reading.** The
name-counter reading is `SUPPORTED`; it is not live-tested.

Side observation (`HYPOTHESIS`, not pursued here):

- The second length table holds 10, 7, 15, 4, 9, 12, 9, 10, 10, 3, 3, 7, 7, 7, …
  Entries 9 and 10 are both 3, consistent with "Ryu" and "Ken"; entry 2 (15) fits
  "Captain America".
- The `0x06096204` region does not hold name codes in this state.
- Together with the alternate layout set (`r11+0xCC90`: 25 cells, 12-pixel step;
  `EXP-0022`), this suggests a latent alternate text mode. Recorded in
  `docs/known_unknowns.md`.

### 2. A record pointer at WRAM-H `0x060F249C`

The two `exp0023c` quote states show different records (4 and 5). Searching both
WRAM regions for values that differ in the predicted way found:

| Candidate | State 4 | State 5 | Hits |
| --- | --- | --- | --- |
| Long `table + 76·r` | `0x002092DC` | `0x00209328` | **one: WRAM-H `0x060F249C`** |
| Byte or word `r` | 4 | 5 | many (not discriminating) |
| Offset `76·r` | `0x130` | `0x17C` | none |

No code constant references `0x060F249C` directly, so it is likely a field of a
structure addressed through a base register. The table base `0x002091AC` appears
as data at `0x06094FD8` and `0x060F9E4A`.

## Hypothesis (Part 1)

During the KO-to-quote transition, one CPU store writes `0x002091AC + 76·r` to
`0x060F249C`, where `r` is the record then displayed. The writing instruction and
its registers expose where `r` comes from.

## Controlled Change (Part 1)

None to game data. A write breakpoint on `060F249C-060F249F 260F249C-260F249F`
(cached and cache-through addresses) halts the CPU at each store.

## Prediction (Part 1)

- The breakpoint fires at least once between the KO and the quote appearing.
- Over the fires, the last value written equals `0x002091AC + 76·r` of the quote
  then shown. The shown record is identified offline with `quote_render --match`.
- In a second replay that shows a different quote, the same instruction (same PC)
  writes a different value.

Refuted if:

- the breakpoint never fires; or
- the shown record differs from the last written value.

## Part 2 (pre-registered; run only after Part 1)

**Forcing test.** At the fire that writes the record pointer:

1. step once;
2. load `0x002093D4` (record 6, never seen) into `0x060F249C` with `L`;
3. resume.

**Prediction:** record 6 is shown. The Part 1 runs are the controls. If the
pointer is only a copy, the original record appears and the forcing point moves
upstream to the code found in Part 1.

## Inputs

- Original image: `local/disc_images/mshvsf_saturn_jp`, identity per `DISC-010`.
- Checkpoint: slot 5, `EXP-0010` state A (`ab60af86089a9575…`, archived as
  `exp0010-slot5`): pre-KO, Ryu/Ken team.
- Stock Mednafen 1.32.1.
