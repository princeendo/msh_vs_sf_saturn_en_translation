# EXP-0006: Verify Mednafen Save/Load States

Task: `EMU-009`
Date: 2026-08-25
Status: DONE
Confidence: CONFIRMED

## Observation

EMU-005, EMU-007, and EMU-008 established the stock runtime, 4 MiB cartridge
configuration, required controller mapping, shortcut actions, and screenshot
workflow. A dedicated repeated save/load checkpoint record had not yet been made.

## Hypothesis

Stock Mednafen 1.32.1 will save a documented MSHvSF title/menu checkpoint, return
to a visibly changed mode-selection screen, and restore the title/menu checkpoint
with `F7`. The same sequence will work again after a cold launch using another
state slot.

## Controlled Change

The stock emulator, source image, BIOS files, and 4 MiB cartridge selection were
unchanged. The only runtime changes were save/load actions, two state-slot
selections, screenshots, and a temporary ignored keyboard mapping for Saturn Start.
The temporary mapping was needed because this host session had no usable way to
send the physical M30 button through automation; the original M30 mapping was
restored before the experiment ended:

```text
Original:  ss.input.port1.gamepad.start joystick 0xecccd365fc40db2f0006000c00010000 button_6
Temporary: ss.input.port1.gamepad.start keyboard 0x0 40
```

The temporary mapping was not used for save/load shortcuts. It was used only to
make the visible checkpoint change reproducible.

## Prediction

Each cold run will create one ignored state file in the configured `mcs` directory.
After Start advances from the title/menu scene, loading the saved state will return
to the title scene. Screenshot bytes may differ because the title background is
animated; scene identity and dimensions, not byte identity, are the comparison.

## Inputs and Provenance

- Source image: ignored `local/disc_images/mshvsf_saturn_jp/`.
- Source identity: the 13-component manifest in `references/mshvsf/saturn_jp/README.md`.
- Release description: locally supplied Marvel Super Heroes vs. Street Fighter
  (Japan) Saturn disc image; release identity as named, not independently verified.
- BIOS aliases: ignored `local/mednafen/firmware/sega_101.bin` and
  `local/mednafen/firmware/mpr-17933.bin`.
- Emulator: ignored `vendor/mednafen/build/src/mednafen`, stock Mednafen 1.32.1,
  SHA-256 `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.
- Japanese BIOS SHA-256: `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac`.
- North American/European BIOS SHA-256:
  `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f`.

## Tools and Environment

- Host: macOS 26.5.2, Darwin 25.5.0, arm64.
- Runtime root: `MEDNAFEN_HOME="$PWD/local/mednafen"`.
- Cartridge: Mednafen reported `Cart: 4MiB Extended RAM`.
- Software: Mednafen reported `T-1238G`, area `J`.
- Controller profile: 8BitDo M30 in wired macOS mode, restored after the run.
- Save-state directory: `local/mednafen/mcs/`.
- Screenshot directory: `local/mednafen/snaps/`.
- State filename template: `filesys.fname_state %f.%M%X`.
- Screenshot filename template: `filesys.fname_snap %f-%p.%x`.

## Procedure

1. Verify all 13 source-image components, the stock binary, and both BIOS aliases.
2. Confirm no Mednafen process or stale lock remains.
3. Launch the untouched source with the project-local runtime root.
4. Move the Mednafen window to visible coordinates when the host restores its
   previous off-screen position, focus it, and wait for the title/menu scene.
5. Select a state slot, press `F5`, and record the generated state filename, size,
   and SHA-256.
6. Capture the saved title scene with `F9`.
7. Send Saturn Start once, wait for the mode-selection screen, and capture it.
8. Press `F7`, capture immediately, and verify that the title scene with `PRESS
   START BUTTON` has returned.
9. Exit with `F12`, verify no process remains, and repeat steps 2 through 8 from a
   cold launch using the next state slot.
10. Restore the original M30 Start mapping and rerun the source identity command.

## Actual Result

The pre-run and post-run source identity commands reported the same 13 filenames,
sizes, and SHA-256 values as the manifest. All three run logs were 4,248 bytes with
SHA-256 `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c` and
identified `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`.

### Cold Run 1

The state was saved in slot 0:

| Artifact | Size | SHA-256 | Description |
| --- | ---: | --- | --- |
| `local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc0` | 3,173,150 bytes | `e54380cfca308b1058f92d2840bde73e4c13d01bd9e4b8c864be82a3730b66db` | Ignored Mednafen save state, slot 0 |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0008.png` | 3,332 bytes | `2a0b629ac9b2a6410ef9c62a1a9b2c6c06c1f608b863efd997061f1104f95290` | Saved title/menu checkpoint |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0010.png` | 21,380 bytes | `d01d1a311f092d704e43cae91468bf6af6673b18387a71bcebea8100fb49dea4` | Mode-selection screen after Start |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0011.png` | 24,616 bytes | `47e3d5eaade0f88d52aee28f6bbb69fdb95ef794a05b994cde066374f5c96b48` | Title/menu scene after `F7` |

