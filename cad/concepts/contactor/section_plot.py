"""True cross-sections of the C1 model: every STL sliced by a plane, cut faces filled, to scale."""
import glob, json, os
import numpy as np, pyvista as pv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
HERE = os.path.dirname(os.path.abspath(__file__)); CTX = os.path.join(HERE, "..", "..", "out_tower15", "stl")
key = "c1_module_gv14up"
roles = json.load(open(os.path.join(HERE, "out", key, "meta.json")))["roles"]
COL = [("contactor", "#3A3A3D"), ("hw_", "#9AA0A6"), ("nut_m8", "#9AA0A6"), ("sb175_housing", "#B8BBC0"), ("sb175_contact", "#E7A35A"),
       ("mrbf", "#E6DEC6"), ("shunt_module", "#2E7D46"), ("g10", "#D9D27A"), ("standoff", "#D9D27A"), ("tray1", "#D9D27A"),
       ("cell_", "#8DB3E2"), ("bus_A", "#C8693A"), ("bus_B", "#C8693A"), ("bus_C", "#C8693A"), ("flex_ccs", "#F0B54A"), ("g10_top", "#D9D27A")]
ROLECOL = {"pos": "#D8452F", "neg": "#19B5C4"}
def colour(n):
    if roles.get(n) in ROLECOL and not n.startswith(("sb175_contact",)): return ROLECOL[roles[n]]
    return next((c for k, c in COL if n.startswith(k)), "#AAAAAA")
def section(ax, axis, value, uidx, xlim, ylim, labels):
    files = glob.glob(os.path.join(HERE, "out", key, "*.stl")) + [f for f in glob.glob(os.path.join(CTX, "*.stl"))
             if os.path.basename(f).startswith(("cell_", "bus_A", "bus_B", "bus_C", "flex_ccs", "g10_top"))]
    order = lambda f: (0 if "cell_" in f else 1 if os.path.basename(f).startswith(("g10", "tray", "standoff")) else 3 if "hw_" in f or "nut" in f else 2)
    for f in sorted(files, key=order):
        n = os.path.basename(f)[:-4]
        if n.startswith("path_"): continue
        m = pv.read(f)
        s = m.slice(normal=axis, origin=[value if i == "xyz".index(axis) else 0 for i in range(3)])
        if s.n_points == 0: continue
        s = s.strip()
        for i in range(s.n_cells):
            ids = s.get_cell(i).point_ids
            P = s.points[ids][:, [uidx, 2]]
            if len(P) < 3: continue
            ax.add_patch(Polygon(P, closed=True, facecolor=colour(n), edgecolor="#111", lw=0.6))
    for (u, z, t, tu, tz) in labels:
        ax.annotate(t, xy=(u, z), xytext=(tu, tz), fontsize=8, va="center",
                    arrowprops=dict(arrowstyle="-", color="#444", lw=0.6), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#999", lw=0.5))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
Zp0, Zp1 = 235.14, 238.32
fig, axs = plt.subplots(1, 2, figsize=(16, 7.8), dpi=150)
L1 = [(20, 270, "contactor, upside-down\n(terminals face down)", -18, 285),
      (27.85, Zp1 + 1, "contactor terminal T1\nsits on the copper", -18, 252),
      (27.85, 236.7, "+ in-bar (copper, 3.2 mm)\nlies flat on the plate", -18, 238),
      (54.55, 236.7, "+ load bar (copper)", 96, 246),
      (40, 233.5, "G10 plate 3.2 mm\n(copper lies on it)", 96, 232),
      (54.55, 229, "M8 stud through\ncopper + plate", 96, 222),
      (27.85, 226, "M8 nut under the plate", -18, 224),
      (-12, 226, "standoff", -18, 212),
      (0, 220, "G10 tray 1", 96, 212),
      (33.5, 208.4, "series bar (cells, L0)", 96, 203),
      (0, 195, "cell", -18, 196)]
section(axs[0], "x", 120.0, 1, (-20, 115), (188, 302), L1)
axs[0].set_title("Section A: cut at x = 120 through both contactor terminals, looking from the front", fontsize=10)
axs[0].set_xlabel("y [mm]"); axs[0].set_ylabel("z [mm]")
L2 = [(51.2, 290, "SB175 housing\n(plug mates from above)", 70, 300),
      (51.2, 244, "busbar contact (+)", 70, 268),
      (24.4, 244, "busbar contact (−)", -60, 268),
      (51.2, 236.7, "+ load bar (copper)", 70, 248),
      (18, 236.7, "− tab (copper)", -60, 250),
      (-20, 240, "shunt bar on top of\nthe − tab / riser flange", -60, 236),
      (-30, 244.5, "shunt sensing board", -60, 258),
      (10, 233.5, "G10 plate", 70, 236),
      (51.2, 229, "1/4-20 stud + lock nut\nunder the plate", 70, 224),
      (-62, 220, "− riser (from band)", -60, 214),
      (20, 220, "G10 tray 1", 70, 214),
      (-20, 200, "cells", -60, 200)]
section(axs[1], "x", 70.7, 1, (-75, 105), (188, 335), L2)
axs[1].set_title("Section B: cut at x = 70.7 through the SB175 contacts and the shunt", fontsize=10)
axs[1].set_xlabel("y [mm]")
for ax in axs:
    ax.axhspan(Zp0, Zp1, color="#D8452F", alpha=0.08)
    ax.text(ax.get_xlim()[1] - 2, Zp1 + 1.2, "copper layer z 235.1–238.3", fontsize=7, ha="right", color="#B0301D")
fig.suptitle("C1 power module, true sections from the CAD model (to scale). Plate = flat G10 sheet; copper bars lie directly on it; parts bolt down through both.", fontsize=11)
fig.tight_layout(); f = os.path.join(HERE, "out", "c1_sections.png"); fig.savefig(f); print(f)
