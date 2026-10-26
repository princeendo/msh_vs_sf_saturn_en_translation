"""Generate a caption spec for one ending from the official arcade English (END-010).

The policy (user decision, 2026-10-24, `data/translations/README.md`):

- the point character's three ending pages get the official English pages
  (English page table ``0x20C1B4``, `EXP-0042`), in ``ME.PAC``;
- the post-boss dialogue gets the arcade's two English partner lines
  (``0x22226C``): record ``p`` for each listed partner ``p`` and record
  ``26 + point`` for the point character (`EXP-0043`). Each English line fills
  its ``MC13`` pair (``16 + 2 * index``). With the default ``whole`` layout,
  both boxes hold the full two-line text: the box never closes between the two
  records, so it reads as one block lasting both boxes' time (`EXP-0045`, user
  request). ``split`` puts one half per box at the line break (`EXP-0044`);
- the inserted names (``0000``) come from the ``MM.BIN`` name table, set to the
  arcade's English names for the point character and the listed partners. The
  game inserts a fixed number of cells per name from a one-byte length table
  (``MM.BIN`` ``0x96DE8``, `EXP-0044`), so those entries are set to the English
  names' cell counts.

``--names`` selects the name variant (`LOC-003`, ``NAME_VARIANTS``):

- ``saturn`` (default): the Japanese release's names (Vega, Gouki,
  Mech-Gouki) in the English text, as the art and voice say them;
- ``us``: the arcade's American names (Bison, Akuma, Cyber Akuma) in the text,
  and the voice switched to the American name calls already on the disc
  (`EXP-0058`). The name art is unchanged (`LOC-004`).

With ``--roster`` (`END-023`), every roster slot is both a point character and a
partner, and ``--with-win-quotes`` adds the M5 win-quote tables
(``official_captions.roster_spec``), giving one combined spec for one font.

Before writing anything, every Saturn record to be replaced is checked against
the arcade Japanese record it pairs with (byte-identical, `EXP-0042`). The text is
read from the local arcade ROM at build time and written to an ignored path.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from tools.disc.iso9660 import Track
from tools.disc.pac_lzss import decode_file
from tools.disc.patch_image import find_entry
from tools.reference.arcade_endings import (
    PAGE_TABLES,
    PARTNER_LINES,
    PARTNER_RECORD,
    SLOTS,
    latin,
    page_span,
)
from tools.reference.cps2_text import build_program, read_quote_table
from tools.reference.mame_audit import parse_driver
from tools.text.caption_compiler import LINE_CELLS, RECORD, SCHEMA_V3, TOKEN
from tools.text.official_captions import best_shifts, centred, roster_spec
from tools.text.pair_font import split_pairs

EN_RECORD, EN_CELLS = 100, 25  # arcade English records: 2 lines of 25 cells
ARCADE_DIALOGUE = 0x217BE0  # Japanese dialogue block = MC13 records 16-119
MC13_TABLE, DIALOGUE_FIRST = 0xA06C, 16  # EXP-0034, EXP-0043
ME_BASE = 0x211D58  # ME.PAC file offset = arcade Japanese page address - this
ARCADE_NAMES, NAME_BYTES = 0x2236BC, 32  # English names, 16 cells per slot
MM_NAMES, NAME_LEAD = 0x7D3C0, 2  # MM.BIN name table; two leading blank cells
MM_NAME_LENGTHS = 0x96DE8  # MM.BIN: one byte per slot, cells inserted per name
NAME_GUESS = 2  # cells assumed for an inserted name when centring a line
WIN_QUOTES_EN = 0x20C014  # arcade English win-quote table (EXP-0029)
# User decisions (2026-10-25, END-024, END-026): the Saturn is the Japanese
# release, whose art and voice say Vega, Gouki, and Mech-Gouki, so the English
# text follows it instead of the US arcade's BISON, AKUMA, and Cyber Akuma.
# Provisional: the art and audio are not changed (`LOC-001`).
NAME_OVERRIDES = {14: "VEGA", 15: "GOUKI"}
# FONT-011 (EXP-0052): the message-window initialiser in MM.BIN stores each caption
# kind's palette as an immediate (``mov #imm,r1`` at these offsets), and the gold
# credits palette is bank 1. Offset: (original, gold); bit 7 is kept.
GOLD_PALETTE_PATCHES = {
    0x961E3: (0x9E, 0x81),  # win quotes (palette 0x1E)
    0x961FB: (0x9F, 0x81),  # ending pages (palette 0x1F)
    0x96233: (0x83, 0x81),  # post-boss dialogue (palette 0x03)
}
# UI-001/UI-002 (EXP-0053): Japanese UI art cells in the quote font, replaced by
# the game's own English arcade art (None = empty cell).
UI_GLYPH_COPIES: dict[int, int | None] = {
    # Player-2 prompt "対戦者求む!" (5 cells) -> " JOIN IN" (user choice).
    0x45B: None,
    0x45C: 0x496,
    0x45D: 0x497,
    0x45E: 0x498,
    0x45F: 0x499,
}
# Mode panel "簡単操作" (4 cells, four shading copies) -> centred "EASY" (2 cells),
# matched by shading: 0x424/0x6A6, 0x428/0x6A8, 0x42C/0x6AA, 0x43A/0x6AC.
for _jp, _en in ((0x424, 0x6A6), (0x428, 0x6A8), (0x42C, 0x6AA), (0x43A, 0x6AC)):
    UI_GLYPH_COPIES |= {_jp: None, _jp + 1: _en, _jp + 2: _en + 1, _jp + 3: None}
# Applied in order, so "Cyber Akuma" is replaced before "Akuma".
TEXT_OVERRIDES = {"Cyber Akuma": "Mech-Gouki", "Akuma": "Gouki"}
# LOC-005 (EXP-0058): MEMFIX.PAC payload 7 is loaded into sound RAM and holds two
# name-call tables of sound IDs indexed by character: table A (10-byte records,
# file 0x124A5E; it chooses the win-screen call) and table B (16-byte records,
# file 0x124B54; use unknown). Entries 20-22 hold the American calls; the US
# variant copies them into 14 (Vega), 15 (Gouki), and 19 (Mech-Gouki).
# Offset: (Japanese call, American call), big-endian u16.
US_VOICE_PATCHES = {
    0x124AEA: (0x0286, 0x004F),  # table A 14: "Vega" -> "Bison"
    0x124AF4: (0x0048, 0x0338),  # table A 15: "Gouki" -> "Akuma"
    0x124B1C: (0x0082, 0x005B),  # table A 19: "Mech Gouki" -> "Cyber Akuma"
    0x124C34: (0x0286, 0x004F),  # table B 14
    0x124C44: (0x0048, 0x0338),  # table B 15
    0x124C84: (0x0082, 0x005B),  # table B 19
}


# LOC-004 (EXP-0060): the life-bar name labels are quote-font cells, and the font
# already holds the US art. The fight HUD draws bold VEGA 0x760-0x762, GOUKI
# 0x750-0x752, and MECH-GOUKI 0x568-0x56D; the US variant copies BISON
# (0x763-0x765), AKUMA (0x753-0x755), and CYBER-AKUMA (0x5D9-0x5DE) over them.
# AKUMA is 50 px wide and the GOUKI sprite 48 px, so its last 2 px are clipped.
US_LABEL_COPIES = {
    **{0x760 + i: 0x763 + i for i in range(3)},
    **{0x750 + i: 0x753 + i for i in range(3)},
    **{0x568 + i: 0x5D9 + i for i in range(6)},
}
# Ending speaker labels: 16-character ASCII fields in ME.PAC, one per character
# index (EXP-0054). Index: (Saturn text, US text).
SPEAKER_FIELDS, SPEAKER_FIELD = 0xB164, 16
US_SPEAKERS = {
    14: ("Vega", "Bison"),
    15: ("Gouki", "Akuma"),
    19: ("Mech-Gouki", "Cyber Akuma"),
}


@dataclass(frozen=True)
class NameVariant:
    """Name handling for one build variant (LOC-003, LOC-004)."""

    names: Mapping[int, str] = field(default_factory=dict)
    text: Mapping[str, str] = field(default_factory=dict)
    voice: Mapping[int, tuple[int, int]] = field(default_factory=dict)
    glyphs: Mapping[int, int] = field(default_factory=dict)
    speakers: Mapping[int, tuple[str, str]] = field(default_factory=dict)


NAME_VARIANTS = {
    "saturn": NameVariant(NAME_OVERRIDES, TEXT_OVERRIDES),
    "us": NameVariant(
        voice=US_VOICE_PATCHES, glyphs=US_LABEL_COPIES, speakers=US_SPEAKERS
    ),
}


def localize(line: str, variant: str = "saturn") -> str:
    """Apply the variant's text overrides to one line of English or a win quote."""
    for old, new in NAME_VARIANTS[variant].text.items():
        line = line.replace(old, new)
    return line


