"""Design-space study (2026-11-27): block layouts to scale, top (x-y) and side (x-z) views, for the candidate architectures.
Blocks are catalog envelopes plus the plug room each connector needs (power-train.md). Units mm."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
C = dict(cell="#7fb3d5", chg="#aed6f1", inv="#d6eaf8", bay="#e59866", fan="#5dade2", plug="#f8c471", board="#58d68d", void="#fdebd0")
MOD, CELL_H, T1, CHG_H, INV_H, LID = 312.0, 210.0, 221.6, 55.0, 34.0, 318.1
def draw(ax_s, ax_t, title, L, W, blocks, H=LID):
    for ax in (ax_s, ax_t):
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax_s.add_patch(Rectangle((0, 0), L, H, fc="none", ec="k", lw=1.5)); ax_t.add_patch(Rectangle((0, 0), L, W, fc="none", ec="k", lw=1.5))
    for (x0, x1, y0, y1, z0, z1, k, lab) in blocks:
        hatch = "//" if k == "void" else None
        side_bay = (k == "bay" and lab == "")
        if side_bay:   # bay beside the converters (in y): outline only in the side view
            ax_s.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc="none", ec=C["bay"], lw=2.0, ls="--"))
            ax_s.text((x0 + x1) / 2, z1 + 8, "power spine beside the converters (dashed, +y side)", ha="center", fontsize=6.5, color="#a04000")
        else:
            ax_s.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=C[k], ec="#555", lw=0.6, hatch=hatch, alpha=0.95))

        if lab and not side_bay:
            ax_s.text((x0 + x1) / 2, (z0 + z1) / 2, lab, ha="center", va="center", fontsize=6.5)
    ax_s.set_xlim(-10, 440); ax_s.set_ylim(-10, 410); ax_t.set_xlim(-10, 440); ax_t.set_ylim(-10, 230)
    ax_s.set_title(title, fontsize=9, loc="left")
    for (x0, x1, y0, y1, z0, z1, k, lab) in sorted(blocks, key=lambda b: b[5]):
        ax_t.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=C[k], ec="#555", lw=0.6, hatch="//" if k == "void" else None, alpha=0.35 if k == "cell" else 0.95))
    vol = L * W * H / 1e6
    ax_t.text(0, W + 8, f"inside {L:.0f} × {W:.0f} × {H:.0f} mm = {vol:.1f} L", fontsize=7.5)
    for (x0, x1, y0, y1, z0, z1, k, lab) in blocks:
        if lab and k != "cell":
            ax_t.text((x0 + x1) / 2, (y0 + y1) / 2, lab if lab else "", ha="center", va="center", fontsize=6.5)
W0 = 186.8
cand = []
# A: v16.3 as built
cand.append(("A  v16.3 as built: bay end-to-end with the converters", 424.0, W0, [
    (91, 403, 14, 172, 0, CELL_H, "cell", "cells"), (0, 91, 0, W0, 0, 164, "void", "EMPTY 2.8 L"),
    (0, 25, 23, 163, 164, 304, "fan", "fan"), (25, 65, 0, W0, T1, LID, "plug", "AC"),
    (65, 270, 26, 161, T1, T1 + CHG_H, "chg", "charger"), (65, 251, 43, 143, 282, 316, "inv", "inverter"),
    (270, 297, 26, 161, T1, T1 + CHG_H, "plug", ""), (297, 410, 0, W0, T1, LID, "bay", "power bay"), (410, 424, 0, W0, 0, 285, "board", "")]))
# B: side spine, twin 92 mm fans
WB = 200.8
cand.append(("B  side spine: bay beside the converters, 2 × 92 mm fans (recommended)", 326.0, WB, [
    (0, 312, 21, 179, 0, CELL_H, "cell", "cells"), (0, 25, 0, 187, T1 + 2, T1 + 94, "fan", "2×92"),
    (25, 61, 0, 135, T1, T1 + CHG_H, "plug", "AC"), (61, 266, 0, 135, T1, T1 + CHG_H, "chg", "charger"), (266, 296, 0, 135, T1, T1 + CHG_H, "plug", "DC"),
    (25, 45, 0, 100.5, 282, 316, "plug", ""), (45, 231, 0, 100.5, 282, 316, "inv", "inverter"), (231, 273, 0, 100.5, 282, 316, "plug", "DC"),
    (25, 312, 139, WB, T1, LID, "bay", ""), (312, 326, 0, WB, 0, 285, "board", "")]))
# C: three decks, power layer on top
cand.append(("C  three-deck tower: power layer on top (+70 mm tall)", 326.0, W0, [
    (0, 312, 14, 172, 0, CELL_H, "cell", "cells"), (0, 25, 23, 163, T1, T1 + 92, "fan", "fan"),
    (25, 61, 26, 161, T1, T1 + CHG_H, "plug", ""), (61, 266, 26, 161, T1, T1 + CHG_H, "chg", "charger"), (266, 296, 26, 161, T1, T1 + CHG_H, "plug", ""),
    (45, 231, 43, 143, 282, 316, "inv", "inverter"), (190, 312, 0, W0, 320, 388, "bay", "bay"), (0, 190, 0, W0, 320, 388, "void", "spare 2 L"),
    (312, 326, 0, W0, 0, 285, "board", "")]))
fig, axs = plt.subplots(3, 2, figsize=(13, 13), dpi=150, gridspec_kw=dict(width_ratios=[1, 1]))
for i, (t_, L, W, b) in enumerate(cand):
    draw(axs[i][0], axs[i][1], t_, L, W, b, H=(390.0 if t_.startswith("C") else LID))
axs[0][0].text(0, -30, "side view (x → front)", fontsize=7); axs[0][1].text(0, -25, "top view", fontsize=7)
fig.tight_layout()
out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", "architecture_options.png")
fig.savefig(out); print(out)
