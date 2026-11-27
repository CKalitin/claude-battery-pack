"""To-scale side elevation of the C1 levels (looking from -y), from the model's part boxes."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import c1_power_module as c1
c = c1.build("gv14up")
COL = {"pos": "#D8452F", "neg": "#19B5C4", "ins": "#C9C46A"}
SPEC = {"contactor": "#2A2A2D", "sb175_housing": "#8A8D93", "mrbf": "#E0D8C0", "shunt_module": "#1E5631", "nut": "#555"}
fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
# cells (context), drawn as a band
ax.add_patch(Rectangle((0.8, 170), 151.6, 36.9, color="#2B6FC4", alpha=0.35, lw=0)); ax.text(5, 185, "cells 5-8 (tops at z 206.9)", fontsize=8, color="#123")
order = ["tray1", "standoff", "g10_plate", "bus_pack", "bus_mod", "shunt_bar", "nut", "g10_sb", "mrbf", "shunt_module", "contactor", "sb175"]
def rank(n): return next((i for i, k in enumerate(order) if n.startswith(k)), 99)
Z0, Z1, P0, P1 = 206.85, 210.0, 235.14, 238.32
R = [  # (x0, x1, z0, z1, colour, alpha) — L-shaped copper drawn piece by piece, as seen from -y
    (0, 163, 218.45, 221.63, "#C9C46A", 0.9),                        # tray 1
    (77.4, 152.0, Z0, Z1, "#D8452F", 1), (138.0, 142.76, Z0, P1, "#D8452F", 1), (136.0, 152.0, P0, P1, "#D8452F", 1),   # + collector, riser, flange
    (50, 80, Z0, Z1, "#19B5C4", 1), (62.0, 80.0, Z0, P1, "#19B5C4", 1),                                                 # - band end, riser + flange
    (54, 150, 231.97, P0, "#C9C46A", 1),                             # module plate
    (136, 152, P0, P1, "#D8452F", 1), (112, 152, P0, P1, "#D8452F", 1), (62.7, 128, P0, P1, "#D8452F", 1),               # in-bar, load bar
    (53.2, 88.2, P1, P1 + 3.2, "#19B5C4", 1), (58.2, 83.2, P1 + 3.2, P1 + 10.2, "#1E5631", 1),                         # shunt bar + board
    (131.5, 156.5, P1, P1 + 12, "#E0D8C0", 1), (77, 101, P1, P1 + 20, "#E0D8C0", 1),                                    # MRBF main, branch
    (92.15, 147.85, P1 + 2, P1 + 59.9, "#2A2A2D", 0.75), (113.4, 126.6, 221.6, 231.97, "#555555", 1),                   # contactor, stud nuts
    (58.0, 83.4, P1 + 10.2, P1 + 89.8, "#8A8D93", 0.75), (54.8, 58.0, P1, P1 + 52, "#C9C46A", 1), (83.4, 86.6, P1, P1 + 52, "#C9C46A", 1)]
for (x0, x1, z0, z1, col, al) in R:
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=col, edgecolor="#111", lw=0.6, alpha=al))
for z in (221.6, 231.97):
    pass
for x in (58, 100, 146):
    ax.add_patch(Rectangle((x - 4, 221.63), 8, 231.97 - 221.63, facecolor="#C9C46A", edgecolor="#111", lw=0.5))   # standoffs
lv = [("L0  pack copper (collectors, band)", 206.85, 210.0), ("L1  G10 tray 1", 218.45, 221.63), ("L2  G10 module plate", 231.97, 235.14),
      ("L3  module copper plane", 235.14, 238.32), ("L4  parts, terminals down", 238.32, 298.2)]
for i, (t, z0, z1) in enumerate(lv):
    y = [208, 220, 229, 240, 268][i]
    ax.annotate(f"{t}\nz {z0:.1f}–{z1:.1f}", xy=(170, (z0 + z1) / 2), xytext=(178, y), fontsize=8.5, va="center",
                arrowprops=dict(arrowstyle="-", color="#666", lw=0.7))
ax.axhspan(277.7, 319.7, xmin=0, xmax=1, color="#B0121C", alpha=0.07); ax.text(5, 314, "lid (seam 277.7, top 319.7)", fontsize=8, color="#B0121C")
ax.axhline(319.7, color="#B0121C", lw=1.2)
for (x, z, t) in [(70.7, 300, "SB175 (mates from above)"), (120, 268, "contactor GV141BAX\nupside-down"), (144, 255, "MRBF 250 A"),
                  (89, 262, "branch\nMRBF"), (150, 214, "+ riser"), (40, 230, "- riser"), (71, 253, "shunt"), (120, 214.5, "tray 1"),
                  (120, 227, "stud nuts"), (25, 233.5, "module plate")]:
    ax.text(x, z, t, fontsize=8, ha="center", va="center", color="#000", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.75))
ax.set_xlim(-5, 245); ax.set_ylim(168, 335); ax.set_aspect("equal")
ax.set_xlabel("x [mm] (front of pack →)"); ax.set_ylabel("z [mm]")
ax.set_title("C1 power module: levels, side view from −y, to scale", fontsize=11)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
fig.tight_layout(); f = "out/c1_levels_elevation.png"; fig.savefig(f); print(f)
