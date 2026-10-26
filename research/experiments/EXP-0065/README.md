# EXP-0065: Life-bar label records (full-width AKUMA, both player sides)

Task: LOC-004 (the AKUMA life-bar width)
Status: DONE
Confidence: CONFIRMED (replay trials on both sides; cold-boot RAM)

## Observation

`EXP-0060` copied the US label art into the cells the HUD draws for GOUKI.
AKUMA is 50 px wide, so its last 2 px were clipped. The italic label set and
the first MECH-GOUKI copy were never seen drawn and were left alone.

## Hypothesis

Like the win banner and the VS screen (`EXP-0062`, `EXP-0063`), the life-bar
labels are `MM.BIN` records of sprite patterns, indexed by character. The US
records give each label its own width.

## Controlled Change

Trial 1: one 16-byte write in WRAM-H. The player-1 GOUKI record
(`0x0604B894`) gets the AKUMA record. Then a control replay without it.
Trial 2: one 16-byte write to the player-2 Mech-Gouki record (`0x0604BAA4`),
setting the italic BISON record.

## Prediction

- Trial 1: the player-1 label reads AKUMA with the last A's foot whole.
- Trial 2: the player-2 label reads italic BISON, right-aligned.

## Inputs and Provenance

- `MM.BIN` from source track 01.
- Play-test state `local/playtest_us/rec/states/f00004857.mcs` (`EXP-0064`,
  US build, Gouki point vs the boss), replayed 323 frames into the fight on the
  US image.

## Tools and Environment

Patched Mednafen 1.32.1 agent with scratch scripts for the write and
screenshot, and the cold-boot poll. Python 3.12.13.

## Procedure

1. Search `MM.BIN` for the patterns `0x5000 + code` of the drawn labels
   (`0x5760`-`0x5762`, `0x5750`-`0x5752`, `0x5568`…): `0x32D84`, `0x32D94`
   and `0x32FA8`. Dump `0x32C80`-`0x33040` in 16-byte rows.
2. Map the tables by character index i (8 patterns per record, `0x5020`
   blank):
   - player 1 at `0x32CA4 + 16i`: bold, left-aligned;
   - player 2 at `0x32E74 + 16i`: italic, right-aligned.

   Index 14 is VEGA, 15 GOUKI, 19 MECH-GOUKI (P1 `0x562`-`0x567`, P2
   `0x568`-`0x56D`). The US records are 26 **AKUMA** (P1 `0x753`-`0x756`,
   4 cells), 27 BISON and 28 CYBER-AKUMA (P1 `0x5D2`-`0x5D8`, P2
   `0x5D9`-`0x5DE`).
3. Run trials 1 and 2 and the control. Zoom the HUD.
4. Implement `US_LABEL_RECORDS`: six 16-byte `MM.BIN` copies (26→15, 27→14,
   28→19 in both tables), with expect checks. Drop the `EXP-0060` glyph
   copies.
5. Build, re-baseline, run all references, remake the patch, and poll the
   records after a cold boot.

## Actual Result

- **Trial 1:** AKUMA is drawn over 4 cells with the final A's foot whole
  (`local/loc004/akuma4_zoom.png`). The control (`akuma3_zoom.png`) is
  clipped.
- **Trial 2:** the player-2 label reads italic **BISON**, right-aligned
  (`p2_trial_zoom.png`). The player-2 table is real and was previously
  unswitched: a CPU Vega or Gouki on the right would have shown VEGA or GOUKI.
- **Build:**
  - The Saturn spec is unchanged (`7ce7820a…`). US spec `2840b15b…`.
  - `MM.BIN`: 197 patched bytes, 72 changed, all checks true.
  - The label cells (`0x560`-`0x5DF`, `0x740`-`0x7FF`) now equal the source
    font.
  - 9 of 9 references pass. US track 01 `87d1daec…`; patch `644d04eb…`,
    156,462 bytes.
- **Cold boot:** by frame 1650 the US image holds `5763 5764…` (BISON),
  `5753 5754 5755 5756` (AKUMA), `…57c3 57c4` (P2 BISON) and `…55dd 55de`
  (P2 CYBER-AKUMA) at the record addresses.

## Conclusion

**CONFIRMED:** the life-bar labels come from per-character records in
`MM.BIN`, one table per player side. The US variant copies the disc's own US
records. That gives AKUMA its full 4-cell width and also switches the
player-2 labels. This replaces the `EXP-0060` glyph copies, and the font is
no longer touched for names.

## Uncertainty and Alternatives

The full-width AKUMA and the player-2 labels were seen in replays with RAM
writes, plus the cold-boot RAM read. They were not seen in a cold-boot
play-through.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold_us
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.json
```
