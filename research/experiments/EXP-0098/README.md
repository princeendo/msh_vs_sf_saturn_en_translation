# EXP-0098: Bison and Akuma live, in the arcade font; four more quote slots

Tasks: RE-050 (live spot checks), RE-049 (quote slot), REF-012 (arcade font
in play)
Status: DONE (this experiment); RE-050 and RE-049 stay open
Confidence: CONFIRMED (Bison and Akuma: all 16 records on the Saturn; the
`RE-049` slot rule holds for four more quotes); HYPOTHESIS (the winning
character decides the slot)

## Observation

- `RE-050`: 13 of 17 characters were checked offline only (`EXP-0036`).
- `RE-049`: the quote uses slot `9E16` when a type-`0x00FF` task holds `9ED6`,
  and `9ED6` otherwise (`EXP-0094`, six quotes). What keeps that task alive
  is not known.
- `EXP-0096` switched the pair glyphs to the arcade's narrow glyphs.

## Hypothesis

1. Each character's 16 records show their built text on the Saturn.
2. The slot rule holds for new quotes.

## Inputs and Provenance

- **Image:** `build/ref012_m8_roster_gold_us` (`EXP-0096`, American names,
  arcade glyphs), track 01 `b9372a58…`.
- **Session (2026-10-28):** the user on 1P, Arcade, Bison and Akuma.
  - Three user wins, then a loss.
  - Recorder `local/re050/play/rec`: 156 states.
  - `bp_log --kind pc --range 060AF724-060AF725`.

## Procedure

1. Read the four `060AF724` hits from the agent's `events.log`, and read
   the slot table (+`0x0C`, +`0x34`, +`0x54`) from the first recorder state
   after each quote.
2. `forced.sh`, from a recorder state before each user KO (Bison `f9560`,
   r12 `0x060F9ED6`; Akuma `f13840`, r12 `0x060F9E16`):
   - `ko_capture.py --force-index i --setter-pcs 060AF282` for i = 0-15;
   - then `verify_records.py --compile-dir build/ref012_m8_roster_gold_us`.
3. `sheet.py` crops each `quote.png` to the text box and stacks them. Every
   box was read.

## Actual Result

### 1. The session

| Frame | r12 | Winner | Quote (shot) |
| --- | --- | --- | --- |
| 9,994 | `9ED6` | the user (Bison) | "You were not even / worth the effort..." (`f10250`, `f3ba7c51…`) |
| 14,208 | `9E16` | the user (Akuma) | "There is no good or evil, / only Akuma!" (`f14460`, `03c73bbb…`) |
| 19,952 | `9ED6` | the user (Bison) | "I am the only one worthy / of this worlds riches..." (`f20188`, `6b4ebc39…`) |
| 26,599 | `9ED6` | the CPU | not captured (the user quit) |

All three quotes are drawn in the arcade glyphs. The US names show in the
text ("only Akuma!").

### 2. The slot table just after each quote

| Quote | `9ED6` +`0x0C` | +`0x54` |
| --- | --- | --- |
| f9994 (Bison) | `0068` (the quote) | 0 |
| f14208 (Akuma) | `00FF` | `0x060F4000` (a character object) |
| f19952 (Bison) | `0068` (the quote) | 0 |
| f26599 (CPU) | `0068` (the quote) | 0 |

The rule holds for all four, so ten of ten quotes so far.

### 3. Forced records

- **Automated checks:** all 32 runs pass the pointer, cart-font, WRAM-L
  table and display-buffer checks.
- **`screen_ok` fails for 28 runs:**
  - The check (`quote_render.screen_body`) counts pixels whose channels are
    all at least 200, which is the white caption colour.
  - The gold palette has no blue, so it finds no text (IoU 0 on every run).
    It passes records 0 and 8 only because their expected index is 0.
  - This is a limit of the tool, not of the image.
- **Read instead** (sheets `bison.png` `524bea4b…`, `akuma.png`
  `6b7d3f99…`): every record shows its own built quote, records 8-15
  repeating 0-7 as the tables do.
- **Tool fix:** `verify_records.py` now skips raw-format tables. Ending
  pages and `MM.BIN` records are not win quotes and are not PAC-compressed.

## Conclusion

- **CONFIRMED:**
  - Bison and Akuma pass all 16 records live in the arcade-glyph image
    (`RE-050`: six characters live now);
  - the `RE-049` slot rule holds for ten of ten quotes.
- **HYPOTHESIS:** the winning character decides the slot. Ryu, Akuma and
  Cyclops wins had the `0x00FF` task (`9E16`). Bison, Zangief, Captain
  America, Dhalsim and every CPU win did not (`9ED6`). This is not tested by
  a controlled change.

## Uncertainty and Alternatives

- **`screen_ok` is blind to the gold palette.** For gold builds the boxes
  must be read until the check learns the palette.
- **Alternative explanations for the slot:** the character-based pattern
  may instead come from move types (a fireball still alive, for example).
  Same-character wins with different finishing moves would tell them apart.

## Reproduction

```bash
# Play: Mednafen (agent build) on build/ref012_m8_roster_gold_us, recorder and bp_log as EXP-0094.
bash research/experiments/EXP-0098/forced.sh   # Mednafen (agent build) running
./invenv.sh python research/experiments/EXP-0098/sheet.py local/re050/sheet/bison.png \
  local/mednafen/agent/runs/re050-bison-r??
```
