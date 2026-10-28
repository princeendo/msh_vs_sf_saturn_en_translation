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

## 2026-10-24 — END-022 / EXP-0047: name growth, and the placeholder census

- **Growth trials** (RAM, untouched image, `ryu_ken_post_boss_ko.mcs`, box 3):
  - control: ケン、;
  - ABCD with length 4: "ＡＢＣＤ、";
  - ABCD with length 2: "ＡＢ、".

  Names can grow, and the length table controls the insertion. Only that line
  shifts.
- **Placeholder census** (`tools/text/placeholder_census.py`): 100
  placeholders. A roster image makes 69 English and leaves 31 in Japanese:
  - 13 in excluded characters' win quotes;
  - 16 in `MC13` pairs of excluded slots;
  - 1 in an unidentified `MM.BIN` table;
  - 1 false positive.
- **Sweep tuning.**
  - The first, loose sweep flagged graphics and offset tables. Inspected:
    `SEL`, `SEL2`, `PL05`, `MVDEMOF6.ST2`, `MEMFIX`, `MC06`, `MC11`.
  - Final rule: a placeholder inside 25 text-like words, with at least four
    kana and at most two zero cells.
- **New text surface.** `MM.BIN` holds a Japanese-only dialogue table (also in
  the arcade programs at `0x213F82`; no English counterpart; it mentions
  Gambit and Rogue). Added as `TXT-001` (backlog).
- `END-022` is `BLOCKED` on the user's side-effect decision.

## 2026-10-24 — END-022 decision; END-023 / EXP-0048: combined roster image

- **User decision:** "Accept English names inside the remaining Japanese lines
  (excluded characters and the one MM.BIN line)." `END-022` is `DONE`.
- **Generator:** `official_endings.py` gains `--roster` and `--with-win-quotes`.
  The single-point spec is unchanged (checked).
- **Build** `build/end023` (track 01 `c06cf0ef…`):
  - two builds identical; all checks true; 21 files changed;
  - 501 pairs, reusing 253 of 321 kanji codes;
  - the win-quote PAC files are byte-identical to the verified roster image,
    because their pairs are allocated first.
- **Renders:** the win quotes are byte-identical to the `roster` reference's.
  All 75 page records and 68 dialogue records were read.
- **Regression:** `m8_roster` added; all six pass.

Next action: `END-024` (live sample; the user works menus from one cold boot).

## 2026-10-25 — END-024 / EXP-0049: live sample of the combined image; VEGA

- **Session:** one cold boot of `build/end023` (`c06cf0ef…`); the user worked
  the menus; the driver forced stage 8 and the boss KO.
- **Five credits, all correct:**
  - CA + Ryu: "CAPTAIN AMERICA, / you are a great fighter." then "We make a good
    team / RYU.", and 6 pages.
  - Zangief + Spider-Man: 6 pages.
  - Bison + Hulk: "BISON" grown to 3 cells; 3 pages.
  - Sakura + Wolverine: 2 pages.
  - Dan + Chun-Li: 5 pages; the last is empty, matching the arcade English,
    checked by MAME `--point dan`.
- **Failed approach:** `--warmup-ko` zeroed `0x060F3E50`/`0x060F4844` in stage
  1. Those offsets are the boss's only, so the user's team lost. A manual write
    to `0x060F3E5A` coincided with the loss (probably player-side). The option
    was removed. The opponent's vitality in two-against-two fights is unknown.
- **User decision:** use VEGA (Saturn naming), not BISON. `NAME_OVERRIDES`
  was added.
  - Rebuild `build/end024_vega` (`e721a167…`): only `MEMFIX.PAC` and `MM.BIN`
    change.
  - `m8_roster` re-baselined; all six references pass.
- **Left for `END-024`:** a cold-boot Vega credit and a win-quote spot check
  (a manual first-fight win).


## 2026-10-25 — END-024 done: VEGA credit and win-quote spot check

- **Session:** one cold boot of `build/end024_vega/image_a` (`e721a167…`), with
  the recorder (`local/end024v/rec`).
- **Win quote:** the user won stage 1 with Vega + Ryu. Vega's quote showed the
  official English "You were foolish / to challenge me!" (`f00008932`
  `3b8a6763…`).
- **Ending:** the driver was armed only after the win (frame 9093), and the
  boss KO came at frames 9613-9786. Then "VEGA, / you are a great fighter.",
  "Our game is at its end, / RYU.", and Vega's three English pages. Composite
  `local/end024v/credit6.png` (`f136a0e4…`).
- **Checks:** `pytest` 203 passed, 1 skipped; `ruff check`, `ruff format
  --check`, and `mypy tools` are clean.
- `END-024` is `DONE`; `END-025` is `READY`.

Next action: `END-025` (coverage exceptions, regression report, and remaining
unknowns; closes M8).

## 2026-10-25 — END-026 / EXP-0050: the Saturn's names in the English text (provisional)

**Revisit this decision before any release** (`LOC-001`;
`docs/localization_plan.md` holds the options and every affected line).

- **How it came about** (user decisions, 2026-10-25, in order):
  1. During `END-024` the user noted that the Saturn's art and voice say
     **Vega**. BISON was switched to VEGA in the name table (`EXP-0049`).
  2. After seeing the VS screen's "MECH-GOUKI" (`EXP-0049` frame `f00009412`),
     the user asked for "Cyber Akuma" → **"Mech-Gouki"** in the text.
  3. Then the user asked for "AKUMA" → **"GOUKI"** wherever it appears, "for
     now".
- **Why provisional.** The user's point: making the text follow the US names
  instead would also need voice samples to stay consistent with the Saturn's
  announcer, and edited art. Not yet planned.
  - The current policy keeps text, art, and voice consistent under the
    Japanese-release names, at no art or audio cost.
  - Open questions: which convention; whether audio is in scope; where clips
    could come from (unverified); and names for excluded characters.
- **What was changed** (all in `tools/text/official_endings.py`):
  - `NAME_OVERRIDES = {14: "VEGA", 15: "GOUKI"}`;
  - `TEXT_OVERRIDES = {"Cyber Akuma": "Mech-Gouki", "Akuma": "Gouki"}`,
    applied in order to the pages, the dialogue, and the combined win quotes.
- **Sites** (roster image): the slot 14 and 15 names; Gouki's win quote
  (`MC0F` records 7 and 15); and the ending pages of Wolverine (`0x2F54`),
  Vega (`0x3CFC`), Gouki (`0x3DE0`), and Dan (`0x40D8`). No other roster line
  names these characters.
- **Side effect:** the new win-quote text moved three other characters'
  win-quote lines by half a character (centring shifts are chosen over the
  whole set). The renders were read.
- **Builds:**
  - `build/end026` (Mech-Gouki only, `61ced9f9…`) was verified live: Vega's
    page 1 reads "behind the Mech-Gouki!!".
  - `build/end027` (plus GOUKI, `2a5b26b7…`): all checks pass, deterministic,
    renders read.
  - `m8_roster` and `end010` were re-baselined (reasons recorded); all six
    references pass.
- **To revert:** empty both override tables, rebuild, re-baseline, and do one
  cold-boot check.
- **Live check of `build/end027`** (Gouki + Ryu, one cold boot):
  - "GOUKI, / you are a great fighter.", then "The fight is all we have, /
    RYU.";
  - Gouki's three pages, with "Gouki";
  - the VS screen art says "GOUKI" and "MECH-GOUKI".

  `END-026` is `DONE`.
- **Checks:** `pytest` 204 passed, 1 skipped; `ruff check`, `ruff format
  --check`, and `mypy tools` are clean. The regression passes 6 of 6.

Next action: `END-025` (closes M8). `LOC-001` is a backlog decision, to be
taken before a release.

## 2026-10-25 — END-025: coverage, exceptions, regression; M8 closed

- **New tool:** `tools/text/ending_coverage.py` (with unit tests), output
  `data/text/ending_coverage.json`, metadata only.
  - Per slot 0-25: the Japanese and English page pointers, page counts, the
    slots that share each pointer, arcade identity, and the `MC13` records.
  - The last pointer of each table has an unknown extent: slots 23-25
    (Japanese) and 19-25 (English).
  - With `--built-track build/end027/...`, every byte outside the roster's
    targets is unchanged: `ME.PAC` (3503 bytes changed inside), decoded
    `MC13` (2724 inside), and `MM.BIN` (172 inside, matching the compiler's
    162 + 10).
- **Findings recorded:**
  - Slot 0 (Apocalypse) shares Cyclops's pages in both arcade tables.
  - Slot 19 shares Dan's Japanese pages.
  - The US arcade's English slot 17 (Norimaro) points to Dan's English.
  - Slots 19-25 all point to one English block.

  Accepted side effects and exceptions are in `docs/coverage_exceptions.md`.
- **Unknowns recorded** (`docs/known_unknowns.md`):
  - the KO character;
  - ordinary-fight vitality;
  - long-name centring;
  - Dan's "THE END";
  - live coverage (7 of 17 endings);
  - the extents of the excluded blocks.
- **Checks:** `pytest` 206 passed, 1 skipped; `ruff check`, `ruff format
  --check`, and `mypy tools` (55 files) are clean.
- `END-025` and `END-020` are `DONE`. **M8 is complete.** No task is `READY`.
  The next work needs a user decision: `SPECIAL-001` (M9), `LOC-001`,
  `REL-001`, or the backlog.

## 2026-10-25 — REL-001: xdelta3 release patch and reproduction README

- **User decisions:**
  - the format is xdelta3 (VCDIFF);
  - the patch stays local, with a README listing the assets needed to rebuild
    it;
  - installing xdelta3 3.2.2 with Homebrew was approved (`brew install
    xdelta`).
- **Finding:** the task note's `tools/disc/make_patch.py` did not exist; only
  `tools/memory/make_patch.py` (RAM dumps) did. The new disc tool is at the
  noted path.
- **Mistake caught and fixed:** writing the new tests first overwrote the
  existing `tests/unit/test_make_patch.py` (the RAM-tool tests). It was
  restored from git, and the new tests are in `test_disc_make_patch.py`.
