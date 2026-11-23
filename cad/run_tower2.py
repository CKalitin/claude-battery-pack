import itertools, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tower2 as t2
from build123d import *

t0 = time.time()
parts = t2.build()
print(f"built {len(parts)} parts in {time.time()-t0:.1f}s;  H_body={t2.H:.1f}  LEDs={t2.led_count()}")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_tower2")
os.makedirs(os.path.join(out, "stl"), exist_ok=True)

# pairs that are supposed to touch / nest (fastener in hole, cable into terminal, riser onto board, etc.)
ALLOW_PREFIX = [("screws_f", "plate_front"), ("screws_r", "plate_rear"), ("screws_f", "tabs_f"), ("screws_r", "tabs_r"),
                ("screws_f", "pem_tab_f"), ("screws_r", "pem_tab_r"), ("feet_", "plate_"), ("pipe_f", "plate_front"),
                ("screws_lid", "u_body"), ("screws_lid", "lid"), ("screws_lid", "pem_lid"),
                ("screws_hold", "u_body"), ("screws_hold", "int_g10_floor"), ("screws_hold", "int_tnuts"), ("int_tnuts", "int_comp_endplates"), ("int_so_studs", "int_comp_endplates"), ("int_so_studs", "int_tnuts"), ("int_so_studs", "int_comp_pcb_standoffs"), ("int_so_upper", "int_comp_pcb_standoffs"), ("int_so_upper", "int_g10_top"), ("int_so_upper", "tray1"), ("int_so_upper", "screws_trays"), ("int_so_upper", "mica_tray"), ("screws_hold", "int_comp_endplates"), ("screws_hold", "int_liner"),
                ("int_comp_rods", "int_comp_endplates"), ("int_comp_rods", "int_comp_rodnuts"),
                ("int_comp_pcb_standoffs", "int_comp_endplates"), ("int_comp_pcb_standoffs", "tray1"),
                ("screws_trays", "tray"), ("screws_trays", "int_comp_pcb_standoffs"), ("screws_trays", "inv_posts"),
                ("screws_trays", "cb_standoffs"), ("screws_trays", "ctrl_pcb"), ("screws_trays", "charger"), ("screws_trays", "inverter"),
                ("inv_posts", "tray"), ("cb_standoffs", "tray1"), ("cb_standoffs", "ctrl_pcb"),
                ("int_busbar_screws", "int_busbar"), ("int_busbar_screws", "int_cell"), ("int_busbar_screws", "int_pack_neg_return"),
                ("int_pack_neg_return", "int_busbar"), ("int_pack_neg_return", "int_flex_ccs"), ("int_pack_pos_riser", "int_busbar"),
                ("int_pack_pos_riser", "ctrl_pcb"), ("int_pack_neg_return", "ctrl_pcb"),
                ("panel_", "lid"), ("screws_panel", "lid"), ("screws_panel", "panel_"),
                ("ctrl_", "ctrl_pcb"), ("cable_", ""), ("screws_fan", "fan_"), ("pem_tray1", "tray1"), ("pem_tray1", "screws_trays"), ("pem_tray1", "ctrl_pcb"), ("pem_tray1", "cb_standoffs"), ("pem_tray1", "inv_posts"), ("pem_tray1", "mica_tray"), ("pem_lid_panel", "lid"), ("pem_lid_panel", "screws_panel"), ("pem_lid_panel", "panel_"), ("screws_fan", "plate_rear")]

def allowed(a, b):
    for p, q in ALLOW_PREFIX:
        if (a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)):
            return True
    return False

bad = []
for a, b in itertools.combinations(parts, 2):
    if allowed(a, b):
        continue
    ba, bb = parts[a].bounding_box(), parts[b].bounding_box()
    if (ba.min.X >= bb.max.X or bb.min.X >= ba.max.X or ba.min.Y >= bb.max.Y or bb.min.Y >= ba.max.Y
            or ba.min.Z >= bb.max.Z or bb.min.Z >= ba.max.Z):
        continue
    try:
        v = (parts[a] & parts[b]).volume
    except Exception:
        v = -1
    if abs(v) > 0.5:
        bad.append((a, b, round(v, 1)))
print("interferences:", bad if bad else "none")

# cables: report what each cable passes through other than its endpoints' parts (informational)
for n in [k for k in parts if k.startswith("cable_")]:
    hits = []
    for m, q in parts.items():
        if m == n or m.startswith(("cable_",)):
            continue
        bq, bc = q.bounding_box(), parts[n].bounding_box()
        if (bq.min.X >= bc.max.X or bc.min.X >= bq.max.X or bq.min.Y >= bc.max.Y or bc.min.Y >= bq.max.Y
                or bq.min.Z >= bc.max.Z or bc.min.Z >= bq.max.Z):
            continue
        try:
            v = (parts[n] & q).volume
        except Exception:
            v = -1
        if abs(v) > 2:
            hits.append((m, round(v)))
    print(f"  {n}: touches {hits}")

for n, p in parts.items():
    export_stl(p, os.path.join(out, "stl", f"{n}.stl"), tolerance=0.05, angular_tolerance=0.15)
export_step(Compound(label="tower_a_v4", children=list(parts.values())), os.path.join(out, "tower_a_v4_assembly.step"))
bb = Compound(children=list(parts.values())).bounding_box()
print("overall", [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], f"total {time.time()-t0:.1f}s")
