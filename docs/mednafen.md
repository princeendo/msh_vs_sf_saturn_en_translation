# Mednafen Research Guide

## Required Order

Use stock Mednafen first. Select and record an upstream release, then document its
URL, version or revision, source hash, host environment, build options, dependencies,
and exact build commands.

Validate the task-required stock capabilities before proposing modifications:

- boot the target using a legally obtained BIOS and source image;
- configure the required 4 MB RAM cartridge;
- verify fightpad input;
- capture screenshots and save states;
- evaluate interactive debugger access.

Record observed behavior and limitations; do not infer capabilities from another
version or platform.

## Selected Stock Release

`EMU-001` selects the unmodified Mednafen `1.32.1` source release for the M0
evaluation.

- Upstream project: <https://mednafen.github.io/>.
- Release page: <https://mednafen.github.io/releases/>.
- Release date: 2024-04-05.
- Source archive URL: <https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz>.
- Retrieval date: 2026-08-24.
- Archive: `mednafen-1.32.1.tar.xz`, 3,571,236 bytes.
- SHA-256: `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`.
- License: GNU GPL version 2, as stated by `mednafen/COPYING` in the source archive;
  bundled components may have separate notices.

The source archive is selected because the upstream release page provides Windows
binaries but no macOS binary, while this research host is macOS arm64. The upstream
Saturn documentation says official Saturn builds are compiled for some 64-bit
architectures, including AArch64, and gives a minimum recommended CPU of quad-core
Intel Haswell class at 3.3 GHz base and 3.7 GHz turbo. These are expected host
requirements only. The exact local stock build result is recorded below; it does not
claim target-game boot or debugger behavior.

The upstream source-build notes list `build-essential`, `pkg-config`, SDL 2.0.5 or
newer, libFLAC, and zlib, with Debian Stretch package names as examples. They also
list successful compilation on FreeBSD, Linux, NetBSD, OpenBSD, and Windows, but do
not establish a macOS build. These are the applicable upstream build prerequisites;
`EMU-002` must determine the corresponding versions and availability on this host.

Selection rationale: `1.32.1` is the latest release listed by the upstream release
page, the general and Saturn documentation are valid as of `1.32.1`, and the Saturn
database identifies MSHvSF Japan product `T-1238G` as requiring 4 MiB extended RAM.
The debugger documentation provides the relevant stock workflow baseline, subject to
the later exact-build tests in `EMU-010` and `EMU-011`.

## Exact Stock Build

`EMU-002` built the unmodified `1.32.1` archive on 2026-08-24 using macOS 26.5.2
arm64, Darwin 25.5.0, Apple Clang 21.0.0, GNU Make 3.81, `pkg-config` 2.5.1,
Homebrew 6.0.18, SDL2 2.32.70, libFLAC 1.5.0, and zlib 1.2.12. The source and
out-of-tree build are retained only in ignored local paths.

From `vendor/mednafen/build`, the configure and build commands were:

