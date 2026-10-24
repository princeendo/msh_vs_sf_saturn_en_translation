"""Read-only inspection of a 2352-byte data track and its ISO 9660 directory.

Raw sector layout (ECMA-130 Mode 1, as summarized in `docs/disc_layout.md`):

* bytes 0-11: sync pattern;
* bytes 12-14: BCD minute/second/frame header;
* byte 15: mode;
* bytes 16-2063: user data;
* the remaining bytes: EDC/ECC (not checked here).

Mode 2 Form 1 sectors (CD-ROM XA, used by PlayStation discs) carry an 8-byte
subheader at bytes 16-23 and user data at bytes 24-2071; the subheader's
submode bit 5 is clear for Form 1. Form 2 sectors (XA audio or video) have no
2048-byte user area and are rejected.

ISO 9660 fields follow ECMA-119:

* the primary volume descriptor is at LSN 16;
* both-endian numbers are read from their little-endian half;
* directory records hold the extent LSN, data length, flags, interleave fields,
  and the name.

The source track is only read. Extracted files go to a caller-chosen directory,
which must be ignored by git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections.abc import Iterator, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO

RAW_SECTOR = 2352
USER_DATA = 2048
SYNC = b"\x00" + b"\xff" * 10 + b"\x00"
FAD_OFFSET = 150


class DiscFormatError(ValueError):
    """Raised when sectors or ISO 9660 structures do not validate."""


def bcd(value: int) -> int:
    return (value >> 4) * 10 + (value & 0xF)


def header_fad(raw: bytes) -> int:
    """Return the frame address encoded in a raw sector header."""
    minute, second, frame = bcd(raw[12]), bcd(raw[13]), bcd(raw[14])
    return (minute * 60 + second) * 75 + frame


@dataclass(frozen=True)
class TrackCheck:
    """Validation summary for every raw sector in a track file."""

    size_bytes: int
    sectors: int
    bad_sync: int
    non_mode1: int
    address_mismatch: int
    first_fad: int
    last_fad: int


def check_track(stream: BinaryIO, size: int) -> TrackCheck:
    """Validate sync, mode, and header address for every sector."""
    if size % RAW_SECTOR:
        raise DiscFormatError(f"size {size} is not a multiple of {RAW_SECTOR}")
    sectors = size // RAW_SECTOR
    bad_sync = non_mode1 = mismatch = 0
    first_fad = last_fad = -1
    stream.seek(0)
    for index in range(sectors):
        raw = stream.read(RAW_SECTOR)
        if raw[:12] != SYNC:
            bad_sync += 1
            continue
        if raw[15] != 1:
            non_mode1 += 1
        fad = header_fad(raw)
        if index == 0:
            first_fad = fad
        last_fad = fad
        if fad != index + FAD_OFFSET:
            mismatch += 1
    return TrackCheck(size, sectors, bad_sync, non_mode1, mismatch, first_fad, last_fad)


class Track:
    """Random access to user data of a Mode 1/2352 track."""

    def __init__(self, stream: BinaryIO, size: int) -> None:
        if size % RAW_SECTOR:
            raise DiscFormatError(f"size {size} is not a multiple of {RAW_SECTOR}")
        self.stream = stream
        self.sectors = size // RAW_SECTOR

    def user(self, lsn: int) -> bytes:
        if not 0 <= lsn < self.sectors:
            raise DiscFormatError(f"LSN {lsn} is outside the track")
        self.stream.seek(lsn * RAW_SECTOR)
        raw = self.stream.read(RAW_SECTOR)
        if raw[:12] != SYNC:
            raise DiscFormatError(f"LSN {lsn} has no sync pattern")
        if raw[15] == 1:
            return raw[16 : 16 + USER_DATA]
        if raw[15] == 2 and not raw[18] & 0x20:
            return raw[24 : 24 + USER_DATA]
        raise DiscFormatError(f"LSN {lsn} is not a Mode 1 or Mode 2 Form 1 sector")

    def read(self, lsn: int, length: int) -> bytes:
        count = (length + USER_DATA - 1) // USER_DATA
        data = b"".join(self.user(lsn + i) for i in range(count))
        return data[:length]


@dataclass(frozen=True)
class Entry:
    """One ISO 9660 directory record."""

    path: str
    lsn: int
    size_bytes: int
    flags: int
    file_unit_size: int
    interleave_gap: int

    @property
    def is_dir(self) -> bool:
        return bool(self.flags & 0x02)


def parse_record(data: bytes, offset: int, parent: str) -> tuple[Entry, int]:
    length = data[offset]
    if length < 34 or offset + length > len(data):
        raise DiscFormatError(f"bad directory record length {length} at {offset}")
    lsn = struct.unpack_from("<I", data, offset + 2)[0]
    size = struct.unpack_from("<I", data, offset + 10)[0]
    flags = data[offset + 25]
    name_length = data[offset + 32]
    name = data[offset + 33 : offset + 33 + name_length].decode("latin-1")
    path = f"{parent}/{name}" if parent else name
    entry = Entry(path, lsn, size, flags, data[offset + 26], data[offset + 27])
    return entry, length


def primary_volume(track: Track) -> dict[str, object]:
    """Parse the primary volume descriptor at LSN 16."""
    pvd = track.user(16)
    if pvd[0] != 1 or pvd[1:6] != b"CD001":
        raise DiscFormatError("no primary volume descriptor at LSN 16")
    root, _ = parse_record(pvd, 156, "")
    return {
        "system_id": pvd[8:40].decode("latin-1").rstrip(),
        "volume_id": pvd[40:72].decode("latin-1").rstrip(),
        "volume_space_size": struct.unpack_from("<I", pvd, 80)[0],
        "logical_block_size": struct.unpack_from("<H", pvd, 128)[0],
        "root_lsn": root.lsn,
        "root_size": root.size_bytes,
    }


def walk(track: Track, lsn: int, size: int, parent: str = "") -> Iterator[Entry]:
    """Yield every entry below a directory extent, depth first."""
    data = track.read(lsn, size)
    offset = 0
    while offset < len(data):
        if data[offset] == 0:
            offset = (offset // USER_DATA + 1) * USER_DATA
            continue
        entry, length = parse_record(data, offset, parent)
        offset += length
        name = entry.path.rsplit("/", 1)[-1]
        if name in ("\x00", "\x01"):
            continue
        yield entry
        if entry.is_dir:
            yield from walk(track, entry.lsn, entry.size_bytes, entry.path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect a 2352-byte data track and list its ISO 9660 files."
    )
    parser.add_argument(
        "track", type=Path, help="Mode 1 or Mode 2 Form 1 BIN track (read only)"
    )
    parser.add_argument(
        "--check", action="store_true", help="validate every sector header"
    )
    parser.add_argument(
        "--extract", type=Path, help="write each file under this (ignored) directory"
    )
    parser.add_argument(
        "--user-stream",
        type=Path,
        help="write all user data, in LSN order, to this (ignored) file",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    track_path: Path = args.track
    for output in (args.extract, args.user_stream):
        if output is not None and output.resolve() == track_path.resolve():
            parser.error("output would overwrite the source track")
    try:
        size = track_path.stat().st_size
        with track_path.open("rb") as stream:
            report: dict[str, object] = {"track": str(track_path)}
            if args.check:
                report["check"] = asdict(check_track(stream, size))
            track = Track(stream, size)
            volume = primary_volume(track)
            report["primary_volume"] = volume
            files = []
            for entry in walk(
                track, int(str(volume["root_lsn"])), int(str(volume["root_size"]))
            ):
                record: dict[str, object] = asdict(entry)
                record["is_dir"] = entry.is_dir
                if not entry.is_dir:
                    try:
                        content = track.read(entry.lsn, entry.size_bytes)
                    except DiscFormatError as error:
                        record["sha256"] = None
                        record["unreadable"] = str(error)
                        files.append(record)
                        continue
                    record["sha256"] = hashlib.sha256(content).hexdigest()
                    if args.extract is not None:
                        target = args.extract / entry.path.split(";")[0]
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(content)
                files.append(record)
            report["files"] = files
            if args.user_stream is not None:
                args.user_stream.parent.mkdir(parents=True, exist_ok=True)
                with args.user_stream.open("wb") as out:
                    for lsn in range(track.sectors):
                        out.write(track.user(lsn))
    except (OSError, DiscFormatError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
