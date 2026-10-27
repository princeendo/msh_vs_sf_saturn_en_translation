# Marvel Super Heroes vs. Street Fighter (Saturn): English Translation

This repository builds an English patch for the Japanese Sega Saturn release of
**Marvel Super Heroes vs. Street Fighter** (MSHvSF). Wherever an official
English text exists, the patch uses it: the arcade release's English, which
the US PlayStation release matches. Where none exists, it uses a new
translation, marked as such.

The repository holds the tools, the translation data, and the expected hashes.
It holds no game data: you build the patch yourself from your own disc image
(see [Build the Patch](#build-the-patch)). How the work was done is recorded in
[TASKS.md](TASKS.md), [research_log.md](research_log.md), and
`research/experiments/`.

## What's Changed

- **Win quotes in English:** every win quote of the 17 regular characters, in
  the US arcade's official English.
- **Endings in English:** each regular character's ending pages and the
  post-boss partner dialogue, in the US arcade's official English, with
  English character names.
- **New lettering:** the Japanese white font is replaced by the game's own
  staff-credits letters, two letters to a cell, in the credits' gold. This is
  the Saturn's own art, not the US arcade font.
- **Attract mode:** the Japanese teaser captions are replaced by the US
  arcade's three English captions (LEGENDARY / HEROES / UNITE AGAIN!!,
  AMAZING / TEAM BATTLES!, NEW HEROES / JOIN / THE FIGHT!!), in the game's
  own win-banner letters and colours.
- **Secret characters and Norimaro:**
  - official English where it exists: the win quotes of Shadow, U.S. Agent,
    Mephisto and Norimaro, and every post-boss partner line;
  - new translations where the US release has none: Metal Zangief's and Dark
    Sakura's own win quotes (the US release reuses Zangief's and Sakura's),
    and every secret character's and Norimaro's ending pages.
- **Bosses:** Apocalypse's and Mech-Gouki's win quotes (shown when they beat
  you), and Apocalypse's exchange with each challenger before his stage-7
  fight, in the arcade's official English.
- **Rare post-loss lines:** about once in 64 losses to the computer, the
  winner says a special line instead of its win quote. These exist only in
  Japanese (the arcade shows them only in Japan), so they are a new English
  translation.
- **CONTINUE? hints:** the gameplay hint under the countdown is the arcade's
  official English, shown in two pages as in the US arcade. The box fits 8
  of the arcade's 12 hints; the game's own joystick arrows are kept.
- **English UI labels:** the player-2 prompt shows the game's own "JOIN IN" art
  instead of 対戦者求む!, and the mode panel's 簡単操作 reads "EASY".
- **Boss fight unlocked:** MECH-GOUKI NOW!! (CYBER-AKUMA NOW!! with American
  names) is in the title menu from the start, without a Survival clear: on
  the SURVIVAL MODE row, press L or R, then Start. Optional; see
  [Build Options](#build-options).
- **Names:** two variants.
  - **Saturn names** (default): Vega, Gouki and Mech-Gouki, which match the
    Saturn's own art and voice.
  - **American names**: Bison, Akuma and Cyber Akuma in the text, life bars,
    win banners, VS screen, sound test, and the announcer's calls (using
    recordings already on the disc).

**Not changed:** the menus, the voices,
the attract-mode Norimaro screen, and every other screen not listed above.

Only track 01 of the disc changes; tracks 02-12 (audio) and the CUE sheet stay
as they are. The full list, with evidence for each item, is in
[release/README.md](release/README.md#what-the-patch-changes).

## Patch Files

You build the patches yourself (the next section); this repository never
distributes them. Each name variant comes in two formats, which give the same
patched track 01:

| xdelta file | Sega Saturn Patcher file | Variant | Patched track 01 SHA-256 |
| --- | --- | --- | --- |
| `mshvsf_saturn_en_m8_gold.Track01.xdelta` | `mshvsf_saturn_en_m8_gold.ssp` | Saturn names (recommended) | `de8861da75ba78f3d89f11dbdd3bb5507c6e5ae9819d16c62a0c3a3bd08edadc` |
| `mshvsf_saturn_en_m8_gold_us.Track01.xdelta` | `mshvsf_saturn_en_m8_gold_us.ssp` | American names | `39ae78b3d848df753bf8a981778b0b56712201c0832149249e45d331b58d010e` |

The `.ssp` hash holds when an in-place applier such as
[saturn-patcher-egui](https://github.com/ralfguth/saturn-patcher-egui) applies
it. The official Sega Saturn Patcher rebuilds the disc, so its track 01
differs in one field, the disc length. Every game file still comes out at
its original place with the same contents (`EXP-0084`).

### Applying a Patch

These patch files cannot be applied by anything in this repository; use one
of the tools below. Either way, patch an untouched copy of the image, never
one already patched. The project tests the result in Mednafen with the 4 MB
RAM cartridge.

| Tool | Patch file | Platforms | Tested here | How-to |
| --- | --- | --- | --- | --- |
| [xdelta3](https://github.com/jmacd/xdelta) (command line) | `.xdelta` | macOS (`brew install xdelta`), Linux, Windows ([releases](https://github.com/jmacd/xdelta-gpl/releases)) | yes, 3.2.2 | the command below |
| [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) | `.xdelta` | any web browser; nothing to install | no | choose the track 01 `.bin` as the ROM file, the patch as the patch file, then "Apply patch" ([source and help](https://github.com/marcrobledo/RomPatcher.js)) |
| [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher) | `.xdelta` | Windows, macOS, Linux ([releases](https://github.com/marco-calautti/DeltaPatcher/releases)) | no | choose the track 01 `.bin` as the original file, the patch as the xdelta patch, then "Apply patch" |
| [saturn-patcher-egui](https://github.com/ralfguth/saturn-patcher-egui) | `.ssp` | Windows, Linux ([releases](https://github.com/ralfguth/saturn-patcher-egui/releases)); macOS by building from source | yes, commit `20837e0` | `saturn-patcher PATCH.ssp "Track 01 copy.bin"` patches the copy in place ([README](https://github.com/ralfguth/saturn-patcher-egui#usage)) |
| [Sega Saturn Patcher](https://segaxtreme.net/resources/sega-saturn-patcher.73/) (Knight0fDragon) | `.ssp` | Windows; needs the [.NET 5 Desktop Runtime](https://dotnet.microsoft.com/download/dotnet/5.0) | its code on macOS, not the Windows program | "Select Saturn Game" → "CD Image" (the `.cue`), "+ Game Patch (SSP)", then "Patch Image"; it writes a new image |

With xdelta3:

```bash
xdelta3 -d -s "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
  mshvsf_saturn_en_m8_gold.Track01.xdelta "Track 01 patched.bin"
```

**After any of the xdelta tools or saturn-patcher-egui:**
1. Check the patched track's SHA-256 against the table above.
2. Put it in place of track 01 under its original filename.
3. Keep tracks 02-12 and the CUE as they are.

Sega Saturn Patcher instead writes a complete new image (CUE and tracks):
load that.

The full steps, hashes, and what each patch changes are in
[release/README.md](release/README.md#apply-the-patch).

## Build the Patch

### Files You Need

None of these are in the repository. Put them at these paths (all ignored by
git):

| File | Where it goes | What it is |
| --- | --- | --- |
| `Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin` to `… (Track 12).bin` and `Marvel Super Heroes vs. Street Fighter (Japan).cue` | `local/disc_images/mshvsf_saturn_jp/` | The Japanese Saturn disc as BIN/CUE: the data track, 11 audio tracks, and the CUE sheet. Every file must match the SHA-256 values in [references/mshvsf/saturn_jp/README.md](references/mshvsf/saturn_jp/README.md); track 01 is `8274307f…14f9` (452,397,792 bytes). |
| `mshvsfu.zip` | `local/arcade_roms/mshvsf/` | The MAME arcade ROM set `mshvsfu` (USA 970827). The official English is read from it at build time. The zip used: SHA-256 `32f4cb993a55eeff1397b24df5e9b2f14dd5baf6955a6fd69c77a49327794eee`; per-file ROM identities in [references/mshvsf/arcade/README.md](references/mshvsf/arcade/README.md). |
| `cps2.cpp` | `local/mame_src/` | MAME's public CPS-II driver source at commit `f34f02505e32c1993c6a782b6814232cbfc74e36` (SHA-256 `a8c09ef8…1602`). It describes the arcade ROM layout. Downloaded by a command below. |

### Set Up

- [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer (uv can install
  Python).
- xdelta3. The recorded patches were made with 3.2.2 (`brew install xdelta`
  on macOS); another version may give a different patch file, but the same
  patched track.

```bash
./setup_venv.sh
mkdir -p local/mame_src
curl -sSfLo local/mame_src/cps2.cpp https://raw.githubusercontent.com/mamedev/mame/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp
```

### Build the Release Patches

```bash
# 1. Build both release images from the untouched disc and check their hashes.
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp \
  --only m8_roster_gold m8_roster_gold_us

# 2. Make each patch from its image (checked against its reference).
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --out-dir build/release/m8_gold
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us

# 3. The same patches as Sega Saturn Patcher (.ssp) files (no extra tool needed).
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --release-version 0.1.0 \
  --description "Official arcade English text; Saturn character names." \
  --out-dir build/release/m8_gold
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --release-version 0.1.0 \
  --description "Official arcade English text; US character names." \
  --out-dir build/release/m8_gold_us
```

The patches are written to `build/release/m8_gold/` and
`build/release/m8_gold_us/`. Step 1 rebuilds each image twice and stops if any
hash differs from the recorded one. Leave out `--only …` to rebuild all nine
regression references. The full procedure, with expected hashes, is in
[release/README.md](release/README.md#rebuild-the-patch-from-this-repository).

### Build Options

The release images are built by the generator `tools.text.official_endings`
with the options below; [data/regression/reference_builds.json](data/regression/reference_builds.json)
lists each image's exact options.

| Option | What it does | Release images |
| --- | --- | --- |
| `--names saturn` / `--names us` | Saturn names (Vega, Gouki, Mech-Gouki) or American names (Bison, Akuma, Cyber Akuma) in every place listed under "Names" above. | `saturn` in `m8_roster_gold`, `us` in `m8_roster_gold_us` |
| `--unlock-boss-fight` / `--no-unlock-boss-fight` | Start with the title menu's boss fight unlocked (the default), or keep the original lock (a Survival clear). | unlocked |
| `--roster data/text/m5_roster.json` | The 17 regular characters: their endings and partner dialogue in English. | on |
| `--with-win-quotes` | Adds the regular characters' win quotes (needs `--roster`). | on |
| `--glyph-style credits` / `quote` | Letters from the staff-credits font (`credits`) or the original quote font (`quote`). | `credits` |
| `--caption-palette gold` / `silver` | Text colour: the credits' gold, or the original grey. | `gold` |
| `--ui-english` | The "JOIN IN" and "EASY" labels. | on |
| `--attract-captions` | The English attract-mode captions. | on |
| `--secret-roster data/text/secret_roster.json` | Official win quotes for Apocalypse, Mech-Gouki, Shadow, U.S. Agent, Mephisto and Norimaro. | on |
| `--secret-translations data/translations/secret_characters.json` | New translations for the secret characters and Norimaro, plus their official partner lines and names. | on |
| `--story-lines data/translations/story_lines.json` | The rare post-loss lines (`MM.BIN` records 16-41) and Vega's orders in two secret characters' intros (records 42-43), new translations. | on |
| `--official-hints` | The CONTINUE? hints in the arcade's official English, paged as in the arcade (8 of 12 hints fit). | on |
| `--ui-translations data/translations/continue_hints.json` | Earlier new translations of the 16 Japanese hints (`UI-004`), one page each. Cannot be combined with `--official-hints`. | off |
| `--boss-exchanges` | Apocalypse's pre-fight exchanges, from the arcade's official English. | on |

To build a variant of your own, such as the release image with the original
boss-fight lock:

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --glyph-style credits --caption-palette gold --ui-english \
  --attract-captions --secret-roster data/text/secret_roster.json \
  --secret-translations data/translations/secret_characters.json \
  --story-lines data/translations/story_lines.json --official-hints --boss-exchanges \
  --no-unlock-boss-fight --out local/custom/spec.json
./invenv.sh python -m tools.text.caption_compiler local/custom/spec.json --out-dir build/custom
./invenv.sh python -m tools.disc.make_patch --built-dir build/custom/image_a \
  --stem mshvsf_saturn_en_custom --out-dir build/release/custom
```

A custom image has no recorded reference, so `make_patch` runs without
`--reference`. Its other checks still run.

## Development

### Further Files for Research

Building the patch needs only the files above. The research tools also read
these, at these paths (all ignored by git):

| File | Where it goes | What it is |
| --- | --- | --- |
| `mshvsf.zip`, `mshvsfj.zip` | `local/arcade_roms/mshvsf/` | The MAME sets `mshvsf` (Europe 970625) and `mshvsfj` (Japan 970707). Used to check that Japanese and English text pairs the same way in every region. Identities in [references/mshvsf/arcade/README.md](references/mshvsf/arcade/README.md). |
| `Marvel Super Heroes vs. Street Fighter (USA).bin` and `.cue` | `local/disc_images/mshvsf_ps1_us/` | The US PlayStation release (SLUS-00793), the second English reference. Identity in [references/mshvsf/ps1_us/README.md](references/mshvsf/ps1_us/README.md). |
| `sega_101.bin` (and `mpr-17933.bin`) | `local/mednafen/firmware/` | The Saturn BIOS (Japanese 1.01; North American/European) for Mednafen. Hashes in [docs/mednafen.md](docs/mednafen.md#local-saturn-bios). |
| `scph1001.bin` | `local/mednafen/firmware/` | The PlayStation BIOS, to run the PS1 US disc in Mednafen. Hash in [docs/mednafen.md](docs/mednafen.md#local-playstation-bios-reference-captions-only). |
| `mednafen-1.32.1.tar.xz` | extracted to `vendor/mednafen/src/` | Mednafen's source. The project builds it with its agent-interface patch, which lets the tools drive the emulator; see [vendor/mednafen/README.md](vendor/mednafen/README.md). |

Arcade captures in MAME also need each set's decryption key and the QSound
ROM, which the zips above lack (see
[references/mshvsf/arcade/README.md](references/mshvsf/arcade/README.md)).

### Python Tooling

Run every Python command through `./invenv.sh`, without activating a virtual
environment:

```bash
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

### Local Data

Keep original images outside the repository or under an ignored path such as
`local/disc_images/`, and treat them as read-only. Generated images go only in
`build/`. Mednafen's runtime configuration belongs in the ignored
`local/mednafen/`; its provenance and setup are in
[docs/mednafen.md](docs/mednafen.md) and
[vendor/mednafen/README.md](vendor/mednafen/README.md).

Research records are kept by purpose:

- `research/experiments/`: one directory per controlled experiment;
- `research/screenshots/`, `savestates/`, `memory_dumps/`, and `traces/`:
  ignored binary evidence, with tracked metadata where appropriate;
- `data/translations/`: structured, evidence-backed text correspondences;
- `docs/discoveries.md`: confirmed durable findings only;
- `docs/known_unknowns.md`: unresolved questions;
- `research_log.md`: chronological successes and failures.

### Project Guides

- [AGENTS.md](AGENTS.md): authoritative operating rules
- [docs/agent_briefing.md](docs/agent_briefing.md): short, cited summary of current findings and tools
- [TASKS.md](TASKS.md): dependency-controlled research plan
- [research_log.md](research_log.md): chronological journal
- [docs/project_scope.md](docs/project_scope.md): milestone gates and non-goals
- [docs/research_protocol.md](docs/research_protocol.md): experiment protocol
- [docs/architecture.md](docs/architecture.md): repository architecture
- [docs/references.md](docs/references.md): source bibliography and evidence rules
- [data/translations/README.md](data/translations/README.md): translation policy
