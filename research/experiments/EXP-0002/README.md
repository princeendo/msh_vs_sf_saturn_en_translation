# EXP-0002: Force MSHvSF 4 MiB Extended RAM

Task: EMU-005
Status: DONE
Confidence: CONFIRMED

## Observation

The prior `EMU-004` launch used `ss.cart=auto` and reached the MSHvSF title
screen while reporting `Cart: 4MiB Extended RAM`. That established the database
selection and a boot endpoint, but did not separately test the explicit cartridge
configuration.

## Hypothesis

Forcing Mednafen's `ss.cart` setting to `extram4` will initialize the 4 MiB
extended-RAM model and allow the untouched MSHvSF Saturn image to reach the same
stable title-screen endpoint.

## Controlled Change

Only the Mednafen cartridge setting changed from the project-local baseline
`ss.cart=auto` to the command-line value `ss.cart=extram4`. The stock binary,
BIOS aliases, source image, runtime root, region, cache mode, and input sequence
were unchanged. Mednafen automatically persisted the command-line setting to the
ignored local configuration; it was restored to `ss.cart=auto` after testing.

## Prediction

Each cold launch will report software ID `T-1238G`, report `Cart: 4MiB Extended
RAM`, and reach a visibly rendered MSHvSF title screen after the recorded Start
input and boot delay. The source-image component hashes will remain unchanged.

## Inputs and Provenance

- Source image: ignored `local/disc_images/mshvsf_saturn_jp/`.
- Source identity: the 13-component manifest in
  `references/mshvsf/saturn_jp/README.md`.
- Release description: locally supplied Marvel Super Heroes vs. Street Fighter
  (Japan) Saturn disc image; release identity as named, not independently
  verified.
- BIOS aliases: ignored `local/mednafen/firmware/sega_101.bin` and
  `local/mednafen/firmware/mpr-17933.bin`, hashes recorded in `docs/mednafen.md`.
- Emulator: ignored `vendor/mednafen/build/src/mednafen`, stock Mednafen 1.32.1,
  SHA-256 `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.

## Tools and Environment

- Host: macOS 26.5.2, Darwin 25.5.0, arm64.
- Emulator: Mednafen 1.32.1, native arm64 stock build.
- Runtime root: `MEDNAFEN_HOME="$PWD/local/mednafen"`.
- Source verification utility: project Python environment through `./invenv.sh`.
- Existing runtime warnings: unsupported CUE `CATALOG` directive and absent
  adjacent `.sbi`; neither input was changed.
- Tested input: host Enter (`key code 36`) to continue the title flow and host
  F12 (`key code 111`) to terminate after evidence capture.

## Procedure

1. Verify all source-image components with:

   ```bash
   ./invenv.sh python -m tools.disc.hash_source \
     --description "EMU-005 pre-run source identity verification" \
     --json local/disc_images/mshvsf_saturn_jp/*
   ```

2. Verify the stock binary and canonical BIOS aliases:

   ```bash
   shasum -a 256 vendor/mednafen/build/src/mednafen \
     local/mednafen/firmware/sega_101.bin \
     local/mednafen/firmware/mpr-17933.bin
   ```

3. Confirm no process owns the local runtime lock.

4. Launch the unchanged source with the explicit cartridge setting, redirecting
   output to an ignored log:

   ```bash
   MEDNAFEN_HOME="$PWD/local/mednafen" \
     vendor/mednafen/build/src/mednafen -ss.cart extram4 \
     "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
     > local/mednafen/logs/emu005-extram4-run3.log 2>&1
   ```

5. Focus the Mednafen window, send Enter, wait for the boot/title flow, and
   capture the visible endpoint. Repeat the launch from a cold start.

6. Terminate the final run with the focused F12 action and verify no process
   remains. Remove only a stale ignored runtime lock when required before a
   subsequent cold launch.

7. Restore the local setting without launching a game:

   ```bash
   MEDNAFEN_HOME="$PWD/local/mednafen" \
     vendor/mednafen/build/src/mednafen -ss.cart auto -help \
     > local/mednafen/logs/emu005-restore-auto-2.log 2>&1
   ```

8. Re-run the source identity command with the post-run description and compare
   every component with the tracked manifest.

## Actual Result

The first automation attempt timed out before endpoint capture. A later short
capture was black because it occurred before the title flow had finished. These
failed attempts are retained as ignored logs and are not used as endpoint
evidence. The timed-out log is 4,264 bytes with SHA-256
`b0e9fc2f6b3fc26e21883305d946582c4f534d6ae713997291e66897807916dd`; the two
short retries are each 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`.

The controlled long runs produced the following identical runtime result:

```text
SGID: T-1238G
SGNAME: MARVEL SUPER HEROES VS. STREET FIGHTER
SGAREA: J
Cart: 4MiB Extended RAM
```

At approximately 20 seconds after the Start input, the host capture showed the
legal notice screen. At approximately 35 seconds, both repeated cold runs
showed the rendered MSHvSF title screen with `PRESS START BUTTON`.

| Artifact | Size | SHA-256 | Description |
| --- | ---: | --- | --- |
| `local/mednafen/logs/emu005-extram4-run2.log` | 4190 bytes | `e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2` | Forced-cart runtime log |
| `local/mednafen/snaps/emu005-extram4-run2-20s.png` | 5606265 bytes | `0a5aa0512ad539d05e3993d0148b37741b253befca37b959a38bff9799fe1d00` | 5120x2880 host capture of legal notice |
| `local/mednafen/snaps/emu005-extram4-run2-35s.png` | 5964265 bytes | `8d1bb3fd2e6f6eaa48a9f0df4d4399774bc48d072d11086e4f2b73f94812882b` | 5120x2880 host capture of title screen |
| `local/mednafen/logs/emu005-extram4-run3.log` | 4190 bytes | `e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2` | Independent cold-repeat log |
| `local/mednafen/snaps/emu005-extram4-run3-35s.png` | 6035363 bytes | `9fa0dc7e1189c4740cbaa6c2f0b11a265424d3b75de597a91540ceffe200bc51` | 5120x2880 host capture of repeated title screen |
| `local/mednafen/logs/emu005-extram4-run4.log` | 4190 bytes | `e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2` | Final cold-repeat log with clean F12 termination |

The final focused F12 test terminated the emulator without a fallback signal.
The local `ss.cart` setting was restored to `auto`. Pre-run and post-run source
identity reports matched all 13 manifest entries byte-for-byte.

## Conclusion

`CONFIRMED`, scoped to the tested runtime path: explicitly forcing Mednafen's
`extram4` setting selects `4MiB Extended RAM` for MSHvSF software `T-1238G`, and
the untouched image reproducibly reaches its rendered title screen from cold
launches. This validates cartridge configuration and operation sufficient for
the M0 runtime path.

## Uncertainty and Alternatives

This experiment does not directly read, write, or boundary-test cartridge RAM,
and it does not establish which game code accesses which cartridge address. It
also does not establish that the CUE `CATALOG` or missing `.sbi` warnings are
irrelevant to later experiments. Direct debugger and memory-workflow tests remain
gated by `EMU-010` through `EMU-012`.

## Reproduction

From the repository root, use the launch command in the Procedure section with
the project-local runtime root and the recorded source image. Focus the window,
send Enter, wait at least 35 seconds, and inspect the title endpoint. Repeat from
a cold launch. Restore `ss.cart=auto` with the recorded `-help` command after the
test. Runtime logs, host captures, source images, BIOS files, and emulator binaries
remain under ignored local paths.
