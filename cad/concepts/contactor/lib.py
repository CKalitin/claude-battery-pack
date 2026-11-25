"""Sandbox for contactor-mounting concepts.

Shared v15 context (cells, walls, lid, converters, front PCB) comes from ctx/*.brep (checks) and
out_tower15/stl/*.stl (renders). Each concept builds only the power-bay parts, then runs the same checks:
  - interference with the context and between its own parts (allow-list per concept)
  - clearances: + to - copper >= 10 mm, pack copper to chassis metal >= 7 mm, to series bars >= 7 mm
  - current-path metrics from the centre-line polylines the concept declares
Dimensions marked UNCONFIRMED in comments are estimates (see docs/contactor-mounting.md).
"""
import glob, itertools, json, math, os, sys
os.environ.setdefault("DISPLAY", ":99")
from build123d import Box, Cylinder, Pos, Plane, Solid, Vector, import_brep, export_stl, Location, Axis

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.abspath(os.path.join(HERE, "..", ".."))
CTX_BREP = os.path.join(HERE, "ctx")
CTX_STL = os.path.join(CAD, "out_tower15", "stl")
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)

# ---------------- key heights from v15 (mm) ----------------
Z_TERM = 206.85          # cell terminal top = series bar bottom
Z_BAR_TOP = 210.0        # series bars / collectors top
Z_TRAY_TOP = 221.6252    # tray 1 top (G10)
Z_LID_TOP = 319.7002
Z_LID_IN = Z_LID_TOP - 1.6
Z_SEAM = 277.7
CU = 4.76                # 3/16 in copper bar (SendCutSend COP-187) UNCONFIRMED stock for SCS copper thickness
G10 = 3.175              # 1/8 in G10

# ---------------- primitives ----------------
def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

def cyl_z(x, y, z0, z1, r):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, abs(z1 - z0))

def cyl_between(p, q, r):
    p, q = Vector(*p), Vector(*q)
    d = q - p
    return Solid.make_cylinder(r, d.length, Plane(origin=p, z_dir=d))

def tube(points, r):
    """Cable: cylinders between points + spheres at the joints (smooth enough for a feasibility model)."""
    from build123d import Sphere
    s = None
    for a, b in zip(points[:-1], points[1:]):
        c = cyl_between(a, b, r)
        s = c if s is None else s + c
    for p in points[1:-1]:
        s += Pos(*p) * Sphere(r)
    return s

