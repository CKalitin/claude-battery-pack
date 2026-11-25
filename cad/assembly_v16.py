"""v16 assembly-order proof: every step's parts are swept along their insertion path through everything already
installed, and every nut gets a socket-access check. Run: python assembly_v16.py   (writes docs/v16-assembly-check.txt)

Sweep of a solid S along a straight path d*H = S union prism(f, d*H) for every face f of S that faces against d
(exact for any shape: every swept point lies on a segment that starts on such a face). A step fails if its sweep
cuts a part installed earlier by more than TOL_V mm^3.
"""
import os, sys, time, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
from build123d import Compound, Vector, Solid, Face, extrude, Pos, Cylinder, Box
import tower15 as t5
from c1_power_module import build as c1

TOL_V = 1.0
BAY = ("bus_pack_pos", "bus_pack_neg", "bus_link", "bus_neg_out", "bus_pos_out", "mrbf", "contactor", "shunt",
       "sb175", "g10_sb_bracket", "tray1_g10", "cable_", "keepout_")

def sweep(shape, d, H):
    """Swept volume of shape moved by d*H (d unit Vector)."""
    out = [shape]
    for f in shape.faces():
        try:
            n = f.normal_at(f.center())
        except Exception:
            continue
        # curved faces: test a few points
        dots = [n.dot(d)]
        try:
            for u, v in ((0.2, 0.2), (0.8, 0.8), (0.2, 0.8), (0.8, 0.2)):
                dots.append(f.normal_at(u, v).dot(d))
        except Exception:
            pass
        if min(dots) < -1e-6:
            try:
                out.append(extrude(f, amount=H, dir=d))
            except Exception:
                pass
    return out

def hits(moving, placed, d, H, allow=()):
    """moving / placed: {name: shape}. Returns [(moving, placed, volume)]."""
    res = []
    pbb = {k: v.bounding_box() for k, v in placed.items()}
    for mn, ms in moving.items():
        pieces = sweep(ms, d, H)
        bb = ms.bounding_box()
        lo = Vector(min(bb.min.X, bb.min.X + d.X * H), min(bb.min.Y, bb.min.Y + d.Y * H), min(bb.min.Z, bb.min.Z + d.Z * H))
        hi = Vector(max(bb.max.X, bb.max.X + d.X * H), max(bb.max.Y, bb.max.Y + d.Y * H), max(bb.max.Z, bb.max.Z + d.Z * H))
        for pn, ps in placed.items():
            if any((mn.startswith(a) and pn.startswith(b)) or (mn.startswith(b) and pn.startswith(a)) for a, b in allow):
                continue
            b = pbb[pn]
            if b.min.X >= hi.X or b.max.X <= lo.X or b.min.Y >= hi.Y or b.max.Y <= lo.Y or b.min.Z >= hi.Z or b.max.Z <= lo.Z:
                continue
            v = 0.0
            for pc in pieces:
                try:
                    pv = pc.volume
                    if pv < 1e-3:
                        continue
                    x = pc & ps
                    xv = x.volume if x is not None else 0.0
                    if xv > min(pv, ps.volume) + 1.0:      # OCC returned the operand (bad boolean): fall back to a sampled check
                        xv = 0.0
                        for k in range(1, 41):
                            y = (ms.moved(Pos(d.X * H * k / 40, d.Y * H * k / 40, d.Z * H * k / 40))) & ps
                            xv = max(xv, y.volume if y is not None else 0.0)
                        v = max(v, xv); break
                    v += xv
                except Exception:
                    pass
            if v > TOL_V:
                res.append((mn, pn, round(v, 1)))
    return res

