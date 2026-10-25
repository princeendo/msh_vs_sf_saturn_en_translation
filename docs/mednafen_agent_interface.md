# Mednafen Agent Interface (EMU-020)

Status: **modification proposed and authorized by the user on 2026-10-17** ("I
authorize that Mednafen modification"), after `EMU-012` found stock Mednafen
insufficient for agent-driven experiments.

## Current Versus Required Capability

| Need (M3 experiments, `EXP-0025` onward) | Stock 1.32.1 | Required |
| --- | --- | --- |
| Read memory | Hand-typed `D` dumps | Agent reads any address space to a file |
| Write memory | Hand-typed `L` loads | Agent writes bytes directly |
| Breakpoints | Hand-typed `Shift+W`; each hit halts until a human presses `R` | Agent sets and clears them; hits can be **logged and continued** or halted |
| Registers at a hit | Visible only on screen | Written to a log file with PC and hit number |
| Act right after a hit | Manual step and load (failed in `EXP-0025` Part 2) | A queued write applied after the hitting instruction executes, optionally filtered by PC |
| Halt control | Keyboard only | `pause`, `step`, `run`, and "run N frames, then halt" |
| States | Slot hotkeys | Save and load to explicit paths |
| Screenshots | `F9`, counter-named | PNG to an explicit path |

## Why Stock Is Inadequate

See the `EMU-012` matrix in `docs/mednafen.md`. Every memory and debugger action
needs the user to type into a prompt (no paste), to relay screenshots, and to beat
the running game's timing. The only remote mode (`-remote`) supports settings
only.

## Alternatives Considered

| Alternative | Rejected because |
| --- | --- |
| GUI automation (AppleScript keystrokes, `screencapture`) | Needs Accessibility and Screen Recording grants (`screencapture` is currently denied to the agent). Prompt typing is still timing-fragile, and registers would need OCR. |
| Stock `-remote` | Settings commands only |
| Another emulator with scripting | Would discard the validated Mednafen evidence chain (extractor, checkpoints), and Saturn accuracy differs. BizHawk is not native on macOS. |
| Save-state editing only | Covers memory writes at checkpoints, but not breakpoints, registers, or halts |
| **Minimal frontend patch** | **Chosen** |

## Minimal Modification

The patch touches only the **frontend driver**; there are no changes to the Saturn
core or emulation:

- **New file:** `src/drivers/agent.inc`, included by `debugger.cpp` so it can use
  the existing breakpoint, stepping, and register helpers.
- **`debugger.cpp`:** two calls in `CPUCallback` (breakpoint hit and
  post-instruction hook).
- **`main.cpp`:** a poll in `MDFND_Update` (game thread, every frame and while
  halted) and a frame counter in `GameLoop`.
- **`debugger.h`:** two declarations.

It is enabled **only** when the environment variable `MEDNAFEN_AGENT_DIR` names a
directory. Unset, the binary behaves like stock (one `getenv` at first poll).

### Protocol

The protocol is file based, and the game thread polls it.

1. The client writes `cmd.tmp` in the agent directory and renames it to `cmd`.
2. Mednafen reads it, deletes it, executes each line, and writes `resp.tmp`,
   then renames it to `resp`. The first response line echoes `id`; every command
   then gets `ok …` or `err …`.
3. Breakpoint hits and post-hit actions are appended to `events.log`:
   `hit n=… frame=… pc=… PC=… R0=… … MACL=…`.

| Command | Effect |
| --- | --- |
| `id <token>` | Echoed back, to match responses |
| `status` | `halted=0/1 frame=N pc=XXXXXXXX` |
| `spaces` | Lists address-space names (`workraml`, `workramh`, `vdp1vram`, …) |
| `regs` | Group 0 registers (CPU), `NAME=hex` |
| `read <space> <hexaddr> <len> <path>` | Raw bytes to a file |
| `write <space> <hexaddr> <hexbytes>` | Writes bytes |
| `bp write\|read\|pc <ranges…>` | Same syntax as the debugger prompts; an empty list clears that type |
| `bpmode halt\|log` | Stock halting (default), or log-and-continue |
| `onhit <pcfilter\|any> write <space> <hexaddr> <hexbytes>` | After a hit whose PC matches, apply the write once the hitting instruction has executed |
| `onhit clear` | Removes queued actions |
| `pause` / `step` / `run` | Halt control |
| `frames <N>` | Run N frames, then halt |
| `savestate <path>` / `loadstate <path>` | Only while not halted (upstream warns against loading while stepping) |
| `screenshot <path>` | PNG of the last emulated frame (no debugger overlay) |

The Python client is `tools/mednafen/agent.py`, with tests.

## Maintenance Cost

- The patch is about 400 lines against 1.32.1 only.
- It is kept as `vendor/mednafen/patches/0001-agent-interface.patch`, applied to a
  **separate** copy of the stock source (`vendor/mednafen/src-agent/`) and built in
  `vendor/mednafen/build-agent/`.
- The stock tree and binary (`ca9bec5f…`) stay untouched for comparison runs.

## Validation Plan

1. **Stock equivalence.** With `MEDNAFEN_AGENT_DIR` unset, the patched binary boots
   the original image like stock.
2. **Read.** `read workramh` at a paused instant equals the extractor output of a
   state saved at the same instant (`savestate`, then `mcs_extract`).
3. **Write.** A write, then a read back, round-trips. A load restores the
   original.
4. **Breakpoint log.** Rerunning `EXP-0025` Part 1 in log mode records PC
   `060AF724`/`060AF728` with R0 = record pointer and R1 = `060F249E`, matching
   the user's manual halts.

## Provenance

- Upstream: <https://mednafen.github.io/>, release 1.32.1, archive
  `mednafen-1.32.1.tar.xz`, SHA-256 `de7eb94a…3832`, GPL-2.0. The patch inherits
  GPL-2.0.
- Build: same configure options as `EMU-002`. See `vendor/mednafen/README.md`.

## Build and Validation Results (2026-10-17)

- **Patch:** `vendor/mednafen/patches/0001-agent-interface.patch`, SHA-256
  `c30146ef…5244`, 592 lines. Applied to a copy of the stock drivers, it
  reproduces `src-agent/src/drivers` exactly.
- **Binary:** `vendor/mednafen/build-agent/src/mednafen`, SHA-256
  `fe0edb99f1ffe63aeb1923ac5fbe2a9c719aa29bd116803e0b446b04731eb02c`. Same
  configure options as stock. No compiler warnings from the patched files.
- **Fix during validation:** the first build (`a463ca28…`) split file paths on
  spaces, so `loadstate` of a slot file failed. Paths now take the rest of the
  line.

| Check | Command(s) | Result |
| --- | --- | --- |
| V1 smoke | `status`, `spaces`, `regs` on the original image | 13 address spaces; SH-2 registers returned. Boot log: `T-1238G`, 4 MiB cart. |
| V2 read = state | `loadstate` slot 5 (`ab60af86…`), then one command file: `read workramh`, `read workraml`, `savestate`, `screenshot` | Both reads are **byte-identical** to `mcs_extract` of the state saved in the same poll (WRAM-H `7dabeef8…`, WRAM-L `8feacb42…`). The screenshot shows the paused fight. |
| V3 write and halt control | `pause`; write `1234` to `0x060F9E66`, read back, restore; `step`, `run`, `frames 30` | Round trip exact and restored. `savestate` is refused while halted. `frames 30` halted 30 frames later. |
| V4 breakpoint log | `tools/mednafen/ko_capture.py` during one human KO from slot 5 | **Pass**: hits at `060AF724`/`060AF728` with R1 `060F249E`, matching the manual halts. A post-KO checkpoint replays the transition exactly with no input. Forcing writes verified in `EXP-0025` Part 2. |

Note: the register named `PC` reads 0 when halted by `pause`, but is valid inside
breakpoint hits, as logged in `events.log`. `RPC` is the SH-2 pipeline PC.

Several clients may share one Mednafen (for example `session_recorder.py` and
`ending_driver.py`, `END-010`): `Agent.command` holds an exclusive `flock` on
`lock` in the agent directory for each command exchange. The patch itself is
unchanged.
