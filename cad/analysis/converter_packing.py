"""Converter search 2026-11-27: 3D box packing of each serious charger/inverter candidate inside the cell-module
footprint (x +-156, y +-79: the module with its end plates), with every other space claim placed.

Pack first, claim second (handoff-converters.md 2e). Each option is a list of axis-aligned boxes. The checker reports:
  - anything outside the footprint (x, y) or above the lid,
  - every overlapping pair (keep-outs included) that is not in the option's ALLOW list,
  - + to - copper gaps < 10 mm,
  - MRBF fuse lift-out: nothing above a fuse up to the lid,
and draws a plan view per level plus an x-z elevation.

Dimensions: manufacturer drawings unless flagged UNCONF (see docs/converters.md section 4).
Run:  ~/.venvs/cad/bin/python cad/analysis/converter_packing.py      (writes PNGs to versions/v16-c1-power-module/renders/)
"""
import os, sys, itertools
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders")
FX, FY = 156.0, 79.0                 # footprint half-sizes: module 312 x 158 incl. end plates (tower15 STACK_L, EP_W)
Z_BB = 210.0                         # series bars / collectors top (lib.Z_BAR_TOP)
Z_D1 = 221.6                         # deck-1 G10 top (tower15 Z_T1TOP: end-plate standoffs)
G10 = 3.175

COL = {"chg": "#aed6f1", "inv": "#a9dfbf", "pos": "#f1948a", "neg": "#85c1e9", "ct": "#f8c471", "sb": "#bb8fce",
       "bms": "#58d68d", "fan": "#d5dbdb", "keep": "none", "lid": "#f9e79f", "g10": "#fcf3cf", "cell": "#eeeeee",
       "combo": "#5dade2", "fuse": "#f5b041"}

class B:
    def __init__(s, name, x0, x1, y0, y1, z0, z1, kind, label=None, src=""):
        s.n, s.k, s.lab, s.src = name, kind, label, src
        s.x0, s.x1, s.y0, s.y1, s.z0, s.z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    def gap(s, o):
        """Separation distance (0 if overlapping) and overlap volume."""
        dx = max(o.x0 - s.x1, s.x0 - o.x1, 0); dy = max(o.y0 - s.y1, s.y0 - o.y1, 0); dz = max(o.z0 - s.z1, s.z0 - o.z1, 0)
        return (dx * dx + dy * dy + dz * dz) ** 0.5
    def overlaps(s, o, tol=0.01):
        return (min(s.x1, o.x1) - max(s.x0, o.x0) > tol and min(s.y1, o.y1) - max(s.y0, o.y0) > tol
                and min(s.z1, o.z1) - max(s.z0, o.z0) > tol)

def check(opt):
    parts, allow, lid = opt["parts"], opt.get("allow", []), opt["lid_in"]
    issues = []
    for p in parts:
        if p.k in ("cell",):
            continue
        if p.x0 < -FX - 0.01 or p.x1 > FX + 0.01 or p.y0 < -FY - 0.01 or p.y1 > FY + 0.01:
            issues.append(f"OUTSIDE footprint: {p.n} x[{p.x0:.1f},{p.x1:.1f}] y[{p.y0:.1f},{p.y1:.1f}]")
        if p.z1 > lid + 0.01 and p.k not in ("sb", "lid"):
            issues.append(f"ABOVE lid {lid:.1f}: {p.n} z1 {p.z1:.1f}")
    def allowed(a, b):
        return any((a.n.startswith(x) and b.n.startswith(y)) or (a.n.startswith(y) and b.n.startswith(x)) for x, y in allow)
    for a, b in itertools.combinations(parts, 2):
        if a.k == "cell" or b.k == "cell":
            continue
        if a.k == "keep" and b.k == "keep":
            continue
        if a.overlaps(b) and not allowed(a, b):
            issues.append(f"CLASH {a.n} x {b.n}")
        if {a.k, b.k} == {"pos", "neg"}:
            g = a.gap(b)
            if g < 10.0 and not allowed(a, b):
                issues.append(f"+/- GAP {g:.1f} mm < 10: {a.n} x {b.n}")
    for f in [p for p in parts if p.k == "fuse"]:                 # MRBF lift-out column: fuse top -> lid
        col = B("liftout_" + f.n, f.x0, f.x1, f.y0, f.y1, f.z1, lid, "keep")
        for p in parts:
            if p is f or p.k in ("keep", "cell", "lid") or p.n.startswith(f.n.split("_")[0] + "_nut"):
                continue
            if col.overlaps(p) and not allowed(col, p):
                issues.append(f"FUSE LIFT-OUT blocked: {f.n} by {p.n}")
    return issues

