from __future__ import annotations

import json
import struct
import wave
from pathlib import Path

import pytest

from tools.audio.cmnse_bank import (
    STEP_MAX,
    STEP_MIN,
    Clip,
    decode,
    decode_state,
    export,
    main,
    parse,
)


def bank(clips: list[tuple[int, bytes]]) -> bytes:
    table = b"".join(struct.pack(">HH", tag, len(data)) for tag, data in clips)
    header = bytes(16) + struct.pack(">I", len(clips))
    return header + table + b"".join(data for _, data in clips)


def test_parse_reads_ids_flags_and_offsets() -> None:
    data = bank([((2 << 10) | 0x00A, b"\x00" * 3), (0x2AD, b"\x88")])
    assert parse(data) == [
        Clip(0, 0x00A, 2, 0x1C, 3),
        Clip(1, 0x2AD, 0, 0x1F, 1),
    ]


def test_parse_rejects_clips_past_the_end() -> None:
    with pytest.raises(ValueError):
        parse(bank([(1, b"\x00\x00")])[:-1])


def test_decode_is_high_nibble_first_without_bias() -> None:
    # 7: +128*7>>2 = 224, step 128*2.4 -> 307; 0: +0, step 307*0.9 -> 276.
    assert decode(b"\x70") == [224, 224]
    assert decode(b"\xf8") == [-224, -224]
    assert decode(b"\x07") == [0, 224]


def test_decode_state_returns_the_final_predictor_and_step() -> None:
    assert decode_state(b"\x70") == ([224, 224], 224, 276)
    # Resuming from a stored state continues the same sequence.
    assert decode(b"\x07", 224, 276) == decode(b"\x70\x07")[2:]


def test_silence_stays_at_zero() -> None:
    assert decode(b"\x08\x80" * 16) == [0] * 64


def test_step_clamps() -> None:
    rising = decode(b"\x77" * 64)
    assert rising[-1] - rising[-2] == (STEP_MAX * 7) >> 2
    # From the floor, a zero nibble keeps the step at the minimum.
    assert decode(b"\x01") == [0, STEP_MIN >> 2]


def test_export_writes_wavs_and_index(tmp_path: Path) -> None:
    data = bank([(0x004, b"\x70\x00"), (0x008, b"\x08")])
    rows = export(data, tmp_path, 12000, 0.5)
    assert [r["file"] for r in rows] == ["cmnse_00_id004.wav", "cmnse_01_id008.wav"]
    with wave.open(str(tmp_path / "cmnse_00_id004.wav")) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 12000)
        frames = struct.unpack("<4h", w.readframes(4))
    assert frames[0] == round(32767 * 0.5)
    assert rows[1]["gain"] == 1.0  # a silent clip is not scaled


def test_main_reads_an_extracted_bank(tmp_path: Path) -> None:
    source = tmp_path / "CMNSE.PAC"
    source.write_bytes(bank([(0x004, b"\x70")]))
    out = tmp_path / "out"
    assert main(["--bank", str(source), "--out-dir", str(out), "--peak", "0"]) == 0
    rows = json.loads((out / "index.json").read_text())
    assert rows[0]["peak"] == 224 and rows[0]["gain"] == 1.0
