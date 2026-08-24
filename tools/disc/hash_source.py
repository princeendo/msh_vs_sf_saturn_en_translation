"""Record immutable-source file identity without modifying the source."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class SourceIdentity:
    """Stable identifying metadata for one source file."""

    filename: str
    size_bytes: int
    sha256: str
    description: str


def identify_source(path: Path, description: str = "") -> SourceIdentity:
    """Calculate identifying metadata for a regular file."""
    if not path.is_file():
        raise ValueError(f"not a regular file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)

    return SourceIdentity(
        filename=path.name,
        size_bytes=path.stat().st_size,
        sha256=digest.hexdigest(),
        description=description,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report source-image identity without modifying the source."
    )
    parser.add_argument("files", nargs="+", type=Path, help="source files to hash")
    parser.add_argument(
        "--description",
        default="",
        help="game/version description applied to each reported file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="emit machine-readable JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        identities = [identify_source(path, args.description) for path in args.files]
    except (OSError, ValueError) as error:
        build_parser().error(str(error))

    if args.as_json:
        print(json.dumps([asdict(identity) for identity in identities], indent=2))
        return 0

    for index, identity in enumerate(identities):
        if index:
            print()
        print(f"Filename: {identity.filename}")
        print(f"Size: {identity.size_bytes} bytes")
        print(f"SHA-256: {identity.sha256}")
        print(f"Description: {identity.description or '(not provided)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