def plot(opt, fname):
    parts, lid = opt["parts"], opt["lid_in"]
    levels = opt["levels"]                                         # [(title, z_lo, z_hi)]
    n = len(levels) + 1
    fig, axs = plt.subplots(n, 1, figsize=(11, 4.3 * n), dpi=130)
    for ax, (title, zlo, zhi) in zip(axs, levels):
        ax.add_patch(Rectangle((-FX, -FY), 2 * FX, 2 * FY, fc="#fafafa", ec="#c0392b", lw=2.2, zorder=0))
        ax.text(-FX, FY + 4, "cell module footprint 312 × 158 (end plates incl.)", color="#c0392b", fontsize=7.5)
        sel = [p for p in parts if p.z1 > zlo and p.z0 < zhi and p.k not in ("cell",)]
        for p in sorted(sel, key=lambda q: (q.k == "keep", q.z0)):
            if p.k == "keep":
                ax.add_patch(Rectangle((p.x0, p.y0), p.x1 - p.x0, p.y1 - p.y0, fc="none", ec="#7f8c8d", lw=0.8, ls="--", hatch="///", alpha=0.6))
            else:
                ax.add_patch(Rectangle((p.x0, p.y0), p.x1 - p.x0, p.y1 - p.y0, fc=COL.get(p.k, "#ccc"), ec="#333", lw=0.8, alpha=0.92))
            if p.lab:
                ax.text((p.x0 + p.x1) / 2, (p.y0 + p.y1) / 2, p.lab, ha="center", va="center", fontsize=6.3,
                        color="#555" if p.k == "keep" else "#000")
        ax.set_xlim(-FX - 12, FX + 12); ax.set_ylim(-FY - 10, FY + 14); ax.set_aspect("equal")
        ax.set_title(f"{title}   (z {zlo:.0f}–{zhi:.0f})", fontsize=9.5)
        ax.set_xlabel("x [mm]  rear ← → front"); ax.set_ylabel("y [mm]")
    ax = axs[-1]                                                     # elevation (x-z), every part projected
    ax.add_patch(Rectangle((-FX, Z_BB - 200), 2 * FX, 200, fc="#eeeeee", ec="#999"))
    ax.text(0, Z_BB - 18, "cells (LF105 × 8, 4S2P)", ha="center", fontsize=8, color="#666")
    for p in sorted(parts, key=lambda q: -(q.y1)):
        if p.k in ("cell",):
            continue
        if p.k == "keep":
            ax.add_patch(Rectangle((p.x0, p.z0), p.x1 - p.x0, p.z1 - p.z0, fc="none", ec="#7f8c8d", lw=0.6, ls="--"))
        else:
            ax.add_patch(Rectangle((p.x0, p.z0), p.x1 - p.x0, p.z1 - p.z0, fc=COL.get(p.k, "#ccc"), ec="#333", lw=0.6, alpha=0.55))
    ax.axhline(lid, color="#c0392b", lw=1.2, ls="-."); ax.text(-FX, lid + 2, f"lid inside z {lid:.0f}  ({lid - 201.85:.0f} mm above the can tops; v16.3: 116)", fontsize=7.5, color="#c0392b")
    ax.axvline(-FX, color="#c0392b", lw=1.5); ax.axvline(FX, color="#c0392b", lw=1.5)
    ax.set_xlim(-FX - 12, FX + 12); ax.set_ylim(Z_BB - 30, max(lid + 30, max(p.z1 for p in parts) + 10)); ax.set_aspect("equal")
    ax.set_title("side elevation (x–z), all parts projected; red verticals = footprint ends", fontsize=9.5)
    ax.set_xlabel("x [mm]"); ax.set_ylabel("z [mm]")
    issues = check(opt)
    verdict = "✓ packs: 0 issues" if not issues else f"✗ {len(issues)} issues"
    fig.suptitle(f"{opt['title']}\n{verdict}", fontsize=11.5, y=0.997)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    out = os.path.join(OUT, fname)
    fig.savefig(out); plt.close(fig)
    return out, issues

