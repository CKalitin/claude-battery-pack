"""Blue Sea 2151 dual MRBF terminal fuse block, stand-alone close-up: how it mounts and where current flows.

Same part models as C1 (lib.bs_block). Coordinates: M10 hole at the origin, block along +x, copper bar top at z = 3.175.
Lugs as in C1: charger lug (stud 0) leaves toward -x, inverter lug (stud 1) toward +x, both 90 deg (barrel up).
"""
import json, os, sys
from lib import *

def build():
    c = Concept("mrbf_2151_demo", "Blue Sea 2151 dual MRBF block")
    T = 3.175; z0 = T
    c.add("bar_load", box(-22.0, 22.0, -12.0, 12.0, 0.0, T) - cyl_z(0, 0, -1, T + 1, 5.25), "pos")
    c.add("hw_m10_head", cyl_z(0, 0, -5.6, 0.0, 12.5))                       # DIN 603 M10 carriage bolt (square neck in the bar)
    c.add("hw_m10_shank", cyl_z(0, 0, 0.0, z0 + 2.5 + 8.0 + 4.0, 5.0))
    c.add("hw_m10_nut", cyl_z(0, 0, z0 + 2.5, z0 + 2.5 + 8.0, 9.25) - cyl_z(0, 0, z0, z0 + 12, 5.0))
    parts, studs, ztop = bs_block("2151", 0.0, 0.0, z0, d=(1, 0), prefix="bs2151")
    for n, (s, r) in parts.items():
        c.add(n, s, r)
    for i, ((x, y), d, nm) in enumerate(zip(studs, ((-1, 0), (1, 0)), ("charger", "inverter"))):
        lug, top = lug90(x, y, ztop, d=d)
        c.add(f"lug_{nm}", lug - cyl_z(x, y, ztop - 1, ztop + 3, 4.0), "pos")
        c.add(f"hw_nut_{nm}", stud_stack(x, y, ztop + 1.8) - cyl_z(x, y, ztop, ztop + 12, 4.0))
        c.add(f"cable_{nm}", tube([top, (top[0], top[1], top[2] + 22.0)], 4.0 if nm == "inverter" else 3.4))
    # current: bar -> nut-clamped tab -> strap bends up at the body -> runs under the fuses -> fuse bottom face
    #          -> fuse element -> fuse top face -> lug -> cable. The M8 stud carries no current (isolated; clamp only).
    zt, zs = z0 + 1.25, z0 + 9.75
    for nm, (x, y), sgn in zip(("charger", "inverter"), studs, (-1, 1)):
        xe = x + 8.0 * sgn
        c.paths[nm] = [(0, -14.0, T / 2), (0, 0, T / 2), (0, 0, zt), (20.05, 0, zt), (20.05, 0, zs), (xe, 0, zs),
                       (xe, 0, ztop + 0.9), (x + 17.0 * sgn, 0, ztop + 0.9), (x + 17.0 * sgn, 0, ztop + 46.0)]
    c.add("cap_2151", bs_cap("2151", 0.0, 0.0, z0, d=(1, 0)), "ins")
    c.labels = [("bar_load", "+ load bar (copper)"), ("hw_m10_nut", "M10 nut: clamps tab to bar"),
                ("bs2151_strap", "tinned copper strap (source)"), ("bs2151_body", "plastic body"),
                ("bs2151_fuse_0_body", "MRBF fuse 30 A"), ("bs2151_fuse_1_body", "MRBF fuse 50 A"),
                ("bs2151_fuse_0_top", "fuse top = load contact"), ("bs2151_fuse_1_bot", "fuse bottom = source contact"),
                ("bs2151_stud", "M8 stud, isolated"), ("lug_charger", "90° lug, 8 AWG"), ("lug_inverter", "90° lug, 6 AWG"),
                ("hw_nut", "washer + M8 nut"), ("cable_charger", "to charger"), ("cable_inverter", "to inverter")]
    return c

if __name__ == "__main__":
    c = build()
    c.export()
    print("exported", len(c.parts))
