"""Option B cross-section (y-z, looking from the front) at the contactor: where the +14 mm of width comes from."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
fig, axs = plt.subplots(1, 2, figsize=(13, 6.2), dpi=160)
def panel(ax, Win, title):
    T = 1.6
    ax.add_patch(Rectangle((-T, 0), T, 318, fc="#c0392b")); ax.add_patch(Rectangle((Win, 0), T, 318, fc="#c0392b"))
    ax.add_patch(Rectangle((Win / 2 - 65, 6), 130, 200, fc="#7fb3d5", ec="#555")); ax.text(Win / 2, 100, "cells (130 wide)", ha="center", fontsize=9)
    ax.add_patch(Rectangle((0, 218.5), Win, 3.2, fc="#c9c46a"))
    ax.add_patch(Rectangle((3, 221.7), 135, 55, fc="#aed6f1", ec="#555")); ax.text(70, 249, "charger 135", ha="center", fontsize=9)
    ax.add_patch(Rectangle((3, 282.3), 100.5, 34, fc="#d6eaf8", ec="#555")); ax.text(53, 299, "inverter 100.5", ha="center", fontsize=9)
    gap0 = 138
    strip = Win - gap0
    cx = gap0 + 3.2 + 27.85
    ax.add_patch(Rectangle((cx - 27.85, 238.3), 55.7, 60, fc="#e59866", ec="#555", alpha=0.9))
    ax.text(cx, 270, "GV14\ncontactor\nØ 55.7", ha="center", fontsize=8.5)
    ax.add_patch(Rectangle((gap0, 232), strip, 6.3, fc="#d68910"))
    ax.text(gap0 + strip / 2, 226, "copper plane", ha="center", fontsize=7.5)
    over = (cx + 27.85 + 3.2) - Win
    def dim(x0, x1, z, txt, c="k"):
        ax.annotate("", (x0, z), (x1, z), arrowprops=dict(arrowstyle="<->", color=c, lw=1.1)); ax.text((x0 + x1) / 2, z + 4, txt, ha="center", fontsize=8.5, color=c)
    dim(0, Win, 345, f"inside width {Win:.1f}")
    dim(gap0, Win, 330, f"strip {strip:.1f}")
    dim(0, 3, 205, "3", "#555"); dim(3, 138, 205, "charger 135", "#555")
    dim(gap0, gap0 + 3.2, 312, "3.2"); dim(cx + 27.85, cx + 27.85 + 3.2, 312, "3.2")
    if over > 0.1:
        ax.add_patch(Rectangle((Win, 238), over, 60, fc="none", ec="red", lw=2, hatch="xx"))
        ax.text(Win + over / 2 + 2, 225, f"{over:.1f} mm\nshort", color="red", ha="left", fontsize=9, weight="bold")
    ax.set_xlim(-20, 225); ax.set_ylim(180, 360); ax.set_aspect("equal")
    ax.set_title(title, fontsize=10); ax.set_xlabel("y [mm]"); ax.set_ylabel("z [mm]")
panel(axs[0], 186.8, "W 190 (today): contactor doesn't fit beside the charger")
panel(axs[1], 200.8, "W 204: +14 mm, contactor fits with 3.2 mm each side")
fig.tight_layout()
out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", "option_b_width.png")
fig.savefig(out); print(out)
