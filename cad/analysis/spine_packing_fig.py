"""Top view of the power spine at the copper-plane level: what fits beside the charger at W 204 vs W 225 (2026-11-27)."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
X0, X1 = -131.9, 152.0          # fan front face .. front board back parts
def panel(ax, Win, title, parts, sb_on_leads=False):
    h = Win / 2
    ax.add_patch(Rectangle((-156.9, -h), 333.95, Win, fc="none", ec="#c0392b", lw=2))
    ax.add_patch(Rectangle((-156.9, -92), 25, 184, fc="#5dade2", ec="#555")); ax.text(-144, 0, "2×92\nfans", ha="center", va="center", fontsize=7, rotation=90)
    ax.add_patch(Rectangle((-91.9, -h + 3), 205, 135, fc="#aed6f1", ec="#555")); ax.text(10, -h + 70, "charger 205 × 135 (inverter above it)", ha="center", fontsize=8)
    y0 = -h + 3 + 135 + 3
    ax.add_patch(Rectangle((X0, y0), X1 - X0, h - y0, fc="#fdf2e9", ec="#e59866", lw=1, ls="--"))
    ax.text(X0 + 2, h - 6, f"spine strip {X1 - X0:.0f} × {h - y0:.1f} mm", fontsize=7.5, color="#a04000")
    for (x0, x1, ya, yb, c, lab) in parts:
        ax.add_patch(Rectangle((x0, y0 + ya), x1 - x0, yb - ya, fc=c, ec="#333", lw=0.8))
        ax.text((x0 + x1) / 2, y0 + (ya + yb) / 2, lab, ha="center", va="center", fontsize=6.8)
    ax.set_xlim(-170, 190); ax.set_ylim(-120, 125); ax.set_aspect("equal"); ax.set_title(title, fontsize=10)
    ax.set_xlabel("x [mm] (rear ← → front)"); ax.set_ylabel("y [mm]")
fig, axs = plt.subplots(3, 1, figsize=(11, 15), dpi=150)
NEG, POS, LOAD, SB = "#85c1e9", "#f1948a", "#f8c471", "#bb8fce"
# 1: W 204, all on the plane, single file: does not fit
p1 = [(-128, -44.5, 12, 47, NEG, "shunt 83.5"), (-36, 19.6, 17, 42.4, SB, "SB175 55.6"), (28, 100.5, 1, 57, LOAD, "GV14 72.5"),
      (108, 169.9, 19, 39, POS, "5191 62"), (178, 266.5, 19, 39, LOAD, "2151 88.5")]
panel(axs[0], 200.8, "W 204, everything bolted to the plane: needs ≈ 390 mm of strip, has 284  ✗", p1)
# 2: W 204, SB175 on leads, 5191 ∥ 2151
p2 = [(-128, -44.5, 12, 47, NEG, "shunt 83.5"), (-34, 54.5, 3, 26, LOAD, "2151 88.5"), (-34, 27.9, 33, 56, POS, "5191 62"),
      (64, 136.5, 1, 57, LOAD, "GV14 72.5")]
panel(axs[1], 200.8, "B1: W 204, SB175 off the plane (2 short 1/0 AWG leads to the lid), 5191 beside the 2151  ✓ 272 mm", p2)
# 3: W 225, all on the plane, two lanes
p3 = [(-128, -44.5, 44, 79, NEG, "shunt 83.5"), (-128, -72.4, 8, 33.4, SB, "SB175"), (-34, 54.5, 3, 26, LOAD, "2151 88.5"),
      (-34, 27.9, 40, 63, POS, "5191 62"), (64, 136.5, 12, 68, LOAD, "GV14 72.5")]
panel(axs[2], 221.8, "B2: W 225, everything bolted to the plane in two lanes  ✓ 272 mm", p3)
fig.tight_layout()
out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", "spine_packing.png")
fig.savefig(out); print(out)
