# EXP-0055: Decode the common sound bank `CMNSE.PAC`

Task: LOC-005 (its first blocker: decode the bank and export the clips)
Status: DONE
Confidence: CONFIRMED (bank layout and decoder); clip identities UNKNOWN until
the user listens

## Observation

- `EXP-0054` showed that sound is mixed in software and streamed through three
  looping SCSP slots (`0x484`, `0x248C`).
- At the win screen, sound RAM holds a large block of `CMNSE.PAC`, the likely
  announcer bank.
- The user hears "Vega" at character select and in the win announcement.
- `CMNSE.PAC` (358,164 bytes, SHA-256 `2123cab2…dbb723`, LSN 3582) has:
  - a u32 count of 88 at `0x10`;
  - 88 (u16 tag, u16 length) entries from `0x14`;
  - concatenated data from `0x174`. The lengths sum to `0x5759D`, which ends
    3 bytes before the end of the file.
- The data is 4-bit ADPCM: silence is runs of nibbles 0 and 8.

## Hypothesis

The clips are decoded by game code that can be found and transcribed exactly.
The transcription is right if, replaying each mixer channel's data from its
start, it reproduces the predictor and step the game stored for that channel.

## Controlled Change

None to the game. Analysis only. The change between candidate decoders is the
algorithm alone; the input bytes are the same.

## Prediction

For every active mixer channel in a recorded state, decoding the bytes from
the channel's start to its cursor, from predictor 0 and step `0x80`, gives
exactly the stored (predictor, step).

## Inputs and Provenance

- Source track 01 (hash in `references/mshvsf/saturn_jp/README.md`). The tool
  reads `CMNSE.PAC;1` from it.
- States: `local/end024v/rec/states/*.mcs` (44 states from the `END-024`
  Vega recording; `f00009368.mcs` is the reference instant).
- `local/loc002/snd_win/st*.mcs`: the `EXP-0054` win-screen SCSP trace, used
  only for the abandoned ring-buffer matching below.

## Tools and Environment

- Mednafen 1.32.1 save states, parsed with `tools/memory/mcs_extract.py`.
  WRAM-H is a validated region (`DBG-012`). Sound RAM (`SCSP`/`RAM`, swapped
  to bus order) and cart RAM are not validated against a debugger dump.
- Python 3.12.13 (`./invenv.sh`), `tools/sh2/disasm.py`.
- Scratch analysis only: numpy and capstone, through `uv run --with` (uv
  0.11.7). They are not project dependencies.

## Procedure

1. **Standard decoders.** IMA, OKI and Yamaha ADPCM, high or low nibble first,
   were tried on every clip. All drifted, with a mean |DC| / peak of
   0.27-0.41 per 256-sample window.
2. **Step-table search.** Searched sound RAM, WRAM-H and WRAM-L for the IMA,
   OKI and Yamaha tables (u8, u16, u32; both endiannesses; partial runs) and
   for any symmetric 16-entry delta table or geometric step table. Nothing
   was found.
3. **68K driver.** The only nibble operations in sound RAM `0`-`0xB000`
   (`0x46B8`-`0x4774`) belong to the sequencer, not to a sample decoder.
4. **SH-2 mixer.** WRAM-H holds the ring-buffer addresses `0x05A00484` and
   `0x05A0248C` as literals (`0x0600D2F0`, `0x0600DDCC`). Disassembling around
   them (`tools/sh2/disasm.py --base 0x06000000 --start 0x0600D300 --end
   0x0600D480`) gave:
   - `0x0600D338`: the channel loop. It walks 16 channels (`mov #16` at
     `0x0600D33E`) with an active mask at `0x060132D4`. Records are 44 bytes,
     from the pointer at `0x06012B6C`. It reads each byte and decodes the high
     nibble, then the low one.
   - `0x0600D420`: the per-nibble decoder:

     ```text
     T = !(n & 8); m = n & 7
     d = (step * m) >> 2          ; muls.w, shlr2
     pred += T ? d : -d           ; no clamp
     step = (step * MUL[m]) >> 16 ; MUL at 0x0600D46C
     step = clamp(step, 0x80, 0x6000)
     out += (pred * vol) >> 16    ; left and right accumulators, stride 8
     ```

     `MUL` = `E666 E666 E666 E666 13333 1999A 20000 26666` (0.9, 0.9, 0.9, 0.9,
     1.2, 1.6, 2.0, 2.4).
   - `0x0600D4AA`: copies each accumulator into the next slot, so every
     decoded sample is played twice.
   - `0x0600D300`: clamps and writes the mix to the ring buffers 1:1.