```bash
PKG_CONFIG=/opt/homebrew/bin/pkg-config \
CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

The resulting native arm64 binary is `vendor/mednafen/build/src/mednafen`, size
21,322,536 bytes, SHA-256
`ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`. With the
project-local `MEDNAFEN_HOME`, `./src/mednafen -help` exited successfully without a
BIOS or game image, reported version `1.32.1`, and listed the Saturn `ss` module.
The selected build's debugger and target runtime behavior remain later experimental
questions.

## EMU-006 Input Enumeration Investigation

The identified test device is an 8BitDo M30 gamepad connected over USB (VID `0x2DC8`,
PID `0x5006`). macOS HID enumeration and Apple Games recognize the device. The stock
Mednafen process, however, logs only `Initializing joysticks...`; it does not expose a
device for port configuration.

Two minimal SDL probes reported `joysticks=0` and `controllers=0` while the M30 was
connected. The probes were run once through the SDL2-compat library used by the
Mednafen binary and once through Homebrew's native SDL2 library; both reported
`driver=<none> joysticks=0`. The native comparison used only a temporary derived probe
binary and did not modify Mednafen or any source image.

Current upstream SDL HIDAPI source inspection also shows that its 8BitDo driver lists
SF30 Pro, SN30 Pro, Pro 2, Pro 3, and Ultimate product IDs, but not M30 PID `0x5006`.
This is `SUPPORTED` evidence for an SDL-layer device-support or controller-mode
blocker, not confirmation that every M30 USB mode is unsupported. The next controlled
experiment is to change only the M30's documented USB mode and repeat HID and SDL
enumeration before attempting Mednafen bindings.

## EMU-006 Mapping Result

The M30 was switched to the documented wired macOS mode with `A + Start` and connected
by USB. In this mode macOS presents the physical M30 as a PS4-compatible `Wireless
Controller`; SDL reports `PS4 Controller` with six axes, twelve buttons, and one hat.
Mednafen's exact joystick identity is
`0xecccd365fc40db2f0006000c00010000`.

The ignored profile at `local/mednafen/mednafen.cfg` keeps
`ss.input.port1 gamepad` and adds the following SDL bindings while retaining the
existing keyboard fallbacks:

| Saturn control | SDL input |
| --- | --- |
| D-pad up/right/down/left | Hat-compatible buttons 12/13/14/15 |
| A/B/X/Y | Buttons 0/1/2/3 |
| Z/C | Buttons 4/5 |
| Start | Button 9 (PS4 Options / M30 Start) |

The selected Saturn Digital Gamepad model does not provide usable L/R bindings in
the tested Mednafen configuration. L/R are intentionally excluded from EMU-006 by
scope decision; MSHvSF checkpoint capture does not require them. The mapping profile
was parsed successfully and a target launch recorded the joystick identity and
`Cart: 4MiB Extended RAM` in ignored log
`local/mednafen/logs/emu006-mapping-run.log` (4,248 bytes,
SHA-256 `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c`).
Runtime control and emulator-shortcut validation remains EMU-007.

## Project-Local Configuration Strategy

`EMU-003` confirms that the selected build can be launched with an isolated runtime
root. The generated configuration and all runtime artifacts remain ignored under
`local/mednafen/`; the generated 1.32.1 configuration is not a tracked project
configuration because it contains host-specific input bindings and the complete
version-generated default set.

Use this launch convention from the repository root:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue"
```

The stable settings recorded from the selected build are:

| Setting | Value | Purpose |
| --- | --- | --- |
| `filesys.path_firmware` | `firmware` | Supplied BIOS files below the local root. |
| `filesys.path_sav` | `sav` | Saturn nonvolatile save data. |
| `filesys.path_savbackup` | `b` | Save-data backups. |
| `filesys.path_state` | `mcs` | Compressed save states. |
| `filesys.path_snap` | `snaps` | Screen snapshots. |
| `filesys.path_movie` | `mcm` | Movie data. |
| `filesys.path_pgconfig` | `pgconfig` | Per-game configuration overrides. |
| `filesys.path_cheat` | `cheats` | Cheat data. |
| `filesys.fname_state` | `%f.%M%X` | Stable state filename template. |
| `filesys.fname_snap` | `%f-%p.%x` | Stable snapshot filename template. |
| `autosave` | `0` | Avoid implicit state changes at load/exit. |
| `debugger.autostepmode` | `0` | Avoid entering debugger step mode on launch. |
| `ss.bios_jp` | `sega_101.bin` | Recorded Japanese Saturn BIOS alias. |
| `ss.bios_na_eu` | `mpr-17933.bin` | Recorded North American/European BIOS alias. |
| `ss.cart` | `auto` | Use the selected build's Saturn software database. |

Stock Mednafen has no project log-directory setting. Retain diagnostic output, when
needed, by redirecting stdout and stderr to an ignored path below the same root:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/run.log 2>&1
```

The tested cold-reset procedure is to end the running instance, verify that no
process retains `local/mednafen/mednafen.lck`, and rerun the launch command. Two
independent target relaunches loaded the same local configuration and recreated the
same Saturn setup. This does not verify an in-game reset hotkey; input and checkpoint
actions remain `EMU-007` through `EMU-009` work.

The target run selected software ID `T-1238G` and reported `Cart: 4MiB Extended RAM`.
It initialized the Saturn video and audio modules but was stopped before a normal
game-screen endpoint during `EMU-003`; this observation did not close `EMU-004` or
`EMU-005`.
The run also reported the source CUE's unsupported `CATALOG` directive and absence of
an adjacent `.sbi` file; neither issue was changed during this task.

## EMU-004 Boot Result

`EMU-004` confirmed on 2026-08-24 that the same stock launch reaches a stable
MSHvSF title screen. The exact command was:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu004-launch-2.log 2>&1
```

