# Text Data

Store derived, non-copyrightable text-system metadata and schemas here after an
experiment establishes them. Do not store extracted game text dumps.

## Files

- `font_candidates.json`: the 1,922 quote-font codes that no record-shaped
  table uses (`EXP-0023`, `unseen_codes.json`, SHA-256 `32e513ae…`). Only code
  numbers. `caption_compiler.py` empties unused kanji from this list to make
  room for pair glyphs. It was copied here from the ignored
  `research/memory_dumps/exp0023/` so that a fresh clone can rebuild
  (`REL-001`).
  - "Unseen" does not mean unused. 120 of the 128 credits-font codes
    `0x1E0`-`0x25F` are on this list (`EXP-0051`). Reclaim only kanji
    (`0x926`-`0xC5F`), as the compiler does.
