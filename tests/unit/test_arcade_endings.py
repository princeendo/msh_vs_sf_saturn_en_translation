from __future__ import annotations

from tools.reference.arcade_ending_route import STAGE_WORD, VITALITY, timeline
from tools.reference.arcade_endings import (
    PAGE_TABLES,
    PARTNER_LINES,
    PARTNER_RECORD,
    SLOTS,
    ending,
    page_span,
)

A = 0x0140  # "A" in the arcade Latin map (EXP-0029)


def program_with_pages() -> bytes:
    program = bytearray(0x240000)
    for language, table in PAGE_TABLES.items():
        size = 76 if language == "ja" else 100
        base = 0x230000 + 0x1000 * list(PAGE_TABLES).index(language)
        for slot in range(SLOTS):
            start = base + 3 * size * slot  # three pages per slot
            program[table + 4 * slot : table + 4 * slot + 4] = start.to_bytes(4, "big")
            program[start : start + 2] = (A + slot).to_bytes(2, "big")
    for index in range(2 * SLOTS):
        address = PARTNER_LINES + PARTNER_RECORD * index
        program[address : address + 2] = (A + index % SLOTS).to_bytes(2, "big")
    return bytes(program)


def test_page_span_runs_to_next_pointer() -> None:
    program = program_with_pages()
    start, end = page_span(program, PAGE_TABLES["en"], 9)
    assert end - start == 300


def test_ending_reports_pages_and_partner_lines() -> None:
    report = ending(program_with_pages(), point=9, partner=15)
    assert report["pages_ja"]["records"] == 3  # type: ignore[index]
    assert report["pages_en"]["records"] == 3  # type: ignore[index]
    assert report["pages_en"]["text"].startswith("J")  # type: ignore[index]
    lines = report["partner_lines_en"]
    assert lines["partner"]["address"] == f"0x{PARTNER_LINES + 1500:06X}"  # type: ignore[index]
    assert lines["point"]["text"].startswith("J")  # type: ignore[index]


def test_route_forces_and_releases_in_order() -> None:
    lines = timeline("gouki", end=9000)
    force = lines.index(f"3000 force16 {STAGE_WORD:#x} 0x0607")
    release = lines.index(f"7100 unforce {STAGE_WORD:#x}")
    assert force < release
    assert f"5600 force16 {VITALITY[0]:#x} 0x0000" in lines
    assert "4360 press 4 P1 Up" in lines and "4400 press 4 P1 Right" in lines
    assert "4440 press 6 P1 Button 1" in lines
    assert lines[-1] == "9000 exit"
    assert "4360 press 6 P1 Button 1" in timeline("ken")


def test_point_path_runs_before_the_point_confirm() -> None:
    lines = timeline("captain_america", end=9000, point="gouki")
    assert lines.index("4260 press 4 P1 Up") < lines.index("4300 press 6 P1 Button 1")
    assert "4360 press 4 P1 Down" in lines and "4400 press 4 P1 Right" in lines
