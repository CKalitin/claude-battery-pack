"""v15 clearance check: minimum air gap between opposite-potential copper, and between pack copper and chassis metal."""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tower15 as t
p = t.build()
POS = ["bus_pack_pos", "mrbf_main", "bus_link", "bus_pos_out", "mrbf_branch"]
NEG = ["bus_pack_neg", "shunt_bar", "bus_neg_out"]
MID = ["bus_A", "bus_B", "bus_C"]
CHASSIS = ["body_half_A", "body_half_B", "lid", "plate_front", "plate_rear", "module_endplates", "rods"]
def d(a, b):
    return p[a].distance_to(p[b])
rows = []
for a, b in itertools.product(POS, NEG):
    rows.append(("+ vs -", a, b, d(a, b)))
for a, b in itertools.product(POS + NEG, MID):
    rows.append(("pack vs series bar", a, b, d(a, b)))
for a, b in itertools.product(POS + NEG, CHASSIS):
    rows.append(("pack vs chassis", a, b, d(a, b)))
for kind in ("+ vs -", "pack vs series bar", "pack vs chassis"):
    sub = sorted([r for r in rows if r[0] == kind], key=lambda r: r[3])
    print(f"--- {kind}: minimum {sub[0][3]:.1f} mm")
    for r in sub[:6]:
        print(f"   {r[1]:14s} {r[2]:16s} {r[3]:6.1f} mm")
