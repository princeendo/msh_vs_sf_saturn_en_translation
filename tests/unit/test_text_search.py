from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.text.search import (
    Pattern,
    encode_text,
    find_all,
    main,
    parse_hex,
    search,
)


def test_parse_hex_accepts_spacing_and_rejects_bad_input() -> None:
    assert parse_hex("82 a0 82A2") == b"\x82\xa0\x82\xa2"
    with pytest.raises(ValueError):
        parse_hex("8")
    with pytest.raises(ValueError):
        parse_hex("")


def test_encode_text_uses_explicit_encoding() -> None:
    assert encode_text("あ", "shift_jis") == b"\x82\xa0"
    assert encode_text("あ", "euc_jp") == b"\xa4\xa2"
    assert encode_text("あ", "utf-16-be") == b"\x30\x42"
    with pytest.raises(ValueError):
        encode_text("é", "ascii")
    with pytest.raises(ValueError):
        encode_text("a", "not-a-codec")


def test_find_all_reports_overlapping_and_absent_matches() -> None:
    assert find_all(b"aaaa", b"aa") == [0, 1, 2]
    assert find_all(b"abc", b"x") == []


def test_search_reports_addresses_context_and_hashes(tmp_path: Path) -> None:
    data = b"\x00\x01\x82\xa0\x02\x82\xa0"
    path = tmp_path / "dump.bin"
    path.write_bytes(data)

    result = search(
        [path], [Pattern("text:あ", "shift_jis", b"\x82\xa0")], 0x06000000, radius=1
    )

    record = result["files"][0]  # type: ignore[index]
    assert record["sha256"] == hashlib.sha256(data).hexdigest()
    item = record["results"][0]
    assert item["match_count"] == 2
    assert [m["address"] for m in item["matches"]] == ["0x06000002", "0x06000005"]
    assert item["matches"][0]["context"] == {"start_offset": 1, "hex": "01 82 a0 02"}


def test_main_json_multiple_encodings_and_no_match(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "dump.bin"
    path.write_bytes(b"\xa4\xa2")

    args = [str(path), "--text", "あ", "--encoding", "shift_jis"]
    assert main([*args, "--encoding", "euc_jp", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    counts = {r["encoding"]: r["match_count"] for r in output["files"][0]["results"]}
    assert counts == {"shift_jis": 0, "euc_jp": 1}


def test_main_text_mode_and_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "dump.bin"
    path.write_bytes(b"\x12\x34")

    assert main([str(path), "--hex", "1234"]) == 0
    assert "1 match(es)" in capsys.readouterr().out

    with pytest.raises(SystemExit) as error:
        main([str(path)])
    assert error.value.code == 2
