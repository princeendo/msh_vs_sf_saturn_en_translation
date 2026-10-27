from __future__ import annotations

from pathlib import Path

from tools.mednafen.replay_state import quiet_home


def test_quiet_home_mutes_a_copy_and_shares_firmware(tmp_path: Path) -> None:
    source = tmp_path / "mednafen"
    (source / "firmware").mkdir(parents=True)
    (source / "mednafen.cfg").write_text("sound 1\nsound.volume 100\nss.cart auto\n")
    target = quiet_home(source, tmp_path / "quiet")
    assert (target / "mednafen.cfg").read_text().splitlines() == [
        "sound 1",
        "sound.volume 0",
        "ss.cart auto",
    ]
    assert (target / "firmware").resolve() == (source / "firmware").resolve()
    assert (source / "mednafen.cfg").read_text().count("sound.volume 100") == 1
    assert quiet_home(source, target) == target  # an existing home is kept


def test_quiet_home_turns_off_vsync_even_in_an_existing_home(tmp_path: Path) -> None:
    source = tmp_path / "mednafen"
    (source / "firmware").mkdir(parents=True)
    (source / "mednafen.cfg").write_text(
        "video.glvsync 1\nvideo.blit_timesync 1\nsound.volume 100\n"
    )
    target = tmp_path / "quiet"
    target.mkdir()
    (target / "mednafen.cfg").write_text("video.glvsync 1\nsound.volume 100\n")
    quiet_home(source, target)
    assert (target / "mednafen.cfg").read_text().splitlines() == [
        "video.glvsync 0",
        "sound.volume 0",
    ]


def test_quiet_home_keeps_other_bytes_exactly(tmp_path: Path) -> None:
    source = tmp_path / "mednafen"
    (source / "firmware").mkdir(parents=True)
    raw = b"name \xe8\xa7\x92\x85x\x1c\nvideo.glvsync 1\n"
    (source / "mednafen.cfg").write_bytes(raw)
    target = quiet_home(source, tmp_path / "quiet")
    assert (target / "mednafen.cfg").read_bytes() == raw.replace(
        b"video.glvsync 1", b"video.glvsync 0"
    )
