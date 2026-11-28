"""Shell facet options (D40), end-view section through a module end plate. 2026-11-28.
A "facet" is one of the two flat 30-degree bends that round off each long edge of the bent 5052 shell (SCS bends sheet, it can't roll a radius).
F = the length of each facet. Bigger F = softer, rounder-looking corner; it also eats into the inside corner where the module sits.
Run: ~/.venvs/cad/bin/python cad/analysis/facet_options.py
"""
import math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import tower17 as t

c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
T = t.T

def outer(W, F, H, lid_gap=0.2):
    """Closed outer section: body (W wide) bottom corners + lid (WL wide) top corners, both F facets."""
    cnr = F * (c30 + s30)
    a = W / 2 - cnr
    WL = W + 2 * (T + lid_gap)
    al = WL / 2 - cnr
    bot = [(-a, 0), (-(a + F * c30), F * s30), (-W / 2, cnr)]
    top = [(-WL / 2, H - cnr), (-WL / 2 + F * s30, H - cnr + F * c30), (-al, H), (al, H), (WL / 2 - F * s30, H - cnr + F * c30), (WL / 2, H - cnr)]
    botr = [(W / 2, cnr), (W / 2 + 0 - F * 0, cnr)]
    return bot, top, [(a, 0), (a + F * c30, F * s30), (W / 2, cnr)], cnr, a, al

def inner_offset(pts, d):
    return t.offset_polyline(pts, d)

def clash_depth(W, F, y_c, z_c):
    """How far a part corner at (y_c, z_c) pokes past the inside face of the floor facets (mm, >0 = clash)."""
    cnr = F * (c30 + s30); a = W / 2 - cnr
    segs = [((a, 0), (a + F * c30, F * s30)), ((a + F * c30, F * s30), (W / 2, cnr))]
    worst = -1e9
    for (p, q) in segs:
        dy, dz = q[0] - p[0], q[1] - p[1]; L = math.hypot(dy, dz)
        ny, nz = -dz / L, dy / L                                    # inward normal (towards the box centre / up)
        if ny > 0: ny, nz = -ny, -nz
        # signed distance of the corner from the outer facet line, inward positive
        d = (y_c - p[0]) * ny + (z_c - p[1]) * nz
        u = ((y_c - p[0]) * dy + (z_c - p[1]) * dz) / L
        if -1 <= u <= L + 1:
            worst = max(worst, T - d)
    return worst

OPTS = [
    ("A  as built (D40)", 174.0, 8.0, 0.0, "fits as is; tightest corner"),
    ("B  v16 look, module raised", 174.0, 15.0, 8.0, "+8 mm height (lid z 341)"),
    ("C  v16 look, v16 width", 190.0, 15.0, 0.0, "16 mm past the footprint"),
    ("D  v16 look, notched end plates", 174.0, 15.0, 0.0, "end plates notched, G10 narrowed"),
]

def parts(dz):
    z0 = t.Z_CELL + dz
    return {"end plate (6061 .313, 158 wide)": (t.EP_W / 2, z0, t.EP_TOP + dz, "#9aa4ad"),
            "G10 cell frame (±81.4)": (t.EP_W / 2 + 2.4, z0, z0 + t.G10_FRAME, "#d9c27a"),
            "G10 floor (±72)": (72.0, t.Z_FLOOR + dz, z0, "#e8dca8")}

