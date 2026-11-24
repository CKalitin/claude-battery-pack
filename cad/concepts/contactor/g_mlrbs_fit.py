"""Concept G: Blue Sea ML-RBS 7713 standing on tray 1, knob up through the lid (manual LOCKED-OFF = service disconnect).
Fit scan: every x/y position on a 5 mm grid, both orientations; count positions with no interference against the
context (walls, lid panel parts, front PCB parts, charger, inverter, upper standoffs).
Outline from the Blue Sea spec sheet (6834 rev 007): 138.9 x 76.2 x 95.3 mm overall UNCONFIRMED which axis is which."""
import json
from lib import *
L, W, H = 138.9, 76.2, 95.25
C = ctx(("body_half", "panel_", "pem_", "screws_lid", "ctrl_", "ledboard_f", "charger", "inverter", "tray2", "so_upper", "antenna"))
bbs = {k: v.bounding_box() for k, v in C.items()}
ok = []
z0 = Z_TRAY_TOP
for rot in (0, 1):
    lx, ly = (L, W) if rot == 0 else (W, L)
    for x in range(50, 171, 5):
        for y in range(-93, 94, 5):
            b = box(x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2, z0, z0 + H)
            bb = b.bounding_box()
            if bb.max.Z > Z_LID_IN + 25:      # knob may pass the lid; body must stay under it
                continue
            hit = False
            for k, s in C.items():
                if bb_overlap(bb, bbs[k]) and (b & s).volume > 0.5:
                    hit = True; break
            if not hit:
                ok.append((rot, x, y))
print(json.dumps({"fits": len(ok), "positions": ok[:20], "top_of_body": round(z0 + H, 1), "lid_inner": round(Z_LID_IN, 1)}))
