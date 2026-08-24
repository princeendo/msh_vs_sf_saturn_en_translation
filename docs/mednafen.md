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
