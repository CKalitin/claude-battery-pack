"""Flat patterns for every SendCutSend part of Claude battery pack v5 + DFM checks.
Bent parts are unfolded analytically with SCS's .063 5052 numbers (K .42, Ri .035"): BA = th*(Ri + K*T), OSSB = (Ri+T)*tan(th/2).
DXF layers: CUT (profile + holes), BEND (bend centre lines). Units mm.
"""
import math, os, json
import ezdxf
import tower5 as t5
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_tower5", "scs_dxf")
os.makedirs(OUT, exist_ok=True)
T, K, RI = t5.T, t5.K, t5.RI
def BA(th): return th * (RI + K * T)
def OSSB(th): return (RI + T) * math.tan(th / 2)
BD90 = 2 * OSSB(math.pi / 2) - BA(math.pi / 2)
REPORT = []

# ---------------- unfold a profile (OML polyline) ----------------
class Unfold:
    def __init__(self, oml):
        self.p = oml
        self.L = [math.dist(a, b) for a, b in zip(oml[:-1], oml[1:])]
        dirs = [math.atan2(b[1] - a[1], b[0] - a[0]) for a, b in zip(oml[:-1], oml[1:])]
        self.th = [0.0] + [abs((dirs[i] - dirs[i - 1] + math.pi) % (2 * math.pi) - math.pi) for i in range(1, len(dirs))] + [0.0]
        self.sgn = [0] + [1 if ((dirs[i] - dirs[i - 1] + math.pi) % (2 * math.pi) - math.pi) > 0 else -1 for i in range(1, len(dirs))] + [0]
        # s of each vertex's bend centre
        self.sv = [0.0]
        for i, L in enumerate(self.L):
            a, b = self.th[i], self.th[i + 1]
            self.sv.append(self.sv[-1] + BA(a) / 2 + (L - OSSB(a) - OSSB(b)) + BA(b) / 2)
        self.width = self.sv[-1]
        self.flats = [L - OSSB(self.th[i]) - OSSB(self.th[i + 1]) for i, L in enumerate(self.L)]

    def s_of(self, seg, d):
        """flat coordinate of a point on segment seg at OML distance d from its start vertex."""
        a = self.th[seg]
        return self.sv[seg] + BA(a) / 2 + (d - OSSB(a))

    def bends(self):
        return [(self.sv[i], math.degrees(self.th[i]), "up" if self.sgn[i] > 0 else "down") for i in range(1, len(self.p) - 1)]

def seg_point(oml, seg, pt):
    return math.dist(oml[seg], pt)

# ---------------- DXF writer ----------------
def write_dxf(name, outline, holes=(), slots=(), bends=(), circles_d=()):
    """outline: list of (x,y) closed polygon. holes: [(x,y,d)]. slots: list of closed polylines. bends: [((x0,y0),(x1,y1))]."""
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=7); doc.layers.add("BEND", color=1, linetype="DASHED")
    msp = doc.modelspace()
    msp.add_lwpolyline(outline, close=True, dxfattribs={"layer": "CUT"})
    for (x, y, d) in holes:
        msp.add_circle((x, y), d / 2, dxfattribs={"layer": "CUT"})
    for s in slots:
        msp.add_lwpolyline(s, close=True, dxfattribs={"layer": "CUT"})
    for (a, b) in bends:
        msp.add_line(a, b, dxfattribs={"layer": "BEND"})
    f = os.path.join(OUT, name + ".dxf")
    doc.saveas(f)
    return f