The post-load capture showed the title scene again. The title background animation
changed its colors and artwork between captures, so the screenshot bytes differed.

### Cold Run 2

The state was saved in slot 1:

| Artifact | Size | SHA-256 | Description |
| --- | ---: | --- | --- |
| `local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc1` | 3,244,032 bytes | `88e8945770bf26667e9006aff476b4d5dab7f7eaef93fa471ceced343dc93d80` | Ignored Mednafen save state, slot 1 |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0012.png` | 18,847 bytes | `987a6da8844ba28f7901643435cf536fcc422ac3ff496ed185f09630d8c26a6e` | Saved title/menu checkpoint |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0015.png` | 24,114 bytes | `2d4772688b0c2477d0594d7b5909b2c8046dbddeb1bababc709f9443777ab07e` | Mode-selection screen after Start |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0017.png` | 19,145 bytes | `0d94b909bf94286ed7d960bc21171ec49ea843d161cba221ea6e656a61431310` | Title/menu scene after immediate `F7` capture |

The first post-load capture in this run was delayed approximately three seconds
and showed an attract-mode Spider-Man scene. An immediate capture after repeating
`F7` showed the saved title scene, establishing a timing caveat rather than a
load failure.

An earlier exploratory run saved while the emulator window was off-screen and
produced a black screenshot. Its state and screenshot are not used as evidence;
the corrected visible-window run overwrote slot 0 before the recorded cycle.

## Conclusion

`CONFIRMED`: stock Mednafen 1.32.1 can save and load the documented MSHvSF
title/menu checkpoint using the project-local `mcs` path. Two cold observations,
using slots 0 and 1, returned to the equivalent visible checkpoint after a known
mode-selection transition. The experiment does not claim byte-identical state
files, byte-identical screenshots, or RAM identity.

## Uncertainty and Alternatives

- Equivalent visible state does not imply byte-identical RAM or deterministic state
  file bytes; the two state files have different sizes and hashes.
- The title background and attract mode are time-dependent. Capture immediately
  after `F7` when the title scene itself is required.
- This session used a temporary keyboard Start mapping because automation could not
  generate the physical M30 Start event. The original M30 mapping was restored and
  save/load shortcuts remain the stock configured actions.
- Save-state binaries remain ignored and were hashed only for artifact identity;
  they were not decompressed or diffed as RAM.

## Reproduction

From the repository root, verify source identity before and after the run with:

```bash
./invenv.sh python -m tools.disc.hash_source \
  --description "EMU-009 source identity verification" \
  --json local/disc_images/mshvsf_saturn_jp/*
```

Launch with:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu009-run.log 2>&1
```

With the emulator window visible and focused, select a slot with `=` when needed,
press `F5`, capture with `F9`, advance with Saturn Start, load with `F7`, and
capture immediately. Verify retained ignored artifacts with `stat -f`, `file`, and
`shasum -a 256`. Do not treat `.mc0` or `.mc1` files as raw Saturn memory dumps.
