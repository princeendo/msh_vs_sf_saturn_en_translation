from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from tools.disc.make_patch import compare_images, components, decode, encode, patch_name


def write(directory: Path, files: dict[str, bytes]) -> dict[str, Path]:
    directory.mkdir()
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / "notes.txt").write_text("ignored")
    return components(directory)


def test_compare_images_lists_differing_and_unchanged(tmp_path: Path) -> None:
    source = write(tmp_path / "a", {"x (Track 01).bin": b"1", "x.cue": b"c"})
    built = write(tmp_path / "b", {"x (Track 01).bin": b"2", "x.cue": b"c"})
    assert compare_images(source, built) == (["x (Track 01).bin"], ["x.cue"])


def test_compare_images_rejects_different_component_sets(tmp_path: Path) -> None:
    source = write(tmp_path / "a", {"x (Track 01).bin": b"1"})
    built = write(tmp_path / "b", {"y (Track 01).bin": b"1"})
    with pytest.raises(ValueError):
        compare_images(source, built)


def test_patch_name_uses_the_track_label() -> None:
    name = "Marvel Super Heroes vs. Street Fighter (Japan) (Track 01).bin"
    assert patch_name("m8", name) == "m8.Track01.xdelta"
    assert patch_name("m8", "disc.bin") == "m8.disc.xdelta"


@pytest.mark.skipif(shutil.which("xdelta3") is None, reason="needs xdelta3")
def test_xdelta_round_trip_and_wrong_source(tmp_path: Path) -> None:
    source, target = tmp_path / "s.bin", tmp_path / "t.bin"
    data = bytes(range(256)) * 400
    source.write_bytes(data)
    target.write_bytes(data[:1000] + b"ENGLISH" + data[1007:])
    patch, out = tmp_path / "p.xdelta", tmp_path / "o.bin"
    encode("xdelta3", source, target, patch)
    decode("xdelta3", source, patch, out)
    assert out.read_bytes() == target.read_bytes()
    wrong = tmp_path / "w.bin"
    wrong.write_bytes(bytes(len(data)))
    with pytest.raises(subprocess.CalledProcessError):
        decode("xdelta3", wrong, patch, tmp_path / "w_out.bin")
