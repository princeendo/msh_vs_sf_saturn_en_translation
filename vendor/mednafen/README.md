# Mednafen Vendor Area

No Mednafen fork, patch, or binary is currently authorized here.

Stock Mednafen must first be evaluated under `EMU-012`. A modification may begin only
after `EMU-020` documents a concrete insufficiency and the task gate authorizes the
smallest useful change.

## Selected Stock Release

`EMU-001` selects the unmodified Mednafen `1.32.1` source release for the M0
evaluation.

- Upstream project: <https://mednafen.github.io/>.
- Release page: <https://mednafen.github.io/releases/>.
- Release date: 2024-04-05.
- Source archive: `mednafen-1.32.1.tar.xz`.
- Source archive URL: <https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz>.
- Retrieval date: 2026-08-24.
- Size: 3,571,236 bytes.
- SHA-256: `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`.
- License: GNU GPL version 2, from the archive's `mednafen/COPYING` file; bundled
  components may have separate notices.

The source release is selected instead of a Windows binary because the research host
is macOS arm64 and the upstream release page does not provide a macOS binary. The
upstream Saturn documentation says official Saturn builds are compiled for some
64-bit architectures, including AArch64, and recommends at least a quad-core Intel
Haswell-class CPU at 3.3 GHz base and 3.7 GHz turbo. These are expected host
requirements, not a local build or runtime result. Build options, dependency versions,
and the resulting binary identity belong to `EMU-002`.

The upstream source-build notes list `build-essential`, `pkg-config`, SDL 2.0.5 or
newer, libFLAC, and zlib, with Debian Stretch package names as examples. They list
successful compilation on FreeBSD, Linux, NetBSD, OpenBSD, and Windows, but do not
establish a macOS build. `EMU-002` must determine the corresponding dependency
versions and availability on this host.

## EMU-002 Stock Build

`EMU-002` built the selected archive without a local patch on 2026-08-24. The source
was extracted to ignored `vendor/mednafen/src/`, and the out-of-tree build was placed
under ignored `vendor/mednafen/build/`.

Host and tool versions:

- Host: macOS 26.5.2, Darwin 25.5.0, arm64.
- Compiler: Apple Clang 21.0.0 (`/usr/bin/clang`, `/usr/bin/clang++`).
- Make: GNU Make 3.81.
- `pkg-config`: 2.5.1; Homebrew: 6.0.18.
- SDL2: 2.32.70 via Homebrew `sdl2-compat`.
- libFLAC: 1.5.0; zlib: 1.2.12.

The archive acquisition command, when the archive is not already available, is:

```bash
curl -L --fail --silent --show-error \
  -o /path/to/mednafen-1.32.1.tar.xz \
  https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz
```

The build commands were:

```bash
mkdir -p vendor/mednafen/src vendor/mednafen/build
tar -xJf /path/to/mednafen-1.32.1.tar.xz \
  --strip-components=1 -C vendor/mednafen/src
cd vendor/mednafen/build
PKG_CONFIG=/opt/homebrew/bin/pkg-config \
CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

`config.status --config` recorded `--enable-debugger`, `--enable-ss`, the local
prefix, and the explicit compiler and `pkg-config` paths. All other configure options
remained at their upstream defaults. The resulting binary is a native arm64 Mach-O:

- Path: `vendor/mednafen/build/src/mednafen`.
- Size: 21,322,536 bytes.
- SHA-256: `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`.

The isolated smoke test was run from the build directory with no BIOS or game image:

```bash
MEDNAFEN_HOME="$PWD/../../../local/mednafen" ./src/mednafen -help
```

It exited successfully, reported Mednafen `1.32.1`, and listed the `ss` Saturn
emulation module. The GNU-style `--version` spelling is not accepted by this binary;
it reports `Unrecognized argument: --version`. This build result does not claim that
the target game boots or that debugger behavior has been experimentally verified.

If authorized, track:

- upstream project URL;
- release version or commit revision;
- source archive filename, byte size, SHA-256, retrieval date, and license;
- host and dependency versions;
- exact build and test commands;
- the documented stock limitation and patch rationale;
- minimal patch files and reproducible validation results.

Do not commit upstream source archives, built emulator binaries, runtime state, BIOS
files, game images, screenshots, save states, dumps, or traces. Keep those artifacts
in ignored local paths and track only permitted provenance and evidence metadata.