def en_lines(program: bytes, address: int, variant: str = "saturn") -> list[str]:
    """The two lines of an arcade English record, stripped and localized."""
    text = latin(program, address, EN_RECORD)
    return [
        localize(text[:EN_CELLS].strip(), variant),
        localize(text[EN_CELLS:].strip(), variant),
    ]


def speaker_patches(variant: str) -> list[dict[str, str]]:
    """Spec ``patches`` entries for the variant's ME.PAC speaker-label fields."""

    def field_hex(text: str) -> str:
        if len(text) > SPEAKER_FIELD:
            raise ValueError(f"{text!r} is longer than {SPEAKER_FIELD} characters")
        return text.ljust(SPEAKER_FIELD).encode("ascii").hex()

    return [
        {
            "file": "ME.PAC",
            "offset": f"0x{SPEAKER_FIELDS + SPEAKER_FIELD * index:X}",
            "hex": field_hex(new),
            "expect": field_hex(old),
        }
        for index, (old, new) in sorted(NAME_VARIANTS[variant].speakers.items())
    ]


def voice_patches(variant: str) -> list[dict[str, str]]:
    """Spec ``patches`` entries for the variant's name-call edits (with expect)."""
    return [
        {
            "file": "MEMFIX.PAC",
            "offset": f"0x{offset:X}",
            "hex": f"{new:04x}",
            "expect": f"{old:04x}",
        }
        for offset, (old, new) in sorted(NAME_VARIANTS[variant].voice.items())
    ]


