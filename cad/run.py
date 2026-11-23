import itertools, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build123d import *
import packmodel as pack

out = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(out, exist_ok=True)
parts = pack.build()

# interference check (volume of pairwise intersection)
bad = []
names = list(parts)
for a, b in itertools.combinations(names, 2):
    pa, pb = parts[a], parts[b]
    ba, bb = pa.bounding_box(), pb.bounding_box()
    if (ba.min.X > bb.max.X or bb.min.X > ba.max.X or ba.min.Y > bb.max.Y or bb.min.Y > ba.max.Y
            or ba.min.Z > bb.max.Z or bb.min.Z > ba.max.Z):
        continue
    v = (pa & pb).volume
    if v > 1e-3:
        bad.append((a, b, round(v, 2)))
print("interferences:", bad if bad else "none")

for n, p in parts.items():
    print(f"{n:18s} vol={p.volume/1000:8.1f} cm3  bbox={p.bounding_box().size}")

asm = Compound(label="pack_1kwh", children=[p for p in parts.values()])
export_step(asm, os.path.join(out, "pack_assembly.step"))
for n in ["shell_5052", "lid_5052", "carrier_mjf_pa12", "liner_formex", "busbar_1", "power_pcb", "bms_pcb"]:
    export_step(Compound(children=[parts[n]]), os.path.join(out, f"{n}.step"))
for n, p in parts.items():
    export_stl(p, os.path.join(out, "stl", f"{n}.stl")) if os.makedirs(os.path.join(out, "stl"), exist_ok=True) is None else None
export_stl(pack.cutaway(parts["shell_5052"]), os.path.join(out, "stl_cut", "shell_5052.stl")) if os.makedirs(os.path.join(out, "stl_cut"), exist_ok=True) is None else None
export_stl(pack.cutaway(parts["liner_formex"]), os.path.join(out, "stl_cut", "liner_formex.stl"))
print("exported"); print("SHELL_H", pack.SHELL_H, "z_pwr", pack.z_pwr, "z_bms", pack.z_bms)
