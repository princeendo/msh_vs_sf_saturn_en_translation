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
