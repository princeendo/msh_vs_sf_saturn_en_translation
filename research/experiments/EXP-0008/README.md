# EXP-0008: Validate Save-State Region Extraction

Task: `DBG-012`
Date: 2026-10-15
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0007` produced a slot-2 state and stock debugger dumps of High Work RAM, Low
Work RAM, VDP1 VRAM, and VDP2 VRAM, all taken during one frame-advance pause.
`tools/memory/mcs_extract.py` (`DBG-006`) parses the state layout written by
Mednafen 1.32.1 `src/state.cpp`. The state's 16-bit arrays are written as host
native elements, and this host is little-endian. The debugger reads these spaces
with `ne16_rbo_be`, which yields Saturn big-endian bytes.

## Hypothesis

Swapping each 16-bit element of the stored arrays (`--byte-order saturn`)
reproduces the debugger dumps byte for byte. The unswapped stored bytes
(`--byte-order state`) do not.

## Controlled Change

The input state and dumps are unchanged. The only variable is the byte-order
transformation applied to the extracted regions.

## Prediction

For WRAM-H, WRAM-L, VDP1 VRAM, and VDP2 VRAM:

- the `saturn`-order extraction has the same SHA-256 as `wram-c.bin`,
  `wraml-b.bin`, `vdp1vram-a.bin`, and `vdp2vram-a.bin` respectively;
- the `state`-order extraction differs from the dump wherever the two bytes of a
  16-bit element differ.

Cartridge RAM has no debugger dump and remains unvalidated by this experiment.

## Inputs and Provenance

- State: ignored
  `local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc2`,
  3,848,175 bytes, SHA-256
  `2c735816da8fcb2dbcc63b62da05454a07994f3f08ba56239fbe5fa829c65eb9` (`EXP-0007`
  slot 2, saved during the frame-advance pause).
- Reference dumps (ignored, `local/mednafen/dumps/`, from the same pause):
  `wram-c.bin` (High Work RAM), `wraml-b.bin` (Low Work RAM), `vdp1vram-a.bin`,
  and `vdp2vram-a.bin`. Hashes are recorded in `EXP-0007`.
- The emulator, source image, and BIOS identities are as recorded in `EXP-0007`.

## Tools and Environment

- `tools/memory/mcs_extract.py` (`DBG-006`), Python 3.12.13 via `./invenv.sh`, uv
  0.11.7, macOS arm64 (little-endian host).
- `cmp` and `shasum -a 256` for comparisons.

## Procedure

1. Run `--list` on the state to confirm that the header and all sections parse.
2. Extract every region in `saturn` order and in `state` order to the ignored default
   directory `research/memory_dumps/2c735816da8fcb2d/`.
3. Compare each region with its dump using `cmp`. Count differing bytes for the
   `state`-order outputs.
4. Re-extract to a scratch directory and compare for determinism.

## Actual Result

The state header reported version `0x103201`, little-endian variable data, and a
302x240 preview. All sections parsed to the declared total length of 9,159,854
bytes. Variable sizes were `MAIN/WorkRAML` and `MAIN/WorkRAMH` at 1,048,576 bytes
each, `CART_EXTRAM/LO` and `HI` at 2,097,152 each, and `VDP1/VRAM` and `VDP2/VRAM`
at 524,288 each.

| Region | `saturn`-order SHA-256 | Debugger dump | `cmp` | `state`-order differing bytes |
| --- | --- | --- | --- | ---: |
| `wram_h` | `5e7c2347ddf805da44fddafe7f663bbb23d8896a7014bcbea9a4f4790f94ead0` | `wram-c.bin` | identical | 554,066 |
| `wram_l` | `0cb95fbf577923bfc2729e5d5303b2200a6ea9e9d77dcbdde39dddbecd4f9a5c` | `wraml-b.bin` | identical | 574,942 |
| `vdp1_vram` | `173764195179ce178ff8475c7c82d51dd17bd7e3014fa2e025f58d2a18a8894d` | `vdp1vram-a.bin` | identical | 214,932 |
| `vdp2_vram` | `fa94f7ca4c62267bf05f97a492ef91c3f82aa6a3b7ec676215446b7724360b0f` | `vdp2vram-a.bin` | identical | 172,764 |
| `cart_ram` | `eeaa16c834fecfdc7f531a37973363a9389de7ee07ac2ef9205bce6ae0c790cb` | none available | not tested | — |

The manifests are `manifest.json` (SHA-256
`1710743301eb065f67b8d6f1665091d524c2c867c45ec818d16a1aef3b887c63`) and
`manifest.state-order.json`. A second extraction produced byte-identical files for
all five regions.

## Conclusion

`CONFIRMED`: for stock Mednafen 1.32.1 states on a little-endian host, extracting
WRAM-H, WRAM-L, VDP1 VRAM, and VDP2 VRAM with 16-bit element swapping reproduces the
stock debugger dumps of the same paused instant byte for byte. The unswapped
alternative is `DISPROVEN`. This also shows that the slot-2 state, saved with `F5`
during frame advance, captured the same instant as the dumps.

Cartridge RAM extraction remains `HYPOTHESIS`. It uses the same `uint16` storage and
element swap, according to `ss/cart/extram.cpp`, but no independent stock reference
exists to compare it against.

## Uncertainty and Alternatives

- One state at a title/menu scene was tested. Other scenes use the same code path,
  but the validation covers the tested state only.
- Big-endian hosts set the header's big-endian flag, and the tool then skips the
  swap. That path is covered by a synthetic test only.
- Validating cartridge RAM needs some independent observation. One option is a
  known value the game writes to a cart address, observed through CPU disassembly
  or a write breakpoint.

## Reproduction

```bash
S="local/mednafen/mcs/Marvel Super Heroes vs. Street Fighter (Japan).0eac041df6b7d4ca563f4c35017eea24.mc2"
./invenv.sh python -m tools.memory.mcs_extract "$S" --list
./invenv.sh python -m tools.memory.mcs_extract "$S"
./invenv.sh python -m tools.memory.mcs_extract "$S" --byte-order state
cmp research/memory_dumps/2c735816da8fcb2d/wram_h.bin local/mednafen/dumps/wram-c.bin
cmp research/memory_dumps/2c735816da8fcb2d/wram_l.bin local/mednafen/dumps/wraml-b.bin
cmp research/memory_dumps/2c735816da8fcb2d/vdp1_vram.bin local/mednafen/dumps/vdp1vram-a.bin
cmp research/memory_dumps/2c735816da8fcb2d/vdp2_vram.bin local/mednafen/dumps/vdp2vram-a.bin
```
