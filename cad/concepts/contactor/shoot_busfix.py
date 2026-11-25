"""v16.2: the two pack busbars as bend-legal 1/8 in copper Zs."""
import json, os
from render import shot, OUT
key = "c1_module_gv14up"; meta = json.load(open(os.path.join(OUT, key, "meta.json")))
ONLY = ("bus_pack_pos", "bus_pack_neg", "bs5191", "hw_m10nut_main", "hw_carriage_0", "hw_carriage_head_0", "hw_carriage_1",
        "hw_carriage_head_1", "strap_main", "hw_nut_main", "bus_mod_in", "shunt_bar")
L = [("bus_pack_pos", "+ busbar: collector + Z (one part, 1/8 in Cu)"), ("bus_pack_neg", "− busbar: band + Z (one part, 1/8 in Cu)"),
     ("bs5191_body", "Blue Sea 5191 + MRBF (now points +y)"), ("strap_main", "Z-strap (shorter)"), ("shunt_bar", "Tesla shunt bar"),
     ("bus_mod_in", "in-bar")]
for fn, view, foc, dist in (("pack_busbars_fix.png", (0.9, -1.0, 0.55), (105, -45, 222), 300),
                            ("pack_busbars_fix_side.png", (0.0, -1.0, 0.12), (105, -45, 222), 300)):
    print(shot(key, meta["roles"], L, fn, "v16.2 pack busbars: two Z-bends each, no C",
               "SCS COP-125: R 0.050 in, flanges ≥ 12.0 mm, joggle 31.5 mm (≥ 12.9). Holes ≥ 8 mm from bend lines",
               view=view, focal=foc, dist=dist, only=ONLY, ctx_only=("cell",)))
