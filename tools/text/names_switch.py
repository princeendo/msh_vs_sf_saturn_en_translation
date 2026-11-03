"""OPT-005: the NAMES switch's sites, the places where the name variants differ.

The image is built with American names (the default, user 2026-11-02). Each
frame, the tail's ``vblank`` routine (``data/opt004/submenu.s``) checks every
site and copies the chosen variant's bytes over the other variant's.

- The generator diffs the American spec with the Saturn spec built from the
  same arguments (``alternates``). The result is the spec's ``names_switch``
  list: Saturn records, fields and byte patches.
- The compiler counts those records' and fields' pairs into the one font, so
  both variants share one code map (`EXP-0106`). After the build it encodes
  the Saturn bytes and reads the American bytes from its own outputs
  (``sites``), then packs the site table (``pack``).

Run-time homes (`OPT-005`, from states):
- ``MM.BIN`` is resident at ``0x06018B00``;
- character PACs decode into four 64 KiB WRAM-L slots from ``0x00200000``;
- ``ME.PAC`` is at ``0x001FFFF0`` + file offset for the ending;
- MEMFIX entry 7 (the name calls) is in sound RAM at ``0x05A06510``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tools.disc.pac_lzss import decode_file

MM_BASE = 0x06018B00
ME_BASE = 0x001FFFF0
SLOT_STEP, SLOTS = 0x10000, 4  # from 0x00200000 (in submenu.s)
ENTRY7 = (0x123BB8, 0x3BC0)  # MEMFIX.PAC entry 7: offset, size
SOUND_ENTRY7 = 0x05A06510
RECORD = 76


NAMES_BIT, GRAMMAR_BIT = 1, 2  # bits of the saved setting 0x06017AB4


@dataclass(frozen=True)
class Site:
    """``american`` is the disc's bytes and ``saturn`` the other variant's: for
    a GRAMMAR site (``switch`` 2) the official and the corrected text."""

    address: int  # absolute, or the offset in each character slot
    slots: bool
    american: bytes
    saturn: bytes
    switch: int = NAMES_BIT


def _key(entry: Mapping[str, object]) -> tuple[str, int]:
    return str(entry["file"]).upper(), int(str(entry["offset"]), 16)


def alternates(
    american: Mapping[str, object], saturn: Mapping[str, object]
) -> list[dict[str, object]]:
    """The Saturn spec's records, fields and patches that differ from the
    American spec's (spec v3 entries)."""
    out: list[dict[str, object]] = []

    def records(spec: Mapping[str, object]) -> dict[tuple[str, int, int], list[str]]:
        found = {}
        for table in spec["tables"]:  # type: ignore[attr-defined]
            for record in table["records"]:
                found[
                    (table["file"].upper(), int(table["table"], 16), record["record"])
                ] = record["lines"]
        return found

    ours, theirs = records(american), records(saturn)
    if set(ours) != set(theirs):
        raise ValueError("the two variants list different records")
    for (name, table, record), lines in sorted(theirs.items()):
        if ours[(name, table, record)] != lines:
            out.append(
                {
                    "kind": "record",
                    "file": name,
                    "table": f"0x{table:X}",
                    "record": record,
                    "lines": lines,
                }
            )

    def fields(spec: Mapping[str, object]) -> dict[tuple[str, int], dict[str, object]]:
        return {_key(f): f for f in spec.get("fields", [])}  # type: ignore[attr-defined]

    ours_f, theirs_f = fields(american), fields(saturn)
    if set(ours_f) != set(theirs_f):
        raise ValueError("the two variants list different fields")
    for key, field in sorted(theirs_f.items()):
        if ours_f[key]["text"] != field["text"]:
            out.append({"kind": "field", **field})

    def patches(spec: Mapping[str, object]) -> dict[tuple[str, int], dict[str, object]]:
        # The sub-menu's own patches (OPT-004/OPT-005) do not depend on the
        # names; the two specs place the tail differently (EXP-0112).
        return {
            _key(p): p
            for p in spec.get("patches", [])  # type: ignore[attr-defined]
            if not str(p.get("why", "")).startswith("OPT-004")
        }

    ours_p, theirs_p = patches(american), patches(saturn)
    for key in sorted(set(ours_p) | set(theirs_p)):
        a, s = ours_p.get(key), theirs_p.get(key)
        a_hex = a["hex"] if a else (s or {}).get("expect")
        s_hex = s["hex"] if s else (a or {}).get("expect")
        if a_hex == s_hex:
            continue
        if not isinstance(a_hex, str) or not isinstance(s_hex, str):
            raise ValueError(f"{key}: a one-variant patch needs its expected bytes")
        out.append(
            {
                "kind": "bytes",
                "file": key[0],
                "offset": f"0x{key[1]:X}",
                "american": a_hex,
                "saturn": s_hex,
            }
        )
    return out


