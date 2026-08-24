# Research Log

This chronological journal preserves both successful and failed work. Durable,
confirmed findings are separately summarized in `docs/discoveries.md`.

## Entry Template

```markdown
## YYYY-MM-DD HH:MM TZ — EXP-NNNN or SESSION-NNNN

Task: TASK-ID

Goal:

Observation:

Hypothesis:

Action:

Result:

Conclusion:

Next action:
```

## 2026-08-24 15:44 CDT — SESSION-0001

Task: ENV-001 through ENV-006

Goal:
Construct the initial reproducible research repository without beginning M1 reverse
engineering.

Observation:
The repository initially contained only an MIT license and a generic Python
`.gitignore`. Local `uv 0.11.7` and Python 3.14.4 were available.

Hypothesis:
A minimal uv project, explicit operating contract, dependency-gated task plan,
copyright safeguards, and a tested source-integrity utility are sufficient initial
infrastructure for subsequent M0 work.

Action:
Created the repository scaffold, environment wrappers, documentation corpus,
research templates, task graph, and SHA-256 source-identification tool using only
synthetic tests.

Result:
`./setup_venv.sh` selected CPython 3.12.13, generated the uv lockfile, created
`.venv`, and installed the project plus development tools. The synchronized tool
versions used by the checks were pytest 9.1.1, Ruff 0.16.4, and mypy 2.3.1.

The first `ruff format --check .` found one formatting-only issue in
`tools/disc/hash_source.py`. The source was adjusted without semantic change. The
following final commands succeeded:

```text
./setup_venv.sh
./invenv.sh pytest
./invenv.sh ruff check .
./invenv.sh ruff format --check .
./invenv.sh mypy tools tests
bash -n setup_venv.sh invenv.sh
test -x setup_venv.sh && test -x invenv.sh
./invenv.sh python --version
./invenv.sh python -m tools.disc.hash_source \
  --description "Synthetic fixture" --json LICENSE
```

Final outcomes: 4 tests passed; Ruff lint passed; all 54 discovered files were
formatted; strict mypy passed across 10 source files; shell syntax and executable
bits passed; the CLI emitted filename, 1,062-byte size, SHA-256, and supplied
description without modifying `LICENSE`. A second `./setup_venv.sh` completed
successfully, confirming rerun safety.

`git check-ignore` probes confirmed coverage for representative local disc image,
BIOS, derived build, screenshot, save-state, memory dump, trace, extracted file,
Mednafen build, and virtual-environment paths. Probes also confirmed that synthetic
JSON fixtures and tracked research README files are not ignored.

Conclusion:
`CONFIRMED` for repository construction only: the documented uv setup and baseline
quality commands are reproducible in the recorded host environment, and the source
identity utility behaves as tested on synthetic/permitted data. `ENV-001` through
`ENV-006` meet their construction acceptance criteria. No game binary, emulator,
runtime memory, or caption was inspected, and no target reverse-engineering
conclusion was reached.

Next action:
Begin `DOC-001`, collecting authoritative Sega Saturn architecture references and
recording concise, citable claims. `EMU-001` and the other READY M0 documentation
tasks may proceed independently, but M1 remains blocked by `GATE-M0`.

## 2026-08-24 16:35 CDT — SESSION-0002

Task: ENV-007 / local Mednafen BIOS setup

Goal:
Make the supplied local Saturn BIOS set available to Mednafen without
tracking copyrighted binary files, while recording immutable identities.

Observation:
`/Users/colinwhite/Downloads/Sega Saturn BIOS` contained 11 BIOS files, each 524288
bytes. The repository already ignored `*.bin` and recommended local Mednafen state
under `local/mednafen/`.

Hypothesis:
Copying the supplied files to ignored `local/mednafen/firmware/` and providing the two
Mednafen 1.32.1 default filenames from hash-matching supplied files will make the
firmware discoverable without changing the source files or tracking BIOS content.

Action:
Copied all 11 supplied files without renaming them. Created `sega_101.bin` from
`Bios Saturn 1.01 (J) [!].bin` and `mpr-17933.bin` from `Sega Saturn BIOS (EUR).bin`.
Recorded all sizes and SHA-256 hashes in `docs/mednafen.md`, along with the
`MEDNAFEN_HOME="$PWD/local/mednafen"` launch convention. Updated ENV-007's blocker
to identify only the still-missing MSHvSF Saturn JP image.