The retained log is 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`. It records
software ID `T-1238G`, the Japanese area, and `Cart: 4MiB Extended RAM`. After
the window was focused, Enter was sent to continue the title flow and the
configured snapshot action was sent after a three-second wait. The resulting
ignored screenshot is:

- Path: `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0001.png`
- Size: 22,616 bytes, 352x240 pixels.
- SHA-256: `4c19283ec7c84b6b7690fa526e3323a7e0121efa75fa5fa9c6e88bf3c24f0d85`.
- Content: stable MSHvSF title screen with the mode menu visible.

The run exited cleanly. Pre-run and post-run checks matched all 13 source-image
component hashes in `references/mshvsf/saturn_jp/README.md`, as well as the
selected binary and canonical BIOS hashes. This closes `EMU-004` only. The
reported cart selection was setup/runtime evidence only; `EXP-0002` records the
separate controlled cartridge-operation observation that closes `EMU-005`.

## EMU-005 4 MiB Cartridge Result

`EMU-005` is confirmed by `research/experiments/EXP-0002/README.md`. The controlled
variable was the Mednafen command-line setting `-ss.cart extram4`; the stock binary,
BIOS aliases, runtime root, source image, region, and input sequence remained the
same as the `EMU-004` configuration. Mednafen persisted the command-line setting to
the ignored local configuration, and the setting was restored to `ss.cart auto` after
the experiment.

Three cold forced-cart launches each reported:

```text
SGID: T-1238G
SGNAME: MARVEL SUPER HEROES VS. STREET FIGHTER
SGAREA: J
Cart: 4MiB Extended RAM
```

The repeated runs reached the visible MSHvSF title screen with `PRESS START BUTTON`
after the recorded Start input and boot delay. The retained runtime log for the
successful repeated runs is 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`. Host-capture
metadata and hashes are recorded in `EXP-0002`; the captures remain ignored.

Pre-run and post-run checks matched all 13 source-image components in
`references/mshvsf/saturn_jp/README.md`. This confirms explicit 4 MiB cartridge
configuration and operation sufficient for the tested MSHvSF boot path. It does not
directly test cartridge RAM reads, writes, address boundaries, or game access
patterns; those remain debugger questions.

## Documented Debugger Baseline

The upstream pages and retrieved identities are cataloged in `docs/references.md`.
The debugger page is valid as of `1.32.0-UNSTABLE`; the general and Saturn pages are
valid as of `1.32.1`. These are documented capabilities only. `EMU-001`, `EMU-010`,
and `EMU-011` must verify them in the selected stock build and exact target session.

### Entry And CPU Control

| Key | Documented action |
| --- | --- |
| `Left Alt+D` | Toggle the master debugger view. |
| `Alt+1` | Select the CPU debugger view. |
| `R` | Run. |
| `S` | Step. |
| `Return` | Edit the selected disassembly address or register. |
| `Shift+Return` | Edit the watch address. |
| `Space` | Toggle a PC breakpoint at the selected disassembly address. |
| `Shift+R` | Edit read breakpoints. |
| `Shift+W` | Edit write breakpoints. |
| `Tab` | Move focus between disassembly and registers. |

PC breakpoints are documented as testing the PC at the start of an instruction. Do
not infer Saturn delay-slot or breakpoint timing beyond that statement without a
controlled test.

### Memory View And Capture

| Key | Documented action |
| --- | --- |
| `Alt+3` | Select the memory editor. |
| `Ctrl+Left` / `Ctrl+Right` | Select the previous or next address space. |
| `D` | Dump a range from the selected address space to a file. |
| `L` | Load a file into the selected address space. |
| `S` / `R` / `T` | Search for byte strings, relative byte strings, or text. |
| `Insert` | Enter memory edit mode. |
| `P` | Low-level poke through the virtual CPU's write handlers. |
| `Shift+P` | Attempt a high-level poke to underlying ROM or RAM. |

The documented dump specifications are:

```text
start_address end_address filename
start_address +count filename
```

The first form's end address is inclusive. `L`, `P`, `Shift+P`, and memory edit mode
modify emulated state and are not capture operations. High-level poke is not available
for every system. Dump files, traces, and other runtime evidence belong under ignored
paths with checkpoint, address-space, range, size, and SHA-256 metadata recorded.

### Required Live Checks

- Confirm that the selected build includes debugger support and that `ss` exposes the
  CPU and memory views required by the project.
- Enumerate every Saturn CPU choice, displayed register, and memory-editor address
  space exactly as shown; do not supply names from source code or another frontend.
