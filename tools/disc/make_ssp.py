"""Make and verify a Sega Saturn Patcher (.ssp) release patch (REL-002).

An ``.ssp`` is a ZIP archive (``EXP-0084``). The entries this tool writes:

| Entry | Content |
| --- | --- |
| ``NAME._DFR`` | BSDIFF40 patch turning the original file ``NAME`` into the new one |
| ``version.txt`` | format version; the official patcher refuses a patch without it |
| ``readme.txt`` | text the official patcher shows |
| ``meta.txt`` | ``Key:Value`` lines (name, author, URL, version, description) |
| ``driveOrder.txt`` | every ISO 9660 entry by extent: ``PATH,INDEX,XAMODE`` |
| ``changes.md5`` | ``NAME:MD5`` of each original file that has a ``._DFR`` |

The official patcher (Knight0fDragon, v1.95) extracts the image's files, applies
each ``._DFR`` with bspatch, and rebuilds the image in ``driveOrder.txt`` order;
it fails without ``version.txt`` or ``driveOrder.txt``. The open-source
``saturn-patcher-egui`` checks each source file against ``changes.md5`` and
rewrites the patched files in place, regenerating EDC/ECC. The official
patcher's optional ``ip.bin`` would replace the image's whole 32 KiB system
area; it is left out, so the image keeps its own and no boot code is shipped.

Each ``._DFR`` is made by ``bsdiff40`` below, a pure-Python bsdiff 4 scan
(no new dependency) whose output any BSDIFF40 bspatch applies.

Safety and reproducibility follow ``make_patch``: the source must be in the
tracked manifest, the built track 01 must match its regression reference, the
patch is written under ``build/`` (it holds game-derived data and is never
committed), it is built twice and must be byte-identical, and it is applied to
a copy of the source with this module's own applier and compared with the built
track.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import io
import json
import zipfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.iso9660 import RAW_SECTOR, USER_DATA, Entry, Track, primary_volume, walk
from tools.disc.make_patch import (
    BASELINE,
    SOURCE_DIR,
    SOURCE_MANIFEST,
    TRACK01,
    compare_images,
    components,
    reference_track01,
)
from tools.disc.patch_image import (
    REPO_ROOT,
    load_manifest_hashes,
    replace_files,
    sha256_file,
)

# The version the official patcher v1.3 wrote into the sample patch (EXP-0084).
# v1.95 reads "1.0" as its older text format and refuses a patch whose version
# is newer than itself, so the oldest bsdiff-format version is the safest.
SSP_VERSION = "1.3.7760.32512"
BSDIFF_MAGIC = b"BSDIFF40"
CHUNK = 2048
BACK = 4096
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
META_KEYS = ("Name", "Author", "URL", "Version", "Description", "Contact")
AUTHOR = "MSHvSF Saturn localization contributors"
URL = "https://github.com/princeendo/msh_vs_sf_saturn_en_translation"
TITLE = "Marvel Super Heroes vs. Street Fighter (Japan) - English"


def offtout(value: int) -> bytes:
    """bsdiff's 8-byte sign-magnitude little-endian integer."""
    magnitude = abs(value)
    if magnitude >= 1 << 63:
        raise ValueError(f"{value} does not fit")
    return (magnitude | (1 << 63 if value < 0 else 0)).to_bytes(8, "little")


def offtin(data: bytes) -> int:
    raw = int.from_bytes(data[:8], "little")
    magnitude = raw & ((1 << 63) - 1)
    return -magnitude if raw >> 63 else magnitude


def _add(base: bytes, delta: bytes, sign: int) -> bytes:
    """``base + sign * delta`` per byte, modulo 256; equal chunks skip the work."""
    out = bytearray(base)
    zero = bytes(CHUNK)
    for start in range(0, len(delta), CHUNK):
        piece = delta[start : start + CHUNK]
        if piece == zero[: len(piece)]:
            continue
        for i, value in enumerate(piece, start):
            out[i] = (out[i] + sign * value) & 0xFF
    return bytes(out)


def equal_count(a: bytes, b: bytes) -> int:
    """How many positions hold the same byte in two equal-length strings."""
    x = int.from_bytes(a, "little") ^ int.from_bytes(b, "little")
    return x.to_bytes(len(a), "little").count(0)


