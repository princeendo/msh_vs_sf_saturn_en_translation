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

## 2026-08-24 19:34 CDT - SESSION-0007

Task: DOC-005

Goal:
Catalog a small set of legally inspectable Saturn localization projects that provide
specific methods for future experiments without transferring game-specific facts.

Observation:
The repository had no evaluated project corpus. Public patch indexes contain many
released Saturn translations, but publication or download access does not grant code
reuse rights, and many repositories omit a license or mix source with derived assets.

Hypothesis:
A license-first search would identify a small corpus covering source verification,
text round trips, guarded patching, disc rebuilds, and runtime reload checks, while
explicitly excluding ambiguous or unlicensed material.

Action:
Searched GitHub repository metadata and Saturn translation indexes, inspected
immutable repository revisions, license files, README documentation, manifests,
tests, and representative patch/rebuild code. Retrieved five commit archives with
curl 8.7.1 and hashed them with shasum 6.02:

```text
devil_summoner_tools 1e1483fb72584ad5dc39f07dff5e2ef5750dd69a
  4977408 bytes
  1a008b377254b3df84ab8149bf259bfa031298178abf8e7d8a895ecdedfdda9d
langrisser3-english bee5a495eba18bbec0872faa552df47f4370f040
  1938981 bytes
  236294909f5c9e0cb4235af3514a3fcd71b7fdf321ae069d7d48aa858623cc72
culdcept_saturn_tools 098142497c4b86e7c30b1ff98a8fb6cc032525e1
  48093 bytes
  797e908786fe2a8ff8e6f7e0353c93b1d9cdbc4194fab9657c82889bedf48b23
pcrown 26def6fd9c2f804fc30ec90c95afa98974cafa02
  4601139 bytes
  39e989c47321f3e74e154bdf9ae9e2eeb2aaf325095db5e39571f91d186dc2b1
new-parm-archives-tools 1453906aef0e87eefe240ee976fbf6d53a071e63
  439108 bytes
  7d37c53e2a9efa33a6a1bfa9e0f36191f8ca1a7b3432070159e8cdc7402b20d2
```

Result:
One project provides explicitly scoped 0BSD source and three provide GPL source with
clear method value. Together they support source manifests, no-edit round trips,
expected-byte patch guards, structured text/control records, capacity checks,
growth-aware ISO updates, raw-sector EDC/ECC repair, mixed-mode output verification,
and testing after a reload boundary. None was run against copyrighted media in this
task.

`new-parm-archives-tools` has conflicting MIT scope statements between its README and
NOTICE and is therefore documentation-only pending clarification. The released Rabbit
Saturn fighting-game translation has no detected repository license and is retained
only as a question-generating lead. SegaXtreme is treated as a discovery index, not a
license authority.

Conclusion:
`SUPPORTED`: the selected corpus meets `DOC-005` provenance, license, technique, and
transferability criteria. No project establishes an MSHvSF structure or behavior, and
no project code or game-derived asset was copied. No experiment record or discovery
entry is warranted.

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
Begin `DOC-006` to identify authoritative release provenance for official English
MSHvSF post-fight text. M1 remains blocked by `GATE-M0`.

## 2026-08-24 20:02 CDT - SESSION-0008

Task: DOC-006

Goal:
Identify authoritative candidate releases for official English MSHvSF post-fight text
and define the evidence needed to accept wording and correspondence.

Observation:
The repository named the US arcade release as primary and US PlayStation as secondary,
but had no revision identities, hashes, or reliability assessment. Search results also
exposed a period quote guide under several platform categories without independent
release evidence.

Hypothesis:
A pinned MAME catalog, Redump-compatible PlayStation identity, and official contextual
materials would establish release provenance, while direct capture would remain
necessary for wording and Japanese-English correspondence.

Action:
Pinned arcade and PlayStation catalog evidence to signed MAME 0.289 tag `mame0289`,
commit `f34f02505e32c1993c6a782b6814232cbfc74e36`; retrieved and hashed its CPS-II
source and PSX software list. Retrieved and hashed the archived official arcade and
US PlayStation manuals. Inspected Redump disc 12632 metadata, Capcom's current
collection page, the ESRB record, and Robert Iu's 1999 quote guide.

```text
MAME 0.289 cps2.cpp  977277 bytes
  a8c09ef83841d75b81a4b2ee8ac029ebf8eecb6a743b016abb33e3d46e861602
MAME 0.289 psx.xml   3919227 bytes
  d5c9acd791513686a6e94061f2efb49f0c46d13260aa0465ade8ebe84a0fbc1f
arcade operator manual PDF 3393718 bytes
  709fc6257bef27d07f01fc004adc20ff215fe6afb1eea742c03882318876f48e
US PlayStation manual PDF 6452890 bytes
  ddaa9fb8f8974a034af26628caf55b544fceffa05ebbd627c966ed2ccb136840
```

Result:
MAME identifies two original US arcade revisions: `mshvsfu`, `USA 970827`, and
`mshvsfu1`, `USA 970625`, with distinct program ROM fingerprints. Capcom's modern
collection labels a separate `USA 970707` release, whose relationship to the MAME
sets is unresolved. Redump disc 12632 and MAME's software list identify US
PlayStation `SLUS-00793` through a complete single-track fingerprint.

The operator and console manuals corroborate official products but contain no quote
corpus. The 1999 GameFAQs guide explicitly derives from US PS1 and only speculates
that arcade should be close; it is therefore a candidate index, not authoritative
arcade wording. No Japanese-English correspondence was found or asserted.

Conclusion:
`SUPPORTED`: bibliographic and reproducible identity evidence is sufficient to close
`DOC-006`. Exact wording remains `UNKNOWN` until direct capture from verified media,
and correspondence remains `UNKNOWN` until the staged `REF-001` through `REF-005`
context experiments. No quote text is added to translation data. No experiment record
or discovery entry is warranted.

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
Begin `DOC-007` to catalog XvSF Saturn translation and research references without
comparative analysis or modification. M1 remains blocked by `GATE-M0`.

## 2026-08-24 18:20 CDT - SESSION-0009

Task: ENV-007

Goal:
Record the immutable identity of the supplied MSHvSF Saturn JP source image without
tracking copyrighted disc contents.

Observation:
`/Users/colinwhite/Downloads/Marvel Super Heroes vs. Street Fighter (Japan)` contained
one CUE descriptor and twelve BIN components: one MODE1/2352 data track followed by
eleven audio tracks as described by the supplied CUE. The source directory was not
modified. The repository already ignored `local/` and optical-disc media extensions.

Hypothesis:
Copying the complete set to `local/disc_images/mshvsf_saturn_jp/`, retaining the CUE
beside its BIN components, and tracking only a hash manifest will provide a reproducible
local input without placing the image in version control.

Action:
Copied all files with preserved names and metadata:

```text
mkdir -p local/disc_images/mshvsf_saturn_jp
cp -p "/Users/colinwhite/Downloads/Marvel Super Heroes vs. Street Fighter (Japan)"/* local/disc_images/mshvsf_saturn_jp/
./invenv.sh python -m tools.disc.hash_source \
  --description "Locally supplied Marvel Super Heroes vs. Street Fighter (Japan) Saturn disc image; release identity as named, not independently verified" \
  --json local/disc_images/mshvsf_saturn_jp/*
```

