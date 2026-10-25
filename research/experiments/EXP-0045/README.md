# EXP-0045: One Dialogue Block per Speaker (Whole Line Across the Pair)

Task: END-010 (layout revision, user request)
Status: DONE (2026-10-24)
Confidence: CONFIRMED

## Observation

`EXP-0044` split each English partner line at its line break across the two
Saturn boxes of its pair: "You are worthy" / "RYU." / "We shall meet again" /
"AKUMA.". The user asked for each line to appear whole in one block that lasts
as long as the two boxes together, giving two blocks instead of four.

In the `EXP-0039` and `EXP-0044` recordings, the box never closed between the
two records of a pair; only the text changed.

## Hypothesis

When both records of a pair hold identical text, nothing on screen changes at
the hand-over. The pair then reads as one block lasting both boxes' time. No
code change is needed.

## Controlled Change

- **T3 (RAM trial).** On the untouched image, from `ryu_ken_post_boss_ko.mcs`,
  copy record 36 (Ken's box 1, decoded `0xAB1C`) over record 37 (WRAM-L
  `0x0022AB68`). Take a screenshot every frame for frames 560-760, against a
  no-write control.
- **Build.** `official_endings.py` has a new `--dialogue-layout whole` (now the
  default): both records of a pair get the full two-line English text. `split`
  keeps the `EXP-0044` layout. Only `MC13.PAC` changes relative to the
  `EXP-0044` build.

## Prediction

- **T3:**
  - the control's box content changes exactly once, at the hand-over;
  - the duplicated run's box content never changes in the window;
  - there is no blank frame between the boxes in either run.
- **Build:** the dialogue shows two blocks of about 480 frames each, with the
  same total duration, followed by the unchanged pages.

## Inputs and Provenance

- **T3:** untouched image `8274307f…`; checkpoint `ryu_ken_post_boss_ko.mcs`
  (`18995e6d…`).
- **Build:**
  - spec `local/end010/spec/ryu_ending.json` (`1d978fe4…`, layout `whole`),
    regenerated from `mshvsfu.zip` and identical to the tested spec;
  - output `build/end010`, track 01
    `ba3fb3ce6f07fb28…`, manifest `a0980f43…`;
  - the `EXP-0044` split build was kept as `build/end010_split` (`b481a4c6…`).
- **Replay states,** saved during the `EXP-0044` cold-boot runs on the `end010`
  image, so they hold its font and name table:
  - `live2_ryu_ken/rec/states/f00007048.mcs` (`129462fe…`);
  - `live3_ryu_gouki/rec/states/f00023803.mcs` (`3e560229…`).

  Both are on the `STAGE-08` stage map, before `MC13` loads.

## Procedure

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --out local/end010/spec/ryu_ending.json
./invenv.sh python -m tools.text.caption_compiler local/end010/spec/ryu_ending.json \
  --out-dir build/end010
```

- **T3 and the replays** used one-off agent scripts:
  - load the state;
  - for T3, apply the write, then step one frame at a time with a screenshot
    each frame;
  - for the replays, write the boss vitality words to 0 from frame 300, then
    take a screenshot every 30 frames to frame 4,500.
- **Why a replay is valid here:** the font (`MEMFIX.PAC`), `ME.PAC`, and
  `MM.BIN` are byte-identical to the `EXP-0044` build. Only `MC13.PAC` differs,
  and it reloads from disc at the stage-8 transition (`EXP-0040`). So the state
  carries the right font and names, and the new image supplies the new
  dialogue.

## Actual Result

### T3: the hand-over is seamless

- **Control:** the box content changes exactly once, at frame 659.
  - Whole-frame hashes: frame 658 `6f33c2d2…`, frame 659 `d9e1fa21…`.
  - No blank or intermediate frame.
- **Duplicate:** the box content is constant for all 201 frames.
  - Frames 658 and 659 are both byte-identical to the control's frame 658
    (`6f33c2d2…`), so the whole screen is unchanged at the hand-over.

### Build

- All compiler checks are true, and the two image builds are identical.
- `MEMFIX.PAC`, `ME.PAC`, and `MM.BIN` are byte-identical to the `EXP-0044`
  build. `MC13.PAC` is spliced, with the declared length kept and 7 zero-fill
  bytes.
- **Regression:** `end010` was re-baselined to `ba3fb3ce…`. The previous
  `b481a4c6…` is kept under `previous`, with its reason. All five references
  pass.

### Replays on the new image, forced KO

| Team | Block 1 (frames 1440-1920) | Block 2 (frames 1950-2430) |
| --- | --- | --- |
| Ryu + Ken | "RYU," / "you're not bad." (`t01680` `084ef4cf…`) | "We shall meet again" / "KEN." (`t02190` `92d79343…`) |
| Ryu + Gouki | "You are worthy" / "RYU." (`t01680` `a4057866…`) | "We shall meet again" / "AKUMA." (`t02190` `750ae4c3…`) |

- Each block is about 480 frames, and the four-box total is unchanged.
- At 30-frame sampling, the box content is constant within each block.
- Pages 1-3 then follow at frames 2460-4140, with the same content hashes as
  each other across both runs.

## Conclusion

**CONFIRMED.** When both records of a dialogue pair hold identical text, the
box shows one unbroken block for the pair's full time, with no visible seam.
The `whole` layout gives one block per speaker, as the user asked. It is now
the default and the `end010` reference.

## Uncertainty and Alternatives

- The replays reused states from cold-boot runs on the `EXP-0044` image. This
  is valid because only `MC13.PAC` changed, and it reloads at stage 8. A fresh
  cold boot of `ba3fb3ce…` was not run.
- The frame-level seam test covered one pair (Ken's, records 36-37). The other
  pairs were checked at 30-frame sampling only.

## Reproduction

See Procedure. T3 needs no gameplay. The replays need the `EXP-0044` live
states (local), or a cold boot with the user working the menus and
`tools/mednafen/ending_driver.py`.
