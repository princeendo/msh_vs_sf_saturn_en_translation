# EXP-0025: Identify Ryu's Win-Quote Selection Mechanism

Task: `RE-023`
Date: 2026-10-17
Status: IN_PROGRESS (Part 1 run; Part 2 pre-registered)
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

## Part 1 Result (2026-10-17)

Original image, process 87687, log `local/mednafen/logs/re023-exp0025-part1.log`.
Slot 5 (state A) was loaded and the opponent KO'd with Ryu.

- **Attempt 1.** The breakpoint stopped twice during the transition, on the
  Ryu/Ken win portraits before the text box appeared (F9 `-0058`, `-0059`,
  identical). F9 does not capture the debugger overlay, so no registers were
  recorded.
- **Attempt 2.** Halts were captured with macOS screenshots in `~/Downloads`
  (`Screenshot 2026-10-17 at 4.34.18 PM.png` `da79d4122eb04be1…`, `… 4.34.43 PM.png`
  `34a9b6ac378a8c94…`):

| Halt | PC | Instruction | R0 | R1 | Other |
| --- | --- | --- | --- | --- | --- |
| 1 | `060AF724` | `mov.w r0,@r1` | `00209290` | `060F249E` | R8 `00209290`, MACL `000000E4`, R11 `060F8000`, R12 `060F9E16` |
| 2 | `060AF728` | `mov.w r0,@-r1` | `00000020` | `060F249E` | same |

The halts show the instruction about to store (halt 2's R0 already holds the
result of `shlr16` at `060AF726`). So a Mednafen write breakpoint stops **before**
the store executes.

The quote itself was not captured. After the second `R`, the game runs while the
debugger is open, and the user was still clearing the breakpoint when the quote
passed. The written value, `0x00209290`, is record **3** (Q8).

### Code that forms the pointer

Disassembled offline from the `exp0023c-slot7` WRAM-H extraction, entry
`060AF6E0`:

```text
060AF6E0  r6 = 0x060ED800, r7 = 0x060ED900     ; screen buffer
060AF6E4  @(0,gbr).l = 0
060AF6E8  @(2,gbr).w = @(r12 + 80).w            ; record index
060AF6EE  r8 = @(r12 + 52).l                    ; table base (0x002091AC)
060AF6FC  stride = 76, or 100 if @(r11 + 0xCC8E).w != 0
060AF712  @(0,gbr).l = index * stride           ; mulu.w
060AF71C  r8 += low word
060AF720  @(r11 - 0x5B62) = r8                  ; 0x060F249C (two word stores)
```

- With `r12 = 0x060F9E16`, the index word is **`0x060F9E66`** and the table
  pointer is `0x060F9E4A`. The latter holds `0x002091AC`, the same data hit seen
  in the two-state search.
- `0x060F9E66` is among the two-state index-word hits (4 vs 5).
- The alternate stride of **100** (2 × 25 cells × 2 bytes) matches the alternate
  25-cell layout set. That supports the latent alternate text mode
  (`HYPOTHESIS`).
- A setter at `060AF6B8-060AF6DC` writes `@(2,gbr)` to `@(r7 + 80)`, with `r7`
  loaded from `0x060F2498`. That is a candidate writer of the index. The source
  of its `@(2,gbr)` (random or otherwise) is not yet traced.

**H (Part 1): `SUPPORTED`.** One routine stores `table + 76·index` to
`0x060F249C` during the transition, with the index read from `0x060F9E66`. The
written value has not yet been compared with a captured quote.

## Part 2 (revised before the run): forcing the index

**Single change:** write index 6 (`0x0006`, file `local/mednafen/dumps/i6.bin`,
SHA-256 `40d88127…a3fd`) to `0x060F9E66` after every store to that word during
the transition. The procedure:

- step once (`S`), because the breakpoint stops before the store;
- `L` the file into High Work RAM `000F9E66-000F9E67`;
- verify with `D`.

Breakpoints: `060F9E66-060F9E67 260F9E66-260F9E67 060F249C-060F249F
260F249C-260F249F`. Halts at `060AF724`/`060AF728` are only captured, not
changed. The breakpoints stay set until the quote is saved, so no typing happens
while the quote is on screen.

**Prediction:**

- the halt at `060AF724` shows R0 = `0x002093D4` (`0x002091AC + 6·76`);
- the quote shown is record 6, never seen in any earlier run;
- saved-state WRAM-H holds `0x060F249C = 002093D4` and `0x060F9E66 = 0006`;
- `quote_render --match` picks record 6.

**Refuted if:** R0 is not `0x002093D4`, or another record is shown. That would
mean the index is re-read or re-written after the forcing point.

## Part 2 Attempt 1 (2026-10-17): aborted

With breakpoints on the index word and the pointer, the index word `0x060F9E66`
halted in **structure-initialization loops** before the pointer store. From the
user's macOS screenshots:

- **PC `060490EC`** (`mov.w r0,@r10`, R10 `060F9E66`): a word-clearing loop
  (`060490E6` ×11) during the post-fight VITAL/TIME/BONUS tally.
- **PC `06047CCA`** (`mov.w r0,@r10`, R10 `060F9E66`): a fill loop
  (`06047CC4` ×5) over the same structure on the win-pose screen.

The "force at every non-pointer halt" rule therefore meant many manual
step/load cycles, and the user could not tell which write was final. Whether
`i6.bin` was ever loaded at the right offset is unknown, because the memory-editor
screenshot shows position `0x00000`. The run was abandoned with no result.

Lessons:

- several routines write the index word;
- forcing must target the last writer, the setter at `060AF6DA` (to be confirmed)
  or the pointer itself;
- manual debugger work at this granularity is not practical. See `EMU-012` /
  `EMU-020`.
