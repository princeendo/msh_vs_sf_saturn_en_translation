# XvSF Saturn JP

Permitted technical-reference notes belong here. XvSF is never modified, and its
offsets, encodings, functions, and renderer behavior are not MSHvSF facts.

`DOC-007` (2026-10-24) found no public XvSF Saturn translation or internals
research. The catalog and experiment ideas are in `docs/references.md`, "X-Men vs.
Street Fighter (Saturn) and Related Prior Art". XvSF requires the 4 MB cart.

## Local Image (`REF-011`, 2026-10-24)

The user supplied `X-Men vs. Street Fighter Saturn.rar` (140,795,025 bytes;
SHA-256 `2fc4199247b8571d52f2fa6138e82405dc1dd6209fd3c4b4cd0c018434d16de4`). It was
extracted unchanged into the ignored `local/disc_images/xmvsf_saturn_jp/`.

- **Not a preservation image.** It is a 2048-byte-sector data track
  (`X-Men vs. Street Fighter.iso`, 147,263,488 bytes, SHA-256
  `e2b65dfdbc81a295daf3ffd8f8a9a315909830912799fc49b98026d9c59acebc`) with a `.cue`
  that references 40 MP3 audio tracks. Its `readme.html` is a download-site
  redirect page.
- **Header.** The IP header reads product `T-1226G V1.002`, date `19970925`,
  area `J`. MAME 0.289 `saturn.xml` lists `T-1226G` as *X-Men vs. Street Fighter
  (Japan) (Doukonban)*. MAME identifies discs by CHD, so this rip cannot be
  hash-matched; identity is **SUPPORTED** by the header only.
- Use the data track only for read-only, question-driven comparison. Never modify
  it (`AGENTS.md` rule 25).
