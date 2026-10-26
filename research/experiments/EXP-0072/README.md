# EXP-0072: PS1 US attract captions as UI-003's second oracle

Task: UI-003
Status: DONE
Confidence: CONFIRMED (cold-boot capture of the hash-matched US disc)

## Observation

`UI-003` asks for two oracles for the attract captions: the US arcade
(`EXP-0067`) and the PS1 US release. `EXP-0067` recorded only the arcade. The
user's question about the caption colours (2026-10-26) also needed an
independent colour reference.

## Hypothesis

The PS1 US release shows the same English attract captions as the US arcade,
with the same wording and colours.

## Controlled Change

None to any game. A cold boot of the PS1 US disc with no input.

## Prediction

Three English captions on black, in yellow-to-orange outlined capitals.

## Inputs and Provenance

- Disc: `local/disc_images/mshvsf_ps1_us/` (Redump 12632; identity in
  `references/mshvsf/ps1_us/README.md`).
- BIOS: `scph1001.bin`, supplied by the user on 2026-10-26, SHA-256
  `71af94d1e47a68c11e8fdb9f8368040601514a42a5a399cda48c7d3bff1e99d3`, MD5
  `924e392ed05558ffdb115408c263dccf` (`docs/mednafen.md`). Region: North
  America.

## Tools and Environment

Patched Mednafen 1.32.1 (agent build), PlayStation module, launched with
`-psx.bios_na scph1001.bin`; Python 3.12.13.

## Procedure

1. Cold boot; a screenshot every 15 frames for 12,000 frames
   (`local/ui003/ps1_us/shots/`, 800 shots).
2. Select frames that are mostly black with yellow, white or red text.
3. Count the caption colours in one frame per caption.

## Actual Result

- **Captions** (the cycle repeats about every 3,960 frames; first cycle shown):

  | Frame | Caption | SHA-256 |
  | --- | --- | --- |
  | `f003512` | LEGENDARY / HEROES / UNITE AGAIN!! | `1d8db29d…` |
  | `f003887` | AMAZING / TEAM BATTLES! | `2aa6c2a7…` |
  | `f004142` | NEW HEROES / JOIN / THE FIGHT!! | `c69aff67…` |

  The wording and line breaks equal the US arcade's (`EXP-0067`). Contact
  sheet: `local/ui003/ps1_us/caption_sheet.png` (`a75cb249…`).
- **Colours** (`f003512`, 400x240): purple (32,0,96) 4,095 px, yellow
  (240,240,0) 3,591 px, cyan (0,192,192) 3,159 px, then (240,224/208/192/176/
  160/144/128,0). As 4-bit channels these are `F206`, `FFF0`-`FF80` and
  `F0CC`: the arcade's caption colours and the Saturn win-banner colours
  that the fixed `EXP-0071` captions use, in the same frequency order.
- The PS1 attract mode has no Norimaro screen.

## Conclusion

**CONFIRMED:** the PS1 US release shows the arcade's three English captions
with the same wording and colour set. It supports the `EXP-0071` colours.

## Uncertainty and Alternatives

- The PS1 port's storage and rendering are not Saturn facts (rule 14); only
  the visible text and colours are used.
- The capture's colour values are Mednafen's 15-bit output, which is enough to
  compare 4-bit channels.

## Reproduction

Cold boot the US disc in Mednafen with `-psx.bios_na scph1001.bin`
(`MEDNAFEN_HOME=local/mednafen`) and wait about 3,500 frames for the first
caption. The capture used a scratch script that takes an agent screenshot
every 15 frames.
