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
  list it as a required ROM, so a stock MAME 0.289 should refuse to run these
  sets as supplied. That is expected, not yet observed: no MAME build is installed
  locally. A legal key file is a prerequisite for any arcade capture.

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
  byte order is swapped relative to 68000 memory. Whether quote text can be read
  from the raw members is **UNKNOWN** and needs its own experiment.
- Which members hold text, and how it is encoded, is **UNKNOWN**. Do not infer it
  from member names, from shared CRCs, or from other CPS-II games.

## What They Are For

1. **Exact English quotes.** The US and European sets are expected to display the
   official English post-fight text (`REF-004`). Wording counts as evidence only
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
"Regional Arcade Content Claims".

| ID | Claim | Source (reliability) | Matters for |
| --- | --- | --- | --- |
| RC-1 | Norimaro is selectable only in Japan. Elsewhere his select-screen slot shows the game logo. | Wikipedia, citing GameSpot (1998) and GamesRadar (2011) (secondary); RQ87 fan site | The user's report |
| RC-2 | Norimaro's data is still in the US and European ROMs, and his win quotes **were translated** into English. His US ending is untranslated and reuses Dan's text. | RQ87 fan site (undated) | Partly contradicts "JP only" |
| RC-3 | The six secret characters (Armored Spider-Man, Mephisto, U.S. Agent, Dark Sakura, Mech-Zangief, Shadow) have unique win quotes only in Japan. Elsewhere they reuse their base characters' quotes. | TCRF arcade page, **search snippet only** (unread; the page shows a bot check) | Supports the user's report |
| RC-4 | Dark Sakura, Shadow, and Mech-Zangief have real endings in Japan. The US shows a generic "Congratulations" screen. | RQ87 fan site; TCRF snippet agrees | Endings (M6+, out of scope) |
| RC-5 | Some names differ by region: Mech-Gouki becomes Cyber-Akuma, one of Bison's hyper names changes, and "variable" becomes "cross-over". | RQ87 fan site; snippets | Terminology |
| RC-6 | In Japan, Norimaro's availability may depend on the coin setting. | RQ87 FAQ (author unsure) | Capture routes |

Regional facts from the primary MAME driver (checked in the pinned 0.289 source):

- The region letter is printed on the program ROM labels: J = Japan, U = USA,
  E = "ETC (World and Euro)". In these sets only `03`/`04` carry it.
- `mshvsf` (Europe 970625) and `mshvsfu1` (USA 970625) differ only in `03`/`04`.
- `mshvsfu` (USA 970827) also changes `mvs.05`; Brazil 970827 shares `mvs.05d`.

No source documents a text change between revisions, or whether the European
English matches the US English.

Working conclusions until captures settle them:

- Do not assume the three sets contain the same quotes, characters, or lines.
- An English line missing from the US or European set is not evidence that no
  official English exists. For the secret characters (RC-3), the English sets may
  simply have no unique line.
- If RC-2 holds, official English for Norimaro's win quotes may exist in non-JP
  ROMs even though he is not selectable there. Finding it is `SPECIAL-001` work.
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
