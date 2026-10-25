# EXP-0052: Caption Pair Glyphs from the Staff-Credits Font (Silver), and the Caption Palettes

Task: FONT-011
Status: IN_PROGRESS
- **Silver:** built and verified live (2026-10-25).
- **Gold:** under investigation.

Confidence:
- **CONFIRMED:** the silver build (live), the caption palette banks, and the
  capacity limits.
- **HYPOTHESIS:** where the caption palette is generated.

## Observation

- `EXP-0051`: the staff-credits font is quote-font codes `0x1E0`-`0x25F`, and
  squeezed pairs fit the caption grid.
- The user chose the credits font, squeezed two per cell, in gold, with the
  thin glyphs tuned and the palette worked out. When gold proved blocked
  (below), the user chose: "Both: build silver, then dig".

## Hypotheses

1. A credits-style pair glyph can replace the quote-style one for every
   roster win quote and ending, within the font's capacity.
2. Captions can be shown in the credits' gold.

## Palette Findings

No gameplay. States from the `END-024`/`END-026` recordings were replayed on
the `m8_roster` image, with one-off agent scripts.

- **The CRAM copy.** The game keeps two 4 KB copies of colour RAM in WRAM-H
  (`0x060C7C24` and `0x060C8C24`). SCU DMA copies one to CRAM every frame
  (`0x0601BABC`, R9 = source). A sprite's colour bank `colr & 0x7FF` is its
  CRAM index: credits bank `0x0F0` is the gold gradient.
- **Caption banks** (sprite colour words read from the VDP1 table, colours
  from the CRAM copy):

  | Screen | Caption `colr` | Bank | Values 1-9 | `B` | `F` |
  | --- | --- | --- | --- | --- | --- |
  | Win quote | `0x61E0` | `0x1E0` | (240,240,240) down to (112,112,112) in steps of 16 | (16,16,0) | black |
  | Post-boss dialogue | `0x6030` | `0x030` | the same | the same | the same |
  | Ending page | `0x61F0` | `0x1F0` | the same | the same | the same |
  | Staff credits | `0x70F0`-`0x7170` | `0x0F0`… | yellow (240,240,0) to orange (240,112,0) | (32,0,96) | black |

  The caption banks hold the credits layout in grey, so credits glyphs drawn
  with them come out silver.
- **Gold is always loaded.** CRAM bank `0x010` equals the credits gold bank,
  word for word, on the win-quote, dialogue, page, and credits screens.
- **The colour word.** It comes from a sprite's request-list attribute: the
  writer at `0x0601CB72` computes
  `colr = (attr & 0x7000) | ((attr & 0x1F) << 4)`. The request list is at
  `0x060EDA20` (8-byte entries; the attribute is the low word of the second
  long). The caption entries carry palette numbers `0x1E` (win quote), `0x03`
  (dialogue), `0x1F` (pages), and `0x0F` (credits).
- **Where the palette number comes from:**
  - The entries are written by an object emitter (`0x06073410`) from
    per-object fields copied into a GBR work area. A register-file save and
    restore (`0x06019B5C`) suggests a script interpreter runs the objects.
  - The win-screen code's palette byte (object +39, from a byte table at
    `0x060C0E00`) gives values 0-3: fighter palettes, not the caption.
- **The grey banks are generated at run time:**
  - The bank first appears between 60 and 120 frames after state
    `end024v f00008668`.
  - Write breakpoints over the whole bank (`0x06`… and `0x26`… aliases)
    logged nothing, and no SCU or SH-2 DMAC set-up targets it.
  - The palette is in no WRAM-L, WRAM-H, or extracted cart RAM dump before
    the copy, and in no disc file (raw or LZSS).
  - Its entries step by `0x0842` (all channels −2) from `0x7BDE`.
  - HYPOTHESIS: the slave SH-2, which the agent's breakpoints may not cover,
    computes it.
- **What rules out a simple remap:** pointing the shared sprite writer at bank
  `0x010` would also recolour fighters. Palettes 0-3 are character palettes,
  and the dialogue caption uses palette 3.

## Glyph Design and Capacity

- **Squeeze.** For each letter, every column pair's fill is merged (keeping
  the lowest value), and a one-pixel outline is redrawn around the pair
  (`tools/text/credits_font.py`). Resampling to six columns (`fit_fill`)
  lost dots and shapes and was not used.