def arc_pts(center, r, a0, a1, plane="xz", n=10, fixed=0.0):
    """Points on an arc in an axis plane; angles in degrees; 'fixed' is the out-of-plane coordinate."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        u, v = center[0] + r * math.cos(a), center[1] + r * math.sin(a)
        pts.append({"xz": (u, fixed, v), "yz": (fixed, u, v), "xy": (u, v, fixed)}[plane])
    return pts

def polyline_len(pts):
    return sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))

def climb(pts):
    up = sum(max(0.0, b[2] - a[2]) for a, b in zip(pts[:-1], pts[1:]))
    down = sum(max(0.0, a[2] - b[2]) for a, b in zip(pts[:-1], pts[1:]))
    return up, down

# ---------------- catalog part models (datasheet outlines) ----------------
def gv14_pcb(cx, cy, z_face, axis="y", flip=True, H=59.9, L=59.9, W=56.1, pitch=26.7):
    """Gigavac GV14 PCB-mount: two M8x1.25-6H female terminals flush on the base face, no mounting feet
    (held by its two terminal bolts through the 'PCB'). flip=True: base face DOWN on the copper at z_face.
    Datasheet numbers (unlabelled in the text extract): 59.9, 56.1, 52.6, 26.7 ... UNCONFIRMED which is which.
    Returns (solid, [terminal xy])."""
    if flip:
        body = box(cx - L / 2, cx + L / 2, cy - W / 2, cy + W / 2, z_face, z_face + H)
    else:
        body = box(cx - L / 2, cx + L / 2, cy - W / 2, cy + W / 2, z_face - H, z_face)
    t = [(cx, cy - pitch / 2), (cx, cy + pitch / 2)] if axis == "y" else [(cx - pitch / 2, cy), (cx + pitch / 2, cy)]
    return body, t

def sb175_bbs(cx, cy, z_top, axis="y", pitch=26.8):
    """Anderson SB175 2-pole housing standing vertical, mating face up at z_top, with two 180BBS busbar contacts.
    Housing 55.6 x 25.4 face, 79.6 long (Anderson DS, Zoro listing). Busbar face 89.8 below the mating face
    ('Bus bar mounting table', DS-SB175 rev02 extract) UNCONFIRMED reading. Pitch 26.8 UNCONFIRMED.
    Returns (housing, [contact solids], [contact xy], z_bus)."""
    long_x = axis == "x"
    hx, hy = (55.6, 25.4) if long_x else (25.4, 55.6)
    housing = box(cx - hx / 2, cx + hx / 2, cy - hy / 2, cy + hy / 2, z_top - 79.6, z_top)
    z_bus = z_top - 89.8
    xy = [(cx - pitch / 2, cy), (cx + pitch / 2, cy)] if long_x else [(cx, cy - pitch / 2), (cx, cy + pitch / 2)]
    contacts = [box(x - 6.35, x + 6.35, y - 6.35, y + 6.35, z_bus, z_top - 79.6) for x, y in xy]   # contact tail below the housing
    return housing, contacts, xy, z_bus

def mrbf_link(p0, p1, z_bot, w=25.0, t=12.0):
    """MRBF fuse lying flat between two studs (ring tabs at both ends). Body ~ UNCONFIRMED 25 x (span) x 12."""
    (x0, y0), (x1, y1) = p0, p1
    if abs(x1 - x0) > abs(y1 - y0):
        return box(min(x0, x1) - 8, max(x0, x1) + 8, y0 - w / 2, y0 + w / 2, z_bot, z_bot + t)
    return box(x0 - w / 2, x0 + w / 2, min(y0, y1) - 8, max(y0, y1) + 8, z_bot, z_bot + t)

def tesla_shunt_flat(x0, x1, yc, z_bot):
    """Tesla shunt lying flat: bar 83.5 x 35 x 3.2 (tesla-shunt.md, UNCONFIRMED) + its sensing module 25 x 43 x 7 on top."""
    bar = box(x0, x1, yc - 17.5, yc + 17.5, z_bot, z_bot + 3.2)
    xm = (x0 + x1) / 2
    mod = box(xm - 12.5, xm + 12.5, yc - 21.5, yc + 21.5, z_bot + 3.2, z_bot + 10.2)
    return bar, mod

# ---------------- context ----------------
CHASSIS = ("body_half", "lid", "plate_front", "plate_rear", "module_endplates", "tray2", "rods", "so_upper", "so_lower",
           "pem_", "screws_lid", "screws_f", "screws_panel")
MID_COPPER = ("bus_A", "bus_B", "bus_C")
OBSTACLES = ("screws_trays", "screws_term", "screws_tap", "charger", "inverter", "ledboard_f", "ctrl_", "panel_", "flex_ccs", "g10_top", "inv_posts", "cell_",
             "antenna", "diffuser_f", "panel_standoffs")

_ctx = {}
def ctx(prefixes):
    out = {}
    for f in sorted(glob.glob(os.path.join(CTX_BREP, "*.brep"))):
        n = os.path.basename(f)[:-5]
        if n.startswith(prefixes):
            if n not in _ctx:
                _ctx[n] = import_brep(f)
            out[n] = _ctx[n]
    return out

def bb_overlap(a, b, pad=0.0):
    return not (a.min.X - pad >= b.max.X or b.min.X - pad >= a.max.X or a.min.Y - pad >= b.max.Y or
                b.min.Y - pad >= a.max.Y or a.min.Z - pad >= b.max.Z or b.min.Z - pad >= a.max.Z)

class Concept:
    def __init__(self, key, title):
        self.key, self.title = key, title
        self.parts, self.role = {}, {}          # role: pos / neg / ins (insulator) / other
        self.allow = []                         # (prefixA, prefixB) pairs allowed to touch
        self.paths = {}                         # name -> centre-line points
        self.notes, self.joints, self.bends = [], {}, {}
        self.labels = []

    def add(self, name, shape, role="other"):
        self.parts[name] = shape; self.role[name] = role

    def allowed(self, a, b):
        return any((a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)) for p, q in self.allow)

    # ---------- checks ----------
    def check(self):
        res = {"key": self.key, "title": self.title}
        C = ctx(CHASSIS + MID_COPPER + OBSTACLES)
        bbs = {k: v.bounding_box() for k, v in self.parts.items()}
        cbb = {k: v.bounding_box() for k, v in C.items()}
        bad = []
        for a, b in itertools.combinations(self.parts, 2):
            if self.allowed(a, b) or not bb_overlap(bbs[a], bbs[b]):
                continue
            x = self.parts[a] & self.parts[b]
            v = x.volume if x is not None else 0.0
            if v > 0.5:
                bad.append((a, b, round(v, 1)))
        for a in self.parts:
            for b in C:
                if self.allowed(a, b) or not bb_overlap(bbs[a], cbb[b]):
                    continue
                x = self.parts[a] & C[b]
                v = x.volume if x is not None else 0.0
                if v > 0.5:
                    bad.append((a, b, round(v, 1)))
        res["interferences"] = bad
        pos = [k for k, r in self.role.items() if r == "pos"]
        neg = [k for k, r in self.role.items() if r == "neg"]

        def mind(A, B, pad=40):
            best = (1e9, None, None)
            for a in A:
                for b in B:
                    ba = bbs[a] if a in bbs else cbb[a]
                    bb = bbs[b] if b in bbs else cbb[b]
                    if not bb_overlap(ba, bb, pad):
                        continue
                    sa = self.parts.get(a, C.get(a)); sb = self.parts.get(b, C.get(b))
                    d = sa.distance_to(sb)
                    if d < best[0]:
                        best = (d, a, b)
            return (round(best[0], 1) if best[0] < 1e9 else None, best[1], best[2])
        chassis = [k for k in C if k.startswith(CHASSIS)]
        mid = [k for k in C if k.startswith(MID_COPPER)]
        res["pos_to_neg"] = mind(pos, neg)
        res["pack_to_chassis"] = min([mind(pos, chassis), mind(neg, chassis)], key=lambda t: t[0] if t[0] is not None else 1e9)
        res["pack_to_series_bars"] = min([mind(pos, mid), mind(neg, mid)], key=lambda t: t[0] if t[0] is not None else 1e9)
        res["paths"] = {}
        for n, pts in self.paths.items():
            up, down = climb(pts)
            res["paths"][n] = {"length_mm": round(polyline_len(pts)), "climb_mm": round(up), "drop_mm": round(down)}
        res["joints"] = self.joints; res["bends"] = self.bends; res["notes"] = self.notes
        with open(os.path.join(OUT, f"{self.key}.json"), "w") as f:
            json.dump(res, f, indent=1)
        return res

    def export(self):
        d = os.path.join(OUT, self.key); os.makedirs(d, exist_ok=True)
        for f in glob.glob(os.path.join(d, "*.stl")):
            os.remove(f)
        for n, s in self.parts.items():
            export_stl(s, os.path.join(d, f"{n}.stl"), tolerance=0.05, angular_tolerance=0.2)
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump({"roles": self.role, "labels": self.labels, "title": self.title}, f)
        for n, pts in self.paths.items():
            # copper centre line from the cells to the output connector's terminal (part bodies bridged at terminal height) as a thin tube so it shows in renders
            export_stl(tube([(x, y, z) for x, y, z in pts], 1.2), os.path.join(d, f"path_{n}.stl"), tolerance=0.1, angular_tolerance=0.3)

# ---------------- Blue Sea MRBF terminal fuse blocks (5191 single, 2151 dual) ----------------
# Outline from Blue Sea's dimensioned drawing (bluesea.com/products/2151 -> "Dimensioned Drawing", 5191.jpg, read 2026-11-24):
#   2151: 88.5 long, 20.0 wide, body 56.5 long x 11.0 high, tab 2.5 thick, M10 hole d 9.525, stud tops 44.5 above the base,
#         0.47 in (11.9 mm) from the latch rib to the outer stud. Positions along the length scaled off the drawing:
#         hole 13.0, studs 47.2 and 73.4 (pitch 26.2), rib 58.9-61.7 (18.4 high). UNCONFIRMED (scaled, +-0.5 mm).
#   5191: 60.9 long, body 29.0, hole 12.0, stud 46.4 (14.5 from the end), latch at the end 21 high. UNCONFIRMED (scaled).
# Internals are inferred from the drawing's side view (the tab bends up at the body and runs along its top as a
# strap under the studs; each stud has an insulating collar). UNCONFIRMED.
# MRBF fuse: 27.8 x 23.0 x 16.3 (reseller 12voltplanet, Solar4RVs). It is a stack fuse: bottom face = source
# contact (sits on the block's strap), top face = load contact (the cable lug sits on it). The stud only clamps.
BS = {"2151": dict(L=88.5, hole=13.0, body=31.8, studs=(47.2, 73.4), ribs=((58.9, 61.7, 18.4),)),
      "5191": dict(L=60.9, hole=12.0, body=31.5, studs=(46.4,), ribs=((58.9, 60.9, 21.0),))}
MRBF_L, MRBF_W, MRBF_H = 27.8, 23.0, 16.3

def _place(hx, hy, hole_u, d):
    """Local block frame -> world box. u along the block from the tab end, v across, origin = M10 hole."""
    dx, dy = d
    def B(u0, u1, v0, v1, z0, z1):
        xs = [hx + dx * (u - hole_u) - dy * v for u in (u0, u1) for v in (v0, v1)]
        ys = [hy + dy * (u - hole_u) + dx * v for u in (u0, u1) for v in (v0, v1)]
        return box(min(xs), max(xs), min(ys), max(ys), z0, z1)
    def P(u, v=0.0):
        return (hx + dx * (u - hole_u) - dy * v, hy + dy * (u - hole_u) + dx * v)
    return B, P

def bs_block(kind, hx, hy, z0, d=(1, 0), prefix="bs"):
    """Blue Sea MRBF terminal fuse block with fuses fitted. Tab bottom at z0, M10 hole at (hx, hy),
    block runs along d from the hole. Returns (parts {name: (shape, role)}, stud xy list, z of the fuse tops)."""
    s = BS[kind]; B, P = _place(hx, hy, s["hole"], d)
    L, ub, t = s["L"], s["body"], 2.5
    parts = {}
    strap = B(0, ub + t, -10, 10, z0, z0 + t)                       # tab (on the M10 stud)
    strap += B(ub, ub + t, -8, 8, z0, z0 + 11.0)                     # bends up at the body
    strap += B(ub, L - 2.0, -8, 8, z0 + 11.0 - t, z0 + 11.0)          # runs along the top under the studs (width UNCONFIRMED)
    strap -= cyl_z(*P(s["hole"]), z0 - 1, z0 + t + 1, 9.525 / 2)
    for u in s["studs"]:
        strap -= cyl_z(*P(u), z0, z0 + 12, 6.0)                      # clearance round the stud: stud is isolated
    parts[f"{prefix}_strap"] = (strap, "pos")
    body = B(ub + t, L, -10, 10, z0, z0 + 11.0) - B(ub, L - 2.0, -8, 8, z0 + 11.0 - t, z0 + 11.0)
    for (r0, r1, h) in s["ribs"]:
        body += B(r0, r1, -10, 10, z0 + 11.0, z0 + h)
    for u in s["studs"]:
        body += cyl_z(*P(u), z0 + 11.0 - t, z0 + 15.0, 6.0)          # insulating collar (centres the fuse)
    parts[f"{prefix}_body"] = (body, "ins")
    zf0, zf1 = z0 + 11.0, z0 + 11.0 + MRBF_H
    for i, u in enumerate(s["studs"]):
        x, y = P(u)
        parts[f"{prefix}_stud_{i}"] = (cyl_z(x, y, z0 + 1.0, z0 + 44.5, 4.0), "pos")   # M8, isolated from the strap
        hous = B(u - MRBF_W / 2, u + MRBF_W / 2, -MRBF_L / 2, MRBF_L / 2, zf0 + 1.0, zf1 - 1.0)
        hous -= cyl_z(x, y, zf0, zf0 + 5.0, 6.4) + cyl_z(x, y, zf0, zf1, 4.5)
        parts[f"{prefix}_fuse_{i}_body"] = (hous, "ins")                                # clear housing, fuse element inside
        parts[f"{prefix}_fuse_{i}_bot"] = (cyl_z(x, y, zf0, zf0 + 1.0, 10.0) - cyl_z(x, y, zf0 - 1, zf0 + 2, 6.4), "pos")  # source contact
        parts[f"{prefix}_fuse_{i}_top"] = (cyl_z(x, y, zf1 - 1.0, zf1, 10.0) - cyl_z(x, y, zf1 - 2, zf1 + 1, 4.3), "pos")  # load contact
    return parts, [P(u) for u in s["studs"]], zf1

def bs_cap(kind, hx, hy, z0, d=(1, 0)):
    """Insulating cap over the body (render only, shown ghosted). Outline UNCONFIRMED."""
    s = BS[kind]; B, _ = _place(hx, hy, s["hole"], d)
    return B(s["body"] - 1.0, s["L"] + 1.0, -15.0, 15.0, z0, z0 + 46.0) - B(s["body"] + 0.5, s["L"] - 0.5, -14.0, 14.0, z0 - 1, z0 + 45.0)

def lug90(x, y, z, d=(-1, 0), r_ring=8.5, t=1.8, off=17.0, r_barrel=5.0, h=24.0):
    """90 deg ring lug (Del City 929605 6 AWG / MAX 5950 8 AWG style), ring on the stud at z, barrel up, offset along d.
    Outline UNCONFIRMED. Returns (lug, barrel top xyz)."""
    bx, by = x + d[0] * off, y + d[1] * off
    lug = cyl_z(x, y, z, z + t, r_ring) - cyl_z(x, y, z - 1, z + t + 1, 4.2)
    lug += box(min(x, bx) - (4.5 if d[0] == 0 else 0), max(x, bx) + (4.5 if d[0] == 0 else 0),
               min(y, by) - (4.5 if d[1] == 0 else 0), max(y, by) + (4.5 if d[1] == 0 else 0), z, z + t)
    lug += cyl_z(bx, by, z, z + h, r_barrel)
    return lug, (bx, by, z + h)

def stud_stack(x, y, z, r_w=8.5):
    """Flat washer + M8 nut (13 AF) on a stud from z."""
    return cyl_z(x, y, z, z + 1.6, r_w) + cyl_z(x, y, z + 1.6, z + 8.1, 7.5)
