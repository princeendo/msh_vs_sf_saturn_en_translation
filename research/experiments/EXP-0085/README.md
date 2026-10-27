# EXP-0085: When the MM.BIN story table is shown

Task: TXT-001
Status: DONE
Confidence: CONFIRMED (records 16-41: arcade trace and Saturn RAM trial);
HYPOTHESIS (which screens show records 39 and 42-44)

## Observation

- **The table:** `MM.BIN` records 16-47 (`0x7CA44`-`0x7D3C4`) follow the 16
  CONTINUE? hints in one array of 76-byte records at `0x7C584`. They hold one
  line per roster slot 0-25, Vega's orders to Shadow and Metal Zangief, a
  punctuation row, and developer jokes (`data/translations/story_lines.json`,
  draft).
- **Saturn play:** a read log in play (`EXP-0081`) showed no screen reading
  them.
- **Arcade:** all three sets hold the same array at `0x2139AC`.
- **Earlier claim:** `EXP-0047` reported a code pointer to the table at
  `0x0B03BA` → `0x214748`.

## Hypothesis

The arcade's own code shows where and when the records are drawn. Reads of
the array, logged in MAME while the game runs, and the decrypted code around
them identify the screen and the trigger. The Saturn port uses the same rule.

## Controlled Change

No game data changes.
- **Arcade:** MAME read taps and, for the trials, a debugger breakpoint that
  sets one register.
- **Saturn:** one instruction is changed in RAM after loading a state.

## Prediction

- **Arcade:** a read by the CONTINUE?-area code at the moment a record
  appears, and a selection rule in that code.
- **Saturn:** forcing that rule on the Saturn shows the record on the same
  screen.

## Inputs and Provenance

- **MAME and sets:**
  - MAME 0.289;
  - `mshvsfj` and `mshvsfu` from `local/arcade_roms/mshvsf/`, the sets of
    `references/mshvsf/arcade/README.md`;
  - default EEPROM in `local/mame_arcade/nvram`.
- **Program dumps (4 MiB, data view):** `mshvsfj` `b2612676…`, `mshvsfu`
  `3f04821c…`. The decrypted opcode space was saved with the debugger's
  `saveo`.
- **Saturn:**
  - US release image `m8_roster_gold_us` (track 01 `a6572495…`);
  - state `local/special004/play/rec/states/f00019422.mcs` (`869342af…`),
    from the `EXP-0081` play session: Apocalypse is about to win a round
    against the player.

## Tools and Environment

- **`tools/reference/mame_timeline.lua`** has a new verb,
  `logreads <first> <last> <path>`. It logs `frame pc offset` per change of
  (frame, PC).
  - MAME read taps need a word-aligned range, so the end address must be
    odd.
  - The control: a tap on the 68000 autovectors `0x60`-`0x7F` logged 62,108
    lines in 60,000 frames.
- **Disassembly:** `tools/sh2/disasm.py` for the Saturn, and MAME
  `-debug -debugger none` with timeline `debug dasm …` for the arcade.
- **Saturn:** `tools.mednafen.write_trial` (silent home).

## Procedure

1. **Attract loop:** `mshvsfj`, 60,000 frames, no input, with a read tap on
   `0x213F82`-`0x2147ED` (`local/txt001/arc1`).
2. **One lost game:**
   - coins, 1P start and the default team (Ryu, Ken), then no input, to
     frame 30,000;
   - the tap covers the whole array, `0x2139AC`-`0x2147EB`, and snapshots
     are taken every 300 frames (`arc2`).
3. **Lose and continue for 200,000 frames:** coins, Start and Button 1 every
   200 frames, with the same tap (`arc3`).
4. **Look for references:** dump the program, then search the data view and
   the decrypted opcodes for longwords pointing into the array. Disassemble
   the hits and their callers.
5. **Arcade trial:** as in step 2, with
   `bpset 70362,1,{d0=27;g}`, which forces the roll; one snapshot at frame
   11,940 (`arc4`).