- Test PC, read, and write breakpoint timing one controlled case at a time, including
  whether DMA or device accesses trigger CPU-oriented breakpoints.
- Test dump range boundaries, output size, selected address space, and repeatability on
  a small non-copyrighted or safely retained runtime range before bulk capture.
- Do not load a save state or invoke power/reset while stopped in step mode. Upstream
  documentation warns that this combination may significantly malfunction for `ss`.
- Treat branch history as unreliable when the CPU debugger is not active unless at
  least one breakpoint is installed.

The upstream debugger page does not document Saturn-specific graphics-viewer support,
address aliases, physical/logical address meaning, high-level pokes, or DMA visibility.
Those are unknown until observed; source-code inspection alone would not make them
runtime-confirmed behavior.

## Local State

Keep runtime configuration, BIOS files, save states, screenshots, memory dumps,
traces, and emulator binaries in ignored local paths. Track only sanitized settings,
provenance, hashes, commands, and factual results.

## Local Saturn BIOS

The locally supplied BIOS files are stored in the ignored directory
`local/mednafen/firmware/`. The source directory was not modified. The two canonical
Mednafen filenames below are copies of supplied files with matching hashes; the other
supplied files remain available for later comparison without being selected by
default.

Mednafen's Saturn documentation for version 1.32.1 defines these default firmware
filenames and hashes:

| Local filename | Supplied filename | Size | SHA-256 | Mednafen use |
| --- | --- | ---: | --- | --- |
| `sega_101.bin` | `Bios Saturn 1.01 (J) [!].bin` | 524288 | `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac` | `ss.bios_jp` |
| `mpr-17933.bin` | `Sega Saturn BIOS (EUR).bin` | 524288 | `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f` | `ss.bios_na_eu` |

The remaining supplied BIOS files are retained under their original filenames:

| Local filename | Size | SHA-256 |
| --- | ---: | --- |
| `Bios GameNavi HiSaturn 1.03.bin` | 524288 | `37561c4444bec52ae1aae31de5579f1856d5b23002ee083ade42f9ed13c8616f` |
| `Bios HI-Saturn 1.01 (J) [!].bin` | 524288 | `feb733e0a1578eb8a6ff9c7f32b0b7319336bcf98f461a5f608e73159f672f4e` |
| `Bios Hi-Saturn 1.02 (J).bin` | 524288 | `1d964171c979f87ca120d77fdb0d98063bb75bfa219bb180aeb650c528ce054e` |
| `Bios Saturn 1.00 (J) [!].bin` | 524288 | `ae4058627bb5db9be6d8d83c6be95a4aa981acc8a89042e517e73317886c8bc2` |
| `Bios Saturn 1.00a (U) [!].bin` | 524288 | `87293093fad802fcff31fcab427a16caff1acbc5184899b8383b360fd58efb73` |
| `Bios Saturn 1.01 (J) [!].bin` | 524288 | `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac` |
| `Bios Saturn 1.01a (U) [!].bin` | 524288 | `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f` |
| `Bios V-Saturn 1.01 (J) [!].bin` | 524288 | `53b303bb5965e4c6aa4310b389e761401f45d71f1459f3a46cf50b588aceddd5` |
| `Sega Saturn BIOS (1.003) (J).bin` | 524288 | `cc1e1b7f88f1c6e6fc35994bae2c2292e06fdae258c79eb26a1f1391e72914a8` |
| `Sega Saturn BIOS (EUR).bin` | 524288 | `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f` |
| `Sega Saturn BIOS (Oct 12, 1994).bin` | 524288 | `cc1e1b7f88f1c6e6fc35994bae2c2292e06fdae258c79eb26a1f1391e72914a8` |

With `MEDNAFEN_HOME` set to the project-local `local/mednafen/` directory, Mednafen's
default `filesys.path_firmware=firmware` setting finds the canonical files without
additional BIOS arguments:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" mednafen /path/to/mshvsf.cue
```

The exact Mednafen build and observed boot result remain subject to `EMU-001` through
`EMU-004`; these names and hashes are setup metadata, not runtime confirmation.

## Modification Gate

Do not modify Mednafen before `EMU-012` is complete and `EMU-020` documents why stock
Mednafen is insufficient. If modification is authorized, make the smallest useful
change and preserve upstream provenance, rationale, patch, and reproducible build
steps in `vendor/mednafen/`.
