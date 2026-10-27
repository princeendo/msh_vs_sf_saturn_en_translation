# EXP-0088: The screens of story records 39 and 42-47

Task: TXT-003
Status: DONE
Confidence: CONFIRMED (records 42-44: arcade trace with a forced CPU team);
SUPPORTED (Saturn screens by matching code); HYPOTHESIS (record 39's arcade
scene, records 45-47 unused)

## Observation

`EXP-0085` found three more readers of the story table besides the post-loss
line, and none for records 45-47:

- **Record 39:** arcade `0x0A06A8` → `0x0705E0`. Other regions show English
  "MSH VS STREET FIGHTER / COMING SOON".
- **Records 42-44:** `0x07059C`/`0x0705A0`/`0x0705A4` (index 0-2, base
  `0x214624`). They are called from three character routines when
  `(-$3800,A5)` ≥ 4. Other regions show "I've finally tracked you /
  down!Now,you're mine!" (`0x2243C0`, three times).

## Hypothesis

Records 42-44 are shown in the intros of the secret characters whose code
calls them. Their condition picks the CPU's side.

## Controlled Change

No game data in the trials:
- arcade: MAME `force16` writes to the CPU team words;
- Saturn: agent writes to the same words in a play state.

The build then gains records 42-43 (user decision below).

## Inputs and Provenance

- **MAME:** 0.289, `mshvsfj` and `mshvsfu` (`references/mshvsf/arcade/README.md`);
  default EEPROM; timeline `tools/reference/mame_timeline.lua`.
- **Saturn:** release US image `0f430c0a…` and the play-check states of
  `EXP-0087` (`local/txt002/play2/rec/states`).

## Procedure and Actual Result

### Team words

- **Arcade:** after picking Dhalsim then Ryu, `0xFF48B0` = `0018 0012`
  (character × 2), and the CPU team follows at `0xFF48B4` (`0020 0024`,
  Sakura and Dan, on the VS screen at frame 6,950).
- **Saturn:** the same layout at `0x060F48B0` (`r11` = `0x060F8000`). In the
  play-check states, player `0012 0014` (Ryu, Ken) and CPU `0010 001A`
  (Blackheart, Zangief).
- **Phase byte:** `0x060F4800`, the Saturn copy of `(-$3800,A5)`, is a game
  phase: 8 in fights, `0x0A` after a KO, `0x12` on CONTINUE?.

### Records 42-44 in the arcade (forced CPU team; reads logged)

| Set | CPU point | Read | Screen |
| --- | --- | --- | --- |
| `mshvsfj` | Shadow (`0x2C`) | record 42 at frame 7,041 (PC `0x0706FE`) | Vega steps in during the intro; a top box shows 行け！シャドウ。実戦テストだ！シャドルーの力を見せてやれ！ |
| `mshvsfj` | Metal Zangief (`0x28`) | record 43 at 7,041 | Vega; 行け！試作改造人間メカザンギエフ！実戦テストだ！！ |
| `mshvsfj` | Dark Sakura (`0x2A`) | record 44 at 6,995 | a top box with a row of dots, no Vega |
| `mshvsfu` | Shadow | English record 25 at 7,041 | Vega; "I've finally tracked you / down!Now,you're mine!" |
| `mshvsfu` | Metal Zangief | English record 26 at 7,041 | the same line |

- **The player's own secret team shows nothing:** with Shadow and Metal
  Zangief forced into the player's team (`0xFF48B0` = `002C 0028`), nothing
  was read and no box appeared. That matches the Saturn session of
  `EXP-0078`, where the user played them: no box at the intro.
- **So:** records 42-44 are shown when the CPU fields those characters.
- **Contact sheets:**
  - `local/txt003/sheet_secret.png`;
  - `local/txt003/arc_cpu/sheet.png` (Shadow, Japanese).

### The Saturn's matching code

- **Callers:** the three entries are `0x060AF5A0`/`0x060AF5A8`/`0x060AF5B0`
  (index 0/1/2, base literal `0x060AF604` = record 42). They are called from
  the decoded character files, named by slot in hex:
  - `MC16.PAC` (slot 22, Shadow) → record 42;
  - `MC14.PAC` (slot 20, Metal Zangief) → record 43;
  - `MC15.PAC` (slot 21, Dark Sakura) → record 44.
