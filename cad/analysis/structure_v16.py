"""v16.3 structure: how the cells reach the enclosure, and whether the thin shell buckles under the pack's weight.

Load path (all in the model): cells -> clamped between the two module end plates (4 M5 rods, 300 kgf preload)
-> 4 x M4 screws up through the body floor into T-nuts in the end-plate feet -> body halves (5052 .063, two L
halves butt-seamed under the G10 floor) -> 7 x M4 into the wall tabs at each end -> front / rear 6061 .187 plates,
which carry the feet (the pack stands on them) and the handle slots (the pack is carried by them).
The converters and the power bay sit on tray 1, on the upper standoffs, on the end plates: same path.

So the body is a beam between the two plates, loaded at the two end-plate screw lines. Checked here:
  1. bending stress in the body section, and plate buckling of the walls in bending and of the floor in compression
  2. shear stress in the walls and shear buckling
  3. the M4 screws (module hold-down, plate tabs)
  4. what "compression members" exist at all (the rods are in tension; only the cells and insulators are compressed)
  5. EVE's own compression / swelling numbers (PBRI-LF105-D06-01 rev E, Table 16-17) against the rods and end plates
Writes docs/v16-structure.txt. Units: N, mm, MPa.
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import tower15 as t

g = 9.81
OUT = []
def p(s=""): OUT.append(s); print(s)

# ---------------- masses [kg] (v16.3 roll-up: CAD volume x density, catalog weights for bought parts) ----------------
M_CELLS = 8 * 1.98                    # EVE spec F
M_MODULE_OTHER = 1.24 + 0.2 + 0.25    # end plates, rods/nuts, G10 floor share
M_UPPER = 2.13 + 0.47 + 1.04 + 0.39 + 0.6   # converters, fan+contactor, copper, fuses/connectors, trays/G10/hardware above the module
M_SHELL = 4.82 - 1.24 + 0.65 + 0.3    # aluminium shell (body, lid, front/rear plates) + hardware
M_TOTAL = M_CELLS + M_MODULE_OTHER + M_UPPER + M_SHELL
W_MOD = (M_CELLS + M_MODULE_OTHER + M_UPPER) * g      # everything that reaches the body through the end-plate screws
p(f"Pack mass ≈ {M_TOTAL:.1f} kg; through the module hold-down screws: {W_MOD/g:.1f} kg = {W_MOD:.0f} N")

# ---------------- geometry ----------------
x_rear, x_front = t.XR, t.XF                  # plate inner faces = supports
x_ep = t.ep_x                                 # module hold-down screw lines
L = x_front - x_rear
a = x_ep[0] - x_rear                          # rear support -> rear screw line
b = x_front - x_ep[1]                         # front screw line -> front support
p(f"Supports (plates) x {x_rear:.1f} / {x_front:.1f} (span {L:.1f}); module screw lines x {x_ep[0]:.1f} / {x_ep[1]:.1f}")

# body section: the two L halves = U section, thin-walled, from the outer mould lines (midline ~ OML - T/2)
def seg_props(pts, T):
    A = Sy = 0.0
    segs = []
    for (y0, z0), (y1, z1) in zip(pts[:-1], pts[1:]):
        l = math.hypot(y1 - y0, z1 - z0); A += l * T; Sy += l * T * (z0 + z1) / 2
        segs.append((y0, z0, y1, z1, l))
    zc = Sy / A
    I = 0.0
    for y0, z0, y1, z1, l in segs:
        zm = (z0 + z1) / 2; dz = z1 - z0
        I += T * l * (dz ** 2 / 12 + (zm - zc) ** 2)
    return A, zc, I
ptsA, _ = t.half_oml(-1); ptsB, _ = t.half_oml(+1)
pts = ptsA[::-1] + ptsB[1:]                   # wall A top -> floor -> wall B top (seam joint ignored: G10 floor bridges it)
A, zc, I = seg_props(pts, t.T)
ztop = max(z for _, z in pts); zbot = 0.0
p(f"Body U section (lid not counted): A {A:.0f} mm², neutral axis z {zc:.1f}, I {I/1e6:.2f}e6 mm⁴, wall top z {ztop:.1f}")

# loads: two point loads at the screw lines (each half the module weight; worst case all on one)
for case, nload in (("standing / carried, 1 g", 1.0), ("carried, dropped onto the feet: 5 g", 5.0)):
    P = W_MOD * nload / 2
    Rr = P * (L - a) / L + P * b / L
    Rf = 2 * P - Rr
    M = max(Rr * a, Rf * b)                   # max moment is under a load point
    V = max(Rr, Rf)
    s_top = M * (ztop - zc) / I; s_bot = M * zc / I
    tau = V / (2 * (ztop - 25.0) * t.T)       # shear carried by the two walls
    p(f"\n[{case}] P = {P:.0f} N per screw line; reactions rear {Rr:.0f} N / front {Rf:.0f} N")
    p(f"  M_max {M/1e3:.1f} N·m; σ wall top {s_top:.2f} MPa (compression when standing); σ floor {s_bot:.2f} MPa; τ walls {tau:.2f} MPa")
    # plate buckling: wall (simply supported plate, pure bending k = 23.9; compression k = 4) - 5052-H32 E 70.3 GPa, ν 0.33
    E, nu = 70300.0, 0.33
    hw = ztop - t.CNR                          # straight wall height between the floor corner and the top facet
    sig_cr_bend = 23.9 * math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t.T / hw) ** 2
    bf = 2 * t.A_FLAT                          # floor flat width
    sig_cr_floor = 4.0 * math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t.T / bf) ** 2
    tau_cr = 5.35 * math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t.T / hw) ** 2
    p(f"  wall plate {hw:.0f} x {t.T} mm: σ_cr (bending) {sig_cr_bend:.1f} MPa -> margin {sig_cr_bend/max(s_top,1e-9):.0f}x; "
      f"τ_cr {tau_cr:.1f} MPa -> {tau_cr/tau:.0f}x")
    p(f"  floor flat {bf:.0f} x {t.T} mm (if it were in compression, carrying the pack upside down): σ_cr {sig_cr_floor:.2f} MPa -> {sig_cr_floor/max(s_bot,1e-9):.1f}x")
    p(f"  5052-H32 yield 193 MPa -> bending margin {193/max(s_top, s_bot):.0f}x")

# ---------------- screws ----------------
p("\n[Screws, 5 g drop]")
P5 = W_MOD * 5
n_hold = 4
F_hold = P5 / n_hold
# M4 into a steel T-nut: pull-through of the 1.6 mm 5052 floor under the screw head is the weak link
# punch-through shear: pi * d_head * t * 0.6 * UTS (5052-H32 UTS 228 MPa)
Fpt = math.pi * 7.0 * t.T * 0.6 * 228
p(f"  module hold-down: 4 x M4 carry {P5:.0f} N in tension -> {F_hold:.0f} N each; floor pull-through (Ø7 head) ≈ {Fpt:.0f} N -> {Fpt/F_hold:.1f}x")
p(f"    M4 8.8: proof 8.8 mm² x 600 MPa ≈ {8.78*600:.0f} N -> {8.78*600/F_hold:.1f}x")
F_tab = P5 / 2 / 7
p(f"  plate -> wall tabs: 7 x M4 per end in single shear, {F_tab:.0f} N each; bearing in 1.6 mm 5052 ≈ 4 x 1.6 x 2 x 193 = {4*1.6*2*193:.0f} N -> {4*1.6*2*193/F_tab:.1f}x")

# ---------------- what is in compression ----------------
p("\n[Compression members]")
p("  Tie rods (4 x M6 A4-70): tension only. The cells push the end plates apart; a tension member cannot buckle.")
p("  Cells + 9 Mylar insulators: the only parts in compression, 130.3 x 195.5 mm faces bearing on each other -> no slenderness, no buckling.")
p("  Upper standoffs (M4, 15 mm, hex 7): carry tray 1 + converters + power bay down into the end plates.")
P_so = (2.13 + 2.5) * g * 5 / 4
A_so = 3 * math.sqrt(3) / 2 * (7 / math.sqrt(3)) ** 2 - math.pi * 1.7 ** 2
Imin = 0.06 * 7 ** 4 - math.pi * 3.4 ** 4 / 64   # hex ~ 0.0601 s^4 (s = across flats)
Pcr = math.pi ** 2 * 69000 * Imin / (2 * 15.0) ** 2   # fixed-free (K = 2), aluminium
p(f"    5 g: {P_so:.0f} N each; Euler (K = 2, Al) {Pcr/1e3:.0f} kN -> {Pcr/P_so:.0f}x; σ {P_so/A_so:.1f} MPa")

# ---------------- EVE compression / swelling ----------------
p("\n[EVE LF105 rev E (PBRI-LF105-D06-01 E, 2023-05-31), Tables 16-17]")
p("  Recommended compression 3000-7000 N, instantaneous max 10000 N; swelling force BOL ≤ 3000 N, EOL (80 % SOH) ≤ 30000 N (rigid fixture)")
As = 20.1; proof = 450.0   # v16.3: 4 x M6 316 A4-70 (was M5, A_s 14.2)
for F in (2943, 7000, 10000, 30000):
    s = F / 4 / As
    p(f"  [M6] F {F/1e3:5.1f} kN: rod σ {s:5.0f} MPa ({'OK' if s < proof else 'YIELDS'} vs 450 proof, {proof/s:.2f}x); "
      f"end-plate deflection ≈ {0.078*F/2943:.2f} mm (v13 FE, linear)")
# system stiffness: rods + plates; how far must the stack grow before the rods reach proof?
E_ss = 193000.0; Lrod = t.STACK_L + 12.0
k_rods = 4 * E_ss * As / Lrod
k_plates = 1 / (2 * 0.078 / 2943)
k_sys = 1 / (1 / k_rods + 1 / k_plates)
F_proof = 4 * As * proof
p(f"  frame stiffness: rods {k_rods/1e3:.1f} kN/mm, two end plates {k_plates/1e3:.1f} kN/mm, series {k_sys/1e3:.1f} kN/mm")
p(f"  rods reach proof at {F_proof/1e3:.1f} kN = {(F_proof-2943)/k_sys:.2f} mm of stack growth past the 2.94 kN preload "
  f"({(F_proof-2943)/k_sys/(8*36.7)*100:.2f} % of 8 x 36.7 mm)")

open(os.path.join(HERE, "..", "..", "docs", "v16-structure.txt"), "w").write("\n".join(OUT) + "\n")