6. **Arcade trial with the slot forced:** `{d0=27;d1=16;g}`, which also
   forces slot 11, Chun-Li (`arc5`).
7. **Saturn:**
   1. control: `write_trial` from state `f00019422`, 524 frames;
   2. trial: the same with `--write workramh:AF228:0009` (the `bf` after
      `cmp/eq #39` becomes `nop`).

## Actual Result

### The selection rule (arcade `0x070336`, Saturn `0x060AF1F2`)

The arcade code (decrypted, `mshvsfj`) runs when the CPU has beaten the
player. The game-over sequence at `0x0AAB2E` calls it with
`D1 = ($52, winner)`, the winner's character ID × 2.

```
0x070336  create the message object
          tst.b  (-$37CD,A5)  ; flag set: per-character hint from 0x0703A4
          jsr    $192C        ; random number -> D0
          tst.w  (-$3370,A5)  ; region: 0 = Japan
          bne    normal
          andi.w #$3F,D0
          cmpi.w #$27,D0      ; 1 in 64
          bne    normal
          lsr.w  #1,D1        ; slot
          index = slot, base = 0x213E6C (record 16)
normal:   index = D0 & 0x0F, base = per-character pointer
          (tables 0x20BFAC/0x20C014/0x20C07C/0x20C0E4 by region)
```

- **The rule:** when the CPU wins, the winner's line is normally one of its
  win quotes. In the Japanese region, a 1-in-64 roll shows story record
  16 + the winner's slot instead.
- **Saturn:** `MM.BIN` has the same code at `0x060AF1F2`-`0x060AF246`:
  - the flag at `0xC833`;
  - `trapa #62`;
  - the region word at `0xCC90`;
  - `and #0x3F` / `cmp/eq #39`;
  - the slot `@(6,gbr) >> 1`;
  - base `0x06095544` (`MM.BIN` `0x7CA44`).
- **The CONTINUE? hint** is a different routine (`0x0703FC`): random & 15,
  base `0x2139AC`. It runs after the winner's line.

### Observations

- **Attract mode:** no read, except one boot-time read at frame 2 (PC
  `0x000244`).
- **One lost game:** a single read, hint record 11 (PC `0x0706FE`,
  frame 12,231). Snapshot `f12300` shows that hint under CONTINUE?
  (`bbe57818…`).
- **26 CONTINUE? screens in 200,000 frames:** hint records 1-15 only; no
  story record. The expected count at 1 in 64 is 0.4.
- **Forced roll (arcade):** at frame 11,929 PC `0x0706FE` read record 24
  (slot 8). The post-loss screen shows the CPU team Blackheart and Zangief.
  The box reads Blackheart's record 24: さて、悪魔と死神、どちらを紹介してほしいかね？
  ("Now, a devil or a reaper... which shall I introduce you to?").
  Snapshot `7b2d64a7…`.
- **Forced roll and slot 11:** record 27 was read. The box reads
  あら？ザンギエフ さっきの場所でローグを見なかった？
  ("Oh? Zangief, didn't you see Rogue back there just now?").
  Snapshot `d158ed5b…`.
  - **The placeholder `{P}`** inserts the speaker's teammate (Zangief,
    Blackheart's partner), not the player's character.
- **Saturn, US release image:**
  - **Control:** Apocalypse's official English win quote, "Destruction is a
    small price to pay for power!" (`8d1fed9a…`).
  - **Trial:** the same screen shows record 16 in Japanese:
    その肉体をアポカリプスにささげよ！来たる時代にふさわしい力を与えてやろう
    ("Give your body to Apocalypse! I'll grant power fit for a new age!")
    (`3195c28d…`).
  - **So the release can show this Japanese text:** on about 1 in 64 losses
    to the CPU, at random.

### The other records

