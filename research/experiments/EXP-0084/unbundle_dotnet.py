"""Extract named assemblies from a .NET single-file bundle (EXP-0084).

Usage: ``python3 -I unbundle_dotnet.py BUNDLE.exe OUT_DIR NAME [NAME ...]``

The bundle's manifest offset is the 8-byte value just before the bundle
signature. The manifest holds the format version, the file count, the bundle
id, five more header fields from version 2 on, and then one record per file:
offset, size, compressed size (version 6 on), type, and a 7-bit-length path.
Files whose path stem is one of NAME are written to OUT_DIR; every record is
printed.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

SIGNATURE = bytes.fromhex(
    "8b1202b96a612038727b930214d7a03213f5b9e6efae3318ee3b2dce24b36aae"
)


def read_string(data: bytes, offset: int) -> tuple[str, int]:
    length = shift = 0
    while True:
        byte = data[offset]
        offset += 1
        length |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            break
    return data[offset : offset + length].decode(), offset + length


def main(argv: list[str]) -> int:
    bundle, out_dir, names = Path(argv[1]), Path(argv[2]), set(argv[3:])
    data = bundle.read_bytes()
    header = struct.unpack_from("<q", data, data.index(SIGNATURE) - 8)[0]
    major, minor, count = struct.unpack_from("<IIi", data, header)
    bundle_id, offset = read_string(data, header + 12)
    if major >= 2:
        offset += 8 * 4 + 8
    print(f"bundle {major}.{minor}, {count} files, id {bundle_id}")
    for _ in range(count):
        start, size = struct.unpack_from("<qq", data, offset)
        offset += 16
        if major >= 6:
            offset += 8
        kind = data[offset]
        path, offset = read_string(data, offset + 1)
        print(path, size, kind)
        if path.split(".")[0] in names:
            (out_dir / path).write_bytes(data[start : start + size])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
