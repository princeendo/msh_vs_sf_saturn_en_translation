# EXP-0005: Verify Mednafen Screenshot Capture

Task: `EMU-008`
Date: 2026-08-25
Status: DONE
Confidence: CONFIRMED

## Observation

`EMU-004` and `EMU-005` reached the MSHvSF title/menu scene, and `EMU-007`
validated the stock Mednafen snapshot shortcut as an available action. A dedicated
EMU-008 capture with retained emulator-generated image metadata has not yet been
recorded.

## Hypothesis

The stock Mednafen 1.32.1 snapshot action (`F9` in the project-local profile) will
capture the described MSHvSF title/menu scene into the configured local snapshot
directory, and the same procedure will work again from a cold launch.

## Controlled Change

Only the screenshot action and ignored runtime screenshot evidence will change. The
stock Mednafen binary, source image, BIOS files, project-local runtime configuration,
and 4 MiB cartridge setting will remain unchanged.

## Prediction

After reaching the title/menu scene, pressing `F9` with the Mednafen window focused
will create a screenshot under `local/mednafen/snaps/` with a recorded filename,
size, dimensions, and SHA-256. A second cold launch and capture will produce the
same scene and another retained screenshot artifact.

## Inputs and Provenance

- Source image: ignored `local/disc_images/mshvsf_saturn_jp/`.
- Source identity: 13-component manifest in
  `references/mshvsf/saturn_jp/README.md`.
- Release description: locally supplied Marvel Super Heroes vs. Street Fighter
  (Japan) Saturn disc image; release identity as named, not independently verified.
- BIOS aliases: ignored `local/mednafen/firmware/sega_101.bin` and
  `local/mednafen/firmware/mpr-17933.bin`; hashes are recorded in `docs/mednafen.md`.
- Emulator: ignored `vendor/mednafen/build/src/mednafen`, stock Mednafen 1.32.1;
  SHA-256 `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.

## Tools and Environment

- Host: macOS arm64, as recorded by the preceding M0 experiments.
- Runtime root: `MEDNAFEN_HOME="$PWD/local/mednafen"`.
- Configuration: ignored `local/mednafen/mednafen.cfg`, including
  `filesys.path_snap snaps`, `filesys.fname_snap %f-%p.%x`, and
  `command.take_snapshot keyboard 0x0 66`.
- Controller: 8BitDo M30 in wired macOS mode, SDL identity `PS4 Controller`.
- Existing runtime warnings: unsupported CUE `CATALOG` directive and absent
  adjacent `.sbi`; neither input is changed.

## Procedure

1. Verify all 13 source-image component hashes, the stock binary hash, and the two
   canonical BIOS hashes before launch.
2. Confirm no Mednafen process or stale runtime lock is present.
3. Launch the untouched source with the project-local runtime root and redirect the
   run log to an ignored path.
4. Focus the Mednafen window, send the previously validated `Enter` input, and wait
   for the title/menu scene to render.
5. Press `F9` once with the emulator window focused. Record the resulting screenshot
   filename, size, dimensions, SHA-256, and visible scene.
6. Exit cleanly, verify no process remains, and repeat steps 2 through 5 from a cold
   launch using a distinct ignored log/artifact name if required.
7. Re-run the source identity command and compare every component with the tracked
   manifest.

## Actual Result

The pre-run source identity command reported all 13 manifest components with the
recorded sizes and SHA-256 values. The stock binary and canonical BIOS hashes also
matched their recorded identities. Both cold launches loaded Mednafen 1.32.1,
enumerated the M30 as `PS4 Controller`, identified software `T-1238G`, area `J`, and
reported `Cart: 4MiB Extended RAM`.

The first run created this emulator-generated screenshot after the title/menu scene
was reached:

| Artifact | Size | Dimensions | SHA-256 | Description |
| --- | ---: | --- | --- | --- |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0003.png` | 19,270 bytes | 352x240 | `7e20cb6ce62bdb0924d1ce00c1a5ac48e74cebbcd2d6fb7fcbb14902e460dfd7` | MSHvSF title screen with `PRESS START BUTTON` |

The second cold run created a second emulator-generated screenshot:

| Artifact | Size | Dimensions | SHA-256 | Description |
| --- | ---: | --- | --- | --- |
| `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0004.png` | 24,589 bytes | 352x240 | `5a655bd264448b796948b9f6c0766c3f160611e5edf6e4f2479863e80775761b` | MSHvSF title screen with `PRESS START BUTTON`, animated background variation |

The retained run logs were each 4,248 bytes with SHA-256
`c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c`.
The post-run source identity command reproduced every pre-run size and SHA-256.
No Mednafen process remained. A zero-byte stale ignored lock from the previous
session was removed after confirming that no process owned it.

## Conclusion

`CONFIRMED`: stock Mednafen 1.32.1's configured `F9` snapshot action creates a
352x240 PNG in the project-local `local/mednafen/snaps/` directory from the
described MSHvSF title/menu scene. The procedure reproduced the visible scene from
two cold launches without changing the source image, emulator binary, BIOS files, or
runtime configuration.

## Uncertainty and Alternatives

The screenshot file is visual evidence only and does not establish binary
provenance beyond the separately recorded launch inputs. Screenshot bytes may differ
between repeated captures if the scene is animated or host scaling changes; scene
identity, dimensions, and hashes will be recorded rather than assuming byte identity.

## Reproduction

The launch convention is:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu008-capture-run-1.log 2>&1
```

Repeat with `emu008-capture-run-2.log` for the second cold run. Focus the window,
send `Enter`, wait approximately 35 seconds for the title/menu scene, press `F9`
once, and exit with `F12`. Verify each generated PNG with `file` and `shasum -a 256`.