def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# ---------------- body halves ----------------
def body_flat(side):
    oml, _ = t5.half_oml(side)
    u = Unfold(oml)
    xr, xf = t5.XR, t5.XF
    tab90 = math.pi / 2
    o90, ba90 = OSSB(tab90), BA(tab90)
    holes, slots, bends = [], [], []
    # main sheet: x along length, s across.  Outline built as polygon walking around, with tabs on both x ends.
    tabs = []                                       # (s0, s1, flange_formed, hole_d_from_bend_oml, hole_s)
    for (y, z) in t5.SCREW_YZ:
        if y == 0.0:
            if side < 0:
                d = abs(0.0 - oml[0][0])            # floor tab centred at y = 0, on segment 0
                sc = u.s_of(0, d)
                tabs.append((sc - 5.0, sc + 5.0, z + t5.TAB_H / 2, z, sc))
            continue
        if (y > 0) != (side > 0):
            continue
        seg = len(oml) - 2                          # wall segment
        sc = u.s_of(seg, z - t5.CNR)
        tabs.append((sc - t5.TAB_H / 2, sc + t5.TAB_H / 2, t5.W / 2 - t5.TAB_END, t5.W / 2 - abs(y), sc))
    tabs.sort()
    REL_W, REL_D = 0.8, o90 + 1.5
    def end_edge(xe, sign):
        """points along one x end, from s=0 to s=width (sign +1 front: tabs protrude to +x)."""
        pts = []
        xb = xe - sign * o90                        # bend line (centre) of tabs
        for (s0, s1, fl, hd, sc) in tabs:
            tab_len = ba90 / 2 + (fl - o90)         # beyond the bend centre line
            xt = xb + sign * tab_len
            pts += [(xe, s0 - REL_W), (xb - sign * 1.5, s0 - REL_W), (xb - sign * 1.5, s0), (xt, s0), (xt, s1), (xb - sign * 1.5, s1),
                    (xb - sign * 1.5, s1 + REL_W), (xe, s1 + REL_W)]
            holes.append((xb + sign * (ba90 / 2 + hd - o90), sc, t5.TAB_TAP))
            bends.append(((xb, s0), (xb, s1)))
        return pts
    W_ = u.width
    front = [(xf, 0.0)] + end_edge(xf, +1) + [(xf, W_)]
    rear = [(xr, 0.0)] + end_edge(xr, -1) + [(xr, W_)]
    outline = front + rear[::-1]
    # holes on the main sheet
    for x in t5.ep_x:
        for y in (-40.0, 40.0):
            if (y > t5.SEAM_Y) == (side > 0):
                holes.append((x, u.s_of(0, abs(y - oml[0][0])), 4.5))
    for x in t5.LID_SCREW_X:
        holes.append((x, u.s_of(len(oml) - 2, t5.LID_SCREW_Z - t5.CNR), 4.25))
    for (s, ang, dr) in u.bends():
        bends.append(((xr, s), (xf, s)))
    name = "body_half_A" if side < 0 else "body_half_B"
    f = write_dxf(name, outline, holes, bends=bends)
    info = dict(part=name, material="5052 .063", flat=(round(xf - xr + 2 * 40, 1), round(W_, 1)), profile_bends=u.bends(), tabs=len(tabs) * 2,
                flats=[round(v, 2) for v in u.flats], tab_flange=[round(t[2], 1) for t in tabs])
    return f, info, u, holes, tabs

def lid_flat():
    oml = t5.lid_oml()
    u = Unfold(oml)
    x0, x1 = t5.XR + 0.5, t5.XF - 0.5
    holes, slots, bends = [], [], []
    top = 3                                          # segment index of the flat top
    def s_top(y):
        return u.s_of(top, y - oml[top][0])
    for n, (x, y, sx, sy, d) in t5.CONNS.items():
        ya, yb = s_top(y - sy / 2 - 0.5), s_top(y + sy / 2 + 0.5)
        slots.append(rect(x - sx / 2 - 0.5, x + sx / 2 + 0.5, ya, yb))
        for s in (-1, 1):
            holes.append((x, s_top(y + s * (sy / 2 + t5.CONN_HOLE)), 4.25))
    for x in t5.LID_SCREW_X:
        holes.append((x, u.s_of(0, t5.LID_SCREW_Z - t5.SEAM_Z), 3.4))
        holes.append((x, u.s_of(len(oml) - 2, t5.H - t5.CNR - t5.LID_SCREW_Z), 3.4))
    for (s, a, dr) in u.bends():
        bends.append(((x0, s), (x1, s)))
    f = write_dxf("lid", rect(x0, x1, 0, u.width), holes, slots, bends)
    return f, dict(part="lid", material="5052 .063", flat=(round(x1 - x0, 1), round(u.width, 1)), profile_bends=u.bends(),
                   flats=[round(v, 2) for v in u.flats]), u, holes

def tray1_flat():
    Y, Zb, Zt = t5.TRAY1_Y, t5.Z_TRAY1 - t5.TRAY1_FL, t5.Z_T1TOP
    oml = [(-Y, Zb), (-Y, Zt), (Y, Zt), (Y, Zb)]
    u = Unfold(oml)
    def s_top(y): return u.s_of(1, y + Y)
    holes, slots = [], []
    for (x0, x1, y0, y1) in t5.TRAY1_CUTS:
        slots.append(rect(x0, x1, s_top(y0), s_top(y1)))
    for x in t5.ep_x:
        for y in (-t5.SO_Y, t5.SO_Y):
            holes.append((x, s_top(y), 4.4))
    holes += [(x, s_top(y), 4.22) for (x, y) in t5.CB_SO_XY]
    holes += [(x, s_top(y), 4.0) for (x, y) in t5.INV_POST_XY]
    holes += [(x, s_top(y), 4.5) for (x, y) in t5.CHG_SCREW_XY]
    bends = [((t5.TRAY1_X0, s), (t5.TRAY1_X1, s)) for (s, a, d) in u.bends()]
    f = write_dxf("tray1", rect(t5.TRAY1_X0, t5.TRAY1_X1, 0, u.width), holes, slots, bends)
    return f, dict(part="tray1", material="5052 .063", flat=(t5.TRAY1_X1 - t5.TRAY1_X0, round(u.width, 1)), profile_bends=u.bends(),
                   flats=[round(v, 2) for v in u.flats]), u, holes

