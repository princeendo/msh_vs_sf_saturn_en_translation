# EXP-0108: SH-2 code runs from cart RAM (OPT-004)

Task: OPT-004
Status: DONE
Confidence: CONFIRMED (patched checkpoint; the `OPT-004` build gives the
cold-boot check)

## Observation

`EXP-0107` confirmed the quote font's tail as a home for a payload at a
fixed cart address. Whether the SH-2 can execute code there (the A-bus), or
the code must first be copied to work RAM, was untested.

## Hypothesis

An Options row handler placed in cart RAM is called and returns like the
game's own handlers.

## Controlled Change

One recorded Options state, with two writes (`tools.memory.mcs_patch`):

| Region | Address | Original | Modified | Purpose |
| --- | --- | --- | --- | --- |
| cart RAM | `0x027BB6A0` | zero (that build had no tail) | `counter.s`, 20 bytes `d1036012…060fa000` | a handler that adds 1 to the long at `0x060FA000` and returns with `lds.l @r15+,pr; rts` |
| WRAM-H | `0x0601E960` | `0601DFDE` | `027BB6A0` | row 0's handler in the Options row table (`EXP-0105`) |

`0x060FA000` was zero in all 474 recorded states (`EXP-0105`).

## Prediction

- With the cursor on row 0, the main input routine calls the handler once
  per frame (`jsr @r8` at `0x0601DF86`).
- The counter grows by one per frame, and the menu keeps running.

## Inputs and Provenance

- **State:** `local/loc006/play/rec/states/f00003213.mcs` (`aa1844a1…0ca3`),
  OPTION MODE. Cursor `0x06017A88` = 0, state `0x06017A84` = 0.
- **Disc loaded:** the control image `build/opt003/us` (track 01
  `b2e526a7…`, the US release).
- **Assembler:** `tools/sh2/asm.py` (new). It reassembles every disassembled
  form to the same opcode (unit test over all 65,536 opcodes) and the
  Options menu code `0x0601DB00`-`0x0601E7A0` to the same bytes (1,383
  instructions; 2 unsupported forms).

## Procedure

```bash
./invenv.sh python -m tools.sh2.asm research/experiments/EXP-0108/counter.s \
  --origin 0x027BB6A0 --out local/opt004/exec/counter.bin
printf '\x02\x7b\xb6\xa0' > local/opt004/exec/handler.bin
./invenv.sh python -m tools.memory.mcs_patch local/loc006/play/rec/states/f00003213.mcs \
  local/opt004/exec/s1.mcs --region cart_ram --address 0x027BB6A0 \
  --data local/opt004/exec/counter.bin
./invenv.sh python -m tools.memory.mcs_patch local/opt004/exec/s1.mcs \
  local/opt004/exec/patched.mcs --region wram_h --address 0x0601E960 \
  --data local/opt004/exec/handler.bin
```

The agent Mednafen (quiet home) then booted the control image for 300
frames, loaded `patched.mcs`, ran 120 frames, and read `0x060FA000`.

## Actual Result

- Frames 306 → 426: the counter went from 1 to 121, one call per frame.
- The handler pointer read back `027BB6A0`; state 0, cursor 0.
- The screenshot (`local/opt004/exec/after.png`) shows OPTION MODE drawn
  normally.

## Conclusion

**CONFIRMED (checkpoint):** the SH-2 executes code in cart RAM, called
through the game's own row-handler pointer and returning with the game's
calling convention (PR pushed in the caller's delay slot, popped by the
callee). The sub-menu code can stay in the font tail with no copy to work
RAM.

## Uncertainty and Alternatives

- **Patched state only:** this is a checkpoint that mixes two builds
  (`mcs_patch`). The `OPT-004` image gives the cold-boot check.
- **Speed:** A-bus fetches are slower than work RAM. A once-per-frame menu
  routine is far from any limit; time-critical code was not tested.

## Reproduction

The Procedure, then the Mednafen steps above. `counter.s` is in this
directory.
