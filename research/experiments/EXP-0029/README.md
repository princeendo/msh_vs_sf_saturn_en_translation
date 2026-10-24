# EXP-0029: Arcade Win-Quote Text in Raw CPS-II Program ROM

Task: REF-008 follow-up (reference text; feeds REF-004 and REF-010)
Status: DONE
Confidence: CONFIRMED for the data layout. The slot-to-character mapping is
SUPPORTED. Correspondence with displayed text is HYPOTHESIS until MAME captures
exist.

## Observation

- MAME 0.289 decrypts only a separate opcode space (`decrypted_opcodes_map`); data
  reads use the raw ROM (`REF-008`). The program files are loaded with
  `ROM_LOAD16_WORD_SWAP`.
- A first probe rebuilt the US `maincpu` region in memory and unswapped each
  16-bit word. Copyright and credits text then appeared as plain ASCII, but no
  win-quote-like sentence did. Plain 8-bit ASCII was **disproven** for win quotes.

## Hypothesis

Win-quote text is stored unencrypted in the raw program data, in a 16-bit
character encoding in which letters are consecutive codes.

## Controlled Change

None to any file. The only variable is how the program bytes are interpreted.

## Prediction

A relative search for common English words (`YOUR`, `WITH`, `THAT`) will find a
single dominant constant offset in one unit size (8- or 16-bit). Decoding with that
offset will give grammatical text.

## Inputs and Provenance

- Local zips `mshvsf.zip`, `mshvsfu.zip`, and `mshvsfj.zip`; SHA-256 and the full
  MAME 0.289 audit are in `references/mshvsf/arcade/README.md`.
- Pinned driver `cps2.cpp` at commit `f34f02505e32c1993c6a782b6814232cbfc74e36`,
  SHA-256 `a8c09ef8…e861602`.
- Rebuilt 4 MiB `maincpu` images (68000 byte order), in memory only:

| Set | Program SHA-256 |
| --- | --- |
| `mshvsf` | `b21726cf2a503cdb6ecf5c1a0f61d47aca669a362e752637fc262b624bfc1b7e` |
| `mshvsfu` | `3f04821ca163556a4eb548e2f15c8cf095a23d024d8b8e07ce3636499103570a` |
| `mshvsfj` | `b2612676a352e4b2ea2f82f2310db8ca4e29564585b9432d244d27adfeafc41d` |

## Tools and Environment

- Python 3.12.13 via `./invenv.sh`. `tools/reference/cps2_text.py` and
  `tools/reference/mame_audit.py` (driver parser).
- Exploratory probes lived in the session scratchpad and were not kept; the tool
  reproduces their results.
- MAME 0.289 (Homebrew bottle `mame--0.289.arm64_tahoe`; binary SHA-256
  `6d40df87963c58cdd3857d203e186af854fea49ae03b2ab555e30ef1029636d9`) was used
  only for `-verifyroms`.

## Procedure

1. Relative search in the unswapped US program (8- and 16-bit big-endian units).
2. Byte context around the hits, to read the space and punctuation codes.
3. Decode all runs, then test the punctuation mapping by the case of the following
   word.
4. Look for longword pointers into the text region and read the tables they form.
5. Repeat on all three sets and compare digests.

## Actual Result

1. **Relative search.** In 16-bit units, `YOUR` (37 hits), `WITH` (15), and `THAT`
   (10) all share base `0x0161` for `a`. The 8-bit search found nothing comparable.
2. **Character map** (high byte `0x01`):

   | Code | Meaning | Basis |
   | --- | --- | --- |
   | `0x0020` | space | context (padding) |
   | `0x0140`-`0x0159` | `A`-`Z` (ASCII minus 1) | context, e.g. "You" |
   | `0x0161`-`0x017A` | `a`-`z` (ASCII) | relative search |
   | `0x0120` | `!` | 680 of 681 following words are capitalized |
   | `0x0185` | `,` | 216 of 277 following words are lowercase |
   | `0x0184` | `.` | context |
   | `0x0187` | `'` | context ("you're") |
   | `0x0121`, `0x012A` | `?`, `-` | context ("X-Men", questions) |
   | `0x0196`, `0x019A`, `0x01A3`, `0x01A4`, `0x01AB`, `0x01AE`, `0x01B7`, `0x01C0`, `0x01D8` | ã á é ê í ñ ó ú ç | Spanish and Portuguese context |

   The first reading swapped `!` and `,`; the case test **disproved** it. Other
   codes stay as `{xxxx}` placeholders. Codes `0x08xx` (Japanese text) are not
   decoded.
3. **Text volume.** There are 138 runs in `0x0057AC`-`0x2374B2`, totalling 59,487
   characters. The text SHA-256 is
   `5ede5615589494a5fb6d11a4b6a79c4e955ef4f96feda5f58b74204242e43732` for **all
   three sets**.
4. **Win-quote table** at program `0x20C014`:
   - 78 big-endian longword pointers: three languages × 26 slots (English 0-25,
     Spanish 26-51, Portuguese 52-77).
   - Each points to a `0x320`-byte block: 8 quotes × 2 lines × 25 codes.
   - Each English slot decodes to 8 non-empty quotes, with 11 placeholder codes in
     total.
   - 69 distinct blocks. Slots 20, 21, and 25 share the blocks of slots 13, 16, and
     7, and the same pattern repeats at +26 and +52.
   - The quote-table digest is identical in all three sets:
     `29db2b670d034a83fc44ad8db92547a0c4eae9976f123713e71770dabf15aa25`.
