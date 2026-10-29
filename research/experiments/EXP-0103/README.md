# EXP-0103: The no-cartridge warning is the BMP file `ERR5.BIN`

Task: UI-008
Status: DONE
Confidence: CONFIRMED (a single-file marker showed at exactly its rows)

## Observation

- **User report (2026-10-29):** a player said "the very first page is still
  in Japanese".
- **Cold boots of the released 0.1.0 image** (American names, track 01
  `c6f1fbd0…`), frames 30-1500 every 30, no input
  (`tools/mednafen/frame_capture.py`):
  - **with the 4 MB cart** (`Cart: 4MiB Extended RAM`): black, the SEGA
    licence screen, then the CAPCOM logo. No Japanese;
  - **with no cart** (`ss.cart none`, `Cart: None`): after the SEGA screen
    the game stops on a Japanese warning, unchanged from frame 600 to 1500:
    "警告 / 4M拡張ラムカートリッジが差し込まれていません。/ 電源を切り、
    4M拡張ラムカートリッジを差し直してください。" ("The 4M Extended RAM
    Cartridge is not inserted. Turn off the power and reinsert it.")
- **On the disc**, `ERR1.BIN`-`ERR5.BIN` (42,358 bytes each, LSNs 12436,
  12457, 12478, 12499, 12520) are Windows BMPs: a 118-byte header and
  16-colour palette, then 352x240 4 bpp pixels, bottom-up. Viewed as images
  they are five Japanese warnings:

  | File | SHA-256 | Warning |
  | --- | --- | --- |
  | `ERR1.BIN` | `29461446…` | internal backup memory not formatted; format it in the Saturn's save-data screen; a button goes to the BIOS screen |
  | `ERR2.BIN` | `125a33a8…` | saved data could not be read; the old data will not be used |
  | `ERR3.BIN` | `4315c728…` | not enough free space for new data; 8 free needed |
  | `ERR4.BIN` | `1941080c…` | 4M cartridge not inserted correctly |
  | `ERR5.BIN` | `0732e81d…` | 4M cartridge not inserted (the screen seen) |

  All five have the same palette: 0 black, 1-6 grey to white, 7-10 cyan,
  11-12 yellow, 13-14 red, 15 green (unused).

## Hypothesis

The no-cart screen is `ERR5.BIN`'s pixels, drawn as they are.

## Controlled Change

One file, `ERR5.BIN`: BMP rows 200-219 (top-down; file offsets `0xE36`-
`0x1BF5`, 3,520 bytes, all `00` before) set to `EE` (palette 14, red). The
header, palette and every other byte are unchanged.

- Marker file: `local/ui008/exp0103/ERR5_marker.BIN`, `5ca702ae…`.
- Image: `build/ui008/exp0103_marker/`, track 01 `beae54d5…`, built from the
  untouched source by `tools/disc/patch_image.py`.

## Prediction

The no-cart boot shows a red band across the warning screen, 20 rows high;
the untouched source shows none.

## Inputs and Provenance

- Source image: `local/disc_images/mshvsf_saturn_jp/` (manifest
  `references/mshvsf/saturn_jp/README.md`).
- Files extracted with `tools/disc/iso9660.py --extract local/ui008/disc`.

## Tools and Environment

- Agent-patched Mednafen 1.32.1 (`vendor/mednafen/build-agent`), JP BIOS
  `sega_101.bin`.
- No-cart home: a copy of `local/mednafen_quiet` with `ss.cart none`, at
  `local/ui008/home_nocart` (firmware symlinked).

## Procedure

```bash
./invenv.sh python -m tools.disc.patch_image \
  --source-dir local/disc_images/mshvsf_saturn_jp \
  --manifest references/mshvsf/saturn_jp/README.md \
  --track "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin" \
  --file "ERR5.BIN;1" --data local/ui008/exp0103/ERR5_marker.BIN \
  --out-dir build/ui008/exp0103_marker
./invenv.sh python -m tools.mednafen.frame_capture \
  "build/ui008/exp0103_marker/Marvel Super Heroes vs. Street Fighter (Japan).cue" \
  local/ui008/exp0103/marker --home local/ui008/home_nocart \
  --first 900 --last 1500 --step 300
```

The same capture of the source image went to `local/ui008/exp0103/source`.

## Actual Result

- **Source:** the Japanese warning at frames 900, 1200 and 1500, identical
  (`d4266c3a…`).
- **Marker:** the same warning with a red band near the bottom, at frames
  900, 1200 and 1500, identical (`f9d042af…`).
- **Pixel check:** the marker screenshot equals the marker BMP drawn with its
  own palette and shifted up 8 rows (screen y = BMP y - 8), with 0
  mismatched pixels. The best other offsets matched 93%.

## Conclusion

**CONFIRMED:** the no-cart warning is `ERR5.BIN` drawn as it is, with the
file's palette (or an identical one). The game shows BMP rows 8-239. A
same-size `ERR5.BIN` with new pixels changes the screen.

## Uncertainty and Alternatives

- Whether the game reads the BMP's palette or its own copy is not tested.
  The English build keeps the palette, so it does not matter.
- `ERR1`-`ERR4` are assumed to use the same path. They are checked one by one
  in `EXP-0104` where Mednafen can trigger them.

## Reproduction

The commands above. Binary evidence stays local: `local/ui008/exp0103/`.
