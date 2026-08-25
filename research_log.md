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
