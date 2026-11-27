"""Close-up renders of the 2151 block (no pack context)."""
import json, os, sys
from render import shot, OUT
key = "mrbf_2151_demo"
meta = json.load(open(os.path.join(OUT, key, "meta.json")))
R, L = meta["roles"], meta["labels"]
NOCTX = ("__none__",)
which = sys.argv[1:] or ["iso", "xray", "exploded"]
F = (30, 0, 22)
if "iso" in which:
    print(shot(key, R, L, "mrbf_2151_iso.png", "Blue Sea 2151 dual MRBF block on the + load bar",
               "assembled; insulating cap ghosted; outline from Blue Sea's drawing, internals inferred ⚠", view=(-0.55, -1.0, 0.75),
               focal=F, dist=210, ctx_only=NOCTX, hide=("path_",), ghost=("cap_",)))
if "xray" in which:
    print(shot(key, R, [("path_", "current path (yellow)"), ("bs2151_strap", "strap: bends up, runs under both fuses"),
                        ("bs2151_fuse_0_bot", "fuse bottom face (source)"), ("bs2151_fuse_1_top", "fuse top face (load)"),
                        ("bs2151_stud", "M8 stud: clamp only, no current"), ("lug_inverter", "lug on the fuse top"),
                        ("bar_load", "+ load bar")],
               "mrbf_2151_xray.png", "Where the contacts are: current path through the 2151",
               "bar → tab → strap → fuse bottom → element → fuse top → lug.  Body, fuses, nuts see-through", view=(-0.35, -1.0, 0.45),
               focal=F, dist=200, ctx_only=NOCTX, hide=("cap_", "cable_"), xray=("bs2151_body", "bs2151_fuse_0_body", "bs2151_fuse_1_body", "hw_")))
if "exploded" in which:
    ex = {"hw_m10_nut": 18.0, "bs2151": 30.0, "bs2151_fuse": 62.0, "lug_": 95.0, "hw_nut": 118.0, "cable_": 95.0}
    print(shot(key, R, L, "mrbf_2151_exploded.png", "2151 exploded: stack order on each stud",
               "bar, M10 nut | block (strap + body + studs) | MRBF fuses | lugs | washer + nut", view=(-0.55, -1.0, 0.45),
               focal=(30, 0, 70), dist=330, ctx_only=NOCTX, hide=("path_", "cap_"), explode=ex))
