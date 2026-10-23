"""Audit MAME-style arcade ROM zips against a pinned MAME driver source.

The driver source is read as text; nothing is executed or extracted to disk. Zip
members are hashed in memory, and the archives are opened read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
import zlib
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROM_START = re.compile(r"^ROM_START\(\s*(\w+)\s*\)")
ROM_END = re.compile(r"^ROM_END\b")
ROM_REGION = re.compile(r'^ROM_REGION\w*\(\s*[^,]+,\s*"([^"]+)"')
ROM_LOAD = re.compile(
    r'^(ROM_LOAD\w*)\(\s*"([^"]+)"\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*,'
    r"\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*CRC\(([0-9a-fA-F]{8})\)"
    r"\s*SHA1\(([0-9a-fA-F]{40})\)"
)
ROM_CONTINUE = re.compile(
    r"^ROM_CONTINUE\(\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*\)"
)
GAME = re.compile(
    r'^GAME\(\s*\d+\s*,\s*(\w+)\s*,\s*(\w+)\s*,(?:[^,]*,){5}\s*"([^"]*)"'
    r'\s*,\s*"([^"]*)"'
)


@dataclass
class RomEntry:
    """One ROM file as a driver definition expects it."""

    name: str
    size: int
    crc32: str
    sha1: str
    region: str = ""
    offset: int = 0
    loader: str = ""


@dataclass
class RomSet:
    """One ROM_START block and its GAME() metadata."""

    name: str
    roms: list[RomEntry] = field(default_factory=list)
    parent: str = ""
    manufacturer: str = ""
    title: str = ""


@dataclass(frozen=True)
class MemberResult:
    """Audit outcome for one expected ROM file."""

    name: str
    status: str
    expected_crc32: str
    expected_sha1: str
    actual_crc32: str = ""
    actual_sha1: str = ""


@dataclass(frozen=True)
class AuditReport:
    """Audit outcome for one zip against one set definition."""

    archive: str
    set_name: str
    title: str
    members: list[MemberResult]
    unexpected: list[str]

    @property
    def matched(self) -> int:
        return sum(member.status == "ok" for member in self.members)

    @property
    def complete(self) -> bool:
        return self.matched == len(self.members) and not self.unexpected


def parse_driver(source: str) -> dict[str, RomSet]:
    """Parse ROM_START blocks and GAME() lines from MAME driver text."""
    sets: dict[str, RomSet] = {}
    current: RomSet | None = None
    region = ""
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if match := ROM_START.match(line):
            current = RomSet(match.group(1))
            sets[current.name] = current
        elif current is not None and ROM_END.match(line):
            current = None
        elif current is not None and (match := ROM_REGION.match(line)):
            region = match.group(1)
        elif current is not None and (match := ROM_LOAD.match(line)):
            loader, name, offset, length, crc, sha1 = match.groups()
            current.roms.append(
                RomEntry(
                    name,
                    int(length, 0),
                    crc.lower(),
                    sha1.lower(),
                    region,
                    int(offset, 0),
                    loader,
                )
            )
        elif current is not None and (match := ROM_CONTINUE.match(line)):
            if not current.roms:
                raise ValueError(f"ROM_CONTINUE without ROM_LOAD in {current.name}")
            current.roms[-1].size += int(match.group(2), 0)
        elif match := GAME.match(line):
            name, parent, manufacturer, title = match.groups()
            if name in sets:
                sets[name].parent = "" if parent == "0" else parent
                sets[name].manufacturer = manufacturer
                sets[name].title = title
    return sets


def hash_members(archive: Path) -> dict[str, tuple[int, str, str]]:
    """Return {member name: (size, CRC-32, SHA-1)} for every file in a zip."""
    hashes: dict[str, tuple[int, str, str]] = {}
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            if info.is_dir():
                continue
            data = bundle.read(info)
            crc = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
            hashes[info.filename] = (len(data), crc, hashlib.sha1(data).hexdigest())
    return hashes


def audit(
    archive_name: str, members: dict[str, tuple[int, str, str]], romset: RomSet
) -> AuditReport:
    """Compare hashed zip members with one set definition."""
    results: list[MemberResult] = []
    for rom in romset.roms:
        if rom.name not in members:
            results.append(MemberResult(rom.name, "missing", rom.crc32, rom.sha1))
            continue
        size, crc, sha1 = members[rom.name]
        if size != rom.size:
            status = "bad_size"
        elif crc != rom.crc32 or sha1 != rom.sha1:
            status = "bad_hash"
        else:
            status = "ok"
        results.append(MemberResult(rom.name, status, rom.crc32, rom.sha1, crc, sha1))
    expected = {rom.name for rom in romset.roms}
    unexpected = sorted(name for name in members if name not in expected)
    return AuditReport(archive_name, romset.name, romset.title, results, unexpected)


def family(sets: dict[str, RomSet], root: str) -> list[RomSet]:
    """Return a parent set and its clones, in driver order."""
    return [rs for rs in sets.values() if root in (rs.name, rs.parent)]


def rank_candidates(
    archive_name: str,
    members: dict[str, tuple[int, str, str]],
    candidates: Sequence[RomSet],
) -> list[tuple[str, int, int]]:
    """Return (set, matched, expected) sorted by matched files, best first."""
    ranked = []
    for romset in candidates:
        report = audit(archive_name, members, romset)
        ranked.append((romset.name, report.matched, len(report.members)))
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True, help="MAME driver .cpp")
    parser.add_argument(
        "--expect-driver-sha256",
        default="",
        help="refuse to run unless the driver source has this SHA-256",
    )
    parser.add_argument(
        "--set",
        dest="set_name",
        default="",
        help="set to audit against (default: each zip's file stem)",
    )
    parser.add_argument(
        "--family",
        default="",
        help="also rank every set in this parent's family by matching files",
    )
    parser.add_argument("archives", nargs="+", type=Path, help="ROM zip files")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    driver_bytes = args.driver.read_bytes()
    driver_sha256 = hashlib.sha256(driver_bytes).hexdigest()
    if args.expect_driver_sha256 and driver_sha256 != args.expect_driver_sha256:
        parser.error(f"driver SHA-256 mismatch: {driver_sha256}")
    sets = parse_driver(driver_bytes.decode("utf-8"))

    results: list[tuple[AuditReport, list[tuple[str, int, int]]]] = []
    for archive in args.archives:
        set_name = args.set_name or archive.stem
        if set_name not in sets:
            parser.error(f"set not defined in driver: {set_name}")
        members = hash_members(archive)
        report = audit(archive.name, members, sets[set_name])
        candidates = (
            rank_candidates(archive.name, members, family(sets, args.family))
            if args.family
            else []
        )
        results.append((report, candidates))

    if args.as_json:
        audits = [
            {
                **asdict(report),
                "matched": report.matched,
                "complete": report.complete,
                "candidates": candidates,
            }
            for report, candidates in results
        ]
        print(json.dumps({"driver_sha256": driver_sha256, "audits": audits}, indent=2))
        return 0

    print(f"Driver SHA-256: {driver_sha256}")
    for report, candidates in results:
        print()
        print(f"{report.archive} vs {report.set_name} ({report.title})")
        print(f"  matched {report.matched}/{len(report.members)} files")
        for member in report.members:
            if member.status != "ok":
                print(f"  {member.status}: {member.name}")
        for name in report.unexpected:
            print(f"  unexpected: {name}")
        for name, matched, expected in candidates:
            print(f"  candidate {name}: {matched}/{expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
