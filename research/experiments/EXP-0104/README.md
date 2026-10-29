# EXP-0104: The five warning screens in English, each triggered on the Saturn

Task: UI-008
Status: DONE
Confidence: CONFIRMED (each screen triggered in Mednafen; each screenshot
equals its built BMP pixel for pixel)

## Observation

- `EXP-0103`: the no-cart warning is `ERR5.BIN`, a BMP drawn as it is.
  `ERR1`-`ERR4` are four more Japanese warnings in the same format.
- No official English exists: the game had no US Saturn release, and the
  arcade and PS1 have no such screens. The terms come from the US Saturn
  BIOS (`mpr-17933`), which holds "Memory Manager", "Manage Memory" (a
  button on its CD-player screen), "System Settings" and "Not Formatted"
  (strings at `0x585DE` and `0x7C87D`-`0x7C92A`). The CD-player screen, seen
  by booting the US BIOS with an audio-only CUE (`-force_module ss`), has no
  title of its own; the Japanese "マルチプレイヤー画面" is translated as "control
  panel".

## Hypothesis

1. Each of `ERR1`-`ERR4` is shown under its own condition, which Mednafen
   can produce: a 1 MB cartridge (ERR4), unformatted backup memory (ERR1), a
   damaged save (ERR2), too little free backup memory (ERR3).
2. English drawn into the five files' pixels, same size and palette, shows
   on each of these screens and changes nothing else.

## Controlled Change

- **Generator:** `official_endings --error-screens` adds expect-checked
  patches for the five files (`tools/disc/error_screens.py`, text in
  `data/ui008/error_screens.json`). Each file keeps its header and palette;
  its pixels are cleared and the English drawn in the US arcade's narrow
  win-quote glyphs (quote-font codes `0x120`-`0x187`, 8 pixels apart), white,
  cyan and red as the Japanese highlights, the title yellow.
- **Built files:**

  | File | Source SHA-256 | English SHA-256 | Patches |
  | --- | --- | --- | --- |
  | `ERR1.BIN` | `29461446…` | `d26cd6da…` | 204 |
  | `ERR2.BIN` | `125a33a8…` | `82677413…` | 181 |
  | `ERR3.BIN` | `4315c728…` | `6d0d7f76…` | 194 |
  | `ERR4.BIN` | `1941080c…` | `7899ae23…` | 105 |
  | `ERR5.BIN` | `0732e81d…` | `66ffbe9d…` | 103 |

- **Release references** rebaselined with the reason "EXP-0104: the five
  boot-time warning screens ERR1.BIN-ERR5.BIN in English (UI-008,
  --error-screens)". Only the five `ERR` files are added to each
  reference's file list; every other file hash is unchanged.
  - `m8_roster_gold` (Saturn names): spec `2a7eacaf…`, track 01 `1112bfb4…`
    (was `cdf366b3…`).
  - `m8_roster_gold_us` (American names): spec `7d35cfe7…`, track 01
    `b2e526a7…` (was `c6f1fbd0…`, the 0.1.0 release).

## Prediction

Each condition shows its English screen, equal to the built BMP shifted up
8 rows. The cart boot with a valid save is unchanged.

## Inputs and Provenance

- Source image as in `EXP-0103`; files extracted to `local/ui008/disc`.
- Backup-RAM fixtures from `tools/mednafen/backup_ram.py`, plus `valid.bkr`,
  a copy of `local/mednafen_quiet/sav/…0eac041df6b7d4ca563f4c35017eea24.bkr`
  (a real save by this game: `MSH_VS_SF__`, 480 bytes, block 2 plus blocks
  3-10).

  | Fixture | SHA-256 | How |
  | --- | --- | --- |
  | `zero.bkr` | `c3502047…` | `backup_ram zero` |
  | `free7.bkr` | `d3a8bedb…` | `backup_ram free7` |
  | `free8.bkr` | `74fd5bf9…` | `backup_ram free8` |
  | `free9.bkr` | `b86fe960…` | `backup_ram free9` |
  | `valid.bkr` | `1f897cef…` | copy of a real save |
  | `corrupt.bkr` | `f2f6fb88…` | `backup_ram corrupt --from valid.bkr` (`.bkr` byte `0x154`, `0D` → `F2`) |

## Tools and Environment

