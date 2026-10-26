# EXP-0062: The win-banner name records and the US switch

Task: LOC-004 (part 3: the win banner)
Status: DONE
Confidence: CONFIRMED (the banner reads BISON after a single pointer change;
a cold boot loads the patched pointers)

## Observation

- `EXP-0054`: the win banner ("VEGA / RYU / WIN") spells names from large
  2×2 letter glyphs. Its string source was not found.
- `EXP-0058` and `EXP-0060`: the disc already holds US versions of other name
  assets.

## Hypothesis

The banner takes each name from a per-character table. If the disc holds US
records, repointing the table entries switches the banner with no new data.

## Controlled Change

One u32 write in WRAM-H (`0x060B87A0`: `0x060B8A88` → `0x060B8BCE`) in the
KO state before the banner, then the same replay without it as a control. The
build changes three pointers in `MM.BIN`.

## Prediction

The replay's banner reads BISON / RYU / WIN. The control reads VEGA / RYU /
WIN.

## Inputs and Provenance

- `local/end024v/rec/states/f00008316.mcs`: the KO of a Vega + Ryu win (the
  banner appears at about +150 frames with no input).
- `MM.BIN` from source track 01. `build/regression/m8_roster_gold_us` and
  `m8_roster_gold` images.

## Tools and Environment

- Patched Mednafen 1.32.1 agent: write breakpoints, bus writes, screenshots,
  savestates.
- `tools/memory/mcs_extract.py`, `tools/memory/vdp1_commands.py`,
  `tools/sh2/disasm.py`. Python 3.12.13.

## Procedure

1. Replay `f00008316` and screenshot at +150, +250, +350 and +450 to find the
   banner. Save a state at +200 (`local/loc004/banner200.mcs`).
2. List VDP1 sprites from that state. The letters are 2×2 cell sprites:
   - V `0x32E`, E `0x2EC`, G `0x300`, A `0x2E4`;
   - R `0x326`, Y `0x344`, U `0x32C`.
3. Static searches for the names in shifted-ASCII, letter-index, code-offset
   and masked-code encodings: nothing.
4. The V's VDP1 command sits in a WRAM-H double buffer (`0x060CE328` /
   `0x060D44C8`). A write breakpoint on its source field gives PC
   `0x0601CAB6`, with R5 = `0x32E`. Disassembly: the generic sprite emitter
   `0x0601C9C4` takes a pattern number and subtracts `0x5000`.
5. Search for `0x532E`: a dense cluster in `MM.BIN` `0x9FD38`-`0xA0140`.
   Decode the records and find the pointers to them.
6. Trial and control replays (the change above). Screenshot at +200.
7. Build, re-baseline, run all references, remake the patch.
8. Cold boot each image and poll `0x060B87A0`, `0x060B87AC` and `0x060B87DC`
   every 150 frames. Also load the stage-map state `end027 f00013440` on each
   image and read the same addresses after a fight loads.

## Actual Result

- **Records.**
  - Header `0002 000A n`, a u32 pointer (it depends on n; probably a
    letter-spacing table), then n+1 (pattern, `1100`) pairs, letters right
    to left.
  - Decoded names: APOCALYPSE, CYCLOPS, CAPTAIN AMERICA, HULK, WOLVERINE,
    SHUMA-GORATH, OMEGA RED, SPIDER-MAN, BLACKHEART, RYU, KEN, CHUN-LI,
    DHALSIM, ZANGIEF, VEGA, GOUKI, SAKURA, NORIMARO, DAN, MECH-GOUKI,
    SHADOW, U.S.AGENT, MEPHISTO, **BISON, AKUMA, CYBER-AKUMA**, CHARLIE.
- **Pointers.**
  - The record pointer for character index i is at `MM.BIN`
    `0x9FBF8 + 12i`, followed by `0x00008004` and a self-address.
  - VEGA (14) `0x9FCA0`, GOUKI (15) `0x9FCAC`, MECH-GOUKI (19) `0x9FCDC`.
    BISON, AKUMA and CYBER-AKUMA are entries 23-25.
- **Trial:** the banner reads **BISON / RYU / WIN**
  (`local/loc004/banner_bison.png`). The control reads VEGA / RYU / WIN.
- **Build:**
  - `MM.BIN` gains three pointer edits, all checks true.
  - The Saturn spec is unchanged (`7ce7820a…`). US spec `84a95315…`, track 01
    `0afe0f7a…`.
  - 9 of 9 references pass. Patch `c4b69e46…`, 156,014 bytes, with a passing
    round trip.
- **Cold boot:**
  - The US image holds `060B8BCE`/`060B8BEC`/`060B8C0A` from frame 1800, when
    the table loads.
  - The table is absent at frame 2700 (title screen) on both images.
  - Loading a stage-map state does not reload it.

## Conclusion

**CONFIRMED:** the win banner takes each name from the pointer table at
`MM.BIN` `0x9FBF8 + 12i`. The US variant repoints entries 14, 15 and 19 to
the disc's own BISON, AKUMA and CYBER-AKUMA records, and a cold boot loads
those pointers.

## Uncertainty and Alternatives

- Seen in a replay for Vega. AKUMA and CYBER-AKUMA are not seen. Their
  records decode correctly and use the same layout.
- Other screens using this table, if any, will also show the US names. That
  is the intended consistency for the variant.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold_us
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.json
```

The trial is a scratch agent script: load `f00008316`, `bus_write`
`0x060B87A0` = `060B8BCE`, `frames 200`, screenshot. The record decoder is
described under Actual Result.
