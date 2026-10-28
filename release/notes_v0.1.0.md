# 0.1.0: first English release

An English translation patch for the Japanese Sega Saturn release of
**Marvel Super Heroes vs. Street Fighter**. Only track 01 changes. You
supply your own disc image; these files contain no game data.

## Downloads

- `mshvsf_saturn_en_0.1.0_xdelta.zip`: xdelta3 patches for track 01.
- `mshvsf_saturn_en_0.1.0_ssp.zip`: Sega Saturn Patcher (`.ssp`) files.

Each zip has both name variants and a `README.txt` with every expected hash:

| Variant | Patched track 01 SHA-256 |
| --- | --- |
| **American names (default):** Bison, Akuma, Cyber Akuma in the text, art and announcer's calls | `c6f1fbd0b85ed4f6f48a6d366cc4e39cb2c6dccfa001f06025de3473e979359b` |
| Saturn names: Vega, Gouki, Mech-Gouki, as in the Japanese release | `cdf366b3b3ac33a5e176f56a1585d3f1d9fcd9fd10ab1599bf3f87c859780858` |

The untouched track 01 must have SHA-256
`8274307f9562d2da7fb7be0f5f306846edb74afde5913324bef04938ed3214f9`.
Step-by-step instructions: [release/README.md](https://github.com/princeendo/msh_vs_sf_saturn_en_translation/blob/main/release/README.md).

## What is in English

- **Win quotes** for all 17 regular characters, in the official US arcade
  English.
- **Endings:** each character's ending pages and the post-boss partner
  dialogue, in the official US arcade English.
- **Bosses and secret characters:**
  - Apocalypse's and Mech-Gouki's win quotes, and Apocalypse's pre-fight
    exchanges, in official English;
  - Shadow, U.S. Agent, Mephisto, Metal Zangief, Dark Sakura and Norimaro,
    in official English where the arcade has it and new translations where
    it does not.
- **CONTINUE? hints** in the arcade's official English, paged as in the US
  arcade.
- **Rare post-loss lines and Vega's orders:** new translations. These
  exist only in Japanese.
- **Screens:**
  - the attract-mode captions are the US arcade's;
  - "JOIN IN", "EASY" and "TAUNT" replace the Japanese labels;
  - the title menu's boss fight is unlocked from the start.
- **Lettering:** captions use the US arcade's own narrow win-quote letters
  in gold.

New translations are marked as such in the README. Everything else is the
official US arcade English.

## Known limits

- **Still Japanese:**
  - the attract-mode Norimaro screen, whose brush lettering is art;
  - text for characters and slots that normal play does not reach.
- **Dan's last ending page** is blank, as in the official English.
- **Long names in the post-boss dialogue** (Captain America) sit right of
  centre.
- **Patchers:**
  - the official Sega Saturn Patcher rebuilds the disc, so its track 01
    differs in the disc-length field only;
  - graphical xdelta patchers are untested.
- **Play coverage:** six characters' win quotes and seven endings were seen
  in play. The rest were checked offline with the same pipeline.

This is a fan translation. Marvel Super Heroes vs. Street Fighter is ©
Capcom and Marvel.
