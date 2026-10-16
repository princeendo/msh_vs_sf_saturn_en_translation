from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.memory.diff import ByteRange, changed_mask, compare, main, runs

SCHEMA = Path("tools/memory/diff_result.schema.json")


def write(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    return path


def test_runs_finds_inclusive_ranges_and_merges_gaps() -> None:
    mask = bytes([0, 1, 1, 0, 0, 1, 0, 1])

    assert runs(mask, 1) == [ByteRange(1, 2), ByteRange(5, 5), ByteRange(7, 7)]
    assert runs(mask, 1, merge_gap=1) == [ByteRange(1, 2), ByteRange(5, 7)]
    assert runs(mask, 0) == [ByteRange(0, 0), ByteRange(3, 4), ByteRange(6, 6)]
    assert runs(bytes(4), 1) == []


def test_changed_mask_rejects_size_mismatch() -> None:
    with pytest.raises(ValueError, match="size mismatch"):
        changed_mask(b"ab", b"abc")


def test_compare_reports_ranges_with_base_address(tmp_path: Path) -> None:
    a = write(tmp_path / "a.bin", bytes([0, 1, 2, 3, 4, 5]))
    b = write(tmp_path / "b.bin", bytes([0, 9, 9, 3, 4, 9]))

    result = compare(a, b, 0x06000000, include_unchanged=True)

    assert result["raw_changed_bytes"] == 3
    assert result["changed_bytes"] == 3
    assert result["changed_ranges"] == [
        {"start": "0x06000001", "end": "0x06000002", "offset": 1, "length": 2},
        {"start": "0x06000005", "end": "0x06000005", "offset": 5, "length": 1},
    ]
    assert result["unchanged_ranges"] == [
        {"start": "0x06000000", "end": "0x06000000", "offset": 0, "length": 1},
        {"start": "0x06000003", "end": "0x06000004", "offset": 3, "length": 2},
    ]


def test_compare_excludes_offsets_changed_in_control_pair(tmp_path: Path) -> None:
    a = write(tmp_path / "a.bin", bytes([0, 1, 2, 3]))
    b = write(tmp_path / "b.bin", bytes([9, 9, 9, 3]))
    control_a = write(tmp_path / "ca.bin", bytes([0, 1, 2, 3]))
    control_b = write(tmp_path / "cb.bin", bytes([7, 1, 2, 3]))

    result = compare(a, b, 0, controls=[(control_a, control_b)])

    assert result["raw_changed_bytes"] == 3
    assert result["excluded_bytes"] == 1
    assert result["changed_bytes"] == 2
    assert result["changed_ranges"] == [
        {"start": "0x00000001", "end": "0x00000002", "offset": 1, "length": 2}
    ]


def test_compare_rejects_unequal_inputs(tmp_path: Path) -> None:
    a = write(tmp_path / "a.bin", b"ab")
    b = write(tmp_path / "b.bin", b"abc")

    with pytest.raises(ValueError):
        compare(a, b, 0)


def test_main_json_matches_schema_keys(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    a = write(tmp_path / "a.bin", bytes([1, 2]))
    b = write(tmp_path / "b.bin", bytes([1, 3]))

    assert main([str(a), str(b), "--base", "0x200000", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    schema = json.loads(SCHEMA.read_text())
    assert set(schema["required"]) <= set(output) <= set(schema["properties"])
    assert output["schema"] == schema["properties"]["schema"]["const"]
    assert output["changed_ranges"][0]["start"] == "0x00200001"


def test_main_text_mode_and_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    a = write(tmp_path / "a.bin", bytes([1, 2]))
    b = write(tmp_path / "b.bin", bytes([1, 3]))

    assert main([str(a), str(b)]) == 0
    assert "changed: 1 in 1 ranges" in capsys.readouterr().out

    with pytest.raises(SystemExit) as error:
        main([str(a), str(tmp_path / "missing.bin")])
    assert error.value.code == 2
