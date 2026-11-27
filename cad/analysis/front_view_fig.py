"""Head-on (front) view, y-z: cell width vs front LED/control board width, option A (W 190) and B (W 204)."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
fig, axs = plt.subplots(1, 2, figsize=(12, 8), dpi=160)
def R(ax, y0, y1, z0, z1, fc, ec="#555", lw=0.8, ls="-", a=1.0, lab=None, fs=8.5):
    ax.add_patch(Rectangle((y0, z0), y1 - y0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls, alpha=a))
    if lab: ax.text((y0 + y1) / 2, (z0 + z1) / 2, lab, ha="center", va="center", fontsize=fs)
def dim(ax, y0, y1, z, txt, c="k"):
    ax.annotate("", (y0, z), (y1, z), arrowprops=dict(arrowstyle="<->", color=c, lw=1.1))
    ax.text((y0 + y1) / 2, z + 4, txt, ha="center", fontsize=8.5, color=c)
def panel(ax, Wout, title, spine):
    Win = Wout - 3.2; h = Win / 2
    R(ax, -Wout / 2, Wout / 2, 0, 319.7, "none", ec="#c0392b", lw=2)                      # shell outline
    R(ax, -79, 79, 6.35, 193.5, "#5d6d7e", lab=None)                                       # module end plate (behind the board)
    R(ax, -65.15, 65.15, 6.35, 201.85, "#7fb3d5", a=0.95, lab="cells\n130.3 wide")
    if spine:   # B: converters against -y wall, spine on +y
        R(ax, -h, -h + 135, 221.6, 276.6, "#aed6f1", lab="charger")
        R(ax, -h, -h + 100.5, 282.3, 316.3, "#d6eaf8", lab="inverter")
        R(ax, -h + 138, h, 221.6, 318, "#e59866", a=0.85, lab="power\nspine")
    else:       # A: converters centred, bay in front of them (seen head-on it overlaps them)
        R(ax, -67.5, 67.5, 221.6, 276.6, "#aed6f1", lab="charger")
        R(ax, -50.25, 50.25, 282.3, 316.3, "#d6eaf8", lab="inverter")
        R(ax, -h, h, 232, 318, "#e59866", a=0.45, lab="power bay (in front of the converters)")
    bw = 175.0 if not spine else Win - 4.0
    R(ax, -bw / 2, bw / 2, 36.0, 285.3, "none", ec="#1e8449", lw=2.2, ls="--")
    ax.text(0, 22, f"front LED + control board {bw:.0f} × 249 (dashed, in front)", ha="center", fontsize=8.5, color="#1e8449")
    dim(ax, -65.15, 65.15, -18, "cells 130.3")
    dim(ax, -79, 79, -34, "end plate 158")
    dim(ax, -bw / 2, bw / 2, -50, f"board {bw:.0f}", "#1e8449")
    dim(ax, -h, h, -66, f"inside {Win:.1f}")
    ax.set_xlim(-125, 125); ax.set_ylim(-80, 335); ax.set_aspect("equal")
    ax.set_title(title, fontsize=10); ax.set_xlabel("y [mm]"); ax.set_ylabel("z [mm]")
panel(axs[0], 190.0, "A as built (W 190), from the front", False)
panel(axs[1], 204.0, "B side spine (W 204), from the front", True)
fig.tight_layout()
out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", "front_view_A_B.png")
fig.savefig(out); print(out)
