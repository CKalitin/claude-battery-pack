"""v16 assembly = tower15 shell/converters/terminals (v15 power bay removed) + C1 power module (gv14up).
Writes versions/v16-c1-power-module/claude_battery_pack_v16_assembly.step. Checks live in run_tower15.py and
concepts/contactor/c1_power_module.py (interference, clearance, keep-outs, fuse lift-out)."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
import tower15 as t5
from build123d import Compound, export_step
from c1_power_module import build as c1
BAY = ("bus_pack_pos", "bus_pack_neg", "bus_link", "bus_neg_out", "bus_pos_out", "mrbf", "contactor", "shunt",
       "sb175", "g10_sb_bracket", "tray1_g10", "cable_", "keepout_")
t0 = time.time()
parts = {k: v for k, v in t5.build().items() if not k.startswith(BAY)}
c = c1("gv14up")
parts.update({f"c1_{k}": v for k, v in c.parts.items() if not k.startswith(("path_", "cap_"))})
for k, v in parts.items():
    v.label = k
out = os.path.join(HERE, "..", "versions", "v16-c1-power-module", "claude_battery_pack_v16_assembly.step")
export_step(Compound(list(parts.values())), out)
print(f"{len(parts)} parts -> {out} in {time.time()-t0:.0f}s")