fig = plt.figure(figsize=(15, 9.6))
gs = fig.add_gridspec(2, 4, height_ratios=[1.35, 1])
H = t.H
for i, (name, W, F, dz, note) in enumerate(OPTS):
    Hh = H + dz
    bot_l, top, bot_r, cnr, a, al = outer(W, F, Hh)
    # whole section (top row)
    ax = fig.add_subplot(gs[0, i])
    WL = W + 2 * (T + 0.2)
    wt = t.WALL_TOP + dz
    body = [(-W / 2, wt), (-W / 2, cnr), (-(a + F * c30), F * s30), (-a, 0), (a, 0), (a + F * c30, F * s30), (W / 2, cnr), (W / 2, wt)]
    lidp = [(-WL / 2, t.SEAM_Z + dz)] + top + [(WL / 2, t.SEAM_Z + dz)]
    for pts, d in ((body, T), (lidp, -T)):
        ax.add_patch(Polygon(pts + inner_offset(pts, d)[::-1], closed=True, fc="#c8102e", ec="k", lw=0.6))
    ax.add_patch(Rectangle((-79, t.Z_CELL + dz), 158, t.EP_TOP - t.Z_CELL, fc="#9aa4ad", ec="k", lw=0.6))
    ax.text(0, (t.Z_CELL + t.EP_TOP) / 2 + dz, "cells + end plate\n158 wide", ha="center", fontsize=8)
    ax.plot([-79, -79], [-8, Hh + 8], "b--", lw=0.8); ax.plot([79, 79], [-8, Hh + 8], "b--", lw=0.8)
    ax.annotate("", xy=(-al, Hh + 6), xytext=(al, Hh + 6), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(0, Hh + 9, f"lid flat {2 * al:.0f} mm", ha="center", fontsize=8)
    ax.text(0, -16, f"W {W:.0f} mm  ·  F {F:.0f} mm  ·  H {Hh:.0f} mm", ha="center", fontsize=9)
    ax.set_title(f"{name}\n{note}", fontsize=10, loc="left")
    ax.set_xlim(-108, 108); ax.set_ylim(-24, Hh + 16); ax.set_aspect("equal"); ax.axis("off")
    if i == 0:
        ax.text(-79, Hh + 13, "footprint ±79", color="b", fontsize=7, ha="center")
    # bottom corner zoom (bottom row)
    az = fig.add_subplot(gs[1, i])
    oml = [(a - 12, 0), (a, 0), (a + F * c30, F * s30), (W / 2, cnr), (W / 2, cnr + 30)]
    inn = inner_offset(oml, T)
    az.add_patch(Polygon(oml + inn[::-1], closed=True, fc="#c8102e", ec="k", lw=0.8))
    worst = -1e9
    for lab, (y1, z0, z1, col) in parts(dz).items():
        y0 = y1 - 30
        corner = [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]
        cut = 0.0
        if name.startswith("D"):
            if lab.startswith("end plate"):                    # profile cut in the plate's own plane: free on the SCS laser
                need = max(0.0, clash_depth(W, F, y1, z0))
                cut = need / s30 + 1.0
                corner = [(y0, z0), (y1 - cut, z0), (y1, z0 + cut), (y1, z1), (y0, z1)]
            else:                                              # flat G10 sheets can't be bevelled by a laser: narrow them
                yn = {"G10 cell frame (±81.4)": 73.0, "G10 floor (±72)": 66.4}[lab]
                corner = [(y0, z0), (yn, z0), (yn, z1), (y0, z1)]
                az.text(yn + 0.6, (z0 + z1) / 2, f"±{yn:.1f}", fontsize=7, va="center")
        az.add_patch(Polygon(corner, closed=True, fc=col, ec="k", lw=0.6, alpha=0.95))
        d = clash_depth(W, F, y1, z0)
        if not name.startswith("D"):
            worst = max(worst, d)
        if d > 0 and not name.startswith("D"):
            az.plot(y1, z0, "rx", ms=9, mew=2)
        if cut:
            az.text(y1 - cut / 2 + 2, z0 + cut / 2 + 5, f"end plate\ncorner cut {cut:.0f} mm", fontsize=7, ha="left", color="#333")
    az.plot([79, 79], [-3, 40], "b--", lw=0.8)
    if not name.startswith("D"):
        msg = "clear" if worst <= 0 else f"CLASH {worst:.1f} mm"
        if dz: msg = "clear (module up 8 mm)"
    else:
        msg = "clear; module side play ⚠️"
    az.set_title(f"bottom corner: {msg}", fontsize=9, loc="left", color=("#060" if (worst <= 0 or dz or name.startswith('D')) else "#c00"))
    az.set_xlim(52, 100); az.set_ylim(-3, 40); az.set_aspect("equal")
    az.set_xlabel("y (mm)", fontsize=8); az.tick_params(labelsize=7)
    if i == 0: az.set_ylabel("z (mm)", fontsize=8)
fig.suptitle("Shell facets (D40): each long edge of the bent shell is two flat 30° bends of length F instead of a round corner. "
             "Section through a module end plate.", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.96))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "versions", "v17-option-d", "renders", "facet_options.png")
fig.savefig(out, dpi=130)
print(out)
for name, W, F, dz, note in OPTS:
    print(name, {k: round(clash_depth(W, F, v[0], v[1]), 2) for k, v in parts(dz).items()})