def common_prefix(a: bytes, i: int, b: bytes, j: int) -> int:
    """Length of the longest common prefix of ``a[i:]`` and ``b[j:]``."""
    limit = min(len(a) - i, len(b) - j)
    step, n = 1, 0
    while n < limit and a[i + n : i + n + step] == b[j + n : j + n + step]:
        n += step
        step *= 2
    while step > 1 and n < limit:
        step //= 2
        if a[i + n : i + n + step] == b[j + n : j + n + step]:
            n += step
    return min(n, limit)


class _Index:
    """Positions of each ``KEY``-byte string of ``old``, newest first."""

    KEY = 8
    CHAIN = 32

    def __init__(self, old: bytes) -> None:
        self.old = old
        self.head: dict[bytes, int] = {}
        self.prev = [-1] * len(old)
        for pos in range(len(old) - self.KEY + 1):
            key = old[pos : pos + self.KEY]
            self.prev[pos] = self.head.get(key, -1)
            self.head[key] = pos

    def longest(self, new: bytes, scan: int, hints: Sequence[int]) -> tuple[int, int]:
        """(length, old position) of the longest match for ``new[scan:]``."""
        best_len, best_pos = 0, 0
        candidates = [p for p in hints if 0 <= p < len(self.old)]
        pos = self.head.get(new[scan : scan + self.KEY], -1)
        while pos >= 0 and len(candidates) < self.CHAIN + len(hints):
            candidates.append(pos)
            pos = self.prev[pos]
        for pos in candidates:
            length = common_prefix(new, scan, self.old, pos)
            if length > best_len:
                best_len, best_pos = length, pos
        return best_len, best_pos


def _forward(old: bytes, opos: int, new: bytes, npos: int, limit: int) -> int:
    """bsdiff's forward extension: the prefix length maximising 2*matches - length."""
    limit = min(limit, len(old) - opos)
    s = best_s = best_len = i = 0
    while i < limit:
        size = min(CHUNK, limit - i)
        a = old[opos + i : opos + i + size]
        if a == new[npos + i : npos + i + size]:
            s, i = s + size, i + size
            if s * 2 - i > best_s * 2 - best_len:
                best_s, best_len = s, i
            continue
        for k in range(size):
            s += old[opos + i + k] == new[npos + i + k]
            if s * 2 - (i + k + 1) > best_s * 2 - best_len:
                best_s, best_len = s, i + k + 1
        i += size
    return best_len


def _backward(old: bytes, pos: int, new: bytes, scan: int, limit: int) -> int:
    """bsdiff's backward extension, capped at ``BACK`` bytes."""
    s = best_s = best_len = 0
    for i in range(1, min(limit, pos, BACK) + 1):
        s += old[pos - i] == new[scan - i]
        if s * 2 - i > best_s * 2 - best_len:
            best_s, best_len = s, i
    return best_len


def _sub(new: bytes, old: bytes) -> bytes:
    """``new - old`` per byte, modulo 256; equal chunks are zero."""
    out = bytearray(len(new))
    for start in range(0, len(new), CHUNK):
        a, b = old[start : start + CHUNK], new[start : start + CHUNK]
        if a != b:
            out[start : start + len(b)] = bytes(
                (y - x) & 0xFF for x, y in zip(a, b, strict=True)
            )
    return bytes(out)