- **Shadow's condition** (`MC16` decoded `0x11BE`-`0x11FA`):
  - phase byte `@(0xC800 + r11)` ≥ 4;
  - character byte `@(3,r12)` = 0 (the CPU side);
  - and, new on the Saturn, byte `0x0601801C` = 0. It read 0 in every
    play-check state.
- **No Saturn trial:** writing the CPU team words in a play state crashed
  the load into the BIOS menu, with Dan and Sakura as well. Writing the
  original team back loaded normally. The Saturn fixes the opponent's files
  earlier than the last state before the VS screen, and the earlier states
  wait forever on the mode select without a player.

### Record 39

- **Arcade only:** its arcade reader (`0x0A067C`-`0x0A06C4`) sits in a
  scene script that loads graphics and palettes. It was not read in 60,000
  frames of attract mode (`EXP-0085`).
- **No Saturn reader:** no file on the Saturn disc, raw or decoded, holds
  record 39's address. On the Saturn, record 39 is shown only as slot 23's
  post-loss line (base + slot).

### Records 45-47

- No pointer to them exists in the arcade's decrypted code or in any Saturn
  file.
- The table is indexed only as hints (0-15), post-loss lines (16 + slot,
  slots 0-25) and Vega's orders (42 + 0-2), so nothing reaches 45-47.

### Build (user decision 2026-10-27: faithful translations)

- `--story-lines` now builds records 16-43; records 42-43 take the draft
  translations of Vega's orders.
- Record 44 (dots) and records 45-47 are not built.

- **Specs:** Saturn names `91c62f7b…`, American names `86957f2a…`.
- **References:** both rebaselined; nine of nine pass.

| Variant | Track 01 | xdelta | `.ssp` |
| --- | --- | --- | --- |
| Saturn names | `de8861da75ba78f3d89f11dbdd3bb5507c6e5ae9819d16c62a0c3a3bd08edadc` | 644,312 bytes, `4535ce19…` | 561,714 bytes, `b1d1e65a…` |
| American names | `39ae78b3d848df753bf8a981778b0b56712201c0832149249e45d331b58d010e` | 645,074 bytes, `d65695b6…` | 561,872 bytes, `7d6f98a5…` |

- `saturn-patcher-egui` gives both track 01 hashes.
- **Rendering on the Saturn (post-loss trick of `EXP-0087`):**
  - record 42 shows "Go, Shadow! This is a combat test! / Show them the
    power of Shadaloo!!" (`r42.png` `47e66813…`);
  - record 43 shows "Go forth, prototype Metal Zangief! / This is a combat
    test!!" (`r43.png` `86379b3c…`).

## Conclusion

- **CONFIRMED (arcade):** Vega's orders (records 42-43) and Dark Sakura's
  dots (44) appear in the intro when the CPU fields Shadow, Metal Zangief or
  Dark Sakura.
- **SUPPORTED (Saturn):** the same code and conditions, plus the flag at
  `0x0601801C`.
- **HYPOTHESIS:** record 39's extra screen is an arcade-only scene, and
  records 45-47 are unused.

## Uncertainty and Alternatives

- **When does the CPU field these characters in normal play?** Not found,
  in the arcade or on the Saturn. If never, records 42-43 are only ever
  seen when forced.
- **What `0x0601801C` means** is unknown.
- **The Saturn intro box was not seen;** the rendering of records 42-43 is
  checked through the post-loss trick below.

## Reproduction

```bash
# Arcade: CPU team forced to Shadow (point) + Metal Zangief (timeline verbs):
#   4500 force16 0xff48b4 0x2c ; 4500 force16 0xff48b6 0x28 ;
#   1 logreads 0x2139ac 0x2147eb <log> ; snapshots 6900-7600
# Saturn rendering of records 42-43 (post-loss trick):
RECORDS="42 43" bash research/experiments/EXP-0087/verify_story.sh
```
