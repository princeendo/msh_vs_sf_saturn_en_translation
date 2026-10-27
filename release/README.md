# Release Patch: English Win Quotes and Endings (M8)

This folder describes the English patch for the Japanese Sega Saturn release of
**Marvel Super Heroes vs. Street Fighter**. It covers how to apply the patch,
and how to rebuild it from this repository.

**The patch file itself is not in the repository.** Its bytes include
game-derived data, which this project never commits (`AGENTS.md` rule 21).
Build it locally (see "Rebuild the Patch") and distribute it yourself.

[`m8_roster_gold.json`](m8_roster_gold.json) is the release record: hashes,
sizes, xdelta3 version, and flags (metadata only).
[`m8_roster_gold.ssp.json`](m8_roster_gold.ssp.json) is the same for the
Sega Saturn Patcher (`.ssp`) file.

## Choose a Name Variant

Two patches are built from the same tools. They differ only in how three
characters are named (`LOC-003`):

| | Saturn names (default) | American names |
| --- | --- | --- |
| Patch | `mshvsf_saturn_en_m8_gold.Track01.xdelta` | `mshvsf_saturn_en_m8_gold_us.Track01.xdelta` |
| Sega Saturn Patcher patch | `mshvsf_saturn_en_m8_gold.ssp` | `mshvsf_saturn_en_m8_gold_us.ssp` |
| Record | [`m8_roster_gold.json`](m8_roster_gold.json), [`.ssp.json`](m8_roster_gold.ssp.json) | [`m8_roster_gold_us.json`](m8_roster_gold_us.json), [`.ssp.json`](m8_roster_gold_us.ssp.json) |
| Reference | `m8_roster_gold` | `m8_roster_gold_us` |
| English text | Vega, Gouki, Mech-Gouki | Bison, Akuma, Cyber Akuma (as the US arcade) |
| Announcer's name calls | Vega, Gouki, Mech Gouki (unchanged) | Bison, Akuma, Cyber Akuma: recordings already on the disc, selected through six data edits in `MEMFIX.PAC` (`EXP-0058`) |
| Life-bar names (both sides) | VEGA, GOUKI, MECH-GOUKI | BISON, AKUMA, CYBER-AKUMA: the game's own US label records (`EXP-0065`) |
| Ending speaker labels | Vega, Gouki, Mech-Gouki | Bison, Akuma, Cyber Akuma (`EXP-0060`) |
| Sound test, title-menu unlock message | 18.VEGA, 22.GOUKI, MECH-GOUKI NOW!! | 18.BISON, 22.AKUMA, CYBER-AKUMA NOW!! (`EXP-0061`) |
| Win banner ("… WIN") | VEGA, GOUKI, MECH-GOUKI | BISON, AKUMA, CYBER-AKUMA: the game's own banner records (`EXP-0062`) |
| VS-screen names | Vega, Gouki, Mech-Gouki | BISON, AKUMA, CYBER-AKUMA: the game's own VS name records (`EXP-0063`) |
| Attract-mode captions | English (both variants, identical) | English (both variants, identical) |

- **Saturn names** matches everything the game shows and says. It is the
  recommended patch.
- **American names** switches every name surface found so far (`LOC-004`).
  It was played from a cold boot (`EXP-0064`): the "Akuma" and "Bison" calls
  at character select, BISON / AKUMA vs CYBER-AKUMA on the VS screen, AKUMA
  and CYBER-AKUMA life bars, the AKUMA / BISON / WIN banner, and the "Akuma"
  win call.
  - Seen running: after a cold boot, sound RAM holds the American calls
    (`EXP-0059`).
  - Proven in a replay: switching that table entry makes the win screen say
    "Bison" (`EXP-0058`).
  - Seen in replays: BISON and CYBER-AKUMA life bars, a "Bison" speaker
    label (`EXP-0060`), a BISON / RYU / WIN banner (`EXP-0062`), and BISON on
    the VS screen (`EXP-0063`).
  - Seen in play since (`EXP-0074`): the full-width AKUMA life bar for
    player 1 and the italic AKUMA for player 2.
  - Not yet heard in play: the Cyber Akuma call.

Apply either patch the same way (below), using that patch's file and target
hash. Everything else in this README applies to both.

The release uses the gold credits-style captions (`FONT-011`, reference
`m8_roster_gold`, user decision 2026-10-25). The earlier white-font build
(reference `m8_roster`, record [`m8_roster.json`](m8_roster.json)) can still be
rebuilt the same way with `--reference m8_roster`.

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
- **English UI labels:** the player-2 prompt shows the game's own "JOIN IN"
  art instead of "対戦者求む!", and the mode panel's "簡単操作" now reads
  "EASY" (`UI-001`, `UI-002`).
