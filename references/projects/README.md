# Project References

Record relevant external projects, exact revisions, licenses, useful techniques, and
limits on applicability. Another project can motivate an experiment but cannot prove
MSHvSF behavior.

The evaluated `DOC-005` corpus is cataloged in `docs/references.md`. Direct code reuse
requires both an explicit license and confirmation that the particular file is inside
that license's scope. Game-derived text, images, screenshots, binary patches, and
third-party tools are not reusable merely because they appear in a public repository.

Current method references:

| Project | License status | Bounded use |
| --- | --- | --- |
| `coregee/devil_summoner_tools` | 0BSD with explicit exclusions | Source manifests, guarded patches, transactional rebuild and verification patterns. |
| `ralfguth/langrisser3-english` | GPL-3.0-or-later with third-party notices | Growth-aware ISO rebuild, EDC/ECC repair, mixed-mode output, and tests. |
| `benclaff/culdcept_saturn_tools` | GPL-3.0-or-later | Structured extraction, control preservation, and capacity rejection. |
| `eadmaster/pcrown` | GPL-2.0, mixed-provenance tree | Released pipeline and reload-boundary testing lesson; reuse only clearly scoped source. |
| `new-parm-archives-tools` | Conflicting MIT scope statements | Documentation lead only until clarified. |

Unlicensed projects remain question-generating leads only. Do not copy their code,
scripts, prose, images, patches, or derived data.
