# EXP-0004: Validate M30 In-Game Controls and Mednafen Shortcuts

Task: `EMU-007`
Date: 2026-08-25
Status: DONE
Confidence: SUPPORTED

## Observation

`EMU-006` confirmed that the ignored local Mednafen profile parses and enumerates
the 8BitDo M30 in wired macOS mode as the SDL `PS4 Controller`. It configured the
required Saturn controls, but no in-game action or emulator shortcut has yet been
observed.

## Hypothesis

The configured M30 bindings operate the intended MSHvSF Saturn controls in-game,
and the selected stock Mednafen build performs the configured screenshot, pause,
frame-advance, save/load-state, and save-slot actions.

## Controlled Change

Only runtime input actions, one host-specific ignored shortcut binding, and ignored
runtime evidence change. The stock Mednafen binary, source image, BIOS files, and
M30 bindings remain unchanged. Because the Mac keyboard lacks a reliable Pause key,
the local profile is being tested with an unused `F4` binding. An initial `F1`
attempt conflicted with Mednafen's help action and is recorded as a failed binding
attempt.

## Prediction

Each required M30 control will produce its expected visible or gameplay effect. Each
available shortcut will produce its documented effect and any expected runtime
artifact. An unavailable or unreliable action will remain explicitly recorded as
unverified rather than being inferred from configuration labels.

## Inputs and Provenance

- Source image: ignored `local/disc_images/mshvsf_saturn_jp/`.
- Source identity: 13-component manifest in
  `references/mshvsf/saturn_jp/README.md`.
- Release description: locally supplied Marvel Super Heroes vs. Street Fighter
  (Japan) Saturn disc image; release identity as named, not independently verified.
- BIOS aliases: ignored `local/mednafen/firmware/sega_101.bin` and
  `local/mednafen/firmware/mpr-17933.bin`; hashes are recorded in
  `docs/mednafen.md`.
