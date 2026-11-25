"""Render a concept: python shoot.py <key> [view ...]   views: iso, top, front, lid"""
import json, os, sys
from render import shot, OUT
key = sys.argv[1]; views = sys.argv[2:] or ["iso", "top"]
meta = json.load(open(os.path.join(OUT, key, "meta.json")))
roles = meta["roles"]; roles.update({k: "path" for k in ("path_pos", "path_neg")})
labels = [tuple(l) for l in meta["labels"]]
V = {"iso": dict(view=(0.75, -0.85, 1.15), focal=(100, 0, 235), dist=430),
     "iso2": dict(view=(-0.55, -1.0, 0.75), focal=(100, 5, 245), dist=470),
     "top": dict(view=(0.0, 0.0, 1.0), focal=(95, 5, 240), dist=520, up=(1, 0, 0)),
     "xray": dict(view=(0.75, -0.85, 1.15), focal=(100, 0, 235), dist=430,
                  xray=("contactor", "sb175_housing", "mrbf", "bs2151_body", "bs5191_body", "shunt_module", "g10_sb_cheek", "charger", "fet_parts", "fet_driver")),
     "front": dict(view=(1.0, -0.12, 0.18), focal=(100, 5, 250), dist=520),
     "side": dict(view=(0.0, -1.0, 0.12), focal=(100, 5, 255), dist=520),
     "lid": dict(view=(1.0, -0.95, 0.85), focal=(100, 5, 265), dist=560)}
sub = "Claude battery pack, power-bay concept study 2026-11-24 | fast render | lid removed" 
for v in views:
    kw = dict(V[v])
    extra = {}
    if v == "lid":
        extra = dict(ghost_lid=True)
    f = shot(key, roles, labels, f"{key}_{v}.png", meta["title"], sub if v != "lid" else sub.replace("lid removed", "lid shown transparent"),
             hide=("inverter", "tray2", "body_half_A", "ledboard_f", "ctrl_", "cap_") if v in ("iso", "top", "iso2", "xray") else (), **kw, **extra)
    print(f)