The command reported all thirteen components, with the filenames, sizes, and SHA-256
values recorded in `references/mshvsf/saturn_jp/README.md`.

Result:
The copied files have the same sizes and SHA-256 values as the supplied source files:
the data track is 452,397,792 bytes, the eleven audio tracks range from 3,238,704 to
10,600,464 bytes, and the CUE is 1,697 bytes. No source or copied media file is tracked.
The disc layout itself was not inspected or inferred.

Conclusion:
`CONFIRMED`: the supplied source identity is reproducibly recorded for ENV-007, and
the complete local image set is available at the documented ignored path. This confirms
identity and artifact placement only; it does not confirm any target disc-layout,
filesystem, encoding, or caption-storage claim.

Verification commands and outcomes:

```text
set -e; for source in "/Users/colinwhite/Downloads/Marvel Super Heroes vs. Street Fighter (Japan)"/*; do cmp -s "$source" "local/disc_images/mshvsf_saturn_jp/${source##*/}"; done
  Passed; every source and copied component byte-matched.
./invenv.sh python -m tools.disc.hash_source --json local/disc_images/mshvsf_saturn_jp/*
  13 files reported; values matched the tracked manifest.
git check-ignore -v local/disc_images/mshvsf_saturn_jp/*
  All 13 files matched the existing local/ ignore rule.
```

Next action:
Continue the current M0 task sequence. Before any M1 work, inspect this untouched image
under a documented tool configuration and record the target layout separately.

## 2026-08-24 20:30 CDT - SESSION-0010

Task: EMU-001

Goal:
Select one exact unmodified stock Mednafen release for the M0 evaluation and record
the provenance, license, expected host requirements, and selection boundary before any
build or runtime claim.

Observation:
The repository had already retrieved the upstream `mednafen-1.32.1.tar.xz` archive and
recorded its identity, but `EMU-001` remained open. The upstream release page lists
`1.32.1` as the latest release dated 2024-04-05. Its general and Saturn documentation
are valid as of `1.32.1`; the Saturn page identifies MSHvSF Japan product `T-1238G` as
requiring 4 MiB extended RAM. The release page provides Windows binaries but no macOS
binary. The current host is Darwin 25.5.0 arm64 with 12 logical CPUs.

Hypothesis:
Mednafen `1.32.1` source is the most reproducible stock candidate for this project,
provided its source identity and GPL license are recorded and macOS arm64 remains an
explicit build hypothesis rather than an assumed capability.

Action:
Rehashed the existing external archive and inspected its top-level license file:

```text
shasum -a 256 /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/mednafen-1.32.1.tar.xz
  de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832
stat -f '%N %z bytes' /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/mednafen-1.32.1.tar.xz
  3,571,236 bytes
tar -xOf /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/mednafen-1.32.1.tar.xz mednafen/COPYING
  GNU GENERAL PUBLIC LICENSE, Version 2, June 1991
uname -srm
  Darwin 25.5.0 arm64
sysctl -n hw.ncpu hw.memsize hw.model
  12 / 25769803776 / Mac16,8
```

Result:
The archive identity matches the prior provenance record: filename
`mednafen-1.32.1.tar.xz`, size 3,571,236 bytes, and SHA-256
`de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`. The archive's
`mednafen/COPYING` is GNU GPL version 2. The upstream Saturn documentation states
that official Saturn builds target some 64-bit architectures including AArch64 and
recommends at least a quad-core Intel Haswell-class CPU at 3.3 GHz base and 3.7 GHz
turbo. Those statements define expected requirements only; no local build or runtime
behavior was tested. The upstream source-build notes additionally list
`build-essential`, `pkg-config`, SDL 2.0.5 or newer, libFLAC, and zlib, with Debian
Stretch package names as examples, and list successful compilation on FreeBSD, Linux,
NetBSD, OpenBSD, and Windows. They do not establish a macOS build.

Conclusion:
`SUPPORTED`: `1.32.1` is selected as the exact unmodified stock release for this
investigation. The selection is source-bound and reproducible, is appropriate for
testing the documented MSHvSF 4 MiB cartridge requirement, and does not authorize a
Mednafen modification. macOS arm64 build success remains `UNKNOWN` pending `EMU-002`.
`EMU-001` meets its acceptance criteria.

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
Run `EMU-002` to acquire or use the exact external source archive, document host
dependencies and build options, build pristine stock Mednafen, record the binary hash,
and perform only the specified smoke test. Do not patch Mednafen.

## 2026-08-24 19:28 CDT - SESSION-0011

Task: EMU-002

Goal:
Build the selected unmodified Mednafen `1.32.1` source release on the macOS arm64
research host and record reproducible provenance without booting a target image.

Observation:
The previously retrieved archive was available at the recorded temporary path. Its
identity matched `EMU-001`: filename `mednafen-1.32.1.tar.xz`, size 3,571,236 bytes,
and SHA-256 `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`.
The host provided Apple Clang 21.0.0, GNU Make 3.81, `pkg-config` 2.5.1, Homebrew
6.0.18, SDL2 2.32.70 through `sdl2-compat`, libFLAC 1.5.0, and zlib 1.2.12.

Hypothesis:
The pristine `1.32.1` archive can configure and compile natively on this macOS arm64
host with the Saturn module and internal debugger enabled, using the detected stock
dependencies and no source patch.

Controlled change:
Only the build environment and out-of-tree generated build files changed. The source
was extracted unchanged under ignored `vendor/mednafen/src/`; no source file was
patched. Configure options explicitly enabled `--enable-debugger` and `--enable-ss`;
all other options remained at upstream defaults.

Procedure and exact commands:

```text
mkdir -p vendor/mednafen/src vendor/mednafen/build
tar -xJf /var/folders/mm/pxsndw4s4pv_djh93l0yrvc00000gp/T/opencode/mednafen-1.32.1.tar.xz --strip-components=1 -C vendor/mednafen/src
cd vendor/mednafen/build
PKG_CONFIG=/opt/homebrew/bin/pkg-config CC=/usr/bin/clang CXX=/usr/bin/clang++ ../src/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

The first `make -j12` invocation was terminated by the tooling timeout after 120
seconds while compiling; it emitted no compiler or linker failure. The same unchanged
build was resumed with `make -j12` and a 600-second command timeout and completed with
exit status 0. `./config.status --config` recorded the configure arguments and the
automatic compiler flags.

Actual result:
The resulting native arm64 Mach-O binary was
`vendor/mednafen/build/src/mednafen`, size 21,322,536 bytes, SHA-256
`ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`. Its build
information reported Mednafen `1.32.1`, Apple LLVM 21.0.0, zlib 1.2.12, SDL2 2.32.70,
libFLAC 1.5.0, and an emulation-module list containing `ss`.

Smoke test:

```text
MEDNAFEN_HOME="$PWD/../../../local/mednafen" ./src/mednafen -help
```

Run from `vendor/mednafen/build`, this exited successfully without a BIOS or game
image and printed the command-line help. The GNU-style `--version` spelling was also
tested and rejected as `Unrecognized argument: --version`; it is not the smoke-test
command for this build.

Conclusion:
`CONFIRMED`: stock Mednafen `1.32.1` configures and builds natively on this macOS
arm64 host with Saturn and debugger support enabled, and the resulting binary passes
an isolated no-image smoke test. This does not confirm target boot, 4 MiB cartridge
behavior, input, screenshots, save states, or debugger semantics.

Uncertainty:
The build emitted numerous upstream and SDK deprecation/unused-option warnings. No
target BIOS or game image was used, and no runtime debugger workflow was tested.

Next action:
Proceed to `EMU-003`, using the verified binary and project-local runtime root. Do not
begin target boot or debugger experiments before the configuration strategy is
documented.

## 2026-08-24 19:52 CDT — SESSION-0012

Task: EMU-003

Goal:
Isolate stock Mednafen configuration, runtime artifacts, and diagnostic output from
user-global state, then verify a repeatable launch and cold-relaunch procedure.

Observation:
`local/mednafen/` already contained the generated 1.32.1 configuration and ignored
runtime directories. No Mednafen process held the existing zero-byte lock file before
testing. The stock binary, both selected BIOS aliases, and the source-image identity
records were unchanged.

Hypothesis:
Setting `MEDNAFEN_HOME` to the ignored project-local root will cause stock Mednafen to
load configuration and place runtime state and retained diagnostics below that root,
without requiring a tracked copy of the generated host-specific configuration.

Controlled change:
Only runtime invocation and ignored generated artifacts changed. The source image,
BIOS files, stock Mednafen source, and stock Mednafen binary were not modified.

Action:
Verified the following identities before launch:

```text
vendor/mednafen/build/src/mednafen  21322536 bytes
  ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587
