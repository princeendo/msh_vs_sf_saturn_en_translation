# Translation Data

This directory is for structured, evidence-backed text correspondences after review.
It is not a scratchpad for guesses or bulk extracted copyrighted scripts.

Each record should identify:

- target game, platform, region, and source-image hash;
- character and context;
- source and reference release identifiers;
- concise source and proposed English text only when legally appropriate;
- provenance or observation method;
- experiment or review record;
- confidence and unresolved ambiguity;
- technical constraints only when measured.

## Win-Quote Policy (user decision, 2026-10-24)

- Each Saturn win-quote record `k` uses the official arcade English entry `k & 7`
  for that character: the line the arcade displays in the same selection state
  (`EXP-0031`).
- Two Saturn records share each English line, by design. Meaning-based
  retranslation is not used where an official paired line exists.
- Apply this to a character only after its Saturn table and arcade remap are
  verified (`tools/reference/quote_pairing.py`).
- `GATE-TRANSLATION` passed on 2026-10-24 (user GO). For Ryu, `preferred_english` is
  the paired `arcade_us_text`.
- Ken's pairing is verified (table identity with arcade Japanese slot 10, in
  `data/text/ken_arcade_pairing.json`), so the policy may now apply to Ken.
  Other characters wait for their own verification.

Do not assume line ordering or correspondence across releases. Keep hypotheses in
`research_log.md` until supported, and do not represent a translation as final without
review. Store bulk source material locally under ignored paths; track only permitted
metadata and the minimal text needed for the project record.
