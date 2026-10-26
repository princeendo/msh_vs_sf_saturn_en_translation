# EXP-0061: US names in the sound test and the title-menu unlock message

Task: LOC-004 (part 2: menu and sound-test text)
Status: DONE
Confidence: CONFIRMED (the strings the program loads at boot and the pointers
that read them); not seen on screen

## Observation

`EXP-0054`: `MM.BIN` holds the sound-test titles "18.VEGA" (`0x6341`) and
"22.GOUKI" (`0x639D`), and the title-menu message " MECH-GOUKI NOW!!"
(`0x24F03`).

## Hypothesis

Same-length ASCII edits in `MM.BIN` show the US names, with no code change,
provided the program reads each string from the start of its slot.

## Controlled Change

`official_endings --names us` adds three `MM.BIN` patches with expect checks
(`US_STRINGS`):

| Offset | Saturn | US |
| --- | --- | --- |
| `0x6341` | `18.VEGA` + 13 spaces (20-character field) | `18.BISON` + 12 spaces |
| `0x639D` | `22.GOUKI` + 12 spaces | `22.AKUMA` + 12 spaces |
| `0x24F03` | ` MECH-GOUKI NOW!!` (17 characters, then NUL) | `CYBER-AKUMA NOW!!` (17) |

## Prediction

- The US image's program in RAM holds the new strings where the Saturn image
  holds the old ones.
- The program's pointers point at the slot starts.

## Inputs and Provenance

- Source `MM.BIN` from track 01.
- `build/regression/m8_roster_gold_us` and `m8_roster_gold` images.

## Tools and Environment

- `official_endings`, `caption_compiler`, `reference_builds`, `make_patch`
  (xdelta3 3.2.2).
- Patched Mednafen 1.32.1 agent (cold boot, then read `workramh` and
  `workraml`).

## Procedure

1. Search the ASCII text of `MM.BIN`, `ME.PAC`, `ME.SHX`, `MEMFIX.PAC`,
   `SEL*.PAC` and `MC13.PAC` (raw and LZSS) for the regional names.
2. Add the edits, build, re-baseline `m8_roster_gold_us`, run all
   references, and remake the patch.
3. Cold boot each image for 2,700 frames. Search work RAM for old and new
   strings.
4. Find pointers to the strings in `MM.BIN`, assuming the measured load
   address `0x06018B00`.

## Actual Result

- **Search:**
  - `MM.BIN` has only the three strings.
  - `ME.SHX` holds the speaker table too. `ME.PAC` is `ME.SHX` inside a
    16-byte container header (`0`, `0xED02`). Its payload is what loads at
    WRAM-L `0x230000`, so the `EXP-0060` `ME.PAC` speaker edits are the ones
    the game reads.
- **Build:**
  - The Saturn spec is unchanged (`7ce7820a…`). The US spec is
    `8f0b63de…`.
  - `MM.BIN`: 77 patched bytes, 32 changed, nothing outside the patches.
  - All 9 references pass. US track 01 is `fbb64910…`.
  - Patch `65275636…`, 155,842 bytes, with a passing round trip.
- **Cold boot:**
  - US image: "18.BISON" at `0x0601EE41`, "22.AKUMA" at `0x0601EE9D`,
    "CYBER-AKUMA NOW!!" at `0x0603DA03`; no old strings.
  - Saturn image: the old strings at the same addresses.
- **Pointers:**
  - The title-menu lists (`MM.BIN` `0x24DC4`, `0x24EB0`) point at
    `0x0603DA03`, the slot start, so the full new string is drawn.
  - The sound-test list (`0x6140`) points at `0x0601EE3F`, two control bytes
    before "18.", so the field layout is unchanged.

## Conclusion

**CONFIRMED:** the US variant's program holds "18.BISON", "22.AKUMA" and
"CYBER-AKUMA NOW!!", read from the same slots.

## Uncertainty and Alternatives

- Not seen on screen. The sound test needs menu input, and the message needs
  the unlock. The agent has no input.
- The unlock message loses its centring space. It is one character wider, as
  wide as the other 17-character item (" SURVIVAL MODE  ").

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold_us
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.json
```

The cold-boot string search was a scratch agent script: launch Mednafen on
the CUE, `frames 2700`, read `workramh` and `workraml` (1 MiB each), and
search for the strings.
