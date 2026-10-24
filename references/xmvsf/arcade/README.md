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
- No XvSF `.key` files are held, so none of these sets runs in MAME yet. MAME
  0.289's current `xmvsfj` (Japan 970113) is not held.
- XvSF is a reference only (`AGENTS.md` rules 13 and 25). Nothing here is an MSHvSF
  fact.
