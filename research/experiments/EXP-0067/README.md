# EXP-0067: US arcade oracle for the attract-mode captions

Task: UI-003 (oracle)
Status: DONE
Confidence: CONFIRMED (both arcade sets captured; pairs made by sequence
position)

## Observation

`EXP-0066`: the Saturn attract mode shows four Japanese captions per cycle:
- ヴァリアブル / ヒーロー / バトル;
- 第2弾!!;
- 解き放て! / 友情パワー;
- 広がれ!! / ヒーロー / ワールド.

`UI-003` takes the US releases as the reference.

## Hypothesis

The Saturn captions come from the arcade. The US arcade `mshvsfu` shows
English captions in the same places, and the Japanese arcade `mshvsfj` shows
the Saturn's Japanese ones, so the two can be paired by position in the
cycle.

## Controlled Change

None. MAME runs of both sets without input, with the same timeline.

## Prediction

At each place where `mshvsfj` shows a Japanese caption, `mshvsfu` shows an
English one.

## Inputs and Provenance

- `local/arcade_roms/mshvsf/mshvsfu.zip` (SHA-256 `32f4cb99…`) and
  `mshvsfj.zip` (`3f541827…`). Identities are in
  `references/mshvsf/arcade/README.md`.
- MAME 0.289 (Homebrew), with `tools/reference/mame_timeline.lua`.

## Tools and Environment

```bash
MAME_TIMELINE=local/ui003/mame/attract.timeline mame mshvsfu -rompath local/arcade_roms/mshvsf -video none -sound none -nothrottle -skip_gameinfo -nomouse -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram -snapshot_directory local/ui003/mame/snap -homepath local/mame_arcade -autoboot_script tools/reference/mame_timeline.lua
```

- The same command runs `mshvsfj` with `-snapshot_directory
  local/ui003/mame_j/snap`. The timeline takes a snapshot every 15 frames
  for 15,000 frames.
- Fine timelines take a snapshot every 3 frames: frames 1150-1450 for
  `mshvsfj` and 1480-1800 for `mshvsfu`.

## Procedure

1. Capture both sets. Detect mostly black frames with white, red or yellow
   text.
2. Order each set's captions by their neighbouring screens: the MARVEL logo,
   the Ryu/Cyclops cut, the title, the VS animation and the red silhouettes.
3. Fine-capture the first caption stretch of each set.

## Actual Result

The sequences match screen for screen, except for the first caption
stretch:

| Position in the cycle | `mshvsfj` (and Saturn) | `mshvsfu` |
| --- | --- | --- |
| After the MARVEL logo, before the Ryu/Cyclops cut and the title | ヴァリアブル / ヒーロー / バトル (white, frames 1198-1225), then **第2弾!!** (red, 1234-1249) | **LEGENDARY / HEROES / UNITE AGAIN!!** (yellow, one caption, 1522-1573) |
| After the title cycle | 解き放て! / 友情パワー (`f01695`) | **AMAZING / TEAM BATTLES!** (`f02025`) |
| Next, before the VS animation | 広がれ!! / ヒーロー / ワールド (`f02025`) | **NEW HEROES / JOIN / THE FIGHT!!** (`f02355`) |

- The US captions are three to four lines of yellow-orange outlined capitals,
  centred, the style of the arcade's large letters. The Japanese captions are
  plain white (or red) gothic.
- The US set has no Norimaro screen; the Japanese set does.
- Evidence (local): `local/ui003/arcade_first_caption.png` (`40e699ab…`) and
  `arcade_later_captions.png` (`1f21cb78…`).

## Conclusion

**CONFIRMED** (by sequence position): the US arcade replaces:
- the two-caption opening (ヴァリアブル ヒーロー バトル, 第2弾!!) with one
  caption, LEGENDARY HEROES UNITE AGAIN!!;
- 解き放て! 友情パワー with AMAZING TEAM BATTLES!;
- 広がれ!! ヒーロー ワールド with NEW HEROES JOIN THE FIGHT!!.

## Uncertainty and Alternatives

- The PS1 US attract mode is not recorded. The arcade is the primary oracle
  for these captions (`UI-003` lists both).
- Mapping two Japanese captions to one US caption needs a decision. One
  option is a Saturn that shows LEGENDARY HEROES UNITE AGAIN!! over both
  slots, or splits it across them. That needs the user's choice once the
  `MVSOP` format is decoded.
- Art source options for later:
  - the Saturn's own large letter glyphs (the win-banner font `0x2E0`+,
    similar in style);
  - the arcade's caption graphics (import; needs the user's approval and
    provenance);
  - the PS1 US art.

## Reproduction

The commands are under Tools and Environment. Timelines are generated as
`<frame> snap` lines (see `tools/reference/mame_timeline.lua`).