Result:
The canonical aliases have the documented Mednafen hashes: `sega_101.bin` is
`dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac`, and
`mpr-17933.bin` is
`96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f`. The source
directory was not modified. Runtime boot has not yet been tested because the exact
Mednafen build and MSHvSF source image are not available.

Conclusion:
`SUPPORTED`: the local firmware layout and canonical filenames are consistent with
the Mednafen 1.32.1 documentation and independently match the supplied-file hashes.
`EMU-001` through `EMU-004` are still required before treating firmware use as
runtime-confirmed.

Verification commands and outcomes:

```text
./invenv.sh python -m tools.disc.hash_source --description "Locally supplied Sega Saturn BIOS; filename-based release identity" --json local/mednafen/firmware/*.bin
  13 files reported; every file was 524288 bytes and the hashes matched the manifest.
git check-ignore -v local/mednafen/firmware/*.bin
  All 13 files matched the existing local/ ignore rule.
cmp source files and copied files, including both canonical aliases
  Source copies and canonical aliases byte-matched.
git diff --check
  Passed.
./invenv.sh pytest
  4 passed.
./invenv.sh ruff check .
  Passed.
./invenv.sh ruff format --check .
  54 files already formatted.
./invenv.sh mypy tools tests
  Passed; 10 source files checked.
```

Next action:
Select and document the exact stock Mednafen version under `EMU-001`. ENV-007 remains
blocked until the MSHvSF Saturn JP image path and release description are supplied.

## 2026-08-24 17:01 CDT — SESSION-0003

Task: DOC-001

Goal:
Identify authoritative Sega Saturn architecture references and validate the two
initial work-RAM dump ranges without inspecting target game data.

Observation:
The repository's initial memory-map document labeled WRAM-L
`0x00200000-0x002FFFFF` and WRAM-H `0x06000000-0x060FFFFF`, but both were marked
as awaiting source validation. No platform bibliography had been recorded.

Hypothesis:
Official Sega developer manuals mirrored by archival or third-party hosts would
directly establish the initial ranges and enough system context for later controlled
debugger work, while later Sega corrections would identify relevant caveats.

Action:
Inspected official Sega English-document copies from the Antime mirror and Sega's
1997 electronic corpus from the InfoChunk mirror. Downloaded the three relevant
PDFs outside the repository with curl 8.7.1 and hashed them with shasum 6.02:

```text
curl -L --fail --silent --show-error \
  -o /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-097-R5-072694.pdf \
  https://antime.kapsi.fi/sega/files/ST-097-R5-072694.pdf
curl -L --fail --silent --show-error \
  -o /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-103-R1-040194.pdf \
  https://antime.kapsi.fi/sega/files/ST-103-R1-040194.pdf
curl -L --fail --silent --show-error \
  -o /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-210-110194.pdf \
  https://antime.kapsi.fi/sega/files/ST-210-110194.pdf
shasum -a 256 \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-097-R5-072694.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-103-R1-040194.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-210-110194.pdf
stat -f '%N %z bytes' \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-097-R5-072694.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-103-R1-040194.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-210-110194.pdf
```

The resulting identities were:

```text
ST-097-R5-072694.pdf  1702622 bytes
d56a86087f10c61d0bafaf5dfa0de134f92fe413e6e40f69a656df5192ccc8d3
ST-103-R1-040194.pdf  707231 bytes
0d44855f9ce5a62cbcd08895c1bf647b409651968c420c2b6a96399be1ce5a82
ST-210-110194.pdf  326397 bytes
7842694c3fb747a9db921ac73e2454741d960fe40c2289fc515a2cb2feb7abdb
```

Downloaded the independent Internet Archive copy and compared it byte-for-byte:

```text
curl -L --fail --silent --show-error \
  -o /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/SCUum-archive.pdf \
  https://archive.org/download/237-r-1/SCUum.pdf
shasum -a 256 \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/SCUum-archive.pdf
stat -f '%N %z bytes' \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/SCUum-archive.pdf
cmp \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/ST-097-R5-072694.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/SCUum-archive.pdf
```

