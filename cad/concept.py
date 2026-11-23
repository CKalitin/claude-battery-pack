"""Exterior concept: Mac-Pro-tower-style end frames (handles + feet) around a radiused red wrap.
Wraps the v1 internal stack (packmodel). Units mm. x = length, y = width, z = up.
"""
import os
from build123d import *
import packmodel as pm

R_BODY = 22.0          # wrap bend radius (outside) [mm]
T = 1.6                # wrap sheet [mm]
W = pm.SHELL_W         # body width
H = pm.SHELL_H + pm.T_SHEET   # body height incl. lid
L = pm.SHELL_L         # body length between end frames
SEAM_Z = H - 34.0      # lid / body split line
GAP = 1.0              # shadow gap at seam

FR_T = 8.0             # end-frame plate thickness (machined 6061) [mm]
FR_PROUD = 8.0         # frame stands proud of body sides [mm]
FR_W = W + 2 * FR_PROUD
HANDLE_H = 52.0        # frame extends above body for handle [mm]
FOOT_H = 18.0
FR_H = H + HANDLE_H + FOOT_H
FR_R = 26.0

def rr(w, h, r):
    return RectangleRounded(w, h, r)

def section_yz(w, h, r):
    """Closed rounded-rect profile on the YZ plane, centred at (y=0, z=h/2)."""
    return Plane.YZ.offset(0) * Pos(0, h / 2) * rr(w, h, r)

def wrap_tube():
    outer = extrude(Plane.YZ * Pos(0, H / 2) * rr(W, H, R_BODY), amount=L / 2, both=True)
    inner = extrude(Plane.YZ * Pos(0, H / 2) * rr(W - 2 * T, H - 2 * T, R_BODY - T), amount=L / 2, both=True)
    return outer - inner

def body_and_lid():
    tube = wrap_tube()
    body = tube - Pos(0, 0, SEAM_Z) * Box(L + 2, W + 2, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lid = tube & Pos(0, 0, SEAM_Z + GAP) * Box(L + 2, W + 2, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # connector openings in lid (from v1 stack)
    for (x, y, cl, cw) in (pm.CONN_PWR, pm.CONN_CAN):
        lid = lid - Pos(x, y, H - 10) * Box(cl + 1, cw + 1, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body, lid

def end_frame(sign):
    prof = Plane.YZ * Pos(0, FR_H / 2 - FOOT_H) * rr(FR_W, FR_H, FR_R)
    f = extrude(prof, amount=FR_T)
    f = f.moved(Location((sign * (L / 2) + (0 if sign > 0 else -FR_T), 0, 0)))
    x0 = sign * (L / 2) + (0 if sign > 0 else -FR_T)
    # handle slot: stadium cutout above body
    slot = Plane.YZ * Pos(0, H + HANDLE_H / 2 + 2) * SlotCenterToCenter(FR_W - 2 * 46 - 30, 30)
    f = f - extrude(slot.moved(Location((x0, 0, 0))), amount=FR_T)
    # arch between feet
    arch = Plane.YZ * Pos(0, -FOOT_H) * SlotCenterToCenter(FR_W - 2 * 30 - 2 * FOOT_H, 2 * FOOT_H - 4)
    f = f - extrude(arch.moved(Location((x0, 0, 0))), amount=FR_T)
    # machined hex dimple field on the outer face (blind, 1.2 mm) - cheese-grater nod
    pitch, d = 11.0, 7.0
    face_x = x0 + (FR_T if sign > 0 else 0)
    dimples = []
    rows = int((H - 70) / (pitch * 0.866))
    for r in range(rows):
        z = 40 + r * pitch * 0.866
        off = (pitch / 2) if r % 2 else 0
        n = int((W - 40) / pitch)
        for c in range(n):
            y = -((n - 1) * pitch) / 2 + c * pitch + off - pitch / 4
            if abs(y) > (W - 40) / 2:
                continue
            dimples.append(Pos(face_x - sign * 0.6, y, z) * Sphere(d / 2 + 0.6))
    f = f - Compound(dimples)
    return f

def connectors():
    out = []
    for (x, y, cl, cw), h in ((pm.CONN_PWR, 8), (pm.CONN_CAN, 6)):
        out.append(Pos(x, y, H - 2) * Box(cl, cw, h + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return out

def build():
    body, lid = body_and_lid()
    parts = {"body_red": body, "lid_red": lid, "frame_pos": end_frame(+1), "frame_neg": end_frame(-1)}
    for i, c in enumerate(connectors()):
        parts[f"conn_{i}"] = c
    return parts

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "concept")
    os.makedirs(out, exist_ok=True)
    parts = build()
    for n, p in parts.items():
        export_stl(p, os.path.join(out, f"{n}.stl"), tolerance=0.05, angular_tolerance=0.1)
        print(n, round(p.volume / 1000, 1), "cm3", p.bounding_box().size)
    export_step(Compound(children=list(parts.values())), os.path.join(out, "concept_exterior.step"))
    print("frame overall", FR_W, "x", FR_H, "; body", L, W, H)