# ------------------------------------------------------------------ shared parts
def cells():
    return [B("cells", -FX, FX, -FY, FY, Z_BB - 200, Z_BB, "cell")]

def lid_conns(lid, inlet_xy, outlet_xy, button_xy):
    """Lid connectors: body depth below the lid inside face (tower15 CONNS)."""
    (ix, iy), (ox, oy), (bx, by) = inlet_xy, outlet_xy, button_xy
    return [B("lid_inlet_c14", ix - 10, ix + 10, iy - 13.5, iy + 13.5, lid - 25, lid, "lid", "C14\ninlet"),
            B("lid_outlet_5-15", ox - 15, ox + 15, oy - 19, oy + 19, lid - 30, lid, "lid", "5-15R\noutlet"),
            B("lid_button", bx - 9.5, bx + 9.5, by - 9.5, by + 9.5, lid - 30, lid, "lid", "btn")]

def bay_strip(y_in, zp1, x_front, lid):
    """Power bay in a strip along the -y wall, y in [-79, y_in], copper plane top at zp1.
    Rear -> front: shunt (pack- arrives from the rear cells), SB175, 2151 on the + rail, GV14, 5191 at the + riser.
    Returns boxes. Dims: tesla-shunt.md, contactor-mounting.md, lib.BS (Blue Sea drawings, UNCONF), sb175_bbs."""
    zp0 = zp1 - G10 - 3.175
    p = []
    p.append(B("g10_bayplate", -FX, x_front, -FY, y_in, zp0 - 6.35, zp0, "g10", None))
    # shunt: bar 83.5 x 35 + PCB overhang 8 (+y side), flat; node A rear, node B front
    p.append(B("shunt", -150, -66.5, -77, -34, zp0, zp1 + 10.2, "neg", "Tesla shunt\n83.5 × 43"))
    p.append(B("keep_shunt_conn", -150, -132, -42, -34, zp1 + 10.2, zp1 + 45, "keep", None))
    # - rail: node B -> SB175 - contact (outer lane), + rail: 2151 -> SB175 + contact (inner lane)
    p.append(B("rail_neg", -74, -14, -77, -57, zp0, zp1, "neg", "− rail"))
    p.append(B("sb175", -60, -4.4, -77, -33, zp1, lid + 8.4, "sb", "SB175 + G10 cheeks\n55.6 × 44"))
    p.append(B("rail_pos", -26, 110, -47, -27, zp0, zp1, "pos", None))
    p.append(B("bs2151", -2, 86.5, -51, -24.5, zp1, zp1 + 31.8, "pos", "2151 + 2 MRBF"))
    p.append(B("bs2151_fuse_chg", 20, 47.8, -49, -26.5, zp1 + 31.8, zp1 + 48.1, "fuse", None))
    p.append(B("bs2151_fuse_inv", 50, 77.8, -49, -26.5, zp1 + 31.8, zp1 + 48.1, "fuse", None))
    return p

