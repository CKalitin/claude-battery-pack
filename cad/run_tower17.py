"""v17 (option D) build + pairwise interference check + STEP / STL export (cad/out_tower17/, gitignored; the STEP is
also written to versions/v17-option-d/). Every ALLOW entry is justified; anything else that overlaps is a failure.
Run: ~/.venvs/cad/bin/python cad/run_tower17.py [--fast]   (--fast: check only, no export)"""
import itertools, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tower17 as t
from build123d import Compound, export_step, export_stl

# (prefix A, prefix B, why the two solids are allowed to overlap)
ALLOW = [
    ("pipe_f", "plate_front", "light pipe press-fit in the 3.2 mm slot"),
    ("screws_term", "cell_", "M4 into the cell pole thread"),
    ("rods", "rodnuts", "M6 rod in nut"),
    ("flex_ccs", "bms_hdr_j1", "flex tail seated in the J1 FPC connector"),
    ("bs2151_", "bs2151_", "purchased block: its own internal parts"),
    ("bs5191_", "bs5191_", "purchased block: its own internal parts"),
    ("w_p1a", "term_chg_tb", "ferrule in the charger TB"),
    ("w_p2", "term_chg_tb", "ferrule in the charger TB"),
    ("w_p1b", "plug_relay_87", "into receptacle 87"),
    ("w_p4", "plug_pp45_neg", "in PP45"),
    ("w_shunt_pigtail", "shunt_pcb", "pigtail soldered to the module PCB"),
    ("w_h2_gnd", "w_ring_gnd", "crimp"),
    ("w_h2_load_a", "w_ring_load", "crimp"),
    ("w_h2_bplus_a", "w_ring_bplus", "crimp"),
    ("w_h3_coil", "contactor", "flying leads leave the contactor's notch"),
    ("w_h3_relay", "plug_j6", "into J6"),
    ("w_h3_relay", "w_h3_relay", "one cable splitting at the relay"),
    ("w_h5_acsense", "w_h3_relay", "AC-sense core in the same J6 cable"),
    ("w_h5_acsense", "w_p1a", "piggyback shares pin 30 with the charger + lead"),
    ("w_h3_cn301", "plug_j7", "into J7"),
    ("w_h4_btn", "panel_pushbutton", "button terminals"),
    ("w_h4_led", "plug_j5", "into J5"),
    ("w_h4_ntc", "plug_j9", "into J9"),
    ("w_a1_ac_in", "plug_c13", "cord into the right-angle C13"),
    ("w_a1_ac_in", "panel_inlet", "FASTONs on the inlet"),
    ("w_a2_ac_out", "plug_cn500", "into CN500"),
    ("w_a2_ac_out", "panel_outlet", "on the outlet terminals"),
    ("w_a3_pe_in", "panel_inlet", "PE FASTON"),
    ("w_a3_pe_out", "panel_outlet", "ground terminal"),
    ("w_a3_pe", "w_a3_pe", "PE splice into one lug barrel"),
    ("w_a3_pe_trunk", "w_pe_barrel", "crimp"),
]

def allowed(a, b):
    return any((a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)) for p, q, _ in ALLOW)

def overlap(ba, bb):
    return not (ba.min.X >= bb.max.X or bb.min.X >= ba.max.X or ba.min.Y >= bb.max.Y or bb.min.Y >= ba.max.Y
                or ba.min.Z >= bb.max.Z or bb.min.Z >= ba.max.Z)

def interferences(parts):
    bbs = {k: v.bounding_box() for k, v in parts.items()}
    sols = {k: [(s, s.bounding_box()) for s in v.solids()] for k, v in parts.items()}
    bad, used = [], set()
    for a, b in itertools.combinations(parts, 2):
        if not overlap(bbs[a], bbs[b]):
            continue
        v = 0.0
        for sa, ba in sols[a]:                      # solid by solid: compounds of many solids are slow and unreliable
            if not overlap(ba, bbs[b]):
                continue
            for sb, bb in sols[b]:
                if not overlap(ba, bb):
                    continue
                try:
                    x = sa & sb
                    v += x.volume if x is not None else 0.0
                except Exception as e:
                    v += 1e9
        if v > 0.5:
            if allowed(a, b):
                for p, q, _ in ALLOW:
                    if (a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)):
                        used.add((p, q)); break
            else:
                bad.append((a, b, round(v, 1)))
    return bad, used

if __name__ == "__main__":
    t0 = time.time()
    parts = t.build()
    print(f"built {len(parts)} parts in {time.time() - t0:.0f} s", flush=True)
    bad, used = interferences(parts)
    print(f"interferences ({len(bad)}):" if bad else "interferences: none")
    for x in bad:
        print("   ", x)
    unused = [(p, q) for p, q, _ in ALLOW if (p, q) not in used]
    print(f"allow entries used {len(used)} of {len(ALLOW)}; unused: {unused}")
    print(f"check done at {time.time() - t0:.0f} s", flush=True)
    if "--fast" in sys.argv:
        sys.exit()
    OUT = os.path.join(HERE, "out_tower17" + (("_" + t.VARIANT) if t.VARIANT else "")); stl = os.path.join(OUT, "stl")
    os.makedirs(stl, exist_ok=True)
    for f in os.listdir(stl):
        os.remove(os.path.join(stl, f))
    for n, s in parts.items():
        s.label = n
        export_stl(s, os.path.join(stl, f"{n}.stl"), tolerance=0.05, angular_tolerance=0.15)
    ver = os.path.join(HERE, "..", "versions", "v17-option-d"); os.makedirs(ver, exist_ok=True)
    if not t.VARIANT:
      export_step(Compound(label="claude_battery_pack_v17_assembly", children=list(parts.values())),
                os.path.join(ver, "claude_battery_pack_v17_assembly.step"))
    bb = Compound(children=[v for v in parts.values()]).bounding_box()
    print("overall", [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], f"total {time.time() - t0:.0f} s")
