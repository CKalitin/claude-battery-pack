import itertools, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import *
import tower

t0 = time.time()
parts = tower.build()
print(f"built {len(parts)} parts in {time.time()-t0:.1f}s")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_tower")
os.makedirs(os.path.join(out, "stl"), exist_ok=True)

# interference check on bbox-overlapping pairs; skip pairs that are meant to touch/nest
ALLOWED = {frozenset(p) for p in [("screws_f", "plate_front"), ("screws_r", "plate_rear"),
                                  ("screws_f", "tabs_f"), ("screws_r", "tabs_r"),
                                  ("screws_f", "pem_tab_f"), ("screws_r", "pem_tab_r"),
                                  ("feet_f", "plate_front"), ("feet_r", "plate_rear"),
                                  ("pipe_f", "plate_front"), ("pipe_r", "plate_rear"),
 ("screws_lid", "u_body"), ("screws_lid", "lid"), ("screws_lid", "pem_lid"), ("screws_hold", "u_body"), ("screws_hold", "int_carrier_mjf_pa12"), ("screws_hold", "int_comp_endplates"), ("screws_hold", "int_liner_formex"),
 ("int_comp_rods", "int_comp_endplates"), ("int_comp_rods", "int_comp_rodnuts"), ("int_comp_pcb_standoffs", "int_comp_endplates"), ("int_comp_pcb_standoffs", "int_power_pcb")]}
bad = []
for a, b in itertools.combinations(parts, 2):
    if frozenset((a, b)) in ALLOWED:
        continue
    ba, bb = parts[a].bounding_box(), parts[b].bounding_box()
    if (ba.min.X >= bb.max.X or bb.min.X >= ba.max.X or ba.min.Y >= bb.max.Y or bb.min.Y >= ba.max.Y
            or ba.min.Z >= bb.max.Z or bb.min.Z >= ba.max.Z):
        continue
    try:
        v = (parts[a] & parts[b]).volume
    except Exception as e:
        v = -1
    if abs(v) > 0.5:
        bad.append((a, b, round(v, 1)))
print("interferences:", bad if bad else "none")

for n, p in parts.items():
    export_stl(p, os.path.join(out, "stl", f"{n}.stl"), tolerance=0.05, angular_tolerance=0.15)
asm = Compound(label="tower_a", children=[p for p in parts.values()])
export_step(asm, os.path.join(out, "tower_a_assembly.step"))
for n in ("plate_front", "u_body", "lid"):
    export_step(Compound(children=[parts[n]]), os.path.join(out, f"{n}.step"))
bb = asm.bounding_box()
print("overall", [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], f"total {time.time()-t0:.1f}s")