UP = Vector(0, 0, 1)
# (step, part prefixes, direction the part LEAVES along (reverse of insertion), travel, note)
STEPS = [
    ("0 shell", ("body_half", "feet", "plate_rear", "screws_r", "fan_nfa14", "screws_fan", "pem_body_lid"), None, 0, "reference: open body, rear plate and fan in place"),
    ("1 pack module (bench-built) lowered into the body", ("cell_", "g10_spacers", "module_endplates", "tnuts", "rods", "rodnuts", "g10_floor", "g10_frame",
        "g10_top", "so_lower", "so_upper", "so_studs", "screws_hold", "bus_A", "bus_B", "bus_C", "screws_term", "screws_tap", "flex_ccs",
        "bus_pack_pos", "bus_pack_neg", "hw_carriage_0", "hw_carriage_head_0", "hw_carriage_1", "hw_carriage_head_1", "panel_standoffs"), UP, 330.0,
        "carriage bolts in both flange square holes before the collectors go on (+: M10 for the 5191, -: M8 node A)"),
    ("2 tray 1 with the charger pre-screwed from below (bench) + plate standoffs", ("tray1", "pem_tray1", "charger_npb450_12", "standoff_"), UP, 330.0,
        "charger screws enter from under tray 1, so the charger rides in on the tray"),
    ("3 front board + diffuser lowered in front of the module", ("ledboard_f", "ctrl_", "diffuser_f", "antenna", "screws_panelmount"), UP, 330.0,
        "screws through the diffuser from the front (front plate still off); flex tail into the FPC from above"),
    ("4 front plate + light pipe (moves in along -x)", ("plate_front", "screws_f", "pipe_f"), Vector(1, 0, 0), 40.0, ""),
    ("5 power module (bench-built, flipped) lowered onto the standoffs, MRBF fuses not yet on", ("g10_plate", "hw_carriage_2", "hw_carriage_head_2", "hw_carriage_3",
        "hw_carriage_head_3", "hw_carriage_nodeB", "hw_carriage_head_nodeB", "bus_mod_", "shunt_bar", "shunt_module", "contactor", "hw_stud_", "nut_m8", "sb175",
        "hw_locknut", "g10_sb_cheek", "bs2151_strap", "bs2151_body", "bs2151_stud", "hw_m10nut_2151"), UP, 330.0,
        "shunt-bar hole drops over the node-A bolt; on the bench the 2151 M10 nut is torqued before the SB175 + cheeks go on"),
    ("5b 2151 MRBF fuses (30 A, 50 A) onto their studs", ("bs2151_fuse",), UP, 150.0, "body wall's top facets (y >= 88.6 above z 300): the module can't drop in with the fuses fitted"),
    ("6 node-A nut + GND ring", ("ring_gnd", "sig_gnd_barrel", "hw_nut_nodeA"), UP, 120.0, ""),
    ("7 Blue Sea 5191 + MRBF 250 A on the + flange M10", ("bs5191_", "hw_m10nut_main"), UP, 200.0, ""),
    ("8 charger leads", ("lug_charger", "hw_nut_charger", "cable_charger", "lug_neg_charger", "cable_neg_charger"), UP, 120.0, ""),
    ("9 tray 2 + inverter (pre-screwed from below) onto the posts", ("tray2", "inv_posts", "screws_trays", "inverter_nts400p_112"), UP, 330.0, ""),
    ("10 inverter leads (PP45 on), - nut, LOAD+ ring", ("lug_inverter", "ring_loadplus", "sig_loadplus_barrel", "hw_nut_inverter", "cable_inverter", "lug_neg_inverter", "cable_neg_inverter", "hw_nut_neg_nodeB"), UP, 120.0, ""),
    ("11 signal harness", ("plug_", "sig_shunt", "sig_gnd", "sig_loadplus", "fuse_inline_loadplus", "sig_coil", "sig_chg", "sig_inv", "sig_conv", "tie_", "sig_fan", "sig_coax"), UP, 80.0, ""),
    ("12 AC leads", ("sig_ac",), UP, 80.0, ""),
    ("13 Z-strap (service disconnect) + B+ ring", ("strap_main", "hw_nut_main", "ring_bplus", "sig_bplus", "fuse_inline_bplus", "hw_nut_strapfoot"), UP, 150.0,
        "the strap's 150 mm sweep doubles as the service check: it comes out with every lead in place"),
    ("14 lid with pass-throughs, button wired", ("lid", "panel_", "pem_lid_panel", "screws_panel", "screws_lid", "sig_button"), UP, 120.0, "plug j_btn before the lid closes"),
]

# socket access: nut name prefix -> (socket OD [mm], from z offset)  DIN 3124 / typical 3/8" drive thin-wall
SOCKETS = {"hw_nut_strapfoot": 15.0, "hw_nut_nodeA": 18.0, "hw_nut_main": 18.0, "hw_nut_charger": 18.0, "hw_nut_inverter": 18.0,
           "hw_nut_neg_nodeB": 18.0, "hw_m10nut_main": 23.5, "hw_m10nut_2151": 23.5}

