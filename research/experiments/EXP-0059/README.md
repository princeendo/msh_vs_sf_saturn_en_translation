# EXP-0059: The American-name variant build

Task: LOC-003 (two name variants as parallel patch paths), with the `LOC-005`
voice switch
Status: DONE
Confidence: CONFIRMED (deterministic builds of both variants; the cold-booted
US image loads the American name calls); not yet heard in play (Akuma, Cyber
Akuma, character select)

## Observation

- The Saturn-name build (`m8_roster_gold`) applies `NAME_OVERRIDES`
  (VEGA, GOUKI) and `TEXT_OVERRIDES` (Akuma → Gouki, Cyber Akuma →
  Mech-Gouki) to the official arcade English.
- `EXP-0058`: the voice's name calls come from two tables in `MEMFIX.PAC`.
  Entries 20-22 hold the American calls.

## Hypothesis

One generator switch can produce both variants from the untouched source:
- the Saturn variant byte-identical to the current reference;
- the US variant differing only in names, name-related text, and the six
  name-call words.

## Controlled Change

`official_endings --names us`:
- no name or text overrides;
- six `MEMFIX.PAC` patches with original-byte checks (`US_VOICE_PATCHES`).

`--names saturn` is the default.

## Prediction

- The `saturn` spec hash equals the stored `m8_roster_gold` spec
  (`7ce7820a…`).
- The `us` build passes every compiler check and changes only patched bytes
  in `MEMFIX.PAC` and `MM.BIN`.
- After a cold boot of the US image, sound RAM table entries 14, 15 and 19
  read `0x004F`, `0x0338` and `0x005B`.

## Inputs and Provenance

- Source image `local/disc_images/mshvsf_saturn_jp/` (hashes in
  `references/mshvsf/saturn_jp/README.md`).
- `mshvsfu.zip` and `cps2.cpp`, as pinned in
  `data/regression/reference_builds.json`.

## Tools and Environment

- `tools/text/official_endings.py` (new `--names`), `caption_compiler`,
  `tools/regression/reference_builds.py`, `tools/disc/make_patch.py`
  (xdelta3 3.2.2).
- Patched Mednafen 1.32.1 agent interface for the cold boot.
- Python 3.12.13.

## Procedure

1. Generate both specs with the `m8_roster_gold` arguments, one with and one
   without `--names us`, and diff them.
2. Compile the US spec from the source image.
3. Add the reference `m8_roster_gold_us`, baseline it, and run all
   references with `--driver` (specs regenerated).
4. Make the release patch with `make_patch --reference m8_roster_gold_us`.
5. Cold boot each image without input for 2,700-4,200 frames. Every 300
   frames, read sound RAM name-call tables A (`0x73B6`, 10-byte records) and
   B (`0x74AC`, 16-byte records) at entries 14, 15, 19, 20, 21 and 22.

## Actual Result

- **Specs:** `saturn` = `7ce7820a…`, identical to the stored gold spec.
  `us` = `75e5f1bb…`. The diff:
  - name fields BISON and AKUMA, plus slot 14's name-length byte;
  - 14 text records: lines naming Akuma and Cyber Akuma, and a few lines
    re-centred by a half cell, because the generator picks centring offsets
    across all lines;
  - the six `MEMFIX.PAC` name-call words.
- **Compile:** every check is true. Only patched bytes changed: `MEMFIX.PAC`
  12 patched, 10 changed (beyond the font); `MM.BIN` 20 patched, 14 changed.
- **Regression:** 9 of 9 references pass with regenerated specs.
  `m8_roster_gold_us` track 01 is `e1337dbf…`.
- **Release patch:** `mshvsf_saturn_en_m8_gold_us.Track01.xdelta`, 155,248
  bytes, SHA-256 `82208a8c…`. Encoding is deterministic and the round trip
  passes. The record is `release/m8_roster_gold_us.json`.
- **Cold boot:**
  - The tables are loaded by frame 2463. On the US image, A and B entries
    14/15/19 read `0x004F`, `0x0338` and `0x005B`.
  - Control, the Saturn image: `0x0286`, `0x0048` and `0x0082`.
  - Entries 20-22 are `0x004F`/`0x0338`/`0x005B` on both images.

## Conclusion

- **CONFIRMED:** `--names` selects the variant. Both variants build
  deterministically from the untouched source, each with its own reference
  and patch. The US image loads the American name calls at boot. With
  `EXP-0058` (the table-A entry drives the win-screen call), the US build's
  win screen says "Bison" for that character.
- `LOC-003`'s acceptance criteria are met. The US variant stays a **preview**
  until the name art is replaced (`LOC-004`).

## Uncertainty and Alternatives

- Heard in play: nothing yet in the US build. "Akuma" and "Cyber Akuma" are
  inferred from the same table. Table B's role (perhaps character select)
  is unknown.
- The US text's few half-cell centring changes come from the generator's
  shared centring offsets, not from name edits. They are deterministic, and
  the regression reference covers them.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.json
```

The cold-boot table read was a scratch agent script: launch Mednafen on the
image's CUE, run `frames 300` repeatedly, and read `scspram` at `0x73B6` (230
bytes) and `0x74AC` (368 bytes).
