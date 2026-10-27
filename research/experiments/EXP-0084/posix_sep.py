"""Copy a .NET assembly with its user-string literal "\\" changed to "/" (EXP-0084).

Usage: ``python3 -I posix_sep.py IN.dll OUT.dll``

The official patcher strips its work folder from file paths with
``path.Replace(folder + "\\", "")``. On macOS paths use "/", so nothing
matches: no ``._DFR`` is applied and every file is treated as a raw track.
The literal is one entry in the metadata ``#US`` heap, shared by every use in
the assembly; the replacement has the same length, so only that entry's byte
changes. Walks PE -> CLI header -> metadata root -> ``#US`` and requires
exactly one such entry.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path


def file_offset(data: bytes, sections: list[tuple[int, int, int]], rva: int) -> int:
    for virtual, size, raw in sections:
        if virtual <= rva < virtual + size:
            return rva - virtual + raw
    raise ValueError(f"RVA {rva:#x} is in no section")


def main(argv: list[str]) -> int:
    data = bytearray(Path(argv[1]).read_bytes())
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optional = pe + 24
    pe32 = struct.unpack_from("<H", data, optional)[0] == 0x10B
    directories = optional + (96 if pe32 else 112)
    table = optional + struct.unpack_from("<H", data, pe + 20)[0]
    sections = []
    for i in range(count):
        size, virtual = struct.unpack_from("<II", data, table + 40 * i + 8)
        raw = struct.unpack_from("<I", data, table + 40 * i + 20)[0]
        sections.append((virtual, size, raw))
    cli_rva = struct.unpack_from("<I", data, directories + 14 * 8)[0]
    cli = file_offset(data, sections, cli_rva)
    root = file_offset(data, sections, struct.unpack_from("<I", data, cli + 8)[0])
    if data[root : root + 4] != b"BSJB":
        raise ValueError("no metadata root")
    pos = root + 16 + struct.unpack_from("<I", data, root + 12)[0] + 2
    streams = struct.unpack_from("<H", data, pos)[0]
    pos += 2
    heap = None
    for _ in range(streams):
        offset, size = struct.unpack_from("<II", data, pos)
        end = data.index(0, pos + 8)
        if data[pos + 8 : end] == b"#US":
            heap = (root + offset, size)
        pos = (end + 4) & ~3
    if heap is None:
        raise ValueError("no #US heap")
    start, size = heap
    hits, i = [], 1
    while i < size:
        first = data[start + i]
        if first & 0x80 == 0:
            length, head = first, 1
        elif first & 0xC0 == 0x80:
            length, head = ((first & 0x3F) << 8) | data[start + i + 1], 2
        else:
            length = int.from_bytes(data[start + i : start + i + 4], "big") & 0x1FFFFFFF
            head = 4
        text = start + i + head
        if length == 3 and data[text : text + 2] == b"\\\x00":
            hits.append(text)
        i += head + length
    if len(hits) != 1:
        raise ValueError(f"expected one backslash literal, found {len(hits)}")
    data[hits[0]] = ord("/")
    Path(argv[2]).write_bytes(data)
    print(f"#US entry at file offset {hits[0]:#x}: 0x5C -> 0x2F")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