- **Caption look:** captions and ending text use the game's own staff-credits
  font, squeezed two letters per cell, in the credits' gold, instead of the
  original white font. The gold also colours the remaining Japanese message
  windows (excluded characters).
- **Attract-mode captions:** the Japanese teaser captions before the demo
  are replaced by the US arcade's three English captions, with its wording,
  line breaks and centring: LEGENDARY / HEROES / UNITE AGAIN!!, AMAZING /
  TEAM BATTLES!, and NEW HEROES / JOIN / THE FIGHT!!, in the game's own
  win-banner letters and colours (`UI-003`, `EXP-0071`, `EXP-0073`). Letters
  are 24 pixels apart (the arcade's 28 does not fit the Saturn's narrower
  screen).
- **Secret characters** (`SPECIAL-003`, `EXP-0078`): Shadow, U.S. Agent and
  Mephisto get the arcade's official English win quotes; Metal Zangief's and
  Dark Sakura's own win quotes and every secret character's ending pages are
  new English translations (not official text: the arcade only reuses
  Zangief's and Sakura's quotes and shows a generic message); the post-boss
  partner lines are the arcade's official English.
- **Norimaro** (`SPECIAL-002`, `EXP-0079`): his win quotes and post-boss
  partner lines are the international arcade's official English; his ending
  pages are a new English translation (not official text).
- **Bosses** (`SPECIAL-004`, `EXP-0081`, `EXP-0082`): Apocalypse's and
  Mech-Gouki's win quotes, shown when they beat you, and Apocalypse's
  exchange with each challenger before his stage-7 fight, are the arcade's
  official English.
- **CONTINUE? hints** (`UI-004`, `EXP-0080`): the gameplay hint under the
  countdown is a new English translation (no official English exists); the
  joystick arrows are the game's own.
- **Boss fight unlocked:** the title menu's MECH-GOUKI NOW!! (CYBER-AKUMA
  NOW!! with American names) is available from the start, without a
  Survival clear: on the SURVIVAL MODE row, press L or R, then Start
  (`OPT-001`, `EXP-0075`). Build option `--unlock-boss-fight`, on by
  default; `--no-unlock-boss-fight` keeps the original lock.
- **Names follow the Saturn's own art and voice:** Vega (not M. Bison), Gouki
  (not Akuma), and Mech-Gouki (not Cyber-Akuma). This is a **provisional**
  decision (`LOC-001`, `docs/localization_plan.md`). The American-name patch
  differs only here (see "Choose a Name Variant").

**Not changed:**
- menus, voice, and every other screen; the attract-mode Norimaro screen.
  The American-name patch also changes three name calls; see "Choose a Name
  Variant".

Only track 01 changes. Tracks 02-12 (audio) and the CUE sheet are
byte-identical to the original.

