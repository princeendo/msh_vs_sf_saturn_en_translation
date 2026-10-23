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

Region labels are as supplied by the user. They are not yet audited against the
pinned MAME catalog; that audit is `REF-008`.

| Filename | Region (as supplied) | Size (bytes) | SHA-256 |
| --- | --- | ---: | --- |
| `mshvsf.zip` | Europe | 21896860 | `5fae509a111b7403243956322c642e24ad1811630f54775bed761095f956385d` |
| `mshvsfu.zip` | USA | 21897435 | `32f4cb993a55eeff1397b24df5e9b2f14dd5baf6955a6fd69c77a49327794eee` |
| `mshvsfj.zip` | Japan | 21897527 | `3f5418276843fa2c5747c53d4c892016c2da2b7acd0759eccb9c900dfae0d19c` |

Zip SHA-256 values identify these local archives only. Archive metadata can differ
between sets with identical ROMs, so release identity must come from per-member
hashes.

### Member Observations (`unzip -v`, 2026-10-23)

- Each zip has 20 members totalling 46,399,488 bytes, so each looks like a
  self-contained (non-merged) set. Whether MAME needs any other file, such as a
  CPS-II decryption key, is untested.
- Members `mvs.01`, `mvs.02`, `mvs.06a`-`mvs.10b`, and `mvs.11m`-`mvs.20m` have
  the same names, sizes, and CRC-32 values in all three sets.
- The sets differ only in these members:

| Set | Region-specific members (CRC-32) |
| --- | --- |
| `mshvsf` | `mvse.03f` (`b72dc199`), `mvse.04f` (`6ef799f9`), `mvs.05a` (`1a5de0cb`) |
| `mshvsfu` | `mvsu.03g` (`0664ab15`), `mvsu.04g` (`97e060ee`), `mvs.05d` (`921fc542`) |
| `mshvsfj` | `mvsj.03i` (`d8cbb691`), `mvsj.04i` (`32741ace`), `mvs.05h` (`77870dc3`) |

- The `mvsu.03g` and `mvsu.04g` CRC-32 values match the pinned MAME 0.289
  `mshvsfu` (*USA 970827*) fingerprints in `docs/references.md`. This is
  **SUPPORTED** only: it is a CRC-32 comparison of two members, not a full audit
  with SHA-1 values.
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
secret characters that the English sets may lack. This is a **HYPOTHESIS**.
Nothing here has tested it. Until it is tested:

- Do not assume the three sets contain the same quotes, characters, or lines.
- An English line missing from the US or European set is not evidence that no
  official English exists. It may only mean that the line was never in that
  release.
- Norimaro and other special cases are out of scope until `SPECIAL-001` (M9) is
  authorized. `REF-008` may record which sets appear to contain such content, but
  it may not translate, extract, or modify it.

## Rules

- Only hashes, set names, member names, CRCs, and other factual metadata are
  committed. Wording is committed only as a transcription with capture provenance.
- Record the exact MAME build or commit, audit output, command line, settings,
  route, and screenshot hashes for every capture.
- The US arcade revision distinction (`mshvsfu` versus `mshvsfu1`) still applies;
  see `../arcade_us/README.md`. The local US set is not `mshvsfu1`.
