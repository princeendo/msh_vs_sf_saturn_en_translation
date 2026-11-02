# EXP-0111: A guarded V-blank hook runs code in the font tail every frame (OPT-005)

Task: OPT-005
Status: DONE
Confidence: CONFIRMED (cold boot, unattended); the attract loop is not
covered (another handler)

## Observation

- The NAMES switch must rewrite text in RAM after files load, every frame
  (`OPT-005` design).
- The main V-blank-in handler (`0x0600C13C`, `SYS.BIN` at `0x06002000`)
  saves every register and calls `0x0600CB5C` through the literal at
  `0x0600C1C0`.
- That handler is installed by frame ~1,704, before the font tail loads,
  so its code cannot be called directly.
- `0x0600CB5C` itself calls `MM.BIN` routines, so `MM.BIN` is resident
  whenever the handler runs. `MM.BIN`'s dead state-2 routine is intact in
  every unpatched state with that handler, including an ending and its
  credits (`sp004`).

## Hypothesis

With the literal pointing to a guard in the dead routine
(`0x0601E232`), the guard calls the tail's `vblank` routine once its first
long matches the built signature, and otherwise calls `0x0600CB5C` directly.
The game boots and runs as before.

## Controlled Change

- **`tools/text/options_submenu.py`:**
  - `MM.BIN` `0x572C`-`0x5753` (40 bytes, from
    `d90a6192…4f26000b`): the state-2 trampoline (6 bytes), the guard
    (16 bytes), a pad, and four literals (submenu, vblank, signature,
    `0x0600CB5C`);
  - `SYS.BIN` `0xA1C0`: `0600CB5C` → `0601E232`.
- **`data/opt004/submenu.s`:** `vblank` adds 1 to `frames` (in the tail)
  and jumps to `0x0600CB5C`.
- **The image:** the US release spec plus `--options-submenu`
  (`local/opt005/us_guard.json`), `build/opt005/us_guard`. Payload 704
  bytes at `0x027BF2A0`.

## Prediction

- The only writes to the guard or the literal are the boot loads.
- `frames` stays 0 until the font loads, then grows by one per main-handler
  frame.
- The game reaches the title and the attract loop.

## Procedure

1. `guard_watch.py`, 20,000 frames: write breakpoints (log mode) on
   `0x0601E22C`-`0x0601E253` and `0x0600C1C0`-`0x0600C1C3`; the handler
   and a screenshot every 1,000 frames.
2. A second boot: a state every 100 frames from 1,800 to 3,000; `frames`
   read from each state's cart RAM.

## Actual Result

- **Write log:** 1,006 hits, all in frames 1,003-1,655, from the boot
  loaders (PCs `0x0605717E`, `0x060572C6`, `0x06041018`, `0x060037B4`, …).
  None after frame 1,655 through 20,000.
- **Handler:** `0x06056F60` at frame 1,004 and `0x0600C13C` at 2,004; from
  about 2,300 it is `0x0602141C` (the attract loop) through frame 20,000.
- **Counter:**

  | Frame | Handler | `frames` |
  | --- | --- | --- |
  | 1,800-2,105 | `06056F60` / `0600C13C` | 0 |
  | 2,205 | `0600C13C` | 35 |
  | 2,305-3,005 | `0602141C` | 44 |

  The font loaded at about frame 2,170 in this boot, and the load writes
  the tail, counter included. From then on, `vblank` ran once per
  main-handler frame. Before then the guard fell through.
- **No crash:** the game ran the boot, the title and 17,000 frames of
  attract.

## Conclusion

**CONFIRMED:** the guarded hook runs the tail's code every frame the main
V-blank handler is active, from the moment the tail is present, and falls
through safely before that. Its two `MM.BIN`/`SYS.BIN` sites are written
only by the boot loads.

## Uncertainty and Alternatives

- **The attract loop** uses another handler (`0x0602141C`), so the hook
  does not run there.
- **The signature** is one long: random cart RAM matching it before the
  load has odds of 1 in 2^32 per boot.
- **Gameplay** (fights, endings) was not reached in this run. The `OPT-005`
  state survey found `0x0600C13C` in 37 of 43 states from fights, Options
  and an ending.

## Reproduction

```bash
CUE="build/opt005/us_guard/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python research/experiments/EXP-0111/guard_watch.py "$CUE" local/opt005/guard \
  --frames 20000 --shot 1000
```
