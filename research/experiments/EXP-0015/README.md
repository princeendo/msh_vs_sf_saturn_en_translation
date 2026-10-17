# EXP-0015: Live Mutation of the Ryu Quote Table

Task: `RE-012`
Date: 2026-10-17
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0013` found that each displayed Ryu quote matches exactly one 38-cell record of
16-bit codes in a WRAM-L table. The table is 15 records of 76 bytes at
`0x002091F8-0x0020966B`, identical in every state including pre-KO state A.

Kana codes follow `0x0800 + (Shift-JIS second byte − 0x9F)`. All 11 observed quotes
(Q1-Q11) map to records in this table. Quote selection after a checkpoint varies
(`EXP-0009`).

## Hypothesis

The quote screen builds its text from this WRAM-L table. Changing a record's codes
before the quote screen changes the displayed glyphs to the glyphs for the new
codes.

## Controlled Change

There is exactly one variable: in state A (slot 5), line-1 cells 0-2 of all 15
records are set to `0801 0803 0805`. This is 45 two-byte writes, made by loading
`re012-aiu-patched.bin` into workraml `000091F8-0000966B` while frozen. Every other
byte of the range is unchanged. Changing every record makes the prediction
independent of which quote is selected.

The control is the same procedure, loading `re012-aiu-original.bin` (no byte
changes).

## Prediction

- **Patched runs.** The top-left three cells of line 1 show `あ い う`, whichever
  quote appears. The rest of the quote is unchanged. Most records have blank cells
  there. Records 0 and 4 lose three characters, records 8 and 10 lose two, and
  record 1 loses one.
- **Control runs.** The quote is shown normally.
- **If the cells change to glyphs other than あいう:** the table drives the display,
  but the kana formula is wrong for あ/う.
- **If nothing changes:** this table is not the display source, for example because
  it is reloaded or a different copy is used. The hypothesis is then `DISPROVEN`.

Run both the patched and control procedures at least twice, from a clean reload of
state A each time.

## Original and Modified Bytes

All 45 writes are listed in ignored `local/mednafen/dumps/re012-aiu-manifest.json`
(SHA-256 `2df36119…d125`). For record `r` (0-14), with base
`0x002091F8 + 76·r`:

- offsets `+0`, `+2`, `+4` change from their original codes to `0801`, `0803`, and
  `0805` respectively;
- records 2, 3, 5, 6, 7, 9, 11, 12, 13, and 14 have `0020` (blank) in all three
  cells;
- record 1 has `0020` in cells 0-1;
- records 8 and 10 have `0020` in cell 0 only;
- records 0 and 4 have text in all three cells.

Purpose: a visible, quote-independent marker.

## Procedure (after `EMU-011` is `DONE`)

1. Launch from the repository root. Press `5`, then `F7`, then `Option+A`.
2. Press `Option+D`, then `Option+3`. Select Low Work RAM, press `L`, and enter
   `000091F8 0000966B local/mednafen/dumps/re012-aiu-patched.bin`. Press `D` and
   dump the same range to `re012-run1-loaded.bin` to verify.
3. Press `Option+D` to close the debugger, then `Option+R`. KO Vega with Ryu and
   wait for the full quote.
4. Press `Option+A`, then select slot 9 and `F5` to save the visible result, then
   `F9`. Press `Option+R`.
5. Repeat steps 1-4 once more (run 2, slot 9 again after recording it).
6. Run the control twice with `re012-aiu-original.bin`.

## Procedure Revision (before the run)

- **Slots.** One slot per run, so no run's evidence is overwritten: patched run 1 to
  slot 9, patched run 2 to slot 1, control run 1 to slot 2, control run 2 to
  slot 3. Slots 1-3 previously held `EXP-0006`/`EXP-0007`/`EXP-0009` states, which
  were archived with verified hashes in `research/savestates/archive-2026-10-15/`.
- **Files.** Short, byte-identical file names are used: `p.bin` (patched) and
  `o.bin` (original).
- **Verification dumps.** `r1.bin`, `r2.bin`, `c1.bin`, and `c2.bin`.

## Actual Result (runs 1-4, 2026-10-17)

The first attempt at patched run 1 produced Mednafen's warning "unexpected EOF, short
by 00000050". The end address was most likely mistyped as 80 bytes too large. The
run was restarted from a reload of state A.

| Run | Loaded | Verification dump (SHA-256) | Saved slot / state SHA-256 | Screenshot | Quote shown |
| --- | --- | --- | --- | --- | --- |
| Patched 1 | `p.bin` | `r1.bin` `08a1a3aa…` (= patched) | 9 / `877bcd9125f10d9f17dec9dfc744510926d36224fc9f9e2c628cdaa2b0421ba5` | `-0039.png` `d2509220…fee6f` | **`あいう` + Q8** (record at `0x00209290`) |
| Patched 2 | `p.bin` | `r2.bin` `08a1a3aa…` (= patched) | 1 / `69b18b482f20fa9be15ec6ee2f94b6c6a24f90ffbffa3d2b8191e43c6cddf1ce` | `-0040.png` `8bb73855…f96f4` | Ken-addressed quote (`教えてくれ、ケン`), no `あいう` |
| Control 1 | `o.bin` | `c1.bin` `78fd5a38…` (= original) | 2 / `dd39fafc26afa57452984077bc2f0fc67d958dcabd7e90a5c3b9cf84862f2263` | `-0041.png` `7ff2b82e…8ed` | Same Ken-addressed quote, normal |
| Control 2 | `o.bin` | `c2.bin` `78fd5a38…` (= original) | 3 / `9ed8b4cb8337fa96044aff93c4c08cabac80ab90e8ae22cfd908905ac51f401b` | `-0042.png` `0069c182…e5e70` | Q5, normal |

Extracted WRAM-L from each saved state shows the table range equal to `p.bin` in
patched runs 1 and 2, and equal to `o.bin` in both controls. All four states are
archived with verified hashes in ignored `research/savestates/archive-2026-10-17/`.

Patched run 1 matches the prediction exactly. The first three cells of line 1 show
`あ い う`, and the rest of Q8 is unchanged (those cells are normally blank). This
also confirms the displayed glyphs for codes `0801`/`0803`/`0805`, which were never
observed before.

Patched run 2 showed a quote that is not in the patched range:

- **WRAM-H buffer.** The `0x060ED80A` buffer holds line 1 as `09CD 0807 0825 080E
  084B 08A9 0863 08A5` (`教えてくれ、ケン`).
- **Template record.** Its line 2 matches WRAM-L at `0x002091D4`, inside a record at
  **`0x002091AC`**, one record (76 bytes) before the patched range. That record's
  line 1 is `0020 0020 09CD 0807 0825 080E 084B 08A9 0000 0020…`.
- **Name placeholder.** The buffer has ケン (`0863 08A5`, two cells) where the record
  has `0000`. That is consistent with `0000` being a partner-name placeholder
  (`HYPOTHESIS`).
- **Table bounds.** The bytes before `0x002091AC` are not text. The table is
  therefore 16 records, `0x002091AC-0x0020966B`. `EXP-0013`'s walk stopped at the
  `0000`.

Patched run 2 does not contradict the hypothesis: its record was not modified.
Reproduction from a clean checkpoint still needs another patched run that selects
a patched record.

### Runs 5-6 (additional patched runs, same procedure)

| Run | Verification dump | Saved slot / state SHA-256 | Screenshot | Quote shown |
| --- | --- | --- | --- | --- |
| Patched 3 | `r3.bin` `08a1a3aa…` (= patched) | 4 / `0a02f37d357a1729a750b2974691b4902798734768dbcdbfd60300550e8cbd0e` | `-0043.png` `acbd1687c5ebb3e0bbd240ba2500a9be3afef7f0b454ff95f243ec2d1212f6ce` | **`あいう` + Q8** (record `0x00209290`) |
| Patched 4 | `r4.bin` `08a1a3aa…` (= patched) | 1 / `70bd6d1d8a067b8fbdfed8f383bba60b4ca704c5780f301f35c954518a38af3c` | `-0044.png` `d3c89f1f98e2f4c3ccb09cd062ddce66fd18d21a1844d764fe47d8212bee8865` | **`あいうと闘え！…`** (Q5, record `0x002094F0`) |

Both saved states contain the patched table, checked by extraction against `p.bin`.
They are archived as `slot4-run3.mc4` and `slot1-run4.mc1` in
`research/savestates/archive-2026-10-17/`.

### Before/after evidence

| Record | Before | After (patched) | Observed change |
| --- | --- | --- | --- |
| Q8 `0x00209290` (cells 0-2 were `0020 0020 0020`) | `EXP-0010` C2 thumbnail `06f0b279…`; `EXP-0009` `-0028.png` | `-0039.png`, `-0043.png` | Three blank cells now show `あ い う`; the rest is unchanged |
| Q5 `0x002094F0` (cells 0-2 were `0020 0841 0822`) | Control 2 `-0042.png` (`もっと闘え！…`) | `-0044.png` | `もっ` replaced, giving `あいうと闘え！…`; the rest is unchanged |

The portrait, box, logos, and other text were unchanged in every patched
screenshot.

## Conclusion

`CONFIRMED`. Writing 16-bit codes into the WRAM-L quote table records before the
quote screen changes the displayed glyphs in the corresponding cells. The
prediction (`あいう` in line-1 cells 0-2, the rest unchanged) held in **three of
three** patched runs that selected a patched record, covering two different
records. Both controls showed unmodified quotes.

The one other patched run selected the unpatched record at `0x002091AC`, which is
outside the written range. That is consistent with the hypothesis, not a
counterexample.

This also confirms that codes `0801`, `0803`, and `0805` display `あ`, `い`, and
`う`.

## Uncertainty and Alternatives

- **Table bounds.** The table is 16 records (`0x002091AC-0x0020966B`), not 15. The
  record at `0x002091AC` contains `0000` where the partner name appears on screen.
  That `0000` is a name placeholder is a `HYPOTHESIS` (one observation, Ken as
  partner).
- **Other contexts.** Whether this table holds Ryu's quotes for other partners,
  opponents, or modes, and where it is loaded from on disc, is untested.
- **Scope.** The confirmation covers line-1 cells 0-2 of two records. It does not
  establish the meaning of every code. Kanji codes and other cells are covered only
  by `EXP-0013`'s `SUPPORTED` mapping.
- **Session.** All runs used one Mednafen process. The source identity was
  re-verified at closeout.
