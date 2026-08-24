from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.disc.hash_source import identify_source, main


def test_identify_source_reports_stable_metadata(tmp_path: Path) -> None:
    source = tmp_path / "synthetic.bin"
    content = b"synthetic test data\x00\xff"
    source.write_bytes(content)

    identity = identify_source(source, "Synthetic fixture")

    assert identity.filename == "synthetic.bin"
    assert identity.size_bytes == len(content)
    assert identity.sha256 == hashlib.sha256(content).hexdigest()
    assert identity.description == "Synthetic fixture"
    assert source.read_bytes() == content


def test_main_emits_machine_readable_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "fixture.bin"
    source.write_bytes(b"fixture")

    result = main(["--json", "--description", "Test data", str(source)])
    output = json.loads(capsys.readouterr().out)

    assert result == 0
    assert output == [
        {
            "filename": "fixture.bin",
            "size_bytes": 7,
            "sha256": hashlib.sha256(b"fixture").hexdigest(),
            "description": "Test data",
        }
    ]


def test_main_emits_human_readable_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "fixture.bin"
    source.write_bytes(b"fixture")

    assert main([str(source)]) == 0

    output = capsys.readouterr().out
    assert "Filename: fixture.bin" in output
    assert "Size: 7 bytes" in output
    assert "SHA-256:" in output
    assert "Description: (not provided)" in output


def test_main_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as error:
        main([str(tmp_path / "missing.bin")])

    assert error.value.code == 2