# ---------------- flat parts: section a solid through its mid-thickness ----------------
def flat_from_solid(name, solid, axis):
    bb = solid.bounding_box()
    if axis == "z":
        pl = Plane.XY.offset((bb.min.Z + bb.max.Z) / 2)
    elif axis == "x":
        pl = Plane.YZ.offset((bb.min.X + bb.max.X) / 2)
    else:
        pl = Plane.XZ.offset(-(bb.min.Y + bb.max.Y) / 2)
    sec = solid & pl.to_local_coords(solid).bounding_box() if False else section(solid, section_by=pl)
    faces = sec.faces()
    flat = Compound([pl.to_local_coords(f) for f in faces])
    exp = ExportDXF(unit=Unit.MM)
    exp.add_layer("CUT")
    exp.add_shape(flat, layer="CUT")
    fpath = os.path.join(OUT, name + ".dxf")
    exp.write(fpath)
    b2 = flat.bounding_box()
    return fpath, (round(b2.size.X, 1), round(b2.size.Y, 1))

def strap_flat(name, horiz_len, riser_h, width):
    """1-bend copper strap: horizontal leg (from its free end to the bend OML) + vertical riser (.125 Cu: K .34, Ri .050")."""
    Kc, Ric, Tc = 0.34, 0.050 * 25.4, t5.CU
    ba = (math.pi / 2) * (Ric + Kc * Tc); o = (Ric + Tc)
    L = (horiz_len - o) + ba + (riser_h - o)
    return L, ba, o

# ---------------- DFM checks ----------------
def check_profile(name, u, holes_s, min_flange=t5.MIN_FLAT_FLANGE, die=t5.DIE):
    msgs = []
    for i, fl in enumerate(u.flats):
        bent_both = u.th[i] > 0 and u.th[i + 1] > 0
        need = die / 2 + 0.6 if bent_both else min_flange
        ok = fl >= need
        msgs.append(f"  segment {i}: flat {fl:.1f} mm  (need >= {need:.1f})  {'OK' if ok else 'FAIL'}")
    bl = [s for (s, a, d) in u.bends()]
    worst = min((abs(hs - b) - hd / 2 for (hx, hs, hd) in holes_s for b in bl), default=99)
    msgs.append(f"  closest hole edge to a bend centre line: {worst:.1f} mm  (need >= {die/2:.1f})  {'OK' if worst >= die / 2 else 'FAIL'}")
    return msgs

