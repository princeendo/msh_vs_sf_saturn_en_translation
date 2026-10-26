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