- Emulator: ignored `vendor/mednafen/build/src/mednafen`, stock Mednafen 1.32.1;
  SHA-256 `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.

## Tools and Environment

- Host: macOS 26.5.2, Darwin 25.5.0, arm64.
- Runtime root: `MEDNAFEN_HOME="$PWD/local/mednafen"`.
- Controller: 8BitDo M30, wired macOS mode, SDL identity `PS4 Controller`.
- Joystick ID: `0xecccd365fc40db2f0006000c00010000`.
- Existing runtime warnings: unsupported CUE `CATALOG` directive and absent
  adjacent `.sbi`; neither input is changed.

## Required M30 Controls

| Saturn control | Configured SDL input | Expected observation | Actual observation |
| --- | --- | --- | --- |
| D-pad up | Hat-compatible button 12 | Navigate/ move upward | User confirmed expected in-game response |
| D-pad right | Hat-compatible button 13 | Navigate/ move right | User confirmed expected in-game response |
| D-pad down | Hat-compatible button 14 | Navigate/ move downward | User confirmed expected in-game response |
| D-pad left | Hat-compatible button 15 | Navigate/ move left | User confirmed expected in-game response |
| A | Button 0 | Trigger mapped game action | User confirmed expected in-game response |
| B | Button 1 | Trigger mapped game action | User confirmed expected in-game response |
| X | Button 2 | Trigger mapped game action | User confirmed expected in-game response |
| Y | Button 3 | Trigger mapped game action | User confirmed expected in-game response |
| Z | Button 4 | Trigger mapped game action | User confirmed expected in-game response |
| C | Button 5 | Trigger mapped game action | User confirmed expected in-game response |
| Start | Button 9 | Start/confirm or pause gameplay menu | User confirmed expected in-game response |

L/R and retained keyboard fallbacks are out of scope for this experiment, following
the EMU-006 scope decision.

## Shortcut Validation

The current generated profile names these actions: `take_snapshot`, `pause`,
`advance_frame`, `run_normal`, `save_state`, `load_state`, `state_slot_dec`, and
`state_slot_inc`. For this Mac host, `pause` is temporarily bound to `F4` in the
ignored local profile. The observed result will be recorded after testing rather
than inferred from generated numeric key codes.

| Action | Expected evidence | Actual result |
| --- | --- | --- |
| Screenshot (`F9`) | New ignored image with size and SHA-256 | User confirmed action works; no new file remained under `local/mednafen/snaps/` |
| Pause/unpause | Visible emulation freeze and resume | `UNKNOWN`: default Pause/Break has no reliable Mac key; `F1` opened help and temporary `F4` produced no pause |
| Frame advance (`Option/Alt+A`, `Option/Alt+R`) | One-frame progression while paused, then normal execution | User confirmed shortcut behavior; pause-coupled frame evidence remains limited by unavailable pause input |
| Save state (`F5`) | New ignored state file | User confirmed action works; no new file remained under `local/mednafen/mcs/` |
| Load state (`F7`) | Return to the saved visible checkpoint after a change | User confirmed action works |
| Slot selection (`-`, `=`) | Selected slot changes and is used by save/load | User confirmed action works |

## Procedure

1. Verify all source-image components, the stock binary, and the canonical BIOS
   aliases before launch.
2. Confirm the M30 is connected in wired macOS mode and the Mednafen window is
   focused.
3. Launch the untouched source with the project-local runtime root and redirect
   output to `local/mednafen/logs/emu007-validation.log`.
4. Reach the title/menu endpoint using Start and then enter an ordinary playable
   mode. Test each required M30 control individually, recording the visible or
   gameplay result and avoiding L/R.
5. Capture a baseline screenshot, pause and resume, pause again, advance one frame,
   return to normal execution, and capture the relevant result.
6. Select a state slot, save at a documented visible checkpoint, make a visible
   change using the M30, load the state, and verify the checkpoint returns. Repeat
   with a second slot if the slot-selection action is available.
7. Exit cleanly, verify no Mednafen process or stale lock remains, and hash all
   retained ignored evidence.
8. Re-run the source identity command and compare every component with the tracked
   manifest.

## Actual Result

The pre-run source identity command reported all 13 manifest components with the
recorded sizes and SHA-256 values. The stock binary and canonical BIOS aliases also
matched their recorded hashes. The retained runtime log is:

| Artifact | Size | SHA-256 | Description |
| --- | ---: | --- | --- |
| `local/mednafen/logs/emu007-validation.log` | 4248 bytes | `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c` | M30-enumerated MSHvSF runtime log |

The log records the expected M30 joystick identity, software `T-1238G`, area `J`,
and `Cart: 4MiB Extended RAM`. The user reported the expected in-game behavior for
all required M30 controls and successful use of every tested shortcut other than
pause. No new screenshot or save-state file remained in the configured `snaps/` or
`mcs/` directories after the run, so those binary artifacts have no tracked hash
metadata from this experiment.

The generated profile's default pause binding is SDL `Pause` scancode 72. A
temporary ignored `F1` binding conflicted with Mednafen help; a temporary ignored
`F4` binding produced no pause response. The generated profile was left with its
original Pause binding after the run.

## Conclusion

`SUPPORTED`: the configured physical M30 mapping produced the user-observed expected
in-game behavior for every required control, and the available tested shortcuts were
usable. Pause/unpause remains `UNKNOWN` on this Mac host because no reliable physical
Pause/Break input was available. This task does not establish save-state byte
identity, and it does not replace the repeated checkpoint requirements of EMU-009.

## Uncertainty and Alternatives

The user-observed control results are from one interactive validation session. The
runtime log proves the selected binary, target, and joystick enumeration, but does
not encode individual button transitions. Screenshot and state files were not
retained by this run. Pause availability may differ with an external keyboard that
provides a physical Pause/Break key.

## Reproduction

From the repository root, verify the source before and after the run with:

```bash
./invenv.sh python -m tools.disc.hash_source \
  --description "EMU-007 source identity verification" \
  --json local/disc_images/mshvsf_saturn_jp/*
```

Launch with:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu007-validation.log 2>&1
```

With the M30 connected in wired macOS mode, repeat the required control and shortcut
observations recorded above. Runtime logs, screenshots, save states, source images,
BIOS files, and emulator binaries remain under ignored paths; this record stores only
permitted metadata and hashes.
