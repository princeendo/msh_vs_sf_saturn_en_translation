"""Client for the patched Mednafen agent interface (`EMU-020`).

The patched binary (``vendor/mednafen/build-agent``) polls ``$MEDNAFEN_AGENT_DIR``
on its game thread, every frame and while halted:

1. The client writes the ``cmd`` file atomically, first line ``id <token>``.
2. Mednafen deletes ``cmd``, runs each line, and writes ``resp`` atomically:
   ``id <token>``, then one ``ok …`` / ``err …`` line per command.
3. Breakpoint hits and post-hit actions are appended to ``events.log``.

See ``docs/mednafen_agent_interface.md`` for the command list.
"""

from __future__ import annotations

import argparse
import fcntl
import os
import time
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DIR = Path("local/mednafen/agent")
REGIONS = (  # (bus base, size, address space); cache-through mirrors add 0x20000000
    (0x00200000, 0x100000, "workraml"),
    (0x06000000, 0x100000, "workramh"),
)


class AgentError(RuntimeError):
    pass


def bus_to_space(address: int) -> tuple[str, int]:
    """Map a Saturn bus address in work RAM to (address space, offset)."""
    plain = address & ~0x20000000
    for base, size, space in REGIONS:
        if base <= plain < base + size:
            return space, plain - base
    raise AgentError(f"0x{address:08X} is not in work RAM")


def parse_pairs(text: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in text.split() if "=" in item)


@dataclass
class Agent:
    directory: Path = DEFAULT_DIR
    timeout: float = 10.0
    poll: float = 0.01

    def command(self, *lines: str) -> list[str]:
        """Send commands; return the ``ok`` payloads. Raises on any ``err``.

        An exclusive lock on ``lock`` in the agent directory serialises clients,
        so a recorder and a driver can share one Mednafen (END-010).
        """
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / "lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                return self._exchange(lines)
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _exchange(self, lines: Sequence[str]) -> list[str]:
        token = uuid.uuid4().hex[:12]
        resp = self.directory / "resp"
        resp.unlink(missing_ok=True)
        tmp = self.directory / "cmd.tmp"
        tmp.write_text("\n".join([f"id {token}", *lines]) + "\n")
        os.replace(tmp, self.directory / "cmd")
        deadline = time.monotonic() + self.timeout
        while not resp.exists():
            if time.monotonic() > deadline:
                raise AgentError(f"no response within {self.timeout} s to {lines!r}")
            time.sleep(self.poll)
        reply = resp.read_text().splitlines()
        resp.unlink()
        if not reply or reply[0] != f"id {token}":
            raise AgentError(f"mismatched response: {reply[:1]!r}")
        results = []
        for line in reply[1:]:
            if line.startswith("err"):
                raise AgentError(line)
            results.append(line[3:] if line.startswith("ok ") else line)
        return results

    # Queries
    def status(self) -> dict[str, str]:
        return parse_pairs(self.command("status")[0])

    def halted(self) -> bool:
        return self.status().get("halted") == "1"

    def regs(self) -> dict[str, int]:
        return {k: int(v, 16) for k, v in parse_pairs(self.command("regs")[0]).items()}

    def spaces(self) -> list[str]:
        return self.command("spaces")[0].split()

    # Memory
    def read(self, space: str, address: int, length: int) -> bytes:
        target = (self.directory / f"read-{uuid.uuid4().hex[:8]}.bin").resolve()
        try:
            self.command(f"read {space} {address:X} {length} {target}")
            return target.read_bytes()
        finally:
            target.unlink(missing_ok=True)

    def write(self, space: str, address: int, data: bytes) -> None:
        self.command(f"write {space} {address:X} {data.hex().upper()}")

    def bus_read(self, address: int, length: int) -> bytes:
        space, offset = bus_to_space(address)
        return self.read(space, offset, length)

    def bus_write(self, address: int, data: bytes) -> None:
        space, offset = bus_to_space(address)
        self.write(space, offset, data)

    # Breakpoints
    def breakpoints(self, kind: str, ranges: Sequence[str] = ()) -> None:
        self.command(f"bp {kind} {' '.join(ranges)}".rstrip())

    def bpmode(self, mode: str) -> None:
        self.command(f"bpmode {mode}")

    def onhit_write(self, pc: int | None, address: int, data: bytes) -> None:
        space, offset = bus_to_space(address)
        flt = "any" if pc is None else f"{pc:08X}"
        self.command(f"onhit {flt} write {space} {offset:X} {data.hex().upper()}")

    def onhit_clear(self) -> None:
        self.command("onhit clear")

    def events(self) -> list[str]:
        path = self.directory / "events.log"
        return path.read_text().splitlines() if path.exists() else []

    def clear_events(self) -> None:
        (self.directory / "events.log").unlink(missing_ok=True)

    # Execution
    def pause(self) -> None:
        self.command("pause")

    def step(self) -> None:
        self.command("step")

    def run(self) -> None:
        self.command("run")

    def frames(self, count: int) -> None:
        self.command(f"frames {count}")

    def wait_halted(self, timeout: float = 30.0) -> dict[str, str]:
        deadline = time.monotonic() + timeout
        while True:
            status = self.status()
            if status.get("halted") == "1":
                return status
            if time.monotonic() > deadline:
                raise AgentError(f"not halted within {timeout} s: {status}")
            time.sleep(0.05)

    # Files
    def savestate(self, path: Path) -> None:
        self.command(f"savestate {path.resolve()}")

    def loadstate(self, path: Path) -> None:
        self.command(f"loadstate {path.resolve()}")

    def screenshot(self, path: Path) -> None:
        self.command(f"screenshot {path.resolve()}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send raw commands to the agent.")
    parser.add_argument("commands", nargs="+", help="one quoted command per argument")
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    try:
        for line in Agent(args.dir, args.timeout).command(*args.commands):
            print(line)
    except AgentError as error:
        parser.exit(1, f"{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
