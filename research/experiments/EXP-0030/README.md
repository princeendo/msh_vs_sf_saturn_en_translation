# EXP-0030: Arcade Win Quotes on Screen Match the Decoded Table

Task: REF-010
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0029` decoded a win-quote table from raw ROM data at program `0x20C014`. It
has 26 slots per language, and a name list in `mvs.07b` suggests Ryu is slot 9.
ROM data alone does not show which lines are displayed, or for whom.

## Hypothesis

The win-quote screen draws its two lines directly from that table, and slot `n`
belongs to the `n`-th name in the list. In particular, Ryu's quotes are slot 9,
block `0x21BA20`.

## Controlled Change

None to any game file. Only the scripted inputs vary: the start offset and end
frame of a Hadouken loop. That changes the fight outcome and the quote choice.

## Prediction

1. Every displayed quote equals one decoded 8-quote entry line for line, including
   the padding that centers it.
2. While a quote is shown, work RAM holds that entry's ROM address.
3. The speaker's slot matches the name list.
4. The European set displays the same entry identically.

## Inputs and Provenance

- `mshvsfu.zip` and `mshvsf.zip`, plus their keys and `qsound.zip`. The audit and
  hashes are in `references/mshvsf/arcade/README.md`.
- Default EEPROM, created on first boot in the ignored
  `local/mame_arcade/nvram/`. The coin setting it gives is 2 coins per credit.

## Tools and Environment

- MAME 0.289 (Homebrew bottle; binary SHA-256 `6d40df87…029636d9`). Run headless
  with `-video none -sound none -nothrottle -skip_gameinfo -nomouse`, and
  `-cfg_directory`, `-nvram_directory`, `-snapshot_directory`, and `-homepath`
  under `local/mame_arcade/`.
- `tools/reference/mame_timeline.lua`: replays frame-timed inputs, snapshots, and
  memory dumps (`MAME_TIMELINE` env var).
- `tools/reference/arcade_route.py`: writes the route timeline.
- `tools/reference/cps2_text.py`: provides the decoded table.

## Procedure

1. Explore the route with snapshot contact sheets: coin (two needed), start, Ryu,
   and a second confirm, which picks Ken. Mode and Speed time out (Easy is shown
   on the HUD), and the opponents vary by run.
2. P1 Hadouken loop: Down 10 frames; Right 10 frames from +5; Button 3 for
   4 frames from +12; repeated every 36 frames from frame `5200 + offset`.
3. Snapshot around the win screen, and dump the program space at
   `0xFF2498`-`0xFF24A3` (and all of `0xFF0000`-`0xFFFFFF` once).
4. Compare each displayed quote with the decoded entry the RAM pointer names.

## Actual Result

**Ryu (slot 9), US set.** Final captures were regenerated with
`arcade_route.py` and reproduced the exploratory snapshots bit for bit:

| Run | Route | Frame | `0xFF249C` | Entry | Snapshot SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| `us_q6` | `mshvsfu`, offset 0, loop end 10300 | 10850 | `0x0021BC78` | slot 9, quote 6 | `f75015c9611ed7936a81e65200730d538e988d38d0d553583f79fc2fed91dfa6` |
| `us_q7` | `mshvsfu`, offset 6, loop end 10300 | 8600 | `0x0021BCDC` | slot 9, quote 7 | `1459c6a6b83b889be283f367419cdf8d192d7af969fdc9496cd962f3f49cf9d1` |
| `eu_q6` | `mshvsf`, offset 6, loop end 9300 | 9560 | `0x0021BC78` | slot 9, quote 6 | `211ffe9a7f6c6062528abf03864b0729d9db0222ab33bed7c0126a725cfa956f` |

- The left portrait is Ryu, with Ken beside him. Each displayed quote matches its
  decoded entry line for line. Entry `n` sits at `0x21BA20 + n × 0x64`.
- Line 1 of quote 6 has 2 leading spaces and line 2 has 7. On screen, the 5-cell
  difference measures about 59 px at a pitch of about 11.7 px, so the padding is
  drawn literally.
- In the pre-screen dumps (frames 10700 and 9400), `0xFF249C` is 0.
- The full WRAM dump at frame 10850 also holds the slot 9 block base `0x0021BA20`
  at `0xFF9E4A`. No copy of the text codes is in WRAM; the text is read from ROM.
- Quote-box pixels (crop 320×30 at 32,174) are identical in `us_q6` and `eu_q6`:
  RGB SHA-256 prefix `ffb8cdabdcfd321d`.

**Other winners** (exploratory runs; Ryu lost or another character won). Each
quote matched its decoded entry, and in every case the left portrait is the
name-list character for that slot:

| Set | Left portrait | Pointer | Entry |
| --- | --- | --- | --- |
| `mshvsfu` | Shuma-Gorath | `0x0021B05C` | slot 5, quote 7 |
| `mshvsfu` | Shuma-Gorath | `0x0021AF30` | slot 5, quote 4 |
| `mshvsfu` | Omega Red | (no dump) | slot 6, quote 0 (only match in the table) |
| `mshvsfu` | Chun-Li | `0x0021C128` | slot 11, quote 2 |
| `mshvsfu` | Zangief | `0x0021C768` | slot 13, quote 2 |
| `mshvsfu` | Zangief | `0x0021C894` | slot 13, quote 5 |
| `mshvsfu` | Sakura | `0x0021D064` | slot 16, quote 1 |
| `mshvsf` | Dhalsim | `0x0021C63C` | slot 12, quote 7 |

Also seen: after a lost match, the European continue screen's hint line comes from
`0x223F74`, which is inside the decoded text area.

## Conclusion

**CONFIRMED** (predictions 1-4, reproducible):

- The arcade win-quote screen draws from the `EXP-0029` table, centering padding
  included.
- While a quote is shown, `0xFF249C` holds the address of the entry displayed.
- Slots 5, 6, 9, 11, 12, 13, and 16 match the name list (Shuma-Gorath, Omega Red,
  Ryu, Chun-Li, Dhalsim, Zangief, Sakura).
- Ryu's quotes are slot 9 (`0x21BA20`); quotes 6 and 7 were seen on screen.
- The European set shows quote 6 pixel-identically to the US set.

The other 19 slots stay **SUPPORTED** (from the name list and sharing pattern),
not observed.

## Uncertainty and Alternatives

- Only 2 of Ryu's 8 quotes were observed on screen. The other 6 rest on the
  confirmed layout, not on direct observation.
- How quotes are chosen is not established. Changing the loop's offset or end
  frame changed the choice, so it depends on timing or state.
- **HYPOTHESIS:** inputs held when a quote screen begins skip it. In two runs the
  pointer was set while the loop was still running, and no quote screen appeared.
  When the loop ended earlier, the screen appeared.
- The language setting was not changed; all captures are English. Spanish and
  Portuguese display (RC-7) is untested.
- The slot-9 base sits at `0xFF9E4A`, and the Saturn caption structure is at
  `0x060F9E4A` (`EXP-0027`). The matching low address is noted only as a
  coincidence. Arcade and Saturn structures are not assumed to be related.

## Reproduction

```bash
./invenv.sh python -m tools.reference.arcade_route --offset 0 --loop-end 10300 --snap-start 10700 --snap-end 10900 --snap-every 150 --dump-prefix local/mame_arcade/ref010/final/us_q6 > local/mame_arcade/ref010/final/us_q6.timeline
```

```bash
MAME_TIMELINE=local/mame_arcade/ref010/final/us_q6.timeline mame mshvsfu -rompath local/arcade_roms/mshvsf -video none -sound none -nothrottle -skip_gameinfo -nomouse -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram -snapshot_directory local/mame_arcade/ref010/final/snap_us_q6 -homepath local/mame_arcade -autoboot_script tools/reference/mame_timeline.lua
```

For `us_q7`, use `--offset 6 --snap-start 8600 --snap-end 8800 --snap-every 120`.
For `eu_q6`, use set `mshvsf` with `--offset 6 --loop-end 9300 --snap-start 9400
--snap-end 9600 --snap-every 160`. Compare the snapshot hashes above, and read
bytes 4-7 of each `*_f*.bin` dump for the pointer.
