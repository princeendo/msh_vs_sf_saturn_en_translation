from __future__ import annotations

import pytest

from tools.reference.arcade_route import SETUP, main, timeline


def test_timeline_orders_setup_loop_snaps_and_exit() -> None:
    lines = timeline(6, 5300, 9000, 9080, 40, "local/x/p")

    assert lines[: len(SETUP)] == SETUP
    assert lines[len(SETUP) : len(SETUP) + 3] == [
        "5206 press 10 P1 Down",
        "5211 press 10 P1 Right",
        "5218 press 4 P1 Button 3",
    ]
    assert "5242 press 10 P1 Down" in lines
    assert "9000 snap" in lines
    assert "9040 dump 0xff2498 0xff24a3 local/x/p_f09040.bin" in lines
    assert lines[-1] == "9080 exit"


def test_timeline_without_dumps_has_only_snaps() -> None:
    lines = timeline(0, 5200, 100, 200, 50, "")

    assert not any(" dump " in line for line in lines)
    assert lines[-3:] == ["100 snap", "150 snap", "200 exit"]


def test_main_prints_timeline(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--loop-end", "5200", "--snap-start", "10", "--snap-end", "11"]) == 0

    assert capsys.readouterr().out.splitlines()[-2:] == ["10 snap", "11 exit"]