- **Hand-drawn letters** (`OVERRIDES`): `I`, `M`, `W`, `m`, `w`, `!`, `'`, and
  `‼`, with the gradient taken from the source glyph's rows.
- **Capacity** (roster spec, 453 distinct pairs; reclaimable kanji: 30,235
  bytes; the font has no slack):

  | Shading | Outline | Pair bytes |
  | --- | --- | ---: |
  | full gradient | 8-connected | 40,852 (does not fit) |
  | levels 1, 5, 9 | 8-connected | 34,646 (does not fit) |
  | 2 bands (rows 0-7 at 5, then 1) | 8-connected | 30,902 (does not fit) |
  | **2 bands** | **4-connected** | **29,284 (used)** |
  | flat | 8-connected | 28,455 (fallback) |

  The font compresses runs down columns, so per-row gradients cost bytes.
- **Integration.** A top-level spec field `glyph_style` (`quote` or
  `credits`) is threaded through `pair_font.pair_glyph`, the compiler's
  capacity, build, and verification, and `official_endings --glyph-style`.
  The default is unchanged: the six existing references still pass.

## Build

```bash
./invenv.sh python -m tools.text.official_endings --driver local/mame_src/cps2.cpp \
  --archive local/arcade_roms/mshvsf/mshvsfu.zip --roster data/text/m5_roster.json \
  --with-win-quotes --glyph-style credits --out local/font011/spec/roster_credits.json
./invenv.sh python -m tools.text.caption_compiler local/font011/spec/roster_credits.json \
  --out-dir build/font011
```

- **Result:** spec `173d485c…`; track 01 `9246148f…`; `MEMFIX.PAC`
  `df78fce8…`.
  - Every check is true, and the two builds are identical.
  - 500 pair glyphs; 205 kanji codes reused; 25 bytes of zero fill.
- **Regression:** new reference `m8_roster_credits`; all seven references
  pass.

## Live Result (Silver)

One cold boot of `build/font011/image_a`, with the recorder
(`local/font011/rec`):
- **Win quote:** the user won stage 1 with Ryu + Ken. "I had better
  challenges / back in the day..." showed in the credits-style letters,
  silver with a dark outline, and readable (`f00006454`, `a24e5ebb…`).
- **Driver mistake:** the driver was armed after stage 2 had loaded. Its
  "boss started" test (the stage word is 8 and the opponent's vitality is
  144) matched the stage-2 fight, so it zeroed the boss-only words there. The
  user then lost stage 2. The driver must be armed before the next stage
  loads: at character select, or on a win screen.
- **Ending** (second credit, driver armed at the title): "RYU, / you're not
  bad." and "We shall meet again / KEN.", then Ryu's three pages, all in the
  new font.

  | Frame | Box | SHA-256 |
  | --- | --- | --- |
  | `f00020058` | dialogue block 1 | `6e7694ff…` |
  | `f00020542` | dialogue block 2 | `0c7d7e5e…` |
  | `f00021080`, `f00021575`, `f00022114` | pages 1-3 | `0d5e1f72…`, `f0837a62…`, `9eeeb5fe…` |

  Composite: `local/font011/live_sheet.png` (`929e58ae…`).
- **Weak letter:** capital `W` reads a little like "Ue" in "We". It needs
  another design pass.
- **Side observation:** the player-2 prompt alternates "PRESS START" with
  "対戦者求む!" (`UI-001`), seen in this recording. The user also reports
  Japanese alternating with "EASY" at mode select (`UI-002`).

## Conclusion So Far

1. **CONFIRMED (silver):** credits-style pairs replace the quote-style ones
   for every roster caption, within capacity, and display live in the
   captions' own palette.
2. **Gold:** blocked. The caption palettes are generated by code not yet
   found. Next experiments, smallest first:
   - see whether the agent can break on the slave SH-2, or log its accesses;
   - find the caption objects' palette-number source by tracing the request
     list back to the object data at creation (win quote `0x1E`);
   - as a fallback, overwrite the generated bank after it is written. That
     needs a code hook, so it is a last resort.

## Uncertainty

- The full gradient does not fit, so even gold would use two bands unless more
  space is found.
- Only one win quote, one dialogue pair, and Ryu's pages were seen live. The
  other renders were checked offline.
