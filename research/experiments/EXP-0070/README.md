# EXP-0070: Section A of the attract streams (script, map and palette codecs)

Task: UI-003 (replacement; prerequisite for maps and palettes)
Status: DONE (decoding). The re-encoding approach is pending a user decision.
Confidence: CONFIRMED (the offline decoders reproduce the game's ring
contents and decode the runtime map-update offsets)

## Observation

`EXP-0069`: yellow captions and free layout need the section-A map and
palette data, which pass through a bit-flag LZ (`0x06022750`) and a word LZ
(`0x0602234C`).

## Hypothesis

Section A holds the caption maps and palettes as discrete records. Decoding
it lets those records be found and replaced.

## Controlled Change

None to the game. Disassembly, breakpoints and offline decoding.

## Prediction

The offline decoders reproduce the game's ring buffer. The caption records
appear as full writes of the caption's index, attribute and palette arrays.

## Inputs and Provenance

`MVSOP6.ST2` (section A at `0x800`, `0x28000` bytes). Cycle states
`f001909`, `f003154`; `premap3.mcs` (`f003154` + 205).

## Tools and Environment

`tools/disc/st2_stream.py` (`script_decode`, `map_decode`), patched
Mednafen 1.32.1 agent, `tools/sh2/disasm.py`, Python 3.12.13.

## Procedure

1. Disassemble the bit-flag LZ (`0x06022750`-`0x06022814`), the word LZ
   (`0x0602234C`-`0x06022412`) and their setup (`0x06022658`).
2. Decode `MVSOP6` section A offline. Compare with the ring buffer
   (`0x06028020`-`0x0602A020`) in `premap3.mcs`.
3. Halt at every word-LZ entry (`0x0602234C`) from `f003154` for 300
   frames and from `f001909` for 3,300 frames. Locate the ring read pointer
   (R12) in the decoded script, and decode the update there.
4. Write breakpoints on the palette array (`0x0602EC24`).

## Actual Result

- **Bit-flag LZ (Kosinski-like):**
  - flag bits LSB first; 1 = literal;
  - 0,0 = short copy: 2 bits (MSB first) give length 2-5, then a byte offset
    `b - 0x100`;
  - 0,1 = long copy: word `w`, offset `(w | ~0xFFFF) >> 3`, length
    `(w & 7) + 2`, or a following byte + 1; a byte of 0 ends the stream.
  - **Section A is one stream.** Setup sets the source to WRAM-L
    `0x2C0000` and the start to `0x06022750`; the array area
    `0x0602E020`+ (`0x3C2A` longs) is filled with `0xFFFFFFFF`.
  - `MVSOP6`: `0x27FE8` compressed bytes (`0x18` left in its `0x28000`
    section) decode to a `0x747C0`-byte script. The ring contents are found
    in it.
- **Command stream:** an interpreter (`0x06022426`) reads the script in
  order:
  - a byte of `0xFF` ends a frame's commands;
  - the other commands are object lists (`0x0603D0C8`), palette writes
    (handler `0x06022242`), and map updates.
- **Word LZ (map updates):**
  - control bits LSB first; 1 = literal word;
  - 0 = copy, from a byte b: b ≥ 0x80 short; 0 < b < 0x80 length plus a
    distance byte; b = 0 a long form with three modes;
  - each update is 0x2000 words, and `0xFFFF` means keep;
  - targets `0x0602F020`, `0x06033020`, `0x06037020`. NBG2's index and
    attribute arrays are within the last.
- **The maps and palettes are animated, not stored whole.**
  - From `f003154`, 74 map updates ran in 300 frames, most writing only a
    few words. The update at script `0x33F1C` (frame 202, just before
    caption 3's map build) writes 102 words.
  - Over one cycle from `f001909`, 464 updates ran; 266 did not match
    `MVSOP6`'s script. The cycle draws on other `MVSOP` files, which the game
    rotates through.
  - The palette array is written by handler `0x06022242` almost every frame
    (993 writes in 900 frames), driving the caption fades.

## Conclusion

- **CONFIRMED:**
  - the section-A codecs and its structure: one compressed command script,
    consumed in order;
  - the offline decoders, in `tools/disc/st2_stream.py`
    (`script_decode`, `map_decode`).
- **Cost of free layout.** It means rewriting the per-frame map updates for
  each caption in all eight files' scripts, and re-encoding each section A
  within its `0x28000` bytes, which Capcom's encoder fills to within
  `0x18`.
- **Cheaper path to yellow.** Change the colour values in the caption
  palette commands in place: the script layout stays the same and only the
  values change. Then re-encode, which needs an encoder at least as good as
  the original.

## Uncertainty and Alternatives

- The palette command format (handler `0x06022242`) is not decoded yet.
- Whether a better compressor gains enough room is unknown until an encoder
  exists.
- The game's choice of `MVSOP` file per cycle is not decoded. All eight carry
  the same captions.

## Reproduction

```python
from tools.disc.st2_stream import sections, script_decode, map_decode
st2 = open("local/ui003/st2/MVSOP6.ST2", "rb").read()
a0, asz = sections(st2)[0]
script, end = script_decode(st2[a0:a0 + asz])  # 0x747C0 bytes, end 0x27FE8
words, end = map_decode(script, 0x33F1C)
```
