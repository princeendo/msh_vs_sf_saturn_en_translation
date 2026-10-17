from __future__ import annotations

import os
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from tools.mednafen.agent import Agent, AgentError, bus_to_space, parse_pairs


class FakeMednafen:
    """Answers the file protocol the way the patched binary does."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.memory = {"workramh": bytearray(0x100000), "workraml": bytearray(0x100000)}
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.loop, daemon=True)

    def handle(self, line: str) -> str:
        words = line.split()
        if words[0] == "id":
            return line
        if words[0] == "status":
            return "ok halted=1 frame=12 hits=0 pc=060AF724 pending=0"
        if words[0] == "regs":
            return "ok PC=060AF724 R0=00209290"
        if words[0] == "read":
            space, addr, length, path = (
                words[1],
                int(words[2], 16),
                int(words[3]),
                words[4],
            )
            Path(path).write_bytes(bytes(self.memory[space][addr : addr + length]))
            return f"ok read {length} bytes"
        if words[0] == "write":
            space, addr, data = words[1], int(words[2], 16), bytes.fromhex(words[3])
            self.memory[space][addr : addr + len(data)] = data
            return "ok write"
        return f"err unknown command {words[0]}"

    def loop(self) -> None:
        cmd = self.directory / "cmd"
        while not self.stop.is_set():
            if cmd.exists():
                lines = cmd.read_text().splitlines()
                cmd.unlink()
                reply = "\n".join(self.handle(line) for line in lines) + "\n"
                tmp = self.directory / "resp.tmp"
                tmp.write_text(reply)
                os.replace(tmp, self.directory / "resp")
            time.sleep(0.002)


@pytest.fixture
def fake(tmp_path: Path) -> Iterator[FakeMednafen]:
    server = FakeMednafen(tmp_path)
    server.thread.start()
    yield server
    server.stop.set()
    server.thread.join()


def test_bus_mapping() -> None:
    assert bus_to_space(0x060F9E66) == ("workramh", 0xF9E66)
    assert bus_to_space(0x260F9E66) == ("workramh", 0xF9E66)
    assert bus_to_space(0x002091AC) == ("workraml", 0x91AC)
    with pytest.raises(AgentError):
        bus_to_space(0x02400000)


def test_parse_pairs() -> None:
    assert parse_pairs("halted=1 pc=060AF724") == {"halted": "1", "pc": "060AF724"}


def test_status_regs_and_memory_round_trip(fake: FakeMednafen) -> None:
    agent = Agent(fake.directory, timeout=2.0)
    assert agent.halted()
    assert agent.regs()["R0"] == 0x00209290
    agent.bus_write(0x060F9E66, b"\x00\x06")
    assert agent.bus_read(0x060F9E64, 4) == b"\x00\x00\x00\x06"
    assert list(fake.directory.glob("read-*.bin")) == []


def test_err_lines_raise(fake: FakeMednafen) -> None:
    with pytest.raises(AgentError, match="unknown command"):
        Agent(fake.directory, timeout=2.0).command("bogus")


def test_timeout_without_server(tmp_path: Path) -> None:
    with pytest.raises(AgentError, match="no response"):
        Agent(tmp_path, timeout=0.05).command("status")


def test_parse_hit_line() -> None:
    from tools.mednafen.ko_capture import parse_hit

    line = "hit n=2 frame=900 mode=log PC=060AF728 RPC=060AF72C R0=00000020 R1=060F249E"
    assert parse_hit(line) == {
        "n": 2,
        "frame": 900,
        "PC": 0x060AF728,
        "R0": 0x20,
        "R1": 0x060F249E,
    }
    assert parse_hit("action frame=1 pc=0 write workramh") is None
