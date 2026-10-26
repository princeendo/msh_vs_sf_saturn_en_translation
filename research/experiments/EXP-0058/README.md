# EXP-0058: The name-call tables and a switch to the US calls

Task: LOC-005 (find what chooses the name call and how to switch it)
Status: DONE
Confidence: CONFIRMED (table A drives the win-screen name call; the live
switch to "Bison"); HYPOTHESIS (the use of table B)

## Observation

- `EXP-0057`: on the win screen the mixer plays "Vega" (`0x286`). The disc
  also holds the US calls: "Bison" `0x04F`, "Akuma" `0x338` and "Cyber Akuma"
  `0x05B`.
- The project's character indexes put Vega at 14, Gouki at 15 and
  Mech-Gouki at 19.

## Hypothesis

A per-character table of sound IDs selects the name call. Changing Vega's
entry to `0x04F` makes the win screen play "Bison".

## Controlled Change

One 16-bit write in sound RAM after the win-banner state loads. Nothing else
changes: same state, same image, same frame count.

## Prediction

The clip started at the frame where `0x286` started (frame 242/243 of the
replay) becomes `0x04F`.

## Inputs and Provenance

- Image: `build/ui001/image_a`.
- State: `local/end024v/rec/states/f00008316.mcs` (the Vega + Ryu win
  banner).
- `MEMFIX.PAC` from source track 01.

## Tools and Environment

- A scratch search (Python 3.12.13) for u16/u32 tables with Vega = `0x286`
  at index 14, Gouki = `0x048` at 15 and Mech-Gouki = `0x082` at 19. It
  covered WRAM-H, WRAM-L, cart RAM and all `.PAC`, `.BIN`, `.PRG` and `.DAT`
  files, at strides 2-16.
- `tools/audio/mixer_log.py` with the new `--poke SPACE:ADDRESS:HEX` option.
- Patched Mednafen 1.32.1 agent interface: the `scspram` space read back the
  poke correctly.

## Procedure

1. The table search found `MEMFIX.PAC` `0x124B54` (16-byte records).
2. `MEMFIX.PAC` payload 7 (file `0x123BB8`, `0x3BC0` bytes) is loaded
   byte-identical into sound RAM at `0x6510`, in every checked state from
   character select to the ending. It holds two tables with the same 23 IDs:

   | Table | Sound RAM | `MEMFIX.PAC` | Record | Fields |
   | --- | --- | --- | --- | --- |
   | A | `0x73B6` | `0x124A5E` | 10 bytes | ID, `0031`, `0020`, `07xx`, `8xxx` |
   | B | `0x74AC` | `0x124B54` | 16 bytes | ID, `0030`, `0030`, `0004`, `0006`, `8020`, `07xx`, `8xxx` |

   The IDs in both tables, by index:

   ```text
   0:1CB 1:051 2:1AA 3:069 4:08A 5:00C 6:24E 7:162 8:072 9:31C 10:057 11:2C8
   12:2FD 13:05D 14:286 15:048 16:046 17:061 18:31D 19:082 20:04F 21:338 22:05B
   ```

   Index 14 is "Vega", 15 "Gouki" and 19 "Mech Gouki". Indexes 20, 21 and 22
   are the US calls "Bison", "Akuma" and "Cyber Akuma".
3. Trial on table B: `mixer_log ... f00008316 ... --poke scspram:758C:004F`
   (entry 14). The win call was still `0x286`. A read breakpoint on table B
   for 300 frames logged no SH-2 reads.
4. Trial on table A: `mixer_log ... f00008316 ... --poke scspram:7442:004F`
   (entry 14).

## Actual Result

- **Table B poke:** no change (`0x286` at frame 242).
- **Table A poke:** at frame 242, channel 10 starts `pl0e_1#1` (`0x04F`,
  "Bison"), where the baseline started `0x286` "Vega". The other starts
  (`CMNSE` `0x321` at 267, `MEMFIX` `0x088` at 354) are unchanged.

## Conclusion

- **CONFIRMED:** table A (sound RAM `0x73B6`, from `MEMFIX.PAC` `0x124A5E`)
  chooses the win-screen name call by character index. Setting Vega's entry to
  `0x04F` plays "Bison" in place of "Vega". Nothing else changed.
- **The US switch, as data.** Copy entries 20-22 into 14, 15 and 19:

  | Character | Table A file offset | Table B file offset | Japanese | US |
  | --- | --- | --- | --- | --- |
  | Vega → Bison (14) | `0x124AEA` | `0x124C34` | `0286` | `004F` |
  | Gouki → Akuma (15) | `0x124AF4` | `0x124C44` | `0048` | `0338` |
  | Mech-Gouki → Cyber-Akuma (19) | `0x124B1C` | `0x124C84` | `0082` | `005B` |

  These are offsets in `MEMFIX.PAC` (big-endian u16). No new audio is needed.
- **HYPOTHESIS:** table B serves another occasion, probably character select.
  Switching both tables keeps the variants consistent. It is untested.

## Uncertainty and Alternatives

- Tested only for Vega, only on the win screen, and only by a live poke into
  sound RAM. The disc patch has not been built or cold-booted.
- `MEMFIX.PAC` payload 7 is loaded at boot, so state replays do not pick up a
  disc change. Verifying a built image needs a cold boot and play: character
  select and a win with Vega, Gouki and Mech-Gouki.
- Whether indexes 20-22 are ever used (for example by a region setting) is
  unknown.

## Reproduction

```bash
./invenv.sh python -m tools.audio.mixer_log "build/ui001/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" local/end024v/rec/states/f00008316.mcs local/loc005/win8316 --frames 450
./invenv.sh python -m tools.audio.mixer_log "build/ui001/image_a/Marvel Super Heroes vs. Street Fighter (Japan).cue" local/end024v/rec/states/f00008316.mcs local/loc005/win_bison_a --frames 300 --poke scspram:7442:004F
```

Compare `starts.json` in the two folders: the start at frame 242/243 changes
from `0x286` to `0x04F`.
