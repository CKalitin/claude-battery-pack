"""Low-res 3D block renders of architecture options A and B (lid and near wall off)."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matplotlib; matplotlib.use("Agg")
src = open(os.path.join(HERE, "architecture_fig.py")).read().split("fig, axs =")[0]
ns = {"__file__": os.path.join(HERE, "architecture_fig.py")}; exec(src, ns)
import pyvista as pv
pv.OFF_SCREEN = True
names = {"cell": "cells", "chg": "charger", "inv": "inverter", "bay": "power bay", "fan": "fan", "plug": "plug room", "board": "front board", "void": "EMPTY"}
for (title, L, W, blocks), tag in zip(ns["cand"][:2], ("A", "B")):
    p = pv.Plotter(window_size=(900, 700), off_screen=True)
    p.set_background("white")
    H = 318.1
    for (x0, x1, y0, y1, z0, z1, k, lab) in blocks:
        b = pv.Box(bounds=(x0, x1, y0, y1, z0, z1))
        op = 0.35 if k == "void" else (0.9 if k != "plug" else 0.6)
        p.add_mesh(b, color=ns["C"][k], opacity=op, show_edges=True, edge_color="#444444", line_width=1)
    # floor + far wall + rear plate as thin translucent sheets
    p.add_mesh(pv.Box(bounds=(0, L, W, W + 2, 0, H)), color="#c0392b", opacity=0.25)
    p.add_mesh(pv.Box(bounds=(0, L, 0, W, -2, 0)), color="#c0392b", opacity=0.5)
    p.add_mesh(pv.Box(bounds=(-3, 0, 0, W, -20, H + 50)), color="#9aa4ad", opacity=0.5)
    seen = {}
    for (x0, x1, y0, y1, z0, z1, k, lab) in blocks:
        if k in seen or k == "plug": continue
        seen[k] = ((x0 + x1) / 2, y0 - 5, z1 - 10 if k == "bay" else (z0 + z1) / 2)
    p.add_point_labels(list(seen.values()), [names[k] for k in seen], font_size=13, point_size=1, shape_opacity=0.6, always_visible=True)
    p.add_text(f"{title}\ninside {L:.0f} x {W:.0f} x {H:.0f} mm", font_size=11, color="black")
    p.camera_position = [(L * 0.5 + 560, -620, 620), (L / 2, W / 2, 150), (0, 0, 1)]
    out = os.path.join(HERE, "..", "..", "versions", "v16-c1-power-module", "renders", f"architecture_3d_{tag}.png")
    p.screenshot(out); p.close(); print(out)
