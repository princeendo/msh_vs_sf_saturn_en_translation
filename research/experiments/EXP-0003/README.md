# EXP-0003: M30 Mednafen Input Mapping

Task: `EMU-006`

Date: 2026-08-25

## Goal

Configure the identified 8BitDo M30 for Saturn port 1 without modifying the stock
Mednafen binary or any source-image component.

## Observation

The physical M30 in wired macOS mode presents to SDL as `PS4 Controller`. SDL reports
six axes, twelve buttons, and one hat. Mednafen records joystick ID
`0xecccd365fc40db2f0006000c00010000`.

## Hypothesis

The M30's macOS/PS4 presentation can be mapped to the Saturn Digital Gamepad using
the SDL button and hat-compatible indices exposed by the stock Mednafen SDL backend.

## Controlled Change

Only the ignored local Mednafen profile changed. The stock binary, source image, BIOS,
and emulator source remained unchanged. Keyboard bindings were retained as fallbacks.

## Prediction

The selected profile will parse, Mednafen will enumerate the M30 joystick, and port 1
will use the configured digital-gamepad controls.

## Result

The profile loaded with `7904 valid settings and 0 unknown settings`. The target launch
logged:

```text
Initializing joysticks...
 ID: 0xecccd365fc40db2f0006000c00010000 - PS4 Controller
Cart: 4MiB Extended RAM
```

The retained ignored log is `local/mednafen/logs/emu006-mapping-run.log`, 4,248 bytes,
SHA-256 `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c`.

## Conclusion

`CONFIRMED` for profile parsing and joystick enumeration. The required Saturn controls
are configured as D-pad hat-compatible buttons 12/13/14/15, A/B/X/Y as buttons 0/1/2/3,
Z/C as buttons 4/5, and Start as button 9. L/R are out of scope for EMU-006 because
the tested Mednafen device models did not expose usable bindings and the checkpoint
work does not require them.

## Uncertainty

EMU-007 must still record in-game expected-versus-observed controls and emulator
shortcut behavior. The SDL button numbering is based on the M30's documented macOS
PS4-compatible presentation and the selected Mednafen SDL device identity.

## Reproduction

From the repository root, with the M30 connected in wired macOS mode:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu006-mapping-run.log 2>&1
```

Verify the log contains the recorded joystick ID and `Cart: 4MiB Extended RAM`.
