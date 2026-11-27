"""v17 clearance checks on the tower17 model:
  1. bare + copper to bare - copper >= 10 mm;
  2. bare pack copper (+ and -) to chassis metal >= 7 mm;
  3. pack copper to series bars (info);
  4. everything above the cells inside the module footprint x ±156, y ±79 (front zone, shell hardware and lid-top parts listed);
  5. nothing inside the box above the lid inside face except lid-mounted parts and the SB175;
  6. no wire or connector over an MRBF fuse lift-out prism (fuse footprint, fuse top -> lid);
  7. mains (A1-A3) to low-voltage wiring and bare pack copper >= 6 mm.
Run: ~/.venvs/cad/bin/python cad/clearance_v17.py   (writes versions/v17-option-d/clearance.txt)"""
import itertools, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tower17 as t
from tower17 import box

POS = ("bus_pack_pos", "bus_mod_in", "bus_mod_pos", "strap_main", "bs5191_strap", "bs5191_stud", "bs5191_fuse_0_bot", "bs5191_fuse_0_top",
       "bs2151_strap", "bs2151_stud", "bs2151_fuse_0_bot", "bs2151_fuse_0_top", "bs2151_fuse_1_bot", "bs2151_fuse_1_top", "bolt_5191", "nut_5191",
       "bolt_2151", "nut_2151", "nut_strap_top", "bolt_foot", "nut_foot", "hw_ct_stud", "nut_ct", "sb175_contact_pos", "hw_sb_stud_pos",
       "hw_sb_nut_pos", "relay_tab_30", "relay_tab_87", "lug_pos", "ring_pos")
NEG = ("bus_pack_neg", "shunt_bar", "shunt_pcb", "bus_mod_neg", "sb175_contact_neg", "hw_sb_stud_neg", "hw_sb_nut_neg", "bolt_nodeA", "nut_nodeA",
       "bolt_nodeB", "nut_nodeB", "lug_neg", "ring_neg")
COIL = ("relay_tab_85", "relay_tab_86")                       # battery-referenced coil terminals: chassis rule applies
MID = ("bus_A", "bus_B", "bus_C")
CHASSIS = ("body_half", "lid", "plate_front", "plate_rear", "screws_front", "screws_rear", "screws_pe", "pe_", "screws_lid", "pem_", "module_endplates",
           "rods", "rodnuts", "tnuts", "so_upper", "so_lower", "so_studs", "screws_hold", "screws_deck1", "charger_npb360", "screws_chg",
           "inverter_nts400p", "screws_inv", "screws_fan", "nuts_fan", "fan_spacer", "panel_standoffs", "screws_panelmount", "screws_panel",
           "panel_pushbutton")
# footprint exemptions (outside x ±156, y ±79 above the cells), each with its reason
SHELL = ("body_half", "lid", "plate_", "screws_front", "screws_rear", "screws_pe", "pe_", "screws_lid", "pem_", "feet", "screws_hold")
FRONT_ZONE = ("ledboard", "diffuser", "pipe_f", "antenna", "panel_standoffs", "screws_panelmount", "plug_led")
FRONT_WIRES = ("w_h4_led", "w_h7_coax", "w_a3_pe", "w_pe_barrel")                     # end on front-zone parts / the front-plate PE screw
REAR_WALL = ("fan_spacer", "screws_fan")                                              # rear-wall hardware behind x -156
LID_TOP = ("panel_", "screws_panel", "sb175_housing", "pem_lid_panel")                # through / above the lid
MODULE = ("cell_", "g10_spacers", "module_endplates", "rods", "rodnuts", "tnuts", "g10_floor", "g10_frame", "so_lower", "so_studs")
MAINS = ("w_a1", "w_a2", "w_a3", "plug_c13", "plug_cn500")
LV = ("w_h", "w_ring", "plug_j", "plug_shunt", "plug_cn100", "plug_cn301", "plug_led", "plug_relay", "fuseholder", "ntc", "bms_")

def sel(p, pre):
    return [k for k in p if k.startswith(pre)]

def mind(p, bbs, A, B, cutoff):
    """sorted list of (distance, a, b) for pairs closer than cutoff by bounding box."""
    rows = []
    for a, b in itertools.product(A, B):
        ba, bb = bbs[a], bbs[b]
        dx = max(bb.min.X - ba.max.X, ba.min.X - bb.max.X, 0); dy = max(bb.min.Y - ba.max.Y, ba.min.Y - bb.max.Y, 0)
        dz = max(bb.min.Z - ba.max.Z, ba.min.Z - bb.max.Z, 0)
        if (dx * dx + dy * dy + dz * dz) ** 0.5 > cutoff:
            continue
        d = min(sa.distance_to(sb) for sa in p[a].solids() for sb in p[b].solids())
        rows.append((d, a, b))
    return sorted(rows)

