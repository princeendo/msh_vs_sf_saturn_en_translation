# EXP-0099: "CHOUHATU" reads "TAUNT" on the button-config screen

Task: UI-007
Status: DONE
Confidence: CONFIRMED (the built bytes are shown on the Saturn screen)

## Observation

- The button-config screen offers the romanised Japanese "CHOUHATU" (taunt)
  as a button function (`EXP-0097`, user, 2026-10-28).
- The user asked for "TAUNT".

## Hypothesis

The word is plain ASCII in `MM.BIN`, which is resident in WRAM-H at
`0x06018B00`. A same-length edit of each field changes the screen, with no
code change.

## Controlled Change

- `MM.BIN` holds the word in four 9-byte fields, each after two position
  bytes and before a 0 terminator:

  | Offset | Original | Use |
  | --- | --- | --- |
  | `0x69EE` | " CHOUHATU" | left column (prefix `07 07`) |
  | `0x6A42` | " CHOUHATU" | left column, highlighted (`07 09`) |
  | `0x6ACE` | "CHOUHATU " | right column (`1C 07`) |
  | `0x6B22` | "CHOUHATU " | right column, highlighted (`1C 09`) |

  Each becomes "  TAUNT  ", centred in the same 9 characters.
- `official_endings --ui-english` adds four patches (`taunt_patches`), each
  checked against the original bytes.
- Unit test: `test_taunt_patches_replace_each_chouhatu_field_in_place`.

## Procedure and Actual Result

1. **RAM trial on the US release image**, from the user's `EXP-0097` state
   on the button-config screen (`f8452`):
   - with "  TAUNT  " written to the first field only, the screen did not
     change (`a0e1b094…`). It was drawn already;
   - with all four fields written and the L-button value (`0x06017AE0`) set
     to 0, the screen redraws: L-BUTTON and R-BUTTON both read "TAUNT"
     (`3760963a…`).
2. **Rebuilt:** both release references with the reason "EXP-0099: the
   button-config screen's CHOUHATU reads TAUNT (UI-007, --ui-english)". Nine
   of nine pass.
   - Specs: Saturn names `86178579…`, American names `b89d4679…`.
   - Track 01: `cdf366b3…`, `c6f1fbd0…`.
   - Patches: `c7b18d55…`, `b252e40e…`; `.ssp` `f827caa4…`, `a021dafc…`.
3. **Built bytes on the Saturn:** the four fields read from the new American-
   names image (all "  TAUNT  ") were written to RAM in the same trial, and
   the screen shows TAUNT in both columns (`built_trial_f60.png`, `3760963a…`, identical to step 1, as the bytes are the same).

## Conclusion

**CONFIRMED:** the four `MM.BIN` fields are the word's only source on the
screen, and the release now shows "TAUNT".

## Uncertainty and Alternatives

- **Cold boot:** seen since in `EXP-0100`. The screen there showed TAUNT
  straight from the disc.

## Reproduction

```bash
./invenv.sh python -m tools.mednafen.write_trial \
  "build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/loc006/play/rec/states/f00008452.mcs local/ui007/built_trial.png --frames 120 --shot-at 60 \
  --write workramh:1F4EE:20205441554e542020 --write workramh:1F542:20205441554e542020 \
  --write workramh:1F5CE:20205441554e542020 --write workramh:1F622:20205441554e542020 \
  --write workramh:17AE0:00000000
```
