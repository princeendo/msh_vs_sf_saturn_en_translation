# EXP-0068: The attract streams (`MVSOP*.ST2`), their LZ codec, and the caption tiles and maps

Task: UI-003 (decoding the art source)
Status: DONE (decoding and extraction). The map codecs are traced but not
reimplemented.
Confidence: CONFIRMED (the container and the graphics LZ decoder reproduce
RAM byte for byte; the caption pages render as on screen)

## Observation

`EXP-0066`:
- the four attract captions are VDP2 4bpp tiles;
- an LZ decompressor at `0x06021F0C` writes them to WRAM-H `0x06080000`+;
- the input is in all eight `MVSOP*.ST2` files.

## Hypothesis

The `.ST2` files are containers. The decompressor's format can be read from
the code. The caption maps can be traced to their own source.

## Controlled Change

None to the game. Disassembly, state reads, write and PC breakpoints, and an
offline decoder checked against RAM.

## Prediction

An offline decoder applied to the disc data reproduces the tiles the game
writes. The tiles plus the VDP2 map render each caption as on screen.

## Inputs and Provenance

- `MVSOP0`-`MVSOP7.ST2` and `MVSOPEN.BIN` from source track 01.
- Cycle states (`EXP-0066`).
- Caption states `local/ui003/cap1`-`cap4.mcs`, at frames 2532+142,
  5647+203, 3154+293 and 12501+113.

## Tools and Environment

- New `tools/disc/st2_stream.py` (container, `MISS` stream, graphics LZ).
- New `tools/memory/vdp2_plane.py` (VDP2 page extraction and render).
- `tools/sh2/disasm.py`; patched Mednafen 1.32.1 agent. Python 3.12.13.

## Procedure

1. Disassemble the decompressor (entry `0x06021EDA`). Read its source and
   destination pointers (`0x06021FC4`, `0x06021FC8`) in a state just before it
   runs.
2. Implement the decoder. Find the input block on disc, decode it, and compare
   with RAM.
3. Read the `.ST2` header and the sector tags. Halt at each decompressor call
   (PC `0x06021EE8`) during captions 3 and 4, dump the input blocks, and find
   them on disc.
4. Find the caption layer from the VDP2 registers and VRAM; render each
   caption page.
5. Trace the map: write breakpoints on its RAM sources. Disassemble the map
   builder and both map codecs. Locate the map codec's input on disc.

## Actual Result

- **Graphics LZ** (`0x06021EDA`-`0x06021F56`):
  - header: u32 compressed size, u32 decompressed size;
  - flag bytes MSB first: 0 = literal byte; 1 = big-endian word `w`, copying
    `(w & 0xF) + 3` bytes from `(w >> 4) - 0x1000` back;
  - the routine yields between flag bytes, so it runs across frames.
  - **Verified:** decoding the RAM input reproduces the caption tile region at
    WRAM-H `0x06086020`+ byte for byte, and the tool decodes the disc copy
    identically.
- **`.ST2` container:**
  - header sector: up to eight u32 section sizes. `MVSOP*` has three:
    - A: map streams, loaded to WRAM-L `0x2C0000`;
    - B: an event table;
    - C: one graphics block, e.g. at `MVSOP1` `0x4B800`.
  - after the sections, 0x800-byte sectors. `MISS`-tagged sectors carry
    0x7FC bytes of a graphics stream; the other sectors are interleaved data
    (probably audio). `MVSOP6` has 564 `MISS` sectors, with 11 blocks in the
    stream.
  - the game decodes about one stream block every 60-90 frames, alternating
    WRAM-L `0x240000` and `0x260000`.
  - **Verified:** `MVSOP6` stream block 5 equals the block dumped at
    caption 3's decode.
  - each decoded block begins with a table of u32 part offsets (tiles,
    palette, …).
- **Caption layer:**
  - NBG2: 16 colours, 2x2-cell characters, 2-word pattern names, plane A page
    0 at VDP2 VRAM `0x70000`, colour-RAM offset 6;
  - it comes from WRAM-H `0x06050000` by DMA. The vertical scroll picks the
    caption: ヴァリアブル / ヒーロー / バトル and 第2弾!! share one page.
- **Map path** (traced; not reimplemented):
  1. Section A (WRAM-L `0x2C0000`) is read by a bit-flag LZ (`0x06022750`,
     flags LSB first) into a 0x2000-byte ring at `0x06028020`.
  2. The ring is read by a word LZ (`0x0602234C`). Its control bits are LSB
     first: 1 = a literal word; 0 = a copy (a negative byte = short form; a
     positive byte = length plus a distance byte; zero = a 16-bit form with
     three modes). It writes 0x2000 words per run, skipping `0xFFFF`, to
     arrays at `0x0602F020`, `0x06033020` or `0x06037020`.
  3. The index array (`0x06037020`) and the attribute array (`0x06039020`) go
     to the builder (`0x0601FD70`). Each index n is a 32x32-pixel macro cell:
     2x2 pattern names with characters base + 16n, +4, +8, +12; the base is
     `0x78` for caption 3. The attribute is the palette (5 bits) plus flips.
     The result goes to `0x06050000`.
- **Extraction** (`local/ui003/extract/cap1`-`cap4`: `map.bin`, `tiles.bin`,
  `tiles.json`, `page.png`). The pages render as on screen:

  | Caption | Tile source (in every `MVSOP0`-`7`) | Map SHA-256 |
  | --- | --- | --- |
  | ヴァリアブル ヒーロー バトル | section C (decoded `MVSOP6`/`MVSOP1`: `856664c7…`) | `5e53eb0c…` |
  | 第2弾!! | section C (same page as cap1, lower) | `862e2909…` |
  | 広がれ!! ヒーロー ワールド | one stream block per file (`MVSOP6` block 5: `f28d5272…`) | `38a73e19…` |
  | 解き放て! 友情パワー | one stream block per file (`MVSOP6` block 1: `76888d28…`) | `6bb2a8ab…` |

## Conclusion

**CONFIRMED:**
- the `.ST2` layout and the graphics LZ, with an offline decoder that
  reproduces RAM;
- each caption's tiles and map extracted and rendered.

Every `MVSOP` file carries all four captions: two in section C, two in stream
blocks. So a replacement must be written into all eight files.

## Uncertainty and Alternatives

- The two map codecs (bit-flag LZ, word LZ) are traced but not reimplemented.
  An English replacement whose text fits the existing macro-cell layout needs
  only new tiles. A different layout needs the map encoders.
- A replacement needs a graphics-LZ encoder. Each block's new compressed size
  must fit its sectors (section C: its section size; stream blocks: the
  `MISS` payload space up to the next block), or the stream must be rebuilt.
- The interleaved non-`MISS` sectors are not identified. They must be kept in
  place.

## Reproduction

```bash
./invenv.sh python -m tools.disc.st2_stream local/ui003/st2/MVSOP6.ST2 --out-dir local/ui003/st2/MVSOP6
./invenv.sh python -m tools.memory.vdp2_plane local/ui003/cap3.mcs --out-dir local/ui003/extract/cap3
```

Extract the `.ST2` from the image first, for example with
`tools.audio.sound_bank.disc_files`. The breakpoint and dump scripts were
scratch agent scripts; their parameters are under Procedure.
