from __future__ import annotations

from tools.regression.reference_builds import (
    TRACK01,
    compare,
    rebaseline,
    report_markdown,
)


def manifest(track: str = "t1", mc09: str = "m9", ok: bool = True) -> dict[str, object]:
    return {
        "spec_sha256": "s",
        "outputs": {"MEMFIX.PAC": "mf", "MC09.PAC": mc09},
        "checks": {"font": {"pairs_equal_composed": ok}, "tables": {"MC09.PAC": {}}},
        "image": {"output_sha256": {TRACK01: track}, "checks": {"lsns": True}},
    }


def reference() -> dict[str, object]:
    return {
        "name": "ref",
        "experiment": "EXP-0000",
        "purpose": "Synthetic.",
        "spec_sha256": "s",
        "track01_sha256": "t1",
        "files_sha256": {"MC09.PAC": "m9", "MEMFIX.PAC": "mf"},
    }


def test_compare_passes_identical_hashes() -> None:
    assert compare(reference(), manifest()) == []


def test_compare_reports_hash_changes_and_false_checks() -> None:
    problems = compare(reference(), manifest(track="t2", mc09="x", ok=False))

    assert "check false: font.pairs_equal_composed" in problems
    assert any(p.startswith("track01_sha256") for p in problems)
    assert any(p.startswith("file MC09.PAC") for p in problems)


def test_rebaseline_moves_old_hash_to_previous_and_skips_bad_checks() -> None:
    good, bad = reference(), reference() | {"name": "bad"}
    baseline: dict[str, object] = {"references": [good, bad]}
    results: list[dict[str, object]] = [
        {
            "name": "ref",
            "status": "fail",
            "problems": compare(good, manifest(track="t2")),
            "observed": {"track01_sha256": "t2", "files_sha256": {"MC09.PAC": "m9"}},
        },
        {
            "name": "bad",
            "status": "fail",
            "problems": compare(bad, manifest(ok=False)),
            "observed": {"track01_sha256": "t1", "files_sha256": {}},
        },
    ]

    assert rebaseline(baseline, results, "2026-10-24", "why") == ["ref"]
    assert good["track01_sha256"] == "t2"
    assert good["previous"] == [{"track01_sha256": "t1", "replaced_because": "why"}]
    assert bad["track01_sha256"] == "t1" and "previous" not in bad


def test_report_lists_every_reference_and_its_last_check() -> None:
    skipped = reference() | {"name": "absent"}
    baseline: dict[str, object] = {"references": [reference(), skipped]}
    results: list[dict[str, object]] = [
        {"name": "ref", "status": "pass", "spec_source": "cached", "problems": []},
    ]

    text = report_markdown(baseline, results, "2026-10-24")

    assert "| `ref` | `EXP-0000` |" in text
    assert "pass (cached spec)" in text
    assert "| `absent` |" in text and "not run" in text
    assert "| `MC09.PAC` | `m9` |" in text
