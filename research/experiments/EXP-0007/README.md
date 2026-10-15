# EXP-0007: Verify Stock Debugger Access and WRAM Dumps

Task: `EMU-010`
Date: 2026-10-15
Status: DONE
Confidence: CONFIRMED

## Observation

`EMU-009` confirmed repeatable save/load checkpoints. The stock debugger has not yet
been opened against MSHvSF. Upstream documentation lists `Alt+D` (debugger),
`Alt+1` (CPU view), `Alt+3` (memory editor), `S`/`R` (step/run), and `D` (dump).

Read-only inspection of the stock 1.32.1 source (not runtime evidence) shows:

- `src/ss/debug.inc` registers the Saturn memory-editor address spaces `physical`,
  `workraml`, `workramh`, `scspram`, `scspmprog`, `scsptemp`, `scspmems`, `dspprog`,
  `backup`, `vdp1vram`, `vdp1fb0`, `vdp1fb1`, and `vdp2vram`. The `physical`
  read/write handlers are commented `TODO` stubs, and no cartridge-RAM address space
  is registered.
- The `workramh` and `workraml` spaces are offset-based (`Address &= 0xFFFFF`) and
  read bytes in Saturn big-endian order (`ne16_rbo_be`).
- `src/drivers/memdebugger.cpp` parses dumps as `%08x %08x name` (inclusive end) or
  `%08x +%08x name`, and switches address spaces with `Ctrl+Left`/`Ctrl+Right` or
  `,`/`.`.
- `src/drivers/main.cpp` keeps the game loop paused while frame advance is active and
  processes pending save states in the video update path.
- The project-local profile binds frame advance to `Alt+A`, normal run to `Alt+R`,
  the debugger to `Alt+D`, save/load state to `F5`/`F7`, and snapshots to `F9`.

## Hypothesis

The stock debugger opens against MSHvSF, and CPU step mode can stop and resume
emulation. While frame advance holds the game loop paused, the memory editor can dump
the full `workramh` and `workraml` spaces (offsets `0x00000-0xFFFFF`) to files. A
save state written during the same pause captures the same instant, which later
validates the save-state extractor.

## Controlled Change

Only debugger, frame-advance, state-slot, save-state, and dump actions are added. The
stock binary, source image, BIOS aliases, local configuration, and cartridge setting
are unchanged. No memory edit, poke, or load action is used in the memory editor.

## Prediction

1. `Alt+D` shows the debugger overlay; `S` stops emulation and advances the PC by one
   instruction per press; `R` resumes visible animation.
2. `Alt+A` freezes the scene. `F5` in slot 2 creates a new `.mc2` state before any
   further frame is emulated.
3. Each `D` dump creates a 1,048,576-byte file. Two consecutive `workramh` dumps taken
   in the same pause have identical SHA-256 values.

## Inputs and Provenance

- Source image: ignored `local/disc_images/mshvsf_saturn_jp/`; all 13 components
  matched `references/mshvsf/saturn_jp/README.md` before the run.
- Emulator: `vendor/mednafen/build/src/mednafen`, stock 1.32.1, SHA-256
  `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587` (matched).
- BIOS: `sega_101.bin` SHA-256
  `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac`;
  `mpr-17933.bin` SHA-256
  `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f` (both matched).

## Tools and Environment

- Host: macOS arm64 (Darwin 25.6.0). Runtime root `MEDNAFEN_HOME="$PWD/local/mednafen"`,
  launched from the repository root, so relative dump paths resolve there.
- Controller: 8BitDo M30 in wired macOS mode (`EXP-0004` mapping).
- Dump directory: ignored `local/mednafen/dumps/`.

## Procedure

Part 1, CPU control (emulation running at the title/menu scene):

1. Focus the window and press Saturn Start to reach the title/menu scene.
2. `Option+D`: record what the overlay shows.
3. `Option+1`: CPU view. Press `S` three times and record each PC, then `R`.
4. `Option+D` to hide the debugger and confirm the game is animating.

