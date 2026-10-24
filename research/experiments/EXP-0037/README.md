# EXP-0037: First Look at Ryu's Ending, and the Final-Boss Checkpoint

Task: END-001
Status: DONE (2026-10-24)
Confidence: Observation record. The continue result is `SUPPORTED` (one live
run); everything about the ending's storage, encoding, renderer, and font is
`UNKNOWN`.

## Observation

M5 finished the win-quote pipeline. Nothing is known about endings. `AGENTS.md`
rules 13-14 forbid assuming that they share any structure with win quotes.

## Hypothesis

Only one, from the user's checkpoint plan (`END-001`, 2026-10-24): continuing
after a loss to the final boss returns to character select and keeps the
final-boss stage, so a new pick fights only the boss.

Everything else here is observation, recorded so that the next experiments can
be designed from it.

## Controlled Change

None. The image is the untouched source. The only actions were the user's
gameplay plus the agent's screenshots and save states.

## Prediction

After the continue, character select appears, and the next fight is the final
boss's stage, not stage 1.

**Refuted if:** the run restarts from an earlier stage, or the game ends without
character select.

## Inputs and Provenance

- **Image:** untouched `local/disc_images/mshvsf_saturn_jp`, track 01 SHA-256
  `8274307f9562d2da…`, matching `references/mshvsf/saturn_jp/README.md`.
- **Why not the roster image:** it repacks the quote font (`MEMFIX.PAC` entry
  4, `FONT-003`), and the ending might use that font too (unknown). The
  untouched image keeps the first observation free of our changes.
- **Emulator:** patched Mednafen 1.32.1 agent build, binary SHA-256
  `fe0edb99f1ffe63a…` (`EMU-021`), `MEDNAFEN_HOME=local/mednafen`, 4 MiB
  extended-RAM cart (log: `SGID: T-1238G`, `Cart: 4MiB Extended RAM`).
- **Gameplay (user, 2026-10-24):** arcade mode with Ryu (point) and Ken. Lost
  to the final boss, continued, picked Ryu (point) and Gouki, then beat the boss
  with Ryu.

## Tools and Environment

- New tool, `tools/mednafen/session_recorder.py` (unit test
  `tests/unit/test_session_recorder.py`). It attaches to the running agent and
  saves a screenshot every second and a state every 3 s, named by frame
  (`f<frame>.png` / `.mcs`), keeping the newest N states. It needs no hotkeys.
- `tools/mednafen/replay_state.py`: no-input replays of checkpoints.
- A local ffmpeg 8 tiles screenshots into contact sheets, using the ffmpeg
  `concat` demuxer over an explicit, frame-sorted file list (see the pitfall).

## Procedure

1. Launch the agent build on the untouched image. Run
   `./invenv.sh python -m tools.mednafen.session_recorder local/end001/run1 --keep-states 600`.
   This produced 1,276 screenshots, frames 363-75,386.
2. The user played (see Inputs). The recorder was stopped with `local/end001/run1/STOP`
   and Mednafen was closed during the credits.
3. Read contact sheets and full-size screenshots. Copy the chosen states to
   `local/end001/checkpoints/` (table below).
4. Replay with no input:
   - `select_after_continue.mcs` for 25 × 120 frames;
   - `ryu_gouki_post_boss_ko.mcs` for 360 × 10 frames (`local/end001/replay_ending`).
5. Save four more checkpoints from the post-KO state by `frames N` → `savestate`
   (no input) on the dialogue and ending pages.
6. Measure text-line positions from screenshots with `tools/common/png.py`
   (white-pixel extents and yellow box borders).

## Actual Result

### Continue and stage (prediction met once)

| Frame (live run) | Screen |
| --- | --- |
| ≈58,950-59,800 | `MECH-GOUKI WIN`, then a boss screen with a speech box |
| 59,832-60,307 | `CONTINUE?` countdown 9 → 4 (the user pressed Start) |
| 60,358-60,535 | Ryu/Ken portrait screen with the same gameplay-hint box |
| 60,659-62,013 | Character select, cursor on Ryu |
| ≈62,064-62,301 | Partner pick (Gouki), then mode and speed |
| 62,414-62,475 | Stage map, `STAGE-08`, Mech-Gouki |
| then | `VS` (Gouki/Ryu vs Mech-Gouki), and the fight |