**Verification:**
- Seen running in Mednafen:
  - seven endings (in the white-font build);
  - sampled characters' win quotes, in the earlier win-quote-only image
    (M5), and one (Vega's) in the white combined image;
  - in this gold build (`EXP-0052`): Ryu + Ken's dialogue and pages, a win
    quote, and the redesigned capital `W`;
  - the English UI labels (`EXP-0053`): "EASY" live, and "JOIN IN" in a
    replay;
  - the three English attract captions from a cold boot (`EXP-0073`, in the
    American-name image; both images carry byte-identical `MVSOP*.ST2`
    files).
  - from a cold boot, in the American-name image: Metal Zangief's win quote,
    post-boss lines and ending (`EXP-0078`), and Norimaro's (`EXP-0079`);
    two CONTINUE? hints (`EXP-0080`).
- The rest was checked offline (`EXP-0044` to `EXP-0052`).
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

2. **The patch:**
   - Saturn names: `mshvsf_saturn_en_m8_gold.Track01.xdelta`, 642,747
     bytes, SHA-256
     `f769294861bd7bc70ee69c75b96dc52f0ceb04aef605a38a360f98edfa00c460`;
   - American names: `mshvsf_saturn_en_m8_gold_us.Track01.xdelta`, 644,202
     bytes, SHA-256
     `3d23dcd8444f122d00341d0b3a8ca900de193af9f86962c75869de0dca405ef4`.

   Most of their size is the English attract captions: the rebuilt streams
   keep the original compressed bytes wherever possible (`REL-003`), and
   what remains is the new caption art and the CD error-correction bytes of
   the sectors it touches.

3. **An xdelta3 (VCDIFF) patcher.**
   - Tested: the `xdelta3` 3.2.2 command line (`brew install xdelta` on macOS).
   - Not tested: graphical patchers such as Delta Patcher, xdelta UI, or Rom
     Patcher JS. The patch uses plain VCDIFF with no secondary compression, no
     application header and a 16 MiB window, which they are expected to read.

### Steps

```bash
xdelta3 -d -s "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
  mshvsf_saturn_en_m8_gold.Track01.xdelta "Track 01 patched.bin"
```

1. Run the command above in the folder with the original image.
2. Check the result. Its SHA-256 must be
   `e820f6e12fb54d71f19c83477399e91159de2a1856e0983df93e76cec452a1c2` for the
   Saturn-name patch, or
   `a6572495338f2d490abb75f7e4311230629a2f6b3749e9caabd1f576e87528d4` for the
   American-name patch (use the `_us` patch file in the command).
3. Replace track 01 with the patched file, keeping its original filename so
   the CUE sheet still finds it. Keep tracks 02-12 and the CUE unchanged.
4. Load the CUE in a Saturn emulator. The project tests with Mednafen and the
   4 MB RAM cartridge.

xdelta3 checks each window's Adler-32 checksum. It refuses a wrong source with
"target window checksum mismatch".

### Or: Sega Saturn Patcher (.ssp)

The same changes, as an `.ssp` file (`REL-002`, `EXP-0084`):

| Variant | File | Size (bytes) | SHA-256 |
| --- | --- | ---: | --- |
| Saturn names | `mshvsf_saturn_en_m8_gold.ssp` | 560,868 | `eb809034c1adc21ccfc6f192d93f9fa9df3cb8c6b720ee26830971ca50ec7a61` |
| American names | `mshvsf_saturn_en_m8_gold_us.ssp` | 560,981 | `1a7f0f32be32c81914d3b1190f17829f2411bb6f82b88f3ce2dbb87f772fd185` |

- **Tested: [saturn-patcher-egui](https://github.com/ralfguth/saturn-patcher-egui)**
  (Linux and Windows builds, or build from source on macOS). It patches a
  copy of track 01 in place:

  ```bash
  cp "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" "Track 01 patched.bin"
  saturn-patcher mshvsf_saturn_en_m8_gold.ssp "Track 01 patched.bin"
  ```

  The result has the same SHA-256 as the xdelta result above (`e820f6e1…`,
  or `a6572495…` for the `_us` file). Continue from step 3 above. egui
  checks each original file's MD5 first and stops on a wrong or
  already-patched image.
- **Not tested: the official Sega Saturn Patcher** (Windows, .NET 5 Desktop
  Runtime). Select the CUE as a CD image, then "+ Game Patch (SSP)" and
  "Patch Image".
  - It rebuilds the whole disc instead of patching in place, so its output
    will not have the hashes above.
  - The `.ssp` has the entries its code requires, and no `ip.bin`: the
    image keeps its own boot area.

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
- the expected hashes (`data/regression/reference_builds.json`, references
  `m8_roster_gold` and `m8_roster_gold_us`).

### Commands

```bash
./setup_venv.sh
mkdir -p local/mame_src
curl -sSfLo local/mame_src/cps2.cpp https://raw.githubusercontent.com/mamedev/mame/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp

# 1. Rebuild every reference from the untouched image and check its hashes
#    (9 of 9 must pass). The gold builds land in build/regression/m8_roster_gold/
#    (Saturn names) and build/regression/m8_roster_gold_us/ (American names).
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp

# 2. Make the patch from that build; it is checked against the m8_roster_gold reference.
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --out-dir build/release/m8_gold \
  --record release/m8_roster_gold.json

# 2b. The American-name patch, from its own reference.
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us \
  --record release/m8_roster_gold_us.json

# 3. The Sega Saturn Patcher (.ssp) files, from the same builds.
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold/build/image_a --reference m8_roster_gold \
  --stem mshvsf_saturn_en_m8_gold --release-version 0.1.0 \
  --description "Official arcade English text; Saturn character names." \
  --out-dir build/release/m8_gold --record release/m8_roster_gold.ssp.json
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us \
  --stem mshvsf_saturn_en_m8_gold_us --release-version 0.1.0 \
  --description "Official arcade English text; US character names." \
  --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.ssp.json
```

**Expected:**
- Saturn names: spec `115f6cd3…`, track 01 `e820f6e1…`, patch `f7692948…`;
- American names: spec `d441e9fc…`, track 01 `a6572495…`, patch `3d23dcd8…`;
- the patch hashes assume xdelta3 3.2.2;
- `.ssp`: `eb809034…` (Saturn names) and `1a7f0f32…` (American names). These
  need no external tool; they assume the recorded Python 3.12.13 build (zlib
  1.2.12 and its own bzip2).

`make_ssp` checks the same source and reference. It also checks that only
whole files change, that two builds are byte-identical, and that its own
applier reproduces the built track.

`make_patch` also checks that:
- the source components are the recorded originals;
- only BIN tracks differ;
- two encodings are byte-identical;
- `xdelta3 -d` reproduces the built track.

To build step by step instead, see `research/experiments/EXP-0052/README.md`
(Build; add `--caption-palette gold --ui-english`).
