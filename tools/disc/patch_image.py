"""Write a derived disc image with ISO 9660 files replaced in place.

Safety rules (AGENTS.md rule 1):

- Source components are only read, and their SHA-256 must appear in the tracked
  manifest.
- Output must be under the repository's `build/` directory and must not overlap
  the source directory.
- The replacement must have exactly the original file size. The ISO 9660
  directory is therefore unchanged, and only the file's own sectors are
  rewritten.
- Rewritten sectors get regenerated Mode 1 EDC/ECC. All other bytes and files are
  copied unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections.abc import Sequence
from pathlib import Path

from tools.disc.iso9660 import RAW_SECTOR, USER_DATA, Track, primary_volume, walk
from tools.disc.sector import regenerate

REPO_ROOT = Path(__file__).resolve().parents[2]
CHUNK = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def find_entry(track_path: Path, name: str) -> tuple[int, int]:
    with track_path.open("rb") as stream:
        track = Track(stream, track_path.stat().st_size)
        volume = primary_volume(track)
        for entry in walk(
            track, int(str(volume["root_lsn"])), int(str(volume["root_size"]))
        ):
            if entry.path == name and not entry.is_dir:
                return entry.lsn, entry.size_bytes
    raise ValueError(f"file {name!r} not found")


def replace_files(
    source: Path, target: Path, replacements: Sequence[tuple[int, int, bytes]]
) -> list[dict[str, object]]:
    """Copy ``source`` to ``target``, rewriting each replacement's sectors."""
    spans: dict[int, tuple[int, bytes]] = {}
    for lsn, size, data in replacements:
        if len(data) != size:
            raise ValueError(f"replacement is {len(data)} bytes; the file is {size}")
        count = (size + USER_DATA - 1) // USER_DATA
        for index in range(lsn, lsn + count):
            if index in spans:
                raise ValueError(f"replacements overlap at LSN {index}")
            spans[index] = (lsn, data)
    changed: list[dict[str, object]] = []
    with source.open("rb") as src, target.open("wb") as dst:
        sectors = source.stat().st_size // RAW_SECTOR
        for index in range(sectors):
            raw = src.read(RAW_SECTOR)
            if index in spans:
                lsn, data = spans[index]
                piece = data[(index - lsn) * USER_DATA : (index - lsn + 1) * USER_DATA]
                user = piece + raw[16 + len(piece) : 16 + USER_DATA]
                new_raw = regenerate(raw[:16] + user + raw[16 + USER_DATA :])
                if new_raw != raw:
                    changed.append(
                        {
                            "lsn": index,
                            "original_sha256": hashlib.sha256(raw).hexdigest(),
                            "modified_sha256": hashlib.sha256(new_raw).hexdigest(),
                        }
                    )
                raw = new_raw
            dst.write(raw)
    return changed


def replace_file(
    source: Path, target: Path, lsn: int, size: int, data: bytes
) -> list[dict[str, object]]:
    """Copy ``source`` to ``target``, rewriting one file's sectors."""
    return replace_files(source, target, [(lsn, size, data)])


def load_manifest_hashes(manifest: Path) -> set[str]:
    text = manifest.read_text()
    return {
        token.strip("`")
        for token in text.split()
        if len(token.strip("`")) == 64
        and all(c in "0123456789abcdef" for c in token.strip("`"))
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a derived image with files replaced in place."
    )
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True, help="tracked hashes")
    parser.add_argument("--track", required=True, help="data track filename in source")
    parser.add_argument(
        "--file", action="append", required=True, help="ISO 9660 name; repeatable"
    )
    parser.add_argument(
        "--data", action="append", type=Path, required=True, help="paired with --file"
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    source_dir: Path = args.source_dir.resolve()
    out_dir: Path = args.out_dir.resolve()
    build_root = (REPO_ROOT / "build").resolve()
    if build_root not in out_dir.parents and out_dir != build_root:
        parser.error(f"output must be under {build_root}")
    if out_dir == source_dir or source_dir in out_dir.parents:
        parser.error("output overlaps the source directory")

    try:
        known = load_manifest_hashes(args.manifest)
        components = sorted(p for p in source_dir.iterdir() if p.is_file())
        source_hashes = {p.name: sha256_file(p) for p in components}
        missing = [
            name for name, digest in source_hashes.items() if digest not in known
        ]
        if missing:
            parser.error(f"source components not in manifest: {missing}")
        if len(args.file) != len(args.data):
            parser.error("give one --data per --file")
        track = source_dir / args.track
        replacements = []
        files = []
        for name, data_path in zip(args.file, args.data, strict=True):
            lsn, size = find_entry(track, name)
            data = data_path.read_bytes()
            replacements.append((lsn, size, data))
            files.append(
                {
                    "file": name,
                    "lsn": lsn,
                    "size": size,
                    "replacement_sha256": hashlib.sha256(data).hexdigest(),
                }
            )
        out_dir.mkdir(parents=True, exist_ok=True)
        changed = replace_files(track, out_dir / args.track, replacements)
        for component in components:
            if component.name != args.track:
                shutil.copyfile(component, out_dir / component.name)
        after = {p.name: sha256_file(p) for p in components}
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if after != source_hashes:
        parser.error("source components changed during the build")
    output_hashes = {name: sha256_file(out_dir / name) for name in source_hashes}
    report = {
        "tool": "tools.disc.patch_image",
        "files": files,
        "changed_sectors": changed,
        "source_sha256": source_hashes,
        "output_sha256": output_hashes,
    }
    (out_dir / "build_manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in ("source_sha256",)}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