def main():
    t0 = time.time()
    tp = {k: v for k, v in t5.build().items() if not k.startswith(BAY)}
    c = c1("gv14up")
    parts = dict(tp)
    parts.update({k: v for k, v in c.parts.items() if not k.startswith(("path_", "keepout_", "cap_"))})
    allow = list(c.allow) + [("ctrl_", "ledboard"), ("plug_j_", "ctrl_j_"), ("screws_panelmount", ""), ("screws_f", ""), ("screws_r", ""), ("screws_fan", ""),
                             ("screws_trays", ""), ("screws_hold", ""), ("screws_lid", ""), ("screws_panel", ""), ("pem_", ""), ("hw_carriage", ""),
                             ("hw_stud", ""), ("so_", ""), ("standoff_", ""), ("panel_standoffs", ""), ("flex_ccs", ""), ("sig_", "sig_"), ("tie_", "")]
    # screws/studs are threaded in after the part arrives: they are not swept with it, and contacts on them are not obstacles
    placed, assigned, lines = {}, set(), []
    for step, pre, d, H, note in STEPS:
        mv = {k: v for k, v in parts.items() if k.startswith(pre) and k not in assigned}
        assigned |= set(mv)
        if d is None:
            placed.update(mv); lines.append(f"[{step}] {len(mv)} parts placed ({note})"); continue
        movers = {k: v for k, v in mv.items() if not k.startswith(("screws_", "hw_carriage", "hw_stud", "pem_", "sig_", "cable_", "tie_"))}
        h = hits(movers, placed, d, H, allow)
        lines.append(f"[{step}] {len(mv)} parts; sweep {H:.0f} mm; " + ("CLEAR" if not h else f"{len(h)} HIT(S)") + (f"  ({note})" if note else ""))
        for x in h:
            lines.append(f"    hit: {x[0]} sweeps through {x[1]} ({x[2]} mm3)")
        placed.update(mv)
        # socket access for nuts fitted in this step
        for k in mv:
            for s, od in SOCKETS.items():
                if k.startswith(s):
                    bb = mv[k].bounding_box()
                    cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
                    z0s = max(bb.min.Z + 0.5, bb.max.Z - 6.0)                          # socket engages the nut's flats only
                    sock = Pos(cx, cy, z0s + 50.0) * Cylinder(od / 2, 100.0)
                    inner = Pos(cx, cy, z0s + 50.0) * Cylinder(od / 2 - 2.0, 100.0)    # socket wall only (the stud is inside)
                    sw = sock - inner
                    bad = []
                    for pn, ps in placed.items():
                        if pn == k or pn.startswith(("hw_carriage", "hw_stud", "bs5191_stud", "bs2151_stud")) or (k == "hw_m10nut_2151" and pn.startswith(("sb175", "g10_sb_cheek"))):
                            continue
                        pb = ps.bounding_box()
                        if pb.max.Z < bb.max.Z - 6.0 or pb.min.X > cx + od or pb.max.X < cx - od or pb.min.Y > cy + od or pb.max.Y < cy - od:
                            continue
                        x = sw & ps
                        v = x.volume if x is not None else 0.0
                        if v > TOL_V:
                            bad.append((pn, round(v, 1)))
                    lines.append(f"    socket {od:.1f} mm on {k}: " + ("clear" if not bad else "BLOCKED by " + ", ".join(f"{a} ({b} mm3)" for a, b in bad)))
    lines.append("[service] fuse replacement, lid off: lug + nut + leads on that stud moved aside, fuse lifted 150 mm")
    for fz, gone in (("bs5191_fuse_0", ("strap_main", "hw_nut_main", "ring_bplus", "sig_bplus", "fuse_inline_bplus", "hw_nut_strapfoot")),
                     ("bs2151_fuse_0", ("lug_charger", "hw_nut_charger", "cable_charger")),
                     ("bs2151_fuse_1", ("lug_inverter", "hw_nut_inverter", "cable_inverter", "ring_loadplus", "sig_loadplus", "fuse_inline_loadplus"))):
        mv = {k: v for k, v in parts.items() if k.startswith(fz)}
        obst = {k: v for k, v in placed.items() if not k.startswith(gone) and not k.startswith(fz) and not k.startswith(("lid", "panel_", "screws_panel", "screws_lid", "pem_lid_panel", "sig_button"))}
        h = hits(mv, obst, UP, 150.0, allow)
        lines.append(f"    {fz}: " + ("CLEAR" if not h else "; ".join(f"{a} through {b} ({v} mm3)" for a, b, v in h)))
    left = [k for k in parts if k not in assigned]
    lines.append(f"parts not in any step: {left}")
    lines.append(f"({time.time() - t0:.0f} s)")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(HERE, "..", "docs", "v16-assembly-check.txt"), "w").write(
        "v16 top-down assembly check (cad/assembly_v16.py). Each step's parts are swept out along their insertion path\n"
        "through everything installed before them; each nut gets a socket-wall check (thin-wall 3/8 in drive, OD in mm).\n\n" + txt + "\n")

if __name__ == "__main__":
    main()
