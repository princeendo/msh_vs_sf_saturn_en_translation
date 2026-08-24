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