Part 2, paused dumps:

5. `Option+A` to freeze, `2` to select slot 2, `F5` to save. Check that the `.mc2`
   file exists before anything else is emulated.
6. `Option+D`, `Option+3`. Use `.` and `,` to cycle the address spaces, recording
   each name shown, and stop on High Work RAM.
7. `D`, then `00000000 +00100000 local/mednafen/dumps/exp0007-wramh-a.bin`, `Return`.
8. `D`, then `00000000 +00100000 local/mednafen/dumps/exp0007-wramh-b.bin`, `Return`.
9. Switch to Low Work RAM. `D`, then
   `00000000 +00100000 local/mednafen/dumps/exp0007-wraml-a.bin`, `Return`.
10. `Option+D` to hide the debugger, `Option+R` to resume, then exit.

Do not load a state or reset while the CPU debugger is in step mode.

## Actual Result

Launch log: ignored `local/mednafen/logs/emu010-exp0007.log`. It reports `T-1238G`,
area `J`, and `Cart: 4MiB Extended RAM`, plus the previously recorded missing
`.sbi`, optional `ss.cfg`/per-game config, and `ss.cht` messages. It is 4,358 bytes,
SHA-256 `145f6000e6d0d8799443f72424c2a9e774e55ed3707db14b1933c6f9a4c0b13e`. Unlike
earlier runs, it also contains a host macOS input-method line (`error messaging the
mach port for IMKCFRunLoopWakeUpReliable`); no emulator effect was observed.
Mednafen exited with status 0. All 13 source components, the stock binary, and both
BIOS aliases matched their recorded hashes after the run, and the local profile
still had `ss.cart auto` and the M30 Start binding.

Part 1 (user-observed):

- `Option+D` opened the debugger with the CPU view (disassembly and registers)
  already selected. `Option+1` therefore produced no visible change; this is not
  treated as a failure.
- `S` froze emulation and stepped the highlighted instruction. `R` resumed it.
  PC values were not recorded.

Part 2:

- `Option+A` froze the scene. `2` then `F5` created the slot-2 state at 18:43:45,
  before the first dump at 18:45:06.
- `Option+3` opened the memory editor. Cycling with `.` showed these address spaces,
  in order, as transcribed by the user:
  `SH-2 External Bus (TODO)`, `Low Work RAM`, `High Work RAM`, `SCSP RAM`,
  `SCSP MPROG`, `SCSP TEMP Relative Offset`, `SCSP MEMS`, `DSP Program RAM`,
  `Backup RAM`, `VDP1 VRAM`,
  `VDP1 FB0 RAM (raw no 8bpp/rot addr bit swizzling)`,
  `VDP1 FB1 RAM (raw no 8bpp/rot addr bit swizzling)`, and `VDP2 VRAM`.
  No cartridge-RAM space was listed.
- The prompt text was typed by hand. The first three dumps are 1,048,577 bytes,
  one more than predicted. With `+00100000`, the stock dump loop writes exactly
  `0x100000` bytes. A size of `0x100001` matches the inclusive form
  `00000000 00100000`, and the extra final byte equals the first byte in all three
  files, consistent with the `Address &= 0xFFFFF` wrap. The typed `+` was most
  likely omitted (inferred, not observed). A low-RAM filename was also typed as
  `exp00070-wraml-a.bin`.
- During the same pause, the user re-dumped with the inclusive form
  `00000000 000FFFFF <file>`. Those dumps are exactly 1,048,576 bytes and equal the
  first 1,048,576 bytes of the earlier dumps.