def bsdiff40(old: bytes, new: bytes) -> bytes:
    """A BSDIFF40 patch from ``old`` to ``new``.

    This follows Colin Percival's bsdiff 4 scan: an exact match is taken when it
    beats continuing the current alignment by more than 8 bytes; each match is
    extended forward and backward approximately, and the gap between becomes
    extra bytes. Matches are found through an index of 8-byte strings (plus the
    current and the same-position alignments) instead of a suffix array, and
    the backward extension is capped; the output is a valid BSDIFF40 patch
    either way.
    """
    index = _Index(old)
    ctrl, diff, extra = bytearray(), bytearray(), bytearray()
    scan = length = pos = last_scan = last_pos = last_offset = 0
    while scan < len(new):
        old_score = 0
        scan += length
        scsc = scan
        while scan < len(new):
            length, pos = index.longest(new, scan, (scan + last_offset, scan))
            end = min(scan + length, len(old) - last_offset)
            if scsc < end:
                old_score += equal_count(
                    new[scsc:end], old[scsc + last_offset : end + last_offset]
                )
            scsc = max(scsc, scan + length)
            if (length == old_score and length != 0) or length > old_score + 8:
                break
            if scan + last_offset < len(old) and old[scan + last_offset] == new[scan]:
                old_score -= 1
            scan += 1
        if length == old_score and scan != len(new):
            continue
        lenf = _forward(old, last_pos, new, last_scan, scan - last_scan)
        lenb = 0
        if scan < len(new):
            lenb = _backward(old, pos, new, scan, scan - last_scan)
        if last_scan + lenf > scan - lenb:
            overlap = last_scan + lenf - (scan - lenb)
            s = best_s = lens = 0
            for i in range(overlap):
                s += (
                    new[last_scan + lenf - overlap + i]
                    == old[last_pos + lenf - overlap + i]
                )
                s -= new[scan - lenb + i] == old[pos - lenb + i]
                if s > best_s:
                    best_s, lens = s, i + 1
            lenf += lens - overlap
            lenb -= lens
        diff += _sub(new[last_scan : last_scan + lenf], old[last_pos : last_pos + lenf])
        extra += new[last_scan + lenf : scan - lenb]
        ctrl += offtout(lenf)
        ctrl += offtout(scan - lenb - (last_scan + lenf))
        ctrl += offtout(pos - lenb - (last_pos + lenf))
        last_scan, last_pos, last_offset = scan - lenb, pos - lenb, pos - scan
    parts = [bz2.compress(bytes(p), 9) for p in (ctrl, diff, extra)]
    header = BSDIFF_MAGIC + offtout(len(parts[0])) + offtout(len(parts[1]))
    return header + offtout(len(new)) + b"".join(parts)


def bspatch(old: bytes, patch: bytes) -> bytes:
    """Apply any BSDIFF40 patch (control triples of add, insert, seek)."""
    if patch[:8] != BSDIFF_MAGIC:
        raise ValueError("not a BSDIFF40 patch")
    ctrl_len, diff_len, size = (offtin(patch[8 + 8 * i : 16 + 8 * i]) for i in range(3))
    if min(ctrl_len, diff_len, size) < 0:
        raise ValueError("corrupt BSDIFF40 header")
    ctrl = bz2.decompress(patch[32 : 32 + ctrl_len])
    diff = bz2.decompress(patch[32 + ctrl_len : 32 + ctrl_len + diff_len])
    extra = bz2.decompress(patch[32 + ctrl_len + diff_len :])
    new = bytearray()
    old_pos = c = d = e = 0
    while len(new) < size:
        add, insert, seek = (offtin(ctrl[c + 8 * i : c + 8 * i + 8]) for i in range(3))
        c += 24
        if add < 0 or insert < 0 or len(new) + add + insert > size:
            raise ValueError("corrupt BSDIFF40 control")
        window = bytearray(add)
        lo, hi = max(old_pos, 0), min(old_pos + add, len(old))
        if lo < hi:
            window[lo - old_pos : hi - old_pos] = old[lo:hi]
        new += _add(bytes(window), diff[d : d + add], 1)
        d += add
        new += extra[e : e + insert]
        e += insert
        old_pos += add + seek
    return bytes(new)


@dataclass(frozen=True)
class FileChange:
    name: str
    lsn: int
    size: int
    old: bytes
    new: bytes


def disc_name(entry: Entry) -> str:
    """The patcher's name for an entry: no ``;1``, backslash separators."""
    return "\\".join(part.split(";")[0] for part in entry.path.split("/"))


def entries(path: Path) -> list[Entry]:
    with path.open("rb") as stream:
        track = Track(stream, path.stat().st_size)
        volume = primary_volume(track)
        lsn, size = int(str(volume["root_lsn"])), int(str(volume["root_size"]))
        return list(walk(track, lsn, size))


