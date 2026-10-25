"""Make and verify an xdelta3 (VCDIFF) release patch for a built image (REL-001).

The patch turns the untouched source image into a built image. Every component
that differs gets its own patch; components that are byte-identical (normally all
audio tracks and the CUE sheet) are listed as unchanged and need no patch.

Safety and reproducibility:

- Source components are only read, and their SHA-256 must appear in the tracked
  source manifest (``references/mshvsf/saturn_jp/README.md``).
- With ``--reference``, the built track 01 must equal that regression reference's
  recorded hash (``data/regression/reference_builds.json``).
- Patches are written under ``build/`` (git-ignored): their bytes include
  game-derived data, which is never committed (``AGENTS.md`` rule 21).
- xdelta3 runs with fixed flags (``XDELTA_ENCODE``): no secondary compressor, so
  any VCDIFF patcher can apply it, and no application header, so no local file
  names are stored. Each patch is encoded twice and must be byte-identical, then
  decoded with ``xdelta3 -d`` and compared with the built component.
- The JSON record (hashes, sizes, xdelta3 version, flags) is metadata only and
  may be committed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from tools.disc.patch_image import REPO_ROOT, load_manifest_hashes, sha256_file

XDELTA_ENCODE = ("-e", "-9", "-S", "none", "-A", "-f")
SOURCE_DIR = Path("local/disc_images/mshvsf_saturn_jp")
SOURCE_MANIFEST = Path("references/mshvsf/saturn_jp/README.md")
BASELINE = Path("data/regression/reference_builds.json")
TRACK01 = "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"


def components(directory: Path) -> dict[str, Path]:
    """Image components (BIN and CUE files) by name."""
    return {
        p.name: p
        for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix.lower() in (".bin", ".cue")
    }


def compare_images(
    source: dict[str, Path], built: dict[str, Path]
) -> tuple[list[str], list[str]]:
    """(differing, unchanged) component names; the name sets must match."""
    if set(source) != set(built):
        raise ValueError(f"component names differ: {sorted(set(source) ^ set(built))}")
    differing: list[str] = []
    unchanged: list[str] = []
    for name in sorted(source):
        same = sha256_file(source[name]) == sha256_file(built[name])
        (unchanged if same else differing).append(name)
    return differing, unchanged


def patch_name(stem: str, component: str) -> str:
    """Patch filename: the release stem plus the component's track label."""
    track = re.search(r"\((Track \d+)\)", component)
    label = track.group(1).replace(" ", "") if track else Path(component).stem
    return f"{stem}.{label}.xdelta"


def xdelta_version(xdelta: str) -> str:
    result = subprocess.run([xdelta, "-V"], capture_output=True, text=True)
    match = re.search(r"Xdelta version (\S+)", result.stdout + result.stderr)
    if not match:
        raise RuntimeError("cannot read the xdelta3 version")
    return match.group(1).rstrip(",")


def encode(xdelta: str, source: Path, target: Path, out: Path) -> None:
    subprocess.run(
        [xdelta, *XDELTA_ENCODE, "-s", str(source), str(target), str(out)],
        check=True,
    )


def decode(xdelta: str, source: Path, patch: Path, out: Path) -> None:
    subprocess.run(
        [xdelta, "-d", "-f", "-s", str(source), str(patch), str(out)], check=True
    )


def reference_track01(baseline: Path, name: str) -> str:
    references = json.loads(baseline.read_text())["references"]
    for reference in references:
        if reference["name"] == name:
            return str(reference["track01_sha256"])
    raise ValueError(f"no regression reference named {name!r}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--built-dir", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--manifest", type=Path, default=SOURCE_MANIFEST)
    parser.add_argument("--reference", help="regression reference the build must match")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--stem", required=True, help="patch filename stem")
    parser.add_argument("--out-dir", type=Path, default=Path("build/release"))
    parser.add_argument("--record", type=Path, help="also write the JSON record here")
    parser.add_argument("--xdelta", default="xdelta3")
    args = parser.parse_args(argv)

    out_dir = args.out_dir.resolve()
    build_root = (REPO_ROOT / "build").resolve()
    if build_root not in out_dir.parents and out_dir != build_root:
        parser.error(f"output must be under {build_root}")
    xdelta = shutil.which(args.xdelta)
    if xdelta is None:
        parser.error(f"{args.xdelta} not found; install xdelta3")

    source, built = components(args.source_dir), components(args.built_dir)
    known = load_manifest_hashes(args.manifest)
    unknown = [n for n, p in source.items() if sha256_file(p) not in known]
    if unknown:
        parser.error(f"source components not in the manifest: {unknown}")
    differing, unchanged = compare_images(source, built)
    if any(not n.lower().endswith(".bin") for n in differing):
        parser.error(f"only BIN tracks may differ: {differing}")
    if args.reference:
        expected = reference_track01(args.baseline, args.reference)
        if sha256_file(built[TRACK01]) != expected:
            parser.error(f"built track 01 does not match reference {args.reference}")

    out_dir.mkdir(parents=True, exist_ok=True)
    patches = []
    for name in differing:
        patch = out_dir / patch_name(args.stem, name)
        again = out_dir / (patch.name + ".again")
        check = out_dir / (patch.name + ".decoded")
        encode(xdelta, source[name], built[name], patch)
        encode(xdelta, source[name], built[name], again)
        deterministic = patch.read_bytes() == again.read_bytes()
        again.unlink()
        decode(xdelta, source[name], patch, check)
        round_trip = sha256_file(check) == sha256_file(built[name])
        check.unlink()
        if not (deterministic and round_trip):
            parser.error(f"{patch.name}: {deterministic=} {round_trip=}")
        patches.append(
            {
                "component": name,
                "patch": patch.name,
                "patch_size": patch.stat().st_size,
                "patch_sha256": sha256_file(patch),
                "source_size": source[name].stat().st_size,
                "source_sha256": sha256_file(source[name]),
                "target_sha256": sha256_file(built[name]),
                "deterministic": deterministic,
                "round_trip": round_trip,
            }
        )
    record = {
        "tool": "tools.disc.make_patch",
        "reference": args.reference,
        "xdelta3_version": xdelta_version(xdelta),
        "xdelta3_encode_flags": " ".join(XDELTA_ENCODE),
        "patches": patches,
        "unchanged_components": [
            {"component": n, "sha256": sha256_file(source[n])} for n in unchanged
        ],
    }
    text = json.dumps(record, indent=1) + "\n"
    (out_dir / f"{args.stem}.json").write_text(text)
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(text)
    print(
        json.dumps(
            [{k: p[k] for k in ("patch", "patch_size", "round_trip")} for p in patches]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