The archive copy was 1,702,622 bytes with the same SHA-256; `cmp` produced no
output and exited successfully. The archive item identifies ARK
`ark:/13960/t7hr4p074`.

Reviewed the rendered title, history, and content pages rather than relying on OCR
for exact values. The decisive SCU pages were PDF pages 18 through 22, corresponding
to manual pages 2 through 6: Figure 1.1 for bus composition, Figure 1.3 for the
cache-address map, the cache-hit warning, and Figure 1.5 for cache-through aliases.
The overview claims came from PDF pages 17 through 26, corresponding to manual
pages 6 through 15. The final-specification issue date and WRAM DMA restriction came
from PDF pages 5, 6, and 8, corresponding to manual pages 1, 2, and 4.

Result:
SCU Figure 1.3 labels WRAM-L as the one-Mbyte interval bounded by `00200000H` and
`00300000H`, and WRAM-H as the one-Mbyte interval bounded by `06000000H` and
`06100000H`. Normalized inclusive ranges are therefore
`0x00200000-0x002FFFFF` and `0x06000000-0x060FFFFF`. Figure 1.5 gives respective
cache-through aliases `0x20200000-0x202FFFFF` and
`0x26000000-0x260FFFFF`. The overview independently reports 2 MiB of main RAM.
The final-specification notice item 04 limits SCU-DMA to WRAM-H and prohibits its
use with WRAM-L; this does not prohibit CPU or debugger reads.

The overview's summary table says `DMA 2 ch`, while its detailed SCU table and the
SCU manual describe three CPU DMA channels plus one DSP channel. The later notice
says only two channels may be used concurrently with guaranteed priority. The
conflict is documented rather than collapsed into one unsupported interpretation.

Verification commands and outcomes:

```text
./invenv.sh pytest
  4 passed.
./invenv.sh ruff check .
  Passed.
./invenv.sh ruff format --check .
  54 files already formatted.
./invenv.sh mypy tools tests
  Passed; 10 source files checked.
git diff --check
  Passed.
```

Conclusion:
`SUPPORTED`: the collected official Sega documents, preserved through identified
third-party mirrors, directly support the initial platform ranges and architecture
summary. This is source-supported platform documentation, not a controlled runtime
experiment and not a game-specific discovery. `DOC-001` meets its acceptance
criteria; no experiment record or `docs/discoveries.md` entry is warranted.

Next action:
Begin `DOC-002` to collect SH-2 architecture, instruction, and debugging references.
Other READY M0 documentation tasks and `EMU-001` remain independent options. M1
remains blocked by `GATE-M0`.

## 2026-08-24 17:28 CDT - SESSION-0004

Task: DOC-002

Goal:
Collect authoritative SH-2 architecture, instruction, and hardware-debugging
references needed to interpret future debugger evidence without inferring target
addresses.

Observation:
The repository had Saturn architecture references but no processor-specific corpus.
`docs/code_map.md` prohibited unmeasured target addresses but did not state which SH-2
semantics must be preserved when reading a trace.

Hypothesis:
The official Hitachi SH-1/SH-2 Programming Manual and SH7604 Hardware Manual would
directly support the bounded processor concepts needed for debugger work, while
leaving Mednafen presentation and game-specific behavior unresolved.

Action:
Retrieved both official-document copies from the Antime mirror with curl 8.7.1 and
hashed them with shasum 6.02:

```text
curl -L --fail --silent --show-error \
  -o /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/h12p0.pdf \
  https://antime.kapsi.fi/sega/files/h12p0.pdf
curl -L --fail --silent --show-error \
  -o /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/sh7604.pdf \
  https://antime.kapsi.fi/sega/files/sh7604.pdf
shasum -a 256 \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/h12p0.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/sh7604.pdf
stat -f '%N %z bytes' \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/h12p0.pdf \
  /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/sh7604.pdf
```

The files were 1,034,304 and 2,211,720 bytes with SHA-256 values
`03364fae725c23980ae76d75f266f760844a6ce4e4ec54b7c40897b180be5d44` and
`262cfff2abec2fa0cef5c5475495d6a4da390eff107ed3a75575827467daab9f`.
Inspected rendered pages for publication identity and sections covering registers,
data formats, addressing, branches, exceptions, and the user-break controller.

