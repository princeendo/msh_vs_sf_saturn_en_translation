# EXP-0095: What a run-time name switch would have to swap (LOC-006 groundwork)

Task: LOC-006 (feasibility, first part)
Status: DONE (this census); LOC-006 stays `BACKLOG`
Confidence: CONFIRMED (file differences); HYPOTHESIS (free cart RAM:
cart-RAM extraction is not validated against a debugger dump, `DBG-012`)

## Observation

LOC-006 asks whether an Options entry could switch the Saturn and American
names at run time. The two release images differ only in data, so their
difference is what a switch would have to swap.

## Procedure and Actual Result

### 1. File differences between the two release images

Images: `build/regression/m8_roster_gold` (track 01 `0d55127a…`) and `_us`
(`0c3f72bb…`). Each file was read from track 01; PAC files were decoded.

| File | Bytes differing | Runs | What |
| --- | --- | --- | --- |
| `MEMFIX.PAC` entry 4 | 58,369 of 206,656 | many | the quote font: the name text changes which letter pairs are packed |
| `MEMFIX.PAC` entry 7 | 10 | 1 | the name-call table (`EXP-0058`) |
| `MM.BIN` | 221 | 55 | text records, sound-test titles, banner and VS pointers |
| `ME.PAC` | 139 | 34 | ending speaker labels and text |
| `MC00.PAC` (decoded) | 88 | 31 | pre-fight exchanges |
| `MC14.PAC` (decoded) | 22 | 18 | Metal Zangief's text |
| `MC0F.PAC` (decoded) | 12 | 2 | Vega's table |

Everything except the font totals about 490 bytes.

### 2. Free cart RAM (`cart_free.py`)

- **Method:** intersect the 256-byte blocks of cart RAM that are zero in
  every one of 213 recorder states:
  - this session (`local/re049/play/rec`, 83 states: select, fights, quotes,
    CONTINUE?);
  - `local/sp004/play/rec` (60 states: the Mech-Gouki run, its ending and
    credits);
  - `local/special004/play3/rec` (70 states).
- **Result:** the largest block zero in all of them is `0x0259EB00`,
  0x2E700 bytes (190,208). A second font needs 206,656. Two separate states
  had shown a larger region (0x3BC00 at `0x02591600`), but part of it is used
  elsewhere.
- The font itself lives at `0x0278CF60` (`FONT-001`).

## Conclusion

- **CONFIRMED:**
  - a run-time switch would have to swap the quote font, a 206,656-byte image
    of which 58 KB differs;
  - apart from that, about 490 bytes of tables and text across five files.
- **HYPOTHESIS:**
  - both fonts do not fit side by side in the cart RAM seen free in these
    states;
  - the options to explore are re-reading the font from disc when the option
    changes, a merged font (the release font is already full, `EXP-0079`),
    or space outside cart RAM.

## Uncertainty and Alternatives

- **Cart-RAM extraction is not validated**, and 213 states don't cover every
  scene (the Options menu, Survival, the sound test).
- **The rest of LOC-006 needs the Options menu:** where options are stored,
  how the menu is drawn, and the code hooks. The agent cannot send input, so
  that needs a short session at the menu.

## Reproduction

```bash
# 1: read each file of both track 01s (tools.disc.make_ssp.entries, Track,
#    pac_lzss.decode_file) and compare byte by byte; MEMFIX split by its header.
./invenv.sh python research/experiments/EXP-0095/cart_free.py \
  local/re049/play/rec/states local/sp004/play/rec/states local/special004/play3/rec/states
```
