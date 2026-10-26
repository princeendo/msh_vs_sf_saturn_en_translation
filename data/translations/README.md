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
- `RE-042` (2026-10-24) verified the whole 17-character M5 roster
  (`data/text/roster_pairing.json`):
  - every Saturn table is byte-identical to its arcade Japanese slot;
  - every English block is identical in the US, EU, and JP sets and present in
    the PS1 release.
  The policy applies to all 17. Partner-name placeholders are dropped (see
  `data/text/m5_roster.json`).

## Ending Policy (user decision, 2026-10-24)

The decision, in the user's words: "For END-010, use the arcade's two official
English partner lines for the post-boss dialogue, and the official English for
the three ending pages."

- **Ending pages.** The official arcade English pages for the point character:
  English page table `0x20C1B4`, by slot (`EXP-0042`). Text is read from the
  local ROM at build time, as for win quotes, and not committed.
- **Post-boss dialogue.** The arcade English replaces the Japanese multi-box
  scene with two lines: the partner's line (partner-line record = partner
  slot) and the point character's reply (record 26 + point slot), from the
  table at `0x22226C`. No meaning-based translation of the Japanese boxes is
  made.
- **Scope.** Ryu first (`END-010`). Other characters only after their records
  and pairings are verified (`END-020`).
- **Layout (user decisions, 2026-10-24).**
  - Revised at the user's request (`EXP-0045`): each English partner line is
    shown whole in both boxes of its pair, which reads as one block lasting both
    boxes' time. It was first split at its line break across the two boxes
    (`EXP-0044`), and that layout is kept as `--dialogue-layout split`.
  - Names use the arcade's English names, in the `MM.BIN` name table, with the
    name-length table matched.
- **Names in the remaining Japanese text (user decision, 2026-10-24).** The
  name table is global. The user accepted English names inside the Japanese
  lines a roster image leaves: excluded characters' lines and one `MM.BIN` line
  (`EXP-0047`).
- **The Saturn's names, not the US arcade's (user decisions, 2026-10-25;
  provisional).** The Saturn is the Japanese release: its art, labels, and
  voice say Vega, Gouki, and Mech-Gouki. So the English text uses VEGA (not
  BISON), GOUKI (not AKUMA), and Mech-Gouki (not Cyber Akuma).
  - Implemented by `NAME_OVERRIDES` and `TEXT_OVERRIDES` in
    `tools/text/official_endings.py`. They cover the inserted names, the ending
    pages, the dialogue, and the combined image's win quotes (`EXP-0049`,
    `EXP-0050`).
  - The art and audio are not changed. The final policy is `LOC-001`; options
    and every affected line are in `docs/localization_plan.md`.
  - **An American-name variant also exists (`LOC-003`, user request
    2026-10-25).** `official_endings --names us` keeps the arcade's names
    (BISON, AKUMA, Cyber Akuma) in the text. It also switches the voice to the
    American name calls already on the disc (`EXP-0058`; no new samples). The
    name art is not changed yet (`LOC-004`). `--names saturn` (the default)
    is the build above.
- **Implemented for Ryu** in `EXP-0044`, with Ken and Gouki as partners
  (`tools/text/official_endings.py`). The text is read from the local ROM at
  build time and not committed.

Do not assume line ordering or correspondence across releases. Keep hypotheses in
`research_log.md` until supported, and do not represent a translation as final without
review. Store bulk source material locally under ignored paths; track only permitted
metadata and the minimal text needed for the project record.

## Secret-Character Policy (user decision, 2026-10-26, `SPECIAL-003`)

- Official English where it exists: Shadow's, U.S. Agent's and Mephisto's win
  quotes (`data/text/secret_roster.json`, same pairing as the roster) and
  every secret slot's partner lines.
- New translations where the official English is only a substitute: Metal
  Zangief's and Dark Sakura's own win quotes (the arcade and PS1 reuse
  Zangief's and Sakura's), and every secret ending page (the arcade shows a
  generic two-line message). The user chose this over the substitutes.
- `secret_characters.json` holds the English only. Each record names its
  Japanese source by SHA-256, and the build refuses a different source.
  Translator and method are recorded in the file (`EXP-0078`); the text is
  not official.
- Norimaro (slot 17, `SPECIAL-002`, `EXP-0079`) follows the same policy: his
  win quotes and partner lines are official English; his ending pages are a
  new translation in the same file.

