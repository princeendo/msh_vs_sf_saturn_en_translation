# XvSF Arcade

Permitted provenance notes belong here only when a specific MSHvSF experiment needs
this reference. No structure transfers automatically between releases.

## Local Sets (`REF-011`, 2026-10-24)

Eleven user-supplied zips were copied unchanged to the ignored
`local/arcade_roms/xmvsf/`. Per-zip identity, size, and SHA-256 are in
[`manifest.json`](manifest.json); every member matches MAME 0.289 by CRC-32 and
SHA-1.

- They use older MAME set names: `xmvsfar1.zip` is 0.289's `xmvsfar2`,
  `xmvsfj.zip` is `xmvsfjr2`, `xmvsfjr1.zip` is `xmvsfjr3`, and `xmvsfjr2.zip` is
  `xmvsfjr4`.
- `xmvsfur1.zip` matches `xmvsfur1`, but its members are labelled `xvsu.03h`/`04h`
  where MAME uses `03i`/`04i` (same SHA-1).
- MAME 0.289's current `xmvsfj` (Japan 970113) is not held.

### Keys and MAME Use (2026-10-24)

The user added six keys. They were copied to the ignored
`local/arcade_roms/xmvsf/keys/`, and each matches MAME 0.289 by CRC-32 and SHA-1:

| Key | CRC-32 | Used by (MAME 0.289) |
| --- | --- | --- |
| `xmvsf.key` | `d5c07311` | `xmvsf`, `xmvsfr1` |
| `xmvsfa.key` | `44941468` | `xmvsfa`, `xmvsfar1`-`xmvsfar3` |
| `xmvsfh.key` | `f632a36b` | `xmvsfh` |
| `xmvsfj.key` | `87576cda` | `xmvsfj`, `xmvsfjr1`-`xmvsfjr4` |
| `xmvsfu.key` | `eca13458` | `xmvsfu`, `xmvsfur1`, `xmvsfur2` |
| `phoenix.key` | `2cf772b0` | bootleg "Phoenix" sets only (for example `xmvsfu1d`); not needed |

- Still missing: `xmvsfb.key` (Brazil).
- MAME looks sets up by name, so `local/arcade_roms/xmvsf_mame0289/` holds copies
  of the zips under 0.289 names. The mapping is `xmvsfar1`→`xmvsfar2`,
  `xmvsfj`→`xmvsfjr2`, `xmvsfjr1`→`xmvsfjr3`, and `xmvsfjr2`→`xmvsfjr4`, with keys
  in per-set folders.
- `mame -rompath "local/arcade_roms/xmvsf_mame0289;local/arcade_roms/mshvsf"
  -verifyroms "xmvsf*"` reports **10 of 11 OK**; only `xmvsfb` fails, for its key.
  (`qsound.zip` is shared from the MSHvSF folder.)
- `xmvsfu` and `xmvsfjr2` boot headless to the title and attract screens. Frame
  3000 snapshot SHA-256 values: `xmvsfu`
  `e8a8ab8ec057ee6659348d5c2c869c0f84752c0b99b6f1a360314d092bfb9ba3`, `xmvsfjr2`
  `e19f6bae78b185c906788124abcc6a1be0f8c77b8b3fdfec60759f08ae81f1fb`.
- XvSF is a reference only (`AGENTS.md` rules 13 and 25). Nothing here is an MSHvSF
  fact.
