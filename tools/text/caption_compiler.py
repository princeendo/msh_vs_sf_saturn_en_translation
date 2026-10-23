"""Compile a structured caption file into a derived MSHvSF Saturn image.

Input is a JSON caption spec (``data/captions/caption_spec.schema.json``).

- ``mshvsf-captions/1`` lists records of Ryu's table (``MC09.PAC``, decoded
  ``0x91AC``).
- ``mshvsf-captions/2`` lists several quote tables, each with its ``file`` and
  decoded ``table`` offset (`EXP-0028`).

All tables share **one** font, so distinct pairs are allocated jointly across
files. Each record (index 0-15) gives two line strings. Each line is cut into
two-letter pairs. Each distinct pair becomes one pair glyph
(``glyph_patch.compose``) at a free font code.
``{P}`` keeps the record's ``0000`` partner-name placeholder cell, and is allowed
only at the cell where the original record has it. A pair of two spaces is the
blank cell ``0x0020``. Unused cells are blank. Records not listed are unchanged.

The build uses only confirmed mechanisms:

- `EXP-0023` same-size font repack: pairs at free codes, unseen kanji emptied
  only as needed;
- `EXP-0019`/`EXP-0022` same-size quote-PAC re-encode: splice, falling back to a
  full re-encode;
- `patch_image` in-place file replacement.

All source files are read from the untouched source track. Every step is verified
and recorded in ``compile_manifest.json``.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.iso9660 import Track, check_track, primary_volume, walk
from tools.disc.pac_lzss import PacFormatError, decode_file
from tools.disc.pac_patch import patch
from tools.disc.patch_image import find_entry
from tools.disc.patch_image import main as patch_image_main
from tools.disc.sector import verify_track
from tools.text.font import CELL_BYTES, Font
from tools.text.font_pack import Glyph, unpack
from tools.text.glyph_patch import compose
from tools.text.pair_font import build as build_font
from tools.text.pair_font import char_code, split_pairs, stored_size
from tools.text.quote_render import record_codes, render

SCHEMA = "mshvsf-captions/1"
SCHEMA_V2 = "mshvsf-captions/2"
DEFAULT_FILE = "MC09.PAC"
TABLE, RECORD, RECORDS, LINE_CELLS = 0x91AC, 76, 16, 19
BLANK, PLACEHOLDER = 0x0020, 0x0000
TOKEN = "{P}"
FONT_ENTRY = (0x6A558, 0x32740)  # MEMFIX.PAC entry 4 (EXP-0022)
# Free codes below the code count. 0x00A8-0x00B1 displayed in EXP-0023; the rest
# are empty in the original font but have not been shown on screen.
FREE_RANGES = ((0x00A8, 0x00FF), (0x0190, 0x01DF), (0x0260, 0x02AF))
KANJI = (0x0926, 0x0C5F)
MEMFIX_NAME = "MEMFIX.PAC;1"

Cell = str | None  # a two-character pair, or None for the placeholder


class SpecError(ValueError):
    pass


@dataclass(frozen=True)
class Caption:
    record: int
    lines: tuple[str, str]


def line_cells(text: str) -> list[Cell]:
    """Split a line into cells: two-character pairs and placeholder markers."""
    cells: list[Cell] = []
    for index, segment in enumerate(text.split(TOKEN)):
        if index:
            cells.append(None)
        if segment:
            for pair in split_pairs(segment):
                for char in pair:
                    char_code(char)  # raises ValueError for unsupported characters
                cells.append(pair)
    if len(cells) > LINE_CELLS:
        raise SpecError(f"line {text!r} needs {len(cells)} cells (max {LINE_CELLS})")
    return cells


def parse_spec(spec: dict[str, object]) -> list[Caption]:
    if spec.get("schema") != SCHEMA:
        raise SpecError(f"schema must be {SCHEMA!r}")
    entries = spec.get("records")
    if not isinstance(entries, list) or not entries:
        raise SpecError("records must be a non-empty list")
    captions: list[Caption] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SpecError("each record must be an object")
        record, lines = entry.get("record"), entry.get("lines")
        if not isinstance(record, int) or not 0 <= record < RECORDS:
            raise SpecError(f"record index must be 0-{RECORDS - 1}, got {record!r}")
        if (
            not isinstance(lines, list)
            or len(lines) != 2
            or not all(isinstance(line, str) for line in lines)
        ):
            raise SpecError(f"record {record}: lines must be two strings")
        captions.append(Caption(record, (lines[0], lines[1])))
    if len({c.record for c in captions}) != len(captions):
        raise SpecError("duplicate record index")
    return sorted(captions, key=lambda c: c.record)


@dataclass(frozen=True)
class TableSpec:
    file: str  # ISO 9660 name without version, for example "MC0A.PAC"
    table: int  # decoded offset of record 0
    captions: list[Caption]


def parse_tables(spec: dict[str, object]) -> list[TableSpec]:
    """Parse a v1 (Ryu only) or v2 (several tables) spec."""
    if spec.get("schema") == SCHEMA:
        return [TableSpec(DEFAULT_FILE, TABLE, parse_spec(spec))]
    if spec.get("schema") != SCHEMA_V2:
        raise SpecError(f"schema must be {SCHEMA!r} or {SCHEMA_V2!r}")
    entries = spec.get("tables")
    if not isinstance(entries, list) or not entries:
        raise SpecError("tables must be a non-empty list")
    tables: list[TableSpec] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SpecError("each table must be an object")
        name, offset = entry.get("file"), entry.get("table")
        if not isinstance(name, str) or not name.upper().endswith(".PAC"):
            raise SpecError(f"table file must be a .PAC name, got {name!r}")
        if not isinstance(offset, str) or not offset.startswith("0x"):
            raise SpecError(f"{name}: table must be a hex string like '0xA59C'")
        captions = parse_spec({"schema": SCHEMA, "records": entry.get("records")})
        tables.append(TableSpec(name.upper(), int(offset, 16), captions))
    if len({t.file for t in tables}) != len(tables):
        raise SpecError("duplicate table file")
    return tables


def record_cells(caption: Caption, original: Sequence[int]) -> list[Cell]:
    """All 38 cells of a record; blank pairs fill each line."""
    cells: list[Cell] = []
    for text in caption.lines:
        try:
            line = line_cells(text)
        except SpecError:
            raise
        except ValueError as error:
            raise SpecError(f"record {caption.record}: {error}") from error
        cells.extend(line + ["  "] * (LINE_CELLS - len(line)))
    for index, cell in enumerate(cells):
        if cell is None and original[index] != PLACEHOLDER:
            raise SpecError(
                f"record {caption.record}: {TOKEN} at cell {index}, where the "
                "original record has no placeholder"
            )
    return cells


def distinct_pairs(all_cells: Sequence[Sequence[Cell]]) -> list[str]:
    """Distinct non-blank pairs, in first-appearance order."""
    seen: dict[str, None] = {}
    for cells in all_cells:
        for cell in cells:
            if cell is not None and cell != "  ":
                seen.setdefault(cell, None)
    return list(seen)


def free_codes(image: bytes, ranges: Sequence[tuple[int, int]]) -> list[int]:
    header, glyphs = unpack(image)
    count = int.from_bytes(header[12:16], "big")
    return [
        code
        for low, high in ranges
        for code in range(low, high + 1)
        if code < count and glyphs[code].kind == "empty"
    ]


def table_writes(
    captions: Sequence[Caption],
    cells: Sequence[Sequence[Cell]],
    codes: dict[str, int],
    table: int = TABLE,
) -> dict[int, int]:
    """Decoded offset -> 16-bit value for every cell of every listed record."""
    writes: dict[int, int] = {}
    for caption, record in zip(captions, cells, strict=True):
        for index, cell in enumerate(record):
            if cell is None:
                value = PLACEHOLDER
            elif cell == "  ":
                value = BLANK
            else:
                value = codes[cell]
            writes[table + caption.record * RECORD + 2 * index] = value
    return writes


def capacity_tables(
    tables: Sequence[TableSpec],
    font_image: bytes,
    pacs: dict[str, bytes],
    candidates: Sequence[int],
    ranges: Sequence[tuple[int, int]] = FREE_RANGES,
) -> dict[str, object]:
    """Measure what a spec needs, without building (for specs that may not fit)."""
    cells = [record for table in table_cells(tables, pacs) for record in table]
    pairs = distinct_pairs(cells)
    _, glyphs = unpack(font_image)
    blank = bytes(CELL_BYTES)

    def cell(char: str) -> bytes:
        code = char_code(char)
        return blank if code is None else glyphs[code].cell

    needed = sum(
        stored_size(Glyph("compressed", compose(cell(p[0]), cell(p[1])))) for p in pairs
    )
    reclaimable = sum(stored_size(glyphs[c]) for c in candidates)
    free = len(free_codes(font_image, ranges))
    return {
        "tables": [t.file for t in tables],
        "records": len(cells),
        "pair_cells": sum(1 for r in cells for c in r if c not in (None, "  ")),
        "distinct_pairs": len(pairs),
        "free_codes": free,
        "pair_bytes": needed,
        "reclaimable_kanji_bytes": reclaimable,
        "fits": len(pairs) <= free and needed <= reclaimable,
        "cells_used": sum(len(c) - c.count("  ") for c in cells),
    }


def capacity(
    captions: Sequence[Caption],
    font_image: bytes,
    pac: bytes,
    candidates: Sequence[int],
    ranges: Sequence[tuple[int, int]] = FREE_RANGES,
) -> dict[str, object]:
    """Single-table form (Ryu, v1 specs) of ``capacity_tables``."""
    return capacity_tables(
        [TableSpec(DEFAULT_FILE, TABLE, list(captions))],
        font_image,
        {DEFAULT_FILE: pac},
        candidates,
        ranges,
    )


@dataclass(frozen=True)
class Compiled:
    font_image: bytes
    pac: bytes
    font_info: dict[str, object]
    pac_info: dict[str, object]
    codes: dict[str, int]
    writes: dict[int, int]


@dataclass(frozen=True)
class CompiledFile:
    pac: bytes
    pac_info: dict[str, object]
    writes: dict[int, int]


@dataclass(frozen=True)
class CompiledSet:
    font_image: bytes
    font_info: dict[str, object]
    codes: dict[str, int]
    files: dict[str, CompiledFile]


def table_cells(
    tables: Sequence[TableSpec], pacs: dict[str, bytes]
) -> list[list[list[Cell]]]:
    """Cells of every listed record, per table, checked against the originals."""
    out = []
    for spec in tables:
        decoded = decode_file(pacs[spec.file])[1]
        out.append(
            [
                record_cells(c, record_codes(decoded, c.record, spec.table))
                for c in spec.captions
            ]
        )
    return out


def compile_tables(
    tables: Sequence[TableSpec],
    font_image: bytes,
    pacs: dict[str, bytes],
    candidates: Sequence[int],
    ranges: Sequence[tuple[int, int]] = FREE_RANGES,
) -> CompiledSet:
    """Build one font image and every quote PAC (no disc I/O)."""
    cells = table_cells(tables, pacs)
    pairs = distinct_pairs([record for table in cells for record in table])
    available = free_codes(font_image, ranges)
    if len(pairs) > len(available):
        raise SpecError(
            f"{len(pairs)} distinct pairs, only {len(available)} free codes"
        )
    codes = dict(zip(pairs, available, strict=False))
    new_font, font_info = build_font(
        font_image, pairs, [codes[p] for p in pairs], candidates
    )
    files: dict[str, CompiledFile] = {}
    for spec, records in zip(tables, cells, strict=True):
        pac = pacs[spec.file]
        writes = table_writes(spec.captions, records, codes, spec.table)
        try:
            new_pac, pac_info = patch(pac, sorted(writes.items()))
            pac_info["mode"] = "splice"
        except PacFormatError:
            new_pac, pac_info = patch(pac, sorted(writes.items()), full=True)
            pac_info["mode"] = "full"
        files[spec.file] = CompiledFile(new_pac, pac_info, writes)
    return CompiledSet(new_font, font_info, codes, files)


def compile_files(
    captions: Sequence[Caption],
    font_image: bytes,
    pac: bytes,
    candidates: Sequence[int],
    ranges: Sequence[tuple[int, int]] = FREE_RANGES,
) -> Compiled:
    """Single-table form (Ryu, v1 specs) of ``compile_tables``."""
    result = compile_tables(
        [TableSpec(DEFAULT_FILE, TABLE, list(captions))],
        font_image,
        {DEFAULT_FILE: pac},
        candidates,
        ranges,
    )
    one = result.files[DEFAULT_FILE]
    return Compiled(
        result.font_image,
        one.pac,
        result.font_info,
        one.pac_info,
        result.codes,
        one.writes,
    )


def verify_font(
    old: bytes, new: bytes, compiled: Compiled | CompiledSet
) -> dict[str, object]:
    old_header, old_glyphs = unpack(old)
    new_header, new_glyphs = unpack(new)
    sacrificed = {int(c, 16) for c in compiled.font_info["sacrificed"]}  # type: ignore[attr-defined]
    pair_codes = set(compiled.codes.values())
    changed = {
        c for c, (a, b) in enumerate(zip(old_glyphs, new_glyphs, strict=True)) if a != b
    }
    blank = bytes(CELL_BYTES)

    def cell(char: str) -> bytes:
        code = char_code(char)
        return blank if code is None else old_glyphs[code].cell

    pairs_ok = all(
        new_glyphs[code].cell == compose(cell(pair[0]), cell(pair[1]))
        for pair, code in compiled.codes.items()
    )
    checks: dict[str, object] = {
        "header_unchanged": old_header == new_header,
        "changed_codes_expected": changed == pair_codes | sacrificed,
        "pairs_equal_composed": pairs_ok,
        "sacrificed_empty": all(new_glyphs[c].kind == "empty" for c in sacrificed),
        "pair_codes_were_empty": all(old_glyphs[c].kind == "empty" for c in pair_codes),
    }
    if not all(checks.values()):
        raise SpecError(f"font verification failed: {checks}")
    return checks


def verify_table(
    old_pac: bytes, new_pac: bytes, writes: dict[int, int]
) -> dict[str, object]:
    old, new = decode_file(old_pac)[1], decode_file(new_pac)[1]
    targets = set(writes)
    changed = [i for i in range(len(old)) if old[i] != new[i]]
    checks: dict[str, object] = {
        "decoded_length_unchanged": len(old) == len(new),
        "changes_only_in_target_cells": all((i & ~1) in targets for i in changed),
        "target_cells_expected": all(
            int.from_bytes(new[o : o + 2], "big") == v for o, v in writes.items()
        ),
        "file_size_unchanged": len(old_pac) == len(new_pac),
    }
    if not all(checks.values()):
        raise SpecError(f"table verification failed: {checks}")
    checks["changed_decoded_bytes"] = len(changed)
    return checks


def track_files(path: Path) -> dict[str, str]:
    with path.open("rb") as stream:
        track = Track(stream, path.stat().st_size)
        volume = primary_volume(track)
        return {
            entry.path: hashlib.sha256(
                track.read(entry.lsn, entry.size_bytes)
            ).hexdigest()
            for entry in walk(
                track, int(str(volume["root_lsn"])), int(str(volume["root_size"]))
            )
            if not entry.is_dir
        }


def verify_image(
    source: Path, built: Path, replaced: dict[str, bytes]
) -> dict[str, object]:
    with built.open("rb") as stream:
        check = check_track(stream, built.stat().st_size)
    invalid = verify_track(built)
    before, after = track_files(source), track_files(built)
    differing = sorted(name for name in before if before[name] != after.get(name))
    expected = {
        name: hashlib.sha256(data).hexdigest() for name, data in replaced.items()
    }
    checks: dict[str, object] = {
        "bad_sync": check.bad_sync,
        "non_mode1": check.non_mode1,
        "address_mismatch": check.address_mismatch,
        "invalid_edc_ecc": len(invalid),
        "files": len(after),
        "same_file_names": set(before) == set(after),
        "differing_files": differing,
        "replacements_match": all(after[n] == h for n, h in expected.items()),
    }
    ok = (
        check.bad_sync == check.non_mode1 == check.address_mismatch == 0
        and not invalid
        and checks["same_file_names"]
        and set(differing) <= set(replaced)
        and checks["replacements_match"]
    )
    if not ok:
        raise SpecError(f"image verification failed: {checks}")
    return checks


def build_image(
    source_dir: Path, manifest: Path, track: str, files: dict[str, Path], out_dir: Path
) -> dict[str, object]:
    argv = [
        "--source-dir",
        str(source_dir),
        "--manifest",
        str(manifest),
        "--track",
        track,
    ]
    for name, path in files.items():
        argv += ["--file", name, "--data", str(path)]
    argv += ["--out-dir", str(out_dir)]
    with contextlib.redirect_stdout(io.StringIO()):
        if patch_image_main(argv) != 0:
            raise SpecError("patch_image failed")
    report: dict[str, object] = json.loads(
        (out_dir / "build_manifest.json").read_text()
    )
    return report


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_candidates(path: Path) -> list[int]:
    unseen = [int(c, 16) for c in json.loads(path.read_text())["unseen_codes"]]
    # Highest codes first, as in EXP-0023.
    return sorted((c for c in unseen if KANJI[0] <= c <= KANJI[1]), reverse=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", type=Path, help="caption spec JSON")
    parser.add_argument(
        "--source-dir", type=Path, default=Path("local/disc_images/mshvsf_saturn_jp")
    )
    parser.add_argument(
        "--manifest", type=Path, default=Path("references/mshvsf/saturn_jp/README.md")
    )
    parser.add_argument(
        "--track",
        default="Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin",
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path("research/memory_dumps/exp0023/unseen_codes.json"),
    )
    parser.add_argument("--out-dir", type=Path, required=True, help="under build/")
    parser.add_argument("--files-only", action="store_true", help="skip the disc image")
    parser.add_argument(
        "--capacity", action="store_true", help="only report what the spec needs"
    )
    args = parser.parse_args(argv)

    track = args.source_dir / args.track
    try:
        tables = parse_tables(json.loads(args.spec.read_text()))
        pacs: dict[str, bytes] = {}
        with track.open("rb") as stream:
            disc = Track(stream, track.stat().st_size)
            lsn, size = find_entry(track, MEMFIX_NAME)
            memfix = disc.read(lsn, size)
            for spec in tables:
                lsn, size = find_entry(track, f"{spec.file};1")
                pacs[spec.file] = disc.read(lsn, size)
        offset, length = FONT_ENTRY
        old_font = memfix[offset : offset + length]
        candidates = load_candidates(args.candidates)
        if args.capacity:
            report_cap = capacity_tables(tables, old_font, pacs, candidates)
            print(json.dumps(report_cap, indent=1))
            return 0
        compiled = compile_tables(tables, old_font, pacs, candidates)
        new_memfix = memfix[:offset] + compiled.font_image + memfix[offset + length :]
        outputs = {"MEMFIX.PAC": new_memfix} | {
            name: f.pac for name, f in compiled.files.items()
        }
        report: dict[str, object] = {
            "tool": "tools.text.caption_compiler",
            "spec": str(args.spec),
            "spec_sha256": sha(args.spec.read_bytes()),
            "tables": [
                {
                    "file": t.file,
                    "table": f"0x{t.table:04X}",
                    "records": [c.record for c in t.captions],
                }
                for t in tables
            ],
            "source": {"MEMFIX.PAC": sha(memfix)}
            | {name: sha(data) for name, data in pacs.items()},
            "pairs": {f"0x{code:04X}": pair for pair, code in compiled.codes.items()},
            "font": compiled.font_info,
            "pac": {
                name: {k: v for k, v in f.pac_info.items() if k != "changes"}
                | {"writes": len(f.writes)}
                for name, f in compiled.files.items()
            },
            "outputs": {name: sha(data) for name, data in outputs.items()},
            "checks": {
                "font": verify_font(old_font, compiled.font_image, compiled),
                "memfix_outside_entry_unchanged": new_memfix[:offset] == memfix[:offset]
                and new_memfix[offset + length :] == memfix[offset + length :],
                "tables": {
                    name: verify_table(pacs[name], f.pac, f.writes)
                    for name, f in compiled.files.items()
                },
            },
        }
        files_dir = args.out_dir / "files"
        files_dir.mkdir(parents=True, exist_ok=True)
        for name, data in outputs.items():
            (files_dir / name).write_bytes(data)
        font = Font(compiled.font_image, 0, 0)
        for spec in tables:
            decoded = decode_file(compiled.files[spec.file].pac)[1]
            records = [record_codes(decoded, r, spec.table) for r in range(RECORDS)]
            stem = spec.file.split(".")[0]
            (args.out_dir / f"records-{stem}.png").write_bytes(render(font, records))
        if not args.files_only:
            files = {f"{name};1": files_dir / name for name in outputs}
            builds = []
            for suffix in ("a", "b"):
                out = args.out_dir / f"image_{suffix}"
                builds.append(
                    build_image(args.source_dir, args.manifest, args.track, files, out)
                )
            if builds[0]["output_sha256"] != builds[1]["output_sha256"]:
                raise SpecError("the two image builds differ")
            built_track = args.out_dir / "image_a" / args.track
            sectors = builds[0]["changed_sectors"]
            assert isinstance(sectors, list)
            report["image"] = {
                "output_sha256": builds[0]["output_sha256"],
                "changed_lsns": [s["lsn"] for s in sectors],
                "builds_identical": True,
                "checks": verify_image(
                    track,
                    built_track,
                    {f"{name};1": data for name, data in outputs.items()},
                ),
            }
    except (OSError, ValueError) as error:
        parser.error(str(error))
    (args.out_dir / "compile_manifest.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps({k: report[k] for k in ("tables", "outputs", "checks")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
