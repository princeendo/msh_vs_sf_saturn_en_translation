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

## 2026-10-17 15:10 CDT — EXP-0018

Task: DISC-001

Hypothesis:
A CPU routine writes the quote table during the pre-fight load from transformed
source data; a write breakpoint identifies it and its source.

Action:
- Saved a character-select checkpoint (slot 6).
- Set write breakpoints on the table and picked Ryu.
- Dumped WRAM-H and WRAM-L while halted.
- Added `tools/disc/pac_lzss.py`, with tests.

The first process stalled after a state load during a breakpoint stop. It was
terminated and relaunched; the checkpoint was unaffected.

Result:
- The breakpoint fired right after Ryu was picked, inside an LZSS decompressor
  (PC `0x0603E446`). Its context names `mc09.pac`.
- The 2 KB input buffer equals `MC09.PAC` bytes `0x4800-0x4FFF`.
- Decoding `MC09.PAC` from `0x18` consumes exactly the header length `0x620D` and
  outputs `0xB548` bytes, equal to WRAM-L (all 37,292 bytes written at the break,
  and the full table in state A).
- All 23 `MC*.PAC` files decode with this format.

Conclusion:
`CONFIRMED`; DISC-001 DONE.

Next action:
DISC-002 is blocked by GATE-TRANSLATION. Propose a marker-only disc patch task to
test re-encoding, size limits, and boot behavior first.