def home(name: str, offset: int) -> tuple[int, bool]:
    """Run-time address (or slot offset) of a file offset."""
    if name == "MM.BIN":
        return MM_BASE + offset, False
    if name == "ME.PAC":
        return ME_BASE + offset, False
    if name.startswith("MC") and name.endswith(".PAC"):
        return offset, True
    if name == "MEMFIX.PAC" and ENTRY7[0] <= offset < sum(ENTRY7):
        return SOUND_ENTRY7 + offset - ENTRY7[0], False
    raise ValueError(f"no run-time home known for {name} 0x{offset:X}")


def sites(
    entries: Sequence[Mapping[str, object]],
    outputs: Mapping[str, bytes],
    saturn_writes: Mapping[tuple[str, int], int],
) -> list[Site]:
    """One site per entry. American bytes come from the built files (decoded
    PACs); the Saturn bytes are those overlaid with ``saturn_writes`` (16-bit
    values by file offset, for records and fields) or the entry's own bytes.
    Each site is widened to an even start and an even length of at least 4."""
    decoded: dict[str, bytes] = {}

    def data(name: str) -> bytes:
        if name not in decoded:
            raw = outputs[name]
            decoded[name] = decode_file(raw)[1] if name.startswith("MC") else raw
        return decoded[name]

    out = []
    spans: list[tuple[str, int, int, int]] = []
    for entry in entries:
        name = str(entry["file"]).upper()
        kind = entry["kind"]
        if kind == "record":
            start = int(str(entry["table"]), 16) + RECORD * int(str(entry["record"]))
            end = start + RECORD
        elif kind == "field":
            start = int(str(entry["offset"]), 16)
            end = start + 2 * int(str(entry["cells"]))
        else:
            start = int(str(entry["offset"]), 16)
            end = start + len(bytes.fromhex(str(entry["saturn"])))
        start -= start % 2
        end = max(end + end % 2, start + 4)
        american = data(name)[start:end]
        saturn = bytearray(american)
        if kind == "bytes":
            new = bytes.fromhex(str(entry["saturn"]))
            begin = int(str(entry["offset"]), 16) - start
            if american[begin : begin + len(new)] != bytes.fromhex(
                str(entry["american"])
            ):
                raise ValueError(
                    f"{name} 0x{start:X}: the built bytes are not the American ones"
                )
            saturn[begin : begin + len(new)] = new
        else:
            for offset in range(start, end, 2):
                value = saturn_writes.get((name, offset))
                if value is not None:
                    saturn[offset - start : offset - start + 2] = value.to_bytes(
                        2, "big"
                    )
        if bytes(saturn) == american:
            continue
        address, slots = home(name, start)
        switch = int(str(entry.get("switch", NAMES_BIT)))
        spans.append((name, start, end, switch))
        out.append(Site(address, slots, american, bytes(saturn), switch))
    # A NAMES and a GRAMMAR site must not share bytes of one file (slot
    # offsets of different files may coincide: the copy checks contents).
    for (name_a, a0, a1, sw_a), (name_b, b0, b1, sw_b) in (
        (a, b) for i, a in enumerate(spans) for b in spans[i + 1 :]
    ):
        if name_a == name_b and sw_a != sw_b and a0 < b1 and b0 < a1:
            raise ValueError(
                f"a NAMES site and a GRAMMAR site overlap in {name_a} 0x{a0:X}"
            )
    return out


def pack(found: Sequence[Site]) -> bytes:
    """The site table read by ``vblank``: per site the address (or slot
    offset), the byte length, 1 for slots, the offset of a 4-byte probe where
    the variants differ, the setting bit (1 NAMES, 2 GRAMMAR), then the disc's
    bytes and the other variant's, padded to 4.
    A zero address ends the table."""
    out = bytearray()
    for site in found:
        length = len(site.american)
        first = next(i for i in range(length) if site.american[i] != site.saturn[i])
        probe = min(first - first % 2, length - 4)
        out += site.address.to_bytes(4, "big") + length.to_bytes(2, "big")
        out += (
            (1 if site.slots else 0).to_bytes(2, "big")
            + probe.to_bytes(2, "big")
            + site.switch.to_bytes(2, "big")
        )
        out += site.american + site.saturn
        out += bytes(-len(out) % 4)
    return bytes(out) + bytes(4)


def unpack(table: bytes) -> list[Site]:
    """The sites of a packed table (``pack``), up to its zero address."""
    out, at = [], 0
    while (address := int.from_bytes(table[at : at + 4], "big")) != 0:
        length = int.from_bytes(table[at + 4 : at + 6], "big")
        slots = int.from_bytes(table[at + 6 : at + 8], "big") == 1
        switch = int.from_bytes(table[at + 10 : at + 12], "big")
        body = at + 12
        out.append(
            Site(
                address,
                slots,
                table[body : body + length],
                table[body + length : body + 2 * length],
                switch,
            )
        )
        at = body + 2 * length
        at += -at % 4
    return out