- Agent-patched Mednafen 1.32.1, JP BIOS `sega_101.bin`.
- One Mednafen home per case under `local/ui008/`, each a copy of
  `local/mednafen_quiet` with `ss.cart` set (`auto`, `none`, `extram1` or
  `backup`) and the fixture copied into `sav/` under the image's save name.
  Both the source and the built images use one save name per disc
  (`…0eac041d…` source, `…37613096…` American names); changing `ERR` files
  does not change it.

## Procedure

For each case, a cold boot captured at frames 900, 1200 and 1500 with no
input:

```bash
./invenv.sh python -m tools.mednafen.backup_ram free8 local/ui008/exp0104/free8.bkr
cp local/ui008/exp0104/free8.bkr \
  "local/ui008/home_v_free8/sav/Marvel Super Heroes vs. Street Fighter (Japan).37613096c32ecbe8835b021f1dff31a2.bkr"
./invenv.sh python -m tools.mednafen.frame_capture \
  "build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/ui008/exp0104/us_free8 --home local/ui008/home_v_free8 \
  --first 900 --last 1500 --step 300
```

Each warning screenshot was compared with its built BMP drawn in its own
palette, BMP row y at screen row y - 8, over screen rows 0-231.

## Actual Result

**Part 1: the source image** (Japanese; frame 1500 screenshots):

| Case | Cart | Backup RAM | Screen |
| --- | --- | --- | --- |
| control | 4 MB | `valid` | normal boot (`283f6b9f…`, as with fresh memory) |
| no cart | none | `valid` | ERR5 (`d4266c3a…`) |
| backup cart | Backup Memory | `valid` | ERR5 (`d4266c3a…`) |
| 1 MB cart | 1 MB Extended RAM | `valid` | ERR4 (`ceef2030…`) |
| unformatted | 4 MB | `zero` | ERR1 (`8b43f986…`) |
| damaged save | 4 MB | `corrupt` | ERR2 (`69e301e1…`) |
| 7 blocks free | 4 MB | `free7` | ERR3 (`bc80dfc8…`) |
| 8 blocks free | 4 MB | `free8` | ERR3 (`bc80dfc8…`) |
| 9 blocks free | 4 MB | `free9` | normal boot (`283f6b9f…`) |

**Part 2: the American-names image** (track 01 `b2e526a7…`):

| Case | Screen | Pixel mismatches against the built file |
| --- | --- | --- |
| 4 MB cart, `valid` | normal boot, frames 900/1200/1500 identical to the source's | — |
| no cart | English ERR5 (`a7533232…`) | 0 |
| 1 MB cart | English ERR4 (`a5aaab06…`) | 0 |
| `zero` | English ERR1 (`bee425ae…`) | 0 |
| `corrupt` | English ERR2 (`61f14dcf…`) | 0 |
| `free8` | English ERR3 (`11e24bf8…`) | 0 |
| `free9` | normal boot | — |

**Saturn-names image** (track 01 `1112bfb4…`): the 4 MB cart boot is
identical to the source's; with no cart, English ERR5 (`a7533232…`, the same
as the American-names image).

## Conclusion

**CONFIRMED:** each warning screen and its condition, and the English build
of all five:

- ERR5: no cartridge, or a cartridge that is not extended RAM (a backup
  memory cartridge);
- ERR4: an extended RAM cartridge of the wrong size (1 MB);
- ERR1: internal backup memory not formatted;
- ERR2: the game's save cannot be read (one inverted data byte);
- ERR3: no save, and 8 or fewer free 64-byte blocks (the save needs 9).

The release references build all five in English, and nothing else in
them changes.

## Uncertainty and Alternatives

- **ERR3's "8":** the Japanese gives no unit. The save takes 9 raw blocks
  and the warning shows at 8 free, so "8" is not the raw block count the
  save needs. It could be the BIOS's count (if the BIOS counts one less) or
  the save's data blocks (it has 8 besides its first block). The English says
  "[8] free blocks"; the exact meaning is in `docs/known_unknowns.md`.
- **Terms:** "Memory Manager" is from US BIOS strings. The menus were not
  shown, since the agent cannot press buttons. "Control panel" is a
  description, not a BIOS string.
- Not tested: real hardware; a damaged save other than one data byte; the
  cartridge check on other carts (only none, backup, 1 MB and 4 MB).

## Reproduction

The commands above, per case. Screenshots and fixtures stay local:
`local/ui008/exp0104/`.