| Records | Reader | Other-language text | Screen |
| --- | --- | --- | --- |
| 39 (slot 23) | `0x0A06A8` (Japanese text mode), `0x0705E0` index 0 | English record 28 at `0x2244EC`: "MSH VS STREET FIGHTER / COMING SOON" | a screen that also loads a palette from `0x1ED94C` (HYPOTHESIS: an announcement screen); not seen |
| 42-44 | `0x07059C`/`0x0705A0`/`0x0705A4` (index 0-2, base `0x214624`) | English records 25-27 at `0x2243C0`: "I've finally tracked you / down! Now, you're mine!" (all three) | called from three character intro routines (`0x062A36`, `0x05B2EA`, `0x05F60C`) when `(-$3800,A5)` ≥ 4 (two of them); HYPOTHESIS: Shadow's and Metal Zangief's intros |
| 45-47 | none found | none | no immediate or pointer refers to them; HYPOTHESIS: unused |

### Two earlier findings corrected

- **`EXP-0047`'s pointer is DISPROVEN.** `0x0B03D8` holds `0x00214748`
  inside a table of powers of two in BCD (`…0010 7374 1824`,
  `0021 4748 3648` = 2,147,483,648). It is not a reference to the table.
- **`EXP-0080`'s "no official English hints" is DISPROVEN.**
  - **Where:** for regions other than Japan, the hint routine uses base
    `0x2239FC` (100-byte records). It maps the 16 Japanese indexes through
    `0x070448` (`0,2,4,…,22,0,2,4,6`) onto 12 English hints, each two
    records long.
  - **What:** the text is the arcade's official English, with the same
    arrow codes. For example, "When Air Combo starts to move hits the
    opponent, put the lever ↑ to chase him and execute a combo!" and
    "Push PPP while guarding for the Advancing Guard. Push the opponent
    back!".
  - `mshvsfj` and `mshvsfu` hold identical bytes there.

## Conclusion

**CONFIRMED** (arcade read trace with a forced roll; Saturn RAM trial on the
release image):
- Story records 16-41 are a rare alternative to the CPU winner's win quote,
  on the screen after the player loses, before CONTINUE?.
- The trigger is a 1-in-64 roll, in the Japanese region only, so the
  arcade's other regions never show it.
- The record is 16 + the winner's slot, and `{P}` inserts the winner's
  teammate.
- The Saturn port uses the same rule.

## Uncertainty and Alternatives

- **Records 39 and 42-44:** their screens are identified only from code;
  not seen.
- **Records 45-47:** no reader was found, but a computed address cannot be
  ruled out.
- **The Saturn's region word** `0xCC90` was not read; the Saturn trial
  forced the branch. Saturn retail is Japanese only, so 0 is expected
  (HYPOTHESIS).
- **The roll's distribution:** `jsr $192C` / `trapa #62` was taken to be
  uniform. 1 in 64 assumes that.

## Reproduction

```bash
D=local/txt001/arc4; mkdir -p $D/snap
{ echo "1 logreads 0x2139ac 0x2147eb $D/table_reads.log"
  echo "100 debug bpset 70362,1,{d0=27;g}"; echo "100 debug go"
  echo "3200 press 6 Coin 1"; echo "3230 press 6 Coin 1"
  echo "3320 press 6 1 Player Start"
  echo "4300 press 6 P1 Button 1"; echo "4360 press 6 P1 Button 1"
  echo "11940 snap"; echo "11941 exit"; } > $D/timeline.txt
MAME_TIMELINE=$D/timeline.txt mame mshvsfj -debug -debugger none \
  -rompath local/arcade_roms/mshvsf -video none -sound none -nothrottle \
  -skip_gameinfo -nomouse -cfg_directory local/mame_arcade/cfg \
  -nvram_directory local/mame_arcade/nvram -snapshot_directory $D/snap \
  -homepath local/mame_arcade -autoboot_script tools/reference/mame_timeline.lua

./invenv.sh python -m tools.mednafen.write_trial \
  "build/regression/m8_roster_gold_us/build/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/special004/play/rec/states/f00019422.mcs local/txt001/sat/forced_524.png \
  --frames 524 --write workramh:AF228:0009
```
