# EXP-0018: Trace the Load of the Ryu Quote Table

Task: `DISC-001`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

## Observation

- `EXP-0017` disproved verbatim or plain-text storage of the table on disc.
- The table (WRAM-L `0x002091AC-0x0020966B`) is absent at the title screen and
  present from the first fight onward.
- WRAM-H `0x06094FD8` changes from `00000000` (title) to `002091AC` (fights), inside
  a run of 4-byte entries that are either placeholders or WRAM-L addresses.
- The `EXP-0014` runbook confirms that CPU write breakpoints fire with the debugger
  hidden.

## Hypothesis

A CPU routine writes the table during the pre-fight load from a source buffer that
holds transformed data. A write breakpoint on the table catches that routine, and
its registers identify the source buffer.

## Controlled Change

None to memory. Only write breakpoints are added, during a load started from a
checkpoint taken before the table exists.

## Prediction

- With write breakpoints `002091AC-0020966B 202091AC-2020966B` set at the
  checkpoint, starting the match halts in a routine whose registers include a
  destination inside the table and a source pointer outside it. The source might
  be WRAM-H, WRAM-L, cart RAM, or a CD-block-related address.
- A second run with a breakpoint on `06094FD8-06094FDB` halts when the slot entry is
  written. The surrounding code identifies the loader that registers the table.

If no breakpoint fires, the table is written by DMA or another non-CPU path. That
would be recorded as a limitation (`docs/known_unknowns.md`).

## Procedure (to be expanded into a step table before the run)

1. **Checkpoint.** From a cold boot, go to arcade mode character select and pick
   Ryu and Ken. Before the fight loads, freeze with `Option+A`, save to slot 6
   (C2 is archived), and take an F9 screenshot. Verify by extraction that the
   table is absent.
2. **Run 1 (table writes).** Load the checkpoint. In the CPU view, set
   `Shift+W` to `002091AC-0020966B 202091AC-2020966B`, hide the debugger, and
   continue into the match. At each of the first three halts, record PC, R0-R15,
   and PR with a screenshot, pressing `R` between halts. Then clear the
   breakpoint.
3. **Run 2 (slot entry).** Reload the checkpoint and repeat with
   `06094FD8-06094FDB`.
4. **Dumps.** While halted at the first useful break, dump the memory around each
   source-pointer register with `D`. Paused-state dumps are allowed; do not load a
   state or reset while halted.

## Actual Result

Run on 2026-10-17. Two Mednafen processes were used:

- Process 61938 (log `local/mednafen/logs/disc001-exp0018.log`) made the checkpoint
  and the first breakpoint run.
- That process was left halted after a state load during a breakpoint stop, so it
  was terminated and relaunched as process 63317 (log `disc001-exp0018-run2.log`)
  for the dump run.

Source identity matched the manifest before and after.

### Checkpoint

The character-select screen with nothing picked was saved to slot 6 under frame
advance:

- state SHA-256 `dc1658644e509ca3879c10ee274d5e12f69fc190f4f9d46ada1a9ce588dee47c`,
  3,989,216 bytes, archived as `exp0018-charselect.mc6`;
- F9 screenshot `-0045.png`, 22,782 bytes, SHA-256 `aacb4d3e…accbf`.

### Breakpoint

Write breakpoints `002091AC-0020966B 202091AC-2020966B` fired **immediately after
Ryu was picked, before Ken**, still on character select. The values below are read
from the user's screenshot; individual digits may be misread from the debugger
font.

- **Stop point:** PC `0603E446`, `mov.b r0,@r9`.
- **Registers:**
  - R9 `002091AC` (destination, the table start);
  - R2 `0020911B` (match source);
  - R12 `00000003` (bytes left in the match);
  - R14 `FFFFF000` (window mask);
  - R1 `0603F164` (input pointer);
  - R3 `00000024`, R7 `00000003`, R4 `0603E478` (context);
  - PR `0603E380`.