The next fight after the continue was `STAGE-08` against Mech-Gouki, the boss
who had won. Stage 1 was not replayed. This is **SUPPORTED** (one run). Pick
order and side were not varied.

The no-input replay of `select_after_continue.mcs` stayed on character select,
cursor on Ryu, for all 3,000 frames (50 s). The checkpoint does not time out
quickly, so a later session can pick any team from it.

### Post-boss dialogue (a text scene before the ending)

After the boss KO, the win banner (`RYU GOUKI WIN`), and the tally, the HUD
goes away. The partner (Gouki) drops in beside the fallen boss, and a red box
with a yellow border appears at the top of the screen over the frozen stage.

- **Boxes:** four, shown one after another with no input. Each box appears
  whole within one 10-frame step (no typewriter effect at that resolution).
  Each stays about 230 frames (about 3.8 s). Box first-seen frames (1 s
  resolution): ≈69,479, ≈69,670, ≈69,897, ≈70,131.
- **Lines per box:** 2, 1, 2, 2. Characters per line: 9 + 6, 16, 4 + 10, 7 + 10.
  The longest is 16.
- **Speakers:** no names, portraits, or speaker marks are shown. By content, the
  boxes address Ryu and Gouki by name, but who says which box is not established.
- **Glyphs:** full-width kana, kanji, and punctuation (`、` `・` `！`). There are
  white glyphs on red, 13 pixel rows tall.

### Ending pages

After a fade to black (≈70,368), the background shows a blue gradient with
scrolling `MARVEL COMICS` / `CAPCOM` logos. A picture panel is centered at the
top, and a red text box sits at the bottom.

| Page | First seen (frame) | Last seen | Picture | Lines (characters) |
| --- | --- | --- | --- | --- |
| 1 | ≤ 70,419 | ≥ 70,892 | A: Ryu close-up | 11 + 14 |
| 2 | ≤ 70,942 | ≥ 71,352 | B: Ryu with Cyclops, Spider-Man, and one more Marvel figure | 15 + 10 |
| 3 | ≤ 71,412 | ≥ 72,063 | B (unchanged) | 20 (bracket gaps ambiguous) |

- Pages last about 470-700 frames (about 8-11 s). The text changes from page 2
  to page 3 while picture B stays.
- Then a fade to black (≈72,116) and the staff credits, which are already
  romanized or English, in a different decorative font.
- The full Japanese transcription is in the ignored
  `local/end001/transcription.json` (SHA-256 `ca7de11d…`), following the
  `EXP-0031` precedent: text stays local. Only the main session has read it, so
  it still needs an independent review (as `REF-003` did).

### Layout measurements (352 × 240 screenshots)

- **Box borders:** yellow, x 16-335.
  - Dialogue box: y 16-63.
  - Ending box: y 176-223.
- **Text rows:** glyph ink is 13 rows tall, with a 16-row line pitch.
  - Dialogue: rows 23-35 and 39-51.
  - Ending: rows 187-199 and 203-215.
  - One-line boxes use the top row, not a centered one.
- **Horizontal pitch:** 16 px for the uniform lines (dialogue box 2: 16
  characters across 249 px of ink).
- **Line starts:** all 13 lines start on a 16-px grid with origin x ≡ 12 (mod 16).
  As cell index (x − 12) / 16:

  | Screen | Line starts (cell) |
  | --- | --- |
  | Box 1 | 6, 7 |
  | Box 2 | 2 |
  | Box 3 | 6, 6 |
  | Box 4 | 7, 6 |
  | Page 1 | 6, 4 |
  | Page 2 | 3, 5 |
  | Page 3 | 2 |

  - Starts do not follow simple per-line centering by character count. Box 3
    line 2 (10 characters) starts at cell 6, while centering in a 20-cell row
    would give 5.
  - Page 3 (20 transcribed characters) spans only about 18 cells of ink, so its
    bracket gaps or punctuation are narrower than 16 px, or are not glyphs at all.

### Checkpoints (local, ignored; not RAM evidence)

