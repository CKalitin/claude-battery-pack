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
            v = (self.parts[a] & self.parts[b]).volume
            if v > 0.5:
                bad.append((a, b, round(v, 1)))
        for a in self.parts:
            for b in C:
                if self.allowed(a, b) or not bb_overlap(bbs[a], cbb[b]):
                    continue
                v = (self.parts[a] & C[b]).volume
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
