# EXP-0056: Find the sound banks that hold the name calls

Task: LOC-005 (first blocker: identify the "Vega" and "Gouki" clips)
Status: DONE
Confidence: CONFIRMED (the container and bank layout, which clips the mixer
played, and, by the user's listening, the two name-call clips); DISPROVEN
(Vega-bank #18 as the name call)

## Observation

- The user listened to all 88 `CMNSE.PAC` clips (`EXP-0055`). None announces
  a name. The closest is "Ken", the second half of "Hadou-ken", stored as its
  own clip.
- The user hears "Vega" at character select and in the win announcement.

## Hypothesis

The name calls are in another bank that the same mixer plays. Mapping each
mixer channel's data back to a disc file finds that bank.

## Controlled Change

None to the game. Analysis of recorded states and disc files only.

## Prediction

Some mixer channels in the `END-024` Vega recording play data found in files
other than `CMNSE.PAC`, and those files contain banks in the same layout.

## Inputs and Provenance

- Source track 01 (hash in `references/mshvsf/saturn_jp/README.md`).
- `local/end024v/rec/states/*.mcs`: 44 states from the `END-024` recording
  (Vega, through the final fight, the win and the ending).

## Tools and Environment

- `tools/memory/mcs_extract.py` (Mednafen 1.32.1 states). Python 3.12.13
  (`./invenv.sh`).
- `tools/audio/sound_bank.py`: `cmnse_bank.py` from `EXP-0055`, renamed and
  extended to read the PAC container and export every bank.

## Procedure

1. For every state with the mixer loaded, read each channel record (layout in
   `EXP-0055`). Take the first 64 bytes of the channel's data and search every
   disc file for them (a scratch script).
2. Inspect the headers of the files found. Each is a container of (u32 flag,
   u32 size) pairs, ended by (0, 0), followed by the payloads.
3. Test every payload of every PAC file as a bank. The test passes only if
   the count, the table and the clip lengths add up to the payload's exact
   size.
4. For each fighter bank, find the clips whose bytes equal a clip in the
   select bank.
5. Map the two Vega-bank channels seen at the win screen to clip indexes.

## Actual Result

- **Channel sources:** besides `CMNSE.PAC`, the mixer plays data from:
  - `MEMFIX.PAC`;
  - `PL0E.PAC` (Vega; character 14 in the project's numbering);
  - `PL0F.PAC` (Gouki);
  - `PL05`, `PL09` and `PL13`;
  - movie files.

  Several `PL` clips also occur in `SEL.PAC` and `SEL2.PAC`.
- **Banks:** 28 banks with exact fits, 725 clips in total:

  | Bank | Clips |
  | --- | ---: |
  | `CMNSE.PAC` payload 0 | 88 |
  | `MEMFIX.PAC` payload 8 | 19 |
  | `MEMFIX.PAC` payload 9 | 27 |
  | `SEL.PAC` payload 1, also `SEL2.PAC` payload 0 | 66 |
  | `PLxx.PAC` payload 1 or 2 (one per fighter file; `PL07` and `PL10` have two) | 7-38 each |

  The PAC files whose header is not this container (the LZSS ones) were
  skipped.
- **Shared with the select bank:**
  - Vega (`PL0E` bank): #1 (ID `0x04F`), #5 (`0x133`), #7 (`0x1A5`) and #18
    (`0x286`).
  - Gouki (`PL0F` bank): #1 (`0x048`), #11 (`0x1D1`), #13 (`0x25A`) and #23
    (`0x338`).
  - `PL13` reuses Gouki's `0x1D1` and `0x25A`, so it is probably Mech-Gouki.
    This is not checked.
  - Twelve select-bank clips are in no fighter bank: #0, #14, #16, #19, #27,
    #28, #41, #46, #49, #54, #56 and #63.
- **Win screen:**
  - At `f00008316` (win banner), channel 9 has just played Vega-bank #3
    (`0x07E`).
  - By `f00008668`, channel 10 has played Vega-bank #18 (`0x286`). That is
    the same data as select-bank #48.
  - Earlier, at `f00003038`, Vega-bank #5 (`0x133` = select #17) was played.

## Conclusion

- **CONFIRMED:** the PAC container and bank layout, and the 28 banks.
- **CONFIRMED (user listening, 2026-10-25):** the name calls are clip #1 of
  each fighter bank:

  | Clip | ID | Says | Same data in the select bank |
  | --- | --- | --- | --- |
  | `PL0E.PAC` bank #1 | `0x04F` | "Bison" | `SEL.PAC` payload 1 #4 |
  | `PL0F.PAC` bank #1 | `0x048` | "Gouki" | `SEL.PAC` payload 1 #3 |

  In both, the name starts about 1 s into the clip, after another sound.
  Because the same clip is in the select bank, one recording can serve both
  character select and the win screen.
- **DISPROVEN:**
  - Vega-bank #18 (`0x286`) as the name call. It was only the last clip seen
    in a channel record after the win banner. Clip #1 was never caught in a
    record (see Uncertainty);
  - `CMNSE.PAC` as the source of the name calls (user listening).
- **Open: the voice says "Bison", the text says "Vega".** The text and art
  for this character use "Vega" (`NAME_OVERRIDES`; life bar `0x760`). The
  name call in his bank says "Bison", the US name, yet the user first
  described the in-game line as "Vega". Two questions are not yet answered:
  - whether the in-game select and win lines are this clip;
  - whether other select-bank clips are name calls for the other fighters.

  Seeing the mixer start clip `0x04F`, or the user listening in game, would
  settle the first.

## Uncertainty and Alternatives

- The record shows only which clip a channel last played, at 352-frame
  intervals. A clip that started and ended between two states is not seen.
- The fighters' numbering (`PL0E` = Vega, `PL0F` = Gouki) follows the
  project's character indexes (`NAME_OVERRIDES` 14 and 15). The bank contents
  agree: these banks were played in the Vega run.
- Whether the name call is the announcer or the character speaking is for the
  user to judge.

## Reproduction

```bash
./invenv.sh python -m tools.audio.sound_bank --file '*'
./invenv.sh python -m tools.audio.channel_check local/end024v/rec/states/f00008668.mcs
```

- The first command writes `local/audio/<file>_<payload>/` for each bank: a WAV
  per clip, `index.json`, `catalog.wav` and `catalog.tsv`.
- Listening aid (local only): `local/audio/shortlist.wav` and `shortlist.tsv`.
  These hold the 4 Vega-shared, 4 Gouki-shared and 12 select-only clips, with
  1 s gaps. Vega-bank #1 starts at 0.00 s and Gouki-bank #1 at 7.24 s.
- The full-bank catalogs are `local/audio/pl0e_1/catalog.wav` ("Bison" in
  clip #1 at 1.72 s) and `local/audio/pl0f_1/catalog.wav` ("Gouki" in clip
  #1 at 0.92 s).
