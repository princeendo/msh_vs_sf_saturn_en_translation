"""Distinct quote-font pairs per build variant, and what a merged font would add.

Usage: pair_union.py SPEC [SPEC ...]

Each spec is a generator output (``tools.text.official_endings --out``). Pairs
are counted the way the compiler counts them (``caption_compiler.line_cells``
and ``distinct_pairs``): every non-blank two-letter cell of every table line
and field. The first spec is the base; the report gives each spec's pair count,
the pairs it adds over the base, and the union of all specs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.text.caption_compiler import distinct_pairs, line_cells, parse_document


def pairs(path: Path) -> set[str]:
    tables, fields = parse_document(json.loads(path.read_text()))
    cells = [line_cells(line) for t in tables for c in t.captions for line in c.lines]
    cells += [line_cells(f.text) for f in fields if f.text]
    return set(distinct_pairs(cells))


def main(argv: list[str]) -> int:
    sets = {Path(a).stem: pairs(Path(a)) for a in argv}
    base_name, base = next(iter(sets.items()))
    union: set[str] = set()
    for name, found in sets.items():
        union |= found
        extra = sorted(found - base)
        print(f"{name}: {len(found)} pairs; over {base_name}: +{len(extra)} {extra}")
    print(f"union: {len(union)} pairs; over {base_name}: +{len(union - base)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