# ------------------------------------------------------------------ option D: NPB-360-12TB + NTS-400P-112
def opt_D(chg=("chg_npb360", 182.7, 96.0, 49.0, "NPB-360-12TB\n182.7 × 96 × 49 (fan, 20 A)"), title=None):
    lid = 333.0
    zp1 = lid + 1.6 + 8.4 - 89.8          # SB175 mating face 8.4 above the lid top (C1), contacts 89.8 below it
    p = cells()
    p.append(B("g10_deck1", -FX, FX, -FY, FY, Z_D1 - G10, Z_D1, "g10"))
    # charger flat on deck 1 against +y; DC (TB) end at the rear, AC (C14) end at the front
    cn, cl, cw, ch, clab = chg
    cy0 = FY - cw
    p.append(B(cn, -126, -126 + cl, cy0, FY, Z_D1, Z_D1 + ch, "chg", clab))
    p.append(B("keep_chg_dc_tb", -156, -126, cy0 + 20, cy0 + 70, Z_D1, Z_D1 + ch, "keep", "TB 30"))
    p.append(B("keep_chg_ac_c13", -126 + cl, -86 + cl, FY - 51, FY - 6, Z_D1, Z_D1 + ch, "keep", "C13\n36+4"))
    # deck 2: G10 over the charger only (the strip stays open to the lid: fuse lift-out)
    z2 = Z_D1 + ch + 2.5 + G10
    p.append(B("g10_deck2", -156, 120, -21.5, FY, z2 - G10, z2, "g10"))
    # inverter flat, DC end at the rear (PP45 + MEAN WELL's 10 CFM fan 5 cm from the DC face), AC (CN500) at the front
    p.append(B("inv_nts400p", -86, 100, -21.5, FY, z2, z2 + 34, "inv", "NTS-400P-112\n186 × 100.5 × 34"))
    p.append(B("keep_inv_pp45", -128, -86, 20, 50, z2, z2 + 34, "keep", "PP45\n42"))
    p.append(B("fan_inv_4020", -156, -136, 9, 49, z2, z2 + 40, "fan", "40×40\nfan"))
    p.append(B("keep_inv_cn500", 100, 120, 15, 55, z2, z2 + 34, "keep", "CN500\n20"))
    # separate BMS board, flat over the inverter on 6 mm standoffs, parts <= 10 mm
    # pcb lane space claim 2026-11-27 (spec/requests/pcb-bms-space-claim.md): 150 x 90, top <= 12 mm incl. mated plugs,
    # 25 mm right-angle plug room beyond -x, and beyond -y for x -105..-62. Carried by a G10 .125 bridge over the inverter
    # (no holes in the NTS-400P), the bridge on 4 posts standing on deck 2 beyond the inverter's ends.
    zr = z2 + 34 + 1.0
    p.append(B("g10_bms_bridge", -112, 108, -15, 75, zr, zr + G10, "g10", None))
    for i, (x, y) in enumerate(((-109, -12), (-109, 72), (105, -12), (105, 72))):   # M3 standoffs at the bridge corners
        p.append(B(f"bms_post_{i}", x - 3, x + 3, y - 3, y + 3, z2, zr, "g10", None))
    zb = zr + G10 + 3.0
    p.append(B("bms_board", -105, 45, -15, 75, zb, zb + 1.6, "bms", "BMS board 150 × 90 (pcb lane claim)"))
    p.append(B("keep_bms_parts", -105, 45, -15, 75, zb + 1.6, zb + 13.6, "keep", None))
    p.append(B("keep_bms_plugs_x", -130, -105, -15, 75, zb + 1.6, zb + 13.6, "keep", "plugs"))
    p.append(B("keep_bms_plugs_y", -105, -62, -40, -15, zb + 1.6, zb + 13.6, "keep", "plugs"))
    # power bay strip (y -79 .. -20)
    p += bay_strip(-20.0, zp1, 156, lid)
    # GV14 (body 59.9 x 55.7, flange 72.5) and the 5191 on the + riser in the front corner
    p.append(B("ct_gv14", 96.1, 156, -79, -23.3, zp1 + 2, zp1 + 59.9, "ct", "GV141BAX\n59.9 × 55.7"))
    p.append(B("pos_riser", 122, 148, -77, -46, Z_BB, zp1, "pos", None))          # + collector Z-tab (cells 7-8), as C1
    p.append(B("pos_inbar", 122, 148, -46, -12, zp1 - 3.175, zp1, "pos", None))    # riser flange -> 5191 tab (under the GV14)
    p.append(B("bs5191", 122, 147, -20, 40.9, zp1, zp1 + 31.5, "pos", "5191\n(MRBF 250)"))
    p.append(B("bs5191_fuse", 121, 148.8, -19, 4, zp1 + 31.5, zp1 + 47.8, "fuse", None))
    p += lid_conns(lid, (138, 63), (138, 25), (-120, -55))
    return dict(title=title or "Option D: MEAN WELL NPB-360-12TB (20 A) + NTS-400P-112 (400 W) + 40 mm fan; bay strip on −y",
                parts=p, lid_in=lid,
                levels=[("deck 1: charger + power-bay strip", Z_D1, Z_D1 + ch), ("deck 2: inverter (strip open above)", z2, z2 + 34),
                        ("under the lid: BMS board, lid connectors, SB175", z2 + 34, lid)],
                allow=[("g10_", "g10_"), ("g10_bayplate", "shunt"), ("g10_bayplate", "rail_"), ("rail_neg", "shunt"), ("rail_neg", "sb175"),
                       ("rail_pos", "sb175"), ("rail_pos", "bs2151"), ("g10_deck1", "pos_riser"), ("g10_bayplate", "pos_riser"),
                       ("keep_chg", "chg_"), ("keep_inv", "inv_"), ("bms_board", "keep_bms"), ("bs2151_fuse", "bs2151"), ("bs5191_fuse", "bs5191"),
                       ("keep_inv_pp45", "fan_"), ("rail_pos", "ct_"), ("g10_bayplate", "ct_"), ("pos_riser", "bs5191"), ("ct_", "bs5191"),
                       ("sb175", "lid_"), ("g10_deck1", "keep_"), ("g10_deck2", "keep_inv"), ("bms_post", "g10_deck2"), ("bms_post", "g10_bms"), ("g10_bms_bridge", "keep_"), ("pos_inbar", "pos_riser"), ("pos_inbar", "bs5191"),
                       ("pos_inbar", "ct_"), ("pos_riser", "ct_"), ("rail_pos", "pos_inbar"), ("g10_bayplate", "pos_inbar"), ("g10_bayplate", "bs5191")])