5. **Rate.** The ring slots play at octave -1, FNS 92 (`EXP-0054` slot
   trace), which is 44,100 × 2^-1 × (1 + 92/1024) = 24,031 Hz. With each
   sample doubled, clips play at 12,015.5 Hz.
6. **Verification.** `tools/audio/channel_check.py` decodes each mixer
   channel's bytes, from start to cursor, starting at (predictor 0, step
   `0x80`), and compares the result with the record.
7. **Export.** `tools/audio/cmnse_bank.py` (now `tools/audio/sound_bank.py`,
   `EXP-0056`) writes one WAV per clip.

## Actual Result

- **Channel check over all 44 `end024v` states:** 38 states have a mixer
  record table.
  - **Active channels: 24 of 24 match exactly.**
  - All records: 502 of 575 match. Every mismatch is an inactive (stale)
    record.
  - At `f00009368`, 13 of 16 records match, and the one active channel
    (channel 0, data in WRAM-L `0x002F9D20`, 1,820 bytes decoded) is among
    them.
- **Export:** 88 clips, 59.6 s in total, each 0.17-1.59 s long.
  - Peaks are about 2,000 (raw) in every clip except the four quieter ones,
    `0x094`, `0x096`, `0x099` and `0x09C` (659-916).
  - Mean drift is 0.012 (maximum 0.097), against 0.27-0.41 for the standard
    decoders. Clips end near 0.
- **Ring-buffer matching** (abandoned): correlating the win-screen mix
  buffers with decoded clips (numpy FFT cross-correlation) favoured
  high-nibble-first decoding at half rate (0.65 against 0.45 for low-first).
  It could not single out clips: up to 16 channels from several banks are
  mixed together.

## Conclusion

- **CONFIRMED:**
  - the `CMNSE.PAC` layout (count, tag/length table, concatenated data);
  - the decoder transcribed from `0x0600D420`, at 12,015.5 Hz. It reproduces
    the game's own decoder state on every active channel tested.
- **Not determined:** which clips say "Vega" or "Gouki". That needs listening
  (the user), or a log of which clip IDs the game requests at the announcement.
- **DISPROVEN:** IMA, OKI and Yamaha ADPCM, and low-nibble-first order.

## Uncertainty and Alternatives

- The flag field (`tag >> 10`: 0, 2, 6, 9, 11, 13, 17, 19, 24, 25, 26) and the
  u32 at `0x04` (`0x00057701`) are not interpreted.
- Inactive-record mismatches are probably source data that was overwritten
  after the channel stopped. This is not tested.
- The character-select "Vega" may be in a different bank (`SEL*.PAC` or
  `PLxx.PAC`), not `CMNSE.PAC`. The 88 clips have not been heard.
- Sound-RAM extraction is not validated against a debugger dump. The exact
  channel matches make a byte-order error very unlikely for the spans used.

## Reproduction

Commands:

```bash
./invenv.sh python -m tools.audio.sound_bank
./invenv.sh python -m tools.audio.channel_check local/end024v/rec/states/f00009368.mcs
./invenv.sh python tools/sh2/disasm.py --base 0x06000000 --start 0x0600D300 --end 0x0600D480 local/loc002/wram/wram_h.bin
```

- The tool was first written as `cmnse_bank` and renamed to `sound_bank`
  in `EXP-0056`. That run wrote `local/audio/cmnse/cmnse_NN_idXXX.wav` plus
  `index.json` (SHA-256 `3cd5cc55…f52d`), with `--peak 0.9` normalisation;
  `--peak 0` keeps raw levels. `sound_bank` now writes the same clips to
  `local/audio/cmnse_0/`.
- `local/loc002/wram/wram_h.bin` is WRAM-H from `local/loc002/f9368_bison.mcs`
  (state SHA-256 `649070d9…e576`; WRAM-H `fe3c3f09…8078`), extracted with
  `mcs_extract --region wram_h`. That state is a copy of `f00009368` with a
  font transplanted into cart RAM; its WRAM-H is byte-identical to the
  original state's.
- Listening aids (local only): `catalog.wav` (all clips with 0.5 s gaps;
  start times in `catalog.tsv`).
- **User result (2026-10-25):** none of the 88 clips announces a name. The
  closest is "Ken", the second half of "Hadou-ken", stored as its own clip.
  The name search continues in `EXP-0056`.
