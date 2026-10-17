# EXP-0028: Ken's Win Quotes Through the Generalized Caption Pipeline (M4)

Task: `RE-030`
Date: 2026-10-17
Status: IN_PROGRESS (design; Phase A next)
Confidence: HYPOTHESIS

## Fighter Choice: Ken (`MC0A.PAC`)

Reasons, from M3 evidence:

1. **Ordinary data.** `MC0A.PAC` (LSN 8,492, 28,364 bytes, SHA-256
   `5f65706f…dab9`) holds one 16-record table, like Ryu's. Files with several or
   odd-sized tables (`MC00`, `MC02`, `MC07`, `MC08`, `MC0C`, `MC13`) are not
   ordinary and are excluded (`EXP-0023` census).
2. **Identity evidence.** Three independent observations tie `MC0A` to Ken:
   - the file index follows the name table: entry 9 = リュウ (Ryu) ↔ `MC09`;
     entry 10 = ケン (Ken);
   - the game's slot pointer list at WRAM-H `0x06094FD8` held `0x0021A59C` with
     Ken as Ryu's partner (`EXP-0025` V4), and `0x0020A59C` with Ken on point
     (`EXP-0027` V1). Both are a slot base plus decoded offset `0xA59C`, the start
     of `MC0A`'s table;
   - `MC0A` record 11/12 placeholders would name Ken's partner (testable).
3. **It breaks Ryu-specific assumptions** while staying ordinary (see below).
4. **Minimal gameplay.** One Ken + Ryu team covers both characters in one image
   and one session, with no reset.

Ken plays like Ryu, but that is irrelevant here: the test concerns his quote file,
whose layout differs.

## Ryu-Specific Assumptions Under Test

| ID | M3 assumption | Ken | Handling |
| --- | --- | --- | --- |
| A1 | Quote file `MC09` | `MC0A` (index 10) | Live: a Ken KO shows `MC0A` markers |
| A2 | Table at decoded `0x91AC` (hard-coded in `caption_compiler`, `quote_render`, `verify_records`) | **`0xA59C`** | Per-file table offset |
| A3 | 16 × 76-byte records | Same (census) | Verified live |
| A4 | Placeholder only in record 0, line 1 (cell 8) | **Records 11 (cell 26) and 12 (cell 25), on line 2**, each the last used cell | Compiler is already generic; the verifier's buffer model needs line 2 |
| A5 | — | Records 0, 1, and 13 are single-line (line 2 empty) | Markers keep them one-line, or fill line 2 (decided in Phase A) |
| A6 | One file per build; pair codes allocated for one table | Two files share **one** font | Compiler: multi-file spec with joint pair allocation |
| A7 | `MC09` re-encode fits (splice or full) | `MC0A` margins unknown | Same splice-then-full fallback, measured |
| A8 | Selection index `060AF282` and pointer routine | Expected shared | Forcing 16 Ken records |
| A9 | Slot-1 base `0x002091AC` | Ken on point → expected `0x0020A59C` | Base read from state |

**Correction found while planning.** The `EXP-0023` census reported `MC0A`'s
table at `0xA59A`. The table actually starts at **`0xA59C`**:

- the game's own pointer list points there;
- at `0xA59C`, record 0 starts with blank cells, unlike `0xA59A`.

The census scanner accepted a run shifted by one word. Census offsets are
therefore candidates, not table starts.

## Phase A (offline; no user action)

1. Generalize the tools:
   - **`caption_compiler`.** Schema `mshvsf-captions/2`: a list of
     `{file, table, records}`; v1 specs keep working. It allocates distinct
     pairs jointly across files into one font, patches every listed PAC, and
     builds the image with all replacements.
   - **`quote_render`, `verify_records`.**
     - per-file table offset;
     - the verifier identifies the compiled table by comparing WRAM-L at the
       state's base;
     - the placeholder model allows line 2.
   - Tests for each.
2. Write a marker spec covering both characters:
   - Ryu: unchanged;
   - Ken: `Ken record NN …` markers, with `{P}` at cells 26 and 25 in records 11
     and 12, and one-line records kept one-line.
3. Build twice and run all offline checks: only `MEMFIX.PAC`, `MC09.PAC`, and
   `MC0A.PAC` differ, 0 invalid sectors, and offline renders of 32 records.

## Phase B (live; minimal gameplay)

One cold boot of the Phase A image, with two captures armed in sequence. The user
picks **Ken first, Ryu second** in arcade mode:

- **Fight 1:** KO with **Ken**. This tests A1, A8, and A9.
- **Fight 2** (the next opponent, same session): tag in Ryu and KO with **Ryu**.
  This is the regression check in the shared font, with Ryu in slot 2.

Then, automatically: force records 0-15 from each fight's post-KO checkpoint, and
verify all 32 records.

## Predictions

- **Fight 1.**
  - A pointer into `MC0A`'s table at base `0x0020A59C`.
  - Forced Ken records 0-15 all verify: screen, cart font, WRAM-L table, and
    display buffer.
  - Records 11 and 12 show Ryu's name, リュウ (name entry 9), at their line-2
    placeholder.
- **Fight 2.** Ryu records 0-15 verify at base `0x002191AC` (as `EXP-0027` V1),
  with the shared font.

**Refuted if:**

- a Ken KO shows Ryu's markers, or text from another file;
- any record fails verification;
- the line-2 placeholder renders differently from the model (recorded as a
  variant).

## Gate

Markers only. No translation text; `GATE-TRANSLATION` still applies.