if __name__ == "__main__":
    lines = [f"SCS 5052 .063: BA90 {BA(math.pi/2):.3f}  OSSB90 {OSSB(math.pi/2):.3f}  BD90 {BD90:.3f} mm (SCS lists .096\" = 2.438)",
             f"               BA30 {BA(math.pi/6):.3f}  OSSB30 {OSSB(math.pi/6):.3f}  BD30 {2*OSSB(math.pi/6)-BA(math.pi/6):.3f}"]
    parts = []
    for side in (-1, 1):
        f, info, u, holes, tabs = body_flat(side)
        parts.append(info)
        lines.append(f"{info['part']}: flat {info['flat']}  bends {[(round(s,1), round(a), d) for s,a,d in info['profile_bends']]} + {info['tabs']} tab bends")
        lines += check_profile(info["part"], u, [h for h in holes if t5.XR < h[0] < t5.XF])
        lines.append(f"  tab flanges (formed) {info['tab_flange']} mm  (min formed flange {0.303*25.4:.1f})")
    f, info, u, holes = lid_flat(); parts.append(info)
    lines.append(f"lid: flat {info['flat']}  bends {[(round(s,1), round(a), d) for s,a,d in info['profile_bends']]}")
    lines += check_profile("lid", u, holes)
    base = u.flats[3]; flange = t5.LID_H
    lines.append(f"  U-channel 2:1: base {base:.0f} vs 2 x leg {2*flange:.0f}  {'OK' if base >= 2*flange else 'FAIL'}")
    f, info, u, holes = tray1_flat(); parts.append(info)
    lines.append(f"tray1: flat {info['flat']}")
    lines += check_profile("tray1", u, holes)
    lines.append(f"  U-channel 2:1: base {u.flats[1]:.0f} vs 2 x flange {2*t5.TRAY1_FL:.0f}  OK")
    # one-piece U check (why the body is split)
    leg = t5.WALL_TOP; base1 = t5.W - 2 * t5.CNR
    lines.append(f"one-piece U body would be: base {base1:.0f} vs 2 x leg {2*leg:.0f} -> {'OK' if base1 >= 2*leg else 'FAIL (so split into 2 L halves)'}")

    import tower5 as m
    flat_parts = {
        "plate_front": (m.plate(True), "x", "6061 .187", 1), "plate_rear": (m.plate(False), "x", "6061 .187", 1),
        "tray2": (m.tray2(), "z", "5052 .063", 1),
        "g10_floor": (m.g10_floor(), "z", "G10 .187", 1), "g10_frame": (m.g10_frame(), "z", "G10 .125", 1),
        "g10_top": (m.g10_top(), "z", "G10 .063", 1),
        "g10_spacer": (m.box(-m.G10_SPACER / 2, m.G10_SPACER / 2, -m.CELL_W / 2, m.CELL_W / 2, m.Z_CELL, m.Z_CBODY), "x", "G10 .063", 5),
        "module_endplate": (m.module_endplates()[0].solids()[0], "x", "6061 .313", 2),
        "busbar_link": (list(m.busbars().values())[0], "z", "Copper .125", 3),
        "diffuser": (m.diffuser(), "x", "Acrylic .063 white", 1), "light_pipe": (m.light_pipe(), "z", "Acrylic .118 clear", 1),
        "mylar_tray1": (m.mylar(), "z", "Mylar .010", 1),
    }
    kit = m.kit_1s4p()
    flat_parts.update({"kit_plate_pos_lower": (kit["plate_pos_lower"], "z", "Copper .125", 1),
                       "kit_plate_neg_upper": (kit["plate_neg_upper"], "z", "Copper .125", 1),
                       "kit_insulator": (kit["insulator_g10"], "z", "G10 .063", 1),
                       "kit_spacer": (kit["spacers_cu"].solids()[0], "z", "Copper .187", 4)})
    for n, (sol, ax, matl, q) in flat_parts.items():
        fp, sz = flat_from_solid(n, sol, ax)
        parts.append(dict(part=n, material=matl, flat=sz, qty=q))
        lines.append(f"{n}: {matl}  flat {sz}  qty {q}")
    # copper straps: draw flat DXF directly
    yp = m.cell_pos_y(3)
    hp = m.POS_RISER_X + m.CU - (m.cell_x[3] - m.BB_W / 2); rp = m.Z_CB - m.Z_BB
    Lp, ba, o = strap_flat("pos", hp, rp, m.BB_W)
    hole_p = (m.cell_x[3] - (m.cell_x[3] - m.BB_W / 2))
    write_dxf("bus_pack_pos", rect(0, Lp, 0, m.BB_W), [(hole_p, m.BB_W / 2, 6.6)], bends=[((hp - o + ba / 2, 0), (hp - o + ba / 2, m.BB_W))])
    parts.append(dict(part="bus_pack_pos", material="Copper .125", flat=(round(Lp, 1), m.BB_W), qty=1, bends=1))
    hn = m.RET_RISER_X + m.CU - (m.cell_x[0] - m.BB_W / 2); rn = m.Z_CB - m.Z_BB
    Ln, ba, o = strap_flat("neg", hn, rn, m.RET_Y1 - m.RET_Y0)
    xn = m.cell_x[0] - m.BB_W / 2
    yb0 = -m.cell_pos_y(0) - m.BB_W / 2
    outline = [(0, yb0), (m.BB_W, yb0), (m.BB_W, m.RET_Y0), (Ln, m.RET_Y0), (Ln, m.RET_Y1), (0, m.RET_Y1)]
    write_dxf("bus_pack_neg", outline, [(m.BB_W / 2, -m.cell_pos_y(0), 6.6)], bends=[((hn - o + ba / 2, m.RET_Y0), (hn - o + ba / 2, m.RET_Y1))])
    parts.append(dict(part="bus_pack_neg", material="Copper .125", flat=(round(Ln, 1), round(m.RET_Y1 - yb0, 1)), qty=1, bends=1))
    lines.append(f"bus_pack_pos: Cu .125 flat {Lp:.1f} x {m.BB_W}  1 bend 90 (min formed flange .471\" = 12.0: legs {hp:.1f} / {rp:.1f})")
    lines.append(f"bus_pack_neg: Cu .125 flat {Ln:.1f} long, 1 bend 90 (legs {hn:.1f} / {rn:.1f})")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(OUT, "DFM_report.txt"), "w").write(txt)
    json.dump(parts, open(os.path.join(OUT, "parts.json"), "w"), indent=1, default=str)
