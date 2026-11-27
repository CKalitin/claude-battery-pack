"""Side section (x-z) of the rear end: what fills the 91 mm between the cell module and the rear plate."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
import tower15 as t
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
fig, ax = plt.subplots(figsize=(11, 8.6), dpi=170)
def R(x0, x1, z0, z1, fc, lab=None, ec="k", a=1.0, fs=8.5, rot=0, hatch=None):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=0.8, alpha=a, hatch=hatch))
    if lab: ax.text((x0 + x1) / 2, (z0 + z1) / 2, lab, ha="center", va="center", fontsize=fs, rotation=rot)
xm = -t.STACK_L / 2
R(t.XR - t.PT, t.XR, t.PZ0, t.PZ1, "#9aa4ad", "rear plate", rot=90)
R(t.XR, t.XF, 0, t.T * 2, "#c0392b")
R(t.XR, t.XF, t.SEAM_Z, t.H, "none", ec="#c0392b")
R(-247.0, -222.0, 164.5, 304.5, "#5dade2", "NF-A14\nfan\n25 mm", fs=8)
R(xm, xm + t.EP_T, t.Z_CELL, t.EP_TOP, "#5d6d7e")
for x in t.cell_x[:3]:
    R(x - t.CELL_T / 2, x + t.CELL_T / 2, t.Z_CELL, t.Z_CBODY, "#7fb3d5")
ax.text(t.cell_x[1], 100, "cells", ha="center", fontsize=9)
R(xm - 2, -20, t.Z_TRAY1, t.Z_T1TOP, "#c9c46a")
R(-182, -20, t.Z_T1TOP, t.Z_T1TOP + 55, "#a9cce3", "charger (NPB-450)")
R(-183, -20, t.Z_TRAY2, t.Z_T2TOP, "#c9c46a")
R(-182, -20, t.Z_T2TOP, t.Z_T2TOP + 34, "#a9cce3", "inverter (NTS-400P)")
R(-218.0, -182.0, 230, 262, "#f0b27a", "RA C13\n36 mm", fs=7.5)
R(-202.0, -182.0, 286.3, 310.3, "#f0b27a", "CN500", fs=7.5)
R(-202 - 15, -202 + 15, 288, 318, "#f5cba7", "outlet\n/ inlet", fs=7, a=0.8)
# void
R(t.XR, xm, t.T * 2, 164.5, "#fdebd0", ec="#e67e22", hatch="//", a=0.9)
ax.text((t.XR + xm) / 2, 80, f"EMPTY\n{xm - t.XR:.0f} mm × 164 mm tall\n× 187 mm wide\n≈ 2.8 L", ha="center", fontsize=10, color="#a04000", weight="bold")
R(-222, -182, 304.5, t.SEAM_Z + 40, "none")
def dim(x0, x1, z, txt):
    ax.annotate("", (x0, z), (x1, z), arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax.text((x0 + x1) / 2, z + 4, txt, ha="center", fontsize=8.5)
dim(t.XR, -222, 340, "fan 25")
dim(-222, -182, 340, "AC column 40")
dim(-182, xm, 340, "overhang 26")
dim(t.XR, xm, 360, f"{xm - t.XR:.0f} mm from the rear plate to the cells")
ax.set_xlim(t.XR - 20, -10); ax.set_ylim(-10, 380); ax.set_aspect("equal")
ax.set_xlabel("x [mm]"); ax.set_ylabel("z [mm]")
ax.set_title("v16.3 rear end (side section): why there are 91 mm behind the cells", fontsize=11)
fig.tight_layout()
out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", "rear_end_void.png")
fig.savefig(out); print(out)