- **Measurements:** only track 01 differs from the source: 178 sectors, about
  363 KB of changed runs. With `-e -9 -S none -A -f`, the patch is 155,717
  bytes (`00c3906a…`). xdelta3 rejects a wrong source ("target window checksum
  mismatch", tested on synthetic files).
- **Checks:**
  - deterministic double encode;
  - `xdelta3 -d` round trip;
  - a user-style apply to a copy of the original matches all 13 components of
    `build/end027`;
  - a fresh clone with only the disc, `mshvsfu.zip`, and `cps2.cpp` passes
    6 of 6 references and reproduces the identical patch and record.
- The font-candidate list was copied to `data/text/font_candidates.json` (code
  numbers only, `32e513ae…`). The compiler default and the regression baseline
  now point there.
- **Session checks:** `pytest` 210 passed, 1 skipped; `ruff check`, `ruff
  format --check`, and `mypy tools` (56 files) are clean.
- **Not tested:** graphical VCDIFF patchers.

Next action: none `READY`. A user decision is needed: `SPECIAL-001` (M9),
`LOC-001`, or the backlog.

## 2026-10-25 — New requests added to the plan

- **The user asked for four additions:**
  1. Use the credits' font (which the user finds close to the US caption font)
     instead of the white font. High priority.
  2. Scope the name art and voice (Bison/Akuma), with parallel patch paths for
     both name conventions in English, and an Options toggle as a stretch.
     Medium priority.
  3. Make the player-2 "PRESS START" English only.
  4. Write a detailed agent playbook, to repeat this on XvSF.
- **Observations used to write the tasks (no experiment):**
  - The credits (`local/end026/rec`, e.g. `f00009966`, `6fc4e105…`) draw a
    gold, gradient, slanted Latin font with lower case.
  - 1-second frames of a stage-1 fight show only "PRESS START" and blank, so
    the Japanese alternation is not captured yet.
- **Added:**
  - `FONT-010` (`READY`), then `FONT-011`;
  - `LOC-002` (`READY`) to `LOC-006`, with `LOC-001` updated to the user's
    direction;
  - `UI-001` (`READY`);
  - `DOC-020` (`READY`).

Next action: `FONT-010`.

## 2026-10-25 — DOC-020: cross-game agent playbook for XvSF

- **Wrote** `docs/playbook_cross_game.md`, a playbook for repeating this
  localization on X-Men vs. Street Fighter (Saturn), to be copied into a new
  repository.
- **Sources read:** `AGENTS.md`, `TASKS.md`, `docs/discoveries.md`, this log
  (including the failed approaches), `docs/coverage_exceptions.md`,
  `docs/localization_plan.md`, `docs/known_unknowns.md`,
  `docs/mednafen_agent_interface.md`, `docs/agent_briefing.md`,
  `data/translations/README.md`, `release/README.md`, `references/xmvsf/`,
  and the experiment READMEs it cites.
- **Labelling** (`AGENTS.md` rules 13-15, 25): every game fact is an MSHvSF
  fact with its evidence pointer, followed by a "Verify on XvSF" point. The
  only XvSF statements are the existing intake records of the held files.
  Nothing was asserted about XvSF internals, and no XvSF file was opened.
- **Contents:** design decisions and rationale; the milestone order and the
  decision point at each step; tools and their validation, with emulator
  limits; pitfalls and disproven ideas; the user's localization decisions;
  working with the user; a consolidated XvSF checklist.
- `DOC-020` is `DONE`.

Checks: documentation only; no code changed.

## 2026-10-25 — FONT-010 / EXP-0051: the credits font

- **No gameplay.** States from the `END-026` recording were replayed on the
  `m8_roster` image.
- **Steps:**
  1. Credits sprites are VDP1 16 × 16 4 bpp cells.
  2. No disc file holds them raw or LZSS-decoded, but `TESTFIX.DAT` has
     matching 8 × 8 quadrants for capitals, digits, and punctuation (a side
     finding).
  3. CPU write breakpoints on VDP1 VRAM never fired.
  4. Lower-case tiles are in neither WRAM nor extracted cart RAM.
  5. Logging the SCU DMA registers found transfers from `0x0601CEEC`, called
     from the quote-font glyph routine (`0x0601CDF2` in `0x0601CE00`).
  6. Every tile matched a quote-font glyph: codes `0x1E0`-`0x25F`.
- **Comparison:** the same style as the US arcade caption font (gold gradient,
  outline, slant), but twice as wide.
  - One glyph per cell cannot fit 25-character lines.
  - Squeezed pairs fit and resemble the arcade. Thin glyphs need tuning.
  - Gold needs palette work (the caption bank `0x6030` uses only white and
    black).
- **Disproven or unproductive (do not retry blindly):**
  - raw and LZSS searches for the 16 × 16 tiles;
  - VDP1 VRAM write breakpoints, which gave no hits even on the command
    table;
  - WRAM and cart RAM searches for the staged lower-case tile.

  Use the SCU DMA register log instead.
- **Tooling and checks:**
  - New: `tools/memory/vdp1_commands.py` (VDP1 sprite list and glyph
    matching) and `tools/text/credits_font.py` (credits code map, squeeze, and
    mockups), with tests.
  - Recorded the caveat that `font_candidates.json` lists "unseen", not
    "unused", codes.
  - `pytest` 214 passed, 1 skipped; `ruff check`, `ruff format --check`, and
    `mypy tools` (58 files) are clean.
- **Environment note:** `build/end010`, `end023`, `end024_vega`, `end026`, and
  `end027` disappeared during this session, removed by something outside it.
  They are reproducible; `build/regression` holds the current reference
  images.

Next action: `FONT-011`, waiting on the user's choice: gold squeezed, white
squeezed, or the arcade font (`REF-012`).

## 2026-10-25 — FONT-011 / EXP-0052: credits-style pairs (silver live); gold blocked

- **User choices:** gold squeezed credits pairs with thin glyphs tuned; then,
  when gold proved blocked, "Both: build silver, then dig".
- **Palettes** (agent replays of recorded states):
  - Caption banks `0x1E0`, `0x030`, and `0x1F0` are the credits layout in
    grey.
  - Gold bank `0x010` is always loaded.
  - `colr = (attr & 0x7000) | (palette << 4)`; caption palette numbers are
    `0x1E`, `0x03`, and `0x1F`.
- **Disproven or unproductive (do not retry blindly):**
  - CPU write breakpoints on the caption CRAM bank, both aliases, over the
    window where it changes: no hits;
  - SCU and SH-2 DMAC set-up logs: no transfer to it;
  - searches for the grey palette in WRAM before the copy, in cart RAM, and
    on disc: not found;
  - the win-screen object palette byte (+39, table `0x060C0E00`): fighter
    palettes 0-3, not the caption.

  A remap in the shared sprite writer would recolour fighters.
- **Glyphs:**
  - The full gradient does not fit: 40,852 bytes of pairs against 30,235
    reclaimable.
  - Used: two shading bands with a 4-connected outline (29,284 bytes).
  - Hand-drawn `I`, `M`, `W`, `m`, `w`, `!`, `'`, and `‼`.
  - `fit_fill` resampling was rejected: it lost dots and shapes.
- **Build:** `build/font011` (`9246148f…`), all checks true. New regression
  reference `m8_roster_credits`; all seven pass.
- **Live:** the win quote (Ryu + Ken) and an ending (dialogue and Ryu's
  pages) displayed correctly in silver. Capital `W` is weak.
- **Mistake:**
  - The ending driver was armed after stage 2 had loaded; its boss test
    matched the stage-2 start and zeroed boss-only words. The user lost and
    the credit timed out.
  - **Rule:** arm before the next stage loads, at character select or on the
    win screen.
- **New user report:** "EASY" at mode select alternates with Japanese, so
  `UI-002` was added. "対戦者求む!" was captured alternating with "PRESS
  START" (`UI-001`).
- **Checks:** `pytest` 216 passed, 1 skipped; `ruff`, `ruff format`, and
  `mypy` are clean.

Next: the gold investigation (`EXP-0052` next experiments), then the `W`
redesign.

### 2026-10-25 — FONT-011 gold dig, round 2

- The grey caption bank appears at frame 91 (second copy), then 92 (both),
  after `end024v f00008668`. There is no other RAM copy in frames 60-121.
- Both SH-2s run `CheckRWBreakpoints` (`ss.cpp`). The invisible writer is
  DMA, or a store the pre-decode check misses (HYPOTHESIS: delay slots). SCU
  DMA `0x0601BABC` is direct mode, CRAM uploads only.
- **Palette path:**
  - the emitter `0x060733BC` uses `@(14,GBR) & 0x1F`;
  - `@(12,GBR)` = `0x1E` is restored from a shared context stack
    (`0x06019B5C`);
  - the per-object source is behind the object interpreter. Not found yet.
- **Not productive (do not retry blindly):**
  - write breakpoints on the CRAM-copy bank (no hits);
  - write breakpoints on the shared context stack (only save/restore
    traffic);
  - the `0x0842` constants at `0x0603AF1E`/`0x0603AF46`, which sit in an
    opcode table.
- Three remaining routes are recorded in `EXP-0052`.

### 2026-10-25 — FONT-011 gold, route 1: found and verified live

- **The palette byte** is object +72, read by the emitter at `0x06073354`
  (low five bits; the win quote's is `0x9E`). The earlier filters missed it by
  matching `0x1E` exactly: **filter on `value & 0x1F`.**
- **The initialiser** is a message-window jump table at `0x060AECD4`. Its
  immediates (`MM.BIN`) are `0x961E3` = `0x9E` (win quote), `0x961FB` =
  `0x9F` (pages), and `0x96233` = `0x83` (dialogue). Each was set to `0x81`
  for gold bank 1.
  - The RAM trials showed all three gold. The dialogue trial must start
    before its object is created (`end026 f00004049`).
  - `0x0605AEE1` (`0x03`) is a fighter palette.
- **Build:** `--caption-palette gold` adds the patches with `expect` bytes
  (the compiler now verifies them). Track 01 `3a6c485c…`; reference
  `m8_roster_gold`; 8 of 8 references pass.
- **Live (one cold boot):**
  - A Dark Sakura + U.S. Agent credit (excluded) showed the Japanese windows
    in gold too.
  - Ryu + Ken: the dialogue and three pages in gold.
  - A user win (Ken + Dan): the win quote in gold.
- **Left:** the `W` design; whether the release patch switches to gold.
- **Checks:** `pytest` 217 passed, 1 skipped; `ruff`, `ruff format`, and
  `mypy` are clean.

### 2026-10-25 — FONT-011 closed: capital W, release switched to gold

- **Capital W:** variant A (vertical strokes, a centre stroke from row 4,
  joined at row 8, tapered bottom), chosen from four 3x gold renders.
- **Rebuild:** `e213140a…`; zero fill 0. `m8_roster_credits` and
  `m8_roster_gold` were re-baselined; 8 of 8 pass.
- **Live:** "We shall meet again / KEN." reads correctly in gold
  (`dd5ce932…`).
- **Release:** the gold patch `94b27498…` (158,280 bytes), record
  `release/m8_roster_gold.json`, README updated. The white `m8_roster` record
  is kept.
- `FONT-011` is `DONE`.

## 2026-10-25 — UI-001 / UI-002 / EXP-0053: English-only UI labels

- **Sources:** the player-2 prompt "対戦者求む!" is quote-font cells
  `0x45B`-`0x45F`. The mode panel's "簡単操作" is `0x424`/`0x428`/`0x42C`/
  `0x43A` (four shading copies), each matching an EASY copy (`0x6A6`…`0x6AC`).
- **English art already in the font:** JOIN IN, INSERT COIN, GAME OVER, and
  the US/JP life-bar names (useful for `LOC-002`). The US arcade shows INSERT
  COIN in that corner.
- **User choice:** JOIN IN.
- **Implementation:** `glyph_copies` (compiler-verified), via
  `official_endings --ui-english`. Build `7a3917d1…`; `m8_roster_gold`
  re-baselined; 8 of 8 pass; release patch `7e7d7118…` (158,333 bytes).
- **Live:**
  - EASY is steady (cold boot, 100 frames).
  - The P2 alternation did not appear in this session. It has appeared in
    only one of six sessions, and the trigger is unknown.
  - JOIN IN was verified by replaying the silver state with the new font
    transplanted into its cart RAM. The original state font matched the
    build byte for byte, which validates cart-RAM extraction there.
- **Not productive (do not retry blindly):**
  - waiting for the P2 alternation live;
  - replaying recorded states for the mode panel, which diverge without
    input.
- **Checks:** `pytest` 218 passed, 1 skipped; `ruff`, `ruff format`, and
  `mypy` are clean.

## 2026-10-25 — LOC-002 / EXP-0054: name art and voice inventory (in progress)

- **Life bars:** quote-font label cells; both conventions are in the font
  (VEGA `0x760`/BISON `0x763`; GOUKI/AKUMA; MECH-GOUKI `0x568`/CYBER-AKUMA).
  A BISON swap was shown in a replay with a transplanted font.
- **Win banner:** large letter glyphs `0x2E0`-`0x35F`, so the name is spelled;
  its string table is not located.
- **Ending speaker labels:** an ASCII table in `ME.PAC` `0xB164`, which
  already contains Akuma and Bison.
- **Menus and sound test:** ASCII in `MM.BIN` ("MECH-GOUKI NOW!!" `0x24F03`;
  "18.VEGA"/"22.GOUKI" near `0x6341`).
- **VS screen:** mosaic sprites. The source is not found raw or as LZSS;
  probably `SEL*.PAC`.
- **Audio:** `.ADP` files are music. Voice candidates are `CMNSE.PAC` and
  `PLxx.PAC`, and identifying the clip needs listening.
- **Not productive:**
  - static searches for the label-code table (coincidental matches);
  - write breakpoints on GBR+16/+18 for label bases (too noisy;
    coincidences);
  - a tile search for VS name art across all files.
- **User question (PS1 vs arcade):** most surfaces need no import. For the VS
  screen and voice, PS1 is recommended first (linear TIM images, SPU/XA
  audio), after confirming the Saturn lacks them.
- **LOC-002 voice follow-up:** the user hears "Vega" at character select and
  in the win announcement.
  - An SCSP slot trace (from state `SlotRegs` every 3 frames) shows only
    three looping stream slots, so sound is software-mixed.
  - Sound RAM at the win screen maps to `CMNSE.PAC` (common bank, the likely
    announcer source), `MEMFIX.PAC`, and `PLxx.PAC` fragments.
  - Reading SCSP registers through the agent's `physical` space returns
    zeros; use states instead.
  - `LOC-002` is `DONE`; `LOC-003` is `READY`. `LOC-004` and `LOC-005` have
    their blockers refined.

## 2026-10-25 — LOC-005 / EXP-0055: CMNSE.PAC decoded and exported

- **Bank layout:**
  - u32 count at `0x10` (88);
  - (u16 tag, u16 length) entries from `0x14`, with ID `tag & 0x3FF` and
    flags `tag >> 10`;
  - data concatenated from `0x174`.
- **Decoder:** found by searching WRAM-H for the ring-buffer literals
  (`0x05A00484`/`0x05A0248C`), which led to the SH-2 mixer.
  - Per-nibble routine `0x0600D420`: `d = step*m >> 2`, `pred ± d` (no
    clamp), `step = step*MUL[m] >> 16` clamped to `0x80`-`0x6000`, with
    `MUL` at `0x0600D46C` = 0.9×4, 1.2, 1.6, 2.0, 2.4.
  - High nibble first; a clip starts at (0, `0x80`). Each sample is
    doubled into the 24,031 Hz rings, so clips play at 12,015.5 Hz.
- **Verification:** `tools/audio/channel_check.py` over 44 `end024v`
  states found 24 of 24 active channels matching exactly. The 73
  mismatching records are all inactive and stale.
- **Export:** `tools/audio/cmnse_bank.py` writes 88 WAVs to
  `local/audio/cmnse/`. Local listening aids `index.html`, `catalog.wav`
  and `catalog.tsv` were sent to the user to identify "Vega" and "Gouki".
- **Disproven (do not retry):**
  - IMA, OKI and Yamaha ADPCM, in either nibble order. All drift (mean
    |DC| / peak 0.27-0.41, against 0.012 for the real decoder).
  - Low-nibble-first order.
  - Searching memory for a standard step table: there is none, because the
    step is multiplicative and the table holds 8 multipliers.
  - Treating the 68K nibble code at `0x46B8`-`0x4774` as the decoder: it is
    the sequencer.
- **Not productive:**
  - envelope matching between the recorded WAV and the decoded clips;
  - cross-correlating win-screen ring buffers with the clips. The mix holds
    up to 16 channels from several banks, so it cannot single out clips
    (best score 0.66).
- **Scratch-only dependencies:** numpy and capstone through
  `uv run --with` (uv 0.11.7). They are not added to the project.
- **Checks:** `pytest` 226 passed, 1 skipped; `ruff`, `ruff format` and
  `mypy` are clean.
- **Next:** the user listens and names the clips. Then, if they approve
  `LOC-005`: source a US clip and write the encoder. `LOC-003` remains the
  next unblocked task.

## 2026-10-25 — LOC-005 / EXP-0056: name calls are in the fighter and select banks

- **User listening:** none of the 88 `CMNSE.PAC` clips announces a name.
  The closest is "Ken", split off from "Hadou-". This disproves
  `CMNSE.PAC` as the name source.
- **Channel → file mapping:** across the `end024v` states, the mixer also
  plays data from `MEMFIX`, `PL05`/`09`/`0E`/`0F`/`13`, `SEL`/`SEL2` and
  movie files.
- **Container:** these PACs are (u32 flag, u32 size) pairs ended by (0, 0),
  followed by the payloads back to back. Flag `0xFFFFFFFF` means no
  payload.
- **Banks:** 28 payloads are banks with an exact size fit, 725 clips in
  total (`tools/audio/sound_bank.py --file '*'`). `cmnse_bank.py` is renamed
  to `sound_bank.py`.
- **Candidates:**
  - Vega's `PL0E` bank shares #1, #5, #7 and #18 with the select bank;
    Gouki's `PL0F` bank shares #1, #11, #13 and #23.
  - On the win screen, Vega-bank #18 (`0x286`, also select #48) played
    between `f00008316` and `f00008668`. It is the best "Vega" candidate
    (SUPPORTED).
- **Sent to the user:**
  - `local/audio/shortlist.wav` and `.tsv`, with Vega-bank #18 at 5.41 s;
  - the full `pl0e_1` and `pl0f_1` catalogs.
- **Checks:** `pytest` 228 passed, 1 skipped; `ruff`, `ruff format` and
  `mypy` are clean.

## 2026-10-25 — LOC-005 / EXP-0056: name calls identified by listening

- **User listening:** the name calls are clip #1 of each fighter bank.
  - `PL0E.PAC` #1 (`0x04F`) says **"Bison"**; `PL0F.PAC` #1 (`0x048`)
    says "Gouki".
  - In each, the name starts about 1 s in, after another sound.
  - Both clips are also in the select bank (`SEL.PAC` payload 1, #4 and
    #3).
- **Disproven:** Vega-bank #18 (`0x286`) as the name call. It was only the
  last clip seen in a channel record after the win banner. Clip #1 played
  between the recorded states.
- **Open:**
  - The voice says "Bison" while the text says "Vega", and the user's first
    description of the in-game line was "Vega". Seeing the mixer start
    `0x04F` would settle whether the in-game lines are this clip.
  - If they are, the American-name variant needs only an "Akuma" clip.
- **Checks:** docs only. `pytest` 228 passed, 1 skipped; `ruff` is clean.

## 2026-10-25 — LOC-005 / EXP-0057: in-game clip log (in progress)

- **New tool:** `tools/audio/mixer_log.py` logs mixer clip starts frame by
  frame from a state and matches them to bank clips. Sound RAM is read through
  the agent's `scspram` space; cart RAM from a state saved at the end, because
  the agent refuses `savestate` while halted.
- **Win banner** (`end024v f00008316`): the mixer starts Vega-bank #18
  (`0x286`, also select #48) 116 frames in. `0x04F` is not started.
- **Character select** (`f00003038`): the last clip played was Vega-bank #5
  (`0x133`, also select #17). With no input the screen waits.
- **Not productive:**
  - replaying `f00007963` without input diverges into a continued fight;
  - the agent has no controller input;
  - the opponent's vitality in ordinary fights is unknown (`EXP-0049`), so
    a KO cannot be forced.
- **Status:** the clip-#1 name-call record is under review; the user is
  checking single clips A-E (`local/audio/confirm/`). It is removed from
  `docs/discoveries.md` until resolved.

## 2026-10-25 — LOC-005 / EXP-0057: clip identities settled by listening

- **User listening to single clips:**
  - A `0x04F` says "Bison"; B `0x133` is Vega's select voice; C `0x286`
    says "Vega"; D `0x048` says "Gouki"; E `0x1D1` is Gouki's select
    voice.
- **Conclusions:**
  - The win screen plays "Vega" (`0x286`).
  - The disc holds both names for this character. "Bison" (`0x04F`) was not
    seen played.
  - The `EXP-0056` reading ("the only name call is Bison"; "#18 is not a
    name call") is disproven and corrected there.
- **Next:**
  - find what selects `0x286` over `0x04F` (a sound-ID table, a region
    flag, or an unused leftover);
  - listen to Gouki's other select-shared clips (`0x25A`, `0x338`) for
    "Akuma".

## 2026-10-25 — LOC-005 / EXP-0057: every US-name call is on the disc

- **User listening, second round:**
  - G `0x338` (Gouki bank #23, select #62) says "Akuma";
  - I `0x05B` (`PL13` #1, select #7) says "Cyber Akuma";
  - J `0x082` (`PL13` #2, select #12) says "Mech Gouki";
  - F `0x25A` and H `0x1A5` are not names; the user is unsure where they
    are used.
- **Result:** both naming conventions are on the disc for Vega/Bison,
  Gouki/Akuma and Mech-Gouki/Cyber-Akuma. The American-name variant needs no
  new audio, sourcing or encoder. It needs the mechanism that picks the
  Japanese call, then a switch.
- **Next for `LOC-005`:** locate where the win and select code choose the
  sound ID (`0x286` for Vega). For example, search the program for the
  ID, or break on the mixer's channel set-up when `0x286` starts.

## 2026-10-25 — LOC-005 / EXP-0058: the name-call table, switched to "Bison" live

- **Search:** a scan for a per-character ID table (Vega `0x286` at 14,
  Gouki `0x048` at 15, Mech-Gouki `0x082` at 19) found `MEMFIX.PAC`
  `0x124B54` (16-byte records).
- **Location:** `MEMFIX.PAC` payload 7 is loaded byte-identical into sound
  RAM `0x6510`. It holds two tables with the same 23 IDs:
  - table A: 10-byte records at sound RAM `0x73B6` (file `0x124A5E`);
  - table B: 16-byte records at `0x74AC` (file `0x124B54`).

  Indexes 20-22 are the US calls.
- **Trials** (each one live poke at the `f00008316` win banner, replayed with
  `mixer_log --poke`):
  - table B entry 14 → `0x04F`: no change. An SH-2 read breakpoint on table
    B logged no reads;
  - table A entry 14 → `0x04F` (`scspram:7442`): the win call at frame 242
    becomes `0x04F` "Bison". Nothing else changes. **CONFIRMED.**
- **Not productive:** `0x0286` at sound RAM `0x3226` is ring-buffer audio,
  a coincidence.
- **Switch for the US variant:** six u16 edits in `MEMFIX.PAC`, copying
  entries 20-22 into 14/15/19 of both tables. It is not built or
  cold-booted yet; that belongs with `LOC-003`.

## 2026-10-25 — LOC-003 / EXP-0059: the American-name variant build

- **Switch:** `official_endings --names saturn|us`.
  - `saturn` (the default) regenerates the stored gold spec exactly
    (`7ce7820a…`).
  - `us` drops the name and text overrides and adds the six `MEMFIX.PAC`
    name-call edits with expect checks.
- **US build:**
  - Every compiler check is true; only patched bytes change.
  - New reference `m8_roster_gold_us` (track 01 `e1337dbf…`). 9 of 9
    references pass with regenerated specs.
  - Release patch `82208a8c…` (155,248 bytes, deterministic, round trip).
- **Cold boot:**
  - The US image's sound RAM tables hold the American calls at 14/15/19
    from frame 2463.
  - Control: the Saturn image holds the Japanese calls.
- **Docs:** `release/README.md` explains the two variants. The US one is a
  preview while the name art is unchanged.
- **Tasks:** `LOC-003` DONE; `LOC-004` READY; `LOC-005` READY, with only the
  in-play listening check left.
- **Checks:** `pytest` passes; `ruff`, `ruff format` and `mypy` are clean.

## 2026-10-25 — LOC-004 / EXP-0060: US life-bar names and speaker labels

- **Cells drawn by the fight HUD** (glyph logs): VEGA `0x760`-`0x762`, GOUKI
  `0x750`-`0x752`, MECH-GOUKI `0x568`-`0x56D`.
- **US variant:**
  - copies BISON `0x763`-`0x765`, AKUMA `0x753`-`0x755` and CYBER-AKUMA
    `0x5D9`-`0x5DE` over those cells;
  - sets the `ME.PAC` speaker fields 14, 15 and 19 to Bison, Akuma and
    Cyber Akuma.
- **Build:** the Saturn spec is unchanged. The US spec is `781f70ee…`, track 01
  `49e002df…`, patch `0e055dbc…`. 9 of 9 references pass.
- **Seen:**
  - a BISON / CYBER-AKUMA HUD in a replay with the US font transplanted;
  - a "Bison" speaker label after writing the WRAM-L table copy (`0x23B234`)
    before the page opens. Writing after the page is shown does nothing.
- **Limitation:** AKUMA is 2 px wider than GOUKI's 3-cell sprite, so its last
  A's foot is clipped. The sprite-width table was not found; static searches
  for a per-character label table (index 14 = `0x760`, 15 = `0x750`) found
  nothing.
- **Not used anywhere seen:** the italic label set and the first MECH-GOUKI
  copy. The VS screen draws no quote-font labels (450-frame glyph log).
- **Process error (discarded):** a background glyph scan ran a second
  Mednafen on the same agent directory as foreground replays. Both answered
  commands. Those results were discarded, the checks were rerun one at a
  time, and the pitfall is added to `docs/agent_briefing.md`.
- **Not productive:** tracing `R2` at the glyph routine (it is the cache slot
  map, `0x263D62 + 2 * (code - 0x480)`, not a source pointer).
- **Checks:** `pytest` 232 passed, 1 skipped; `ruff`, `ruff format` and
  `mypy` are clean.

## 2026-10-25 — LOC-004 / EXP-0061: US names in the sound test and the menu

- **Edits** (same-length `MM.BIN` ASCII, with expect checks):
  - `0x6341` "18.VEGA" → "18.BISON";
  - `0x639D` "22.GOUKI" → "22.AKUMA";
  - `0x24F03` " MECH-GOUKI NOW!!" → "CYBER-AKUMA NOW!!".

  No other regional-name ASCII exists in the program and text files.
- **Build:** the Saturn spec is unchanged. US spec `8f0b63de…`, track 01
  `fbb64910…`, patch `65275636…` (155,842 bytes). 9 of 9 references pass.
- **Cold boot:**
  - the US image's RAM holds the new strings at `0x0601EE41`,
    `0x0601EE9D` and `0x0603DA03`; the Saturn image holds the old ones there;
  - the menu pointers target `0x0603DA03`, the slot start.
- **Side finding:** `ME.PAC` = `ME.SHX` plus a 16-byte container header. The
  loaded speaker table comes from it, so the `EXP-0060` edits are effective.
- **Not seen on screen:** the agent cannot navigate menus.
- **Checks:** `pytest` 233 passed, 1 skipped; `ruff` and `mypy` are clean.

## 2026-10-25 — Task added: UI-003 (attract-mode teaser screens)

- User request: the attract-mode teaser screens before the gameplay demo
  still show a lot of Japanese; replace them with their US versions.
- Added `UI-003` (`READY`): a cold-boot inventory (no input needed), the
  source of each screen, the US arcade and PS1 US releases as oracles, a
  replacement route per screen, and a build with regression.

## 2026-10-25 — LOC-004 / EXP-0062: win banner switched to the disc's US records

- **Trace:**
  - the KO state `end024v f00008316` reaches the banner at about +150
    frames;
  - VDP1 commands at +200 give the letter codes;
  - a write breakpoint on the V's command slot found the generic emitter
    `0x0601C9C4`, with R5 = `0x32E` and pattern = `0x5000` + code;
  - a search for `0x532E` led to the `MM.BIN` name records `0x9FD38`-
    `0xA0140` (letters right to left) and their pointer table
    `0x9FBF8 + 12i`.
- **US records already present:** BISON (`0x060B8BCE`), AKUMA (`0x060B8BEC`),
  CYBER-AKUMA (`0x060B8C0A`), at entries 23-25.
- **Trial:** writing `0x060B87A0` = `0x060B8BCE` before the banner makes it
  read BISON / RYU / WIN. The control without the write reads VEGA.
- **Build:**
  - three u32 pointer edits with expect checks (`US_BANNER_POINTERS`);
  - Saturn spec unchanged; US spec `84a95315…`, track 01 `0afe0f7a…`, patch
    `c4b69e46…`; 9 of 9 references pass.
- **Cold boot of the US image:** the table loads by frame 1800 holding the
  US pointers. It is absent at the title screen (frame 2700) on both images,
  and not reloaded when a fight loads.
- **Not productive:**
  - shifted-ASCII, letter-index, code-offset and masked-code searches for
    the name (the records hold sprite patterns `0x5000 + code`);
  - glyph-routine breakpoints: the banner letters are below the glyph
    cache's range (`0x480`+);
  - the WRAM-H "VEGA" at `0x060047F5` (the `M1A_SVEGADP` music file name).
- **Checks:** `pytest` 234 passed, 1 skipped; `ruff` and `mypy` are clean.

## 2026-10-25 — LOC-004 / EXP-0063: VS-screen names switched via the disc's US records

- **Sprites** (VS state `end024v f00009368` +60, VDP1 list): each name is
  a row of 16×16 letter sprites at an 11 px pitch, drawn from the
  staff-credits font (A = `0x210`, hyphen `0x20F`). These are not `SEL*.PAC`
  art (`EXP-0054` assumed a mosaic).
- **Records:**
  - searching for the reversed pattern sequence `0x5000 + code` found the
    `MM.BIN` VS name records (`0x6666A`-`0x668DA`), including BISON, AKUMA
    and CYBER-AKUMA (entries 23-25);
  - the pointer table is at `0x66536 + 12i`.
- **Trial:** from `f00009018`, writing Vega's RAM pointer (`0x0607F0DE`) to
  BISON shows BISON on the VS screen. The control shows VEGA.
- **Build:**
  - three more u32 pointer edits (`US_NAME_POINTERS`, which now also holds
    the banner's);
  - Saturn spec unchanged; US spec `a343d7c7…`, track 01 `41ca8a9a…`, patch
    `ccf6200c…`; 9 of 9 references pass;
  - a cold boot loads the US pointers at frame 1800.
- **LOC-004 remaining:** the AKUMA life-bar width, and a cold-boot play-through
  with screenshots.
- **Checks:** `pytest` 234 passed, 1 skipped; `ruff` and `mypy` are clean.

## 2026-10-25 — EXP-0064: cold-boot play-test of the American-name build

- **Setup:** the US image with `-soundrecord`, the ending driver armed at boot,
  `session_recorder` (0.5 s shots, 3 s states) and the new
  `tools/audio/live_calls.py`, all sharing one emulator. The user picked Gouki
  then Vega.
- **Name calls:** "Akuma" `0x338` (frame 4073) and "Bison" `0x04F` (4382) at
  select. The win call was "Akuma" `0x338` (5869, a cart clip, confirmed from
  state `f00005893`). No Japanese name calls.
- **Screens:** select BISON; VS BISON / AKUMA vs CYBER-AKUMA; life bars AKUMA
  vs CYBER-AKUMA; banner AKUMA / BISON / WIN; dialogue "…we have, BISON."
- **Tasks:** `LOC-005` DONE. `LOC-004` has only the AKUMA life-bar width
  left.
- **Note:** capture ended in the post-boss dialogue, when the user typed
  "credits". The ending pages were not reached.

## 2026-10-25 — LOC-004 / EXP-0065: life-bar label records fix AKUMA's width

- **Records:** the life-bar labels are `MM.BIN` records of 8 patterns, in two
  tables:
  - player 1 at `0x32CA4 + 16i` (bold);
  - player 2 at `0x32E74 + 16i` (italic, right-aligned).

  The US records are entries 26-28, and AKUMA there is 4 cells (`0x753`-
  `0x756`).
- **Trials** (RAM writes from play-test state `f00004857`): the player-1
  AKUMA record shows the whole final A. The player-2 slot shows italic BISON.
- **Correction to EXP-0060:** the italic set *is* used, for the player-2 side.
  `EXP-0060`'s glyph copies left CPU Vega/Gouki opponents named VEGA/GOUKI.
  The record copies replace the glyph copies and switch both sides.
- **Build:** six 16-byte `MM.BIN` record copies with expect checks. The label
  font cells now equal the source. US spec `2840b15b…`, track 01
  `87d1daec…`, patch `644d04eb…`. 9 of 9 references pass. A cold boot loads
  the US records by frame 1650.
- **Checks:** `pytest` 235 passed, 1 skipped; `ruff` and `mypy` are clean.

## 2026-10-25 — UI-003 / EXP-0066: attract-mode teaser inventory and source

- **Capture:** cold boot of the `m8_roster_gold` image for 21,000 frames
  (screenshots every 30 frames, states every 600), plus a 6-frame fine scan
  of one cycle.
- **Captions:** the cycle repeats about every 3,146 frames, with four
  Japanese captions:
  - "ヴァリアブル ヒーロー バトル";
  - "広がれ!! ヒーロー ワールド";
  - "第2弾!!" (red);
  - "解き放て! 友情パワー".

  There is also a Norimaro screen (Japanese brush text plus English); it is
  out of scope without approval.
- **Source trace:**
  - no VDP1 sprites; all NBG layers in cell mode, with the caption tiles at
    VDP2 VRAM `0x6000`+;
  - no file holds them raw or as LZSS;
  - they are in WRAM-H at `0x06086020`, filled by the LZ decompressor
    `0x06021F0C`/`0x06021F44` and DMA'd to VDP2 (VRAM write breakpoints
    see no CPU writes);
  - the decompressor's input stream is found in all eight
    `MVSOP0`-`MVSOP7.ST2` files.
- **Not productive:** the first stream probe was all `0xFF` and matched
  almost every file; use high-entropy probes.
- **Next:** the US oracle (MAME `mshvsfu` attract; PS1 US), then decode the
  `.ST2` layout and the LZ codec.

## 2026-10-26 — UI-003 / EXP-0067: US arcade oracle for the attract captions

- **Runs:** MAME 0.289 runs of `mshvsfu` and `mshvsfj`, without input, with a
  snapshot every 15 frames for 15,000 frames, plus 3-frame fine runs of the
  first caption stretch.
- **Pairs** (by sequence position):
  - ヴァリアブル ヒーロー バトル (white) + 第2弾!! (red) → **LEGENDARY HEROES
    UNITE AGAIN!!** (one caption);
  - 解き放て! 友情パワー → **AMAZING TEAM BATTLES!**;
  - 広がれ!! ヒーロー ワールド → **NEW HEROES JOIN THE FIGHT!!**.
- **Style:** the US captions are yellow-orange outlined capitals. There is no
  Norimaro screen in the US set.
- **Not productive:** pairing by frame number. The two sets' cycles have
  different timings; pair by neighbouring screens.
- **Next:** decode `MVSOP*.ST2` and the LZ codec; agree the art route and the
  two-to-one mapping with the user.

## 2026-10-26 — UI-003 / EXP-0068: MVSOP*.ST2 decoded; caption tiles and maps extracted

- **Graphics LZ** (`0x06021EDA`): u32 csize, u32 size; flag bits MSB first;
  1 = 12-bit-back copy of 3-18 bytes. The offline decoder reproduces the
  RAM caption tiles exactly.
- **`.ST2` container:**
  - header: section sizes (A: map streams loaded to WRAM-L `0x2C0000`; B:
    events; C: a graphics block);
  - stream: 0x800-byte sectors, with `MISS` sectors carrying 0x7FC-byte
    graphics payloads and other sectors interleaved.

  The game decodes stream blocks into WRAM-H `0x06080000`, alternating
  WRAM-L `0x240000`/`0x260000` for the input.
- **Caption layer:** NBG2 page 0 (VRAM `0x70000`). Captions 1 and 2 share a
  page and are chosen by vertical scroll.
- **Map path:** bit-flag LZ (`0x06022750`) into a ring, then word LZ
  (`0x0602234C`) into the arrays at `0x06037020`/`0x06039020`, then the
  macro-cell builder (`0x0601FD70`) into `0x06050000`, then DMA.
- **Extraction:** `tools/memory/vdp2_plane.py` writes map, tiles and a render
  per caption (`local/ui003/extract/`).
- **Sources:** captions 1-2 in section C, captions 3-4 in stream blocks; all
  four in every `MVSOP0`-`7`.
- **Not productive:**
  - searching for contiguous blocks on disc: `MISS` sector tags break the
    blocks every 0x7FC bytes;
  - treating `0x06086000` as the output start (it is `0x06080000`).
- **New tools:** `tools/disc/st2_stream.py`, `tools/memory/vdp2_plane.py`;
  tests in `tests/unit/test_st2_stream.py`.
- **Checks:** `pytest` 239 passed, 1 skipped; `ruff` and `mypy` are clean.

## 2026-10-26 — UI-003 / EXP-0069 (in progress): English caption design and constraints

- **User decision:** use the Saturn's own win-banner letters, as close to the
  US wording as fits.
- **Banner font:** A-Z, `!` `?` `.` `-`; 32×32 letters drawn 24 px apart;
  colours from CRAM bank `0x10`.
- **Tile constraint:** repeated Japanese characters share tiles, so only
  irregular bands are repaintable. "THE FIGHT!!" does not fit.
- **Palette path:** the caption palettes are generated (`0x0601FFD8`) from
  `0xFRGB` values at `0x0602E020`, which the section-A word-LZ codec fills.
  Yellow therefore needs the section-A codecs.
- **Mock-ups:** `local/ui003/mockup*.png`, sent to the user.
- **Not productive:** searching the disc for the CRAM ramp words (they are
  generated from `0xFRGB` values); CRAM write breakpoints (CRAM is filled by
  DMA from WRAM-H `0x06046C00`).
- **Next:** implement the map codecs (bit-flag LZ `0x06022750`, word LZ
  `0x0602234C`) and a graphics-LZ encoder.

## 2026-10-26 — UI-003 / EXP-0070: section A decoded (script, map and palette codecs)

- **Bit-flag LZ (Kosinski-like, `0x06022750`):** decoded. `MVSOP6` section A
  (`0x27FE8` of `0x28000` bytes) decodes to a `0x747C0`-byte command script;
  the ring contents match.
- **Word LZ (`0x0602234C`):** decoded. Map updates are 0x2000-word deltas
  with `0xFFFF` meaning keep.
- **Animated data:** from `f003154`, 74 map updates ran in 300 frames.
  Palettes are written per frame by handler `0x06022242` (fades). The cycles
  rotate through the eight `MVSOP` files.
- **Cost:** free layout needs rewriting per-frame map updates in eight
  scripts, within a section A that has only `0x18` bytes free. Yellow alone
  can come from editing palette values in place, plus a good re-encoder.
- **Tools:** `script_decode`, `map_decode` in `tools/disc/st2_stream.py`,
  with tests.
- **Checks:** `pytest` 241 passed, 1 skipped; `ruff` and `mypy` are clean.

## 2026-10-26 — UI-003 / EXP-0071: English attract captions built (middle route)

- **User decision:** banner letters drawn into the existing tiles (FIGHT!
  instead of THE FIGHT!!), yellow from palette values edited in place.
- **Palette command decoded** (`0x060221F8`): `[delta][count][words]` records;
  a record-level trace (breakpoint `0x06022218`, 2,076 records over 3,400
  frames from `f001909`) located every record in the decoded scripts.
- **Colour format:** `0xFRGB` through the table at `0x06060000`; all 14 banner
  colours convert exactly.
- **Encoders:** `tools/disc/st2_encode.py` (optimal-parse graphics LZ and
  section-A LZ), with round-trip tests.
- **Built:** `tools/disc/attract_captions.py`, layout
  `data/ui003/attract_captions.json`, generator option
  `official_endings --attract-captions`. US-names image with the captions:
  `build/ui003/us_attract` (track 01 `0f87cc6d…`); all four captions verified
  from a cold boot.
- **Disproven / not productive:**
  - *The caption palette lines belong to the captions alone.* Lines
    0x600/0x610 also carry other scenes' colours. Recolouring all five
    grey/red-ramp loads turned the Akuma/Chun-Li lightning background beige.
    Only the 1st, 3rd and 5th loads are caption scenes.
  - *The 1st and 5th loads are the only caption loads.* AMAZING TEAM BATTLES!
    stayed white; its scene starts at the 3rd load.
  - *The banner uses colours 1-11.* It uses 1-9 and 11-14 (12-14 are the cyan
    outline). Caption colour 1 is the page background, so banner colours
    shift to 2-15.
  - *Poking palette RAM right after `loadstate`.* The state load can land
    after the writes and undo them; the magenta test is reliable only when
    the CRAM copy is read back afterwards. Reloaded cycle states also drift
    from the original run, so `cap*.mcs` no longer show their captions on
    this image.
  - *Array word k is CRAM colour k.* It is colour k + 1 (the converter's
    first write is at `@(2, r13)`). Writing the banner colours to words 2-15
    put every colour one slot off (yellow showed dark grey, the purple outline
    orange); the user saw the colours as "really off". Compared with the US
    arcade caption (`mshvsfu_f01531.png`), the fixed build shows the same
    purple / yellow / cyan order.
  - A per-word palette trace (breakpoint at the write, `0x06022242`) was too
    slow; the per-record breakpoint was enough.
  - *Exact screenshot equality between runs.* Two cold boots of the same image
    differ in 72 of 440 frames (animation phase), so other-scene checks are
    by comparison against two baseline runs and by inspection.
- **Section sizes:** section A shrinks by about 4 KB per file; section C grows
  0x76-0x7A bytes into its own zero padding; caption blocks shrink.
- **Checks:** `pytest` 256 passed, 1 skipped (reference builds need the local
  image); `ruff check` clean; `ruff format --check` clean except the existing
  EXP-0070 README code block; `mypy tools tests` clean.
- **Colour fix and both variants (user, 2026-10-26: "Both name variants
  should get the English attract captions. But the colors seem really
  off.")** The banner colours now go in words 1-14 (see above). Both gold
  references take `--attract-captions`:
  - `m8_roster_gold`: spec `466b3c62…`, track 01 `857937f9…`, patch
    `0c2054b8…` (2,875,510 bytes);
  - `m8_roster_gold_us`: spec `db8d699d…`, track 01 `0f87cc6d…`, patch
    `ec54c990…` (2,873,639 bytes);
  - the patches grew from about 157 KB because re-compressed streams change
    most of their bytes.

## 2026-10-26 — UI-003 / EXP-0072: PS1 US attract captions (second oracle); UI-003 done

- **BIOS:** the user supplied `SCPH1001.BIN` (SHA-256 `71af94d1…`, MD5
  `924e392e…`), copied to the ignored `local/mednafen/firmware/scph1001.bin`
  and selected per run with `-psx.bios_na scph1001.bin`
  (`docs/mednafen.md`). Mednafen's sanity check accepts it.
- **Capture:** cold boot of the US disc, a screenshot every 15 frames for
  12,000 frames. Captions: LEGENDARY / HEROES / UNITE AGAIN!! (`f003512`),
  AMAZING / TEAM BATTLES! (`f003887`), NEW HEROES / JOIN / THE FIGHT!!
  (`f004142`); the cycle repeats about every 3,960 frames.
- **Result:** wording equals the US arcade; colours are `F206`, `FFF0`-`FF80`
  and `F0CC`, the same set as the fixed Saturn captions.
- **UI-003:** `DONE`.

## 2026-10-26 — UI-003 / EXP-0073: arcade-layout attract captions

- **User request:** match the PS1/arcade captions' symmetry and wording.
- **Decoded:** the section-A frame format (`0x06021FE4`; parser
  `script_frames`, all eight scripts to their end), the object list
  (`0x06022426`), and the macro-cell builder (`0x0601FD70`). A static replay of
  the map updates reproduces the extracted caption pages.
- **Built:** new caption maps (one macro per text cell, centred lines on a
  24-pixel grid, 3/2/3 lines as in the arcade); `map_encode` for the updates;
  per-file macro origins in `data/ui003/attract_captions.json` (schema 2).
- **Disproven / not productive:**
  - *One macro base (or character delta) per slot works for every file.*
    Slot 3 in file 4 uses base `0x2350`, and the block offsets of slots 3 and
    5 differ in half the files. The `EXP-0071` state-derived deltas were wrong
    for slot 3 in files 0, 2, 4, 6 and slot 5 in files 0, 1, 4, 5; origins are
    now derived by matching caption macros.
  - *Section C fits with the old glyphs kept.* It re-encoded to `0x18AD4` of
    `0x187F8` bytes; blanking the unused caption macros fixes it.
  - *The arcade's 28-pixel letter grid.* UNITE AGAIN!! would be 362 pixels on
    a 352-pixel screen; the banner's 24-pixel grid is used.
  - Section 9 of a frame reads a word per mask bit, not section 2's
    byte-or-word form (the first parser failed on five scripts).
- **Verified:** offline, every caption frame of every file renders exactly
  and no map state outside the windows changes; from a cold boot, all three
  captions (`EXP-0073`).
- **Release:** both gold references rebaselined: `m8_roster_gold` spec
  `e40f897f…`, track 01 `3185310c…`, patch `34e374d2…` (2,856,531 bytes);
  `m8_roster_gold_us` spec `e4a3e4aa…`, track 01 `db1ede9f…`, patch
  `f4350f39…` (2,854,660 bytes). All nine references pass.
- **Backlog (user, 2026-10-26):** `SPECIAL-002` (Norimaro post-fight text and
  ending; not the attract screen), `SPECIAL-003` (secret characters' text and
  endings), `LOC-007` (secret-character names JP vs US/EU), `OPT-001`
  (`--unlock-boss-fight`, default on). `SPECIAL-001`'s blocker is cleared.

## 2026-10-26 — LOC-004 / EXP-0074: AKUMA life-bar labels seen in play

- **Run:** cold boot of the US release image (`db1ede9f…`); the user played
  Versus with Gouki on both sides (keyboard on controller port 2 for this run).
- **Result:** player 1 full-width AKUMA (green span 49 px vs 47 px in the
  earlier clipped build), player 2 italic AKUMA, right-aligned. `LOC-004` is
  `DONE`.
- **Pitfall:** Mednafen saved the command-line port-2 settings into
  `mednafen.cfg` on exit; restored from a backup (`docs/mednafen.md`).

## 2026-10-26 — OPT-001 / EXP-0075: boss fight unlocked from the start

- **Found:** the title menu forces MECH-GOUKI NOW!! (index 5) back to SURVIVAL
  MODE while the word at `0x06017AB0` is 0 (`0x0603D644`); the word is cleared
  at boot (`0x0601DBE4`) and set by `0x06098A1A` from saved data.
- **Controlled test:** one `MM.BIN` byte (`0x50E5`, `00` → `01`): the flag reads
  1 from frame 2,464 to 7,264; the control image reads 0.
- **Play (user):** from a cold boot, CYBER-AKUMA NOW!! via L/R (keyboard P in
  this configuration) on the Survival row; the boss fight against Cyber Akuma
  runs.
- **Build option:** `--unlock-boss-fight` (default on), `UNLOCK_BOSS_PATCH`.
  `end010`, `m8_roster`, `m8_roster_credits` pass `--no-unlock-boss-fight`.
  Release references rebaselined: `m8_roster_gold` track 01 `f5b98b46…`
  (patch `778fda81…`), `m8_roster_gold_us` `3a32e364…` (patch `fb32c9b3…`).
  All nine references pass.

## 2026-10-26 — LOC-007 / EXP-0076: secret-character names compared

- **Read:** the Saturn speaker table, banner/VS name tables and life-bar
  labels; searched every file of the Saturn, `mshvsfu`, `mshvsfj` and the PS1
  US in ASCII and arcade codes.
- **Result:** the Saturn's secret-character names equal the US arcade's
  (ZANGIEF, SAKURA, SHADOW, U.S.AGENT, MEPHISTO, SPIDER-MAN), and both arcade
  regions share the table. Only the PS1 executable's own lists use
  MECH-ZANGIEF, DARK SAKURA, ARMORED SPIDER-MAN. No build change.
- **Disproven:** the hypothesis that a secret character's name differs
  between the JP and US releases (in the game data).
- **Not productive:** the first PS1 pass read no files (the reader needs the
  `;1` version suffix); a byte/word/long search for a slot → name-ID map.
- **Unattended runs are silent now** (user request): `local/mednafen_quiet`.

## 2026-10-26 — SPECIAL-003 / EXP-0077: secret characters' text sources

- **Win quotes:** arcade English slots 20/21/25 = Zangief/Sakura/Spider-Man;
  22-24 have their own blocks. The Saturn's `MC14`/`MC15` Japanese is unique.
- **Disproven:** `EXP-0032`'s PS1-only English blocks: they are copies of the
  Zangief and Sakura blocks.
- **Endings:** Japanese pages unique for 20-22 (5, 3, 6) and shared for 23-25;
  English slots 19-25 share a generic two-record ending. English partner
  lines exist for every secret slot.
- **Next:** the user chooses the route for slots without their own official
  English.

## 2026-10-26 — SPECIAL-003 / EXP-0078: secret characters' text built

- **User decision:** new translations for Metal Zangief's and Dark Sakura's
  win quotes and every secret ending page; official English elsewhere.
- **Built:** `--secret-roster` (slots 22-24, official) and
  `--secret-translations` (`data/translations/secret_characters.json`, 49
  records with source hashes; official partner lines and names for 20-25).
- **Found:** arcade digits (ASCII − 1 + `0x100`) and `0x0186` (opening quote);
  the slot 23-25 ending block is 6 records, the first three already English.
- **Not productive:** the first translations overflowed the font by 656
  bytes; choosing shifts against existing pairs and rewording three lines
  made it fit (12-16 bytes spare).
- **Release:** `m8_roster_gold` track 01 `45217d9d…` (patch `dfca0645…`),
  `m8_roster_gold_us` `de8b2e0d…` (patch `ad56c5bb…`); all nine references
  pass.
- **Next:** live check of a secret character's win quote and ending.
- **Live check prepared (2026-10-26):** secret-character select codes from the
  user's GameFAQs copy (hold Start on Blackheart, Hulk, Dhalsim, Vega, Omega
  Red, Spider-Man). `ending_driver --after-stage N` waits for N won stages
  before arming, so fight 1's win quote shows. First launch stopped by the
  user before a fight; the arm-after-a-win path is not yet exercised. Outside
  a fight the stage word holds unrelated values (`0004`, `5854`, `2c00`…).

## 2026-10-26 — SPECIAL-003 done: secret-character text seen in play

- User play (US release image): Metal Zangief's translated win quote, the
  official post-boss lines with Shadow, and his five translated ending pages,
  all in English (`EXP-0078`).
- **Not productive / fixed:** `ending_driver --after-stage` assumed the stage
  word `0x06NN`; this run used `0x04NN`. Restarted mid-fight, the KO test
  fired in an ordinary fight (where `0x060F3E50` is player 1's vitality) and
  knocked out the player. The driver now keeps the high byte and acts only on
  a fight that starts after arming.
- New backlog: `UI-004` (the CONTINUE? screen's Japanese hint box).

## 2026-10-26 — SPECIAL-002 / EXP-0079: Norimaro's text built

- **Built:** slot 17 joins `--secret-roster` (official win quotes, `MC11`
  `0xA158`, placeholders in records 1, 3, 9, 10, 15 dropped) and
  `SECRET_SLOTS` (official partner lines, name); his five ending pages
  (`ME.PAC` `0x3F5C`) are a new translation in
  `data/translations/secret_characters.json`.
- **Found:** the Saturn's slot 17 table equals the arcade Japanese slot 17;
  its English block is unique, identical in `mshvsfu`, `mshvsf`, `mshvsfj`,
  and on the PS1 (`SELECT.BIN` `0x12E0C`).
- **Not productive:** the build overflowed the font by 657 bytes. Fixed by
  `caption_compiler.retired_kanji` (spec flag `retire_replaced_kanji`, set by
  `--secret-translations`): 250 kanji used only by replaced records become
  sacrificial candidates; the US build uses 8.
- **Fixed:** `secret_tables` was called without the name variant, so the US
  build's ending said "Mech-Gouki"; it now gets `--names`.
- **Release:** `m8_roster_gold` track 01 `7859e93e…` (patch `fb8474ef…`),
  `m8_roster_gold_us` `4a24ab67…` (patch `fbc93fb7…`); all nine references
  pass; 536 pairs each, 22 and 71 bytes spare.
- **Next:** live check (Norimaro's win quote, post-boss lines, ending) on the
  user's command.

## 2026-10-26 — SPECIAL-002 done: Norimaro's text seen in play

- User play (US release image `4a24ab67…`, Norimaro with Shadow): his
  official win quote, the official post-boss lines and his five translated
  ending pages, all in English (`EXP-0079`).
- **Not productive / fixed:** the first launch's `ending_driver
  --after-stage 1` armed at boot on the stage word's first read, `0x0002`,
  and wrote `0x0007` for a few seconds. Stopped, run discarded, Mednafen
  restarted cold (config unchanged). The driver now arms only on a step from
  `0xHH(N-1)` to `0xHHN`; this run's step was `0x0300` → `0x0301`.
- **Next unblocked:** `UI-004` (the CONTINUE? hint box), backlog.

## 2026-10-26 — UI-004 / EXP-0080: CONTINUE? hints found and built

- **Found:** the hint is a 16-record quote-font table at `MM.BIN` `0x7C584`
  (glyph match of `EXP-0078`'s state `f00014068`, color word `0x6010`; one
  disc hit). Same Japanese table in all three arcade sets (`0x2139AC`); no
  English in the arcade or the PS1 US.
- **Not productive:** the `MM.BIN` dialogue table at `0x7CC86` (`TXT-001`)
  was the first candidate; it holds story lines, not hints.
- **Built:** `data/translations/continue_hints.json` (new English, source
  hashes), `official_endings --ui-translations`, `{XXXX}` kept-code cells in
  the compiler, pair punctuation `+ : ( )` in both glyph styles.
- **Not productive:** the first rebuild failed (no credits glyph for `+`); a
  `| head` pipe hid it from `set -e`. Fixed with `pipefail` and the credits
  codes.
- **Release:** `m8_roster_gold` track 01 `3ee38981…` (patch `abd03143…`),
  `m8_roster_gold_us` `103d40a5…` (patch `46832e4d…`); all nine references
  pass.
- **Next:** live check of a hint on the CONTINUE? screen, on the user's
  command.

## 2026-10-26 — UI-004 done: CONTINUE? hints seen in play

- User play (US release image `103d40a5…`): two lost fights showed two
  different English hints, one with the ↑ arrow glyph; each hint holds for
  its whole countdown (`EXP-0080`). Mednafen config unchanged.
- Not yet on screen: the `+ : ( )` glyphs.
- **Next unblocked:** none named in this session's requests; open unknowns
  remain in `docs/known_unknowns.md`.

## 2026-10-26 — Attract colour check (user report: Dan pink to purple)

- **Hypothesis:** the attract-caption recolour (`EXP-0071`) leaks into a
  character scene. **DISPROVEN.** Statically, every recoloured load is
  replaced by a full palette load inside its caption slot in all eight
  streams. Live, the original image itself shows Dan's still in a lavender
  gi for about a frame in the lightning montage (`EXP-0071` follow-up).
- **Not productive:** pixel diffs of frame-aligned captures (277 of 421
  frames differed); the original against itself differs in 75 of 138, from
  timing jitter. Novel-colour counts flagged mostly fades and flash colours.
- New tool: `tools/mednafen/frame_capture.py` (silent cold-boot frame
  capture), smoke-tested on frames 120-240.
- Local cleanup at the user's request: removed eight superseded experiment
  builds under `build/` and 2,227 rolling recorder save states not cited by
  any record (37 GB → 16 GB); cited states and all screenshots kept.

## 2026-10-26 — DOC-021: README usage section and change list

- Rewrote `README.md` as the project entry point (user request): change list,
  required inputs with exact filenames and hashes, set-up, build commands,
  build options, research inputs.
- **Corrected assumption:** building a patch needs `mshvsfu.zip` and
  `cps2.cpp` as well as the Saturn image (the official English is read from
  the arcade ROM at build time).
- **Fresh-clone check** (clone of `0134f26`, only the Saturn image and
  `mshvsfu.zip` linked in): `setup_venv.sh`, the `cps2.cpp` download,
  `reference_builds --only m8_roster_gold m8_roster_gold_us` (both pass),
  both `make_patch` runs (`abd03143…`, `46832e4d…`, identical to the record),
  and the custom `--no-unlock-boss-fight` example (spec differs only by the
  `MM.BIN` `0x50E4` patch; patch `d5e8a5b8…`, round trip true). Git status
  clean afterwards.

## 2026-10-26 — TXT-001, SPECIAL-004, tooling

- **TXT-001:** the story table is `MM.BIN` records 16-47 after the CONTINUE?
  hints (`0x7CA44`-`0x7D3C4`; the name table follows): one line per roster
  slot 0-25, Vega's orders to Shadow and Metal Zangief, punctuation, and
  developer jokes signed KAWASE. Draft English with source hashes in
  `data/translations/story_lines.json` (not built). The CONTINUE? code picks
  a hint with `and #0x0F` (`0x060AF328`) from pointer tables at `0x060AF392`
  and `0x060AF6AA`; the reader of records 16-47 is not found statically.
- **SPECIAL-004 (`EXP-0081`):** both bosses' tables equal the arcade
  Japanese, and both have their own official English; built.
- **Tools:** `ending_driver --stage N --no-ko`; `tools/mednafen/bp_log.py`
  (log-mode breakpoints while someone plays; smoke-tested, 60,405 PC hits
  logged without halting). Fixed: the hit cap now clears PC breakpoints too.
- **Release:** `m8_roster_gold` track 01 `00e15be7…`, `m8_roster_gold_us`
  `3d2a13d2…`; all nine references pass.

## 2026-10-26 — Play session: bosses, CONTINUE?, story-table reads

US build (track 01 `3d2a13d2…`), user at the controls; recorder
(`local/special004/play/rec`), `bp_log` on `06095544-06095EC3` plus PC
`060AF32C`, `ending_driver --after-stage 1 --stage 7 --no-ko`, then
`--after-stage 1` (details in `EXP-0081`).

- **Boss win quotes:** Mech-Gouki's and Apocalypse's official English seen
  as built. Apocalypse is the stage-7 boss.
- **New Japanese text:** Apocalypse's pre-fight exchanges with each hero are
  `MC00`'s three "unidentified" tables. The arcade has them byte for byte,
  and the US arcade has official English (from `0x222AFE`). Not yet built.
- **Mech-Gouki select code (GameFAQs, via the user):** not reproduced. Akuma
  could not be chosen a second time. Unconfirmed, not disproven (one try).
- **CONTINUE? hint:** record 6 seen as built (arrows and `+`). The index
  store at `0x060AF32C` logged `R0 = 6`, `GBR = 0x0601799C`.
- **Read logger:** the first run hit its 5,000-hit cap at frames 1003-1111,
  because boot code uses `0x06095xxx` before `MM.BIN` is loaded. Restarted
  at frame 2984, after checking that WRAM `0x06095544` matched `MM.BIN`
  `0x7CA44`. Afterwards it logged 10,067 hits. Only two kinds of code read
  the range:
  - `0x06010690`/`0x06010694`: the overlay save copy, which copies
    `0x06018B00`-`0x06100000` (and two more ranges, listed at `0x06010620`)
    to `0x02486BC0` at mode changes (frames 4515, 9120, 21442);
  - `0x06021F40`: code from the next overlay, once `MM.BIN` is gone.

  So the story table was not shown on any screen visited. Run it again
  later on Versus, options and the other modes.
- **Lesson:** start `bp_log` after boot (or ignore hits before the file is
  resident), and treat hits after an overlay change as reads of other data.

## 2026-10-26 — SPECIAL-004: Apocalypse's pre-fight exchanges (EXP-0082)

- **Layout:** `MC00.PAC` `0x3634`: 26 slots × 3 boxes (challenger, reply,
  closing). Equal to arcade Japanese `0x2164B8` in all three sets. The census
  tables `0x392E`/`0x3D7A`/`0x404E` were misaligned slices of this one block
  (do not reuse those boundaries).
- **English:** US arcade `0x2203F4`, 100-byte boxes, 300 per slot, 25-code
  lines. Note: `0x2203F8` (the first guess) is 2 codes late.
- **Built** with `official_endings --boss-exchanges` in both release
  references. Bison → Vega was added to the Saturn-name text overrides.
  `0x011E` (Wolverine's line, its only use) is drawn as a comma, inferred
  from the Spanish block (HYPOTHESIS). All nine references pass. Release:
  `m8_roster_gold` track 01 `e0395c3e…`, patch `f2fbadef…`;
  `m8_roster_gold_us` track 01 `963063de…`, patch `9cf26c3b…`.
- **Failed check:** replaying an old-build state on a font-changed image is
  not a font check. The Saturn-name replay drew US-build glyphs ("yp" as
  "Ap"), because the quote font stays in cart RAM from boot. This was
  already a known pitfall; it is recorded again because it is easy to miss.
- **Disproven route:** writing the build's font into cart RAM after loading
  a state. The agent's `physical` space does not reach cart RAM
  (`0x0278CF60` reads match neither font; writes do not stick).
- **Tests:** `pytest tests/unit` (new: exchange pairing and refusal; Bison
  → Vega).
- **Cold-boot play check (EXP-0082):** Saturn-name build `e0395c3e…`, Gouki
  as lead, driver to stage 7. All three boxes were correct English with
  "Gouki" (`local/special004/play2/rec`). The US build has not been
  cold-booted to this fight.
- **Gold pre-fight boxes (EXP-0082):** the box is message-window kind 3,
  whose palette immediate is at `MM.BIN` `0x9621D` (`0x96`). A RAM trial set
  it to `0x81` and the text turned gold; kind 5 (`0x060AEDA1`/`0x060AEDAF`)
  changed nothing. Built into `GOLD_PALETTE_PATCHES`; all nine references
  pass. Release: track 01 `0a6a08c1…` / `0da69726…`, patch `a0c72ed7…` /
  `05f3a90a…`.
- **Lesson:** `MM.BIN` is loaded only after Start is pressed, not during the
  attract demo, and replays restore it from cart RAM. An `MM.BIN` change
  cannot be read back without a play session.
- **US cold-boot play check (EXP-0082):** track 01 `0da69726…`, Akuma as
  lead, driver to stage 7. All three boxes were correct English, with
  "Akuma", in gold ((240,240,0)/(240,176,0)). Both name variants are now
  seen in play; EXP-0082 is CONFIRMED.

## 2026-10-27 — REL-003: smaller release patches (EXP-0083)

- **Breakdown:** the eight `MVSOP` streams were 2.83 MB of the 2.95 MB
  patch: re-compression noise (script ~130 KB, section C ~77 KB, stream
  blocks ~150 KB per file), while the decoded data barely changes.
- **Version 1 (splice, later bytes shift):** 932,677 bytes. The rest was
  shifted bytes and the EDC/ECC of every shifted sector.
- **Version 2 (exact-length runs):** 701,266 bytes; 618 changed sectors.
  One stretch needed far more bytes than the original, and only growing the
  run backward fixed it. A `_fit` that forced scattered groups was slow and
  spread changes over many sectors (avoid).
- **`-W 16777216`:** 642,747 / 644,202 bytes. Zipping adds only 4%.
- **Tooling fix:** unattended Mednafen stalled while the display slept
  (vsync). The silent home now sets `video.glvsync 0` and
  `video.blit_timesync 0`. `quiet_home` splits its settings on `\n` only,
  because `splitlines()` broke a line holding 0x85.
- **Check:** all nine references pass; cold-boot attract capture shows all
  three English captions. `pytest tests/unit` 277 passed; ruff and mypy
  clean.

## 2026-10-27 — REL-002: SSP patches (EXP-0084)

- **Evidence (user permission for each download and install):**
  - a v1.3-made sample `.ssp` (Doom fix patch v0.3, `98c9ffdc…`);
  - the bundled official patcher v1.95 (`9b739d18…`), decompiled with
    `ilspycmd` 11.2 from its single-file bundle, never run;
  - `saturn-patcher-egui` at `20837e06…`, built with cargo 1.99.1.
- **Format:** a ZIP of `NAME._DFR` (BSDIFF40) entries.
  - The official patcher needs `version.txt` and `driveOrder.txt`.
  - egui needs `changes.md5`.
  - `ip.bin` is optional and would replace the system area, so it is left
    out.
- **Mismatch in the open applier:** egui looks up `changes.md5` by exact
  name, so it would not load the v1.3 sample, which has `CHANGES._MD5`.
  v1.95 writes the lower-case name.
- **Disproven:** one whole-file add per `._DFR` is valid but large (1.58 MB
  in total; MEMFIX.PAC alone 191 KB). Data moved inside the files needs
  real matching. A pure-Python bsdiff 4 scan with an 8-byte index gives
  560,868 / 560,981 bytes, smaller than the xdelta patches.
- **Checks:**
  - egui applied each `.ssp` to the untouched track 01 and gave the release
    hashes (`e820f6e1…`, `a6572495…`);
  - `/usr/bin/bspatch` reproduced 34 of 34 files per variant;
  - `make_ssp` round-trips and is deterministic.
- **Layout note:** the original files are packed back to back from LSN 30.
  The official patcher's rebuilt image is untested.
- **Tests:**
  - `pytest tests/unit`: 288 passed (11 new in `test_make_ssp.py`);
  - ruff is clean;
  - mypy reports one error, which predates this work:
    `tests/unit/test_official_endings.py:185`, `SLOTS` is not exported
    (from `6198fc5`).

## 2026-10-27 — REL-002 follow-up: the official patcher's code on macOS (EXP-0084)

- **Setup (user request):** the v1.95 core libraries target plain .NET 5,
  so a .NET 10 console harness can load them. They were taken unmodified
  from the bundle.
- **Test A, unmodified code:** its `SSP` class and DeltaQ bsdiff apply all
  34 `._DFR` patches exactly in both variants. The patch is valid (v1.3),
  `ContainsContent` is true, and 414 drive-order entries are read.
- **macOS-only failures:**
  - the command line (`BuildDisc.Parse`) treats `/` paths as switches, and
    otherwise spun for over ten minutes;
  - `BuildDisc` strips work-folder prefixes with `folder + "\\"`, so on
    macOS no patch was applied (`MM.BIN` unchanged) and the build spun.
- **The fix:** changing the core's single `"\\"` string-heap entry to `"/"`
  (one byte) fixed both. The rebuild then takes 7 s.
- **Test B results:**
  - every file stays at its original LSN with the release contents;
  - only LSN 16 differs (volume space size 216,839 → 218,484), also in the
    no-patch control;
  - the audio tracks are re-laid (about 146 extra lead sectors; track 03's
    pregap 2:00);
  - Mednafen cold boot of both rebuilds: CAPCOM logo, English attract
    captions, demo fight, title screen.
- **Lesson:** the output CUE carries absolute paths on macOS (Windows keeps
  the bare names), and Mednafen refuses them (`filesys.untrusted_fip_check`).
  Rewrite them to bare names.
- **Tooling not installed:** installing `dotnet-stack` was refused by the
  permission check; the harness timed the build stages through reflection
  instead.

## 2026-10-27 — Commit identity rewrite (user request)

- **Rewrite:** every commit on `main` (181) now has author and committer
  `Colin <13876322+princeendo@users.noreply.github.com>` (GitHub account
  `princeendo`).
  - Before: `Colin White <colin.white@edoinc.com>` (180 commits) and one
    `Colin <haljordan@gmail.com>` (the GitHub-made Initial commit).
  - Done with `git filter-branch --env-filter`; the final tree is unchanged.
  - Force-pushed with the user's explicit approval (an exception to
    `AGENTS.md`'s no-force-push rule).
- **Hash references:** all commit hashes changed. The two quoted in this log
  were updated: `facc48e` → `6198fc5`, `8e2b649` → `0134f26`.

## 2026-10-27 — TXT-001: the story table is a rare post-loss win quote (EXP-0085)

- **Method:**
  - a new `logreads` verb in `tools/reference/mame_timeline.lua` (MAME read
    taps; the end address must be odd);
  - decrypted arcade code from the debugger's `saveo`;
  - MAME's `dasm` disassembles the decrypted opcodes, but the plain program
    dump does not show CPS-II immediates.
- **Runs:**
  - **Attract loop, 60,000 frames:** no read (besides a boot sweep).
  - **One lost game:** hint record 11 at CONTINUE?.
  - **26 CONTINUE? screens:** hints only.
- **Code:** the post-loss winner's line (`0x070336`, Saturn `0x060AF1F2`)
  shows story record 16 + the winner's slot. That needs the Japanese region
  and a 1-in-64 roll; otherwise it is a normal win quote.
- **Forced trials:**
  - arcade: Blackheart's record 24, and record 27 with `{P}` = Zangief, the
    winner's teammate;
  - Saturn US release: Apocalypse's record 16 in Japanese.
- **Disproven:**
  - `EXP-0047`'s pointer at `0x0B03BA` is a BCD constant (2,147,483,648);
  - `EXP-0080`'s "no official English hints": the arcade has 12 English
    hints at `0x2239FC`, and `mshvsfj` and `mshvsfu` are identical there.
- **New tasks:**
  - `TXT-002`: build the draft English for records 16-41;
  - `TXT-003`: the screens of records 39 and 42-47;
  - `UI-006`: decide on the official hints (user decision).
- **Not done:** the screens of records 39 and 42-44 were not seen. The rm in
  a first timeline command was refused by the safety check (an unguarded
  variable); the folder was new anyway.

## 2026-10-27 — UI-006: official English CONTINUE? hints, paged (EXP-0086)

- **User decisions:** use the arcade's official English hints; then
  "8 hints, exact, 2 pages".
- **Found:**
  - the US arcade shows each English hint as two pages (records 6 then 7,
    383 frames apart);
  - the Saturn kept the arcade's map and page step behind the region test
    `0xCC90`.
- **Tried and dropped:**
  - one page per hint does not fit: every hint needs three of the Saturn's
    38-character lines;
  - more records do not fit: every `0x9999` run in `MM.BIN`, including the
    208 bytes before the table, is overwritten in RAM during play, so it is
    work memory.
- **Built:**
  - `--official-hints`: arcade English pages 0-15 → records 0-15; `nop`s at
    `MM.BIN` `0x96848` and `0x9638C`; map `0x968A0` → 0..14 twice;
  - both references rebaselined; nine of nine pass;
  - xdelta 641,843 / 643,267 and `.ssp` 559,332 / 559,184 bytes; egui
    reproduces both tracks.
- **New tools:**
  - `tools/memory/mcs_patch.py` writes a region of a save state (here the
    font into cart RAM, which the agent cannot write);
  - `write_trial --shot-at` takes extra screenshots.
- **Verified:** all eight hints, both pages, forced from the `EXP-0081` play
  state with the built font. Not yet from a cold boot.
- **Tasks:** `UI-005` rejected (superseded). `continue_hints.json` is marked
  superseded and stays available.

## 2026-10-27 — TXT-002: post-loss story lines in English (EXP-0087)

- **Built:**
  - `--story-lines` builds `MM.BIN` records 16-41 from
    `story_lines.json`, with `placeholder: anywhere`; record 35 (symbols) is
    kept;
  - `centred` and `line_pairs` now accept `{P}` (two cells; the text after it
    starts a new cell);
  - nine of nine references pass;
  - xdelta 644,163 / 644,944 and `.ssp` 561,626 / 561,628 bytes; egui
    reproduces both tracks.
- **Verified:** forced on the Saturn from the `EXP-0081` state with the
  built font. The `bf` at `0x060AF228` became a `nop`, and the story base
  literal `0x060AF250` was moved per record. All 25 records show in English.
- **Lesson:** forcing Chun-Li's record onto Apocalypse inserted his own
  Japanese name (slot 0, untranslated). Copying Zangief's name entry over
  slot 0 in RAM showed "Oh? ZANGIEF, …". In real play the teammate is always
  a playable character.
- **Next:** one cold-boot play check for `UI-006` and `TXT-002` (user).

## 2026-10-27 — Cold-boot play check: hints and story lines (EXP-0086, EXP-0087)

- **Setup:**
  - US release `0f430c0a…`, user playing with a PS4 controller. The first
    launch had no controller; it was restarted.
  - Recorder `local/txt002/play2/rec`.
  - New `tools/mednafen/continue_driver.py`: forces the 1-in-64 branch and
    steps the hint map 0-7, one per CONTINUE? (log-mode PC breakpoint at
    `0x060AF352`).
- **Result:** eight losses to Blackheart and Zangief.
  - Every post-loss screen showed Blackheart's story line in English.
  - The CONTINUE? screens showed hints 0-7 in order, page 1 then page 2.
- **User report:** page 2 stays on the team screen after a continue. The US
  arcade does the same (MAME `mshvsfu`), so it is authentic. A Japanese-set
  comparison mistimed its inputs.
- **Speed:** fast-forward is fine during fights. The post-loss and CONTINUE?
  screens must play at normal speed, because the recorder takes one
  screenshot per real second.
- **User requests:**
  - `TXT-004` (opt-in `--fix-grammar` for clumsy official English, starting
    with hint 0);
  - no publishing until the open tasks are addressed.

## 2026-10-27 — TXT-003: screens of story records 39 and 42-47 (EXP-0088)

- **Arcade:**
  - the team words are at `0xFF48B0` (player then CPU, character × 2);
  - forcing the CPU team with `force16` showed Vega's order boxes for Shadow
    (42) and Metal Zangief (43), and Dark Sakura's dots (44);
  - the US set shows "I've finally tracked you / down!Now,you're mine!"
    instead;
  - the player's own secret team shows nothing (as on the Saturn in
    `EXP-0078`).
- **Saturn:** the same routine, called from the secret characters' `MC`
  files, with an extra flag `0x0601801C`. The team words mirror the arcade
  at `0x060F48B0`, and the phase byte is `0x060F4800`.
- **Disproven method:** writing the Saturn CPU team after the continue
  always crashed the load into the BIOS menu, with Dan and Sakura as well.
  The original team loaded normally. Earlier states stall on the mode select
  without input.
- **No readers:** records 45-47 have none; record 39's extra reader is an
  arcade-only scene.
- **Built (user decision: faithful translations):** records 42-43; renders
  on the Saturn; nine of nine references pass; patches remade.
- **Tooling note:** an MSHvSF character-select code (Dhalsim + Start, then a
  button) picked Dhalsim in MAME; the team was forced in RAM instead.

## 2026-10-27 — SPECIAL-004: the Mech-Gouki select code, static (EXP-0089)

- **The routine:** `0x06051CD4`, called from both pick confirms.
  - It maps six cursor characters to secret ones while Start is held.
  - For Gouki, it counts Start-held picks per player (`0x06017CEE`/`EF`).
    On the 2nd it gives Mech-Gouki, if `0x06017AB4` ≠ 0.
- **The unlock:** `0x06017AB4` is set by the end-of-mode routine
  (`0x060989F8`) only after the MECH-GOUKI NOW!! fight (mode flags
  `0x0601801C` = `FF`, `0x06018024` = `FF`).
  - A Survival clear (`FF`/`00`) sets `0x06017AB0`, the boss-fight unlock.
  - Arcade/Versus (`00`) sets `0x06017AA8`.
- **Correction:** `EXP-0075`'s "saved-data bytes" are mode flags set at game
  start.
- **Tooling note:** misreading SH-2 `tst`/`bt` (T = 1 when zero) first gave
  the wrong mode-to-unlock table; corrected before writing it down.
- **New tool:** `tools/mednafen/mechgouki_driver.py` (logs the words;
  optional boss KO in that mode, or forcing `0x06017AB4`). The play test is
  pending.

## 2026-10-27 — DOC-020: playbook brought up to date for the XvSF repository

- **Goal:** update `docs/playbook_cross_game.md` before the XvSF repository
  (`princeendo/xmen_vs_sf_saturn_en_translation`) is set up from it.
- **Method:** a read-only review of the 61 commits from `db193ba` to
  `4289061` (`EXP-0051` to `EXP-0088`): `research_log.md`, `TASKS.md`,
  discoveries, policy files, and experiment records.
- **Added:** Phase 6 (special cases, unlocks, UI art, caption colour,
  attract captions, CONTINUE? hints, rare and region-gated text, names and
  voice); new design-decision rows; user decisions 2026-10-25 to 2026-10-27;
  new tool rows; 12 emulator limits; 13 pitfalls; checklist items 20-25.
- **Corrected:** the PS1 "extra" English blocks are copies (`EXP-0077`); the
  xdelta flags and patch size (`REL-003`); the release policy (rule 21
  exception, SSP); the names policy (two variants); capacity (536 pairs,
  retired kanji); the M9 status.
- **Checked against the sources before writing:** the SSP size history
  (`EXP-0084`: whole-file adds made 1,577,860 bytes) and the attract pairing
  method (`EXP-0067`: by sequence position, not frame number). Both first
  drafts were wrong and were fixed.
- **XvSF intake (recorded in the playbook):** the user supplied
  `X-Men vs. Street Fighter (Japan) (3M).7z` (Redump-style BIN/CUE, 42
  files). It was hashed in the XvSF repository; Track 01's user data equals
  the old ISO rip's. The user states XvSF needs the 4 MB cart (2026-10-27).
- **Not covered:** `EXP-0089`, committed by another session during this work.

## 2026-10-27 — SPECIAL-004: Mech-Gouki play test and his post-boss line

- **Play test** (`EXP-0089`; US release image `39ae78b3…`; user at the
  controls; `mechgouki_driver --ko-boss`; recorder `local/sp004/play/rec`):
  - a MECH-GOUKI NOW!! clear set `0x06017AB4` = 1 (frame 11,283);
  - **disproven:** the static prediction that `0x06017AB4` alone is enough.
    With `0x06017AA8` = 0, three Arcade attempts each counted one Gouki
    pick, and the partner cursor skipped Gouki;
  - with `0x06017AA8` forced to 1, holding Start and picking Gouki twice
    gave Mech-Gouki alone (frame 45,253);
  - with it reset to 0, the Mech-Gouki Arcade clear set it again on its own
    (frame 72,468);
  - stage 8 was a Mech-Gouki mirror. The post-boss scene showed dots and
    one Japanese line (`MC13` record 107, 作られし者よ・・・). The ending
    pages were the disc's generic English, not Dan's.
- **Translation:** record 107 became "You who were created..." (new, faithful;
  `data/translations/secret_characters.json`). The US arcade's slot-19
  partner lines are generic and do not correspond.
- **Commands and outcomes:**
  - the specs were regenerated with `official_endings`;
  - `bash local/sp004/rebaseline.sh` (`reference_builds --write-baseline`,
    then the report, `make_patch` and `make_ssp`): nine of nine references
    pass, and both patch formats round-trip;
  - `bash research/experiments/EXP-0089/verify_dialogue.sh`: box 4 shows the
    English (`c020f16e…`).
- **Tooling note:** the recorder keeps only 60 states, so no state from
  before the dialogue survived. The trial used `EXP-0039`'s Ryu checkpoint
  instead.
- **Next:** the remaining open tasks before any release (TXT-004, DBG-002,
  DBG-004, RE-048-050, REF-012, LOC-001, LOC-006, SPECIAL-001).

## 2026-10-27 — DBG-002 and DBG-004 closed as not needed

- **Decision:** both `REJECTED`. `EXP-0010` deferred states B (after the KO,
  before the caption) and D (after the caption) until the C-set comparison
  failed. It did not fail: `EXP-0013` searched the C1/C2/C2b states for the
  candidates, and `RE-012` confirmed the WRAM-L table by mutation (M1).
- **No experiment run:** this is a task-status change only.

## 2026-10-27 — REF-012: arcade win-quote fonts by region (EXP-0090)

- **MAME 0.289,** `mshvsfu` and `mshvsfj`, with no play:
  - two coins, Start, Button 1 twice;
  - vitality forced to 0 from frame 5,600 to 7,800 KOs the player;
  - the CPU's quote is at 10,260 (US) and 10,800 (JP), deterministic over
    two runs.
- **Dumps:** VRAM, object RAM, and the new `share` verb for `:cps_a_regs`
  (the CPS-A registers read back as 0 through the program space; a
  `logwrites` on them over three frames caught nothing).
- **Found:**
  - one shared glyph set, sprite tile = `0x15000` + text code;
  - US narrow Latin glyphs 12 pixels apart (25 a line), Japanese kana and
    kanji 16 apart (19);
  - the Saturn quote font holds the same glyphs at the same codes (pen + 1);
  - a Saturn forced record of arcade codes draws them 16 apart.
- **Disproven:**
  - the user's "different font" as different tile data. It is a different
    code range and pitch;
  - `EXP-0078`'s digit base `0x12F`. The arcade shows `0x138` as "8"
    (forced slot-22 quote, `0xFF9E4A`/`0xFF9E66` taps), and the Saturn shows
    `0x12F`-`0x132` as ")012". The release text "Level 3" and "9 am" is
    wrong; `TXT-005` fixes it.
- **Tooling:**
  - new `tools/reference/cps2_gfx.py` (rebuild, unshuffle, render);
  - `mame_timeline.lua` `share` verb;
  - a `region` verb was tried and dropped, because MAME regions have no
    `read_range` in Lua and the zip rebuild is enough.
- **Not done:** the EU set's pitch, and the pitch rule in either program.

## 2026-10-27 — TXT-005: digit codes fixed in the release (EXP-0091)

- **Change:** `tools/reference/cps2_text.py` `DIGIT_BASE` `0x012F` → `0x0130`,
  with its test updated.
- **Commands and outcomes:**
  - `bash local/txt005/gen.sh` before the change reproduced both reference
    specs byte for byte (`a824a86e…`, `d79c2fce…`);
  - after the change, each spec differs in exactly three lines: "before 9
    am..." ×2 → "8", and "When Level 3 or higher," → "2";
  - `bash local/txt005/rebaseline.sh`: both references rebaselined, nine of
    nine pass, and both patch formats round-trip. New track 01 `ceeca6ab…`
    (Saturn names) and `a1bf1809…` (American names);
  - `bash research/experiments/EXP-0091/verify_digits.sh`: hint 2 shows
    "When Level 2 or higher," and box 4 shows "before 8 am...".
- **Errata:** added to `EXP-0078` and `EXP-0086`.

## 2026-10-27 — RE-048: descenders in the credits pair glyphs (EXP-0092)

- **Observation:**
  - the release's credits font has no descenders (lower case ends on row
    11);
  - "Keep your guard up, puppy" read like "Kee0 vour 9uard u0";
  - the arcade's narrow font (`EXP-0090`) has real descenders, but adopting
    it is a user decision, so it was not used here.
- **Change:** `tools/text/credits_font.py` `OVERRIDES` gains g, j, p, q and y,
  drawn into rows 12-14.
- **Commands and outcomes:**
  - offline: 496 distinct release lines with those letters were rendered in
    16 sheets, and all were read;
  - `bash local/re048/rebaseline.sh`: `m8_roster_credits`, `m8_roster_gold`
    and `m8_roster_gold_us` were rebaselined, nine of nine pass, and both
    patch formats round-trip;
  - `bash research/experiments/EXP-0092/verify_descenders.sh`: two built
    records show the descenders on the Saturn.
- **For the user:** the letter shapes are a design choice and can be redrawn.

## 2026-10-27 — TXT-004: opt-in grammar fixes (EXP-0093)

- **Change:**
  - `--fix-grammar data/translations/grammar_fixes.json` (needs
    `--official-hints`) replaces five official hint pages (0, 1, 4, 8, 12);
  - each fix names the official page by the SHA-256 of its decoded lines.
- **Commands and outcomes:**
  - `bash local/txt004/gen.sh`: each spec differs from the release spec in
    the eight corrected lines and the flag field only;
  - specs `1fde4bf1…` (Saturn names) and `4dd19378…` (American names);
  - both images built (track 01 `99067ff4…` / `a47d2ba8…`);
  - `bash research/experiments/EXP-0093/verify_grammar.sh`: hints 0, 2, 4
    and 6 show the corrected pages on the Saturn.
- **Review:** all 405 distinct built records were read. Candidate fixes
  outside the hints (typos such as "mediate" and "it's appeal", missing
  commas) are listed in `EXP-0093` for the user; none are applied.
- **Default unchanged:** no release reference uses the flag.

## 2026-10-27 — Lead: the Saturn quote routine keeps the arcade's English layout switch

- **Static reading** of WRAM-H (`EXP-0089` checkpoint) at `0x060AF6E0`-`0x060AF79E`
  (translated 68000 code). The routine switches on the words at r11 −
  `0x3372` and − `0x3370` (`0x060F4C8E`, `0x060F4C90`):
  - record size 76 → 100;
  - line length 38 → 50 cells;
  - pitch 16 → 12.

  The arcade's language word is at −`$3370` (`EXP-0031`). Both words read 0.
- **One trial:** `0x060F4C90` = 1 on the box-4 checkpoint left the post-boss
  box empty (`local/ref012/saturn/lang_f1100.png` `ad93c8ee…`). This says
  nothing about pitch.
- **Status:** HYPOTHESIS. The test still needed is a state just before a win
  quote. If it holds, the Saturn could draw the arcade's narrow font 12 px
  apart without a code patch (`REF-012` option 3).
- **RE-049 side note:** r12 in this routine is the running task object.
  `0x060F9E16`/`0x060F9ED6` may be pool slots, a fourth candidate besides
  side, match number and team state.

## 2026-10-27 — RE-049 play session and the language word (EXP-0094)

- **Play:** the user, US release image `0c3f72bb…`, won stage 1 and lost
  stage 2. Recorder `local/re049/play/rec`; pc log at `060AF724`.
  - r12 `9E16` for the user's KO, `9ED6` for the CPU's KO, and `9A56` for the
    hint pages.
- **Pool:**
  - the win scene's tasks sit one slot higher when slot `9ED6` is free;
  - after the user's KO, a task with code `0605F964` held `9ED6`.
- **Disproven:**
  - the winning side alone and the match number alone (with `EXP-0036`);
  - setting the language word at `0x060F4C90` before a quote. The game drops
    to the BIOS, so it is not a 12-pixel switch.
- **Invalid trials:** zeroing slot `9ED6` crashed the game, and copying a
  task into an empty pool before the scene starts was wiped by the scene's
  pool clear.
- **Open:** what the `9ED6` task is. RE-049 stays `BACKLOG`.
- **Addendum:**
  - `EXP-0036`'s quote-time states fit the rule: Cyclops had a type-`0x00FF`
    task in `9ED6` (quote in `9E16`), and the other three had none;
  - in this session the task appeared with Ryu's sprite over the title logo,
    linked to the character object `0x060F3800`;
  - the CPU's win showed its sprite on black, with no tally or logo.

## 2026-10-27 — LOC-006 groundwork: what a name switch must swap (EXP-0095)

- **Release-image census:** the font (`MEMFIX.PAC` entry 4) differs in 58,369
  bytes. Everything else totals about 490 bytes: the name-call table, `MM.BIN`,
  `ME.PAC`, `MC00`, `MC14` and `MC0F`.
- **Cart RAM:** across 213 recorder states, the largest block zero in all of
  them is 190,208 bytes at `0x0259EB00`. A second font (206,656 bytes) does
  not fit there (HYPOTHESIS).
- **Next:** a short session at the Options menu for the menu and storage
  questions. Nothing implemented.

## 2026-10-28 — User decisions; arcade glyphs adopted; Options table; KO session (EXP-0096 to EXP-0098)

- **User decisions:**
  - `RE-048`'s descenders and `TXT-004`'s hint wording are kept;
  - `--fix-grammar` also fixes typos and missing commas elsewhere, and stays
    opt-in;
  - American names, voices and art are the default (`LOC-001` done);
  - the release uses the arcade's narrow glyphs (`REF-012`);
  - two play sessions.
- **`EXP-0096`:**
  - new `--glyph-style arcade`; both release references are rebaselined
    (nine of nine pass);
  - new track 01: `bf36e4cb…` (Saturn names), `b9372a58…` (American names);
  - patches `c3161c1e…` / `376f85bf…`; `.ssp` `d370a32f…` / `66d5909e…`.
  - Found: code `0x122` draws "!?", not "‼". The decoder note is corrected.
  - Pitfall: `reference_builds --write-baseline` refuses a changed spec. The
    new spec must be adopted, with its hash, first (as `TXT-005` did).
- **`EXP-0097` (Options session):**
  - the settings table is at `0x06017AA0`, with its backup-RAM copy at
    `.bkr` `0x19F`;
  - the menu text is in `MM.BIN` `0x5C9F`, with a hidden COMBO GAGE row;
  - "CHOUHATU" on the button-config screen is untranslated.
  - Disproven approach: searching for bytes that step by one over the whole
    session found nothing, because the same bytes change at boot. Comparing
    steady windows before and after worked.
- **`EXP-0098` (KO session, arcade-glyph US image):**
  - Bison and Akuma pass all 16 records;
  - the `RE-049` slot rule holds for ten of ten quotes, and the winner
    pattern is a new HYPOTHESIS;
  - `verify_records.py` now skips raw tables;
  - its `screen_ok` cannot see gold text, so the boxes were read instead.
- **`EXP-0093` addendum:** 21 line fixes (32 record lines), with two shown on
  the Saturn.

Checks: pytest (298 passed, 1 skipped), ruff check, and strict mypy (74
files) pass. `ruff format --check` reports only `EXP-0070/README.md`, which
predates this session and was not touched.

## 2026-10-28 — UI-007: "CHOUHATU" reads "TAUNT" (EXP-0099)

- **User request:** translate the button-config screen's romanised
  "CHOUHATU".
- **Fields:** `MM.BIN` holds it in four 9-byte fields (`0x69EE`, `0x6A42`,
  `0x6ACE`, `0x6B22`). `--ui-english` now patches each to "  TAUNT  ".
- **Pitfall:** writing the text into RAM on an already-drawn screen shows
  nothing. Changing the L-button value (`0x06017AE0`) forces a redraw.
- **Rebuilt:** both references (nine of nine pass), with new patches. Track
  01: `cdf366b3…` (Saturn names), `c6f1fbd0…` (American names).

Checks: pytest (299 passed, 1 skipped), ruff check and strict mypy (74 files) pass. `ruff format --check` flags only the untouched `EXP-0070/README.md`.
