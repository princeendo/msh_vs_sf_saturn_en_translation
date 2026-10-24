from __future__ import annotations

from pathlib import Path

import pytest

from tools.text.code_search import main, search


def words(*codes: int) -> bytes:
    return b"".join(c.to_bytes(2, "big") for c in codes)


def test_search_aligned_wildcards_and_overlaps() -> None:
    data = b"\x00" + words(0x089C, 0x0897) + b"\x00" + words(0x08AE, 0x08AE, 0x08AE)
    # the unaligned 089C 0897 at offset 1 is ignored
    assert search(data, "089C 0897") == []
    assert search(data, "08AE 08AE") == [6, 8]
    assert search(data, "? 08AE", base=0x100) == [0x104, 0x106, 0x108]


def test_empty_pattern_rejected() -> None:
    with pytest.raises(ValueError):
        search(b"", " ")


def test_main_reports_bus_addresses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dump = tmp_path / "wram_l.bin"
    dump.write_bytes(words(0x0020, 0x0970, 0x080B))
    assert main(["0970 080B", str(dump)]) == 0
    assert "0x00200002" in capsys.readouterr().out
