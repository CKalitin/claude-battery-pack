import itertools, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tower15 as t5
from build123d import *

t0 = time.time()
parts = t5.build()
print(f"built {len(parts)} parts in {time.time()-t0:.1f}s")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_tower15")
os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)

ALLOW = [("screws_f", "plate_front"), ("screws_f", "body_half"), ("screws_r", "plate_rear"), ("screws_r", "body_half"),
         ("screws_fan", "plate_rear"), ("screws_fan", "fan_"), ("feet", "plate_"), ("pipe_f", "plate_front"),
         ("screws_lid", "lid"), ("screws_lid", "body_half"), ("screws_lid", "pem_body_lid"), ("pem_body_lid", "body_half"),
         ("screws_hold", "body_half"), ("screws_hold", "g10_floor"), ("screws_hold", "tnuts"), ("screws_hold", "module_endplates"),
         ("tnuts", "module_endplates"), ("so_studs", "module_endplates"), ("so_studs", "tnuts"), ("so_studs", "so_lower"),
         ("so_upper", "so_lower"), ("so_upper", "g10_top"), ("so_upper", "screws_trays"), ("so_lower", "module_endplates"),
         ("rods", "module_endplates"), ("rods", "rodnuts"),
         ("screws_term", "bus_"), ("screws_term", "cell_"), ("bus_", "cell_"),
         ("bus_pack", "ctrl_pcb"), ("bus_pack", "flex_ccs"), ("flex_ccs", "ctrl_ccs_conn"), ("flex_ccs", "bus_"),
         ("screws_trays", "tray"), ("screws_trays", "inv_posts"), ("screws_trays", "ctrl_pcb"), ("screws_trays", "charger"),
         ("screws_trays", "inverter"), ("screws_trays", "pem_tray1"), ("screws_trays", "mylar"),
         ("inv_posts", "tray"), ("pem_tray1", "tray1"), ("pem_tray1", "ctrl_pcb"), ("pem_tray1", "inv_posts"), ("pem_tray1", "mylar"),
         ("panel_", "lid"), ("screws_panel", "lid"), ("screws_panel", "panel_"), ("screws_panel", "pem_lid_panel"),
         ("pem_lid_panel", "lid"), ("pem_lid_panel", "panel_"), ("ctrl_", "ctrl_pcb"), ("cable_", ""), ("g10_spacers", "cell_"), ("screws_strap", "bus_pack"), ("screws_strap", "ctrl_pcb"), ("cb_standoffs", "module_endplates"), ("cb_standoffs", "ctrl_pcb"), ("screws_trays", "cb_standoffs"), ("flex_ccs", "ctrl_ccs_conn"), ("cb_standoffs", "tray1"), ("screws_trays", "cb_standoffs"), ("screws_strap", "bus_pack"), ("screws_hold", "pem_tray1"),
         ("screws_tap", "bus_"), ("screws_tap", "flex_ccs"), ("flex_ccs", "bus_"), ("panel_standoffs", "module_endplates"), ("panel_standoffs", "ledboard_f"),
         ("screws_panelmount", "diffuser_f"), ("screws_panelmount", "ledboard_f"), ("screws_panelmount", "panel_standoffs"),
         ("bus_pack", "fuse_jjn500"), ("bus_pack", "shunt_bar"), ("bus_line", "fuse_jjn500"), ("bus_line", "contactor_ev200"), ("bus_load", "contactor_ev200"),
         ("term_pos", "contactor_ev200"), ("term_pos", "bus_load"), ("term_neg", "shunt_bar"), ("bus_load", "mrbf"),
         ("shunt_bar", "g10_power_deck"), ("shunt_module", "shunt_bar"), ("fuse_jjn500", "g10_power_deck"), ("g10_power_deck", "tray1"), ("contactor_ev200", "tray1"),
         ("cb_standoffs", "g10_power_deck"), ("term_", "lid"), ("term_plates", "lid"), ("term_plates", "term_"), ("flex_ccs", "tray1"), ("flex_ccs", "g10_power_deck"), ("flex_ccs", "ctrl_pcb"),
         ("antenna", "pipe_f"), ("bus_neg_out", "shunt_bar"), ("bus_neg_out", "sb175"), ("bus_pos_out", "sb175"), ("bus_pos_out", "contactor"), ("bus_pos_out", "mrbf_branch"), ("bus_link", "contactor"), ("bus_link", "mrbf_main"), ("bus_pack_pos", "mrbf_main"), ("g10_sb_bracket", "sb175"), ("g10_sb_bracket", "tray1"), ("contactor", "tray1"), ("ctrl_", "ledboard"), ("flex_ccs", "ctrl_ccs"), ("contactor", "mrbf_branch"), ("contactor_ev200", "mylar"), ("g10_power_deck", "mylar")]

def allowed(a, b):
    return any((a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)) for p, q in ALLOW)

def overlap(ba, bb):
    return not (ba.min.X >= bb.max.X or bb.min.X >= ba.max.X or ba.min.Y >= bb.max.Y or bb.min.Y >= ba.max.Y
                or ba.min.Z >= bb.max.Z or bb.min.Z >= ba.max.Z)

bbs = {k: v.bounding_box() for k, v in parts.items()}
bad = []
for a, b in itertools.combinations(parts, 2):
    if allowed(a, b) or not overlap(bbs[a], bbs[b]):
        continue
    try:
        v = (parts[a] & parts[b]).volume
    except Exception:
        v = -1
    if abs(v) > 0.5:
        bad.append((a, b, round(v, 1)))
print("interferences:", bad if bad else "none")
if "--fast" in sys.argv:
    sys.exit()
for n, p in parts.items():
    export_stl(p, os.path.join(OUT, "stl", f"{n}.stl"), tolerance=0.05, angular_tolerance=0.15)
export_step(Compound(label="claude_battery_pack_v15", children=list(parts.values())), os.path.join(OUT, "claude_battery_pack_v15_assembly.step"))
bb = Compound(children=list(parts.values())).bounding_box()
print("overall", [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], f"total {time.time()-t0:.1f}s")