Result:
The September 3, 1996 programming manual directly defines the programmer-visible
registers, 16-bit instruction format, effective-address rules, alignment, sign
extension, delay slots, and architectural `PC` convention. The SH7604 Hardware Manual
`ADE-602-085C`, revision 4.0, directly defines exception stacking and a two-channel
user-break controller able to discriminate instruction fetch, data access, read/write,
size, and channel-B data conditions. It warns that data-access breaks do not identify
an exact instruction as precisely as instruction-fetch breaks.

Conclusion:
`SUPPORTED`: the manuals provide a bounded, citable processor corpus for interpreting
future debugger evidence. They do not establish Mednafen behavior, Saturn mappings,
or MSHvSF addresses. `DOC-002` meets its source and summary criteria; no experiment
record or discovery entry is warranted.

Verification commands and outcomes:

```text
./invenv.sh pytest
  4 passed.
./invenv.sh ruff check .
  All checks passed.
./invenv.sh ruff format --check .
  54 files already formatted.
./invenv.sh mypy tools tests
  Success: no issues found in 10 source files.
git diff --check
  Passed with no output.
```

Next action:
Begin `DOC-003` to collect Saturn boot-media, CD block, ISO9660, track, and filesystem
references. M1 remains blocked by `GATE-M0`.

## 2026-08-24 18:42 CDT - SESSION-0005

Task: DOC-003

Goal:
Collect authoritative Saturn boot-media, CD block, ISO 9660, track, and filesystem
references without inspecting or inferring the target image layout.

Observation:
`docs/disc_layout.md` contained source-identity and future-recording rules but no
platform vocabulary for distinguishing tracks, raw sectors, logical sectors, file
extents, and image-container offsets.

Hypothesis:
Sega's Game-CD format, Boot ROM, and CD Communication Interface manuals, bounded by
the ISO 9660:1988 catalog record, would support the concepts needed for later target
inspection while leaving every target-specific field unresolved.

Action:
Retrieved the three official-document copies from the Antime mirror with curl 8.7.1,
hashed them with shasum 6.02, inspected their publication pages and relevant rendered
sections, and checked ISO's official catalog record for ISO 9660:1988:

```text
curl -L --fail --silent --show-error -o <temporary-path>/ST-040-R4-051795.pdf \
  https://antime.kapsi.fi/sega/files/ST-040-R4-051795.pdf
curl -L --fail --silent --show-error -o <temporary-path>/ST-079B-R3-011895.pdf \
  https://antime.kapsi.fi/sega/files/ST-079B-R3-011895.pdf
curl -L --fail --silent --show-error -o <temporary-path>/ST-162-062094.pdf \
  https://antime.kapsi.fi/sega/files/ST-162-062094.pdf
shasum -a 256 <temporary-path>/ST-040-R4-051795.pdf \
  <temporary-path>/ST-079B-R3-011895.pdf \
  <temporary-path>/ST-162-062094.pdf
stat -f '%N %z bytes' <temporary-path>/ST-040-R4-051795.pdf \
  <temporary-path>/ST-079B-R3-011895.pdf \
  <temporary-path>/ST-162-062094.pdf
```

Result:
The files and identities were:

```text
ST-040-R4-051795.pdf  436835 bytes
  066dccf08feb72713f78d371dcaf749cf9aa9ed9264c51629c0fc85d5770f1d2
ST-079B-R3-011895.pdf 247170 bytes
  ee2c05e29091ab7aac76624612b1f2eabd17335e8590883d549ab2d7e3a8ea7b
ST-162-062094.pdf      875729 bytes
  3fc11970edae90fcbafd47966637a0deb2a941b6e7cb335da451bc7acee8d1ad
```

The Game-CD standard directly supports track ordering, sector forms and user-data
sizes, FAD/LSN conversion, system-area and ISO 9660 boundaries, directory records,
and IP structure. The Boot ROM manual supports the bounded claim that boot code is
checked before game startup. The CD interface manual supports host/CD-block transfer,
TOC/session capability, sector filtering and buffering, and its ISO 9660 file service.

An apparent conflict is scope-specific: the Game-CD standard prohibits multisession,
while the CD block supports multisession media generally and refers to the last
session's volume descriptor. Both statements are retained without attributing either
layout to the target.

