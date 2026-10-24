# EXP-0028: Ken's Win Quotes Through the Generalized Caption Pipeline (M4)

Task: `RE-030`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

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

## Phase A Result (2026-10-23, offline)

### Tooling

- **`tools/text/caption_compiler.py`** accepts schema `mshvsf-captions/2`: a
  list of `{file, table, records}`, in `data/captions/caption_spec.schema.json`.
  - It allocates distinct pairs **jointly** into one font, patches every listed
    PAC (splice, with full re-encode as fallback), and builds and verifies the
    image with all replacements.
  - It writes one offline render per table (`records-<file>.png`).
  - v1 specs still work: rebuilding `ryu_markers.json` reproduces the `RE-022`
    `MEMFIX.PAC` and `MC09.PAC` byte for byte.
- **`tools/text/quote_render.py`** takes `--table` (decoded offset) for
  rendering, matching, and summaries.
- **`tools/mednafen/verify_records.py`**:
  - it reads every compiled table from the manifest, and checks each capture
    against the table that WRAM-L holds at the state's base (reported as
    `table_file`);
  - the buffer model handles a placeholder on either line.
  Regression: all 51 earlier captures (`EXP-0026`, `EXP-0027` V1/V2) still
  pass, each identified as `MC09.PAC`.
- **Tests:** v1/v2 parsing, joint pair allocation across two files, a line-2
  placeholder, a one-line record, and the line-2 buffer model. 137 tests pass;
  ruff and strict mypy are clean.

### Marker spec and build

`data/captions/ryu_ken_markers.json` (`c6d7118e210daf05…`):

- **Ryu:** the `RE-022` markers.
- **Ken:** line 1 `Ken record NN line one`.
  - Line 2 is `NN Ken line two fills all cells to 19!` (38 characters).
  - Records 0, 1, and 13 stay one-line.
  - Record 11's line 2 is `11 Ken partner{P}` (placeholder at cell 26), and
    record 12's is `12 Ken buddy{P}` (cell 25), at the original placeholder
    cells.

```bash
./invenv.sh python -m tools.text.caption_compiler data/captions/ryu_ken_markers.json --out-dir build/exp0028a
```

