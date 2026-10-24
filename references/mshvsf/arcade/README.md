# MSHvSF Arcade ROM Sets (Local)

Three CPS-II arcade ROM sets of *Marvel Super Heroes vs. Street Fighter* are
kept locally as **reference evidence and translation oracles**. They are never a
modification target, and they are not a template for Saturn structures.

## Where They Are

Each set is a MAME-style zip archive. They are copied unchanged to the ignored path
`local/arcade_roms/mshvsf/`. The `local/` rule and the global `*.zip` rule in
`.gitignore` keep them out of version control. Never commit these files, their
members, or anything extracted or captured from them. Treat the copies as
immutable.

Supplied by the user on 2026-10-23 from `~/Downloads/mshvsf/`. The copies were
checked against the originals by SHA-256 when copied.

## Identities

Release identities come from the `REF-008` audit (2026-10-23) against the pinned
MAME 0.289 driver; see [Audit](#audit-against-mame-0289).

| Filename | MAME 0.289 set and title | Size (bytes) | SHA-256 |
| --- | --- | ---: | --- |
| `mshvsf.zip` | `mshvsf`, *(Europe 970625)* | 21896860 | `5fae509a111b7403243956322c642e24ad1811630f54775bed761095f956385d` |
| `mshvsfu.zip` | `mshvsfu`, *(USA 970827)* | 21897435 | `32f4cb993a55eeff1397b24df5e9b2f14dd5baf6955a6fd69c77a49327794eee` |
| `mshvsfj.zip` | `mshvsfj`, *(Japan 970707)* | 21897527 | `3f5418276843fa2c5747c53d4c892016c2da2b7acd0759eccb9c900dfae0d19c` |

Zip SHA-256 values identify these local archives only. Archive metadata can differ
between sets with identical ROMs, so release identity comes from per-member hashes.
`970625`, `970827`, and `970707` are program version labels, not proven release
dates.

## Audit Against MAME 0.289

Reproduce with the pinned driver source (977,277 bytes; the SHA-256 is checked):

```bash
curl -sSfLo /tmp/cps2.cpp https://raw.githubusercontent.com/mamedev/mame/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp
```

```bash
./invenv.sh python -m tools.reference.mame_audit --driver /tmp/cps2.cpp --expect-driver-sha256 a8c09ef83841d75b81a4b2ee8ac029ebf8eecb6a743b016abb33e3d46e861602 --family mshvsf --json local/arcade_roms/mshvsf/mshvsf.zip local/arcade_roms/mshvsf/mshvsfu.zip local/arcade_roms/mshvsf/mshvsfj.zip
```

The committed output is [`mame0289_audit.json`](mame0289_audit.json), from
Python 3.12.13 via `uv`. The results:

- **CONFIRMED:** every ROM file in each zip matches its MAME 0.289 set by name,
  size, CRC-32, and SHA-1. Each zip has 20 of 21 expected files and no unexpected
  members.
- **CONFIRMED:** each zip matches only its own set. Every other set in the family
  scores 18 or fewer of 21, including `mshvsfu1` (USA 970625) and the Phoenix
  bootleg.
- **Missing from every zip:** the CPS-II decryption key that MAME 0.289 lists in
  its `key` region: `mshvsf.key` (CRC-32 `64660867`), `mshvsfu.key`
  (`4c04797b`), and `mshvsfj.key` (`565eeebb`), each 20 bytes. MAME's definitions
  list it as a required ROM.
- **Observed with MAME 0.289** (Homebrew, 2026-10-23): running
  `mame -rompath local/arcade_roms/mshvsf -verifyroms mshvsf mshvsfu mshvsfj`
  reports all three sets as bad. Each is missing its `.key` file and also
  `dl-1425.bin` (24,576 bytes), the QSound device ROM (`qsound_hle`), which is
  normally kept in a separate `qsound.zip`. Legal copies of both are a
  prerequisite for any arcade capture (`REF-009`).

### Member Layout

- All three sets share `mvs.01`, `mvs.02` (audio CPU), `mvs.06a`-`mvs.10b`
  (68000 program), `mvs.11m`/`mvs.12m` (QSound samples), and `mvs.13m`-`mvs.20m`
  (graphics). The roles come from the driver's `ROM_REGION` names.
- The sets differ only in the first three 68000 program files (`maincpu`
  `0x000000`-`0x17FFFF`):

| Set | Region-specific members (CRC-32) |
| --- | --- |
| `mshvsf` | `mvse.03f` (`b72dc199`), `mvse.04f` (`6ef799f9`), `mvs.05a` (`1a5de0cb`) |
| `mshvsfu` | `mvsu.03g` (`0664ab15`), `mvsu.04g` (`97e060ee`), `mvs.05d` (`921fc542`) |
| `mshvsfj` | `mvsj.03i` (`d8cbb691`), `mvsj.04i` (`32741ace`), `mvs.05h` (`77870dc3`) |

- In MAME 0.289, the key decrypts only a separate opcode address space
  (`decrypted_opcodes_map`; `cps2_decrypt` in `cps2.cpp`). Data reads use the raw
  program ROM. The driver loads these files with `ROM_LOAD16_WORD_SWAP`, so their
  byte order is swapped relative to 68000 memory. `EXP-0029` read the quote text
  directly from the raw members.
- The Latin win quotes, the endings, and their pointer tables are in `mvs.07b`,
  which all sets share (`EXP-0029`, **CONFIRMED** as data). How the Japanese text
  is encoded is **UNKNOWN**.

## Running in MAME (`REF-009`)

The user supplied the missing files on 2026-10-24. They were copied (originals kept
in `~/Downloads/mshvsf/`), and the zips were left unchanged. MAME also reads
`<rompath>/<set>/` folders:

| Local path (ignored) | Size | SHA-256 | Matches MAME 0.289 |
| --- | ---: | --- | --- |
| `mshvsf/mshvsf.key` | 20 | `cc4f8d714cc747f84fde20eb440c5542837b55076e4144fcb82116d00a94fb4f` | CRC `64660867`, SHA-1 match |
| `mshvsfu/mshvsfu.key` | 20 | `838fc71e642c4f9a84e6c2bf9fbec202625683df9c00b9c3674941c756586b48` | CRC `4c04797b`, SHA-1 match |
| `mshvsfj/mshvsfj.key` | 20 | `0981af466a7ef34356b11712f0d07a43de7ee104db2e464e0cc4e78907886a31` | CRC `565eeebb`, SHA-1 match |
| `qsound.zip` | 2676 | `55feb9b70dacb7364f0310ed16cc9281b5b0a31318b9e2e0587ae06d15f95356` | `dl-1425.bin`: CRC `d6cf5ef5`, SHA-1 `555f50fe…a0c501` (`src/devices/sound/qsoundhle.cpp`) |

- `mame -rompath local/arcade_roms/mshvsf -verifyroms mshvsf mshvsfu mshvsfj`
  reports "3 romsets found, 3 were OK".
- Each set boots headless to its title screen and attract mode. The command uses
  `tools/reference/mame_snap_frames.lua`, and MAME state goes to the ignored
  `local/mame_arcade/`:

```bash
SNAP_FRAMES="1200 3000" mame mshvsfu -rompath local/arcade_roms/mshvsf -video none -sound none -nothrottle -skip_gameinfo -nomouse -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram -snapshot_directory local/mame_arcade/snap -homepath local/mame_arcade -autoboot_script tools/reference/mame_snap_frames.lua
```

| Set | Frame 3000 (title screen) snapshot SHA-256 |
| --- | --- |
| `mshvsf` | `9f8c1b755b4a59e538961cb6e8f74a580f29365385029ec6ae9ae78ff4d68d16` |
| `mshvsfu` | `6ca0173600fd3424fcc20cd14b45e95522412b8c3f3615eb3878ea803b87b45e` |
| `mshvsfj` | `32c1b52e4cb07d6b369b00aca3b2b3e9d4cc9cf25d8dd2a46d024f0179fdb23b` |

- A second `mshvsfu` run reproduced frames 1200 and 3000 bit for bit. Both runs
  used the EEPROM that the first boot created in `local/mame_arcade/nvram/`.
- Observed in attract mode (not yet analyzed):
  - The US set shows its "Recycle it" and "Parental Advisory Warning" screens.
  - The Japanese set's license screen credits Noritaro Kinashi, Arrival, and NTV,
    and its intro uses "Variable" naming (consistent with RC-5).
- No local `mshvsfu1` (USA 970625) exists. The capture protocol's two-revision
  comparison is limited to `mshvsfu` until one is supplied.

### On-Screen Confirmation (`EXP-0030`)

- Scripted MAME runs reached Ryu's win screen. The displayed quotes matched
  decoded slot 9 entries 6 and 7 line for line, and RAM pointed at those entries.
- The European set showed entry 6 pixel-identically to the US set.
- Winners in slots 5, 6, 11, 12, 13, and 16 also matched the name list. The
  decoded table is therefore a capture-backed source for official arcade English;
  unobserved entries rest on the confirmed layout.

## Second Batch: Full MAME Split Set (`REF-011`)

The user supplied all 11 MAME 0.289 `mshvsf` sets on 2026-10-24
(`~/Downloads/mshvsf/v2`). They were copied unchanged to the ignored
`local/arcade_roms/mshvsf_v2/`.

- Per-zip identity, size, and SHA-256 are in [`v2_manifest.json`](v2_manifest.json).
  Every member matches its MAME 0.289 set by CRC-32 and SHA-1. The parent is
  `mshvsf.zip`; each clone zip holds only its region files.
- The `v2` `mshvsf.zip` has different zip bytes from the first copy, but the same
  20 ROM files.
- Keys: `mshvsfu1` uses `mshvsfu.key`, and `mshvsfj1` and `mshvsfj2` use
  `mshvsfj.key` (the same CRCs in the driver). Copies of the keys already held were
  placed in `local/arcade_roms/mshvsf/<set>/`.
- Run
  `mame -rompath "local/arcade_roms/mshvsf_v2;local/arcade_roms/mshvsf" -verifyroms "mshvsf*"`.
  It reports **6 of 11 OK**: `mshvsf`, `mshvsfu`, `mshvsfu1`, `mshvsfj`,
  `mshvsfj1`, and `mshvsfj2`.
- The other 5 (`mshvsfa`, `mshvsfa1`, `mshvsfb`, `mshvsfb1`, `mshvsfh`) lack only
  `mshvsfa.key`, `mshvsfb.key`, and `mshvsfh.key`.
- `mshvsfu1` (USA 970625) is now available for the capture protocol's
  two-revision comparison. The earlier "no local `mshvsfu1`" limit no longer
  applies.

## What They Are For

1. **Exact English quotes.** All three sets hold the official English post-fight
   text, which `tools/reference/cps2_text.py` decodes to the ignored
   `local/arcade_text/` (`EXP-0029`). This gives a full candidate text per
   character slot (`REF-004`). Wording counts as evidence only
   from a captured, transcribed frame of an identity-verified set, following the
   capture protocol in `docs/references.md`.
2. **Cross-region comparison.** Check whether the European and US English agree,
   and compare both with the Japanese arcade text (`REF-006`).
3. **Japanese arcade reference.** The Japanese set is a Japanese-language
   comparison point for the Saturn target. It is not proof of Saturn storage or
   wording.

## Content May Differ by Region

The user has heard that the Japanese set contains quotes for Norimaro and for
secret characters that the English sets may lack. `REF-008` collected sources on
this (2026-10-23). **Every row below is a `HYPOTHESIS`.** None has been observed in
a captured frame of these sets. Sources are listed in `docs/references.md` under
"Regional Arcade Content Claims". "TCRF" means the Wayback Machine snapshot
`20261011115711` of the arcade page; the live page's bot check could not be passed,
and the user approved using the snapshot.

| ID | Claim | Source (reliability) | Matters for |
| --- | --- | --- | --- |
| RC-1 | Norimaro is normally selectable only in the Japanese sets. Elsewhere his slot shows the game logo. TCRF says international sets unlock him when byte `0xCD` is `01` (a MAME cheat). | TCRF (fan wiki); Wikipedia, citing GameSpot and GamesRadar (secondary); RQ87 (fan site) | The user's report |
| RC-2 | International ROMs still hold translated Norimaro text: his win quotes, his Apocalypse pre-fight lines, his taunt bubble, and his hyper-combo caption. The quotes also exist in Spanish and Portuguese. His international ending shows only the first line of Dan's ending text. | TCRF; RQ87 | **Contradicts "JP only"** for Norimaro's win quotes |
| RC-3 | All secret characters (Capcom and Marvel) have unique win quotes only in the Japanese version. International versions reuse the normal character's quotes; for Shadow, the quotes are from the previous game. TCRF lists the Japanese quotes as a to-do and does not transcribe them. | TCRF | **Supports** the user's report for secret characters |
| RC-4 | Dark Sakura, Mech-Zangief, and Shadow have real endings in Japan. International versions show the generic secret-character screen, which is in English in all regions. TCRF gives fan translations of the Japanese endings. | TCRF; RQ87 | Endings (M6+, out of scope) |
| RC-5 | Some names differ by region: Dictator's "Knee Press Nightmare" (JP) becomes "Scissors Kick Nightmare", and "Variable" becomes "Cross-Over Combinations". Mech-Gouki versus Cyber-Akuma comes from search snippets only. | TCRF; RQ87 | Terminology |
| RC-6 | In Japan 970702 and 970707, Norimaro can be selected only at "1 Coin = 1 Credit" or Free Play. Japan 970625 has no such restriction. The local `mshvsfj` is 970707. | TCRF (refines the uncertain RQ87 claim) | Capture settings |
| RC-7 | The game has a language setting beyond English: the TCRF text mentions setting it to Spanish, Portuguese, or Japanese. In the Hispanic set, the location-test ending text stays in English. Which languages each local set offers is unknown. | TCRF | Whether one set can show several languages |
| RC-8 | Shadow's win quotes are identical to Charlie's in *X-Men vs. Street Fighter* and are left-aligned, except in Japanese. | TCRF | Reference-text oddity |

ROM data (`EXP-0029`, 2026-10-23) tests several of these without MAME. The program
data shows what each set **contains**, not what it displays:

- RC-2 is **SUPPORTED**: slot 17 (NORIMARO) has its own block of 8 English quotes,
  plus Spanish and Portuguese.
- RC-3 is **SUPPORTED** for the palette-swap secrets: Mech-Zangief, Dark Sakura,
  and Armored Spider-Man reuse their base characters' blocks. Shadow, U.S. Agent,
  and Mephisto have their own blocks, so "all secret characters borrow" is too
  broad. The Japanese-only unique quotes are not checked; the Japanese text is not
  decoded.
- RC-4 is **SUPPORTED**: in the endings table, Norimaro shares Dan's block, and
  Cyber-Akuma plus all six secret characters share one generic block.
- RC-7 is **SUPPORTED**: the English, Spanish, and Portuguese text is identical in
  all three sets, including Japan. What a set displays must therefore depend on its
  region code or language setting, not on which text it holds.

Regional facts from the primary MAME driver (checked in the pinned 0.289 source):

- The region letter is printed on the program ROM labels: J = Japan, U = USA,
  E = "ETC (World and Euro)". In these sets only `03`/`04` carry it.
- `mshvsf` (Europe 970625) and `mshvsfu1` (USA 970625) differ only in `03`/`04`.
- `mshvsfu` (USA 970827) also changes `mvs.05`; Brazil 970827 shares `mvs.05d`.

No source documents a text change between revisions, or whether the European
English matches the US English.

Working conclusions until captures settle them:

- The three sets **contain** the same Latin text (`EXP-0029`). Do not assume they
  **display** the same quotes, characters, or lines.
- An English line missing from the US or European set is not evidence that no
  official English exists. For the secret characters (RC-3), the English sets may
  simply have no unique line.
- If RC-2 holds, official English for Norimaro's win quotes exists in the US and
  European ROMs even though he is not normally selectable there (RC-1). If RC-3
  holds, the secret characters' unique quotes have **no** official English
  counterpart. Both are `SPECIAL-001` work.
- If RC-7 holds, a language setting may show other languages from the same set.
  Each capture must record the language setting as well as the set.
- Norimaro, secret characters, and endings are out of scope until their gated
  tasks (`SPECIAL-001` for M9, `END-001` for M6). `REF-008` only records these
  claims; it does not extract, translate, or modify that content.

## Rules

- Only hashes, set names, member names, CRCs, and other factual metadata are
  committed. Wording is committed only as a transcription with capture provenance.
- Record the exact MAME build or commit, audit output, command line, settings,
  route, and screenshot hashes for every capture.
- The US arcade revision distinction (`mshvsfu` versus `mshvsfu1`) still applies;
  see `../arcade_us/README.md`. The local US set is not `mshvsfu1`.
