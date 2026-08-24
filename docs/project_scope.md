# Project Scope

## Objective

Localize the Japanese Sega Saturn release of *Marvel Super Heroes vs. Street
Fighter* into English through reproducible, evidence-led reverse engineering.

## Current Sequence

1. M0: establish and validate the research environment.
2. M1: identify and change one Ryu post-fight caption in live Saturn RAM.
3. M2: reproduce that change from an untouched source disc image.
4. Generalize only after M2 is reproducible.

Follow `TASKS.md` when present; do not bypass missing tasks, dependencies, blockers,
or acceptance criteria.

## References and Targets

- Modification target: MSHvSF Japanese Sega Saturn release only.
- Primary text reference: official English arcade/CPS-II release.
- Secondary text reference: English PlayStation release.
- X-Men vs. Street Fighter for Japanese Saturn is a technical reference only when a
  specific experiment warrants it; never modify it.

Reference releases are evidence and translation oracles, not structural templates.
Do not assume structures, offsets, encodings, addresses, or renderer behavior are
shared across releases or platforms.

## Deferred Work

Broad menus, graphics, gameplay text, FMV subtitles, and custom emulator development
are outside the current phase. Do not begin endings until the post-fight pipeline is
proven and generalized. Do not begin Norimaro or other special cases until the
ordinary-character pipeline is mature and an explicit task permits the work.
