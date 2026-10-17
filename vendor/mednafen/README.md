# Mednafen Vendor Area

The stock Mednafen 1.32.1 source and build stay unmodified in the ignored
`vendor/mednafen/src/` and `vendor/mednafen/build/`.

One patch is authorized: the agent interface. It was authorized by the user on
2026-10-17 after `EMU-012` and `EMU-020`; see
`docs/mednafen_agent_interface.md`. The patch is tracked here and applied to a
separate ignored copy of the source.

## Selected Stock Release

`EMU-001` selects the unmodified Mednafen `1.32.1` source release.

- Upstream project: <https://mednafen.github.io/>.
- Release page: <https://mednafen.github.io/releases/>.
- Release date: 2024-04-05.
- Source archive: `mednafen-1.32.1.tar.xz`.
- Source archive URL: <https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz>.
- Retrieval date: 2026-08-24.
- Size: 3,571,236 bytes.
- SHA-256: `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`.
- License: GNU GPL version 2, from the archive's `mednafen/COPYING` file. Bundled
  components may have separate notices. The agent patch is GPL-2.0-or-later.

Stock build and host details (`EMU-002`) are in `docs/mednafen.md`. The stock binary
is `vendor/mednafen/build/src/mednafen`, SHA-256 `ca9bec5f…2587`.

## Agent-Interface Patch

- Patch: `patches/0001-agent-interface.patch`, against `1.32.1`.
- Scope: frontend driver only. It adds `src/drivers/agent.inc` and hooks in
  `src/drivers/debugger.cpp`, `debugger.h`, and `main.cpp`. The Saturn core is
  unchanged.
- Activation: only when `MEDNAFEN_AGENT_DIR` is set. Unset, the binary behaves
  like stock.

Build (from the repository root; the stock source must already be extracted per
`EMU-002`):

```bash
cp -R vendor/mednafen/src vendor/mednafen/src-agent
patch -d vendor/mednafen/src-agent -p1 < vendor/mednafen/patches/0001-agent-interface.patch
mkdir -p vendor/mednafen/build-agent && cd vendor/mednafen/build-agent
PKG_CONFIG=/opt/homebrew/bin/pkg-config CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src-agent/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

Run (from the repository root):

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" MEDNAFEN_AGENT_DIR="$PWD/local/mednafen/agent" \
  vendor/mednafen/build-agent/src/mednafen "path/to/game.cue"
```

The client is `tools/mednafen/agent.py`. The binary hash and validation results
are recorded in `docs/mednafen_agent_interface.md`.

Do not commit upstream source archives, built binaries, runtime state, BIOS files,
game images, screenshots, save states, dumps, or traces.
