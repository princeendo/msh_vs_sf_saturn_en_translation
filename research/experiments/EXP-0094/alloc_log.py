"""RE-049: log writes to each pool slot's first long from a state until the quote."""
import json, re
from pathlib import Path
from tools.mednafen.agent import Agent
S = Path("local/re049/play/rec/states")
agent = Agent(Path("local/mednafen/agent").resolve(), 10)
slots = range(0x060F9516, 0x060FA000, 0xC0)
ranges = [f"{s:08X}-{s+3:08X}" for s in slots]
out = {}
for name, state, frames in (("win", "f00007809.mcs", 260), ("cpu", "f00012972.mcs", 360)):
    for kind in ("write", "read", "pc"):
        agent.breakpoints(kind)
    if agent.halted():
        agent.run()
    agent.loadstate(S / state)
    agent.pause(); agent.wait_halted(10)
    agent.clear_events()
    agent.bpmode("log")
    agent.breakpoints("write", ranges)
    agent.frames(frames); agent.wait_halted(60)
    agent.breakpoints("write")
    agent.bpmode("halt")
    hits = []
    for line in agent.events():
        if line.startswith("hit "):
            d = dict(p.split("=", 1) for p in line.split()[1:] if "=" in p)
            hits.append({k: d.get(k) for k in ("frame", "PC", "PR", "R0", "R1", "R2", "R3", "R12", "R13", "R14")})
    out[name] = hits
    print(name, len(hits))
Path("local/re049/alloc_log.json").write_text(json.dumps(out, indent=1))