def changed_files(source: Path, built: Path) -> list[FileChange]:
    """Files whose sectors differ; every other sector must be identical."""
    listing = entries(source)
    if [(e.path, e.lsn, e.size_bytes, e.flags) for e in listing] != [
        (e.path, e.lsn, e.size_bytes, e.flags) for e in entries(built)
    ]:
        raise ValueError("the directory listings differ; an .ssp cannot move files")
    owner: dict[int, Entry] = {}
    for entry in listing:
        if not entry.is_dir:
            for i in range((entry.size_bytes + USER_DATA - 1) // USER_DATA):
                owner[entry.lsn + i] = entry
    touched: dict[str, Entry] = {}
    with source.open("rb") as a, built.open("rb") as b:
        lsn = 0
        while chunk_a := a.read(RAW_SECTOR * 512):
            chunk_b = b.read(len(chunk_a))
            for offset in range(0, len(chunk_a), RAW_SECTOR):
                if (
                    chunk_a[offset : offset + RAW_SECTOR]
                    != chunk_b[offset : offset + RAW_SECTOR]
                ):
                    owned = owner.get(lsn + offset // RAW_SECTOR)
                    if owned is None:
                        raise ValueError(
                            f"LSN {lsn + offset // RAW_SECTOR} differs outside any file"
                        )
                    touched[owned.path] = owned
            lsn += len(chunk_a) // RAW_SECTOR
        if b.read(1):
            raise ValueError("the tracks differ in length")
    changes = []
    with source.open("rb") as a, built.open("rb") as b:
        track_a = Track(a, source.stat().st_size)
        track_b = Track(b, built.stat().st_size)
        for entry in sorted(touched.values(), key=lambda e: e.lsn):
            if "/" in entry.path:
                raise ValueError(f"{entry.path}: only root files are supported")
            old = track_a.read(entry.lsn, entry.size_bytes)
            new = track_b.read(entry.lsn, entry.size_bytes)
            changes.append(
                FileChange(disc_name(entry), entry.lsn, entry.size_bytes, old, new)
            )
    return changes


def drive_order(listing: Sequence[Entry]) -> str:
    """``driveOrder.txt``: entries by extent, as the official patcher lists them.

    The XA mode is 0: the patcher derives it from extended attributes, which
    this disc's directory records do not have (EXP-0084).
    """
    ordered = sorted(listing, key=lambda e: e.lsn)
    return "".join(f"{disc_name(e)},{i},0\r\n" for i, e in enumerate(ordered))


def build_ssp(
    changes: Sequence[FileChange], listing: Sequence[Entry], meta: dict[str, str]
) -> bytes:
    """The .ssp bytes; identical inputs give identical bytes."""
    md5 = "".join(
        f"{c.name.upper()}:{hashlib.md5(c.old).hexdigest().upper()}\r\n"
        for c in changes
    )
    readme = "\r\n".join(
        [
            meta["Name"],
            f"Version {meta['Version']}",
            meta["Description"],
            "",
            "Apply to an untouched Redump image of Marvel Super Heroes vs.",
            "Street Fighter (Japan). Source and instructions:",
            meta["URL"],
            "",
        ]
    )
    members = [(f"{c.name.upper()}._DFR", bsdiff40(c.old, c.new)) for c in changes]
    members += [
        ("version.txt", f"{SSP_VERSION}\r\n".encode("ascii")),
        ("readme.txt", readme.encode("ascii")),
        ("driveOrder.txt", drive_order(listing).encode("ascii")),
        ("changes.md5", md5.encode("ascii")),
        ("meta.txt", "".join(f"{k}:{meta[k]}\r\n" for k in META_KEYS).encode("ascii")),
    ]
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, data in members:
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            archive.writestr(info, data, compresslevel=9)
    return out.getvalue()


def read_ssp(ssp: bytes) -> tuple[dict[str, str], dict[str, bytes]]:
    """(``changes.md5`` by name, ``._DFR`` patch by name)."""
    with zipfile.ZipFile(io.BytesIO(ssp)) as archive:
        names = archive.namelist()
        if "version.txt" not in names or "driveOrder.txt" not in names:
            raise ValueError("not an .ssp: version.txt or driveOrder.txt is missing")
        md5 = {}
        for line in archive.read("changes.md5").decode("ascii").splitlines():
            if line.strip():
                name, digest = line.split(":")
                md5[name.strip()] = digest.strip().upper()
        patches = {
            n.removesuffix("._DFR"): archive.read(n)
            for n in names
            if n.endswith("._DFR")
        }
    return md5, patches


def apply_ssp(ssp: bytes, source: Path, target: Path) -> list[str]:
    """Write ``target``: ``source`` with every ``._DFR`` applied in place."""
    md5, patches = read_ssp(ssp)
    files = {disc_name(e): e for e in entries(source) if not e.is_dir}
    replacements = []
    with source.open("rb") as stream:
        track = Track(stream, source.stat().st_size)
        for name, patch in sorted(patches.items()):
            entry = files[name]
            old = track.read(entry.lsn, entry.size_bytes)
            if hashlib.md5(old).hexdigest().upper() != md5[name]:
                raise ValueError(f"{name}: the source file's MD5 does not match")
            new = bspatch(old, patch)
            if len(new) != len(old):
                raise ValueError(f"{name}: the patch changes the file size")
            replacements.append((entry.lsn, entry.size_bytes, new))
    replace_files(source, target, replacements)
    return sorted(patches)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--built-dir", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--manifest", type=Path, default=SOURCE_MANIFEST)
    parser.add_argument("--reference", help="regression reference the build must match")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--stem", required=True, help="patch filename stem")
    parser.add_argument("--release-version", required=True, help="e.g. 0.1.0")
    parser.add_argument("--description", default="", help="one line for meta.txt")
    parser.add_argument("--out-dir", type=Path, default=Path("build/release"))
    parser.add_argument("--record", type=Path, help="also write the JSON record here")
    args = parser.parse_args(argv)

    out_dir = args.out_dir.resolve()
    build_root = (REPO_ROOT / "build").resolve()
    if build_root not in out_dir.parents and out_dir != build_root:
        parser.error(f"output must be under {build_root}")
    source, built = components(args.source_dir), components(args.built_dir)
    known = load_manifest_hashes(args.manifest)
    unknown = [n for n, p in source.items() if sha256_file(p) not in known]
    if unknown:
        parser.error(f"source components not in the manifest: {unknown}")
    differing, _ = compare_images(source, built)
    if differing != [TRACK01]:
        parser.error(f"an .ssp patches track 01 only; differing: {differing}")
    target_sha256 = sha256_file(built[TRACK01])
    if args.reference and target_sha256 != reference_track01(
        args.baseline, args.reference
    ):
        parser.error(f"built track 01 does not match reference {args.reference}")

    meta = {
        "Name": TITLE,
        "Author": AUTHOR,
        "URL": URL,
        "Version": args.release_version,
        "Description": args.description,
        "Contact": URL + "/issues",
    }
    changes = changed_files(source[TRACK01], built[TRACK01])
    listing = entries(source[TRACK01])
    ssp = build_ssp(changes, listing, meta)
    deterministic = ssp == build_ssp(changes, listing, meta)
    out_dir.mkdir(parents=True, exist_ok=True)
    patch = out_dir / f"{args.stem}.ssp"
    patch.write_bytes(ssp)
    check = out_dir / f"{args.stem}.ssp.applied.bin"
    apply_ssp(ssp, source[TRACK01], check)
    round_trip = sha256_file(check) == target_sha256
    check.unlink()
    if not (deterministic and round_trip):
        parser.error(f"{patch.name}: {deterministic=} {round_trip=}")
    with zipfile.ZipFile(io.BytesIO(ssp)) as archive:
        sizes = {i.filename: i.compress_size for i in archive.infolist()}
    record = {
        "tool": "tools.disc.make_ssp",
        "reference": args.reference,
        "ssp_version": SSP_VERSION,
        "patch": patch.name,
        "patch_size": len(ssp),
        "patch_sha256": hashlib.sha256(ssp).hexdigest(),
        "component": TRACK01,
        "source_sha256": sha256_file(source[TRACK01]),
        "target_sha256": target_sha256,
        "deterministic": deterministic,
        "round_trip": round_trip,
        "files": [
            {
                "name": c.name,
                "lsn": c.lsn,
                "size": c.size,
                "source_md5": hashlib.md5(c.old).hexdigest(),
                "target_sha256": hashlib.sha256(c.new).hexdigest(),
                "dfr_stored_size": sizes[f"{c.name.upper()}._DFR"],
            }
            for c in changes
        ],
    }
    text = json.dumps(record, indent=1) + "\n"
    (out_dir / f"{args.stem}.ssp.json").write_text(text)
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(text)
    print(json.dumps({k: record[k] for k in ("patch", "patch_size", "round_trip")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