Conclusion:
`SUPPORTED`: these sources provide a task-oriented platform corpus for a future,
hash-bound target image inspection. No target track, file, extent, sector mode, IP
field, image offset, or rebuild constraint was observed. No experiment record or
discovery entry is warranted.

Verification commands and outcomes:

```text
./invenv.sh pytest
  4 passed.
./invenv.sh ruff check .
  All checks passed.
./invenv.sh ruff format --check .
  54 files already formatted.
./invenv.sh mypy tools tests
  Success: no issues found in 10 source files.
git diff --check
  Passed with no output.
```

Next action:
Begin `DOC-004` to collect documented stock Mednafen debugger commands and limits.
M1 remains blocked by `GATE-M0`.

## 2026-08-24 19:06 CDT - SESSION-0006

Task: DOC-004

Goal:
Record upstream stock Mednafen debugger commands and explicit limitations for the
later selected-version evaluation without claiming local runtime capability.

Observation:
`docs/mednafen.md` required debugger evaluation but did not provide a citable command
baseline. The upstream debugger page labels Saturn as having at least basic debugger
functionality but does not provide Saturn-specific address-space or breakpoint
details.

Hypothesis:
The upstream debugger, general, Saturn-module, and release pages would define a small
documented workflow while leaving module-specific behavior for `EMU-010` and
`EMU-011` to test.

Action:
Retrieved the three upstream HTML pages and the candidate `1.32.1` source archive
with curl 8.7.1, then hashed them with shasum 6.02:

```text
curl -L --fail --silent --show-error -o <temporary-path>/mednafen-debugger.html \
  https://mednafen.github.io/documentation/debugger.html
curl -L --fail --silent --show-error -o <temporary-path>/mednafen-general.html \
  https://mednafen.github.io/documentation/mednafen.html
curl -L --fail --silent --show-error -o <temporary-path>/mednafen-ss.html \
  https://mednafen.github.io/documentation/ss.html
curl -L --fail --silent --show-error -o <temporary-path>/mednafen-1.32.1.tar.xz \
  https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz
shasum -a 256 <temporary-path>/mednafen-debugger.html \
  <temporary-path>/mednafen-general.html <temporary-path>/mednafen-ss.html \
  <temporary-path>/mednafen-1.32.1.tar.xz
stat -f '%N %z bytes' <temporary-path>/mednafen-debugger.html \
  <temporary-path>/mednafen-general.html <temporary-path>/mednafen-ss.html \
  <temporary-path>/mednafen-1.32.1.tar.xz
```

Result:

```text
mednafen-debugger.html 9827 bytes
  13545a2e06adee0ce172f47952a5ca9617ab87ceb074d6cbfde61100c7cfd53d
mednafen-general.html 142106 bytes
  897f6cbd6659d5f53360549a6f2c172164d23b4f3d36db87385071f024098b09
mednafen-ss.html 100442 bytes
  43d0a4a7cfb165b61e38ce2f50d58fd72e7510dd222b267c2bf5304667404c6f
mednafen-1.32.1.tar.xz 3571236 bytes
  de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832
```

The debugger page, last updated 2023-11-25 and valid as of `1.32.0-UNSTABLE`,
documents CPU run/step, PC/read/write breakpoints, watches, low/high-level pokes, and
memory-space dump/load. It explicitly warns that save states and power/reset in step
mode may cause significant malfunctions for Saturn. The general and Saturn pages are
valid as of `1.32.1`; the latter confirms only basic Saturn-module context and the
MSHvSF 4 MiB extended-RAM database entry, not debugger details.

Conclusion:
`SUPPORTED`: upstream documentation provides a bounded command and caution baseline.
Saturn CPU selections, register presentation, address spaces and aliases, graphics
view, high-level poke support, breakpoint timing, and DMA visibility remain
unverified. The archive retrieval is provenance only; no release has been selected or
built. No experiment record or discovery entry is warranted.

Verification commands and outcomes:

```text
./invenv.sh pytest
  4 passed.
./invenv.sh ruff check .
  All checks passed.
./invenv.sh ruff format --check .
  54 files already formatted.
./invenv.sh mypy tools tests
  Success: no issues found in 10 source files.
git diff --check
  Passed with no output.
```

Next action:
Begin `DOC-005` to catalog legally usable Saturn localization projects and bounded
techniques. M1 remains blocked by `GATE-M0`.