def opt_B():
    """Today's NPB-450-12 in the same layout: the 135 mm width is the root cause."""
    return opt_D(chg=("chg_npb450", 205.0, 135.0, 55.0, "NPB-450-12\n205 × 135 × 55 (today)"),
                 title="Option B: today's NPB-450-12 (25 A, CAN) + NTS-400P-112, same layout as D")

def opt_S():
    """Stack: today's NPB-450 flat on deck 1, NTS-400P flat on deck 2, the power bay + BMS + lid connectors on a top deck.
    Pack copper climbs in the 20 mm gap beside the charger (rigid: decks ride on the module, A3)."""
    p = cells()
    p.append(B("g10_deck1", -FX, FX, -FY, FY, Z_D1 - G10, Z_D1, "g10"))
    p.append(B("chg_npb450", -126, 79, -56, FY, Z_D1, Z_D1 + 55, "chg", "NPB-450-12 205 × 135 × 55"))
    p.append(B("keep_chg_dc_tb", -156, -126, -30, 30, Z_D1, Z_D1 + 55, "keep", "TB"))
    p.append(B("keep_chg_ac_c13", 79, 119, 20, 70, Z_D1, Z_D1 + 55, "keep", "C13"))
    z2 = Z_D1 + 55 + 2.5 + G10
    p.append(B("g10_deck2", -156, 156, -56, FY, z2 - G10, z2, "g10"))
    p.append(B("inv_nts400p", -86, 100, -21.5, FY, z2, z2 + 34, "inv", "NTS-400P-112"))
    p.append(B("keep_inv_pp45", -128, -86, 20, 50, z2, z2 + 34, "keep", "PP45"))
    p.append(B("fan_inv_4020", -156, -136, 9, 49, z2, z2 + 40, "fan", "fan"))
    p.append(B("keep_inv_cn500", 100, 120, 15, 55, z2, z2 + 34, "keep", "CN500"))
    p.append(B("pos_riser_up", 122, 147, -78, -73.25, Z_BB, z2 + 46, "pos", None))
    p.append(B("neg_riser_up", -147, -122, -78, -73.25, Z_BB, z2 + 46, "neg", None))
    z3 = z2 + 40 + 2.0 + G10                     # top deck above the 40 mm fan
    zp1 = z3 + 6.35 + 3.175
    lid = zp1 + 89.8 - 8.4 - 1.6
    p.append(B("g10_deck3", -FX, FX, -FY, FY, z3 - G10, z3, "g10"))
    # C1 power module as built (front 113 mm, full width) - contactor-mounting.md
    p.append(B("c1_bay", 43, 156, -79, 79, z3, zp1 + 59.9, "ct", "C1 power module as v16.3\n(GV14, 5191, 2151, shunt, SB175)"))
    p.append(B("bms_board", -150, 25, -75, 15, z3 + 6, z3 + 7.6, "bms", "BMS board 175 × 90"))
    p.append(B("keep_bms_parts", -150, 25, -75, 15, z3 + 7.6, z3 + 17.6, "keep", None))
    p += lid_conns(lid, (-120, 50), (-60, 50), (0, 50))
    return dict(title="Option S: keep NPB-450-12 (25 A, CAN) + NTS-400P-112, power bay on a TOP deck (three decks)",
                parts=p, lid_in=lid,
                levels=[("deck 1: charger, risers in the 20 mm gap", Z_D1, Z_D1 + 55), ("deck 2: inverter", z2, z2 + 34),
                        ("deck 3: C1 power module + BMS + lid connectors", z3, lid)],
                allow=[("g10_", "g10_"), ("g10_", "pos_riser"), ("g10_", "neg_riser"), ("keep_chg", "chg_"), ("keep_inv", "inv_"),
                       ("keep_inv_pp45", "fan_"), ("bms_board", "keep_bms"), ("g10_deck1", "keep_"), ("g10_deck2", "keep_inv"),
                       ("g10_deck2", "fan_"), ("c1_bay", "pos_riser")])

