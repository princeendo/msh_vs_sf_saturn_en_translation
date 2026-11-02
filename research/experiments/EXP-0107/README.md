# EXP-0107: The quote font's tail holds a payload through boot and play (OPT-003)

Task: OPT-003
Status: DONE
Confidence: CONFIRMED (for the scenes covered; see Uncertainty)

## Observation

- The new sub-menu and switch code needs RAM that the game loads and never
  overwrites (`EXP-0105`).
- The disc tools replace files at the same size only, and MEMFIX's entries
  fill their destinations back to back.
- The MEMFIX loader puts font entry 4 (`0x32740` bytes) at cart `0x0278CF60`
  at every boot. A smaller font leaves a zero tail inside that entry
  (`EXP-0106`: 352 spare candidate kanji).

## Hypothesis

A tail reserved at the end of the font is copied to cart RAM by the boot
load and is never written after it.

## Controlled Change

One variable: a 16,384-byte marker in the last 16 KiB of the font entry.

- **Marker:** SHA-256 of `OPT-003` and a block counter, from
  `official_endings.tail_marker`; payload SHA-256 `48eb90bf…35d8`.
- **To make room:** 286 kanji sacrificed instead of 110.
- **Spec:** the US release arguments plus `--font-tail-marker 16384`. It
  differs from the `m8_roster_gold_us` spec only by the `font_tail` key.

## Prediction

- The marker appears byte for byte at `0x027BB6A0`-`0x027BF69F` after boot.
- The only writes to that range are the boot load's.
- Win quotes and hints still draw.

## Inputs and Provenance

| Item | Value |
| --- | --- |
| Marker spec | `local/opt002/specs/us_tail16k.json`, `a56daedd…5dd6` |
| Marker image | `build/opt003/us_tail16k`, track 01 `79c91f17…e88f`, `MEMFIX.PAC` `3f402758…7583` |
| Control image (same compiler, `us.json`) | `build/opt003/us`, track 01 `b2e526a7…077b`, the `m8_roster_gold_us` baseline |
| Font report (marker) | packed 190,228 bytes, zero fill 16,428, reserve 16,384, tail address `0x027BB6A0` |

## Tools and Environment

- **New code:**
  - `pair_font.build(reserve=)`;
  - `caption_compiler`: the `font_tail` spec key (`FontTail`,
    `parse_font_tail`). It refuses a payload larger than the reserve or a
    non-empty tail;
  - `official_endings --font-tail-marker`.
- **Mednafen:** agent-patched 1.32.1. The quiet home for the unattended
  runs; the user's home (`local/mednafen`, 4 MB cart) for play.
- **This directory's `tail_watch.py`:**
  - `boot`: a write log on the tail from power-on;
  - `check`: cart RAM from a state compared with the built entry.
- **Helpers:** `tools.mednafen.bp_log` (write log during play) and
  `tools.mednafen.session_recorder` (states every 5 s, shots every 1 s).
- **Cart RAM is read through `mcs_extract`.** The agent cannot peek the
  physical bus: `ASPACE_PHYSICAL` is a TODO in Mednafen's `ss/debug.inc`.

## Procedure

1. Generate the marker spec. Compile it and the control with
   `caption_compiler`.
2. `tail_watch.py boot`, 6,000 frames (`local/opt003/boot`), then `check`.
3. The same for 20,000 frames of attract mode (`local/opt003/attract`).
4. **Play session:**
   - start the marker image in the user's Mednafen;
   - once past frame 2,400 (after the boot load), start `bp_log --kind write`
     on the tail and the recorder;
   - the user plays;
   - `check` the last states.

## Actual Result

- **Boot (both unattended runs):**
  - 4,096 write hits, all at PC `0x0603E04E` (the CD loader copy loop) in
    frames 1950-1953;
  - R2 steps through `0x027BB6A0`-`0x027BF69C`, one long each, and R0 holds
    the marker words (`2172795D`, `546C73BE`, …);
  - no other write through frame 20,000.
- **Read-back:**
  - at frame 6,000 (title) and 20,000 (attract), the whole font region in
    cart RAM equals the built entry 4, font body and tail;
  - finding the marker at the predicted offset also confirms `mcs_extract`'s
    cart RAM for this range.
- **Play (frames 2,449-16,214, user, 2026-11-02):**
  - title, OPTION MODE (`f00004596`), Ryu and Ken against two teams;
  - a KO and Ryu's win quote ("To live is to fight, to fight is to live!",
    `f00009609`);
  - a loss to Dhalsim and Omega Red (`f00014524`);
  - CONTINUE? with an English hint (`f00015429`).
  - `bp_log`: 0 hits.
  - The states at f15924 and f16214 equal the built entry (body and tail).
  - Mednafen was closed by the user at about f16214.

## Conclusion

**CONFIRMED** for boot, attract, Options, select, VS, fights, win quotes and
CONTINUE?:
- a payload reserved at the end of the quote font loads at a fixed cart
  address (`0x027BF6A0` minus the reserve) at every boot, by the game's own
  loader;
- nothing writes there afterwards;
- the smaller font still draws win quotes and hints.

This is the home for `OPT-004`'s code and data, with no disc growth and no
loader change. It needs the 4 MB cart, which the game already requires
(`UI-008`).

## Uncertainty and Alternatives

- **Not covered:** the ending, the boss, Survival, VS mode, BUTTON CONFIG,
  BACK UP save/load and the sound test.
  - The original font filled this range with glyphs, and the game reads its
    font without writing it, so a writer there is unlikely.
  - The `OPT-004` check will cover BUTTON CONFIG and BACK UP.
- **Write log limits:** it sees CPU writes only. DMA writes would show only
  in the read-back, which also passed.
- **Sacrificed kanji:** the 176 extra are "unseen" kanji, the same accepted
  risk as the release's (`EXP-0079`). The payload size actually needed is
  likely smaller than 16 KiB.
- **Execution:** running SH-2 code from cart RAM (the A-bus) is not tested
  yet. Alternatively the code can be copied to work RAM.

## Reproduction

```bash
# the spec: the US release arguments (EXP-0106) plus
#   --names us --font-tail-marker 16384 --out local/opt002/specs/us_tail16k.json
./invenv.sh python -m tools.text.caption_compiler local/opt002/specs/us_tail16k.json \
  --source-dir local/disc_images/mshvsf_saturn_jp \
  --candidates data/text/font_candidates.json --out-dir build/opt003/us_tail16k
CUE="build/opt003/us_tail16k/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python research/experiments/EXP-0107/tail_watch.py boot "$CUE" \
  local/opt003/attract --frames 20000 --shot 500
./invenv.sh python research/experiments/EXP-0107/tail_watch.py check \
  local/opt003/attract/boot.mcs build/opt003/us_tail16k/files/MEMFIX.PAC
# play: MEDNAFEN_HOME=local/mednafen MEDNAFEN_AGENT_DIR=local/opt003/play/agent
#   vendor/mednafen/build-agent/src/mednafen "$CUE"; after frame 2400:
./invenv.sh python -m tools.mednafen.bp_log local/opt003/play/bplog --kind write \
  --range 027BB6A0-027BF69F --agent-dir local/opt003/play/agent
```