def main(parts=None):
    p = parts or t.build()
    bbs = {k: v.bounding_box() for k, v in p.items()}
    out, ok = [], True
    pos, neg = sel(p, POS), sel(p, NEG)
    for name, A, B, rule, cut in (("+ to -", pos, neg, 10.0, 60), ("pack copper to chassis", pos + neg + sel(p, COIL), sel(p, CHASSIS), 7.0, 25),
                                  ("pack copper to series bars", pos + neg, sel(p, MID), None, 30),
                                  ("mains to LV wiring / pack copper", sel(p, MAINS), sel(p, LV) + pos + neg, 6.0, 25)):
        r = mind(p, bbs, A, B, cut)
        m = r[0][0] if r else float("inf")
        good = rule is None or m >= rule - 0.05
        ok &= good
        out.append(f"--- {name}: minimum {m:.1f} mm" + (f"  (rule >= {rule:.0f}: {'PASS' if good else 'FAIL'})" if rule else "  (info)"))
        for d, a, b in r[:8]:
            out.append(f"      {a:22s} {b:24s} {d:6.1f} mm" + ("   <-- FAIL" if rule and d < rule - 0.05 else ""))
    # footprint
    viol, notes = [], {}
    for k, bb in bbs.items():
        if bb.max.Z <= t.Z_CBODY + 0.5 or k.startswith(SHELL) or k.startswith(MODULE):
            continue
        over = max(bb.max.X - t.FX, -t.FX - bb.min.X, bb.max.Y - t.FY, -t.FY - bb.min.Y)
        if over > 0.05:
            tag = next((n for n, pre in (("front zone", FRONT_ZONE), ("wire to front zone", FRONT_WIRES), ("rear wall", REAR_WALL), ("lid", LID_TOP)) if k.startswith(pre)), None)
            (notes.setdefault(tag, []) if tag else viol).append(f"{k} (+{over:.2f} mm: x {bb.min.X:.1f}..{bb.max.X:.1f}, y {bb.min.Y:.1f}..{bb.max.Y:.1f})")
    ok &= not viol
    out.append(f"--- footprint above the cells (x ±{t.FX:.0f}, y ±{t.FY:.0f}): {'PASS' if not viol else 'FAIL'}")
    out += [f"      OUTSIDE: {v}" for v in viol]
    for tag, v in notes.items():
        out.append(f"      exempt ({tag}): " + "; ".join(v))
    # lid height
    hi = [f"{k} z {bb.max.Z:.1f}" for k, bb in bbs.items() if bb.max.Z > t.LID_IN + 0.05 and not k.startswith(SHELL + LID_TOP + ("so_",))]
    top = max((bb.max.Z, k) for k, bb in bbs.items() if not k.startswith(SHELL + LID_TOP))
    ok &= not hi
    out.append(f"--- under the lid (inside z {t.LID_IN:.0f}): {'PASS' if not hi else 'FAIL ' + '; '.join(hi)}; highest internal part {top[1]} z {top[0]:.1f} ({t.LID_IN - top[0]:.1f} mm below)")
    # fuse lift-out prisms
    bad = []
    for f in sel(p, ("bs2151_fuse_", "bs5191_fuse_")):
        if not f.endswith("_body"):
            continue
        b = bbs[f]
        prism = box(b.min.X, b.max.X, b.min.Y, b.max.Y, b.max.Z + 1.2, t.LID_IN)
        for k in sel(p, ("w_", "plug_", "fuseholder", "ntc", "bms_", "g10_bms", "deck", "bridge", "inverter", "charger", "g10_sb", "sb175", "contactor")):
            if k.startswith(("w_ring", "ring_")):                # ring + barrel on that stud come off with its nut
                continue
            x = p[k] & prism
            v = x.volume if x is not None else 0.0
            if v > 0.5:
                bad.append(f"{f.replace('_body','')}: {k} ({v:.0f} mm3)")
    ok &= not bad
    out.append(f"--- fuse lift-out prisms clear of wiring and structure: {'PASS' if not bad else 'FAIL'}")
    out += [f"      {x}" for x in bad]
    out.append("OVERALL: " + ("PASS" if ok else "FAIL"))
    txt = "\n".join(out)
    print(txt)
    d = os.path.join(HERE, "..", "versions", "v17-option-d"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "clearance.txt"), "w").write("v17 clearance check (cad/clearance_v17.py)\n\n" + txt + "\n")
    return ok

if __name__ == "__main__":
    main()
