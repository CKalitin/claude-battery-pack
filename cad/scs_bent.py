"""SCS-ready STEPs for the bent aluminium parts: same geometry as tower15, but every bend gets SCS's real radii
(.063 5052: inside .035" = 0.889 mm, outside inside + T). new = filleted_extrusion - (sharp_extrusion - original)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tower15 as t5
from build123d import *
RI = 0.035 * 25.4

def filleted_sheet(oml, x0, x1, inside_left):
    T = t5.T
    inner = t5.offset_polyline(oml, T if inside_left else -T)
    poly = oml + inner[::-1]
    face = Face(Wire.make_polygon([Vector(0, y, z) for (y, z) in poly], close=True))
    vr = []
    n = len(oml)
    for j in range(1, n - 1):
        a, b, c = oml[j - 1], oml[j], oml[j + 1]
        turn = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(turn) < 1e-9:
            continue
        left_turn = turn > 0
        inner_is_concave = (left_turn == inside_left)
        vo, vi = oml[j], inner[j]
        vr.append((vi, RI if inner_is_concave else RI + T))
        vr.append((vo, RI + T if inner_is_concave else RI))
    verts = face.vertices()
    for (p, r) in sorted(vr, key=lambda t: t[1]):
        v = min(face.vertices(), key=lambda q: (q.Y - p[0]) ** 2 + (q.Z - p[1]) ** 2)
        face = face.fillet_2d(r, [v])
    return Pos(x0, 0, 0) * extrude(face, amount=x1 - x0, dir=(1, 0, 0))

def redo(orig, oml, x0, x1, inside_left):
    sharp = t5.sheet_extrude(oml, x0, x1, inside_left)
    cuts = sharp - orig
    adds = orig - sharp                       # tabs etc. outside the plain profile
    r = filleted_sheet(oml, x0, x1, inside_left) - cuts
    if adds.volume > 1:
        r = r + adds
    print(f'orig {orig.volume:.0f} sharp {sharp.volume:.0f} adds {adds.volume:.0f} new {r.volume:.0f} solids {len(r.solids())}')
    return r

out = os.path.join(HERE, "out_v16", "scs"); os.makedirs(out, exist_ok=True)
lid = t5.lid()
export_step(redo(lid, t5.lid_oml(), t5.XR + 0.5, t5.XF - 0.5, False), os.path.join(out, "lid_bent.step"))
for side, nm in ((-1, "body_half_A"), (1, "body_half_B")):
    pts, _ = t5.half_oml(side)
    orig = t5.body_half(side)
    export_step(redo(orig, pts, t5.XR, t5.XF, side > 0), os.path.join(out, f"{nm}_bent.step"))
print("ok")
