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
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from tools.disc.attract_captions import FILES, st2_patches
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
from tools.text.caption_compiler import (
    FONT_ENTRY,
    LINE_CELLS,
    RECORD,
    SCHEMA_V3,
    TOKEN,
)
from tools.text.official_captions import (
    best_shifts,
    centred,
    line_pairs,
    roster_spec,
)
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
# OPT-001 (EXP-0075): the boot initialiser in MM.BIN clears the boss-fight unlock
# word 0x06017AB0 (``mov #0,r0`` at 0x0601DBE4); the title menu forces its
# "MECH-GOUKI NOW!!" entry back to SURVIVAL MODE while the word is 0. ``mov #1,r0``
# starts the game unlocked, as a Survival clear does (0x06098A1A sets it to 1).
UNLOCK_BOSS_PATCH = {
    "file": "MM.BIN",
    "offset": "0x50E4",
    "hex": "e001",
    "expect": "e000",
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
# Applied in order, so "Cyber Akuma" is replaced before "Akuma". "Bison" first
# appears in Apocalypse's pre-fight exchanges (SPECIAL-004).
TEXT_OVERRIDES = {"Cyber Akuma": "Mech-Gouki", "Akuma": "Gouki", "Bison": "Vega"}
# SPECIAL-004 (EXP-0082): Apocalypse's pre-fight exchanges. MC00.PAC holds three
# 76-byte boxes per roster slot (the challenger's line, Apocalypse's reply, his
# closing line), equal to the arcade Japanese block; the US arcade's English has
# the same layout in 100-byte boxes.
EXCHANGES_MC00, EXCHANGES_JA, EXCHANGES_EN = 0x3634, 0x2164B8, 0x2203F4
EXCHANGE_BOXES = 3
# The US arcade's only use of code 0x011E ("taking you down{011E} piece by
# piece!") has no known glyph; the Spanish block has a comma there (EXP-0082).
EXCHANGE_CODE_TEXT = {"{011e}": ","}
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


# LOC-004 (EXP-0065): the life-bar name labels are MM.BIN records of 8 sprite
# patterns (0x5000 + quote-font code; 0x5020 is blank), indexed by character:
# player 1 at 0x32CA4 + 16 * index (bold, left-aligned), player 2 at
# 0x32E74 + 16 * index (italic, right-aligned). Records 26-28 are the US labels
# (AKUMA is 4 cells wide); the US variant copies them over 15, 14, and 19.
# Offset: (Saturn record, US record) as hex.
US_LABEL_RECORDS = {
    # P1 14 <- 27: VEGA -> BISON
    0x32D84: ("57605761576250205020502050205020", "57635764576550205020502050205020"),
    # P1 15 <- 26: GOUKI -> AKUMA
    0x32D94: ("57505751575250205020502050205020", "57535754575557565020502050205020"),
    # P1 19 <- 28: MECH-GOUKI -> CYBER-AKUMA
    0x32DD4: ("55625563556455655566556750205020", "55d255d355d455d555d655d755d85020"),
    # P2 14 <- 27
    0x32F54: ("50205020502050205020502057c057c1", "5020502050205020502057c257c357c4"),
    # P2 15 <- 26
    0x32F64: ("5020502050205020502057ad57ae57af", "5020502050205020502057b057b157b2"),
    # P2 19 <- 28
    0x32FA4: ("5020502055685569556a556b556c556d", "5020502055d955da55db55dc55dd55de"),
}
# Ending speaker labels: 16-character ASCII fields in ME.PAC, one per character
# index (EXP-0054). Index: (Saturn text, US text).
SPEAKER_FIELDS, SPEAKER_FIELD = 0xB164, 16
US_SPEAKERS = {
    14: ("Vega", "Bison"),
    15: ("Gouki", "Akuma"),
    19: ("Mech-Gouki", "Cyber Akuma"),
}


# LOC-004 (EXP-0061): ASCII strings in MM.BIN. (file, offset, Saturn, US); each
# US string has the Saturn string's length. The sound-test titles are 20-character
# fields; the title-menu unlock message is NUL-terminated (the leading space of the
# Saturn string makes room for the longer name).
US_STRINGS = (
    ("MM.BIN", 0x6341, "18.VEGA".ljust(20), "18.BISON".ljust(20)),
    ("MM.BIN", 0x639D, "22.GOUKI".ljust(20), "22.AKUMA".ljust(20)),
    ("MM.BIN", 0x24F03, " MECH-GOUKI NOW!!", "CYBER-AKUMA NOW!!"),
)


# LOC-004: the win banner (EXP-0062) and the VS screen (EXP-0063) spell names from
# sprite records in MM.BIN (letters right to left), each reached through a
# per-character pointer table: banner 0x9FBF8 + 12 * index, VS 0x66536 + 12 * index.
# The disc already has BISON, AKUMA, and CYBER-AKUMA records in both (entries
# 23-25); the US variant points entries 14, 15, and 19 at them.
# Offset: (Saturn record, US record), big-endian u32 load addresses.
US_NAME_POINTERS = {
    0x9FCA0: (0x060B8A88, 0x060B8BCE),  # banner 14: VEGA -> BISON
    0x9FCAC: (0x060B8AA2, 0x060B8BEC),  # banner 15: GOUKI -> AKUMA
    0x9FCDC: (0x060B8B22, 0x060B8C0A),  # banner 19: MECH-GOUKI -> CYBER-AKUMA
    0x665DE: (0x0607F2D8, 0x0607F3B2),  # VS 14: VEGA -> BISON
    0x665EA: (0x0607F2EA, 0x0607F3C6),  # VS 15: GOUKI -> AKUMA
    0x6661A: (0x0607F348, 0x0607F3DA),  # VS 19: MECH-GOUKI -> CYBER-AKUMA
}


@dataclass(frozen=True)
class NameVariant:
    """Name handling for one build variant (LOC-003, LOC-004)."""

    names: Mapping[int, str] = field(default_factory=dict)
    text: Mapping[str, str] = field(default_factory=dict)
    voice: Mapping[int, tuple[int, int]] = field(default_factory=dict)
    labels: Mapping[int, tuple[str, str]] = field(default_factory=dict)
    speakers: Mapping[int, tuple[str, str]] = field(default_factory=dict)
    strings: Sequence[tuple[str, int, str, str]] = ()
    pointers: Mapping[int, tuple[int, int]] = field(default_factory=dict)


NAME_VARIANTS = {
    "saturn": NameVariant(NAME_OVERRIDES, TEXT_OVERRIDES),
    "us": NameVariant(
        voice=US_VOICE_PATCHES,
        labels=US_LABEL_RECORDS,
        speakers=US_SPEAKERS,
        strings=US_STRINGS,
        pointers=US_NAME_POINTERS,
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


def string_patches(variant: str) -> list[dict[str, str]]:
    """Spec ``patches`` entries for the variant's same-length ASCII string edits."""
    patches = []
    for name, offset, old, new in NAME_VARIANTS[variant].strings:
        if len(old) != len(new):
            raise ValueError(f"{new!r} must be as long as {old!r}")
        patches.append(
            {
                "file": name,
                "offset": f"0x{offset:X}",
                "hex": new.encode("ascii").hex(),
                "expect": old.encode("ascii").hex(),
            }
        )
    return patches


def label_patches(variant: str) -> list[dict[str, str]]:
    """Spec ``patches`` entries for the variant's life-bar label records."""
    return [
        {"file": "MM.BIN", "offset": f"0x{offset:X}", "hex": new, "expect": old}
        for offset, (old, new) in sorted(NAME_VARIANTS[variant].labels.items())
    ]


def pointer_patches(variant: str) -> list[dict[str, str]]:
    """Spec ``patches`` entries for the variant's MM.BIN name-record pointers."""
    return [
        {
            "file": "MM.BIN",
            "offset": f"0x{offset:X}",
            "hex": f"{new:08x}",
            "expect": f"{old:08x}",
        }
        for offset, (old, new) in sorted(NAME_VARIANTS[variant].pointers.items())
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
    extra_slots: Sequence[int] = (),
) -> tuple[dict[str, object], dict[str, list[int]]]:
    """The v3 spec, and the arcade Japanese records it replaces.

    ``point`` may list several point characters (`END-020`): each gets its pages
    and its point pair; the partner pairs are shared. ``extra_slots`` (the secret
    characters, `SPECIAL-003`) get both dialogue pairs and their names, but no
    official pages (theirs are translated, ``secret_tables``).
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
    extra = [
        slot for slot in extra_slots if slot not in points and slot not in partners
    ]
    for index in [*partners, *extra, *(SLOTS + slot for slot in [*points, *extra])]:
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
    for slot in sorted({*points, *partners, *extra_slots}):
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


SECRET_SLOTS = (17, 20, 21, 22, 23, 24, 25)  # SPECIAL-002/003 (EXP-0077-0079)


def spec_pairs(spec: dict[str, object]) -> set[str]:
    """The letter pairs a spec's tables and fields already draw."""
    texts = [
        line
        for table in spec["tables"]  # type: ignore[attr-defined]
        for record in table["records"]
        for line in record["lines"]
    ] + [field["text"] for field in spec.get("fields", [])]  # type: ignore[attr-defined]
    pairs: set[str] = set()
    for text in texts:
        padded = text + " " * (len(text) % 2)
        pairs |= {padded[i : i + 2] for i in range(0, len(padded), 2)}
    return pairs - {"  "}


def fits(line: str, shift: int) -> bool:
    """Whether ``line`` with ``shift`` fits one record line (``{XXXX}`` = a cell)."""
    try:
        centred(line, shift=shift)
    except ValueError:
        return False
    return True


def fewest_pair_shifts(lines: set[str], existing: set[str]) -> dict[str, int]:
    """Each line's half-cell shift, chosen to add the fewest pairs to ``existing``
    (lines visited in sorted order, so the result is deterministic)."""
    shifts: dict[str, int] = {}
    added: set[str] = set()
    for line in sorted(lines):
        options = [
            (len(line_pairs(line, shift) - existing - added), shift)
            for shift in (0, 1)
            if fits(line, shift)
        ]
        shifts[line] = min(options)[1]
        added |= line_pairs(line, shifts[line]) - existing
    return shifts


def exchange_table(
    program: bytes,
    track: Path,
    existing: set[str] = frozenset(),  # type: ignore[assignment]
    variant: str = "saturn",
) -> dict[str, object]:
    """Spec table for Apocalypse's pre-fight exchanges in official English.

    Record ``3 * slot + box`` gets the US arcade's English box at the same slot
    and position. The Saturn block must equal the arcade Japanese block, or the
    pairing does not hold and the table is refused.
    """
    count = SLOTS * EXCHANGE_BOXES
    with track.open("rb") as stream:
        disc = Track(stream, track.stat().st_size)
        mc00 = decode_file(disc.read(*find_entry(track, "MC00.PAC;1")))[1]
    saturn = mc00[EXCHANGES_MC00 : EXCHANGES_MC00 + RECORD * count]
    if saturn != program[EXCHANGES_JA : EXCHANGES_JA + RECORD * count]:
        raise ValueError("MC00 exchanges differ from the arcade Japanese block")
    boxes = []
    for k in range(count):
        lines = en_lines(program, EXCHANGES_EN + EN_RECORD * k, variant)
        for code, text in EXCHANGE_CODE_TEXT.items():
            lines = [line.replace(code, text) for line in lines]
        boxes.append(lines)
    shifts = fewest_pair_shifts({x for box in boxes for x in box if x}, existing)
    return {
        "file": "MC00.PAC",
        "table": f"0x{EXCHANGES_MC00:X}",
        "records": [
            {
                "record": k,
                "lines": [centred(x, shift=shifts.get(x, 0)) for x in lines],
            }
            for k, lines in enumerate(boxes)
        ],
    }


def secret_tables(
    path: Path,
    track: Path,
    existing: set[str] = frozenset(),  # type: ignore[assignment]
    variant: str = "saturn",
) -> list[dict[str, object]]:
    """Spec tables for the translated secret-character text (``path``).

    Every record names its Japanese source by SHA-256; a source that differs
    (another image, a moved table) is refused. Each line's half-cell shift is
    chosen to add the fewest pairs to ``existing`` (the font is nearly full).
    Names are written in the US arcade form and localized to ``variant``.
    """
    document = json.loads(path.read_text())
    tables = document["tables"]
    for table in tables:
        for record in table["records"]:
            record["lines"] = [localize(x, variant) for x in record["lines"]]
    with track.open("rb") as stream:
        disc = Track(stream, track.stat().st_size)
        sources = {}
        for table in tables:
            name = table["file"]
            if name not in sources:
                data = disc.read(*find_entry(track, f"{name};1"))
                sources[name] = (
                    data if table.get("format") == "raw" else decode_file(data)[1]
                )
    shifts = fewest_pair_shifts(
        {x for t in tables for r in t["records"] for x in r["lines"] if x}, existing
    )
    out = []
    for table in tables:
        base = int(table["table"], 16)
        records = []
        for record in table["records"]:
            k = record["record"]
            source = sources[table["file"]][base + RECORD * k : base + RECORD * (k + 1)]
            if hashlib.sha256(source).hexdigest() != record["source_sha256"]:
                raise ValueError(
                    f"{table['file']} 0x{base:X} record {k}: source differs"
                )
            records.append(
                {
                    "record": k,
                    "lines": [
                        centred(x, shift=shifts.get(x, 0)) for x in record["lines"]
                    ],
                }
            )
        entry: dict[str, object] = {
            "file": table["file"],
            "table": table["table"],
            "records": records,
        }
        if table.get("format") == "raw":
            entry["format"] = "raw"
        out.append(entry)
    return out


def attract_patches(track: Path) -> list[dict[str, str]]:
    """The attract-caption patches for the eight ``MVSOP`` streams (`EXP-0071`)."""
    with track.open("rb") as stream:
        disc = Track(stream, track.stat().st_size)
        files = {
            name: disc.read(*find_entry(track, f"{name};1"))
            for name in [*FILES, "MEMFIX.PAC"]
        }
    offset, length = FONT_ENTRY
    return st2_patches(files, files["MEMFIX.PAC"][offset : offset + length])


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
        "--unlock-boss-fight",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="start with the title menu's boss fight unlocked (OPT-001)",
    )
    parser.add_argument(
        "--attract-captions",
        action="store_true",
        help="draw the attract-mode captions in English banner letters (UI-003)",
    )
    parser.add_argument(
        "--track",
        type=Path,
        default=Path(
            "local/disc_images/mshvsf_saturn_jp/"
            "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
        ),
    )
    parser.add_argument(
        "--secret-translations",
        type=Path,
        help="translated secret-character text and dialogue (SPECIAL-003)",
    )
    parser.add_argument(
        "--ui-translations",
        type=Path,
        help="translated screen text, such as the CONTINUE? hints (UI-004)",
    )
    parser.add_argument(
        "--secret-roster",
        type=Path,
        help="extra win-quote roster with official English (SPECIAL-003)",
    )
    parser.add_argument(
        "--boss-exchanges",
        action="store_true",
        help="Apocalypse's pre-fight exchanges in official English (SPECIAL-004)",
    )
    parser.add_argument("--out", type=Path, required=True, help="spec path (ignored)")
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text(encoding="utf-8"))
    program = build_program(args.archive, sets[args.set_name or args.archive.stem])
    roster = json.loads(args.roster.read_text())["characters"] if args.roster else []
    points = [int(c["slot"]) for c in roster] or args.point
    partners = [int(c["slot"]) for c in roster] or args.partners
    spec, targets = ending_spec(
        program,
        points,
        partners,
        args.dialogue_layout,
        args.names,
        SECRET_SLOTS if args.secret_translations else (),
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
        secret = (
            json.loads(args.secret_roster.read_text())["characters"]
            if args.secret_roster
            else []
        )
        win_quote_tables = roster_spec(quotes, roster + secret)["tables"]
        assert isinstance(win_quote_tables, list)
        spec["tables"] = win_quote_tables + tables
        spec["description"] = (
            "END-023 combined roster image: M5 official English win quotes (RE-044) "
            "and the roster's official English endings, dialogue layout "
            f"{args.dialogue_layout}. Generated from the local arcade ROM; not "
            "committed."
        )
    if args.secret_translations:
        tables = spec["tables"]
        assert isinstance(tables, list)
        tables += secret_tables(
            args.secret_translations, args.track, spec_pairs(spec), args.names
        )
        spec["secret_translations"] = True
        # The font is full: kanji only replaced records use may be reclaimed
        # (caption_compiler.retired_kanji, EXP-0079).
        spec["retire_replaced_kanji"] = True
    if args.ui_translations:
        tables = spec["tables"]
        assert isinstance(tables, list)
        tables += secret_tables(
            args.ui_translations, args.track, spec_pairs(spec), args.names
        )
        spec["retire_replaced_kanji"] = True
    if args.boss_exchanges:
        tables = spec["tables"]
        assert isinstance(tables, list)
        tables.append(exchange_table(program, args.track, spec_pairs(spec), args.names))
        spec["boss_exchanges"] = True
        spec["retire_replaced_kanji"] = True
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
        patches += (
            voice_patches(args.names)
            + speaker_patches(args.names)
            + string_patches(args.names)
            + pointer_patches(args.names)
            + label_patches(args.names)
        )
    if args.unlock_boss_fight:
        spec["unlock_boss_fight"] = True
        patches = spec["patches"]
        assert isinstance(patches, list)
        patches.append(dict(UNLOCK_BOSS_PATCH))
    if args.attract_captions:
        spec["attract_captions"] = True
        patches = spec["patches"]
        assert isinstance(patches, list)
        patches += attract_patches(args.track)
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