| Artifact (ignored, `local/mednafen/`) | Size | SHA-256 | Space / description |
| --- | ---: | --- | --- |
| `mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc2` | 3,848,175 | `2c735816da8fcb2dbcc63b62da05454a07994f3f08ba56239fbe5fa829c65eb9` | Slot-2 state saved during the pause |
| `dumps/exp0007-wramh-a.bin` | 1,048,577 | `cdc1593260a18e98c3feae4e124bd9b93852176baefe91ec724e834be85ec2f0` | High Work RAM, `0x00000-0x100000` incl. |
| `dumps/exp0007-wramh-b.bin` | 1,048,577 | `cdc1593260a18e98c3feae4e124bd9b93852176baefe91ec724e834be85ec2f0` | High Work RAM, repeat |
| `dumps/exp00070-wraml-a.bin` | 1,048,577 | `b30fa5497704413275ceeb8bf71fa7943e24df2e572d86d4962748cd58f060c1` | Low Work RAM, `0x00000-0x100000` incl. |
| `dumps/wram-c.bin` | 1,048,576 | `5e7c2347ddf805da44fddafe7f663bbb23d8896a7014bcbea9a4f4790f94ead0` | High Work RAM, `00000000 000FFFFF` |
| `dumps/wraml-b.bin` | 1,048,576 | `0cb95fbf577923bfc2729e5d5303b2200a6ea9e9d77dcbdde39dddbecd4f9a5c` | Low Work RAM, `00000000 000FFFFF` |
| `dumps/vdp1vram-a.bin` | 524,288 | `173764195179ce178ff8475c7c82d51dd17bd7e3014fa2e025f58d2a18a8894d` | VDP1 VRAM, `00000000 0007FFFF` |
| `dumps/vdp2vram-a.bin` | 524,288 | `fa94f7ca4c62267bf05f97a492ef91c3f82aa6a3b7ec676215446b7724360b0f` | VDP2 VRAM, `00000000 0007FFFF` |

`wram-c.bin` (the High Work RAM re-dump, despite its name) equals
`exp0007-wramh-a.bin[:0x100000]` and differs from `wraml-b.bin`. `wraml-b.bin` equals
`exp00070-wraml-a.bin[:0x100000]`. The High Work RAM dump begins `06 00 BD 68`.

## Conclusion

`CONFIRMED` for the tested scope:

- The stock 1.32.1 debugger opens against MSHvSF.
- CPU step mode pauses (`S`) and resumes (`R`) emulation.
- The memory editor exposes the address spaces listed above. It has no cartridge-RAM
  space.
- During a frame-advance pause, the editor repeatedly dumps High Work RAM, Low Work
  RAM, VDP1 VRAM, and VDP2 VRAM to files. Repeated dumps of the same space are
  byte-identical.
- The inclusive-end dump form `start end file` is the reliable hand-typed form.

## Uncertainty and Alternatives

- This was one cold launch with user-observed Part 1 results. PC values were not
  captured.
- Whether `wram-c.bin` and the other dumps equal the WRAM arrays inside the slot-2
  state is untested. That is the extractor validation experiment.
- The `06 00 BD 68` prefix suggests Saturn big-endian byte order but does not prove
  it.
- `SH-2 External Bus (TODO)` was not read. The source shows stub handlers, so its
  contents are not meaningful evidence.
- The 4 MiB cartridge RAM cannot be dumped through the stock memory editor. Save
  states (`ExtRAM` `LO`/`HI` in `src/ss/cart/extram.cpp`) are the only stock path
  identified so far.

## Reproduction

From the repository root, verify source identity, then launch:

```bash
./invenv.sh python -m tools.disc.hash_source \
  --description "EMU-010 source identity verification" \
  --json local/disc_images/mshvsf_saturn_jp/*
mkdir -p local/mednafen/dumps
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu010-exp0007.log 2>&1
```

Follow the Procedure, using left Option for Alt. In each dump prompt, type the
inclusive form, for example:

```text
00000000 000FFFFF local/mednafen/dumps/wramh.bin
```

Hash the outputs with `shasum -a 256`. Do not load states while in CPU step mode.
