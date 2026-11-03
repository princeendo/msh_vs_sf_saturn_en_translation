# 0.2.0: EXTRA OPTIONS, one patch, English warning screens

An English translation patch for the Japanese Sega Saturn release of
**Marvel Super Heroes vs. Street Fighter**. Only track 01 changes. You
supply your own disc image; these files contain no game data.

## Downloads

- `mshvsf_saturn_en_0.2.0_xdelta.zip`: an xdelta3 patch for track 01.
- `mshvsf_saturn_en_0.2.0_ssp.zip`: a Sega Saturn Patcher (`.ssp`) file.

0.2.0 is **one patch** (0.1.0 had two name variants): the names are now a
switch in the game's options. Each zip has a `README.txt` with every
expected hash:

| Patch | Patched track 01 SHA-256 |
| --- | --- |
| American names by default; Saturn names and grammar fixes switchable | `3812bdc196aa5b6b1b0db7f7e9f0db2f1948803f4581d055fdae0615fbd6dbf2` |

The untouched track 01 must have SHA-256
`8274307f9562d2da7fb7be0f5f306846edb74afde5913324bef04938ed3214f9`.
Step-by-step instructions: [release/README.md](https://github.com/princeendo/msh_vs_sf_saturn_en_translation/blob/main/release/README.md).

## New in 0.2.0

- **EXTRA OPTIONS:** a new OPTION MODE row (A or C) opens a sub-menu with
  four switches, saved with your other options:

  | Switch | Values | Default |
  | --- | --- | --- |
  | **BOSS FIGHT** | UNLOCKED: MECH-GOUKI NOW!! / CYBER-AKUMA NOW!! from the start; LOCKED: the original Survival-clear lock | UNLOCKED |
  | **COMBO GAUGE** | NORMAL, or FULL (keeps the combo gauge refilled). The game's own option, which it hides until an unlock | NORMAL |
  | **NAMES** | AMERICAN (Bison, Akuma, Cyber Akuma) or SATURN (Vega, Gouki, Mech-Gouki), in the text, life bars, banners, VS screen, sound test and the announcer's calls | AMERICAN |
  | **GRAMMAR FIXES** | OFF: the official English as written; ON: light corrections (five CONTINUE? hint pages and 21 lines of win quotes, partner lines and endings). The corrections are new text, not official | OFF |

- **VS POWER GAUGE** is spelled so (the game had VS POWER GAGE).
- **Warning screens:** the five boot-time warnings (no 4 MB RAM cartridge or
  one not inserted correctly, and backup memory not formatted, unreadable or
  full) are a new English translation.

Everything from 0.1.0 is kept: the official US arcade English for win
quotes, endings, bosses, secret characters and CONTINUE? hints; new
translations where only Japanese exists; the US arcade's attract captions
and lettering.

## Known limits

- **Still Japanese:**
  - the attract-mode Norimaro screen, whose brush lettering is art;
  - text for characters and slots that normal play does not reach.
- **The switches and the endings:** NAMES and GRAMMAR FIXES were checked in
  menus, fights and the stage-7 exchanges, in Mednafen and on a real Saturn,
  but no test session reached an ending. The ending text uses the same
  mechanism.
- **The attract demo** may show the disc's names (American) while NAMES is
  SATURN; menus and play follow the switch.
- **Dan's last ending page** is blank, as in the official English.
- **Long names in the post-boss dialogue** (Captain America) sit right of
  centre.
- **Patchers:**
  - the official Sega Saturn Patcher rebuilds the disc, so its track 01
    differs in the disc-length field only;
  - graphical xdelta patchers are untested.
