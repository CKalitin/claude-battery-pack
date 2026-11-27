"""Side elevation (x-z) of the load path: cells -> module end plates -> M4 hold-downs -> body -> front/rear plates (feet, handles)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
import tower15 as t
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
fig, ax = plt.subplots(figsize=(13, 8.2), dpi=170)
def R(x0, x1, z0, z1, fc, ec="k", lw=0.8, a=1.0, z=1, hatch=None):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, alpha=a, zorder=z, hatch=hatch))
H = t.H
# front / rear plates (feet + handles)
for x0, x1 in ((t.XR - 4.75, t.XR), (t.XF, t.XF + 4.75)):
    R(x0, x1, t.PZ0, t.PZ1, "#9aa4ad", z=3)
# body: floor + one wall (section line), lid
R(t.XR, t.XF, 0, t.T * 3, "#c0392b", z=2)                                   # floor (drawn 3x thick)
ax.plot([t.XR, t.XF], [t.WALL_TOP, t.WALL_TOP], color="#c0392b", lw=2.5, zorder=2)
R(t.XR, t.XF, t.SEAM_Z, H, "none", ec="#c0392b", lw=1.2, z=2)
ax.text(t.XR + 6, t.SEAM_Z + 18, "lid", color="#c0392b", fontsize=9)
# wall (behind the section): light fill
R(t.XR, t.XF, 0, t.WALL_TOP, "#f5d7d3", ec="none", z=0)
# G10 floor
R(-t.STACK_L / 2 - 0.5, t.STACK_L / 2 + 0.5, t.Z_FLOOR, t.Z_CELL, "#3b3b3b", z=2)
# cells + module end plates
for x in t.cell_x:
    R(x - t.CELL_T / 2, x + t.CELL_T / 2, t.Z_CELL, t.Z_CBODY, "#7fb3d5", z=2)
for x in t.ep_x:
    R(x - t.EP_T / 2, x + t.EP_T / 2, t.Z_CELL, t.EP_TOP, "#5d6d7e", z=3)
# rods
for z in t.ROD_Z:
    ax.plot([-t.STACK_L / 2 - 6, t.STACK_L / 2 + 6], [z, z], color="#2c3e50", lw=2.2, zorder=4)
# standoffs + tray 1, charger, tray 2, inverter
for x in t.ep_x:
    R(x - 3.5, x + 3.5, t.EP_TOP, t.Z_TRAY1, "#d4ac0d", z=3)
R(-170, 163, t.Z_TRAY1, t.Z_T1TOP, "#c9c46a", z=3)
R(-182, 23, t.Z_T1TOP, t.Z_T1TOP + 55, "#a9cce3", z=2, a=0.8)
R(-183, 8, t.Z_TRAY2, t.Z_T2TOP, "#c9c46a", z=3)
R(-182, 4, t.Z_T2TOP, t.Z_T2TOP + 34, "#a9cce3", z=2, a=0.8)
R(50, 163, 232, 262, "#e59866", z=2, a=0.8)
# hold-down screws
for x in t.ep_x:
    ax.plot([x, x], [-6, t.Z_CELL + 12], color="#111", lw=2.4, zorder=6)
# arrows (load path)
kw = dict(arrowstyle="-|>", mutation_scale=16, lw=2.2, color="#1e8449", zorder=8)
ax.add_patch(FancyArrowPatch((0, 185), (0, 125), **kw)); ax.text(6, 172, "1  cell weight 155 N (and 2.9 kN clamp)", color="#1e8449", fontsize=9)
for s in (-1, 1):
    ax.add_patch(FancyArrowPatch((s * 40, 100), (s * (t.STACK_L / 2 - 12), 100), **kw))
ax.text(-100, 72, "2  friction + clamp carry the\n   stack into the end plates", color="#1e8449", fontsize=9, ha="center")
ax.add_patch(FancyArrowPatch((-120, 335), (t.ep_x[0] + 2, 222), connectionstyle="arc3,rad=0.3", **kw))
ax.text(-40, 340, "3  converters + power bay: trays -> standoffs -> end plates", color="#1e8449", fontsize=9, ha="center")
for x in t.ep_x:
    ax.add_patch(FancyArrowPatch((x, 30), (x, 2), **kw))
ax.text(t.ep_x[1] - 150, -42, "4  4 x M4 hold-downs\n   into the body floor\n   (272 N each at 5 g)", color="#1e8449", fontsize=9)
ax.add_patch(FancyArrowPatch((t.ep_x[0] - 10, 6), (t.XR + 4, 6), **kw))
ax.add_patch(FancyArrowPatch((t.ep_x[1] + 10, 6), (t.XF - 4, 6), **kw))
ax.text(t.XR + 4, -30, "5  body (U section, walls 287 mm tall)\n   carries it to the plates: σ 0.6 MPa at 5 g,\n   wall buckling at 48 MPa (77x)", color="#1e8449", fontsize=9)
for x in (t.XR - 2, t.XF + 2):
    ax.add_patch(FancyArrowPatch((x, -40), (x, -16), arrowstyle="-|>", mutation_scale=16, lw=2.2, color="#922b21", zorder=8))
    ax.add_patch(FancyArrowPatch((x, t.PZ1 + 34), (x, t.PZ1 + 4), arrowstyle="<|-", mutation_scale=16, lw=2.2, color="#922b21", zorder=8))
ax.text(t.XF + 9, -34, "6  feet\n(standing)", color="#922b21", fontsize=9)
ax.text(t.XF + 9, t.PZ1 + 12, "6  handle slot\n(carrying)", color="#922b21", fontsize=9)
# labels
lab = [((0, t.Z_CELL + 15), "8 x LF105 cells + 9 Mylar 0.25 mm insulators"), ((t.ep_x[1] - 2, 196), "module end plate\n6061 .313"),
       ((0, t.ROD_Z[1] + 3), "4 x M5 tie rods (tension only)"), ((t.ep_x[0], t.Z_TRAY1 - 8), "upper standoffs"),
       ((-80, t.Z_TRAY1 + 3), "tray 1"), ((-80, 248), "charger"), ((-80, t.Z_T2TOP + 14), "inverter on tray 2"),
       ((105, 247), "power bay"), ((-120, t.Z_FLOOR + 1), "G10 floor"), ((t.XR - 2, 150), "rear plate"), ((t.XF + 3, 150), "front plate")]
for (x, z), s in lab:
    ax.text(x, z, s, fontsize=8.5, ha="center" if "plate\n" not in s else "center", zorder=9,
            rotation=90 if s in ("rear plate", "front plate") else 0, color="#111",
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=1))
ax.set_xlim(t.XR - 40, t.XF + 90); ax.set_ylim(-60, t.PZ1 + 45); ax.set_aspect("equal")
ax.set_xlabel("x [mm] (rear ← → front)"); ax.set_ylabel("z [mm]")
ax.set_title("v16.3 load path: how the cells reach the enclosure (side section, body wall behind in pink)", fontsize=11)
ax.grid(alpha=0.2)
fig.tight_layout()
out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", "structure_load_path.png")
fig.savefig(out); print(out)
