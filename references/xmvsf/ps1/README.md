# XvSF PlayStation

Permitted provenance notes belong here only for a documented research question. Do
not assume PlayStation and Saturn implementations are structurally equivalent.

## Local Images (`REF-011`, 2026-10-24)

Extracted unchanged from user-supplied `.7z` archives into ignored folders:

| Folder | File | Size | SHA-256 | Identity |
| --- | --- | ---: | --- | --- |
| `local/disc_images/xmvsf_ps1_us/` | `X-Men vs. Street Fighter (USA).bin` | 392393568 | `13e66a3e739cfdfca3801264b1aa7bc90136635becd71caa150056fa80d8b519` | **CONFIRMED**: MAME 0.289 `psx.xml` `xmvsf` (CRC `02cdbe88`, SHA-1 `c04bf744…b656856a`) |
| `local/disc_images/xmvsf_ps1_jp_ex/` | `X-Men vs. Street Fighter - EX Edition (Japan).bin` | 392762832 | `b1f0049f844e51b927c0c0e33ad9e09d9f8da3b9946481cc4c7367fce868b107` | **UNKNOWN**: not in MAME 0.289 `psx.xml` (CRC `7e7d62f4`, SHA-1 `3a5d5503…3b636692`); identity as named only |

Source archives: `X-Men vs. Street Fighter (USA)-PS1.7z` (212,931,976 bytes;
SHA-256 `42daa9e8…ab1a21e`) and `X-Men vs. Street Fighter - EX Edition
(Japan).7z` (213,045,606 bytes; SHA-256 `991f3ee7…bf88f62`). The `.cue` files are
kept beside each `.bin`.