local/mednafen/firmware/sega_101.bin  524288 bytes
  dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac
local/mednafen/firmware/mpr-17933.bin  524288 bytes
  96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f
```

Ran the configuration smoke test:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen -help
```

The process reported base directory
`/Users/colinwhite/workspace/personal/msh_vs_sf_saturn_en_translation/local/mednafen`,
loaded `local/mednafen/mednafen.cfg`, and loaded `7904` valid settings with zero
unknown settings.

Ran the target launch twice, ending each instance after Saturn initialization and
rerunning the identical command:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue"
```

For the retained third run, stdout and stderr were redirected to ignored
`local/mednafen/logs/emu003-launch.log`, 4,282 bytes, SHA-256
`341c7816182d74902dff457ae00655cd46d6f3784c3d0dd7d7a79edba94dfe91`. The run
reported software ID `T-1238G`, selected `Cart: 4MiB Extended RAM`, initialized
Saturn audio and OpenGL video, and used the project-local paths for firmware,
per-game configuration, and cheats. It also created ignored Saturn save data:

```text
local/mednafen/sav/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.bkr
  32768 bytes, SHA-256 6a0d5bcdf8c8243c4f6b8666e76aa0fc8f4eef56df7993b414f3fa7bb3a3e141
local/mednafen/sav/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.smpc
  12 bytes, SHA-256 d56cfb76c84202e39548d613ffe49c390ec69ee9c657d22dd7d7953919bcbe60
```

After each termination, no Mednafen process retained the lock file. The generated
configuration remained ignored. A host automation attempt to send the configured
screenshot and save-state hotkeys timed out, produced no screenshot or state file,
and was not treated as a successful action test.

Result:
The local-root launch, configuration load, runtime save-data placement, diagnostic
log placement, and cold-relaunch procedure all behaved as predicted. The target
initialization also reproduced the database-selected 4 MiB expansion-cart setting.
The launch emitted two source-input warnings: the CUE `CATALOG` directive is
unsupported by this build, and the adjacent `.sbi` file is absent. Neither source
file was changed. No normal game-screen endpoint was recorded.

Conclusion:
`CONFIRMED` for `EMU-003`: the project-local runtime root is usable and isolates the
tested configuration, save data, and retained diagnostic output from user-global
state. The generated configuration remains local because its host-specific input
bindings are not stable project metadata. This result does not close `EMU-004`,
`EMU-005`, `EMU-007`, `EMU-008`, or `EMU-009`; screenshot and interactive save-state
actions require a later controlled input test.

Uncertainty:
The in-emulator reset hotkey, screenshot action, and interactive save/load-state
actions remain unverified. The missing SBI and unsupported CUE directive may affect
later boot validation and require a separate source-format experiment; no conclusion
about their impact was drawn here.

Verification commands and outcomes:

```text
git diff --check
  Passed.
bash -n setup_venv.sh invenv.sh
  Passed.
./invenv.sh pytest
  4 passed.
./invenv.sh ruff check .
  All checks passed.
./invenv.sh ruff format --check .
  54 files already formatted.
./invenv.sh mypy tools tests
  Success: no issues found in 10 source files.
