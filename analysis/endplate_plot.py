import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.tri as mtri
import endplate_fe as fe
from skfem import solve, condense
lay = {"v12: rods at z 28 / 94": [(s*72, z) for s in (-1,1) for z in (28.35, 94.35)],
       "v13: rods at 0.207 h / 0.793 h (z 45 / 153)": [(s*72, z) for s in (-1,1) for z in (fe.Z0+0.207*(fe.Z1-fe.Z0), fe.Z0+0.793*(fe.Z1-fe.Z0))]}
fig, axs = plt.subplots(1, 2, figsize=(11, 6.5), dpi=180)
F = 2943.0
q = F / (2*fe.CY*(fe.Z1-fe.CZ0))
from skfem import LinearForm
@LinearForm
def lin(v, w):
    y, z = w.x
    return q*((np.abs(y) <= fe.CY)*(z >= fe.CZ0))*v
K, f = fe.bil.assemble(fe.ib), lin.assemble(fe.ib)
p = fe.m.p
tri = mtri.Triangulation(p[0], p[1], fe.m.t.T)
for ax, (name, rods) in zip(axs, lay.items()):
    fixed = []
    for (ry, rz) in rods:
        nodes = np.where((p[0]-ry)**2+(p[1]-rz)**2 <= fe.RNUT**2)[0]
        fixed += list(fe.ib.nodal_dofs[0, nodes])
    w = solve(*condense(K, f, D=np.array(fixed)))
    wn = w[fe.ib.nodal_dofs[0]]*1000
    c = ax.tricontourf(tri, wn, levels=np.linspace(0, 660, 23), cmap="magma_r")
    ax.add_patch(plt.Rectangle((-fe.CY, fe.CZ0), 2*fe.CY, fe.Z1-fe.CZ0, fill=False, ls="--", ec="w", lw=1))
    for (ry, rz) in rods: ax.add_patch(plt.Circle((ry, rz), fe.RNUT, color="#2a9d8f"))
    ax.set_title(f"{name}\nmax deflection {np.abs(wn).max():.0f} µm", fontsize=10)
    ax.set_aspect("equal"); ax.set_xlabel("y [mm]"); ax.set_ylabel("z [mm]")
fig.colorbar(c, ax=axs, label="out-of-plane deflection w [µm]  (F = 2.94 kN, 6061-T6, t = 7.95 mm)", shrink=0.8)
fig.suptitle("Module end plate under cell pressure (dashed = cell face, teal = M5 rod nuts)")
fig.savefig("endplate_compare.png", bbox_inches="tight")
print("ok")
