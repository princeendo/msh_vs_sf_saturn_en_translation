# MSHvSF Saturn English Localization Research

This repository is a reproducible, agent-assisted reverse-engineering environment
for localizing the Japanese Sega Saturn release of **Marvel Super Heroes vs.
Street Fighter** (MSHvSF) into English.

The current objective is intentionally narrow: prove that one Ryu post-fight
caption can be identified and changed in live Saturn RAM (M1), then reproduce the
same change from an untouched source disc image (M2). The project is currently at
**M0: research environment bootstrap**. See [TASKS.md](TASKS.md) for the active gate.

## Scope

- Target: MSHvSF, Japanese Sega Saturn release.
- Primary text reference: official English arcade/CPS-II release.
- Secondary text reference: English PlayStation release.
- Technical reference when a specific experiment warrants it: Japanese Saturn
  release of X-Men vs. Street Fighter (XvSF).
- First subject: Ryu post-fight captions.
- Later work: ordinary-character captions, then endings, then special cases.

This phase does not cover broad menus, graphics, gameplay text, FMV subtitles,
endings, Norimaro, or custom emulator development. XvSF is never a modification
target, and similarities between releases are hypotheses until tested.

## Prerequisites

- macOS or another host capable of running a suitable Mednafen build
- [uv](https://docs.astral.sh/uv/)
- Python 3.12 or newer, installed or managed by uv
- A legally obtained Saturn BIOS and MSHvSF Saturn JP image
- A fightpad suitable for capturing deterministic checkpoints

No game image, BIOS, extracted game data, or emulator binary is distributed here.

## Python Setup

Create or update the locked development environment:

```bash
./setup_venv.sh
```

Run every Python command without manually activating a virtual environment:

```bash
./invenv.sh python --version
./invenv.sh pytest
./invenv.sh ruff check .
./invenv.sh mypy tools tests
```

Record a source image's identity before research:

```bash
./invenv.sh python -m tools.disc.hash_source \
  --description "MSHvSF Saturn JP, local source" \
  --json /path/to/source-image.cue
```

Record every file belonging to a multi-file image. Store only the resulting
metadata in version control, never the source files themselves.

## Local Data

Keep original images outside the repository or under an ignored path such as
`local/disc_images/`. Treat originals as immutable. Put generated images only in
`build/`. Project-local Mednafen runtime configuration belongs in ignored
`local/mednafen/`; provenance and reusable configuration guidance belong in
`docs/mednafen.md` and `vendor/mednafen/README.md`.

Research artifacts are separated by purpose:

- `research/experiments/`: one directory per controlled experiment
- `research/screenshots/`, `savestates/`, `memory_dumps/`, and `traces/`: ignored
  binary evidence, with tracked metadata where appropriate
- `data/translations/`: structured, evidence-backed text correspondences
- `docs/discoveries.md`: confirmed durable findings only
- `docs/known_unknowns.md`: unresolved questions
- `research_log.md`: chronological successes and failures

## Mednafen

Stock Mednafen must be selected, built, configured, and evaluated before any fork
or debugger interface is considered. Booting the game, 4 MB RAM cartridge,
fightpad input, screenshots, save states, and interactive debugger access are M0
acceptance requirements. Follow [docs/mednafen.md](docs/mednafen.md).

## Project Guides

- [AGENTS.md](AGENTS.md): authoritative operating rules
- [TASKS.md](TASKS.md): dependency-controlled research plan
- [research_log.md](research_log.md): chronological journal
- [docs/project_scope.md](docs/project_scope.md): milestone gates and non-goals
- [docs/research_protocol.md](docs/research_protocol.md): experiment protocol
- [docs/architecture.md](docs/architecture.md): repository architecture
- [docs/references.md](docs/references.md): source bibliography and evidence rules
