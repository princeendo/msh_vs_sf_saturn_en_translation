# EXP-0063: The VS-screen name records and the US switch

Task: LOC-004 (part 4: the VS screen)
Status: DONE
Confidence: CONFIRMED (a replay shows BISON after one pointer change; a cold
boot loads the patched pointers)

## Observation

- `EXP-0054` saw the VS-screen names (for example "VEGA" and "MECH-GOUKI"
  under the portraits) as part of a sprite mosaic, probably from `SEL*.PAC`.
  No tiles were found.
- `EXP-0062`: the win banner spells names from `MM.BIN` sprite records.
  The records include unused BISON, AKUMA and CYBER-AKUMA entries.

## Hypothesis

The VS names are built the same way: letter sprites from name records, chosen
by a per-character pointer table. If so, US records may exist there too.

## Controlled Change

Two u32 writes in WRAM-H before the VS screen is built:
- `0x0607F0DE`: `0x0607F2D8` → `0x0607F3B2` (Vega → BISON);
- `0x0607F11A`: `0x0607F348` → `0x0607F3DA` (Mech-Gouki → CYBER-AKUMA).

Control: the same replay without the writes.

## Prediction

Vega's VS name reads BISON.

## Inputs and Provenance

- `local/end024v/rec/states/f00009368.mcs` (the VS screen), replayed 60
  frames and saved as `local/loc004/vs60.mcs` for the sprite list.
- `f00009018` (before the VS screen) for the trial.
- `MM.BIN` from source track 01.

## Tools and Environment

- `tools/memory/vdp1_commands.py` (`--font` matching),
  `tools/memory/mcs_extract.py`.
- Patched Mednafen 1.32.1 agent. Python 3.12.13.

## Procedure

1. List the VDP1 sprites at `vs60`. The names are rows of 16×16 sprites,
   palette `0x6010`, at an 11 px pitch, right to left. Font matching gives
   staff-credits codes:
   - MECH-GOUKI: I `0x218` … M `0x21C`;
   - RYU: `0x224`, `0x228`, `0x221`;
   - VEGA: `0x210`, `0x216`, `0x214`, `0x225`.
2. Search for the reversed sequence of patterns `0x5000 + code`: `MM.BIN`
   `0x667E2` (VEGA), `0x6677A` (RYU), `0x66852` (MECH-GOUKI).
3. Decode the records: u16 0, u16 n, u16 0, a u32 spacing pointer
   (`0x0607F3FA`… by n), then n patterns. Then search for pointers to them.
4. Replay the trial and the control from `f00009018` for 410 frames, and take
   screenshots.
5. Add the pointers to `US_NAME_POINTERS`. Build, re-baseline, run all
   references, remake the patch.
6. Cold boot the US image and poll the three RAM pointers every 150 frames.

## Actual Result

- **Records** (`0x6666A`-`0x668DA`): APOCALYPSE, CYCLOPS, HULK, WOLVERINE,
  SHUMA-GORATH, SPIDER-MAN, BLACKHEART, RYU, KEN, CHUN-LI, DHALSIM, ZANGIEF,
  VEGA, GOUKI, SAKURA, NORIMARO, DAN, MECH-GOUKI, SHADOW, U.S.AGENT,
  MEPHISTO, **BISON, AKUMA, CYBER-AKUMA**. Names with a space, such as
  CAPTAIN AMERICA, use another code, which the decoder skipped.
- **Pointer table:** `MM.BIN` `0x66536 + 12i`. VEGA (14) `0x665DE`, GOUKI
  (15) `0x665EA`, MECH-GOUKI (19) `0x6661A`. BISON, AKUMA and CYBER-AKUMA
  are entries 23-25.
- **Trial:** the VS screen shows **BISON** under Vega's portrait
  (`local/loc004/vs_us.png`). The control shows VEGA (`vs_control.png`). The
  opponent team differs from the recording because the replay diverges.
- **Build:**
  - `MM.BIN`: 101 patched bytes, 43 changed, all checks true.
  - The Saturn spec is unchanged. US spec `a343d7c7…`, track 01 `41ca8a9a…`.
  - 9 of 9 references pass. Patch `ccf6200c…`, 156,211 bytes, with a passing
    round trip.
- **Cold boot:** the US pointers (`0607F3B2`/`0607F3C6`/`0607F3DA`) load by
  frame 1800.

## Conclusion

**CONFIRMED:** the VS-screen names are credits-font letter sprites spelled
from `MM.BIN` name records, chosen through the table at `0x66536 + 12i`.
The US variant repoints entries 14, 15 and 19 to the disc's own BISON,
AKUMA and CYBER-AKUMA records. `SEL*.PAC` art is not involved. This corrects
`EXP-0054`.

## Uncertainty and Alternatives

- Only Vega was seen on screen. The Mech-Gouki write did not show, because
  the diverged replay faced another team. AKUMA and CYBER-AKUMA use the same
  record layout.
- `SEL*.PAC` layouts remain undecoded. They are not needed for names.

## Reproduction

```bash
./invenv.sh python -m tools.regression.reference_builds --driver local/mame_src/cps2.cpp --only m8_roster_gold_us
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/m8_roster_gold_us/build/image_a --reference m8_roster_gold_us --stem mshvsf_saturn_en_m8_gold_us --out-dir build/release/m8_gold_us --record release/m8_roster_gold_us.json
```

The trial is a scratch agent script: load `f00009018`, `bus_write`
`0x0607F0DE` = `0607F3B2`, `frames 410`, screenshot.
