"""Which text records, fields and patches differ between two build specs, per file.

Usage: record_diff.py SPEC_A SPEC_B

A run-time switch between the two builds would have to swap exactly these.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from tools.text.caption_compiler import parse_document, parse_patches


def entries(path: Path) -> dict[tuple[str, str], object]:
    document = json.loads(path.read_text())
    tables, fields = parse_document(document)
    out: dict[tuple[str, str], object] = {}
    for t in tables:
        for c in t.captions:
            out[(t.file, f"table 0x{t.table:X} record {c.record}")] = c.lines
    for f in fields:
        out[(f.file, f"field 0x{f.offset:X}")] = f.text
    for p in parse_patches(document):
        out[(p.file, f"patch {p!r}")] = True
    return out


def main(argv: list[str]) -> int:
    a, b = entries(Path(argv[0])), entries(Path(argv[1]))
    differ = Counter(key[0] for key in a.keys() | b.keys() if a.get(key) != b.get(key))
    for name, count in sorted(differ.items()):
        print(f"{name}: {count}")
    print(f"total: {sum(differ.values())} entries in {len(differ)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
