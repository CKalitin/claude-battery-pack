"""List every SendCutSend part in v16, group identical solids (qty), export one STEP per unique part for the SCS quote.
Output: out_v16/scs/*.step + out_v16/scs/parts.csv"""
import os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
import tower15 as t5
from build123d import export_step
from c1_power_module import build as c1
IN = 25.4
# name prefix -> (SCS material, thickness in, process note)
MAT = [("body_half", "5052 aluminum", .063, "bend, powder coat red"), ("lid", "5052 aluminum", .063, "bend, powder coat red"),
       ("plate_front", "6061 aluminum", .187, "cut"), ("plate_rear", "6061 aluminum", .187, "cut"),
       ("module_endplates", "6061 aluminum", .313, "cut (+ tap)"),
       ("g10_floor", "G10", .187, "cut"), ("g10_frame", "G10", .187, "cut"), ("g10_top", "G10", .063, "cut"),
       ("g10_spacers", "G10", .063, "cut"), ("tray1", "G10", .125, "cut"), ("tray2", "G10", .125, "cut"),
       ("g10_plate", "G10", .125, "cut"), ("g10_sb_cheek", "G10", .125, "cut"),
       ("bus_A", "copper", .125, "cut"), ("bus_B", "copper", .125, "cut"), ("bus_C", "copper", .125, "cut"),
       ("bus_pack_pos", "copper", .187, "cut + bend"), ("bus_pack_neg", "copper", .187, "cut + bend"),
       ("bus_mod_in", "copper", .125, "cut"), ("bus_mod_load", "copper", .125, "cut"), ("bus_mod_neg", "copper", .125, "cut"),
       ("strap_main", "copper", .125, "cut + 2 bends"),
       ("diffuser_f", "white acrylic", .118, "cut"), ("pipe_f", "clear acrylic", .118, "cut")]
BAY = ("bus_pack_pos", "bus_pack_neg", "bus_link", "bus_neg_out", "bus_pos_out", "mrbf", "contactor", "shunt",
       "sb175", "g10_sb_bracket", "tray1_g10", "cable_", "keepout_")
parts = {k: v for k, v in t5.build().items() if not k.startswith(BAY)}
parts.update(c1("gv14up").parts)
out = os.path.join(HERE, "out_v16", "scs"); os.makedirs(out, exist_ok=True)
rows = []
for name, shape in parts.items():
    m = next((x for x in MAT if name.startswith(x[0])), None)
    if not m:
        continue
    groups = {}
    for s in shape.solids():
        b = s.bounding_box()
        key = (round(s.volume, 0), tuple(sorted((round(b.size.X, 1), round(b.size.Y, 1), round(b.size.Z, 1)))))
        groups.setdefault(key, []).append(s)
    for i, (key, ss) in enumerate(sorted(groups.items())):
        pn = f"{name}" + (f"_{i+1}" if len(groups) > 1 else "")
        f = os.path.join(out, f"{pn}.step"); export_step(ss[0], f)
        rows.append([pn, m[1], m[2], m[3], len(ss), *key[1], round(key[0] / 1000, 1)])
        print(pn, m[1], m[2], len(ss), key[1])
with open(os.path.join(out, "parts.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["part", "material", "thk_in", "process", "qty", "d1_mm", "d2_mm", "d3_mm", "vol_cm3"]); w.writerows(rows)