Checks: pytest (58 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 15:30 CDT — SESSION-0018

Task: DISC-002 amendment and EXP-0019 design

Decision (user, verbatim): "Amend DISC-002 to reproduce the M1 あいう marker from a
patched disc (no English needed), keep English for later translation tasks behind
GATE-TRANSLATION, and design the experiment."

Action:
- Rewrote `DISC-002` as the marker disc patch (deps: DISC-001 only).
- Added `DISC-020` (official English caption from disc), which depends on DISC-002
  and GATE-TRANSLATION.
- Gathered design facts:
  - all 23 `MC*.PAC` files use word 1 = `0x80000000 | (word 4 + 8)`, with words
    0/2/3 = 0 and 0-3 pad bytes;
  - `MC09.PAC` uses 13 sectors with no free sectors after (next file `PL0A.PAC` at
    LSN 8,259), and 1,496 slack bytes in its last sector;
  - sectors carry real EDC/ECC.
- Pre-registered `EXP-0019`: splice re-encode, same-size placement, regenerated
  EDC/ECC validated against all source sectors, and cold-boot verification.

Next action:
Build the encoder, sector, and patch tooling, then run `EXP-0019`.

## 2026-10-17 14:40 CDT — EXP-0019

Task: DISC-002 (M2)

Hypothesis:
A derived image that differs only in a re-encoded, same-size `MC09.PAC` (48 marker
codes) boots and shows `あいう` in Ryu's win quotes.

Action:
- Added `tools/disc/sector.py` (EDC/ECC, validated on all 192,346 source sectors),
  the encoder, `pac_patch.py`, and `patch_image.py`, with tests.
- Built the patched MC09.PAC (splice at 20,411; stream 25,090; 14 fill bytes) and
  the derived image (changed LSN 8,246 and 8,255-8,258), twice.
- Ran the offline checks.
- The user cold-booted the derived CUE and won twice with Ryu.

Result:
- Offline: identical builds, valid sectors, only MC09.PAC changed, and the decoded
  payload carries exactly the 48 codes.
- Runtime: `あいう。一つ間違えば…` (Q2) and `あいうた、もっと打て！…` (Q6). Both
  saved states' WRAM-L table equals the patched table.
- Source unchanged.

Conclusion:
`CONFIRMED`; M2 reached.

Next action:
RE-020 (M3) planning, and a Latin-glyph/font-code investigation for English.

Checks: pytest (73 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 14:55 CDT — SESSION-0019

Task: FONT-001 design

Observation:
- Ryu's 16 records use 112 distinct codes (blocks `0x00`, `0x04`, `0x08`,
  `0x09-0x0C`), with no Latin letters or digits.
- The `EXP-0013` font search covered only WRAM and cart RAM, not disc files.

Action:
- Added `FONT-001`, now a dependency of `DISC-020`.
- Pre-registered `EXP-0020`:
  - Phase 1: an offline search of all extracted files and decoded PACs for
    known glyph shapes, then fitting the index↔code rule and rendering an atlas;
  - Phase 1b: a staging-cell write breakpoint if Phase 1 fails;
  - Phase 2: a live display test of candidate Latin codes, plus a separate ASCII
    probe.

Next action:
`EXP-0020` Phase 1, which needs no user input.

## 2026-10-17 15:15 CDT — EXP-0020 Phase 1

Task: FONT-001

Hypothesis:
The quote font is in a disc file (raw or PAC-decoded) as glyph bitmaps that match
the known glyph cells.

Action:
- Added `tools/memory/glyph_codes.py` (79 code→cell pairs from 12 states, no
  conflicts).
- Searched 466 files (397 MB) for exact 4 bpp cells, 1 bpp body masks (MSB/LSB),
  and shadow-free 4 bpp cells and row pairs with shifts. Repeated the shadow-free
  row search on WRAM-L/H and cart RAM.

Result:
- 0 meaningful hits; only 3 coincidental hits on a horizontal-stroke glyph in
  background graphics.
- Glyph cells contain shading values `2`-`A` in addition to body `1` and shadow
  `F`.
- WRAM-H literal pools at `0x0601CEE8` and `0x0601D9E0` reference the staging cell
  (candidate renderer and copy routines).

Conclusion:
H1 is not supported for these formats; do not repeat plain 4 bpp, 1 bpp, or
shadow-free bitmap searches of disc files or work RAM.

Next action:
Phase 1b, a staging-cell write breakpoint, which needs the user.

Checks: pytest (75 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 15:45 CDT — EXP-0020 Phase 1b

Task: FONT-001

Hypothesis:
A write breakpoint on the staging cell halts in the glyph renderer and reveals the
font source.

Result:
- The breakpoint fired before the KO, at PC `0601CEB2`, with R9 = `0279192A` (cart
  RAM).
- Disassembling `0x0601CE00` gave the font format: block and size tables, raw,
  empty, or two-stage mask, column-major run fill.
- The font base is `0x0278CF60`, via the pointer at `0x0601D8E4`.
- `tools/text/font.py` decoded all 79 known glyphs byte for byte from state A's
  cart RAM.
- The atlas shows an ASCII set at codes `0x20-0x7E` (half-width).

Conclusion:
Font location and format are `CONFIRMED`; Latin display is `SUPPORTED`, pending
Phase 2. Bitmap searches failed earlier because glyphs are compressed. Do not
repeat bitmap font searches.

Next action:
Phase 2, a live test showing `ABC` via the table patch.

Checks: pytest (78 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 15:20 CDT — EXP-0020 Phase 2

Task: FONT-001

Hypothesis (H2):
Codes `0041-0043` display Latin A, B, C in a win quote.

Action:
Loaded `abc.bin` (line-1 cells 0-2 of all 16 records = `0041 0042 0043`) with `L`
at state A. Ran patched twice and the original once (control), saving states and
screenshots.

Result:
- Both patched runs showed the Ken-template quote with `A B C` in cells 0-2, but
  faint (8x8 gradient glyphs).
- The control was normal.
- The atlas also revealed full-width quote-style A-Z `0x08E8-0x0901`, a-z
  `0x0902-0x091B`, and 0-9 `0x091C-0x0925`, consistent with the known `！`/`!!`
  codes.

Conclusion:
H2 `CONFIRMED` for `0041-0043`; full-width Latin `SUPPORTED`. FONT-001 is DONE.
The code table is in `data/text/font_codes.json`.

Next action:
A short live test of full-width Latin codes; then RE-020 planning.

## 2026-10-17 15:25 CDT — EXP-0021

Task: FONT-002

Hypothesis:
Codes `08F9 0900 08FC 0902 091D` display full-width `R Y U a 1`.

Action:
Loaded `ryu.bin` (80 writes, line-1 cells 0-4 of all 16 records) at state A. Ran
patched ×2 and control ×1. One dump end address was mistyped (80 bytes too long);
its prefix equals the patch.

Result:
- Patched runs showed `RYUa1くれ、ケン…` (record 0) and `RYUa1前達と闘えて…` (Q9),
  solid and shadowed.
- The control was unchanged. Slot extractions confirm the table state.

Conclusion:
`CONFIRMED`; FONT-002 DONE. `data/text/font_codes.json` updated.

Next action:
RE-020 planning; English layout capacity is an open question.

Checks: pytest (78 passed) and ruff format --check (run before commit).

## 2026-10-17 15:35 CDT — SESSION-0020

Task: LAYOUT-001 design

Observation:
- The font in cart RAM spans `0x0278CF60-0x027BF6A0` (206,656 bytes).
- There are 712 empty codes, with free runs `0x00A8-0x00FF`, `0x0190-0x01DF`,
  `0x0260-0x02AF`, and `0x0C5F-0x0DFF` (417).
- Quotes are a fixed 2 × 19 cells with a 38-entry buffer.

Action:
Added `LAYOUT-001` (now a dependency of `DISC-020`). Pre-registered `EXP-0022`:

- Phase A: font disc source search;
- Phase B: layout-constant disassembly;
- Phase C: a live pair-glyph test using an appended raw glyph in an empty block;
- Phase D: deferred layout change.

Next action:
`EXP-0022` Phases A and B (offline).

## 2026-10-17 16:10 CDT — EXP-0022 Phases A-B

Task: LAYOUT-001

Phase A:
- Hypothesis: the font is on disc verbatim.
- Font fragments were found only in `MEMFIX.PAC`. Its entry 4 (`0x6A558`, 206,656
  bytes) equals the cart font byte for byte.
- `MEMFIX.PAC` has a 13-pair header and 12 uncompressed entries.
- Result: `CONFIRMED`. Load path `SUPPORTED`.

Phase B (partial):
- Added `tools/sh2/disasm.py` with tests.
- Code at `0x060AF740-0x060AF81A` writes quote buffer entries using GBR counters
  and the `trapa #62`/`#63` call convention.
- A flag at `r11+0xCC90` selects line offset 38 or 50, spacing 16 or 12, and count
  17 or 23 (`HYPOTHESIS`: an alternate denser layout).
- `#76` in `EXP-0014` is a struct field offset, not the record stride; that earlier
  reading is withdrawn.

Next action:
Phase C, a same-size raw-glyph replacement in `MEMFIX.PAC` plus an `MC09.PAC`
reference, built into a derived image (refined plan in `EXP-0022`).

Checks: pytest (100 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 16:40 CDT — EXP-0022 Phase C build

Task: LAYOUT-001

Action:
- Added `tools/text/glyph_patch.py` and a `pac_patch --full` option, and extended
  `patch_image` to multiple files, all with tests.
- Built a `Th` pair glyph over raw glyph `0x0725` in `MEMFIX.PAC`, and an
  `MC09.PAC` table patch with cell 0 = `0x0725`.
- The splice re-encode overflowed by 4 bytes, so a full re-encode (446-byte fill)
  was used.
- Built the derived image twice.

Result:
- Offline checks pass: only LSN 4,214 and 8,246-8,258 changed, valid EDC/ECC,
  only the two files differ, exactly one glyph and 16 cells changed, builds
  identical, source unchanged.

Next action:
User cold-boot test of `build/mshvsf_exp0022c_a`.

Checks: pytest (105 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 16:55 CDT — EXP-0022 Phase C boot

Task: LAYOUT-001

Result:
- Cold boot of `build/mshvsf_exp0022c_a`: two Ryu wins showed `Th` in line-1 cell
  0 (Q6 `Thうした…`, Q11 `Th おれは…`).
- No glitches reported.
- Saved states' cart font glyph `0x0725` equals the pair cell, and the WRAM-L table
  equals the patch.

Conclusion:
Pair glyphs are `CONFIRMED`. The `MEMFIX` entry 4 load path is now `CONFIRMED`.
LAYOUT-001 is DONE; recommended route R1, for 76 characters per quote. The open
item is storage for many glyphs.

Next action:
RE-020 planning, or a font-storage expansion experiment.

## 2026-10-17 17:10 CDT — SESSION-0021

Task: FONT-003 design

Observation:
- `MEMFIX` entries load to table-driven destinations: WRAM-H literal tables at
  `0x06040274…` and `0x06041260…`, plus the per-entry structures at `0x0601D7F4…`.
- Entry 10 (256 KB) follows the font in cart RAM, leaving about 2.4 KB of
  headroom.
- The disc has no free sectors between files, and 150 sectors free at the track
  end.
- Recompression gains nothing (glyphs are already minimal; raw glyphs would grow).
- A pair glyph compresses to 37 bytes. Kanji glyphs occupy 76,664 bytes.

Action:
Added `FONT-003`. Pre-registered `EXP-0023`:

- Phase A: lossless repacker;
- Phase B: usage census of all MC*.PAC quote tables;
- Phase C: same-size repack with many pair glyphs, cold-boot tested;
- Phase D: deferred growth or second font region.

Next action:
`EXP-0023` Phases A and B (offline).

## 2026-10-17 17:40 CDT — EXP-0023 Phases A-B

Task: FONT-003

Phase A:
- Hypothesis: a lossless repack is possible.
- Measured the header (code count `0x0C60`), the block table (0 above the count),
  the size table (raw = `0x80`), and data filling the entry exactly.
- `tools/text/font_pack.py` rebuilds entry 4 **byte-identically** (`3d8e9a26…`).
- Result: `CONFIRMED`.

Phase B:
- `tools/text/quote_census.py` (validated on MC09: one 16-record table at `0x91AC`)
  found quote-shaped tables in all 23 MC files (700 codes), plus record-shaped
  runs in ME.PAC/ME.SHX/MM.BIN (516 codes). The union is 839 of 2,872 glyphs.
- Unseen: 1,922 glyphs and 131 KB in total, but `0x01-0x07xx` is UI artwork.
- Unseen kanji: 321 glyphs, 30,235 bytes (about 817 pair glyphs).
- Result: `SUPPORTED` (record-shaped text only).

Next action:
Phase C, a same-size repack sacrificing unseen kanji to add at least 8 pair glyphs
in free codes below `0x0C60`, then a cold-boot test.

Checks: pytest (109 passed), ruff check, ruff format --check, and strict mypy.


## 2026-10-17 — EXP-0023 Phase C build (offline)

Task: FONT-003

- Hypothesis H-C: a same-size font repack can add pair glyphs at free codes below
  `0x0C60` by emptying unseen kanji.
- Added `tools/text/pair_font.py` (tests in `tests/unit/test_pair_font.py`).
- 10 pairs "Is that all you got!" at `0x00A8-0x00B1`. Sacrificed `0x0C5E`,
  `0x0C5D`, `0x0C5C`, `0x0C54` (387 bytes freed for 341 needed).
- `MC09.PAC` line 1 of all 16 records patched by splice (200 fill bytes).
- Derived image `build/mshvsf_exp0023c_{a,b}`, identical builds, track 01
  `5f5ef651…`.
- Offline: iso check clean, 0 invalid sectors, only the target files and cells
  changed.
- Result so far: offline predictions held; the live result is pending a cold boot.

Checks: pytest (113 passed), ruff check, ruff format --check, and strict mypy.

Next action:
Cold boot of `build/mshvsf_exp0023c_a`; two Ryu wins.

## 2026-10-17 — EXP-0023 Phase C cold boot

Task: FONT-003

- Booted `build/mshvsf_exp0023c_a` cold (no state loaded). Two Ryu wins (screenshots
  `-0056`, `-0057`; states archived `exp0023c-slot7`/`slot8`).
- Both showed `Is that all you got!` on line 1, with the original line 2 of records
  4 and 5.
- Cart font, WRAM-L table, and WRAM-H display buffer matched the build in both
  states.
- Result: H-C `CONFIRMED`. FONT-003 `DONE`.
- Open: other uses of the sacrificed kanji and of codes `0x00A8-0x00B1`.

Next action:
`RE-020` (M3 planning). English text waits on `GATE-TRANSLATION`.

## 2026-10-17 — RE-020 M3 planning

Task: RE-020

Observations used:
- Ryu's `MC09.PAC` table has 16 records. Only record 0 holds a `0000` placeholder
  (line 1 is 9 cells). Lines in records 1-15 use 12-19 cells.
- `Q1`-`Q11` are observation-order labels from `EXP-0009`/`EXP-0010`, not record
  indices. `EXP-0023` matched its two wins to records 4 and 5 through the WRAM-H
  display buffer.
- Selection looked random across replays (`EXP-0009`). Seeing all 16 records by
  chance would need about 50 wins (coupon-collector estimate), which is
  impractical for manual play.

Decisions:
- RE-020 is now `IN_PROGRESS` as the umbrella. Subtasks:
  - `RE-021`: record map and offline renderer.
  - `RE-022`: caption compiler.
  - `RE-023` / `EXP-0024`: selection mechanism, a hypothesis about the counter
    `@(76,r12)`.
  - `RE-024` / `EXP-0025`: all 16 records live from one compiled image.
  - `RE-025` / `EXP-0026`: variants (Ryu not on point; another partner; versus
    mode).
- M3 captions are record-identifying markers, not translations, so M3 stays
  independent of `GATE-TRANSLATION`.

Next action:
`RE-021` (offline).

## 2026-10-17 — RE-021 / EXP-0024 record map and offline renderer

Task: RE-021

- Hypothesis: an offline render of a record on a 16-pixel grid reproduces the text
  box, so screenshots can be matched to records.
- Built `tools/common/png.py` (stdlib decoder) and `tools/text/quote_render.py`
  (render, match, summary), with tests.
- Calibrated origin `(26, 186)` on the `EXP-0023` screenshots (records known from
  the display buffer).
- Validation: 10 of 10 RAM-known screenshots matched the right record, IoU
  0.83-0.89, margin at least 0.63. Result: `CONFIRMED`.
- Mapping: Q1 = 13, Q2 = 5, Q3 = 2, Q4 = 10, Q5 = 11, Q6 = 1, Q7 = 9, Q8 = 3,
  Q9 = 15, Q10 = 8, Q11 = 12. Record 4 seen unlabeled. 0, 6, 7, 14 never seen.
- **Correction:** `EXP-0019`'s "Q2, record 4" is wrong. Its own state's display
  buffer equals record 5. Recorded in `EXP-0019`, not silently edited.
- Experiment numbers for RE-023, RE-024, and RE-025 shifted to `EXP-0025`,
  `EXP-0026`, and `EXP-0027`.

Checks: pytest (121 passed), ruff check, ruff format --check, and strict mypy.

Next action:
`RE-022` (caption compiler, offline). `RE-023` (selection) is also `READY`.

## 2026-10-17 — RE-022 caption compiler

Task: RE-022

- Added `tools/text/caption_compiler.py`, `data/captions/caption_spec.schema.json`,
  `data/captions/ryu_markers.json` (record-identifying markers, not
  translations), and `data/captions/stress_pangrams.json` (neutral pangrams at
  full length). Tests: `tests/unit/test_caption_compiler.py`.
- `pair_font.build` now takes an explicit code list. Its CLI still reproduces
  EXP-0023's `MEMFIX.PAC` (`90ff759c…`).
- Correction: record 0's placeholder is at **cell 8**, not cell 0 (my `EXP-0024`
  text was wrong; fixed there). The compiler caught it, because `{P}` is
  allowed only where the original record has `0000`.
- Marker build (`build/re022_markers`, manifest `35bab336…`):
  - 51 distinct pairs at `0x00A8-0x00DA`, 2,095 bytes;
  - 21 kanji sacrificed (`0x0C5E` … `0x0C24`);
  - `MC09.PAC` splice re-encode with 456 fill bytes.
  - Checks: font and table verified; 414 files with only the two targets
    differing; 0 invalid sectors; both images identical (track 01 `fd007d13…`);
    a `--files-only` rerun is byte-identical.
  - The `records.png` render shows all 16 markers legibly.
- Stress build (`--files-only`, manifest `90e745b5…`):
  - 227 distinct pairs (`0x00A8-0x029A`, using all three free ranges);
  - 9,637 bytes, with 101 kanji sacrificed of 321;
  - the splice overflowed, so the full re-encode was used, leaving 155 bytes of
    fill.
  - So `MC09.PAC`'s compressed size, not font space, is the tighter limit for a
    full-length English set.
- New unknowns: English punctuation codes, `MC09.PAC` margin for real text, and
  display of the untested free code ranges.

Checks: pytest (128 passed), ruff check, ruff format --check, and strict mypy.

Next action:
`RE-023` (selection mechanism, `EXP-0025`; live debugger session).

## 2026-10-17 — EXP-0025 design (RE-023)

Task: RE-023

- Static reading of `0x060AF81E-0x060AF8D0`: `@(76,r12)` is the partner-name glyph
  counter (expands `0000`). The original RE-023 hypothesis (that it selects the
  quote) is **DISPROVEN** by code reading. Name entry 9 = リュウ (Ryu), matching
  `MC09`.
- Alternate name-length table `0x060AF908` (flag `r11+0xCC8E`) fits English names:
  `HYPOTHESIS`. Logged as an unknown.
- Two-state search: WRAM-H `0x060F249C` holds `0x002091AC + 76·r` for the shown
  record (`0x002092DC` / `0x00209328`), and is the only such hit.
- Pre-registered Part 1 (write breakpoint on that pointer from state A, slot 5,
  original image) and Part 2 (forcing record 6).

Next action:
User runs EXP-0025 Part 1.

## 2026-10-17 — EXP-0025 Part 1 result and Part 2 abort

Task: RE-023

- Part 1 (`SUPPORTED`): the pointer store at `060AF724`/`060AF728` writes
  `table + 76·index`, with the index word at `0x060F9E66` (stride 100 when
  `r11+0xCC8E` is set). The run chose record 3 (Q8). The quote was not captured,
  because the game runs while the debugger is open.
- Part 2 attempt 1 was aborted. Breakpoints on `0x060F9E66` fire inside struct-init
  loops (`060490EC`, `06047CCA`), so the manual forcing procedure was impractical.
- The user reported the manual workflow is too tedious: no paste, everything
  hand-typed, F9 excludes the debugger, and screenshots must be relayed. This is
  concrete evidence for `EMU-012` (stock sufficiency) and `EMU-020`.

Next action:
User decision on the workflow (see the session for options).

## 2026-10-17 — EMU-012, EMU-020, and EMU-021 (agent interface)

Tasks: EMU-012, EMU-020, EMU-021

- `EMU-012` DONE: capability matrix. Stock Mednafen is sufficient for manual work
  and insufficient for agent-driven work.
- `EMU-020` DONE: a minimal, frontend-only patch is proposed; the user explicitly
  authorized the Mednafen modification.
- `EMU-021`: patch `0001-agent-interface.patch` (`c30146ef…`) applied to a
  separate copy, `src-agent`. The binary `fe0edb99…` is built in `build-agent`;
  stock `ca9bec5f…` is untouched.
- Validation:
  - V1 (smoke): pass.
  - V2: agent reads of WRAM-H and WRAM-L are byte-identical to the extractor on a
    same-instant state.
  - V3 (write and halt controls): pass.
  - V4 (breakpoint log): pending one human KO.
- A failure found and fixed: paths with spaces broke `loadstate` (first binary
  `a463ca28…`).
- New client `tools/mednafen/agent.py` and capture script
  `tools/mednafen/ko_capture.py`, with tests.

Checks: pytest (134 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 — EMU-021 V4 and EXP-0025 completed with the agent interface

Tasks: EMU-021, RE-023

- One user KO under `ko_capture.py` (log-mode breakpoints): pointer hits matched
  the manual Part 1 halts. Natural selection gave index 0, and record 0 was shown
  (the matcher agrees; the placeholder rendered as ケン). A post-KO checkpoint
  replayed the transition exactly with no input. EMU-021 DONE.
- New index writer: PC `060AF282` (`index = @(2,gbr) & 0x0F`, special value 39,
  `0xCC90` remap).
- Forcing indices 6, 7, and 14 via `onhit 060AF282` from the checkpoint showed
  exactly those records. RE-023 DONE (`CONFIRMED`). All 16 records have now been
  seen live.
- My pre-registered pointer for index 6 (`0x002093D4`) was an arithmetic slip;
  the correct value `0x00209374` was observed. Recorded in EXP-0025.

Next action:
`RE-024`: boot the `RE-022` marker image and force all 16 records automatically.

## 2026-10-17 — RE-024 / EXP-0026: all 16 marker records live

Task: RE-024

- Booted the `RE-022` marker image in the patched Mednafen. The user played one
  arcade KO with Ryu. Natural index 10 displayed its marker correctly. The
  post-KO checkpoint was saved automatically.
- Forced indices 0-15 from the checkpoint with no input. `verify_records.py`
  passed all 16: pointer, screen (records 1-15 pixel-exact), cart font, WRAM-L
  table, and display buffer.
- All 51 pair codes (`0x00A8-0x00DA`) render.
- Record 0: the placeholder expands to ケン after the Latin text.
- Verifier refinement: the placeholder shifts line 1's trailing blanks. Every
  record has one undrawn extra 39th buffer entry, equal to line 2's first cell.
  The first verifier model was too strict; it was refined from the observed
  buffers and checked again against the `EXP-0025` captures (still passing).
- RE-024 DONE. Next: RE-025 (variants), which closes RE-020 and M3.

Checks: pytest (135 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-17 — RE-025 / EXP-0027 variants; M3 complete

Task: RE-025 (closes RE-020)

- One boot of the marker image and two user fights:
  - V1: Ken on point, Ryu second, Ryu KO;
  - V2: Ryu with partner Gouki.
- 32 forced runs, plus the 2 natural ones, all verified.
- V1: Ryu's table is at `0x002191AC` (team slot 2); 16/16 verified there.
- V2: base `0x002091AC`; 16/16 verified; record 0 shows ゴウキ (name entry 15).
- V3 (versus mode) deferred: port 2 has no bindings.
- Anomaly: a live read of `0x060F9E4A` just after V2's pointer store gave
  `0x002191AC`, while the state at quote time gave `0x002091AC`. Recorded as an
  unknown.
- RE-025 DONE; RE-020 DONE (M3). RE-030 READY (not started).

## 2026-10-17 — RE-030 planning (EXP-0028)

Task: RE-030

- Chose **Ken** (`MC0A.PAC`): an ordinary single 16-record table.
  - Identity is supported by the name-table index (entry 10 = ケン) and by the
    game's slot pointer list `0x06094FD8` (`0x0021A59C` / `0x0020A59C` = slot
    base + `0xA59C`).
  - Ken's placeholders are on **line 2** (records 11 and 12), and three records
    are one-line. Both break M3's Ryu-only assumptions.
- **Correction:** the `EXP-0023` census offset `0xA59A` for `MC0A` is off by one
  word. The table starts at `0xA59C`. Census offsets are candidates only.
- Observation: in `EXP-0027` V2 (partner Gouki), the second entry of the pointer
  list was not a table pointer (`0x99000E99`). Its meaning is `UNKNOWN`.
- Phase A next (offline): multi-file compiler with a shared font, generalized
  verifier, Ryu + Ken marker image. Phase B needs one session: team Ken + Ryu, KO
  with Ken, then KO with Ryu.

## 2026-10-23 — EXP-0028 Phase A (offline)

Task: RE-030

- Generalized the caption compiler: schema v2, multiple tables, one shared font.
  v1 is backward compatible; it reproduces RE-022 byte for byte.
- Generalized the renderer (`--table`) and verifier: table chosen by matching
  WRAM-L at the state's base; line-2 placeholder model. Regression: 51 earlier
  captures still pass.
- Built the Ryu + Ken marker image `build/exp0028a`:
  - 66 pairs; 27 kanji sacrificed;
  - `MC0A` splice with 418 fill bytes; `MC09` identical to RE-022;
  - track 01 `c3990fa5…`; builds identical; 0 invalid sectors;
  - only the 3 target files differ.
- Phase B next (live): team Ken + Ryu; KO with Ken, then KO with Ryu.

Checks: pytest (137 passed), ruff check, ruff format --check, and strict mypy.

## 2026-10-23 — Local arcade ROM sets recorded (REF-008 created)

Task: reference provenance (no reverse engineering; `RE-030` stays on hold).

- The user supplied `mshvsf.zip` (EU), `mshvsfu.zip` (US), and `mshvsfj.zip` (JP)
  from `~/Downloads/mshvsf/`. They were copied with `cp -p` to the ignored
  `local/arcade_roms/mshvsf/`.
- `shasum -a 256` gave identical values for the originals and the copies. Sizes and
  hashes are in `references/mshvsf/arcade/README.md`.
- `git check-ignore -v` showed the zips are ignored by `.gitignore:20:local/`.
- `unzip -v`: each set has 20 members (46,399,488 bytes). Only the `03`/`04`/`05`
  program members differ by region. The `mvsu.03g`/`mvsu.04g` CRC-32 values match
  MAME 0.289 `mshvsfu` (USA 970827): `SUPPORTED`, not a full audit.
- User report, recorded as a `HYPOTHESIS`: only the JP set contains the Norimaro
  and secret-character quotes. It is untested, and special cases stay gated to M9.
- Created `REF-008` (`READY`) to audit the sets and document regional differences
  before any arcade capture. The user asked for a separate documentation task.

Checks: documentation only; no code changed.

## 2026-10-23 — REF-008: arcade set audit and regional claims

Task: `REF-008` (reference documentation; `RE-030` stays on hold).

- Fetched the pinned MAME 0.289 `cps2.cpp`:
  `curl … f34f0250…/src/mame/capcom/cps2.cpp`. It is 977,277 bytes, and its
  SHA-256 `a8c09ef8…e861602` matches `docs/references.md`.
- Added `tools/reference/mame_audit.py` with tests
  (`tests/unit/test_mame_audit.py`). It parses ROM_START/ROM_LOAD/ROM_CONTINUE
  and GAME() blocks, then hashes zip members in memory.
- The first run showed empty titles, caused by a GAME() regex that skipped one
  field too many. Fixed and covered by a test.
- Audit (command in `references/mshvsf/arcade/README.md`):
  - All three sets match their MAME 0.289 sets on all 20 ROM files (CRC-32 and
    SHA-1), and match no other set (at most 18/21).
  - Every zip lacks its `.key` file.
  - `CONFIRMED` in `docs/discoveries.md`.
- A first draft said encryption makes raw members unsearchable. The driver
  contradicts this: `decrypted_opcodes_map` decrypts opcodes only, and data reads
  are raw. Corrected to `UNKNOWN`.
- No MAME is installed (`which mame` is empty). The key-file refusal is expected,
  not observed.
- A research subagent collected regional claims RC-1 to RC-6. Most strong sources
  returned 403 or a bot check. TCRF also showed a bot check in the built-in
  browser, and no attempt was made to get past it. All claims are `HYPOTHESIS`.
  Notable: RC-2 (fan site) says Norimaro's win quotes **were** translated in the US
  ROM. That partly contradicts the "JP only" report. RC-3 (TCRF snippet only) says
  the secret characters' unique quotes are JP-only.
- Created `REF-009` (`BLOCKED`): pin a MAME build and add legal key files. Added it
  as a `REF-004` dependency.

Checks: pytest (142 passed), ruff check, ruff format --check, and strict mypy (58
files), all passing.

## 2026-10-23 — REF-008 addendum: TCRF read via Wayback Machine

- The live TCRF arcade page still showed its bot check after reload, and the user
  could not pass it either. The Wayback snapshot `20261011115711` loaded in full,
  and the user approved using it.
- Its text was read in the built-in browser and replaced the snippet-only claims:
  - RC-1 (Norimaro unlock byte `0xCD` on international sets).
  - RC-2: translated Norimaro win quotes, also in Spanish and Portuguese.
  - RC-3: secret characters have unique quotes in Japan only. TCRF does not
    transcribe them.
  - RC-6 refined: Japan 970702/970707 need 1C1C or Free Play for Norimaro. The
    local set is 970707.
  - New claims RC-7 (language setting) and RC-8 (Shadow's quotes come from XvSF).
- All remain `HYPOTHESIS`: TCRF gives no set or hash for its evidence.

Checks: documentation only; no code changed.

## 2026-10-23 — MAME 0.289 installed; EXP-0029 arcade quote text from ROM data

Tasks: `REF-009` (progress), `EXP-0029` (done), `REF-010` (created).

- `brew install mame` poured bottle `mame--0.289.arm64_tahoe`. The binary SHA-256
  is `6d40df87…029636d9`.
  `mame -rompath local/arcade_roms/mshvsf -verifyroms mshvsf mshvsfu mshvsfj` shows
  0/3 OK: each set is missing `<set>.key` and the QSound ROM `dl-1425.bin`.
  Blocked on user-supplied files.
- `EXP-0029`: the Latin win quotes are unencrypted 16-bit codes in `mvs.07b`. The
  pointer table at `0x20C014` holds 3 languages × 26 slots of 8 × 2 × 25-code
  quotes. The text and quote digests are identical in the EU, US, and JP sets.
  Slot order appears to follow a name list (Ryu = 9), which is `SUPPORTED`.
- Disproven along the way, so do not retry:
  - Win quotes are not plain 8-bit ASCII; only credits and warnings are.
  - The first punctuation guess (`0x0120` = `,`, `0x0185` = `!`) was swapped. A
    test of the following word's case gave 680/681 and 216/277.
- Added `tools/reference/cps2_text.py` (with `tests/unit/test_cps2_text.py`). Also
  extended the `mame_audit` parser with ROM region, offset, and loader; the audit
  JSON is unchanged.
- Decoded text stays in the ignored `local/arcade_text/`. No quote text was
  committed.

Checks: pytest (148 passed), ruff check, ruff format --check, and strict mypy (60
files), all passing.

## 2026-10-24 — REF-009 done: arcade sets verify and boot in MAME 0.289

- The user put `mshvsf.key`, `mshvsfu.key`, `mshvsfj.key`, and `qsound.zip` in
  `~/Downloads/mshvsf/`. CRC-32 and SHA-1 match MAME 0.289: the keys against
  `cps2.cpp`, and `dl-1425.bin` against `src/devices/sound/qsoundhle.cpp` at the
  pinned commit.
- Copied with `cp -p` to `local/arcade_roms/mshvsf/<set>/<set>.key` and
  `qsound.zip`. Keys went into per-set folders instead of the zips, so the recorded
  zip hashes stay valid.
- `-verifyroms`: 3/3 OK. Headless boots used the autoboot Lua script
  `tools/reference/mame_snap_frames.lua` with `-video none -nothrottle`, at about
  2000% speed.
- Snapshots at frames 1200-6000 show the title screen and attract mode for all
  three sets. A repeat run reproduced the `mshvsfu` frames bit for bit. The hashes
  are in `references/mshvsf/arcade/README.md`.
- `REF-010` is now `READY`. Next: design a route to a win-quote screen, by scripted
  inputs or user gameplay.

Checks: no Python code changed; the Lua script ran as shown.

## 2026-10-24 — REF-010 / EXP-0030: arcade quotes confirmed on screen

- Built a frame-timed MAME input runner (`tools/reference/mame_timeline.lua`) and a
  route generator (`tools/reference/arcade_route.py`).
- The route was found with snapshot contact sheets. Two coins are needed (default
  EEPROM is 2 coins per credit). After start, Ryu, and a second confirm (which
  picks Ken), Mode and Speed time out. A P1 Hadouken loop wins some fights.
- Ryu's win screen showed slot 9 quotes 6 and 7, matching the decoded entries line
  for line. `0xFF249C` held the entry address while each was shown. The European
  set showed quote 6 pixel-identically (quote-box crop hash).
- Losing runs showed six other slots, all matching the name list.
- The final captures were regenerated by the tool and reproduced the exploratory
  snapshot hashes bit for bit.
- Pitfalls, so they are not repeated:
  - `0xFF249C` keeps its value after a quote screen. Find the first frame where it
    changes; do not take the first non-zero dump.
  - Lexical sorting of frame-numbered files misorders 8400 versus 10000; sort by
    the number.
  - **HYPOTHESIS:** held inputs skip the quote screen. Two runs set the pointer
    without showing the screen while the loop was still pressing.
- Same inputs on the European and US sets diverge (different program ROMs), so
  each set needs its own route parameters.

Checks: pytest (151 passed), ruff check, ruff format --check, and strict mypy (62
files), all passing.

## 2026-10-24 — REF-003 / REF-004 / EXP-0031: Saturn Ryu ↔ arcade English pairing

- Searched the arcade program for the Saturn Ryu record code lines. All 32 occur
  once, in order. The 16 × 76 table at `0x20EDAC` is byte-identical to the Saturn's
  in all three sets. It is slot 9 of a Japanese pointer table at `0x20BFAC`.
- The arcade index sits at `0xFF9E66`, the same offset as the Saturn
  `0x060F9E66`. Added `force16`, `logwrites`, and `debug` verbs to
  `mame_timeline.lua`.
- MAME's debugger runs headless with `-debug -debugger none` and Lua `command()`
  for `dasm` and `bpset`. There is no `unidasm` in the Homebrew bottle.
- Selection routine: random value, `& 0x0F`, then for non-Japanese languages a
  remap table `00-07 00-07`. Breakpoint tests confirmed it (US 12→4, 9→1; JP
  12→12, 9→9). Forced indexes displayed all 8 English entries and 16 Japanese
  records.
- REF-003: my transcription and a blind subagent transcription are identical. A
  code-level check (cells, blanks, hiragana, punctuation) found 0 mismatches.
- Conclusion: Saturn record `k` corresponds to English entry `k & 7`. This is
  game-logic correspondence, not translation; the English lines are separate
  rewrites (my reading).
- Pitfalls:
  - The routine address differs per region build (US `0x070356` mask, JP
    `0x070378`). The first JP breakpoint at the US address silently did nothing.
  - The raw ROM bytes of these PC-relative tables are encrypted; read them from
    the decrypted opcode space.
- Only the Q10 record and pairing metadata were committed. Full text stays in
  `local/ref003/`, per `data/translations/README.md` ("minimal text").
- Next: REF-005 (needs a legal PS1 image), DOC-007, DOC-008, and the 16-to-8
  policy decision before `GATE-TRANSLATION`.

Checks: pytest (153 passed), ruff check, ruff format --check, and strict mypy (64
files), all passing.

## 2026-10-24 — Translation policy decision (user)

- The user chose the official paired English: Saturn record `k` gets arcade entry
  `k & 7`, even though each English line appears twice.
- Recorded in `GATE-TRANSLATION` notes, `data/translations/README.md`, and the Q10
  record.
- `preferred_english` stays empty until the gate passes. The remaining blockers are
  DOC-007, DOC-008, and REF-005.
- Measured: the paired English lines are at most 25 characters; Saturn lines are 19
  cells.

Checks: documentation and JSON only; the Q10 record re-parsed as valid JSON.

## 2026-10-24 — DOC-007 and DOC-008 done

- DOC-007: a read-only research subagent searched for XvSF Saturn translation and
  internals research. None exists publicly. The sources found (forum threads, the
  Satiator timing note, the Vampire Savior English-activation patch, the
  LemonGrwab Capcom patches, PalMod) are cataloged with reliability and license.
  None grants reuse.
  - Blocked sites were recorded and not bypassed.
  - My brief wrongly said XvSF used the 1 MB cart; sources say 4 MB (HSS-0167),
    like MSHvSF. The repo never carried the error.
- DOC-008: wrote `docs/agent_briefing.md`, a cited entry point that keeps
  discoveries and platform facts separate. Refreshed stale "nothing confirmed"
  status lines in `text_system.md`, `code_map.md`, and `saturn_text_hacking.md`.
  Self-review caught an overstatement (Ken is not live-confirmed) and fixed it.
- `GATE-TRANSLATION` now waits only on REF-005 (legal PS1 `SLUS-00793` image).

Checks: documentation only; pytest (153 passed).

## 2026-10-24 — REF-011: second arcade batch, PS1 image, XvSF material

- Inventoried `~/Downloads/mshvsf/v2` (11 zips), `~/Downloads/mshvsf/Marvel Super
  Heroes vs. Street Fighter (USA).7z` (the stated `~/Downloads/msfhvsf` folder does
  not exist), and `~/Downloads/xmvsf` (11 zips, two PS1 `.7z` files, one Saturn
  `.rar`).
- Archives were listed with `bsdtar -tvf` first, then each was extracted with
  `bsdtar -xf` into its own new, empty, ignored folder. No 7z or unar tools are
  installed; macOS `bsdtar` read both 7z and RAR.
- MSHvSF PS1: size, CRC-32, MD5, and SHA-1 equal Redump 12632 and MAME `psx.xml`,
  so identity is `CONFIRMED`.
- Arcade identity by member SHA-1 against MAME 0.289 (`v2_manifest.json`,
  `xmvsf/arcade/manifest.json`):
  - All MSHvSF sets match. After copying held keys to `mshvsfu1`, `mshvsfj1`, and
    `mshvsfj2`, `-verifyroms` shows 6/11 OK.
  - The XvSF zips use older names (for example `xmvsfj.zip` is 0.289's
    `xmvsfjr2`), and `xmvsfur1.zip` has relabelled members. No XvSF keys are held.
- XvSF Saturn: a CoolROM rip (ISO plus 40 MP3 tracks). Its IP header reads
  `T-1226G V1.002 19970925`, which MAME lists as Doukonban. It cannot be matched
  to MAME's CHD hashes.
- XvSF PS1: the US image matches MAME `psx.xml`; the JP EX Edition is not listed.
- `REF-005` is unblocked: its image is held.

Checks: documentation and metadata only.

## 2026-10-24 — XvSF keys verified; Saturn rip completeness

- The user added `xmvsf.key`, `xmvsfa.key`, `xmvsfh.key`, `xmvsfj.key`,
  `xmvsfu.key`, and `phoenix.key`. All match MAME 0.289 by CRC-32 and SHA-1.
  `phoenix.key` serves only bootleg `…d` sets. The XvSF zips were unchanged
  (SHA-256 diff).
- Built `local/arcade_roms/xmvsf_mame0289/` with zip copies renamed to 0.289 set
  names and keys in per-set folders. `-verifyroms`: 10/11 OK (`xmvsfb.key`
  missing).
- Booted `xmvsfu` and `xmvsfjr2` headless (`mame_snap_frames.lua`). Frame 3000:
  `e8a8ab8e…` (title) and `e19f6bae…` (attract).
- XvSF Saturn ISO: the PVD declares 214,396 sectors against 71,906 in the image.
  All 236 file extents end by sector 71,758, so the file data is complete. A
  better image is only needed for verified identity or emulation.

Checks: documentation and metadata only.

## 2026-10-24 — REF-005 / EXP-0032: PS1 English equals arcade

- Listed the PS1 disc (241 files) by extending `tools/disc/iso9660.py` to Mode 2
  Form 1, with Form 2 (XA) files reported as unreadable. Added a test.
- No ASCII win quotes. The arcade 16-bit codes, little-endian, matched in
  `DAT/SELECT.BIN` and `DAT/SEL.ARC`.
- All 26 arcade English slot blocks occur byte-identical in `SELECT.BIN`
  (`tools/reference/ps1_text.py`; output committed as metadata). Ryu's PS1 English
  equals the arcade's, and the Q10 record now has `ps1_us_text`.
- Found two extra all-Latin PS1 blocks with no arcade match (`0x1376C`,
  `0x13A8C`). This is a hypothesis for secret characters; text not read; deferred
  to SPECIAL-001.
- The Japanese Ryu table is absent from the US PS1 disc.
- `GATE-TRANSLATION`: all dependencies are now `DONE`; it awaits the user's
  go/no-go.

Checks: pytest (156 passed), ruff check, ruff format --check, and strict mypy (66
files), all passing.

## 2026-10-24 — GATE-TRANSLATION passed (user GO)

- The user said: "Pass GATE-TRANSLATION: go. Record the acceptance and allow Ryu's
  captions to use the paired official English."
- At acceptance, all dependencies (DOC-007, DOC-008, REF-003, REF-004, REF-005)
  were `DONE`, and optional REF-006 had evidence.
- Q10 `preferred_english` is set to the paired `arcade_us_text`. Updated the
  `data/translations/README.md` policy note.
- Added `TR-001` (`READY`): build Ryu's official-English captions with the
  existing compiler. It is not started; the Ken work stays on hold.

Checks: documentation and JSON only; Q10 re-parsed as valid JSON.

## 2026-10-24 — TR-001 / EXP-0033: Ryu's official-English captions, live

- Added `tools/text/official_captions.py`, which generates the caption spec from
  the local arcade ROM (record `k` = entry `k & 7`, arcade line breaks, centred in
  blank cells). The text stays local.
- Added `.` → `0x08AB` and `,` → `0x08AC` (chosen by glyph shape) to
  `pair_font.py` and the schema.
- Capacity fits (95 pairs, 3,669 bytes). The build is deterministic (track 01
  `2941a9c5…`), all compiler checks pass, and the offline render is correct.
- Live: the first attempt was restarted (the user's controller was unplugged).
  - One user KO saved `postko.mc`; the natural pick was record 6.
  - The user then paused with frame advance, which froze the capture. Once
    resumed, the debugger was still halted, and `loadstate` refused ("not allowed
    while halted"). The agent's `run` command fixed it.
  - All 16 forced records verify OK. Records 8-15 tie with 0-7 on screen (same
    codes). `verify_records.py` now treats code-identical ties as matches, with a
    test.
- Every screenshot was read by eye and is correct.

Checks: pytest (161 passed), ruff check, ruff format --check, and strict mypy (69
files), all passing.

## 2026-10-24 — Ken pairing verified; EXP-0028 Phase B done (M4 complete)

- Ken pairing: `quote_pairing.py --saturn-pac MC0A.PAC --saturn-table 0xA59C
  --slot 10` shows the table byte-identical to the arcade Japanese slot 10
  (`0x20F26C`) in all three sets. The remap is slot-independent (`EXP-0031`
  routine). Metadata is in `data/text/ken_arcade_pairing.json`. Ken-specific
  arcade display was not captured.
- Rebuilt `build/exp0028a`; it is identical (`c3990fa5…`) after today's
  pair-font changes.
- Phase B live: two sequential captures, with an agent `run` between them so the
  game doesn't freeze after the first.
  - The user did one session (Ken KO, then Ryu KO). Natural records: Ken 10 at
    `0x0020A59C`, Ryu 11 at `0x002191AC`.
  - 32 forced plus 2 natural captures: 34/34 `verify_records` OK. Placeholders
    expanded to the partner names, and every screenshot was read.
- `RE-030` and M4 are `DONE`. M5 (`RE-040`) needs detailed tasks next.

Checks: no code changed in this step; pytest (161 passed).

## 2026-10-24 — M5 breakdown defined (RE-040)

- Mapped RE-040's acceptance criteria one-to-one onto new tasks:
  - `RE-041` census of quote files against arcade slots (`READY`, offline);
  - `RE-042` per-character pairing;
  - `RE-043` exceptions register;
  - `RE-044` roster spec and font capacity;
  - `RE-045` deterministic roster image;
  - `RE-046` representative live verification;
  - `RE-047` regression controls.
- Grounded in `EXP-0023`: 23 quote files, 17 ordinary single tables, and 6
  irregular (`MC00`, `MC02`, `MC07`, `MC08`, `MC0C`, `MC13`). Only `MC09`/`MC0A`
  are mapped to characters so far.
- Known risk recorded in `RE-044`: roster pair count against the roughly
  817-pair unseen-kanji budget.
- Known cost recorded in `RE-046`: each live character needs a user KO. Input
  automation would need separate authorization.

Checks: planning only; no code changed.

## 2026-10-24 — RE-041 / EXP-0034: quote-file census against arcade slots

- New `tools/reference/slot_census.py` (with tests). For each decoded `MC*.PAC`:
  Saturn tables (`find_tables`) plus a byte-identity search for every arcade
  Japanese slot block and record.
- Result: `MCnn` holds slot `nn`'s whole block for all 23 files, identical
  across the three sets. 18 are ordinary; 5 irregular (`MC00`, `MC02` + slot 23,
  `MC08` + slot 24, `MC0C` + a 4-record table, `MC13` 120 records).
- The name table (rendered from the `EXP-0028` Ken state) has the same 26
  characters in arcade slot order.
- Corrections, so they are not repeated:
  - My first classifier compared whole blocks to `find_tables` offsets, which
    can be one word early. It now uses the block offset with 2-byte slack.
  - It also counted `MC13`'s 120-record table as single and `MC07`'s shared block
    twice. Both are fixed: blocks are counted by distinct offset, and every table
    must lie within the block.
  - `EXP-0023`'s "MC07 = 15 records" was a census split; the whole block is
    present.
- Next: `RE-043` decides roles (Norimaro, secrets, Shadow, bosses, and the
  irregular playable files) before `RE-042`.

Checks: pytest (164 passed), ruff check, ruff format --check, and strict mypy (71
files), all passing.

## 2026-10-24 — RE-043: M5 roster and exceptions register

- User decision: a 17-character roster, namely the 14 ordinary playable
  characters plus Captain America, Blackheart, and Dhalsim (their own blocks
  only). Norimaro, secret characters, Shadow, and bosses are excluded. Spider-Man's
  English also covering Armored Spider-Man (shared block) is accepted.
- Wrote `data/text/m5_roster.json` from the coverage manifest (file, slot, table
  offset) and `docs/coverage_exceptions.md` (in-scope table, untouched blocks, and
  the exceptions with evidence and owner).
- Added the rule that M5 builds may write only roster blocks, and must check
  that bytes outside them are unchanged.
- `RE-042` is now `READY`.

Checks: documentation and JSON only.

## 2026-10-24 — RE-042: roster pairing

- New `tools/reference/roster_pairing.py` (with tests). It reads the roster, pairs
  each Saturn table with its arcade slot, compares English blocks across the three
  arcade sets, looks up the PS1 comparison, and lists placeholders.
- All 17 tables are identical to their arcade Japanese slots. The English is
  identical across US, EU, and JP and present in the PS1 release.
- 33 placeholder cells across the roster; Zangief has the most (4). The arcade
  English blocks contain no `0000` code, so every placeholder is dropped. This is
  recorded per cell in `data/text/m5_roster.json`.
- `RE-044` is now `READY`.

Checks: pytest (166 passed), ruff check, ruff format --check, and strict mypy (73
files), all passing.

## 2026-10-24 — RE-044 (in progress): roster spec; capacity short of codes

- The roster English uses `' ? - "` and `‼`, plus undecoded arcade codes
  `0x0122` and `0x0160`. MAME runs with the quote pointer forced (write taps on
  `0xFF249C`/`0xFF249E`) showed them on screen as `‼` and a straight `"`.
  - Pitfall: forcing the pointer only changed line 2. Line 1 kept the natural
    quote, presumably because line 1 had already been drawn from the earlier
    pointer.
- Picked Saturn glyphs by printed bitmap shape: `?` `0x08DC`, `'` `0x08B9`, `"`
  `0x08BB`, `-` `0x08CB`, `‼` `0x08DF`. The decoder change moved `EXP-0029`'s
  digests; an addendum records the new values.
- `official_captions.py --roster` writes a v2 spec. Capacity: 405 distinct pairs
  against 248 free codes, so it does not fit. Bytes are fine (17,179 of 30,235).
- Greedy per-line alignment estimate: 338 pairs, still over. Options are (A)
  reuse unseen-kanji codes in place, or (B) raise the code count. Awaiting the
  user's decision; no build yet.

Checks: pytest (168 passed), ruff check, ruff format --check, and strict mypy (73
files), all passing.

## 2026-10-24 — RE-044 done: option A plus alignment; roster fits

- User decision: option A (reuse unseen-kanji codes in place) plus per-line
  alignment.
- Implemented:
  - a `reusable` parameter in `pair_font.build`, which empties the glyph, then
    stores the pair;
  - `caption_compiler` overflow allocation from the candidates, with the
    capacity field `kanji_codes_reused` and the check
    `reused_codes_in_kanji_range`;
  - `official_captions.best_shifts`, a deterministic greedy 0/1 shift per line,
    applied only in roster mode.
- Regression: the TR-001 spec and images `tr001` and `exp0028a` rebuild with the
  recorded hashes.
- Roster capacity: 338 pairs (248 free + 90 reused kanji codes), 13,992 / 30,235
  bytes; it fits. Spec `b2c097fa…`.
- Next: `RE-045` build. Its offline render review will also check the new
  punctuation glyphs in context.

Checks: pytest (171 passed), ruff check, ruff format --check, and strict mypy (73
files), all passing.

## 2026-10-24 — RE-045 / EXP-0035: roster image built and reviewed offline

- Built `build/re045` from the `RE-044` spec. The two builds are identical (track
  01 `f5044e8a…`), and every compiler check is true.
- 18 files differ: the 17 roster PACs and `MEMFIX`. Fonts: 338 pairs, 90 reused
  and 57 sacrificed kanji (147 of 321).
- Checked by script: the exception blocks (`MC02` `0xDF68`, `MC08` `0xBE5C`,
  `MC0C` `0x3B88`) are unchanged, record `k + 8` equals `k`, and no placeholders
  remain.
- Read all 17 render sheets; the new punctuation is legible in context.
- `RE-046` and `RE-047` are now `READY`. `RE-046` needs a gameplay plan agreed with
  the user.

Checks: no code changed in this step; pytest (171 passed).

## 2026-10-24 — RE-046 run 1: BIOS reset diagnosed and fixed (EXP-0036)

- The roster image `build/re045` reset to the BIOS CD player while loading the
  first fight (Cyclops/Zangief vs Dan/Sakura).
- Ruled out without gameplay:
  - attract demos (3 min, no reset);
  - an idle character select;
  - the original image (user replay reached the fight; a rolling save-state loop
    captured the pre-load state).
- New `tools/mednafen/replay_state.py` loads that state on any image.
  Single-file images isolate `MC12.PAC` (Dan as opponent).
- Not the cause: decoding (game RAM = our decoder), dropped placeholders
  (restoring them still reset), an SH-2 exception (no vector fired), or an SMPC
  reset (only controller polls).
- The cause: the file-read descriptor at `0x0603E8E9` carries the header's
  declared compressed length. Restoring only the header length words fixes it,
  so a shorter declared length breaks the opponent load.
- Fix: `pac_patch` keeps the original declared length and zero-pads the stream.
  The rebuilt roster (`build/re046_roster`, `351254c4…`) passes.
- Pitfalls:
  - The agent's `read` length is decimal. My first dumps were 100,000 bytes, not
    1 MiB.
  - `xtrct` builds `(w0 << 16) | w1`, so memory order is `A1 00 EA 20`.
  - zsh treats `$L:f…` as a modifier; quote it as `${L}`.
  - A record bisect needed a full re-encode when a splice outgrew the file.
- Reference builds `tr001` and `exp0028a` will now rebuild with new hashes,
  because their headers change. `RE-047` will re-baseline them.

Checks: pytest (173 passed), ruff check, ruff format --check, and strict mypy (74
files), all passing.


## 2026-10-24 — RE-046 run 2: four characters verified live (EXP-0036, DONE)

- Image: `build/re046_roster` (track 01 `351254c4…`). Versus `build/re045` it
  differs only in PAC headers and padding: decoded tables, `MEMFIX`, and all 17
  renders are byte-identical; all 78 manifest checks are true.
- The user played four KOs over two sessions (Cyclops/Zangief, Captain
  America/Dhalsim). The natural captures were Cyclops record 3, Zangief 13,
  Captain America 6, and Dhalsim 14.
- Anomaly: three captures read base `0x0607FD0C` and index 0 from
  `0x060F9E4A` / `0x060F9E66`, but their pointers were in the predicted tables.
  - At `060AF724`, `r12` was `0x060F9ED6`, not `0x060F9E16`.
  - Reading `r12 + 0x34` / `+ 0x50` from the second state gave the predicted
    bases and the matching indices; a forced write moved the pointer.
  - So there are two quote states. What selects one is open
    (`docs/known_unknowns.md`).
- Tools: `ko_capture.py` arms both index words, reports `quote_state`, and adds
  `--quote-state`. `verify_records.py` takes the base, index, and pointer from the
  matching state in `quote.mc`. New test `quote_state`.
- Forced 16 records per character (64 runs; no retries were needed). All 68
  captures pass `verify_records.py` (report `local/re046/verify_run2.json`,
  `f97540a7…`). I read every screenshot; all show the paired English.
- Cosmetic: the pair glyph for lowercase `p` has a cut-short descender. It is
  legible and noted as an open polish question.
- `RE-046` is `DONE`. Next: `RE-047` (regression controls, including
  re-baselining `tr001` and `exp0028a` after the declared-length change).
- Pitfall: a stray `cat > file` with no input waits on stdin; the shell hung
  until I stopped it.

Checks: pytest (174 passed), ruff check, ruff format --check, and strict mypy (74
files), all passing.

## 2026-10-24 — RE-047: regression controls and re-baselined references (M5 done)

- Synthetic tests:
  - `roster_spec` for two slots compiles through `parse_tables`, with one
    alignment for a line shared across characters;
  - `quote_pairing.pair` reads each slot through its own JP and EN pointers;
  - the caption schema's line pattern accepts exactly the characters
    `pair_font` maps; punctuation codes are distinct and below `A`.
- New `tools/regression/reference_builds.py` and the committed baseline
  `data/regression/reference_builds.json` (spec, track 01, and file hashes for
  `re022_markers`, `exp0028a`, `tr001`, `roster`).
  - With `--driver` (pinned `cps2.cpp`, SHA-256 `a8c09ef8…`) it regenerates the
    arcade-derived specs; otherwise it checks the cached specs by hash.
  - `--write-baseline` needs `--reason` and keeps replaced hashes in `previous`.
- First run (no baseline): all four rebuilt, every compiler check true.
- Before re-baselining, I compared each rebuild with its old build:
  - `re022_markers`, `exp0028a`, `tr001`: only PAC header words `+0x04` and
    `+0x10` differ; compressed streams, file sizes, and decoded data are
    identical; the new tail bytes are zero padding.
  - The changed sector sets shrink by each PAC's first sector (LSN 8246 `MC09`,
    8492 `MC0A`), which equals the source again.
  - `roster` rebuilds byte-identical to `build/re046_roster` (`351254c4…`).
- Re-baselined (reason: `EXP-0036` declared-length fix). New track 01 hashes:
  `re022_markers` `77b11799…`, `exp0028a` `58d0c56b…`, `tr001` `f9daacc1…`,
  `roster` `351254c4…` (unchanged).
- `MSHVSF_REGRESSION=1 pytest tests/integration` passed (63 s) against the new
  baseline. Report: `docs/regression_report.md`.
- Not done: spec regeneration, because `cps2.cpp` is not on this machine (it
  was fetched to `/tmp` in `REF-008`).
- Pitfall: `patch_image` refuses output outside `build/`, so the local test
  cannot use pytest's `tmp_path`.
- `RE-047` and `RE-040` are `DONE`, so **M5 is complete**. `END-001` (M6) stays
  `BACKLOG` until the user lifts its blocker.

Checks: pytest (182 passed, 1 skipped by default; the local test passes with
`MSHVSF_REGRESSION=1`), ruff check, ruff format --check, and strict mypy (79
files), all passing.

## 2026-10-24 — RE-047 follow-up: spec regeneration checked

- With the user's approval, fetched the pinned MAME 0.289 `cps2.cpp` (commit
  `f34f0250…`) to the ignored `local/mame_src/cps2.cpp`: 977,277 bytes, SHA-256
  `a8c09ef8…e861602`, matching `docs/references.md`.
- `reference_builds --driver local/mame_src/cps2.cpp`: `official_captions.py`
  regenerated the `tr001` and roster specs from `mshvsfu.zip`, byte-identical to
  the baseline hashes. All four references pass. The report now shows each spec's
  source (`stored` for committed marker specs, `regenerated` for arcade-derived
  ones).
- The arcade README notes the kept driver path.

Checks: pytest (182 passed, 1 skipped), ruff check, ruff format --check, and
strict mypy, all passing.

## 2026-10-24 — Backlog housekeeping and M6 opened

- `DISC-020` closed as `DONE`, superseded by `TR-001` (`EXP-0033`): an
  official-English Ryu image booted from scratch and was verified live.
- Recorded as low-priority `BACKLOG`, per the user: `RE-048` (lowercase
  descenders), `RE-049` (second quote state selector), `RE-050` (more live
  roster checks), `REL-001` (distributable patch), and `REF-012`. `REF-012`
  investigates the user's observation that the US/EU arcade sets use a different
  win-quote font, and whether it could serve the Saturn (`HYPOTHESIS`; a user
  decision if viable).
- User GO for M6: `END-001` is `READY`. Checkpoint plan: reach the final boss in
  arcade mode, lose, and save a state at continue / character select. Whether
  continuing keeps the final stage is a `HYPOTHESIS` to check first.
- No code changed.

## 2026-10-24 — END-001 / EXP-0037: final-boss checkpoint and first look at Ryu's ending

Task: END-001

Goal: Make the final-boss checkpoint, test the continue hypothesis, and observe
Ryu's ending without assuming any win-quote structure.

Observation, action, and result:

- **Setup.**
  - The untouched image (track 01 `8274307f…`, hash checked) ran on the agent
    build (`fe0edb99…`).
  - The roster image was not used, because it repacks the quote font, which
    the ending might share.
  - New `tools/mednafen/session_recorder.py`: a screenshot every second and a
    state every 3 s, frame-named, ring-buffered. It needs no hotkeys.
- **Gameplay (user).** Ryu/Ken, lost to Mech-Gouki, continued, then Ryu/Gouki
  beat Mech-Gouki with Ryu.
- **Continue hypothesis: `SUPPORTED`** (one run). The countdown led to a
  Ryu/Ken portrait screen, then character select, then `STAGE-08` against
  Mech-Gouki.
- **Checkpoints.**
  - A no-input replay of `select_after_continue.mcs` held on select for at least
    50 s.
  - Nine checkpoints (`local/end001/checkpoints/`) are listed with hashes in
    `EXP-0037`.
- **Ending observations.**
  - A four-box post-boss dialogue at the top of the stage, after the partner
    Gouki drops in. Each box shows about 230 frames, appears whole, and has no
    speaker cue.
  - Three ending pages, two pictures, and a bottom box. Each page shows about
    470-700 frames. Then the credits, which are already romanized.
  - Measured: 13-row glyphs, 16-px pitch and line pitch, and line starts on a
    16-px grid (x ≡ 12 mod 16), not simple centering.
  - The transcription is local only (`local/end001/transcription.json`,
    `ca7de11d…`) and not independently reviewed.

Method pitfalls (no game hypothesis involved):

1. **Contact-sheet indexing.** Counting tiles from
   `ffmpeg -pattern_type glob` did not match the `ls` order of the frame-named
   files, so the first select state (frame 59,809) was really on the
   countdown. A no-input replay exposed it: `GAME OVER`. States were re-picked
   by reading frame-named screenshots, and sheets now use the `concat` demuxer
   over an explicit list.
2. **Replay steps are not exact frames.** `replay_state.py` steps drift, so
   timing comes from the live frame-named screenshots, and checkpoint names
   follow their saved screenshots. Three were renamed after reading them.

Conclusion: `END-001` is `DONE`. Tasks `END-002` to `END-006` were created
with hypotheses, checkpoint needs, and designs (`EXP-0037`), and `END-010`
now depends on them. Unknowns were added to `docs/known_unknowns.md`. No
discovery is confirmed, so `docs/discoveries.md` is unchanged.

Next action: `END-002` (renderer) or `END-003` (RAM structure search). Both
need no gameplay. `END-005` needs one boss fight from `select_after_continue.mcs`.

## 2026-10-24 — END-002 / EXP-0038: the ending text is VDP1 sprites of quote-font glyphs

Task: END-002

Goal: Identify the video path that draws the ending text, with no gameplay.

Hypothesis 1: the glyphs of dialogue box 1 are VDP1 normal sprites, one per
cell.

Hypothesis 2, formed from the passive result: the glyph cells are quote-font
cells from the `FONT-001` routine.

Action and result:

- **Passive.**
  - `mcs_extract` of `ending_dialogue_box1.mcs` and `ending_page1.mcs`.
  - `vdp1_sprites`: 38 sprites each (`0x6030` and `0x61F0`), 16 × 16 4 bpp, on
    a 19 × 2 grid at x = 26 + 16k. Screenshot row = VDP1 y + 8.
  - There is one cell per distinct glyph. Page 1 has 23 distinct glyphs, which
    matches the transcription.
- **Font.** The new `tools/text/glyph_match.py` matched 40 of 40 glyph cells
  byte-exact to decoded quote-font cells (base `0x0278CF60`), one code each.
  The codes fit the known scheme. Raw cells are not in RAM; the staging cell
  `0x0601CEEC` holds each screen's last glyph.
- **Active.** The new `tools/mednafen/write_trial.py` zeroed one VDP1 cell:
  - box 1 cell `0x0A780`: only those 69 px changed in the box, at 2 and at 60
    frames (the write survived);
  - page 1 cell `0x0BD80`: only its 150 px changed.
- **Routine.** A PC breakpoint on `0x0601CE00` across the box 1 → 2 change gave
  12 hits in one frame:
  - R3 = box 2's distinct codes in order;
  - R9 = the VDP1 destination, `+0x80` per glyph;
  - PR = `0x0601CDE2`;
  - R1 = a pre-filled slot table in WRAM-L `0x00260E5E` (not the text).

Pitfall (method): screenshots of separate launches differ by 1,865 px over the
idle fighters. The pause after `loadstate` is asynchronous, so the animation
phase varies. Compare control and trial inside the text box, or by diff
bounding box, never by whole-frame hash.

Deviation: the task's design said to skip the candidate commands. A cell write
was used instead, because it tests the same claim and the game does not rebuild
glyph cells during a screen. It is recorded in `END-002`.

Conclusion: `CONFIRMED` for box 1 and page 1, recorded in discoveries
(`END-002`). `END-004` is now `READY`, because there is a trace start (the
caller of `0x0601CE00`). `END-003` can search for the known code sequences
directly.

Checks: pytest, ruff check, ruff format --check, and strict mypy (see the
commit).

Next action: `END-003` (code search in RAM) or `END-004` (trace R3 to its RAM
source, then to the disc).

## 2026-10-24 — END-003 / EXP-0039: the ending text is a live WRAM-L code table

Task: END-003

Goal: Find where the ending's 16-bit codes live in work RAM, with no gameplay.

Hypothesis: the dialogue and page text are held in work RAM as the same 16-bit
codes and read from there.

Action and result:

- **Direct search.** It used the codes known from `EXP-0038`, with `?` for
  unknown kanji, over WRAM-L/H of eight `EXP-0037` checkpoints.
  - Every line hit exactly once in WRAM-L, inside 76-byte records (19 × 2
    cells, `0x0020` padding).
  - Box records: 1 `0x0022AE14`, 2 `0x0022AE60`, 3 `0x0022B9F4`,
    4 `0x0022BA40`. Page records: `0x00233664` + `0x4C`·k.
  - All 13 line starts match the screen, so positions are explicit, not
    computed centering.
  - Page 3's "bracket gaps" are glyph whitespace. The transcription was
    corrected locally.
- **Placeholder.** Box 1 line 2 and box 3 line 1 hold `0x0000` where a name
  shows (Ryu, then Gouki). A WRAM-H name table from about `0x06095FC0` holds
  32-byte name entries (Ryu at `0x06095FE4`). `0x08A8` is the long-vowel mark.
- **Live trials** (`write_trial.py` into the post-KO state, with controls):
  - box 2 cell 1 → R: only that cell changed;
  - box 1's `0x0000` → R: R then ・・・, no name;
  - Ryu's name entry → R Y U: box 1 showed RYU.
- **Load time.** Bisection of the run 1 states: absent at frame 53,481, present
  at 53,651 (the `STAGE-08` transition, team still Ryu/Ken). The records are
  identical through the ending.
- **New tool:** `tools/text/code_search.py`, with tests.

Conclusion: `CONFIRMED` for boxes 1-2 and the placeholder, `SUPPORTED` for
boxes 3-4 and the pages (discoveries `END-003`). `END-004` now has a concrete
trace start: a write breakpoint on a record address, replayed from
`f00053481.mcs`.

Next action: `END-004` (no gameplay).

## 2026-10-24 — END-004 / EXP-0040: the ending text comes from `MC13.PAC` and `ME.PAC`

Task: END-004

Goal: Trace the `EXP-0039` records to their disc file, with no gameplay.

Hypothesis: a disc read during the `STAGE-08` transition writes the records,
and an offline decode reproduces them exactly.

Action and result:

- **Write breakpoints** (log, then halt) replayed from
  `before_stage08_load.mcs`:
  - dialogue record: first written at replay frame 221 by the LZSS
    decompressor (PC `0603E446`, `DISC-001`). Context header word
    `0x8000792B`, destination `0x00220000`;
  - page record: written at frame 233 by a longword copy (PC `0603E04E`) from
    `0x0603F000`. Context header word `0x0000ED02`, destination `0x00230000`.
  - Both name fields read `me.pac`, so the name field is not a reliable
    per-load name.
- **Offline.** Cut `ME.PAC` and all `MCnn.PAC` from the untouched track by LSN
  (hashes match the listing).
  - `MC13.PAC` header word 1 = `0x8000792B`. Its decode equals the four dialogue
    records exactly, and 60,584 of 61,042 bytes overall.
  - `ME.PAC` word 1 = `0x0000ED02`. It is raw from `0x10`: equal to the copied
    RAM at the halt, and the three page records equal the file in all states.
  - The differences are pointer relocations (file + base + `0x40`), plus 30
    unexplained non-text longwords in `ME.PAC`'s region.
- `MC13` is slot 19 (Cyber-Akuma), whose "120-record table" (`EXP-0034`) holds
  the post-boss dialogue. That explains why it loads with the boss stage
  regardless of partner. `docs/coverage_exceptions.md` was updated to separate
  the boss's quotes (`SPECIAL-001`) from the dialogue records (ending scope).

Conclusion: `CONFIRMED` (discoveries `END-004`). Created `END-007` (M6): a
marker build per file, replayed from a pre-load checkpoint, before any
translated text.

Next action: `END-007` (no gameplay), or `END-005` (one gameplay session).

## 2026-10-24 — END-007 / EXP-0041 Part 1: marker builds load from a derived image

Task: END-007

Goal: Show that edited ending files on a derived image are what the game
uses, with no gameplay.

Hypothesis: a one-code marker edit per file loads at `STAGE-08` and reaches
the ending, with no other copy, checksum, or length check.

Action and result:

- **Builds**, each marker full-width R (`08F9`):
  - A: `ME.PAC` `0x367E` `09AD` → `08F9`, a raw same-size edit; 1 sector.
  - B: `MC13.PAC` decoded `0xAE62` `0970` → `08F9`; 16 sectors.
    - The splice re-encode was refused: 31,044 > 31,036 bytes, because `MC13`
      has 1 byte of slack.
    - `--full` gave 30,569 bytes, declared length kept at 31,011, with 443
      zero-fill bytes; the header is unchanged.
  - C: both files.
  - In every build, the other tracks and the CUE equal the source.
- **Load path** (`write_trial --dump`, new option): `before_stage08_load.mcs`,
  600 frames, on the untouched image and A/B/C. The loaded regions differ only
  at each marker word (2/2/4 bytes).
- **Display.** Page 1 RAM `0x0023366E` → R showed in only that cell (145 px).
  Box 2 was already shown in `EXP-0039`.
- **No re-read.** Post-KO replays on A and B equal the controls pixel for
  pixel.
- **Loader name field over run 1:** `me.pac` → `end.pac` → `sel.pac` (select
  after the continue) → `end.pac`. The boss-stage loads repeat after a continue,
  and `END.PAC` is involved too (not examined).

Deviation: the criterion "replay a pre-load checkpoint and screenshot" cannot be
met without gameplay, because the boss fight intervenes. Part 1 is `CONFIRMED`
by composition (disc to RAM, RAM to screen). Part 2 is one user fight on image
C from `before_stage08_load.mcs`. `END-007` is `BLOCKED` on that run.

Next action: `END-007` Part 2 (user), or `END-006` (no gameplay).

## 2026-10-24 — END-007 / EXP-0041 Part 2: the page marker shows live from a derived image

Task: END-007

Action and result:

- **Setup.** The agent launched `build/end007_c`, loaded
  `before_stage08_load.mcs`, and started the recorder.
  - RAM read back `08F9` at both marker words after the load.
  - The user lost once, and the agent reloaded the state.
  - Ryu (team Ryu/Ken) won with the KO.
- **Page 1 showed R at line 1 cell 5.**
  - It differs by 145 px from the untouched run's page 1, in the marker cell
    only.
  - The screenshot is byte-identical to the Part 1 RAM-trial screenshot.
- **Pages 2-3** are pixel-identical to the untouched Ryu/Gouki run. Page 3 is
  byte-identical.
- **Dialogue.** Ryu/Ken boxes 1-2 are other lines, so the `MC13` box 2 marker
  was not displayed (anticipated).
  - Box 3 equals Ryu/Gouki's except the placeholder name.
  - Box 4 is identical.
  - Recorded as an uncontrolled `END-005` observation.
- **Checkpoint:** `ryu_ken_post_boss_ko_imageC.mcs` (`b1ef3827…`).
- **Correction:** a placeholder hash typed into the EXP-0041 draft was replaced
  with the computed one before commit.

Conclusion: `END-007` is `DONE` (`CONFIRMED`). The route for M7 is proven up
to the source image: raw edits to `ME.PAC`, and full re-encodes of `MC13`.

Next action: `END-005` (controlled partner run, one gameplay session) or
`END-006` (arcade reference, no gameplay).

## 2026-10-24 — END-006 / EXP-0042: arcade reference for Ryu's ending

Task: END-006

Goal: Capture the arcade Japanese and official English for Ryu's ending and
the post-boss dialogue, with no Saturn gameplay.

Action and result:

- **ROM search.** All seven Saturn records occur verbatim in all three
  programs.
  - Pages are at `0x2153CC`, behind a four-language 26-slot page table
    (`0x20C14C`/`1B4`/`21C`/`284`).
  - The English pages for Ryu (`0x21F580`) are 3 × 2 × 25 cells.
  - `MC13` records 16-119 = arcade block `0x217BE0` (319 records past slot 19).
  - The English has no counterpart of the four-box dialogue, only a 52-record
    partner-line table at `0x22226C`.
- **No-play MAME route.**
  - Saturn run 1 states gave the stage byte `0x060F4881` (4-7 over stages 5-8)
    and the boss vitality `0x060F3E50`.
  - Forcing `0xFF4880` = `0x0607` and `0xFF3E50`/`0xFF4844` = 0 in MAME gave
    stage 8 and an instant KO.
  - The first run looped stage 8, because the stage was never released. Fixed
    by releasing both words during and after the fight.
- **Screens.**
  - `mshvsfj` (Ryu/Ken and Ryu/Gouki): the Saturn's Japanese dialogue and
    pages.
  - `mshvsfu`/`mshvsf`: English pages, plus two partner lines.
    - Ryu/Ken: records 10 and 35.
    - Ryu/Akuma: predicted as records 15 and 35, then seen.
- **New tools:** `arcade_endings.py` and `arcade_ending_route.py`, with tests.
  The route tool reproduces the Gouki timeline.

Conclusion: `CONFIRMED` (discoveries `END-006`). Gap: no official English for
the Saturn four-box dialogue. That is the scope decision for `END-010` (adopt
the arcade's two lines, use a non-official translation, or leave it Japanese).

Next action: `END-005`, and the user's dialogue scope decision.

## 2026-10-24 — END-010 scope decision (user)

- The decision, in the user's words: "For END-010, use the arcade's two official
  English partner lines for the post-boss dialogue, and the official English for
  the three ending pages."
- Recorded in `END-010` and in `data/translations/README.md` (ending policy).
- `END-010` stays `BACKLOG`. It depends on `END-005`, which shows which
  dialogue records each partner uses.
  - The two English lines must replace four Saturn boxes: two
    partner-specific, then two shared Ryu boxes (`EXP-0041`).
  - Showing one line where two boxes play is an open design question for an
    experiment.
- No code changed.

## 2026-10-24 — END-005 / EXP-0043: point and partner roles in the ending

Task: END-005

Hypothesis (pre-registered in `EXP-0037`): the dialogue depends on the
partner, and the pages on the point character.

Action and result:

- **Saturn controlled run.** Untouched image, `select_after_continue.mcs`,
  Ryu + Ken. The user lost once and the agent restored the state; then Ryu
  won, with Ryu landing the KO.
  - Pages: 0 px vs `EXP-0037` (byte-identical screenshots).
  - Box 4: 0 px. Box 3: the name only. Boxes 1-2: other lines.
  - All four boxes equal the image-C Ryu/Ken run.
  - The continue kept the boss stage, twice.
- **Records.** Glyph matching gave `MC13` records 36-37 (Ken's pair) and
  86-87 (Ryu's pair, as for Ryu/Gouki).
  - Formula: 16 + 2·(partner slot) and 16 + 2·(26 + point slot). It matches
    the English partner-line indices, and 16 + 2·52 = 120 records.
- **Arcade predictions** (no play, `arcade_ending_route.py`, now with
  `--point`):
  - Ryu + Chun-Li: records 38-39 and 86-87; English 11 and 35. Met.
  - Gouki + Captain America: records 20-21 and 98-99; English 2 and 41; Gouki's
    ending. Met.
- **Deviation.** The planned Gouki + Ryu run picked Captain America, because
  cursor paths depend on the point character. The KO character was not varied.

Conclusion: H1 and the indexing model are `CONFIRMED` (discoveries
`END-005`). `END-010` is `READY`.

Next action: `END-010`.

## 2026-10-24 — END-010 / EXP-0044: Ryu's ending in official English (M7 complete)

Task: END-010

Action and result:

- **Trials** (RAM, untouched image):
  - T1: a blank record shows as an empty box.
  - T2: `0x0000` works at any cell.
  - The user chose the layout: split each line at its break across the two
    boxes, and use English names.
- **Name table.** Found in `MM.BIN` (`0x7D3C0`, raw at WRAM-H `0x06018B00`) by
  a byte search of all disc files. A cold-boot check showed the built image's
  names in RAM, with nothing else in `MM.BIN`'s region changed.
- **Safety.** No sacrificial kanji are used by any ending page or dialogue
  record.
- **Tools:**
  - `caption_compiler.py` schema v3 (raw, multi-table, fields, patches,
    placeholders anywhere), with v1/v2 regression unchanged;
  - `official_endings.py` (spec from the ROM, with a Japanese-identity check);
  - `ending_driver.py`;
  - an agent client lock.
- **Failed approach** (recorded so it is not retried): replaying
  `before_stage08_load.mcs` on the built image gave empty boxes and pages.
  - The quote font is loaded after boot and stays resident, so the state's old
    font lacked the pair glyphs.
  - The agent cannot write cart RAM (the `physical` space reads zeros there).
  - Live checks therefore use a cold boot, with the user working the menus and
    the driver forcing stage 8 and the KO.
- **Live run 1.** All English, but "RYU ," had a blank cell.
  - Found a one-byte name-length table at `MM.BIN` `0x96DE8` (all 26 entries
    match the Japanese name lengths). Ryu's 3 ≠ 2 pair cells.
  - Added byte `patches` and rebuilt.
- **Live runs 2-4** (rebuilt, track 01 `b481a4c6…`): Ryu + Ken twice and Ryu +
  Gouki, all exactly as predicted. The pages are English.
- **Regression.** Reference `end010` was added (spec regenerated by
  `official_endings.py`). All five references pass.

Conclusion: `END-010` is `DONE` and M7 is complete. `END-020` (M8) is `READY`.

Checks: pytest (198 passed, 1 skipped), ruff check, ruff format --check, strict
mypy, and the full reference regression (5 pass).

## 2026-10-24 — END-010 layout revision / EXP-0045: one dialogue block per speaker

User request: show each partner line whole, in one block lasting both boxes'
time, instead of split across four boxes.

- **T3** (RAM, untouched image): record 36 copied over record 37.
  - Control: the box changes once (frame 659), with no blank frame.
  - Duplicate: no change across 201 frames; the whole screen is byte-identical
    at the hand-over.
- **Generator:** `official_endings.py --dialogue-layout whole` (the default) or
  `split`.
- **Build** `build/end010`, track 01 `ba3fb3ce…`. Only `MC13.PAC` differs from
  the `EXP-0044` build; the split build is kept as `build/end010_split`.
- **Replays** of the `EXP-0044` cold-boot stage-map states on the new image
  (valid because font, names, and pages are byte-identical, and `MC13` reloads
  at stage 8), with a forced KO:
  - Ryu + Ken: "RYU, / you're not bad." then "We shall meet again / KEN.";
  - Ryu + Gouki: "You are worthy / RYU." then "We shall meet again / AKUMA.";
  - each block about 480 frames, then the unchanged pages.
- **Regression:** `end010` re-baselined with the reason recorded; all five
  references pass.
- **Note:** the first replay command was interrupted by the user by mistake,
  but had completed the Ryu + Ken run. The partial Ryu + Gouki folder was
  cleared and rerun.

Checks: pytest, ruff, format, mypy, and the full regression all pass.

## 2026-10-24 — END-020 started; END-021 / EXP-0046: census and capacity

- `END-020` broken down into `END-021` to `END-025`.
- `official_endings.py` takes several point slots. The single-point output is
  byte-identical.
- **Census** (`tools/text/ending_census.py` → `data/text/ending_census.json`,
  metadata only): all 17 roster slots are consistent.
  - Page counts are equal, totalling 75.
  - `ME.PAC` and `MC13` records equal the arcade Japanese.
  - All lines fit, including the longest name (8 cells).
  - BISON's name length grows (2 → 3); this is untested.
- **Capacity:**
  - endings alone: 369 pairs (121 kanji codes reused);
  - plus the M5 win quotes: 454 pairs (206 of 321 kanji codes, 19,303 of 30,235
    bytes). It fits.
- **Per screen:** at most 25 distinct English glyphs per page, against 34 in
  Japanese.

Next action: `END-022`.