./invenv.sh python -m tools.disc.hash_source --description
  "MSHvSF Saturn JP source identity verification" --json
  local/disc_images/mshvsf_saturn_jp/*
  All 13 source-image component hashes and sizes matched the recorded manifest.
```

Next action:
Begin `EMU-004` to document whether the target reaches a normal game screen. Keep the
local root and exact launch convention unchanged.

## 2026-08-24 20:42 CDT — EXP-0001

Task: EMU-004

Goal:
Reach and document a stable, visibly rendered MSHvSF Saturn game screen using
the selected stock Mednafen build, project-local configuration, recorded BIOS,
and untouched source image.

Observation:
`EMU-003` initialized the target and reported software ID `T-1238G` and
`Cart: 4MiB Extended RAM`, but stopped before a normal game-screen endpoint.
The source image, stock binary, BIOS aliases, and local configuration were
available unchanged. The source CUE still produced the previously recorded
unsupported `CATALOG` and missing `.sbi` warnings.

Hypothesis:
Continuing the boot/title flow with the existing keyboard configuration will
reach a stable, visibly rendered MSHvSF title or menu screen.

Action:
Verified all 13 source-image component hashes before launching. Verified the
stock binary hash `ca9bec5fd7bb8fbdec6ff7bf9bbfdac6906b8802e1e50813ae716256e7ca2587`
and canonical BIOS hashes. Launched the unchanged command twice under the
project-local `MEDNAFEN_HOME`. On the retained second run, after the window was
focused, sent Enter, waited three seconds, and sent the configured Mednafen
snapshot key through macOS System Events. Exited with the configured host F12
command.

Result:
The retained run log was 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`. It
recorded `T-1238G`, `MARVEL SUPER HEROES VS. STREET FIGHTER`, area `J`, and
`Cart: 4MiB Extended RAM`. Mednafen created the ignored screenshot
`local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter (Japan)-0001.png`,
352x240 pixels, 22,616 bytes, SHA-256
`4c19283ec7c84b6b7690fa526e3323a7e0121efa75fa5fa9c6e88bf3c24f0d85`. Visual
inspection showed the stable title screen and mode menu. Mednafen exited
cleanly, and the post-run source-image hashes matched the pre-run manifest.

Conclusion:
`CONFIRMED`: EMU-004's normal game-screen endpoint is reproducibly reached by
the recorded stock launch and input sequence. This does not independently
close EMU-005, EMU-006, EMU-007, or EMU-008.

Next action:
Begin `EMU-005` with a separate controlled observation of 4 MiB expansion-RAM
operation. Preserve the exact launch root and source identity.

## 2026-08-24 21:17 CDT — EXP-0002

Task: EMU-005

Goal:
Validate the required 4 MiB Saturn expansion-RAM configuration with a controlled
runtime observation separate from the `EMU-004` automatic-detection boot.

Observation:
The `EMU-004` run reported `Cart: 4MiB Extended RAM` while using `ss.cart=auto`,
but a configuration value alone was not sufficient evidence for EMU-005.

Hypothesis:
Forcing `ss.cart=extram4` will initialize the 4 MiB extended-RAM model and allow
the untouched MSHvSF image to reach the same stable title-screen endpoint.

Action:
Verified all 13 source-image component hashes before launch and verified the stock
Mednafen binary and both canonical BIOS alias hashes. The exact forced launch was:

```text
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen -ss.cart extram4 \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu005-extram4-run3.log 2>&1
```

The first host automation attempt timed out before evidence capture. A short retry
captured a black window before the title flow completed. Those attempts were not
used as endpoint evidence. Two extended cold runs then sent Enter, waited through
the boot flow, and captured the window at approximately 20 and 35 seconds. A final
cold run repeated the title endpoint and confirmed that refocused F12 terminated
the emulator without a fallback signal. The persisted local setting was restored
with `-ss.cart auto -help`.

Result:
Every forced run log reported:

```text
SGID: T-1238G
SGNAME: MARVEL SUPER HEROES VS. STREET FIGHTER
SGAREA: J
Cart: 4MiB Extended RAM
```

The 20-second capture showed the legal notice. The 35-second captures showed the
MSHvSF title screen with `PRESS START BUTTON`. The successful repeated runtime log
was 4,190 bytes with SHA-256
`e3ff1139f0774d6bb34160d315f6d496386ff5cdf75c7e63564e7862224156f2`. The two title
captures were 5,964,265 bytes with SHA-256
`8d1bb3fd2e6f6eaa48a9f0df4d4399774bc48d072d11086e4f2b73f94812882b` and 6,035,363
bytes with SHA-256
`9fa0dc7e1189c4740cbaa6c2f0b11a265424d3b75de597a91540ceffe200bc51`.

The post-run source identity report matched the same 13 manifest entries and the
local configuration was returned to `ss.cart auto`.

Conclusion:
`CONFIRMED`, scoped to the tested runtime path: explicit `extram4` selection is
honored by stock Mednafen 1.32.1 for MSHvSF and supports repeatable operation to
the title screen. This does not directly test cartridge RAM reads, writes, or
boundaries, and the existing CUE/SBI warnings remain unresolved.

Next action:
Proceed to the next unblocked M0 research task, `DOC-007`. Keep `EMU-006` blocked
until the physical fightpad and OS identity are available.

## 2026-08-24 21:58 CDT — SESSION-0014

Task: EMU-006

Goal:
Determine why the identified 8BitDo M30 cannot yet be configured as Mednafen's
Saturn port-1 controller, using one backend comparison without modifying the
emulator or source image.

Observation:
macOS HID enumeration recognizes `8BitDo M30 gamepad` over USB with VID `0x2DC8`
and PID `0x5006`. SDL HIDAPI can enumerate the HID path, but the SDL joystick and
gamepad APIs report no devices. Stock Mednafen consequently logs only
`Initializing joysticks...` during startup.

Hypothesis:
The failure is caused by SDL device/backend support or the M30's current USB
controller mode, rather than by Mednafen's Saturn port configuration.

Action:
Ran the minimal SDL probe through the SDL2-compat library linked by the stock
Mednafen build, then ran the same probe through Homebrew's native SDL2 library
using a temporary derived binary with only its dynamic-library path changed.
Inspected current upstream SDL HIDAPI 8BitDo support for the M30 product ID.

Result:
Both SDL2-compat and native SDL2 runs reported `driver=<none> joysticks=0`.
Current upstream SDL HIDAPI 8BitDo support lists several 8BitDo product IDs but
not PID `0x5006`. No repository files, Mednafen binary, or source-image component
was modified.

Conclusion:
`SUPPORTED`: the observed blocker is at or below SDL device exposure, and is not
explained by SDL2-compat alone. `UNKNOWN`: whether another documented M30 USB
mode exposes a supported protocol. EMU-006 remains `BLOCKED`; no mapping has been
claimed and no binary modification was made.

Next action:
Change only the M30's documented USB mode, reconnect it, and repeat the HID and
SDL enumeration probes. If SDL exposes a joystick, configure and validate port 1;
otherwise document the mode-independent blocker and evaluate the next permitted
stock-input option.

## 2026-08-25 08:29 CDT — EXP-0003

Task: EMU-006

Goal:
Configure the identified 8BitDo M30 for Saturn port 1 without modifying the stock
Mednafen binary or any source-image component.

Observation:
The physical M30 was connected in the documented wired macOS mode using `A + Start`.
In that mode macOS presents it as a PS4-compatible `Wireless Controller`, and SDL
reports `PS4 Controller` with six axes, twelve buttons, and one hat. Mednafen records
joystick ID `0xecccd365fc40db2f0006000c00010000`.

Hypothesis:
The M30's macOS/PS4 presentation can be mapped to the Saturn Digital Gamepad using
the SDL button and hat-compatible indices exposed by stock Mednafen.

Controlled change:
Only the ignored local Mednafen profile changed. The stock binary, source image,
BIOS, and emulator source remained unchanged. Keyboard bindings were retained as
fallbacks.

Action:
Configured port 1 as `gamepad` with D-pad hat-compatible buttons 12/13/14/15,
A/B/X/Y as buttons 0/1/2/3, Z/C as buttons 4/5, and Start as button 9. Launched the
untouched target with the exact stock binary and recorded the output in
`local/mednafen/logs/emu006-mapping-run.log`.

Result:
The profile loaded with `7904 valid settings and 0 unknown settings`. The target
launch enumerated the recorded joystick and reported `Cart: 4MiB Extended RAM`. The
retained log is 4,248 bytes with SHA-256
`c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c`.

Conclusion:
`CONFIRMED` for local profile parsing, M30 joystick enumeration, and the configured
required Saturn control set. L/R are intentionally excluded from EMU-006 by scope
decision because the tested Mednafen device models did not expose usable bindings
and MSHvSF checkpoint capture does not require them. EMU-006 is `DONE`.

Uncertainty:
EMU-007 must still record in-game expected-versus-observed controls and emulator
shortcut behavior. The SDL button numbering is based on the M30's documented macOS
PS4-compatible presentation and the selected Mednafen SDL device identity.

Next action:
Run EMU-007 to validate the required controls in-game and test screenshot, pause,
frame advance, save/load state, and slot-selection shortcuts where available.

## 2026-08-25 — EXP-0004

Task: EMU-007

Goal:
Validate the required physical M30 controls in-game and test the useful stock
Mednafen shortcuts without changing the source image or emulator binary.

Observation:
`EMU-006` had already confirmed the M30 profile parsed and the selected stock build
enumerated the device. Runtime action behavior and shortcut availability remained
unverified. A standard Mac keyboard did not provide a reliable Pause/Break key.

Hypothesis:
The configured M30 controls and available shortcuts will produce their intended
runtime behavior in MSHvSF; pause may be unavailable on this host despite its
generated SDL binding.

Action:
Verified the 13 source-image component hashes before launch, verified the stock
binary and canonical BIOS hashes, and launched:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  > local/mednafen/logs/emu007-validation.log 2>&1
```

The physical M30 was used for the required controls only. The configured screenshot,
frame-advance, normal-run, save-state, load-state, and slot-selection actions were
tested. The generated pause binding was tested as configured; temporary F1 and F4
host bindings were also tried only in the ignored local profile. The stock binary,
BIOS, and source image were not modified.

Result:
The user reported the expected in-game behavior for D-pad up/right/down/left,
A/B/C, X/Y/Z, and Start. The user also reported successful use of every tested
shortcut except pause. F1 opened Mednafen help; F4 produced no pause response. No
new screenshot or state file remained under the configured local directories after
the run. The retained runtime log is 4,248 bytes with SHA-256
`c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c` and records
joystick ID `0xecccd365fc40db2f0006000c00010000`, software `T-1238G`, area `J`, and
`Cart: 4MiB Extended RAM`.

The post-run source identity command reproduced every pre-run size and SHA-256
value. The generated profile retained its original SDL Pause scancode 72 after
the temporary binding attempts.

Conclusion:
`SUPPORTED` for the required M30 runtime mapping and the available tested shortcuts.
Pause/unpause is `UNKNOWN` on this Mac host, not a confirmed capability. EMU-007
meets its documentation acceptance criteria with the unavailable shortcut explicitly
recorded.

Next action:
Proceed to EMU-008 only; do not begin EMU-009 until EMU-008 is complete. The pause
unknown may be revisited if a physical Pause/Break keyboard becomes available.

## 2026-08-25 09:08 CDT — EXP-0005

Task: EMU-008

Goal:
Verify that stock Mednafen 1.32.1 can produce reproducible emulator-generated
screenshots of a described MSHvSF scene under the project-local runtime configuration.

Observation:
`EMU-004` and `EMU-005` reached the MSHvSF title/menu scene, and `EMU-007` reported
that the configured snapshot shortcut worked, but no dedicated EMU-008 screenshot
record had been completed. The selected profile maps `command.take_snapshot` to F9,
stores snapshots under `local/mednafen/snaps/`, and uses the `%f-%p.%x` filename
template.

Hypothesis:
Pressing F9 with the focused Mednafen window at the title/menu scene will create a
local screenshot, and the same procedure will succeed after a second cold launch.

Action:
Verified all 13 source-image component hashes, the stock binary hash, and both
canonical BIOS hashes before launch. Ran the established project-local launch twice,
using the validated Enter input to reach the title/menu scene, waiting approximately
35 seconds, pressing F9 once, and exiting with F12. The source image, BIOS files,
stock binary, and runtime configuration were not changed.

Result:
The first capture was `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter
(Japan)-0003.png`, 19,270 bytes, 352x240, SHA-256
`7e20cb6ce62bdb0924d1ce00c1a5ac48e74cebbcd2d6fb7fcbb14902e460dfd7`. The second
cold capture was `local/mednafen/snaps/Marvel Super Heroes vs. Street Fighter
(Japan)-0004.png`, 24,589 bytes, 352x240, SHA-256
`5a655bd264448b796948b9f6c0766c3f160611e5edf6e4f2479863e80775761b`. Both visibly
show the MSHvSF title screen with `PRESS START BUTTON`; the second has an expected
animated-background variation. Both run logs were 4,248 bytes with SHA-256
`c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c` and recorded
software `T-1238G`, area `J`, and `Cart: 4MiB Extended RAM`. The post-run source
identity report matched every pre-run component. No emulator process remained; a
zero-byte stale ignored lock from the previous session was removed after confirming
that no process owned it.

Conclusion:
`CONFIRMED`: the established stock Mednafen screenshot action reproducibly captures
the described title/menu scene into the project-local snapshot directory. The result
confirms visual-evidence capture only; it does not establish binary provenance beyond
the separately recorded launch identities, nor does it imply byte-identical captures
for an animated scene.

Next action:
Begin EMU-009, verifying repeated save/load-state return to an equivalent documented
checkpoint. Do not treat save-state files as RAM dumps.

## 2026-08-25 09:21 CDT - EXP-0006

Task: EMU-009

Goal:
Verify that stock Mednafen 1.32.1 can repeatedly save and restore an equivalent
documented MSHvSF checkpoint without treating save-state files as RAM dumps.

Observation:
EMU-005, EMU-007, and EMU-008 were complete. The configured stock save/load
shortcuts had been observed, but no dedicated experiment had recorded state paths,
hashes, and repeated visible restoration.

Hypothesis:
Saving at the title/menu checkpoint, advancing to mode selection, and loading with
`F7` will return to the title scene. The sequence will reproduce after a cold launch
using another state slot.

Controlled change:
Only ignored runtime state/screenshot artifacts and save/load inputs changed. The
Mednafen binary, source image, BIOS aliases, and 4 MiB cartridge configuration were
unchanged. Because automation could not generate the physical M30 Start event, the
ignored local profile temporarily changed `ss.input.port1.gamepad.start` from the
M30 joystick binding to `keyboard 0x0 40`; the original M30 line was restored before
exit. This temporary mapping was used only for the visible checkpoint transition.

Result:
The first corrected visible-window run saved slot 0 as
`local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc0`,
3,173,150 bytes, SHA-256
`e54380cfca308b1058f92d2840bde73e4c13d01bd9e4b8c864be82a3730b66db`. The title
checkpoint screenshot was 3,332 bytes, SHA-256
`2a0b629ac9b2a6410ef9c62a1a9b2c6c06c1f608b863efd997061f1104f95290`; the mode
selection screenshot was 21,380 bytes, SHA-256
`d01d1a311f092d704e43cae91468bf6af6673b18387a71bcebea8100fb49dea4`; and the
post-load title screenshot was 24,616 bytes, SHA-256
`47e3d5eaade0f88d52aee28f6bbb69fdb95ef794a05b994cde066374f5c96b48`.

The second cold run saved slot 1 as
`local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc1`,
3,244,032 bytes, SHA-256
`88e8945770bf26667e9006aff476b4d5dab7f7eaef93fa471ceced343dc93d80`. The title
checkpoint screenshot was 18,847 bytes, SHA-256
`987a6da8844ba28f7901643435cf536fcc422ac3ff496ed185f09630d8c26a6e`; the mode
selection screenshot was 24,114 bytes, SHA-256
`2d4772688b0c2477d0594d7b5909b2c8046dbddeb1bababc709f9443777ab07e`; and the
immediate post-load title screenshot was 19,145 bytes, SHA-256
`0d94b909bf94286ed7d960bc21171ec49ea843d161cba221ea6e656a61431310`.

All six screenshots were 352x240 RGB PNGs. A delayed post-load capture in the
second run showed attract mode rather than the title scene; an immediate repeated
load/capture returned the title scene. All three run logs were 4,248 bytes with
SHA-256 `c8e2ff0aec4d9535f3fe4e5d25bbe09f5ee49d19fdccba016461c004ffc7699c`.
The source identity command reproduced all 13 manifest hashes after the runs.

Conclusion:
`CONFIRMED`: stock Mednafen 1.32.1 repeatedly restored the equivalent visible
checkpoint across two cold launches and two state slots. State bytes are not claimed
to be identical, and no state file was treated as a RAM dump.

Uncertainty:
The title screen is animated and transitions into attract mode with elapsed time.
The checkpoint procedure therefore requires an immediate post-load screenshot when
the title scene is the criterion. The first exploratory save made while the emulator
window was off-screen was excluded from evidence and overwritten by the corrected
slot-0 run.

Next action:
Proceed to EMU-010 only. Do not modify Mednafen; debugger access remains a separate
stock-build verification task.

## 2026-10-15 18:55 CDT — EXP-0007

Task: EMU-010

Goal:
Verify stock debugger access against MSHvSF and obtain repeatable paused memory dumps
to serve as reference data for a planned save-state extractor.

Observation:
EMU-009 was done. Read-only source inspection of stock 1.32.1 showed the Saturn
memory-editor address spaces, the dump prompt syntax, and that the
`physical` space is a `TODO` stub with no cartridge-RAM space registered.

Hypothesis:
The debugger opens and CPU step mode pauses and resumes. During a frame-advance pause,
the memory editor dumps the full Work RAM spaces repeatably, and a state saved in the
same pause captures the same instant.

Action:
Pre-run checks matched all 13 source components, the binary, and both BIOS files.
Mednafen was launched with the project-local root and log
`local/mednafen/logs/emu010-exp0007.log`. The user then:

- Opened the debugger and stepped/resumed with `S`/`R`.
- Froze the game with `Option+A` and saved slot 2 with `F5`.
- Cycled the memory editor's address spaces and dumped High Work RAM twice and Low
  Work RAM once.
- Re-dumped both Work RAM spaces and both VDP VRAMs with inclusive end addresses.

Result:
- `Option+1` had no visible effect because the CPU view was already active. `S`/`R`
  froze and resumed emulation.
- The memory editor listed 13 address spaces and no cartridge RAM.
- The first dumps were 1,048,577 bytes, most likely because the `+` was omitted while
  hand-typing. The inclusive form adds the wrapped offset-0 byte, which matched.
- The two High Work RAM dumps had identical SHA-256
  `cdc1593260a18e98c3feae4e124bd9b93852176baefe91ec724e834be85ec2f0`.
- Inclusive re-dumps were exactly 1 MiB and equal to the first 1 MiB of the earlier
  dumps.
- The slot-2 state is 3,848,175 bytes, SHA-256
  `2c735816da8fcb2dbcc63b62da05454a07994f3f08ba56239fbe5fa829c65eb9`.
- Mednafen exited 0. Post-run source, binary, and BIOS hashes matched.

Conclusion:
`CONFIRMED` for stock debugger access, CPU pause/resume, the listed address spaces,
and repeatable paused WRAM/VRAM dumps. The stock memory editor cannot dump the 4 MiB
cartridge RAM. The prediction of exact 1 MiB `+`-form dumps was not tested as
intended because of the typing error. The inclusive form is now the documented
hand-typed form.

Next action:
Per the approved win-quote plan:

1. Record the save-state extractor task and the AGENTS.md save-state amendment.
2. Build the extractor.
3. Validate it against `wram-c.bin`, `wraml-b.bin`, `vdp1vram-a.bin`, and
   `vdp2vram-a.bin` from the slot-2 state.

EMU-011 is READY.

## 2026-10-15 19:20 CDT — EXP-0008

Task: DBG-006, DBG-012

Goal:
Build a save-state region extractor and validate it against the `EXP-0007` paused
debugger dumps.

Observation:
The stock debugger dumps only through hand-typed prompts and has no cartridge-RAM
space. Save states contain `MAIN/WorkRAML`, `MAIN/WorkRAMH`, `CART_EXTRAM/LO` and
`HI`, `VDP1/VRAM`, and `VDP2/VRAM`, written per `src/state.cpp`.

Hypothesis:
Swapping each stored 16-bit element reproduces the debugger dumps. The unswapped
stored bytes do not.

Action:
- Amended `AGENTS.md` (validated extraction only) and re-sequenced `TASKS.md`:
  - redefined `DBG-006`;
  - added `DBG-012` and `REF-007`;
  - moved transcription after checkpoint capture;
  - added the C1′ noise-control and C2 states.
- Implemented `tools/memory/mcs_extract.py` with 11 synthetic tests.
- Extracted the slot-2 state in both byte orders and compared each region with
  `cmp`.

Result:
- WRAM-H, WRAM-L, VDP1 VRAM, and VDP2 VRAM in `saturn` order were identical to
  `wram-c.bin`, `wraml-b.bin`, `vdp1vram-a.bin`, and `vdp2vram-a.bin`.
- The `state` order differed by 554,066, 574,942, 214,932, and 172,764 bytes,
  respectively.
- Re-extraction was byte-identical.
- Checks passed: pytest (15), ruff check, ruff format, and strict mypy.

Conclusion:
`CONFIRMED` for the four validated regions. Unswapped state order is `DISPROVEN`
as Saturn byte order. Cartridge-RAM extraction remains `HYPOTHESIS`.

Next action:
`REF-007`: observe win-quote selection with Ryu/Ken, saving each pre-KO state under
frame advance.

## 2026-10-15 19:40 CDT — EXP-0009

Task: REF-007

Goal:
Determine whether a pre-KO checkpoint fixes the win quote, so that C1/C2/C1′
quote-screen states can be planned.

Observation:
Selection behavior was unknown, and the user suspected it might be fixed per
fighter pairing.

Hypothesis:
For a fixed pre-KO checkpoint, varying only the KO timing or finisher does not change
the quote.

Action:
Ryu/Ken saved pre-KO states in slot 3 (vs Vega) and slot 4 (vs Sakura). The user
replayed each six times with different finishers, Ryu on point and no tag, and took
`F9` screenshots 18-29.

Result:
Slot 3 produced quotes Q1, Q1, Q2, Q3, Q4, Q5. Slot 4 produced Q3, Q6, Q2, Q7, Q8,
Q9. Hadouken gave different quotes in the two fights, and Q2/Q3 appeared against
both opponents. Every screen used the same joint Ryu/Ken portrait. Source identity
was unchanged.

Correction: an agent inference of "team-voiced" quotes, drawn from the joint
portrait and `俺達`, was wrong. The user reports that there are no team quotes, and
the quote belongs to whoever landed the KO, which was Ryu in every replay. That rule
is consistent with all twelve screens but untested for a Ken KO.

Conclusion:
The hypothesis is `DISPROVEN`. It is `SUPPORTED` that selection varies after the
checkpoint and is not determined by move or opponent alone.

Do not retry the "quote is fixed per matchup or checkpoint" assumption. One
checkpoint can yield both C1 and C2.

Next action:
`REF-001`: choose the first Ryu quote from Q1-Q9. Then capture quote-screen states
for DBG-003, saving each with `Option+A` then `F5`.

## 2026-10-15 19:55 CDT — SESSION-0015

Task: REF-001

Goal:
Choose the first Ryu win quote for M0/M1 work.

Observation:
`EXP-0009` showed nine Ryu quotes. The user does not read Japanese and expressed no
preference.

Action:
Selected Q3 on technical grounds only: it appeared against both Vega (snapshot 21)
and Sakura (snapshot 24), which supplies a same-text, different-history control.
Recorded `data/translations/ryu_post_fight_q3.json`, which matches the
`quote.schema.json` fields. It holds the route, evidence hashes, and open REF-004
correspondence questions. Japanese text is left empty until REF-003 review.

Result:
REF-001 is `DONE`; REF-002 and DBG-001 are `READY`.

Next action:
Capture the pre-KO state (A) and the Q3 quote-screen state (C1) with screenshots,
saving under frame advance (`DBG-001`, `DBG-003`, `REF-002`).

## 2026-10-15 20:25 CDT — EXP-0010

Task: DBG-001, DBG-003, DBG-005, REF-002

Goal:
Capture a pre-KO checkpoint and quote-screen checkpoints for differential memory
analysis.

Observation:
Q3, the REF-001 pick, did not recur from state A (slot 5) in about 100 user replays,
although it appeared in 2 of 12 `EXP-0009` replays.

Hypothesis:
One pre-KO checkpoint can yield different-quote and same-quote quote-screen states,
each reloadable to the same scene.

Action:
- Dropped the Q3 targeting. The user saved the next quote screens in fixed slots
  without visual matching.
- A wall-clock same-quote control (2 s wait) produced a black screen. It was redone
  with 10 counted frame advances.
- Added save-time thumbnail export to `mcs_extract`, because F9 screenshots were
  taken seconds away from the saves.
- Archived slots 0-4 to ignored `research/savestates/archive-2026-10-15/` with
  verified hashes before reuse.

Result:
- Checkpoints: A = slot 5, C1 = slot 7 (Q10), C1′ = slot 0 (Q10), C2 = slot 6 (Q8),
  C2b = slot 8 (Q11).
- Slot 5 reloads were byte-identical screenshots. Slot 7 reloads both showed Q10.
- All EXP-0009/0010 pre-KO checkpoints were saved during the game's own pause menu.
- Quotes Q10 and Q11 were new, for 11 distinct Ryu quotes in total.

Conclusion:
`CONFIRMED` checkpoint set. The working subject moves from Q3 to Q10. Why Q3 did not
recur is `UNKNOWN`.

Do not retry targeting a specific quote by replay until selection is understood.
States B and D are deferred to `BACKLOG`.

Next action:
DBG-007/DBG-008 (WRAM extraction is already available via the validated tool),
DBG-009 diff tooling, DBG-010 search tooling, then DBG-011 comparisons
(C1 vs C2, C1 vs C1′).

## 2026-10-15 21:00 CDT — EXP-0011

Task: DBG-007, DBG-008, DBG-009, DBG-010, DBG-011

Goal:
Acquire WRAM for each `EXP-0010` checkpoint, build diff and search tooling, and test
whether the visible quote is stored as Shift-JIS in WRAM.

Hypothesis:
During the quote screen, the visible quote is present in WRAM-L or WRAM-H as
Shift-JIS bytes.

Action:
- Extracted WRAM from A, C1, C1′, C2, and C2b. Repeat extraction was
  byte-identical.
- Added `tools/memory/diff.py` (with schema) and `tools/text/search.py`, with
  synthetic tests.
- Diffed C1 vs C2 and C1 vs C2b, excluding C1/C1′ changes.
- Searched eight Shift-JIS fragments from the three quotes.

Result:
- WRAM-L C1/C1′ changes: 0. WRAM-H C1/C1′ changes: 6,263 bytes.
- Quote-dependent changes:
  - WRAM-L: 1,192 bytes (C2) and 1,332 bytes (C2b);
  - WRAM-H: 14,932 bytes (C2) and 14,482 bytes (C2b).
- All Shift-JIS fragments had 0 matches in every dump.
- Structured candidates:
  - WRAM-L sequential 16-bit entries (`0x0C..`, `0x0D..`, with `FFFF` gaps);
  - a WRAM-H 28-byte record chain at `0x06014798` with VDP2 VRAM destinations;
  - a high-entropy WRAM-H block at `0x06014CB5-0x0601677B`.

Conclusion:
Shift-JIS quote text in WRAM at the quote screen is `DISPROVEN` for the tested
fragments. Do not retry plain Shift-JIS WRAM searches at this checkpoint without a
new reason, such as an earlier state B. Quote-dependent WRAM candidates are
`SUPPORTED` but have no established meaning.

Next action:
`DBG-013`: compare VDP VRAM across quote checkpoints. Then `EMU-011`: a write
breakpoint on the candidates.

Checks: pytest (31 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-15 21:40 CDT — EXP-0012

Task: DBG-013

Goal:
Locate the quote glyph pixels in VDP VRAM.

Hypothesis:
The rendered quote glyph pixels are in VDP2 VRAM, at addresses that differ between
quotes and are stable between C1 and C1′.

Action:
- Diffed VDP2 and VDP1 VRAM across C1, C1′, C2, and C2b.
- Added `tools/memory/vdp1_sprites.py` to walk VDP1 command lists and render
  sprites, with tests.
- Rendered all sprites, then only the text-area color groups.

Result:
- VDP2 VRAM is identical in C1, C2, and C2b. It changes only in C1′, in one ~146 KB
  block that looks like a transition, so C1′ is not a clean VRAM control.
- Rendering VDP1 sprites alone reproduces the win screen.
- Sprites with color word `0x61E0` (38 per state, two rows) draw exactly the quote
  text.
- Glyph cells are 16x16, 4 bpp, one per distinct character, at about
  `0x05C4B080-0x05C4BEFF`. Shared characters (`の い 拳 を る え な ！ !!`) are
  byte-identical across quotes at different addresses.
- State A has no `0x61E0` sprites.

Conclusion:
VDP2 as the text location is `DISPROVEN`. Text drawn by VDP1 sprites from
per-character font glyph cells is `SUPPORTED`. Do not search VDP2 VRAM for quote
text on this screen.

Next action:
`DBG-014`: search WRAM (and, labeled `HYPOTHESIS`, cart RAM) for the exact glyph
cells to locate the font. Derive character codes, then search for quote code
sequences.

Checks: pytest (37 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-15 22:20 CDT — EXP-0013

Task: DBG-014

Goal:
Locate the glyph font and the quote character codes.

Hypothesis:
Glyph cells are copied verbatim from a font table resident in WRAM or cart RAM.

Action:
- Searched WRAM-L, WRAM-H, and cart RAM for the exact 4 bpp glyph cells.
- Searched for 1 bpp body masks (shifts, bit orders, row slices).
- Built per-quote glyph-identity patterns.
- Added `tools/text/pattern_search.py` (equality-pattern search, with tests) and
  searched 16-bit runs.

Result:
- Only the last glyph cell of each quote was found, at WRAM-H `0x0601CEEC` (a
  staging buffer). No 1 bpp font matched.
- Each quote's 38-cell pattern matched exactly once in WRAM-L of the pre-KO state:
  Q8 at `0x00209290`, Q10 at `0x0020940C`, Q11 at `0x0020953C`.
- The table (15 records of 76 bytes from `0x002091F8`) is identical in all states.
- 44 glyph identities map consistently to codes. 46 of 46 kana fit
  `0x0800 + (SJIS2 − 0x9F)` (hiragana) and the matching katakana rule.
- The current quote also appears as `(0x5000|code, 0x0002)` entries at WRAM-H
  `0x060ED80A`, only on quote screens.

Conclusion:
A resident font in WRAM/cart as cells or as uncompressed 1 bpp is `DISPROVEN`; do
not repeat those searches without a new format hypothesis. 16-bit quote-code
records in WRAM-L plus the per-screen WRAM-H buffer are `SUPPORTED`. Confirmation
needs the gated `RE-012` mutation.

Next action:
Complete the remaining GATE-M0 prerequisites, starting with `EMU-011`. Then, in M1,
change one code in the Q10 record and observe the screen.

Checks: pytest (41 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-15 22:45 CDT — SESSION-0016

Task: GATE-M0 amendment; EMU-011 and RE-012 preparation

Decision (user, verbatim): "Amend GATE-M0 so the live RAM mutation (RE-012) depends
only on the technical prerequisites (EMU-011 debugger workflow plus validated
extraction); keep the reference/doc tasks as prerequisites for translation work.
Record the change, then prepare the mutation test."

Action:
- Gate split:
  - `GATE-M0` now depends on ENV, EMU-001..011, REF-001/002/007, and the DBG tasks.
  - New `GATE-TRANSLATION` (DOC-007, DOC-008, REF-003..005) gates `DISC-002`.
  - EMU-012/020 remain required before any Mednafen modification, per `AGENTS.md`
    rule 16.
- Mapped the WRAM-L table. It has 15 records, all 11 observed quotes included
  (Q3 = record 1), plus 4 not yet seen.
- Added `tools/memory/make_patch.py` (with tests) and built
  `re012-aiu-{original,patched,manifest}` (45 writes; manifest SHA-256
  `2df36119…d125`).
- Pre-registered `EXP-0014` (EMU-011) and `EXP-0015` (RE-012).

Result:
No emulator run. The tooling and experiment designs are ready.

Next action:
Run `EXP-0014` with the user at the keyboard.

Checks: pytest (49 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 13:25 CDT — EXP-0014

Task: EMU-011 (and GATE-M0 acceptance)

Goal:
Test stock debugger writes, revert, registers, and write breakpoints before the
first live mutation.

Hypothesis:
`L` writes a file into Low Work RAM while frozen, `D` reads it back exactly, loading
the original restores it, and a write breakpoint on the WRAM-H quote buffer fires
during a replay.

Action:
User session from state A:

- Dumped the table range, loaded the patch, dumped, loaded the original, dumped.
- Set write breakpoints `060ED80A-060ED8A1 260ED80A-260ED8A1` and replayed the KO.

The first `L` attempt failed, most likely from a mistyped long filename; the
retry used short identical copies.

Result:
- Dumps were `78fd5a38…` (before), `08a1a3aa…` (after patch, equal to `p.bin`), and
  `78fd5a38…` (after revert).
- The breakpoint fired before the quote was drawn:
  - PC `060AF8C6`, `mov.w r0,@r6`;
  - R6 is about `060ED80A`, R7 `060ED900`, and R8 `002091FA` (inside the WRAM-L
    table);
  - nearby constants `#76` and `0x5000`.
- The CPU-view memory pane shows `0xAA` (stub).

Conclusion:
The workflow is `CONFIRMED`; EMU-011 is DONE. `GATE-M0` (amended) is accepted, and
the milestone is now M1. That the code reads the WRAM-L table into the WRAM-H
buffer is `SUPPORTED`.

Next action:
`RE-012` via `EXP-0015`.

Checks: pytest, ruff check, ruff format --check, and strict mypy (run at commit).

## 2026-10-17 13:50 CDT — EXP-0015

Task: RE-012 (M1)

Goal:
Confirm that the WRAM-L quote table drives the displayed caption.

Hypothesis:
Changing record codes before the quote screen changes the displayed glyphs.

Action:
From state A, loaded `p.bin` (45 writes: line-1 cells 0-2 of the 15 records at
`0x002091F8+` set to `0801 0803 0805`) or `o.bin` (control) with `L`, verified by
`D`, then KO'd Vega with Ryu. Ran patched ×4 and control ×2, saving each state
and screenshot. One `L` attempt hit an EOF warning from a mistyped end address and
was restarted.

Result:
- Patched runs 1, 3, and 4 showed `あいう` in the predicted cells: Q8 twice, and Q5
  with `もっ` overwritten.
- Patched run 2 selected the unpatched record at `0x002091AC`, a Ken-addressed
  quote with a `0000` placeholder that is shown as ケン.
- Both controls were normal.
- Every saved patched state still contained the patch.

Conclusion:
`CONFIRMED`; M1 reached. The table is 16 records from `0x002091AC`. The `0000`
partner-name placeholder is a `HYPOTHESIS`.

Next action:
`DISC-001` (M2): find what writes the table and where it comes from on disc. A
write breakpoint on `0x002091AC-0x0020966B` during a load is the first candidate
experiment.

## 2026-10-17 14:10 CDT — SESSION-0017

Task: DISC-001 design

Observation:
- The WRAM-L quote table is absent in the `EXP-0006`/`EXP-0007` title states.
- It is present and byte-identical in both `EXP-0009` fights and all `EXP-0010`
  states.
- The Q8 record does not occur in WRAM-H, or in cart RAM (unvalidated), at the title
  screen or during fight 1.
- The CUE declares track 01 as `MODE1/2352` (192,346 sectors) and tracks 02-12 as
  audio.

Action:
- Added `DISC-010` (disc layout) as the file-mapping prerequisite.
- Pre-registered `EXP-0016` (Mode 1 / ISO 9660 inspection plus tooling) and
  `EXP-0017` (verbatim table search).
- Outlined `EXP-0018` (write-breakpoint trace of the table load) for the case
  where `EXP-0017` is negative.

Next action:
`EXP-0016`, which needs no user input.

## 2026-10-17 14:40 CDT — EXP-0016 / EXP-0017

Task: DISC-010, DISC-001

EXP-0016:
- Built `tools/disc/iso9660.py` (Mode 1 sector validation, PVD, directory walk,
  extraction, user-data stream) with synthetic tests.
- Track 01: 192,346 valid Mode 1 sectors, LSN = index.
- PVD: `SEGA SEGASATURN` / `MSH_VS_STREET_FIGHTER`, block size 2,048, root at
  LSN 20, volume space size 216,839 (more than track 01).
- 414 flat, non-interleaved, non-overlapping files.
- Source hashes were unchanged. Result: `CONFIRMED`. The metadata is in
  `references/mshvsf/saturn_jp/iso9660_files.json`.

EXP-0017:
- Hypothesis: the table is stored verbatim on disc.
- Searched the full table, the 16 records, the longest code runs, and byte-swapped
  forms in the 393,924,608-byte user stream: 0 of 66 hits.
- Searched 12 quote fragments as Shift-JIS, EUC-JP, and UTF-16BE: 0 hits.
- Result: `DISPROVEN`. Do not repeat verbatim or plain-encoding disc searches for
  this table.
- Observation: WRAM-H `0x06094FD8` holds the only pointer (`002091AC`). It is
  `00000000` at the title screen, inside a run of `99 00 NN 99` placeholders and
  WRAM-L addresses.

Next action:
`EXP-0018`: a live write-breakpoint trace from a character-select checkpoint.

Checks: pytest (53 passed), ruff check, ruff format --check, and strict mypy.