| File (`local/end001/checkpoints/`) | Source | SHA-256 | Shows |
| --- | --- | --- | --- |
| `continue_after_boss_loss.mcs` | live frame 59,979 | `bf7ada8b6b04fe04…` | `CONTINUE?` countdown after losing to Mech-Gouki (Ryu, Ken) |
| `select_after_continue.mcs` | live frame 60,837 | `50fc3951d395f095…` | Character select after continuing; stage 8 pending |
| `ryu_gouki_boss_fight_late.mcs` | live frame 68,520 | `3223796fb3e06…` | Ryu/Gouki vs Mech-Gouki, shortly before the final KO |
| `ryu_gouki_post_boss_ko.mcs` | live frame 69,033 | `f42218550c0fb23c…` | Just after the boss KO; the dialogue and ending follow with no input |
| `ending_dialogue_box1.mcs` | post-KO + 400 frames | `949ee58d095d4376…` | Dialogue box 1 |
| `ending_dialogue_box4.mcs` | post-KO + 1,300 frames | `911b6ce374e90c27…` | Dialogue box 4 |
| `ending_page1.mcs` | post-KO + 1,800 frames | `a68b2da188428f57…` | Ending page 1 |
| `ending_page2.mcs` | post-KO + 2,300 frames | `179663bb86967e44…` | Ending page 2 |
| `ending_page3.mcs` | post-KO + 2,900 frames | `7287075f5402e89a…` | Ending page 3 |

"Post-KO + N" counts agent frame commands across replay steps, which drift
(see the pitfall), so the screenshot saved with each state (the `.png` beside
it) is authoritative. Each was read and matches its filename.

### Pitfalls found

1. **Contact-sheet indexing.** Tiling with `ffmpeg -pattern_type glob` and
   counting tiles did not line up with the `ls` order of the frame-named files:
   - the first `select_after_continue.mcs` (frame 59,809) was really on the
     `CONTINUE?` countdown;
   - a no-input replay caught it (the countdown ran out into `GAME OVER`);
   - the states were re-picked by reading the frame-named screenshots directly,
     and sheets were rebuilt from an explicit file list.
2. **Replay step counts are not exact frames.** `replay_state.py` steps (frames
   N, screenshot, run) add frames between steps, so timing comes from the
   recorder's frame-named live screenshots.

## Conclusion

- The checkpoint plan works. `select_after_continue.mcs` puts any later team one
  boss fight away from its ending. That the boss stage is kept is `SUPPORTED` by
  one run, and the next pick from that checkpoint will be a second observation.
- Ryu's run shows two text scenes after the boss:
  1. a four-box post-boss dialogue at the top of the stage;
  2. three ending pages with pictures and a bottom box.
- Both use red boxes with yellow borders, 13-row glyphs, and a 16-px grid.
- Nothing here shows where the text is stored, how it is encoded, how it is
  drawn, or which font it uses. The resemblance to the win-quote caption style
  is visual only (`AGENTS.md` rules 13-14).

## Uncertainty and Alternatives

- **What selects the dialogue:** it may depend on the pair (Ryu with Gouki), on
  the partner alone, on the point character, or it may always be shown. One run
  cannot tell.
- **What selects the ending:** it may follow the point character, the character
  who landed the KO, the one still standing, or the team. In this run Ryu was
  point and landed the KO, so these are confounded.
- **How the text is drawn:** VDP1 sprites per glyph, VDP2 tile layers, or
  pre-rendered bitmaps (the picture panels at least look like bitmaps). It may
  also differ between the dialogue and the pages.
- **Line positions:** they could come from leading spaces in the data, per-line
  start offsets, or computed centering with narrow glyphs. The measurements rule
  out only simple centering by character count.
- **Speakers:** attribution is unknown; the screen gives no speaker cue.

## Designed Next Experiments

Each becomes its own task (`TASKS.md`, `END-002` to `END-006`), one
`IN_PROGRESS` at a time.

### END-002: which video path draws the ending text (no gameplay)

- **Hypothesis (one at a time):** the glyphs of dialogue box 1 are drawn by VDP1
  sprite commands, one per glyph cell.
- **Single change:**
  1. *Passive step.* Extract VDP1 and VDP2 VRAM (validated regions, `DBG-012`)
     from `ending_dialogue_box1.mcs`, and list the commands with
     `tools/memory/vdp1_sprites.py`.
  2. *Active step*, if candidates are found. Set the skip bit (control-word bit
     14) on just those commands through the agent (`write vdp1vram`) while
     paused, then step one frame and take a screenshot.
