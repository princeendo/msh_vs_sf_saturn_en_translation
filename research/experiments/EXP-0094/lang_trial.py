"""Language-word trial on a real win quote: f7980, control vs 0x060F4C90 = 1."""

from pathlib import Path

from tools.mednafen.agent import Agent

S = Path("local/re049/play/rec/states")
agent = Agent(Path("local/mednafen/agent").resolve(), 10)
for name, writes in (
    ("control", []),
    ("lang4C90", [(0x060F4C90, b"\x00\x01")]),
    ("lang_both", [(0x060F4C8E, b"\x00\x01"), (0x060F4C90, b"\x00\x01")]),
):
    for kind in ("write", "read", "pc"):
        agent.breakpoints(kind)
    if agent.halted():
        agent.run()
    agent.loadstate(S / "f00007980.mcs")
    agent.pause()
    agent.wait_halted(10)
    for address, data in writes:
        agent.bus_write(address, data)
    for at in (120, 240):
        agent.frames(120)
        agent.wait_halted(30)
        agent.screenshot(Path(f"local/re049/{name}_f{at}.png"))
    print(name, [(hex(a), agent.bus_read(a, 2).hex()) for a, _ in writes])