def box_line(text: str) -> str:
    """Centre one dialogue half in whole cells; ``{0000}`` becomes ``{P}``."""
    text = text.replace("{0000}", TOKEN)
    segments = text.split(TOKEN)
    used = sum(len(split_pairs(s)) for s in segments if s)
    used += NAME_GUESS * (len(segments) - 1)
    if used > LINE_CELLS:
        raise ValueError(f"{text!r} needs {used} cells (max {LINE_CELLS})")
    return "  " * ((LINE_CELLS - used) // 2) + text


def name_text(name: str) -> str:
    """Odd-length names get a leading half space, so they end on a cell edge."""
    return name if len(name) % 2 == 0 else " " + name


def ending_spec(
    program: bytes,
    point: int | Sequence[int],
    partners: Sequence[int],
    layout: str = "whole",
    variant: str = "saturn",
) -> tuple[dict[str, object], dict[str, list[int]]]:
    """The v3 spec, and the arcade Japanese records it replaces.

    ``point`` may list several point characters (`END-020`): each gets its pages
    and its point pair; the partner pairs are shared.
    """
    points = [point] if isinstance(point, int) else list(point)
    page_tables, pages_ja = [], []
    for slot in points:
        start, end = page_span(program, PAGE_TABLES["en"], slot)
        pages = [en_lines(program, a, variant) for a in range(start, end, EN_RECORD)]
        shifts = best_shifts([line for page in pages for line in page if line])
        jp_start, jp_end = page_span(program, PAGE_TABLES["ja"], slot)
        if (jp_end - jp_start) // RECORD != len(pages):
            raise ValueError(f"slot {slot}: Japanese and English page counts differ")
        pages_ja += [jp_start, len(pages)]
        page_tables.append(
            {
                "file": "ME.PAC",
                "format": "raw",
                "table": f"0x{jp_start - ME_BASE:X}",
                "records": [
                    {
                        "record": k,
                        "lines": [centred(x, shift=shifts.get(x, 0)) for x in page],
                    }
                    for k, page in enumerate(pages)
                ],
            }
        )
    dialogue = []
    for index in [*partners, *(SLOTS + slot for slot in points)]:
        halves = en_lines(program, PARTNER_LINES + PARTNER_RECORD * index, variant)
        first = DIALOGUE_FIRST + 2 * index
        if layout == "whole":
            lines = [box_line(half) for half in halves]
            boxes = [lines, lines]
        else:
            boxes = [[box_line(half), ""] for half in halves]
        for offset, box in enumerate(boxes):
            dialogue.append({"record": first + offset, "lines": box})
    names, lengths = [], []
    for slot in sorted({*points, *partners}):
        address = ARCADE_NAMES + NAME_BYTES * slot
        override = NAME_VARIANTS[variant].names.get(slot)
        name = override or latin(program, address, NAME_BYTES).strip()
        cells = len(split_pairs(name_text(name)))
        lengths.append(
            {
                "file": "MM.BIN",
                "offset": f"0x{MM_NAME_LENGTHS + slot:X}",
                "hex": f"{cells:02x}",
            }
        )
        names.append(
            {
                "file": "MM.BIN",
                "offset": f"0x{MM_NAMES + NAME_BYTES * slot + 2 * NAME_LEAD:X}",
                "cells": NAME_BYTES // 2 - NAME_LEAD,
                "text": name_text(name),
            }
        )
    spec: dict[str, object] = {
        "schema": SCHEMA_V3,
        "description": (
            f"END-010 official arcade English ending: point slot "
            f"{points[0] if len(points) == 1 else points}, partners "
            f"{list(partners)}, dialogue layout {layout}. Generated from the local "
            "arcade ROM; not committed."
        ),
        "tables": [
            {
                "file": "MC13.PAC",
                "table": f"0x{MC13_TABLE:X}",
                "placeholder": "anywhere",
                "records": dialogue,
            },
            *page_tables,
        ],
        "fields": names,
        "patches": lengths,
    }
    targets: dict[str, list[int]] = {
        "pages_ja": pages_ja,  # start, count for each point character
        "dialogue_records": [int(str(r["record"])) for r in dialogue],
        "dialogue_ja": [
            ARCADE_DIALOGUE + RECORD * (int(str(r["record"])) - DIALOGUE_FIRST)
            for r in dialogue
        ],
    }
    return spec, targets


def check_targets(
    program: bytes, targets: dict[str, list[int]], mc13: bytes, me: bytes
) -> dict[str, bool]:
    """Every replaced Saturn record must equal its arcade Japanese record."""
    spans = targets["pages_ja"]
    pages_ok = all(
        program[start + RECORD * k : start + RECORD * (k + 1)]
        == me[start - ME_BASE + RECORD * k : start - ME_BASE + RECORD * (k + 1)]
        for start, count in zip(spans[::2], spans[1::2], strict=True)
        for k in range(count)
    )
    decoded = decode_file(mc13)[1]
    dialogue_ok = all(
        program[a : a + RECORD]
        == decoded[MC13_TABLE + RECORD * r : MC13_TABLE + RECORD * (r + 1)]
        for a, r in zip(
            targets["dialogue_ja"], targets["dialogue_records"], strict=True
        )
    )
    if not (pages_ok and dialogue_ok):
        raise ValueError(
            f"Saturn records differ from arcade: {pages_ok=} {dialogue_ok=}"
        )
    return {"pages_equal_arcade_ja": pages_ok, "dialogue_equal_arcade_ja": dialogue_ok}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--archive", type=Path, required=True, help="arcade ROM zip")
    parser.add_argument("--set", dest="set_name", default="", help="default: zip stem")
    parser.add_argument(
        "--point", type=int, nargs="+", default=[9], help="slot(s) (Ryu = 9)"
    )
    parser.add_argument("--partners", type=int, nargs="+", default=[10, 15])
    parser.add_argument(
        "--dialogue-layout", choices=("whole", "split"), default="whole"
    )
    parser.add_argument(
        "--roster", type=Path, help="roster JSON: every slot as point and partner"
    )
    parser.add_argument(
        "--with-win-quotes", action="store_true", help="add the roster win quotes"
    )
    parser.add_argument(
        "--caption-palette",
        choices=("silver", "gold"),
        default="silver",
        help="gold switches the captions to the credits' gold bank (FONT-011)",
    )
    parser.add_argument(
        "--ui-english",
        action="store_true",
        help="replace Japanese UI art cells with English art (UI-001, UI-002)",
    )
    parser.add_argument(
        "--glyph-style",
        choices=("quote", "credits"),
        default="quote",
        help="pair glyphs from the quote font or the staff-credits font (FONT-011)",
    )
    parser.add_argument(
        "--names",
        choices=sorted(NAME_VARIANTS),
        default="saturn",
        help="Saturn (Japanese-release) or American names (LOC-003)",
    )
    parser.add_argument(
        "--track",
        type=Path,
        default=Path(
            "local/disc_images/mshvsf_saturn_jp/"
            "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
        ),
    )
    parser.add_argument("--out", type=Path, required=True, help="spec path (ignored)")
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    roster = json.loads(args.roster.read_text())["characters"] if args.roster else []
    points = [int(c["slot"]) for c in roster] or args.point
    partners = [int(c["slot"]) for c in roster] or args.partners
    spec, targets = ending_spec(
        program, points, partners, args.dialogue_layout, args.names
    )
    if args.with_win_quotes:
        if not roster:
            parser.error("--with-win-quotes needs --roster")
        quotes = [
            [[localize(line, args.names) for line in quote] for quote in s.quotes]
            for s in read_quote_table(program, WIN_QUOTES_EN, SLOTS)
        ]
        tables = spec["tables"]
        assert isinstance(tables, list)
        win_quote_tables = roster_spec(quotes, roster)["tables"]
        assert isinstance(win_quote_tables, list)
        spec["tables"] = win_quote_tables + tables
        spec["description"] = (
            "END-023 combined roster image: M5 official English win quotes (RE-044) "
            "and the roster's official English endings, dialogue layout "
            f"{args.dialogue_layout}. Generated from the local arcade ROM; not "
            "committed."
        )
    if args.glyph_style != "quote":
        spec["glyph_style"] = args.glyph_style
    if args.ui_english:
        spec["glyph_copies"] = {
            f"0x{t:03X}": None if s is None else f"0x{s:03X}"
            for t, s in sorted(UI_GLYPH_COPIES.items())
        }
    if args.caption_palette == "gold":
        patches = spec["patches"]
        assert isinstance(patches, list)
        patches += [
            {
                "file": "MM.BIN",
                "offset": f"0x{offset:X}",
                "hex": f"{new:02x}",
                "expect": f"{old:02x}",
            }
            for offset, (old, new) in GOLD_PALETTE_PATCHES.items()
        ]
    if args.names != "saturn":
        spec["names"] = args.names
        patches = spec["patches"]
        assert isinstance(patches, list)
        patches += voice_patches(args.names) + speaker_patches(args.names)
        copies = spec.get("glyph_copies") or {}
        assert isinstance(copies, dict)
        copies |= {
            f"0x{t:03X}": f"0x{s:03X}"
            for t, s in NAME_VARIANTS[args.names].glyphs.items()
        }
        spec["glyph_copies"] = dict(sorted(copies.items()))
    with args.track.open("rb") as stream:
        disc = Track(stream, args.track.stat().st_size)
        files = {
            name: disc.read(*find_entry(args.track, f"{name};1"))
            for name in ("MC13.PAC", "ME.PAC")
        }
    checks = check_targets(program, targets, files["MC13.PAC"], files["ME.PAC"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