| Item | Result |
| --- | --- |
| Pairs | 66 distinct at `0x00A8-0x00E9`, 2,653 bytes; 27 unseen kanji sacrificed (2,716 bytes freed); font zero-fill 63 |
| `MEMFIX.PAC` | `1d3b0de497f3836f…` |
| `MC09.PAC` | `e3582deba0bef84e…`, **identical to `RE-022`** (Ryu's pairs are allocated first, in the same order); splice; 456 fill |
| `MC0A.PAC` | `fe7d468b04bd4fbf…`; splice from stream byte 23,505; 418 fill bytes; 876 decoded bytes changed, all in target cells |
| Font check | header unchanged; only pair and sacrificed codes changed; pairs equal composed cells |
| Image | builds A and B identical; track 01 `c3990fa568dbbd6d…76de`; 414 files, only `MEMFIX`, `MC09`, and `MC0A` differ; 0 bad sync, mode, or address; **0 invalid EDC/ECC**; 109 changed sectors (LSN 4166-8505) |
| Determinism | a `--files-only` rerun is byte-identical for all three files |
| Renders | `records-MC09.png`, `records-MC0A.png` (ignored): all 32 records legible; Ken's one-line records and line-2 placeholders as designed |

Manifest: `build/exp0028a/compile_manifest.json` (`620f7fc6b4d53fb6…`).

**Phase A: done.** All offline predictions held. Phase B (live) needs one
session: team **Ken first, Ryu second**. Fight 1: KO with Ken. Fight 2: tag in
Ryu and KO with Ryu.

## Resume: Phase B (on hold since 2026-10-23, at the user's request)

Phase B is the only open step of `RE-030`. Everything it needs is committed or
reproducible.

1. **Rebuild the image if `build/` was cleaned** (ignored, deterministic; expect
   track 01 `c3990fa5…`):

   ```bash
   ./invenv.sh python -m tools.text.caption_compiler data/captions/ryu_ken_markers.json --out-dir build/exp0028a
   ```

2. **Rebuild the patched Mednafen if needed:** see `vendor/mednafen/README.md`
   (patch `0001-agent-interface.patch`; expect binary `fe0edb99…`).
3. **Launch with the agent enabled** (background):

   ```bash
   MEDNAFEN_HOME="$PWD/local/mednafen" MEDNAFEN_AGENT_DIR="$PWD/local/mednafen/agent" \
     vendor/mednafen/build-agent/src/mednafen "build/exp0028a/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
   ```

4. **Arm two captures in sequence** (background), before the user plays:

   ```bash
   R=local/mednafen/agent/runs
   ./invenv.sh python -m tools.mednafen.ko_capture --out-dir $R/exp0028-ken --checkpoint --timeout 2400
   ./invenv.sh python -m tools.mednafen.ko_capture --out-dir $R/exp0028-ryu --checkpoint --timeout 2400
   ```

5. **User gameplay** (one session, no reset, no F-keys): arcade mode, pick **Ken
   first, Ryu second**.
   - **Fight 1:** KO with **Ken**.
   - **Fight 2:** the next opponent; tag in Ryu and KO with **Ryu**.
6. **Force and verify, automatically**, for each of `exp0028-ken` and
   `exp0028-ryu`:
   - for i in 0-15: `ko_capture --state <run>/postko.mc --out-dir <run>-rNN
     --force-index i --setter-pcs 060AF282`;
   - then `verify_records --compile-dir build/exp0028a <run>-r?? <run>`.
   - Expect `table_file` `MC0A.PAC` with base `0x0020A59C` for Ken, and
     `MC09.PAC` with base `0x002191AC` for Ryu.
7. Record the results against this file's predictions. Then update `TASKS.md`
   (`RE-030`, M4), `docs/discoveries.md`, and `research_log.md`.

## Phase B Result (2026-10-24, live)

- **Setup.**
  - Patched Mednafen `fe0edb99…` on `build/exp0028a/image_a`. Track 01 is
    `c3990fa5…`; a fresh rebuild today was byte-identical after the TR-001 code
    changes.
  - Two `ko_capture.py --checkpoint` runs were armed in sequence, with an agent
    `run` between them.
- **Session.** One user session: Ken first, Ryu second.
  - **Fight 1 (Ken KO).** Pointer `0x0020A894` = `0x0020A59C` + 76 × 10, with
    table base `0x0020A59C` (`MC0A`, slot 1). The natural pick was record 10.
    `postko.mc` SHA-256 `f9bb8ef4…2c7c`; the screen shows "Ken record 10" with
    Ken's portrait on the left.
  - **Fight 2 (Ryu KO, second member).** Pointer `0x002194F0` = `0x002191AC` +
    76 × 11, with table base `0x002191AC` (`MC09`, slot 2). The natural pick was
    record 11. `postko.mc` SHA-256 `88576318…b24d`.
- **Forced records.** All 16 records of each fighter were forced
  (`--force-index i --setter-pcs 060AF282`).
- **Verification.** `verify_records.py --compile-dir build/exp0028a` gives **34 of
  34 OK** (32 forced plus 2 natural; report SHA-256 `24e29eed…25f5`). For every
  run:
  - the pointer is correct;
  - the table file is chosen by RAM content (`MC0A` for Ken, `MC09` for Ryu);
  - the shared cart-RAM font matches;
  - the WRAM-L table and display buffer match;
  - the screen match picks the forced record (IoU at least 0.92; margins down to
    0.008, because the markers differ by digits).
- **Placeholders.** Ken's records 11 and 12 expand to name entry 9 (リュウ) after
  "Ken partner" and "Ken buddy". Ryu's record 0 expands to entry 10 (ケン). Both
  are as predicted.
- **Visual check.** All 32 screenshots were read and match their markers. Ken's
  records 0, 1, and 13 are one-line by design (the spec keeps the original
  single-line layout).

### Conclusion

**CONFIRMED.** The generalized mechanism works for a second ordinary fighter:
- several tables in one image, with a shared pair font;
- a per-file table offset;
- slot-dependent table bases;
- line-2 placeholders;
- one-line records.

All predictions held. `RE-030` and milestone M4 are complete.

