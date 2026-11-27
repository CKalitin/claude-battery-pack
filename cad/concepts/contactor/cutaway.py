"""Section cutaways of the C1 module: what lies on what, bolts included."""
import json, os
from render import shot, OUT
key = "c1_module_gv14up"
meta = json.load(open(os.path.join(OUT, key, "meta.json")))
roles = meta["roles"]
LAB = [("contactor", "Contactor (upside-down, terminals on the copper)"), ("hw_stud_ct", "Contactor M8 studs"),
       ("nut_m8", "M8 nuts, under the plate"), ("bus_mod_in", "Copper: + in-bar (L3)"), ("bus_mod_load", "Copper: + load bar (L3)"),
       ("g10_plate", "G10 plate (L2): copper lies on it"), ("standoff_", "Standoff"), ("tray1", "G10 tray 1 (L1)"),
       ("bus_pack_pos", "Pack + collector on the cells (L0)"), ("bus_C", "Series bar (L0)"), ("cell_", "Cells"),
       ("sb175_housing", "SB175 housing"), ("sb175_contact", "SB175 busbar contacts"), ("hw_stud_sb", "1/4-20 contact studs"),
       ("hw_locknut", "Lock nuts, under the plate"), ("bus_mod_neg", "Copper: - tab (L3)"), ("shunt_bar", "Shunt bar (on the copper)"),
       ("g10_sb_cheek", "G10 cheek (holds the SB175)"), ("mrbf", "Branch MRBF"), ("flex_ccs", "Cell sense flex"), ("bus_B", "Series bar (L0)")]
only = None
print(shot(key, roles, LAB, f"{key}_cut_contactor.png", "Section through the contactor terminals (cut at x = 120, looking from the front)",
           "cut faces show solid material | copper bars lie directly on the G10 plate; contactor studs go down through both; nuts underneath",
           cut=((1, 0, 0), (120, 0, 0)), view=(1.0, -0.35, 0.28), focal=(120, 40, 245), dist=230, size=(1600, 1200),
           ctx_only=("cell_7", "cell_8", "bus_C", "bus_B", "flex_ccs", "g10_top"), hide=("path_",)))
print(shot(key, roles, LAB, f"{key}_cut_sb175.png", "Section through the SB175 contacts (cut at x = 70.7, looking from the front)",
           "the SB175 stands on the copper the same way: busbar contacts on the bars, studs through bar + plate, lock nuts underneath",
           cut=((1, 0, 0), (70.7, 0, 0)), view=(1.0, -0.35, 0.28), focal=(70, 35, 260), dist=260, size=(1600, 1200),
           ctx_only=("cell_6", "cell_7", "bus_C", "bus_B", "flex_ccs", "g10_top"), hide=("path_",)))
