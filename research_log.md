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