- **Listing (`0603E40C-0603E47E`):** a literal copy loop and a match loop. The match
  loop reads two bytes into `v`, sets length = `(v & 15) + 3` and source
  = `r9 + ((v >> 4) | 0xFFFFF000)`, then copies byte by byte. Input refills are
  through `bsr 0603E456`.

### Paused dumps (process 63317, same breakpoint)

| File (ignored, `local/mednafen/dumps/`) | Size | SHA-256 |
| --- | ---: | --- |
| `e18-wramh.bin` (High Work RAM) | 1,048,576 | `a264631fa14af0feb558f33c1ef8ee44b9755c665dfb2a4eaffedcfec42b7794` |
| `e18-wraml.bin` (Low Work RAM) | 1,048,576 | `57ffa710f54012911fdf3ccb0418757675f8f483d098a4ab171b32e772730fc6` |

- **Decompressor context.** The R4 context at WRAM-H `0x0603E478` contains
  `00207F98`, `0603E41C`, `06040E1C`, `06040E30`, and the ASCII name **`mc09.pac`**.
- **Input buffer.** WRAM-H `0x0603E988-0x0603F187` (2,048 bytes) is
  **byte-identical** to `MC09.PAC` file bytes `0x4800-0x4FFF`. The file is
  `MC09.PAC;1`, LSN 8,246, 25,128 bytes, SHA-256 `6c096573…0016`. This buffer is a
  one-sector input window.

### Offline reproduction

`tools/disc/pac_lzss.py` decodes `MC09.PAC` as follows:

- **Header.** Six big-endian words: `00000000 80006215 00000000 00000000 0000620D
  0000B548`.
- **Stream.** Starts at `0x18`. Flag bytes are read MSB first; bit 0 is a literal
  and bit 1 is a two-byte match as above.
- **Size.** Decoding consumes exactly `0x620D` bytes and outputs exactly `0xB548` =
  46,408 bytes, matching the header's fourth and fifth words. Three trailing bytes
  remain.
- **Output hash.** SHA-256 `6a6d8119842d52b494f41b76b28eabe58a9459ca9dab607f91a6adfede11065a`.

Comparison of the decoded output with WRAM-L (output offset 0 = `0x00200000`):

| WRAM-L source | Equal bytes | First difference |
| --- | ---: | --- |
| At the breakpoint (`e18-wraml.bin`) | all 37,292 bytes before the write pointer | `0x002091AC`, the write pointer |
| State A (pre-KO) | 45,999 / 46,408 | `0x0020008F` |

In state A the 16-record table `0x002091AC-0x0020966B` (decoded offset `0x91AC`)
is identical. The 409 differing bytes in state A are in scattered short runs
elsewhere. They were not interpreted.

Generality (`SUPPORTED` only): all 23 `MC*.PAC` files decode with exactly their
declared stream length (report `exp0018_pac_report.json`, SHA-256 `878046fa…6037`).
52 of 79 `.PAC` files decode this way. The other 27 have other layouts that were
not interpreted.

## Conclusion

`CONFIRMED`: Ryu's win-quote table is stored LZSS-compressed in `MC09.PAC`.

- Picking Ryu decompresses the file's stream (offset `0x18`, length `0x620D`) to
  WRAM-L `0x00200000`, 46,408 bytes.
- The table is decoded offset `0x91AC-0x966B`.
- The decompressor reads the file one 2,048-byte sector at a time through a WRAM-H
  buffer.

The decoder reproduces memory byte for byte, and anyone can rerun it offline.

## Uncertainty and Alternatives

- **Header.** The meaning of header words 1-3, including `0x80006215`, and the
  three trailing bytes is unknown.
- **Pre-output matches.** Behavior when a match reaches before the output start is
  unverified (decoded as zero).
- **Patching.** Whether the game checks a checksum or the file size has not been
  tested. That is `DISC-002` work.
- **Other files.** That `MCxx` numbering maps to characters is a `HYPOTHESIS`
  (only MC09 = Ryu is observed).
- **Unrun step.** Run 2 (a breakpoint on the `0x06094FD8` slot entry) was not
  needed and was not run.
