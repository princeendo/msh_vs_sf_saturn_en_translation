# EXP-0010: Capture Pre-KO and Win-Quote Checkpoints

Task: `DBG-001`, `DBG-003`, `REF-002` (optional `DBG-002`)
Date: 2026-10-15
Status: IN_PROGRESS
Confidence: HYPOTHESIS

## Observation

`EXP-0009` showed that a Ryu/Ken pre-KO checkpoint yields varying Ryu win quotes.
`REF-001` selected Q3. `EXP-0008` validated save-state extraction of WRAM and VDP
VRAM, but only for states saved while frame advance holds the game paused.

## Hypothesis

Starting from one pre-KO checkpoint (A), repeated KOs can produce these states, each
saved during a frame-advance pause with a matching screenshot, and each reloadable
to the same visible scene:

- a Q3 quote-screen state (C1);
- a second Q3 state from a separate replay (C1′);
- a different-quote state (C2).

## Controlled Change

Only replays from state A, freeze/save/screenshot actions, and reloads. The binary,
source image, BIOS, configuration, and cartridge are unchanged. Slots 0-4 hold
earlier evidence and are not overwritten.

## Prediction

1. A, C1, C1′, and C2 states exist in slots 5, 6, 8, and 7, each with a screenshot
   taken in the same pause.
2. C1 and C1′ screenshots show Q3, and C2 shows a different Ryu quote.
3. Reloading A and C1 twice each restores the same scene.

## Inputs and Provenance

- Same Mednafen process as `EXP-0009` (pid 7476, log
  `local/mednafen/logs/ref007-exp0009.log`), so no cold relaunch. Source identity
  matched the manifest after `EXP-0009` while that process was running.
- Base checkpoint: `EXP-0009` slot 3 (vs Vega), SHA-256
  `dd08030853d0b4fa1ee1ea7973ab27aebb71f3bc1ef37d90b6e68f4c70d3b5e7`.

## Procedure

Use left Option for Alt. Keep the debugger closed. Press `F7` only while running
normally.

1. State A: select slot 3 (`3`) and load it (`F7`). Immediately press `Option+A`,
   then `5`, `F5`, `F9`, then `Option+R`.
2. Replays: select slot 5 (`5`). For each replay, press `F7`, KO with Ryu, and wait
   for the quote text to finish drawing.
   - **Q3 the first time (C1):** `Option+A`, `6`, `F5`, `F9`, `Option+R`.
   - **Q3 a second time (C1′):** `Option+A`, `8`, `F5`, `F9`, `Option+R`.
   - **First non-Q3 quote (C2):** `Option+A`, `7`, `F5`, `F9`, `Option+R`.
   - Before the next replay, press `5` again to reselect slot 5.
3. Optional B (`DBG-002`): during a replay, after the KO but before the quote
   screen, `Option+A`, `9`, `F5`, `F9`, `Option+R`. Note which quote that replay
   produced.
4. Reload checks: select each of slots 5 and 6, then press `F7` and `F9` twice.

## Revision 1 (mid-session)

Observation: the user created state A in slot 5 (19:47:37; 5,386,660 bytes, SHA-256
`ab60af86089a95750629396088932bfe30a66c0daff7681c1ae973d5fd91dce6`). No screenshot
of A was taken. One replay saved a non-Q3 quote screen in slot 7 (19:48:29;
5,487,503 bytes, SHA-256
`9482880a11269e5ce630179db70bc1833375ee39d30af2ab84161a265a6a47ce`), with screenshot
`-0030.png` showing a tenth distinct Ryu quote, Q10 (opening `一瞬の迷いが`).

The user then made about 100 replays from slot 5 without Q3 appearing. Q3 had
appeared in 2 of 12 `EXP-0009` replays. This contradicts a uniform per-replay random
draw over a fixed pool, and suggests that a condition carried in the checkpoint, or
in how the KO happens, restricts the available quotes. The cause is `UNKNOWN`.
Which quotes appeared during those 100 replays was not recorded.

Change: the memory comparison needs two different quotes from the same winner, not
Q3 specifically. The revised procedure therefore fills slots 6, 8, and 9 with the
next three quote screens in order, with no visual matching by the user. The agent
assigns C1, C2, and C1′ roles from the screenshots afterward. A time-only control
(slot 7 reloaded and frozen about 2 s later, saved to slot 0) gives a same-text pair
when no natural repeat occurs.

Before slot 0 is reused, the `EXP-0006`–`EXP-0009` states in slots 0-4 were copied
with `cp -p` to ignored `research/savestates/archive-2026-10-15/slotN.mcN`. Each copy
was SHA-256-verified against the hashes recorded in those experiments.

## Actual Result (partial)

The user completed the revised Tasks 1-4. Save-time thumbnails were extracted from
each state's embedded preview (`tools.memory.mcs_extract`, which now writes
`preview.png`). They are authoritative for the saved instant. The F9 screenshots
from this session were taken 5-19 s before their saves, so they are not.

| Slot | Saved | Size | SHA-256 | Thumbnail shows | Role |
| ---: | --- | ---: | --- | --- | --- |
| 5 | 19:47:37 | 5,386,660 | `ab60af86089a95750629396088932bfe30a66c0daff7681c1ae973d5fd91dce6` | Vega fight, in-game `1P PAUSE` | A |
| 7 | 19:48:29 | 5,487,503 | `9482880a11269e5ce630179db70bc1833375ee39d30af2ab84161a265a6a47ce` | Win screen, Q10 (`一瞬の迷いが`) | C1 |
| 6 | 20:08:35 | 5,490,320 | `5534ad9e464630d0f3d2ccecccaa2a4c5fab2a6fa45ce708fc4ae00ebfcc3878` | Win screen, Q8 (`まだまだお前達は`) | C2 |
| 8 | 20:09:02 | 5,490,328 | `072497f2891b9693db6dd31026cbef227c059f0d63ec289429877711ed4910bf` | Win screen, Q11 (`おれは・・・`) | C2b |
| 0 | 20:09:57 | 5,485,814 | `7a883d1b581aff7dcbb55d6db72f99fa2a7393d8696b2fa194a4dfb1ab9bcc84` | Black screen | Failed C1′ |

- Q11 is an eleventh distinct Ryu quote.
- The `EXP-0009` slots 3 and 4 thumbnails also show `1P PAUSE`, so every pre-KO
  checkpoint was saved during the game's own pause menu.
- Slot 0 shows that the quote screen ends within about 2 s of the slot-7 instant.
  A wall-clock wait is unsuitable for the time control, so it will be redone with
  counted frame advances.
- No reload screenshots exist from Task 4; the snapshot counter stops at `-0033`.
- Regions and thumbnails for slots 0 and 5-8 were extracted to ignored
  `research/memory_dumps/<sha256[:16]>/`.

Session screenshots (ignored `local/mednafen/snaps/`):

| File | Time | Size | SHA-256 |
| --- | --- | ---: | --- |
| `-0030.png` | 19:48:32 | 20,008 | `15ccd17a1dc8e28688d79ca8297b58833a11f86d3d1233a0d52d5a958599642a` |
| `-0031.png` | 20:08:16 | 20,181 | `675e9c8263f77904ab909262bdee4fcfd11af29558a16037af969f3ff477d8af` |
| `-0032.png` | 20:08:57 | 19,547 | `d863d565ce1288fefd9e48b197735603481c33868eb69a2b89dbc015cc81f512` |
| `-0033.png` | 20:09:58 | 326 | `f0858bda6c535ff0619c61598b8e4b972eb40f2802648c1b75e004562e900ef6` |
