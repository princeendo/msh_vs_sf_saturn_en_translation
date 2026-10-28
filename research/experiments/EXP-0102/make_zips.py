"""REL-004: zip every xdelta variant and every SSP variant, each with a readme.

Reads the committed release records for hashes and the built patches from
build/release/. Zip members get a fixed timestamp, so the zips are reproducible.
"""

import json
import sys
import zipfile
from pathlib import Path

VERSION = sys.argv[1]
OUT = Path(sys.argv[2])
VARIANTS = (  # (record stem, build dir, label), default first
    (
        "m8_roster_gold_us",
        "m8_gold_us",
        "American names (default): Bison, Akuma, Cyber Akuma",
    ),
    ("m8_roster_gold", "m8_gold", "Saturn names: Vega, Gouki, Mech-Gouki"),
)
TRACK = "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
REPO = "https://github.com/princeendo/msh_vs_sf_saturn_en_translation"
STAMP = (2026, 10, 28, 0, 0, 0)
APPLY = {
    "xdelta": [
        f'xdelta3 -d -s "{TRACK}" \\',
        '  <patch>.Track01.xdelta "Track 01 patched.bin"',
    ],
    "ssp": [
        'saturn-patcher <patch>.ssp "Track 01 patched.bin"',
        "(saturn-patcher-egui). The official Sega Saturn Patcher rebuilds the",
        "disc instead: its track 01 differs only in the disc-length field.",
    ],
}


def add(bundle: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, STAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    bundle.writestr(info, data)


def readme(kind: str, rows: list[str], source: str) -> str:
    return "\n".join(
        [
            f"Marvel Super Heroes vs. Street Fighter (Saturn) English {VERSION}",
            f"({kind} patches)",
            "",
            'For the Japanese Saturn image "Marvel Super Heroes vs. Street Fighter',
            '(Japan)". Only track 01 changes; keep tracks 02-12 and the CUE sheet.',
            "",
            "Untouched track 01 SHA-256:",
            f"  {source}",
            "",
            *rows,
            "Apply:",
            *(f"  {line}" for line in APPLY[kind]),
            "Then put the patched file in place of track 01, under the same name.",
            "",
            "Full instructions, the change list and known limits:",
            f"  {REPO}/blob/main/release/README.md",
            "",
        ]
    )


OUT.mkdir(parents=True, exist_ok=True)
for kind in ("xdelta", "ssp"):
    rows, files, sources = [], [], set()
    for stem, build, label in VARIANTS:
        suffix = ".ssp.json" if kind == "ssp" else ".json"
        record = json.loads(Path(f"release/{stem}{suffix}").read_text())
        patch = record["patches"][0] if kind == "xdelta" else record
        sources.add(patch["source_sha256"])
        path = Path("build/release", build, patch["patch"])
        assert path.stat().st_size == patch["patch_size"], path
        rows += [
            label,
            f"  {patch['patch']} ({patch['patch_size']:,} bytes)",
            f"  file SHA-256:     {patch['patch_sha256']}",
            f"  patched track 01: {patch['target_sha256']}",
            "",
        ]
        files.append(path)
    assert len(sources) == 1
    name = OUT / f"mshvsf_saturn_en_{VERSION}_{kind}.zip"
    with zipfile.ZipFile(name, "w") as bundle:
        add(bundle, "README.txt", readme(kind, rows, sources.pop()).encode())
        for path in files:
            add(bundle, path.name, path.read_bytes())
    print(name)
