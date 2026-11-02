# EXP-0112: NAMES switches the resident name sites at run time (OPT-005)

Task: OPT-005
Status: DONE (resident sites); the character-slot and ending sites need
gameplay (the user's session)
Confidence: CONFIRMED (cold boot, unattended, RAM read back)

## Observation

- `--names-switch` builds the American image with a site table in the font
  tail: 42 sites (`tools/text/names_switch.py`).
- The V-blank hook runs every main-handler frame (`EXP-0111`).

## Hypothesis

With NAMES (`0x06017AB4`) = 1, every resident site holds its Saturn bytes
within a frame of the hook running. With 0, the American bytes return.
Sites whose file is not loaded are left alone.

## Controlled Change

- **The image:** the US release arguments plus `--options-submenu
  --names-switch`.
  - Spec `local/opt005/names2.json` (`names.json` with two fixes below),
    built to `build/opt005/names2`.
  - Payload 4,380 bytes at `0x027BDEA0`, in a 6 KiB tail; 173 kanji
    sacrificed, 587 pairs (both name sets).
- **The sites:** 26 resident (20 in `MM.BIN`, 6 name calls in sound RAM),
  10 in the ending's `ME.PAC` area, 6 in the character slots.
- **The test:** `switch_watch.py` boots the image. From frame 2,100 it
  writes NAMES every 5 frames: first 1 until every resident site reads its
  Saturn bytes, then 0 until they read American. Sound RAM is read through
  the agent's `scspram` space.

## Prediction

20 → Saturn (and the 6 calls once sound RAM is loaded), then back.

## Actual Result

### Two faults found and fixed on the way (first image, `names.json`)

1. **Sound RAM writes did not land.**
   - The routine's copy ran every frame for the six calls (PC breakpoints
     on its loops: probe and full compare matched, and the copy stored
     `0x0286` at `0x05A07442`).
   - Sound RAM still read `004F` the next frame, so a store through the
     cached alias (`0x05A…`) does not reach sound RAM.
   - Fix: the copy also stores through the cache-through alias
     (`0x25A…`).
2. **The sub-menu's own patches were taken for name sites.**
   - The Saturn spec is generated without `--names-switch`, so it uses the
     1 KiB tail, and its sub-menu patches hold other addresses.
   - Three of them (the guard, the row-8 handler, the PRESS A OR C
     pointer) became "sites": selecting Saturn would have pointed the guard
     elsewhere.
   - The compiler's check ("the built bytes are not the American ones")
     caught it on the next build. `alternates` now skips patches tagged
     `OPT-004`, with a unit test.

### The run (`names2`)

| From frame | NAMES | Resident sites |
| --- | --- | --- |
| 2,100 | (0) | 20 American, 0 Saturn (sound RAM not yet loaded) |
| ~2,170 (tail loaded) | 1 | 0 American, 20 Saturn |
| after the name calls load | 1 | 0 American, 26 Saturn |
| next step | 0 | 26 American, 0 Saturn |

The 10 `ME.PAC` sites held neither variant: no ending is loaded, and
nothing was written there.

## Conclusion

**CONFIRMED (cold boot):** the NAMES setting switches every resident name
site, the `MM.BIN` text and pointers and the sound-RAM name calls, both
ways, within a few frames. Sites whose file is not loaded are left alone.

## Uncertainty and Alternatives

- **Not yet seen:**
  - the character-slot sites (MC00 exchanges, MC0F quotes) and the ending;
  - what the switch looks and sounds like on screen.

  Both need the user's session.
- **The attract loop** runs another V-blank handler, so the hook is idle
  there. In the earlier run, some `MM.BIN` sites read neither variant during
  attract (the attract reuses that RAM), and they are rewritten when the
  main handler is back.
- **The second fault in the names image (`names.json`)** was only exercised
  in this test window. That image is superseded.

## Reproduction

```bash
CUE="build/opt005/names2/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue"
./invenv.sh python research/experiments/EXP-0112/switch_watch.py "$CUE" \
  build/opt005/names2/files/MEMFIX.PAC local/opt005/switch2 --start 2100 --end 2300 --step 5
```