def fig_combined(fname):
    """Victron MultiPlus 12/500/20 120V (311.9 x 183 x 101, connections on the 183 x 101 end; Victron manual 7.6)
    in its three orientations against the footprint. Cable/plug room at the connection end: 50 mm (UNCONF, 16 mm2 + G-ST18i)."""
    L, Wd, D, R = 311.9, 183.0, 101.0, 50.0
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8), dpi=130)
    cases = [("flat on its back: 312 × 183 plan, 101 tall", L, Wd, True, "✗ 183 > 158 wide"),
             ("on its side: 312 × 101 plan, 183 tall", L, D, True, "✗ 312 + 50 cable room = 362 > 312 long"),
             ("upright (as wall-mounted): 183 × 101 plan, 312 tall", Wd, D, False, "✗ 312 tall + 50 cable room under it: lid ≈ 590,\n   ≈ 388 mm above the cells (today 116), and the bay still needs a strip")]
    for ax, (t, a, b, cable, v) in zip(axs, cases):
        ax.add_patch(Rectangle((-FX, -FY), 2 * FX, 2 * FY, fc="#fafafa", ec="#c0392b", lw=2.2))
        x0 = -FX if cable else -a / 2
        ax.add_patch(Rectangle((x0, -FY), a, b, fc=COL["combo"], ec="#333", alpha=0.85))
        ax.text(x0 + a / 2, -FY + b / 2, "MultiPlus\n12/500/20", ha="center", va="center", fontsize=8)
        if cable:
            ax.add_patch(Rectangle((x0 + a, -FY + 10), R, b - 20, fc="none", ec="#7f8c8d", ls="--", hatch="///"))
            ax.text(x0 + a + R / 2, -FY + b / 2, "DC + AC\nconnections\n50", ha="center", va="center", fontsize=6.5)
        else:
            ax.text(0, -FY - 18 + b + 30, "connections face down, into the cell tops", ha="center", fontsize=7)
        ax.set_xlim(-FX - 15, FX + 75); ax.set_ylim(-FY - 30, max(FY, -FY + b) + 25); ax.set_aspect("equal")
        ax.set_title(t, fontsize=9); ax.text(-FX, -FY - 24, v, color="#c0392b", fontsize=9, weight="bold")
    fig.suptitle("Option A: Victron MultiPlus 12/500/20 120V, the only catalog inverter-charger near this size: no orientation fits the 312 × 158 footprint", fontsize=10.5)
    fig.tight_layout(); out = os.path.join(OUT, fname); fig.savefig(out); plt.close(fig); return out

if __name__ == "__main__":
    print(fig_combined("conv_A_multiplus.png"))
    for fn, name in ((opt_B, "conv_B_npb450_nts400p.png"), (opt_S, "conv_S_stack_top_bay.png"), (opt_D, "conv_D_npb360_nts400p.png")):
        o = fn()
        out, iss = plot(o, name)
        print(out); print("\n".join(iss) if iss else "  0 issues")
