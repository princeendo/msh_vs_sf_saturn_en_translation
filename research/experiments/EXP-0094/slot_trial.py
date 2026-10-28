"""RE-049 trials: does the quote task take the highest free 0xC0 pool slot?"""
import json, sys
from pathlib import Path
from tools.mednafen.agent import Agent
S = Path("local/re049/play/rec/states")
agent = Agent(Path("local/mednafen/agent").resolve(), 10)
leftover = Path("local/re049/dump_f00007980/wram_h.bin").read_bytes()[0xF9ED6:0xF9ED6 + 0xC0]
trials = {
    "A_win_control": ("f00007980.mcs", None),
    "B_win_free_9ED6": ("f00007980.mcs", bytes(0xC0)),
    "C_cpu_control": ("f00013145.mcs", None),
    "D_cpu_fill_9ED6": ("f00013145.mcs", leftover),
}
results = {}
agent.bpmode("halt")
for name, (state, slot) in trials.items():
    for kind in ("write", "read", "pc"):
        agent.breakpoints(kind)  # clear
    if agent.halted():
        agent.run()
    agent.loadstate(S / state)
    agent.pause()
    agent.wait_halted(10)
    if slot is not None:
        agent.bus_write(0x060F9ED6, slot)
    agent.breakpoints("pc", ["060AF724-060AF725"])
    agent.run()
    status = agent.wait_halted(60)
    regs = agent.regs()
    results[name] = {"frame": status["frame"], "r12": f"{regs['R12']:08X}", "r0": f"{regs['R0']:08X}"}
    print(name, results[name], flush=True)
agent.breakpoints("pc")
Path("local/re049/slot_trial.json").write_text(json.dumps(results, indent=1))
