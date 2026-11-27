"""C1 power module, level by level: one exploded view + one top view per level."""
import json, os
from render import shot, OUT
key = "c1_module_gv14up"
meta = json.load(open(os.path.join(OUT, key, "meta.json")))
roles = meta["roles"]
L0 = ("bus_pack_pos", "bus_pack_neg")
L1 = ("tray1",)
L2 = ("g10_plate", "standoff_", "nut_m8")
L3 = ("bus_mod_in", "bus_mod_load", "bus_mod_neg", "shunt_bar")
L4 = ("contactor", "sb175", "mrbf_main", "mrbf_branch", "shunt_module", "g10_sb_cheek")
LAB = [("bus_pack_pos", "Pack + collector + riser (cells 7-8)"), ("bus_pack_neg", "Pack - band + riser (from cells 1-2)"),
       ("bus_C", "Series bar (cell to cell, mid-potential)"), ("bus_B", "Series bar (cell to cell, mid-potential)"), ("tray1", "G10 tray 1 (open notches for the risers)"),
       ("g10_plate", "G10 module plate"), ("standoff_", "Standoffs to tray 1"), ("nut_m8", "Contactor stud nuts (under plate)"),
       ("bus_mod_in", "+ in-bar (MRBF -> contactor T1)"), ("bus_mod_load", "+ load bar (T2 -> SB175 +, branch tab)"),
       ("bus_mod_neg", "- tab (shunt -> SB175 -)"), ("shunt_bar", "Tesla shunt bar"),
       ("contactor", "Contactor GV141BAX, upside-down"), ("sb175_housing", "SB175 housing (mates from above)"),
       ("mrbf_main", "MRBF 250 A main fuse"), ("mrbf_branch", "Dual MRBF: charger 30 A, inverter 50 A"),
       ("shunt_module", "Shunt sensing board"), ("g10_sb_cheek", "G10 cheeks holding the SB175"), ("cell_8", "Cells")]
sub = "true plan view (no perspective) | front of pack (+x) at top, -y wall on the right | faint outline = G10 module plate (level 2)"
TOP = dict(view=(0.0, 0.0, 1.0), focal=(102, 0, 240), dist=600, up=(1, 0, 0), parallel=82)
shots = [
    ("lvl0_pack_copper", "Level 0: pack copper on the cells (z 207-210, risers up to 238)", L0, ("cell_", "bus_A", "bus_B", "bus_C")),
    ("lvl1_tray", "Level 1: G10 tray 1 (z 218.5-221.6)", L1 + L0, ("cell_",)),
    ("lvl2_plate", "Level 2: G10 module plate on standoffs (z 232.0-235.1)", L2, ()),
    ("lvl3_copper", "Level 3: module copper, ONE flat plane (z 235.1-238.3)", L3 + ("bus_pack_pos", "bus_pack_neg"), ()),
    ("lvl4_parts", "Level 4: parts standing on the copper, terminals down", L4, ()),
]
for fn, title, only, ctx_only in shots:
    ghost = ("bus_pack", "g10_plate") if fn == "lvl1_tray" else (() if fn == "lvl2_plate" else ("g10_plate",))
    only2 = only + (("g10_plate",) if fn != "lvl2_plate" else ())
    print(shot(key, roles, LAB, f"{key}_{fn}.png", title, sub, only=only2, ctx_only=ctx_only, ghost=ghost, **TOP))
# exploded: each level lifted so all five are visible at once
EX = {"bus_pack": 0, "tray1": 35, "g10_plate": 120, "standoff_": 120, "nut_m8": 120, "bus_mod": 190, "shunt_bar": 190,
      "contactor": 270, "sb175": 270, "mrbf": 270, "shunt_module": 270, "g10_sb_cheek": 270}
print(shot(key, roles, LAB, f"{key}_exploded.png", "C1 power module, exploded by level",
           "levels lifted apart: 0 pack copper | 1 tray | 2 plate | 3 copper plane | 4 parts | risers belong to level 0 and reach level 3",
           only=L0 + tuple(x for x in L1) + L2 + L3 + L4, hide=("tray1",) if False else (), ctx_only=("cell_7", "cell_8", "cell_6", "cell_5"), explode=EX,
           view=(1.0, -1.1, 0.6), focal=(95, -10, 360), dist=820, size=(1600, 1800)))
