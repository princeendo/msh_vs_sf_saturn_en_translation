from __future__ import annotations

import hashlib
import json
import zipfile
import zlib
from pathlib import Path

import pytest

from tools.reference.mame_audit import (
    audit,
    family,
    hash_members,
    main,
    parse_driver,
    rank_candidates,
)

PROG = b"synthetic program"
SOUND = b"sound-head" + b"sound-tail"
CLONE_PROG = b"clone program!!"


def crc(data: bytes) -> str:
    return f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


DRIVER = f"""
ROM_START( parent )
\tROM_REGION( CODE_SIZE, "maincpu", 0 )
\tROM_LOAD16_WORD_SWAP( "p.03", 0x000000, {len(PROG):#x}, CRC({crc(PROG)}) SHA1({sha1(PROG)}) )
\tROM_LOAD( "s.01",   0x00000, 0x0a, CRC({crc(SOUND)}) SHA1({sha1(SOUND)}) )
\tROM_CONTINUE(         0x10000, 0x0a )
ROM_END

ROM_START( clone )
\tROM_LOAD16_WORD_SWAP( "c.03", 0x000000, {len(CLONE_PROG):#x}, CRC({crc(CLONE_PROG)}) SHA1({sha1(CLONE_PROG)}) )
\tROM_LOAD( "s.01",   0x00000, 0x0a, CRC({crc(SOUND)}) SHA1({sha1(SOUND)}) )
\tROM_CONTINUE(         0x10000, 0x0a )
ROM_END

GAME( 1997, parent,     0,        cps2,     cps2_2p6b, cps2_state, init_cps2,     ROT0,   "Maker", "Synthetic (Europe 970625)",  MACHINE_SUPPORTS_SAVE )
GAME( 1997, clone,      parent,   cps2,     cps2_2p6b, cps2_state, init_cps2,     ROT0,   "Maker", "Synthetic (USA 970827)",     MACHINE_SUPPORTS_SAVE )
"""  # noqa: E501


def write_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as bundle:
        for name, data in members.items():
            bundle.writestr(name, data)
    return path


def test_parse_driver_reads_sets_titles_and_continued_sizes() -> None:
    sets = parse_driver(DRIVER)

    assert list(sets) == ["parent", "clone"]
    assert sets["parent"].parent == ""
    assert sets["clone"].parent == "parent"
    assert sets["clone"].title == "Synthetic (USA 970827)"
    assert sets["parent"].manufacturer == "Maker"
    sound = sets["parent"].roms[1]
    assert (sound.name, sound.size, sound.crc32) == ("s.01", 20, crc(SOUND))


def test_audit_reports_ok_missing_bad_and_unexpected(tmp_path: Path) -> None:
    sets = parse_driver(DRIVER)
    archive = write_zip(
        tmp_path / "parent.zip",
        {"p.03": PROG[:-1] + b"?", "extra.txt": b"x"},
    )

    report = audit(archive.name, hash_members(archive), sets["parent"])

    statuses = {member.name: member.status for member in report.members}
    assert statuses == {"p.03": "bad_hash", "s.01": "missing"}
    assert report.unexpected == ["extra.txt"]
    assert report.matched == 0
    assert not report.complete


def test_audit_detects_size_mismatch(tmp_path: Path) -> None:
    sets = parse_driver(DRIVER)
    archive = write_zip(tmp_path / "parent.zip", {"p.03": PROG, "s.01": SOUND[:5]})

    report = audit(archive.name, hash_members(archive), sets["parent"])

    assert [member.status for member in report.members] == ["ok", "bad_size"]


def test_rank_candidates_prefers_the_matching_set(tmp_path: Path) -> None:
    sets = parse_driver(DRIVER)
    archive = write_zip(tmp_path / "clone.zip", {"c.03": CLONE_PROG, "s.01": SOUND})
    members = hash_members(archive)

    assert audit(archive.name, members, sets["clone"]).complete
    ranked = rank_candidates(archive.name, members, family(sets, "parent"))
    assert ranked == [("clone", 2, 2), ("parent", 1, 2)]


def test_main_checks_driver_hash_and_emits_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    driver = tmp_path / "driver.cpp"
    driver.write_text(DRIVER)
    digest = hashlib.sha256(driver.read_bytes()).hexdigest()
    archive = write_zip(tmp_path / "clone.zip", {"c.03": CLONE_PROG, "s.01": SOUND})

    with pytest.raises(SystemExit):
        main(
            ["--driver", str(driver), "--expect-driver-sha256", "0" * 64, str(archive)]
        )
    capsys.readouterr()

    args = [
        "--driver",
        str(driver),
        "--expect-driver-sha256",
        digest,
        "--json",
        "--family",
        "parent",
        str(archive),
    ]
    assert main(args) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["driver_sha256"] == digest
    [entry] = output["audits"]
    assert entry["set_name"] == "clone"
    assert entry["complete"] is True
    assert entry["candidates"][0] == ["clone", 2, 2]
