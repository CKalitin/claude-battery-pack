"""Flat patterns (DXF, layers CUT + BEND) for every SendCutSend part of v17, DFM checks for the bent parts, and a JSON of
flat sizes + cut lengths for cad/bom_v17.py. Bent shell: analytic unfold as flats15 (5052 .063: K .42, Ri .035").
Bent copper .125: K .34, Ri .050" (contactor-mounting.md). Run: ~/.venvs/cad/bin/python cad/flats17.py [--v16]
Writes versions/v17-option-d/scs_dxf/ (+ parts.json, DFM_report.txt). --v16 also measures the v16.3 flats for scaling."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
import ezdxf
from build123d import *
import tower17 as t
import bay17 as b
from flats15 import Unfold, rect

OUT = os.path.join(HERE, "..", "versions", "v17-option-d", "scs_dxf")
os.makedirs(OUT, exist_ok=True)
T, K, RI = t.T, t.K, t.RI
BA = lambda th: th * (RI + K * T)
OSSB = lambda th: (RI + T) * math.tan(th / 2)
CK, CRI = 0.34, 0.050 * 25.4                               # copper .125
BA_CU = math.pi / 2 * (CRI + CK * t.CU)
STATS = {}

def stat(name, x0, x1, y0, y1, cut, qty=1, bends=0):
    STATS[name] = dict(w=round(x1 - x0, 1), h=round(y1 - y0, 1), cut=round(cut, 0), qty=qty, bends=bends)

def write_dxf(name, outline, holes=(), slots=(), bends=()):
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=7); doc.layers.add("BEND", color=1, linetype="DASHED")
    msp = doc.modelspace()
    cut = 0.0
    for poly in [outline] + list(slots):
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "CUT"})
        cut += sum(math.dist(a, c) for a, c in zip(poly, poly[1:] + poly[:1]))
    for (x, y, d) in holes:
        msp.add_circle((x, y), d / 2, dxfattribs={"layer": "CUT"}); cut += math.pi * d
    for (p, q) in bends:
        msp.add_line(p, q, dxfattribs={"layer": "BEND"})
    doc.saveas(os.path.join(OUT, name + ".dxf"))
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    stat(name, min(xs), max(xs), min(ys), max(ys), cut, bends=len(bends))

def face_dxf(name, faces, bends=(), qty=1):
    exp = ExportDXF(unit=Unit.MM)
    exp.add_layer("CUT"); exp.add_layer("BEND")
    cut = 0.0
    for f in faces:
        exp.add_shape(f, layer="CUT")
        cut += sum(w.length for w in f.wires())
    for (p, q) in bends:
        exp.add_shape(Edge.make_line(p, q), layer="BEND")
    exp.write(os.path.join(OUT, name + ".dxf"))
    bb = Compound(faces).bounding_box()
    stat(name, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, cut, qty=qty, bends=len(bends))

def from_solid(name, solid, axis, qty=1):
    """section a flat part through its mid-thickness and lay it in XY."""
    bb = solid.bounding_box()
    c = {"x": (bb.min.X + bb.max.X) / 2, "y": (bb.min.Y + bb.max.Y) / 2, "z": (bb.min.Z + bb.max.Z) / 2}[axis]
    pl = {"x": Plane.YZ.offset(c), "y": Plane.XZ.offset(-c), "z": Plane.XY.offset(c)}[axis]
    faces = [pl.to_local_coords(f) for f in section(solid, section_by=pl).faces()]
    face_dxf(name, faces, qty=qty)

# ---------------- shell (bent) ----------------
def body_flat(side):
    oml, _ = t.half_oml(side)
    u = Unfold(oml)
    u_ba = []                                               # Unfold uses flats15 constants (same stock: 5052 .063)
    xr, xf = t.XR, t.XF
    o90, ba90 = OSSB(math.pi / 2), BA(math.pi / 2)
    holes, bends, tabs = [], [], []
    for (y, z) in t.SCREW_YZ:
        if abs(y) < 1e-6:
            if side < 0:
                sc = u.s_of(0, abs(0.0 - oml[0][0]))
                tabs.append((sc - 5.0, sc + 5.0, z + t.TAB_H / 2, z, sc))
            continue
        if (y > 0) != (side > 0):
            continue
        seg = len(oml) - 3
        sc = u.s_of(seg, z - t.CNR)
        tabs.append((sc - t.TAB_H / 2, sc + t.TAB_H / 2, t.W / 2 - t.TAB_END, t.W / 2 - abs(y), sc))
    tabs.sort()
    REL_W = 0.8
    def end_edge(xe, sign):
        pts = []
        xb = xe - sign * o90
        for (s0, s1, fl, hd, sc) in tabs:
            tab_len = ba90 / 2 + (fl - o90)
            xt = xb + sign * tab_len
            pts.extend([(xe, s0 - REL_W), (xb - sign * 1.5, s0 - REL_W), (xb - sign * 1.5, s0), (xt, s0), (xt, s1), (xb - sign * 1.5, s1),
                        (xb - sign * 1.5, s1 + REL_W), (xe, s1 + REL_W)])
            holes.append((xb + sign * (ba90 / 2 + hd - o90), sc, t.TAB_TAP))
            bends.append(((xb, s0), (xb, s1)))
        return pts
    W_ = u.width
    front = [(xf, 0.0)] + end_edge(xf, +1) + [(xf, W_)]
    rear = [(xr, 0.0)] + end_edge(xr, -1) + [(xr, W_)]
    outline = front + rear[::-1]
    for x in t.ep_x:
        for y in (-t.HOLD_Y, t.HOLD_Y):
            if (y > t.SEAM_Y) == (side > 0):
                holes.append((x, u.s_of(0, abs(y - oml[0][0])), 4.5))
    for x in t.LID_SCREW_X:
        holes.append((x, u.s_of(len(oml) - 3, t.LID_SCREW_Z - t.CNR), 4.25))
    for (s, ang, dr) in u.bends():
        bends.append(((xr, s), (xf, s)))
    name = "body_half_A" if side < 0 else "body_half_B"
    write_dxf(name, outline, holes, bends=bends)
    return name, u, [h for h in holes if xr < h[0] < xf], [t_[2] for t_ in tabs]

def lid_flat():
    oml = t.lid_oml()
    u = Unfold(oml)
    x0, x1 = t.XR + 0.5, t.XF - 0.5
    holes, slots = [], []
    top = 3
    s_top = lambda y: u.s_of(top, y - oml[top][0])
    for n, cc in t.CONNS.items():
        x, y, sx, sy, d, ax = cc
        if ax == "n":
            holes.append((x, s_top(y), sx + 0.4)); continue
        slots.append(rect(x - sx / 2 - 0.5, x + sx / 2 + 0.5, s_top(y - sy / 2 - 0.5), s_top(y + sy / 2 + 0.5)))
        holes += [(hx, s_top(hy), 4.25) for (hx, hy) in t.conn_holes(cc)]
    slots.append(rect(t.SB_C[0] - t.SB_HOUS[0] / 2 - 1, t.SB_C[0] + t.SB_HOUS[0] / 2 + 1, s_top(t.SB_C[1] - t.SB_HOUS[1] / 2 - 1), s_top(t.SB_C[1] + t.SB_HOUS[1] / 2 + 1)))
    for x in t.LID_SCREW_X:
        holes.append((x, u.s_of(0, t.LID_SCREW_Z - t.SEAM_Z), 3.4))
        holes.append((x, u.s_of(len(oml) - 2, t.H - t.CNR - t.LID_SCREW_Z), 3.4))
    bends = [((x0, s), (x1, s)) for (s, a, d) in u.bends()]
    write_dxf("lid", rect(x0, x1, 0, u.width), holes, slots, bends)
    slot_edges = [(min(p[1] for p in sl), max(p[1] for p in sl)) for sl in slots]
    return u, holes, slot_edges

def check(name, u, holes, lines, slots=()):
    for i, fl in enumerate(u.flats):
        both = u.th[i] > 0 and u.th[i + 1] > 0
        need = t.DIE / 2 + 0.6 if both else t.MIN_FLAT_FLANGE
        lines.append(f"  {name} segment {i}: flat {fl:.2f} mm (need >= {need:.2f}) {'OK' if fl >= need - 0.005 else 'FAIL'}")
    bl = [s for (s, a, d) in u.bends()]
    worst = min((abs(hs - s) - hd / 2 for (hx, hs, hd) in holes for s in bl), default=99)
    lines.append(f"  {name} closest hole edge to a bend centre line: {worst:.1f} mm (need >= {t.DIE / 2:.1f}) {'OK' if worst >= t.DIE / 2 - 0.05 else 'FAIL'}")
    if slots:
        w2 = min(min(abs(a - s), abs(c - s)) for a, c in slots for s in bl)
        lines.append(f"  {name} closest slot edge to a bend centre line: {w2:.1f} mm {'OK' if w2 >= t.DIE / 2 - 0.05 else 'FAIL'}")

# ---------------- bent copper ----------------
def rface(x0, x1, y0, y1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)

def copper_flats(lines):
    rise = t.Z_P0 - t.Z_COP - 2 * 1.27                       # straight riser between the two bend tangents
    # pack+ : low sheet to x_edge 103, then BA + riser + BA + flange to 130 (flange starts at the second bend centre 108.7)
    dev_p = BA_CU + rise + BA_CU + (130.0 - (103.0 + 2 * 1.27 + t.CU))
    s = rface(t.cell_x[6] - t.BB_W / 2, 140.5, -46, -21) + rface(t.cell_x[6] - t.BB_W / 2, 103.0, -21, 8) + rface(103.0, 103.0 + dev_p, -12, 8)
    for k in (6, 7):
        s -= Pos(t.cell_x[k], -t.TERM_OFF) * Circle(3.3)
    s -= Pos(*t.tap_pts()[4]) * Circle(1.25)
    xm5191 = 103.0 + dev_p - (130.0 - b.X5191)
    s -= Pos(xm5191, b.Y5191) * Circle(4.9)
    face_dxf("bus_pack_pos", s.faces(), bends=[((103.0 + BA_CU / 2, -12, 0), (103.0 + BA_CU / 2, 8, 0)),
                                               ((103.0 + BA_CU * 1.5 + rise, -12, 0), (103.0 + BA_CU * 1.5 + rise, 8, 0))])
    dev_n = BA_CU + rise + BA_CU + ((-115.0 - (2 * 1.27 + t.CU)) - (-147.5))
    s = rface(-140.5, t.cell_x[1] + t.BB_W / 2, -46, -21) + rface(-115.0, -88.0, -71, -46) + rface(-115.0 - dev_n, -115.0, -71, -48.5)
    for k in (0, 1):
        s -= Pos(t.cell_x[k], -t.TERM_OFF) * Circle(3.3)
    s -= Pos(*t.tap_pts()[0]) * Circle(1.25)
    xa = -115.0 - dev_n + (b.NODE_A[0] + 147.5)
    s -= Pos(xa, b.NODE_A[1]) * Circle(4.3)
    face_dxf("bus_pack_neg", s.faces(), bends=[((-115.0 - BA_CU / 2, -71, 0), (-115.0 - BA_CU / 2, -48.5, 0)),
                                               ((-115.0 - BA_CU * 1.5 - rise, -71, 0), (-115.0 - BA_CU * 1.5 - rise, -48.5, 0))])
    for nm, hole_edge in (("pack+ 5191 hole", b.X5191 - 4.9 - (103 + 2 * 1.27 + t.CU)), ("pack- node-A hole", -115 - 2 * 1.27 - t.CU - (b.NODE_A[0] + 4.3))):
        lines.append(f"  copper {nm}: edge {hole_edge:.1f} mm from the bend centre (rule used >= 8) {'OK' if hole_edge >= 8 else 'FAIL'}")
    # Z-strap: foot (y -18 .. leg) -> leg up -> top run + pad
    zf = b.ZF
    leg_h = zf + t.CU - t.Z_P1
    o = CRI + t.CU
    foot = (2.7 + t.CU - (-18.0)) - o
    legs = leg_h - 2 * o
    top = (41.0 - 2.7) - o
    y0 = -18.0
    y1 = y0 + foot + BA_CU + legs + BA_CU                    # where the flat top run starts
    s = rface(136.5, 151.5, y0, y1 + top) + rface(114.0, 136.5, y1 + top - 17.0, y1 + top)
    s -= Pos(b.FOOT[0], b.FOOT[1]) * Circle(3.2)
    s -= Pos(b.ST_MAIN[0], y1 + top - (41.0 - b.ST_MAIN[1])) * Circle(4.3)
    bl = [y0 + foot + BA_CU / 2, y0 + foot + BA_CU * 1.5 + legs]
    face_dxf("strap_main", s.faces(), bends=[((136.5, v, 0), (151.5, v, 0)) for v in bl])
    lines.append(f"  copper strap: foot flange {foot:.1f}, top flange {top:.1f} mm (min .471in = 12.0) {'OK' if min(foot, top) >= 12 else 'FAIL'}; "
                 f"joggle height {zf - t.Z_P1:.1f} mm (SCS .506-3.75in = 12.9-95) {'OK' if 12.9 <= zf - t.Z_P1 <= 95 else 'FAIL'}")
    lines.append(f"  copper strap foot hole: edge {bl[0] - BA_CU / 2 + BA_CU / 2 - (b.FOOT[1] + 3.2):.1f} mm from the lower bend centre (rule used >= 8)")
    rise_out = t.Z_P1 - t.Z_BB
    lines.append(f"  copper pack Z joggle height {rise_out:.1f} mm {'OK' if 12.9 <= rise_out <= 95 else 'FAIL'}; riser flange pos {130 - 103:.0f}, neg {147.5 - 115:.0f} mm")

def v17():
    lines = [f"SCS 5052 .063: BA90 {BA(math.pi / 2):.3f}  BD30 {2 * OSSB(math.pi / 6) - BA(math.pi / 6):.3f} mm; copper .125 BA90 {BA_CU:.3f} mm",
             f"facet F {t.F}, lip {t.LIP_L}, body W {t.W}, lid width {t.WL:.1f}, H {t.H:.1f}"]
    for side in (-1, 1):
        name, u, holes, tabs = body_flat(side)
        check(name, u, holes, lines)
        lines.append(f"  {name} tab flanges (formed) {[round(v, 1) for v in tabs]} mm (min formed flange 7.7) {'OK' if min(tabs) >= 7.7 else 'FAIL'}")
    u, holes, slots = lid_flat()
    check("lid", u, [(x, s, d) for x, s, d in holes], lines, slots)
    lines.append(f"  lid U-channel 2:1: base {u.flats[3]:.0f} vs 2 x leg {2 * t.LID_H:.0f} {'OK' if u.flats[3] >= 2 * t.LID_H else 'FAIL'}")
    copper_flats(lines)
    p = t.build(harness=False)
    from_solid("plate_front", p["plate_front"], "x"); from_solid("plate_rear", p["plate_rear"], "x")
    from_solid("module_endplate", p["module_endplates"].solids()[0], "x", qty=2)
    from_solid("diffuser_f", p["diffuser_f"], "x")
    from_solid("pipe_f", p["pipe_f"], "z")
    for n in ("g10_floor", "g10_frame", "deck1", "deck2", "g10_bay", "g10_bms_bridge"):
        from_solid(n, p[n], "z")
    from_solid("g10_sb_cheek", p["g10_sb_cheek_0"], "y", qty=2)
    from_solid("mylar_top", p["g10_top"], "z")
    from_solid("mylar_spacer", p["g10_spacers"].solids()[0], "x", qty=9)
    for k in "ABC":
        from_solid(f"bus_{k}", p[f"bus_{k}"], "z")
    for n in ("bus_mod_pos", "bus_mod_neg", "bus_mod_in"):
        from_solid(n, p[n], "z")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(OUT, "DFM_report.txt"), "w").write(txt + "\n")
    json.dump(STATS, open(os.path.join(OUT, "parts.json"), "w"), indent=1)

if __name__ == "__main__":
    v17()
    for k, v in STATS.items():
        print(f"{k:16s} {v}")
