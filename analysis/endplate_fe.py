"""Kirchhoff plate FE (Morley elements, scikit-fem) of one module end plate under cell swelling pressure,
point-supported at the tie-rod nuts. Compares rod layouts."""
import numpy as np
from skfem import MeshTri, Basis, ElementTriMorley, BilinearForm, LinearForm, solve, condense
from skfem.helpers import dd, ddot

E, nu, t = 68.9e3, 0.33, 7.95                    # 6061-T6 [MPa], [-], plate thickness [mm]
D = E * t**3 / (12 * (1 - nu**2))                # flexural rigidity [N mm]
Y0, Y1, Z0, Z1 = -79.0, 79.0, 6.35, 191.85       # end plate extent [mm]
CY, CZ0 = 65.15, 6.35                            # cell face half-width, bottom [mm]
RNUT = 4.6                                       # rod nut contact radius [mm]

m = MeshTri.init_tensor(np.linspace(Y0, Y1, 80), np.linspace(Z0, Z1, 94))
e = ElementTriMorley(); ib = Basis(m, e)

@BilinearForm
def bil(u, v, w):
    def C(T): return E * t**3 / (12 * (1 - nu**2)) * ((1 - nu) * T + nu * np.eye(2)[:, :, None, None] * (T[0, 0] + T[1, 1]))
    return ddot(C(dd(u)), dd(v))

def run(F, rods):
    """F = total clamp force [N]; rods = list of (y, z) [mm]."""
    q = F / (2 * CY * (Z1 - CZ0))                # uniform pressure on the covered cell face [MPa]
    @LinearForm
    def lin(v, w):
        y, z = w.x
        return q * ((np.abs(y) <= CY) * (z >= CZ0)) * v
    K, f = bil.assemble(ib), lin.assemble(ib)
    p = m.p
    fixed = []
    for (ry, rz) in rods:
        nodes = np.where((p[0] - ry) ** 2 + (p[1] - rz) ** 2 <= RNUT ** 2)[0]
        if len(nodes) == 0:
            nodes = [np.argmin((p[0] - ry) ** 2 + (p[1] - rz) ** 2)]
        fixed += list(ib.nodal_dofs[0, nodes])
    w = solve(*condense(K, f, D=np.array(fixed)))
    wn = w[ib.nodal_dofs[0]]                     # vertex deflections [mm]
    face = (np.abs(p[0]) <= CY)
    # bending stress from element-wise curvatures at quadrature points
    cb = ib.interpolate(w)
    H = cb.hess                                  # [2,2,nel,nqp]
    kxx, kyy, kxy = H[0, 0], H[1, 1], H[0, 1]
    Mx = -D * (kxx + nu * kyy); My = -D * (kyy + nu * kxx); Mxy = -D * (1 - nu) * kxy
    sx, sy, txy = 6 * Mx / t**2, 6 * My / t**2, 6 * Mxy / t**2
    vm = np.sqrt(sx**2 - sx * sy + sy**2 + 3 * txy**2)
    return dict(q=q, wmax=np.abs(wn).max(), wrange=wn[face].max() - wn[face].min(), smax=vm.max())

if __name__ == "__main__":
    zc = (Z0 + Z1) / 2
    lay = {
        "A current 4 (z 28, 94)": [(s * 72, z) for s in (-1, 1) for z in (28.35, 94.35)],
        "B 4 at 0.207 h (z 45, 153)": [(s * 72, z) for s in (-1, 1) for z in (Z0 + 0.207 * (Z1 - Z0), Z0 + 0.793 * (Z1 - Z0))],
        "C 4 corners (z 20, 178)": [(s * 72, z) for s in (-1, 1) for z in (20.0, 178.0)],
        "D 6 (z 20, 99, 178)": [(s * 72, z) for s in (-1, 1) for z in (20.0, zc, 178.0)],
        "E 2 (z 99)": [(s * 72, zc) for s in (-1, 1)],
    }
    for F in (2943.0, 10000.0):
        print(f"\nF = {F:.0f} N")
        for k, r in lay.items():
            o = run(F, r)
            print(f"  {k:28s} q={o['q']:.4f} MPa  w_max={o['wmax']:.3f} mm  w_range(face)={o['wrange']:.3f} mm  sigma_vm,max={o['smax']:.0f} MPa")