- **Prediction:** a set of normal sprites at y ≈ 23 and 39 whose x positions sit
  on the 16-px grid, one per visible glyph (9 + 6 for box 1, no blanks). Skipping
  them removes the text and nothing else.
- **Refuted if:** no such sprite set exists, or skipping it leaves the text
  (then test VDP2 next: NBG/RBG cell or bitmap layers, as a separate
  hypothesis).
- **Then:** repeat the passive step on the `ending_page*` states. The pages may
  use another path.

### END-003: whether the text exists as per-character values in work RAM (no gameplay)

- **Hypothesis:** while box 1 is on screen, its text is held in work RAM as one
  fixed-width value per character.
- **Single change:** none, read only. Run `tools/text/pattern_search.py` over
  WRAM-L and WRAM-H from `ending_dialogue_box1.mcs`. It is encoding-agnostic:
  it uses only the repeat structure of the visible text.
  - Box 1 is nine identical marks, then three different symbols, then three of
    the first mark.
  - The same three-symbol name recurs at the start of page 1's line 2 and page
    2's line 2.
  - Try 8- and 16-bit widths, with and without a line separator.
- **Prediction:** at least one hit whose values are consistent across boxes and
  pages (the same symbol gets the same value).
- **Refuted if:** there are no hits at either width. Then the text is
  compressed, pre-rendered, or held only in cart RAM or VRAM, and the next test
  follows the renderer source from `END-002`.
- **Not assumed:** any code table. The win-quote codes (`0x08xx`) may be compared
  afterwards, as a separate test.

### END-004: which disc file holds the ending text (depends on END-002 or END-003)

- **Hypothesis:** formed from `END-003`'s RAM address, or from `END-002`'s glyph
  source.
- **Single change:** a write breakpoint (log mode) on that address, replayed from
  `ryu_gouki_post_boss_ko.mcs` with no input, to find the writer. Then trace it
  back to a CD read, a decompressor, or a copy.
- **Prediction:** a load from an identifiable disc file during the post-KO
  sequence. The file is not assumed to be `MCnn` or PAC/LZSS until observed.

### END-005: what selects the dialogue and the ending (one user session per team)

- **Hypothesis:** the post-boss dialogue depends on the partner, while the
  ending pages depend only on the point character.
- **Single change:** the partner only. From `select_after_continue.mcs`, pick
  Ryu (point) + Ken and beat the boss with Ryu.
- **Prediction:** the ending pages are pixel-identical to this run (in the text
  boxes), and the dialogue differs or is absent.
- **Refuted if:** the pages differ (so the ending depends on more than the point
  character), or the dialogue is identical (so it does not depend on the
  partner).
- **Later single-variable runs:** swap the order (Gouki point, Ryu partner); KO
  with the partner instead of the point character.
- **Also checked:** the run is a second observation of the continue-keeps-stage
  result.

### END-006: arcade reference for Ryu's ending (no Saturn change)

- **Hypothesis:** the arcade sets show the same post-boss dialogue and ending
  pages for the same team, and the US/EU sets show official English for them.
- **Single change:** none. Use scripted MAME runs (`tools/reference/`), with
  memory and ROM search as in `EXP-0029`/`EXP-0030`.
- **Prediction:** the Japanese arcade screens match this transcription. English
  screens exist as the translation oracle (`TR` policy; PS1 `SLUS-00793` is
  secondary).
- **Not assumed:** that the arcade text format equals the Saturn's (rule 14).

## Reproduction

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" MEDNAFEN_AGENT_DIR="$PWD/local/mednafen/agent" \
  vendor/mednafen/build-agent/src/mednafen \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python -m tools.mednafen.session_recorder local/end001/run1 --keep-states 600
```

```bash
./invenv.sh python -m tools.mednafen.replay_state \
  "local/disc_images/mshvsf_saturn_jp/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/end001/checkpoints/ryu_gouki_post_boss_ko.mcs local/end001/replay_ending \
  --steps 360 --step-frames 10
```

The second command replays the whole dialogue and the ending pages from the
post-KO checkpoint with no input.
