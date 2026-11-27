"""v17 top-down assembly proof (written order in versions/v17-option-d/README.md). Each step's rigid parts are swept out
along their insertion path through everything installed before them (screws, bolts, studs and flexible leads are not
swept); every screw head and nut fitted in a step gets a straight tool path (driver or socket); then the service check:
lid off, each MRBF fuse lifts out after only its own nut, lug and leads move, and the Z-strap comes out with every
other lead in place. Run: ~/.venvs/cad/bin/python cad/assembly_v17.py  (writes versions/v17-option-d/assembly-check.txt)"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build123d import Vector, extrude, Pos, Cylinder, Rot
import tower17 as t

TOL_V = 1.0
UP = Vector(0, 0, 1)

def sweep(shape, d, H):
    """Swept volume of shape moved by d*H: S union prism(f, d*H) for every face facing along d (assembly_v16 method)."""
    out = [shape]
    for f in shape.faces():
        try:
            dots = [f.normal_at(f.center()).dot(d)]
            for u, v in ((0.2, 0.2), (0.8, 0.8), (0.2, 0.8), (0.8, 0.2)):
                dots.append(f.normal_at(u, v).dot(d))
        except Exception:
            continue
        if max(dots) > 1e-6:                     # faces facing the direction of travel generate the swept prism
            try:
                out.append(extrude(f, amount=H, dir=d))
            except Exception:
                pass
    return out

def inter_v(a, b):
    x = a & b
    return x.volume if x is not None else 0.0

def overlap_bb(a, b):
    return not (a.min.X >= b.max.X or b.min.X >= a.max.X or a.min.Y >= b.max.Y or b.min.Y >= a.max.Y or a.min.Z >= b.max.Z or b.min.Z >= a.max.Z)

def hits(moving, placed, d, H, allow=()):
    res = []
    psol = {k: [(s, s.bounding_box()) for s in v.solids()] for k, v in placed.items()}
    for mn, ms in moving.items():
        for m in ms.solids():
            bb = m.bounding_box()
            lo = Vector(min(bb.min.X, bb.min.X + d.X * H), min(bb.min.Y, bb.min.Y + d.Y * H), min(bb.min.Z, bb.min.Z + d.Z * H))
            hi = Vector(max(bb.max.X, bb.max.X + d.X * H), max(bb.max.Y, bb.max.Y + d.Y * H), max(bb.max.Z, bb.max.Z + d.Z * H))
            pieces = None
            for pn, sols in psol.items():
                if any((mn.startswith(a) and pn.startswith(b)) or (mn.startswith(b) and pn.startswith(a)) for a, b in allow):
                    continue
                v = 0.0
                for ps, b in sols:
                    if b.min.X >= hi.X or b.max.X <= lo.X or b.min.Y >= hi.Y or b.max.Y <= lo.Y or b.min.Z >= hi.Z or b.max.Z <= lo.Z:
                        continue
                    if pieces is None:
                        pieces = [(pc, pc.bounding_box()) for pc in sweep(m, d, H) if pc.volume > 1e-3]
                    for pc, pb in pieces:
                        if not overlap_bb(pb, b):
                            continue
                        try:
                            xv = inter_v(pc, ps)
                            if xv > min(pc.volume, ps.volume) + 1.0:          # bad boolean: sample positions instead
                                xv = max(inter_v(m.moved(Pos(d.X * H * k / 40, d.Y * H * k / 40, d.Z * H * k / 40)), ps) for k in range(1, 41))
                            v = max(v, xv)
                        except Exception:
                            pass
                if v > TOL_V:
                    res.append((mn, pn, round(v, 1)))
    return res

# parts that are not swept: threaded in after the part arrives, or flexible
# connectors that mate sideways: name prefix -> (direction they pull out, mating travel mm). Swept out that far, then up.
MATE = {"plug_c13": (Vector(1, 0, 0), 25.0), "plug_pp45": (Vector(-1, 0, 0), 15.0), "plug_cn100": (Vector(-1, 0, 0), 8.0),
        "plug_cn301": (Vector(-1, 0, 0), 8.0), "plug_cn500": (Vector(1, 0, 0), 8.0), "plug_j2": (Vector(-1, 0, 0), 8.0),
        "plug_j3": (Vector(0, -1, 0), 8.0), "plug_j4": (Vector(1, 0, 0), 8.0), "plug_j5": (Vector(1, 0, 0), 8.0),
        "plug_j6": (Vector(0, 1, 0), 8.0), "plug_j7": (Vector(0, 1, 0), 8.0), "plug_j8": (Vector(0, 1, 0), 8.0), "plug_j9": (Vector(0, 1, 0), 8.0)}
BENCH_MATED = ("plug_c13", "plug_pp45", "plug_cn100", "plug_cn301", "plug_cn500")      # mated on the bench, ride in with their deck
NOSWEEP = ("screws_", "bolt_", "hw_ct_stud", "hw_sb_stud", "pem_", "w_", "nut", "flex_ccs", "pe_star", "pe_nut")

# (step, part prefixes, direction the parts LEAVE along (reverse of insertion), travel mm, note)
STEPS = [
    ("0 shell: body halves, feet, rear plate", ("body_half", "feet", "plate_rear", "screws_rear", "pem_body_lid"), None, 0, "reference: open body"),
    ("1 pack module (bench) lowered into the body", ("cell_", "g10_spacers", "module_endplates", "tnuts", "rods", "rodnuts", "g10_floor", "g10_frame",
        "g10_top", "so_lower", "so_upper", "so_studs", "screws_hold", "bus_A", "bus_B", "bus_C", "screws_term", "screws_tap", "flex_ccs",
        "bus_pack_pos", "bus_pack_neg", "bolt_nodeA", "bolt_5191", "panel_standoffs"), UP, 360.0,
        "carriage bolts into the two flange square holes before the straps go on (M8 node A, M10 5191)"),
    ("2 deck 1 (bench: charger, relay, bay standoffs, deck-2 posts screwed from below; charger leads P1a/P2 in the TB, P1a on relay 30, C13 plugged in) "
        "lowered; 4 screws into the end-plate standoffs",
        ("deck1", "charger_npb360", "term_chg", "screws_chg", "relay_", "screws_relay", "bay_standoffs", "screws_bay_bot", "posts_d2", "screws_d2_bot",
         "screws_deck1", "plug_c13", "plug_relay_30", "w_p1a"), UP, 360.0, "flex tail fed up through the deck slot; loose lead ends parked to the sides"),
    ("3 LED board + diffuser lowered in front of the module; M3 from the front", ("ledboard", "diffuser", "antenna", "screws_panelmount"), UP, 360.0,
        "front plate still off"),
    ("4 front plate + light pipe (slides in along -x)", ("plate_front", "screws_front", "pipe_f"), Vector(1, 0, 0), 40.0, ""),
    ("5 power bay (bench, built upside down, flipped) lowered onto the standoffs; node-A hole over its bolt; 5 screws from above",
        ("g10_bay", "shunt_", "sb175", "g10_sb_cheek", "screws_sb_cheek", "hw_sb", "contactor", "hw_ct", "nut_ct", "bus_mod", "bs2151_strap",
         "bs2151_body", "bs2151_stud", "bolt_2151", "nut_2151_m10", "bolt_nodeB", "bolt_foot", "screws_bay_top"), UP, 360.0,
        "on the bench: contactor and SB175 nuts under the plate; 2151 M10 thin nut before the SB175 + cheeks"),
    ("5b 2151 MRBF fuses (30 A, 50 A) onto their studs", ("bs2151_fuse",), UP, 150.0, ""),
    ("6 node-A nut + GND ring", ("ring_neg_gnd", "w_ring_gnd", "nut_nodeA"), UP, 120.0, ""),
    ("7 Blue Sea 5191 + MRBF 250 A on the + flange bolt, M10 nut", ("bs5191_", "nut_5191"), UP, 200.0, ""),
    ("8 deck 2 (bench: inverter + bridge posts screwed from below; PP45, CN100, CN301, CN500 plugged in) lowered onto its 4 posts; 4 nylon M4 from above",
        ("deck2", "inverter_nts400p", "screws_inv", "bridge_posts", "screws_bridge_posts_bot", "screws_d2_top", "plug_pp45", "plug_cn100",
         "plug_cn301", "plug_cn500"), UP, 360.0, "loose lead ends parked to the sides"),
    ("9 fan spacer + 40 mm fan lowered to the rear wall; M3 from outside, nyloc nuts inside", ("fan_spacer", "fan_4020", "screws_fan", "nuts_fan"), UP, 120.0, ""),
    ("10 BMS bridge (bench: standoffs, board, 4 x M3) lowered onto the posts; 4 M3 from above", ("g10_bms_bridge", "bms_", "screws_bms", "screws_bridge"), UP, 120.0, ""),
    ("11 charger leads: P1b on relay 87 + lug on the 2151 charger stud, P2 lug on node B", ("w_p1b", "w_p2", "lug_pos_chg", "lug_neg_chg",
        "plug_relay_87", "nut_2151_chg"), UP, 120.0, ""),
    ("12 inverter leads: P3 lug + LOAD+ ring on the 2151 inverter stud, P4 lug on node B, nuts", ("w_p3", "w_p4", "lug_pos_inv",
        "lug_neg_inv", "ring_pos_load", "w_ring_load", "nut_2151_inv", "nut_nodeB"), UP, 120.0, ""),
    ("13 signal harness: BMS J2-J9, shunt, coil, relay coil, LOAD+ run, NTC, LED, antenna", ("plug_j", "plug_shunt_j1",
        "plug_relay_85", "plug_relay_86", "plug_led", "w_h1", "w_h2_load", "w_h2_gnd", "fuseholder_load", "w_h3", "w_h5", "w_h4_led",
        "w_h4_ntc", "ntc_probe", "w_h6", "w_h7"), UP, 80.0, ""),
    ("14 Z-strap (service disconnect) on, B+ ring + lead, two nuts", ("strap_main", "nut_strap_top", "nut_foot", "ring_pos_bplus", "w_ring_bplus",
        "w_h2_bplus", "fuseholder_bplus"), UP, 150.0, ""),
    ("15 PE lug on the front +y screw (star washer, ring, nut)", ("screws_pe", "pe_star", "pe_nut", "pe_ring", "w_pe_barrel"), UP, 80.0, ""),
    ("16 lid: wire inlet, outlet, PE and button beside the pack (150 mm loops), then close", ("lid", "panel_", "pem_lid_panel", "screws_panel",
        "screws_lid", "w_a1", "w_a2", "w_a3", "w_h4_btn"), UP, 120.0, "unplug J8 first if the lid has to leave the bench"),
]
# screw groups / nuts that need a vertical tool at their step: name -> tool diameter [mm] (None = head diameter + 1)
TOOL_Z = {"screws_deck1": None, "screws_bay_top": None, "screws_d2_top": None, "screws_bridge": None, "screws_bms": None, "screws_term": None}
SOCKETS = {"nut_nodeA": 18.0, "nut_5191_m10": 23.5, "nut_2151_chg": 18.0, "nut_2151_inv": 18.0, "nut_nodeB": 18.0, "nut_strap_top": 18.0, "nut_foot": 15.0,
           "nut_2151_m10": 23.5}
HORIZ = {"nuts_fan": (Vector(1, 0, 0), 9.0, 40.0), "pe_nut": (Vector(-1, 0, 0), 10.0, 60.0)}
LID_OFF = ("lid", "panel_", "pem_lid_panel", "screws_panel", "screws_lid", "w_a1", "w_a2", "w_a3", "w_h4_btn")
SERVICE = (("bs5191_fuse_0", ("strap_main", "nut_strap_top", "nut_foot", "ring_pos_bplus", "w_ring_bplus", "w_h2_bplus", "fuseholder_bplus")),
           ("bs2151_fuse_0", ("nut_2151_chg", "lug_pos_chg", "w_p1b")),
           ("bs2151_fuse_1", ("nut_2151_inv", "lug_pos_inv", "w_p3", "ring_pos_load", "w_ring_load", "w_h2_load", "fuseholder_load")))
# mating contacts that a swept part legitimately starts in; the flex is flexible and fed through after (v16 rule)
ALLOW = [("w_", ""), ("flex_ccs", ""), ("bs2151_", "bs2151_"), ("bs5191_", "bs5191_"), ("relay_tab", "plug_relay"),
         ("plug_c13", "term_chg_c14"), ("plug_led", "ledboard_hdr")]

def tool_check(cyl, placed, skip):
    bad = []
    cb = cyl.bounding_box()
    for pn, ps in placed.items():
        if pn.startswith(skip):
            continue
        v = 0.0
        for s in ps.solids():
            if overlap_bb(cb, s.bounding_box()):
                v += inter_v(cyl, s)
        if v > TOL_V:
            bad.append((pn, round(v, 1)))
    return bad

def main(parts=None):
    t0 = time.time()
    parts = parts or t.build()
    placed, assigned, lines, ok = {}, set(), [], True
    for step, pre, d, H, note in STEPS:
        mv = {k: v for k, v in parts.items() if k.startswith(pre) and k not in assigned}
        assigned |= set(mv)
        if d is None:
            placed.update(mv); lines.append(f"[{step}] {len(mv)} parts ({note})"); continue
        movers = {k: v for k, v in mv.items() if not k.startswith(NOSWEEP)}
        straight = {k: v for k, v in movers.items() if not k.startswith(tuple(MATE)) or k.startswith(BENCH_MATED)}
        h = hits(straight, placed, d, H, ALLOW)
        for k, v in movers.items():
            m = next((MATE[n] for n in MATE if k.startswith(n)), None)
            if m is None or k.startswith(BENCH_MATED):
                continue
            md, ml = m
            h += hits({k: v}, placed, md, ml, ALLOW)                                   # unmate / mate stroke
            h += hits({k: v.moved(Pos(md.X * ml, md.Y * ml, md.Z * ml))}, placed, UP, H, ALLOW)
        # bench-mated connectors: also prove the stroke on the bench sub-assembly (against this step's own parts)
        for k, v in movers.items():
            if k.startswith(BENCH_MATED):
                md, ml = next(MATE[n] for n in MATE if k.startswith(n))
                own = {a: b for a, b in mv.items() if a != k and not a.startswith(NOSWEEP + ("plug_",))}
                h += hits({k: v}, own, md, ml, ALLOW)
        ok &= not h
        lines.append(f"[{step}] {len(mv)} parts; sweep {H:.0f} mm: " + ("CLEAR" if not h else f"{len(h)} HIT(S)") + (f"  ({note})" if note else ""))
        for x in h:
            lines.append(f"    hit: {x[0]} sweeps through {x[1]} ({x[2]} mm3)")
        placed.update(mv)
        # tools
        for k in mv:
            if k in TOOL_Z or (k.startswith("screws_bridge") and k == "screws_bridge"):
                res = []
                for s in mv[k].solids():
                    bb = s.bounding_box()
                    cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
                    dia = (bb.max.X - bb.min.X) + 1.0
                    cyl = Pos(cx, cy, bb.max.Z + 0.05 + 75.0) * Cylinder(dia / 2, 150.0)
                    res += tool_check(cyl, placed, (k,))
                ok &= not res
                lines.append(f"    driver on {k} ({len(mv[k].solids())} screws): " + ("clear" if not res else "BLOCKED by " + ", ".join(f"{a} ({v} mm3)" for a, v in res)))
            if k in SOCKETS:
                od = SOCKETS[k]; bb = mv[k].bounding_box()
                cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
                z0 = max(bb.min.Z + 0.5, bb.max.Z - 5.0)
                sock = Pos(cx, cy, z0 + 60.0) * Cylinder(od / 2, 120.0) - Pos(cx, cy, z0 + 60.0) * Cylinder(od / 2 - 2.0, 120.0)
                skip = (k, "bolt_", "bs5191_stud", "bs2151_stud")
                if k == "nut_2151_m10":
                    skip += ("sb175", "g10_sb_cheek", "screws_sb_cheek", "bs2151_fuse")          # bench: fitted before them
                res = tool_check(sock, placed, skip)
                ok &= not res
                lines.append(f"    socket {od:.1f} mm on {k}: " + ("clear" if not res else "BLOCKED by " + ", ".join(f"{a} ({v} mm3)" for a, v in res)))
            if k in HORIZ:
                dv, od, L = HORIZ[k]; res = []
                for s in mv[k].solids():
                    bb = s.bounding_box()
                    cy, cz = (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2
                    x0 = bb.max.X + 0.05 if dv.X > 0 else bb.min.X - 0.05
                    cyl = Pos(x0 + dv.X * L / 2, cy, cz) * (Rot(0, 90, 0) * Cylinder(od / 2, L))
                    res += tool_check(cyl, placed, (k, "screws_fan", "screws_pe"))
                ok &= not res
                lines.append(f"    nut driver {od:.0f} mm x {L:.0f} mm along {'+x' if dv.X > 0 else '-x'} on {k}: " + ("clear" if not res else "BLOCKED by " + ", ".join(f"{a} ({v} mm3)" for a, v in res)))
    lines.append("[service] lid off (lid, its connectors and leads beside the pack): each MRBF fuse lifts 150 mm after only its own nut, lug and leads move")
    closed = {k: v for k, v in placed.items() if not k.startswith(LID_OFF)}
    for fz, gone in SERVICE:
        mv = {k: v for k, v in parts.items() if k.startswith(fz)}
        obst = {k: v for k, v in closed.items() if not k.startswith(gone) and not k.startswith(fz) and not k.startswith(fz.rsplit("_fuse", 1)[0] + "_stud")}
        h = hits(mv, obst, UP, 150.0, ALLOW[1:])
        ok &= not h
        lines.append(f"    {fz} (moved: {', '.join(gone)}): " + ("CLEAR" if not h else "; ".join(f"{a} through {b} ({v} mm3)" for a, b, v in h)))
    gone = ("nut_strap_top", "nut_foot", "ring_pos_bplus", "w_ring_bplus", "w_h2_bplus", "fuseholder_bplus")
    obst = {k: v for k, v in closed.items() if not k.startswith(gone) and k != "strap_main" and not k.startswith(("bolt_foot", "bs5191_stud"))}
    h = hits({"strap_main": parts["strap_main"]}, obst, UP, 150.0, ())
    ok &= not h
    lines.append("    strap_main (service disconnect), every other lead in place: " + ("CLEAR" if not h else "; ".join(f"{a} through {b} ({v} mm3)" for a, b, v in h)))
    left = [k for k in parts if k not in assigned]
    ok &= not left
    lines.append(f"parts not in any step: {left}")
    lines.append("OVERALL: " + ("PASS" if ok else "FAIL"))
    lines.append(f"({time.time() - t0:.0f} s)")
    txt = "\n".join(lines); print(txt)
    d = os.path.join(HERE, "..", "versions", "v17-option-d"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "assembly-check.txt"), "w").write(
        "v17 top-down assembly check (cad/assembly_v17.py). Rigid parts swept out along their insertion path through\n"
        "everything installed before; screws/nuts get a driver or socket path (tool OD in mm).\n\n" + txt + "\n")
    return ok

if __name__ == "__main__":
    main()
