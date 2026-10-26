from __future__ import annotations

from tools.mednafen.bp_log import parse_hit


def test_parse_hit_reads_fields() -> None:
    hit = parse_hit("hit n=4 frame=273 mode=log PC=06022242 R0=FFFFF111 GBR=06021054")
    assert hit is not None
    assert hit["frame"] == "273" and hit["PC"] == "06022242"
    assert hit["GBR"] == "06021054"


def test_parse_hit_ignores_other_lines() -> None:
    assert parse_hit("onhit write workramh 1000 00") is None
