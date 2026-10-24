from __future__ import annotations

from pathlib import Path

from tools.mednafen.session_recorder import prune


def test_prune_keeps_newest_by_frame(tmp_path: Path) -> None:
    for frame in (900, 10000, 50, 2000):
        (tmp_path / f"f{frame:08d}.mcs").write_bytes(b"")
    doomed = prune(tmp_path, "f*.mcs", 2)
    assert [p.name for p in doomed] == ["f00000050.mcs", "f00000900.mcs"]
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "f00002000.mcs",
        "f00010000.mcs",
    ]


def test_prune_zero_keeps_all(tmp_path: Path) -> None:
    (tmp_path / "f00000001.png").write_bytes(b"")
    assert prune(tmp_path, "f*.png", 0) == []
    assert len(list(tmp_path.iterdir())) == 1
