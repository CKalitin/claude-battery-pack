"""+ current path height vs distance: v15 (from the v15 build coordinates) vs C1 (from the C1 model's centre line)."""
import json, math, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
def prof(pts):
    s, out = 0.0, [(0.0, pts[0][2])]
    for a, b in zip(pts[:-1], pts[1:]):
        s += math.dist(a, b); out.append((s, b[2]))
    return out
# v15: collector -> riser -> flange -> MRBF (block 26 tall) -> link up to the GX12 studs -> load stud -> drop -> SB175 tongue
v15 = [(134, -33.5, 208.4), (149.6, -33.5, 208.4), (149.6, 0, 208.4), (149.6, 0, 225.0), (134, 0, 225.0), (134, 0, 251.0),
       (134, 15, 251.0), (134, 15, 284.0), (137, 64.5, 284.0), (110, 64.5, 284.0), (110, 35.5, 284.0), (110, 35.5, 225.0),
       (102.7, 13.6, 225.0), (102.7, 13.6, 230.0)]
import c1_power_module as c1
c = c1.build("gv14up")
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
for pts, lab, col in ((v15, "v15 (GX12 upright, SB175 on tray bracket)", "#D8452F"), (c.paths["pos"], "C1 power module (+)", "#1D9E75"),
                      (c.paths["neg"][2:], "C1 power module (−), from the riser foot", "#19B5C4")):
    p = prof(pts); ax.plot([a for a, _ in p], [b for _, b in p], lw=2.4, color=col, label=lab)
ax.axhline(238.3, color="#888", lw=0.8, ls=":"); ax.text(5, 239.5, "C1 copper plane z 238.3 = SB175 busbar face", fontsize=8, color="#555")
ax.axhspan(277.7, 319.7, color="#B0121C", alpha=0.08); ax.text(5, 300, "lid (seam 277.7 → top 319.7)", fontsize=8, color="#B0121C")
ax.set_xlabel("copper length from the cell collector [mm]"); ax.set_ylabel("height z [mm]")
ax.set_title("+ current path, cells → output connector terminal", fontsize=11)
ax.legend(fontsize=8, loc="center right", frameon=False); ax.grid(alpha=0.25); ax.set_ylim(200, 325)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); f = os.path.join(HERE, "out", "profile_v15_vs_c1.png"); fig.savefig(f); print(f)
print("v15 len", round(prof(v15)[-1][0]), "C1 len", round(prof(c.paths['pos'])[-1][0]))