5. **Endings table** (seen, not fully parsed) at `0x20C1B4`: 78 pointers. In
   English, slots 0 and 1 share one block, slots 17 and 18 share one, and slots
   19-25 share one generic screen.
6. **Name list.** The run at `0x22369A` begins with 26 uppercase names. Read in
   order as slots 0-25 (`CAPTAIN AMERICA HULK` is two names with single-space
   padding):

   | Slot | Name | Slot | Name | Slot | Name |
   | ---: | --- | ---: | --- | ---: | --- |
   | 0 | APOCALYPSE | 9 | RYU | 18 | DAN |
   | 1 | CYCLOPS | 10 | KEN | 19 | CYBER-AKUMA |
   | 2 | CAPTAIN AMERICA | 11 | CHUN-LI | 20 | ZANGIEF (2nd) |
   | 3 | HULK | 12 | DHALSIM | 21 | SAKURA (2nd) |
   | 4 | WOLVERINE | 13 | ZANGIEF | 22 | SHADOW |
   | 5 | SHUMA-GORATH | 14 | BISON | 23 | U.S.AGENT |
   | 6 | OMEGA RED | 15 | AKUMA | 24 | MEPHISTO |
   | 7 | SPIDER-MAN | 16 | SAKURA | 25 | SPIDER-MAN (2nd) |
   | 8 | BLACKHEART | 17 | NORIMARO | | |

   The shared quote blocks (20→13, 21→16, 25→7) fall exactly on the repeated
   names. So does the endings sharing: Norimaro (17) with Dan (18), and slots 19-25
   on one screen. Each block's content also fits its character's theme.

## Conclusion

- **CONFIRMED** (reproducible from data, three sets):
  - English, Spanish, and Portuguese win-quote text is stored unencrypted in the
    shared program ROM `mvs.07b` (`0x200000`-`0x27FFFF`;
    text at `0x219DEE`-`0x2374B2`, tables at `0x20C014` and `0x20C1B4`).
  - It uses the 16-bit map above and the table layout above.
  - It is identical in the Europe, USA, and Japan sets. The region-specific files
    (`03`-`05`, below `0x180000`) contain no differing Latin text.
- **SUPPORTED** (consistent, not yet observed on screen):
  - The slot order matches the name list (Ryu = slot 9, block `0x21BA20`).
  - Norimaro (slot 17) has a full English quote block (agrees with RC-2).
  - Mech-Zangief, Dark Sakura, and Armored Spider-Man reuse their base
    characters' quotes in all three languages (agrees with RC-3).
  - The ending sharing agrees with RC-4.
  - U.S. Agent (23), Mephisto (24), and Shadow (22) have **their own** Latin
    blocks. That narrows RC-3: "all secret characters borrow" holds only for the
    palette-swap secrets, as far as the data shows.
- The Japanese set holds the same English text, so the ROMs do not differ in
  which Latin quotes they *contain*. What each region *displays* is decided
  elsewhere, by region code and language setting (RC-7). That is untested.

## Uncertainty and Alternatives

- Data in ROM is not proof of display. Lines could be re-wrapped, filtered by
  region, or unused. Wording becomes evidence only from a captured frame
  (`docs/references.md`).
- The 25-code width and 8-quote count are inferred from data alignment. How the
  game selects quotes (per opponent, random) is unknown.
- The Japanese win quotes (presumably the `0x08xx` codes) and their table are not
  decoded, so RC-3's Japanese-only unique quotes are not checked.
- The names list might follow another order that merely coincides. The sharing
  pattern makes that unlikely, but code tracing or capture is needed to confirm.

## Reproduction

```bash
curl -sSfLo /tmp/cps2.cpp https://raw.githubusercontent.com/mamedev/mame/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp
```

```bash
./invenv.sh python -m tools.reference.cps2_text --driver /tmp/cps2.cpp --out local/arcade_text/mshvsfu.json --quote-table 0x20c014 --quotes-out local/arcade_text/mshvsfu_win_quotes.json local/arcade_roms/mshvsf/mshvsfu.zip
```

Repeat with `mshvsf.zip` and `mshvsfj.zip`; the printed text and quote digests
must match the values above. Outputs contain game text and stay in the ignored
`local/arcade_text/`.

## Addendum (2026-10-24, RE-044): two more codes decoded

Forcing the arcade quote pointer (`0xFF249C`) to Chun-Li and Akuma entries showed
`0x0122` as a one-cell double exclamation (`‼`, for example "stuff‼") and `0x0160`
as a straight double quote. Both were added to `tools/reference/cps2_text.py`.
That changes the digests above. With the updated map, all three sets give:

- text SHA-256 `5846cf34b857987d0efc69b80fb6478cef311c1470f3fa83e660d2cec945653d`;
- quote-table SHA-256
  `6659c4d20d8495e00559f57f13d1d5c697ac1d9fb82724c00cb1fd755aa84d80`.

Program hashes and every other result are unchanged.

