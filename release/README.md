# Release Patch: English Win Quotes and Endings (M8)

This folder describes the English patch for the Japanese Sega Saturn release of
**Marvel Super Heroes vs. Street Fighter**. It covers how to apply the patch,
and how to rebuild it from this repository.

**The patch file itself is not in the repository.** Its bytes include
game-derived data, which this project never commits (`AGENTS.md` rule 21).
Build it locally (see "Rebuild the Patch") and distribute it yourself.

[`m8_roster.json`](m8_roster.json) is the release record: hashes, sizes,
xdelta3 version, and flags (metadata only).

## What the Patch Changes

17 characters: Cyclops, Captain America, Hulk, Wolverine, Shuma-Gorath, Omega
Red, Spider-Man, Blackheart, Ryu, Ken, Chun-Li, Dhalsim, Zangief, Vega, Gouki,
Sakura, and Dan.

- **Win quotes:** the official US arcade English, after every win
  (`docs/coverage_exceptions.md`, Win Quotes).
- **Endings:**
  - each character's ending pages, in the official US arcade English;
  - the post-boss partner dialogue, using the arcade's English partner lines;
  - English character names (`docs/coverage_exceptions.md`, Endings).
- **Names follow the Saturn's own art and voice:** Vega (not M. Bison), Gouki
  (not Akuma), and Mech-Gouki (not Cyber-Akuma). This is a **provisional**
  decision (`LOC-001`, `docs/localization_plan.md`).

**Not changed:**
- Norimaro, the secret characters, Apocalypse, and Mech-Gouki's own text;
- menus, graphics, voice, and every other screen.

Only track 01 changes. Tracks 02-12 (audio) and the CUE sheet are
byte-identical to the original.

**Verification:**
- Seen running in Mednafen:
  - seven endings;
  - sampled characters' win quotes, in the earlier win-quote-only image
    (M5), and one (Vega's) in this combined image.
- The rest was checked offline (`EXP-0044` to `EXP-0050`).
- Open questions are in `docs/known_unknowns.md`.

## Apply the Patch

### You need

1. **The original disc image**, as BIN/CUE with 12 tracks. Every component must
   match these SHA-256 values (`references/mshvsf/saturn_jp/README.md`):

   | Component | Size (bytes) | SHA-256 |
   | --- | ---: | --- |
   | `Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin` | 452397792 | `8274307f9562d2da7fb7be0f5f306846edb74afde5913324bef04938ed3214f9` |
   | `… (Track 02).bin` to `… (Track 12).bin` | | as listed in `references/mshvsf/saturn_jp/README.md` |
   | `Marvel Super Heroes vs. Street Fighter (Japan).cue` | 1697 | `526a4370aee466d9ace54e6ce6526b199580c736f2c8a888b704a98a7d9013b7` |

   Only track 01 is patched, but the other tracks must be the originals.

2. **The patch:** `mshvsf_saturn_en_m8.Track01.xdelta`, 155,717 bytes, SHA-256
   `00c3906ade7971a638a5b9d6399f61dfe39cbe04490da5df7e6e6cd676eb76db`.

3. **An xdelta3 (VCDIFF) patcher.**
   - Tested: the `xdelta3` 3.2.2 command line (`brew install xdelta` on macOS).
   - Not tested: graphical patchers such as Delta Patcher, xdelta UI, or Rom
     Patcher JS. The patch uses plain VCDIFF with no secondary compression and
     no application header, which they are expected to read.

### Steps

```bash
xdelta3 -d -s "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
  mshvsf_saturn_en_m8.Track01.xdelta "Track 01 patched.bin"
```

1. Run the command above in the folder with the original image.
2. Check the result. Its SHA-256 must be
   `2a5b26b75a0d908050ccf361c99f37a2f2a83dc70e3dc9612e5e98c16da5624d`.
3. Replace track 01 with the patched file, keeping its original filename so
   the CUE sheet still finds it. Keep tracks 02-12 and the CUE unchanged.
4. Load the CUE in a Saturn emulator. The project tests with Mednafen and the
   4 MB RAM cartridge.

xdelta3 checks each window's Adler-32 checksum. It refuses a wrong source with
"target window checksum mismatch".

## Rebuild the Patch from This Repository

The build is deterministic. It reproduces the hashes above from the untouched
image and the arcade ROM set.

### Assets you must supply (none are in the repository)

| Asset | Where it goes | Identity |
| --- | --- | --- |
| Saturn disc image (all 13 components) | `local/disc_images/mshvsf_saturn_jp/` | SHA-256 values in `references/mshvsf/saturn_jp/README.md` |
| MAME arcade set `mshvsfu` (USA 970827) | `local/arcade_roms/mshvsf/mshvsfu.zip` | The zip used: SHA-256 `32f4cb993a55eeff1397b24df5e9b2f14dd5baf6955a6fd69c77a49327794eee`. The per-file ROM identities are in `references/mshvsf/arcade/README.md`. A different zip with the same ROMs should work, but that is untested. |
| MAME `cps2.cpp` at commit `f34f02505e32c1993c6a782b6814232cbfc74e36` | `local/mame_src/cps2.cpp` | SHA-256 `a8c09ef83841d75b81a4b2ee8ac029ebf8eecb6a743b016abb33e3d46e861602` (public source; command below) |

The arcade set is the source of the official English text, so it is
required. The `cps2.cpp` driver tells the tools how the arcade ROM files are
laid out.

### Tools

- `uv` and Python 3.12 or newer: run `./setup_venv.sh`.
- xdelta3 3.2.2. The record was made with this version; another version may
  produce a different patch file, but the same target hash.

### Already in the repository

- the roster (`data/text/m5_roster.json`);
- the font-candidate list (`data/text/font_candidates.json`);
- the translation policy (`data/translations/README.md`);
- the generators and compiler (`tools/`);
- the expected hashes (`data/regression/reference_builds.json`, reference
  `m8_roster`).

### Commands

```bash
./setup_venv.sh
mkdir -p local/mame_src
curl -sSfLo local/mame_src/cps2.cpp https://raw.githubusercontent.com/mamedev/mame/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp

# 1. Rebuild every reference from the untouched image and check its hashes
#    (6 of 6 must pass). The m8_roster build lands in build/regression/m8_roster/.
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp

# 2. Make the patch from that build; it is checked against the m8_roster reference.
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster/build/image_a --reference m8_roster \
  --stem mshvsf_saturn_en_m8 --out-dir build/release/m8 --record release/m8_roster.json
```

**Expected:**
- the spec: `04ccb452…`;
- track 01: `2a5b26b7…`;
- the patch: `00c3906a…` (with xdelta3 3.2.2).

`make_patch` also checks that:
- the source components are the recorded originals;
- only BIN tracks differ;
- two encodings are byte-identical;
- `xdelta3 -d` reproduces the built track.

To build step by step instead, see `research/experiments/EXP-0050/README.md`
(Reproduction).
