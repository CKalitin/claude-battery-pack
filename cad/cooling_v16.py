"""v16 cooling check: flow network through the box + lumped air temperature rise (replaces the v14 area-ratio estimate).

Network (pressures relative to ambient, the NF-A14 at the rear plate exhausting):
  ambient -> front plate holes -> LED-board/diffuser air holes -> (lower holes: 8 mm gap up to the bay) -> bay
          -> converter plane: inverter channel | charger level | cell side gaps -> rear plenum
  ambient -> rear-plate holes OUTSIDE the fan circle -> rear plenum           (short circuit)
  rear plenum -> fan -> rear-plate holes INSIDE the fan circle -> ambient
Each restriction: dp = K * rho/2 * (Q/A)^2 (orifices: K = 1/Cd^2).
Run: python cooling_v16.py   (prints the table used in docs/v16-cooling.md)
"""
import math
import tower15 as t

RHO, CP = 1.2, 1005.0                 # air density [kg/m^3], specific heat [J/(kg K)]
CD_THICK = 0.78                       # short-tube orifice, t/d ~ 1 (4.75 mm plate, 4.8 mm hole) - textbook range 0.75-0.82
CD_STACK = 0.78                       # diffuser + LED board, 4.6 mm long Dia 6 hole
A_HOLE = math.pi * 4.8 ** 2 / 4 * 1e-6
A_AIR = math.pi * 6.0 ** 2 / 4 * 1e-6

# NF-A14 5V PWM at 100 %: 140.2 m3/h free air, 2.08 mm H2O shut-off (noctua.at spec page). Curve shape between the
# two points is not published as numbers: p = p0 (1 - (Q/Q0)^1.4) is a typical axial-fan fit. UNCONFIRMED shape.
Q0, P0 = 140.2 / 3600, 2.08 * 9.80665

def fan_dp(q, n_rel=1.0):
    """Fan pressure rise [Pa] at flow q [m3/s]; fan laws for speed fraction n_rel."""
    q0, p0 = Q0 * n_rel, P0 * n_rel ** 2
    return p0 * max(0.0, 1 - (q / q0) ** 1.4)

def k_of(A_list_K):
    """Combine series restrictions into one 'resistance' R with dp = R q^2."""
    return sum(K * RHO / 2 / A ** 2 for (A, K) in A_list_K)

def par(*R):
    """Parallel combination of quadratic resistances: q = sum sqrt(dp/R_i) -> R = 1/(sum 1/sqrt(R_i))^2."""
    return 1.0 / sum(1 / math.sqrt(r) for r in R) ** 2

def geometry(blank_rear=False, inv_fan=False):
    air = t.air_holes()
    n_lo = sum(1 for p in air if p[1] <= t.EP_TOP)
    n_hi = len(air) - n_lo
    rear = t.rear_holes()
    fy, fz = t.FAN_YZ
    n_in = sum(1 for p in rear if math.hypot(p[0] - fy, p[1] - fz) <= 66.0)      # holes the impeller faces (hub excluded later by Cd)
    n_out = 0 if blank_rear else len(rear) - n_in
    # internal areas [m^2]
    w_in = 2 * (t.W / 2 - t.T)                       # 186.8 mm inside width
    gap = 8.0e-3 * (2 * t.PANEL_Y) * 1e-3                 # LED board back -> module end plate: 8 mm x board width
    lid_in = t.H - t.T
    a_inv_unit = t.INV[1] * t.INV[2] * 1e-6           # inverter end face 100.5 x 34
    a_inv_chan = w_in * (lid_in - t.Z_TRAY2) * 1e-6 - a_inv_unit - 0.0       # bypass beside/above the inverter
    a_chg_unit = t.CHG[1] * t.CHG[2] * 1e-6
    a_chg_chan = w_in * (t.Z_TRAY2 - t.Z_T1TOP) * 1e-6 - a_chg_unit
    a_side = 2 * 14.0e-3 * (t.Z_TRAY1 - t.Z_CELL) * 1e-3  # 14 mm gaps between the cell module and the walls, both sides
    return dict(n_lo=n_lo, n_hi=n_hi, n_in=n_in, n_out=n_out, gap=gap, a_inv_unit=a_inv_unit, a_inv_chan=a_inv_chan,
                a_chg_unit=a_chg_unit, a_chg_chan=a_chg_chan, a_side=a_side, n_air_all=len(t.air_holes(True)), n_rear=len(rear))

K_UNIT = 4.0     # converter body (vented cover, dense parts) as a lumped loss on its end-face area. UNCONFIRMED (no MEAN WELL data)
K_DUCT = 1.5     # bypass channels: entry 0.5 + exit 1.0 (length ~200 mm, friction small at these velocities)

def solve(blank_rear=False, n_rel=1.0):
    g = geometry(blank_rear)
    # front: plate holes then board holes, per group; lower group adds the 8 mm gap (turn + exit, K 1.5 on the gap area)
    Rf_hi = k_of([(g["n_hi"] * A_HOLE, 1 / CD_THICK ** 2), (g["n_hi"] * A_AIR, 1 / CD_STACK ** 2)])
    Rf_lo = k_of([(g["n_lo"] * A_HOLE, 1 / CD_THICK ** 2), (g["n_lo"] * A_AIR, 1 / CD_STACK ** 2), (g["gap"], 1.5)])
    R_front = par(Rf_hi, Rf_lo)
    # converter plane: three parallel paths; each converter path = unit (K_UNIT) in parallel with its bypass (K_DUCT)
    R_inv = par(k_of([(g["a_inv_unit"], K_UNIT)]), k_of([(g["a_inv_chan"], K_DUCT)]))
    R_chg = par(k_of([(g["a_chg_unit"], K_UNIT)]), k_of([(g["a_chg_chan"], K_DUCT)]))
    R_side = k_of([(g["a_side"], K_DUCT + 1.0)])                 # + 1.0: turns at both ends
    R_mid = par(R_inv, R_chg, R_side)
    R_path = R_front + R_mid
    R_short = k_of([(g["n_out"] * A_HOLE, 1 / CD_THICK ** 2)]) if g["n_out"] else float("inf")
    R_out = k_of([(g["n_in"] * A_HOLE, 1 / CD_THICK ** 2)])       # fan outlet through the holes in its circle
    # unknown: plenum suction s > 0.  q_path = sqrt(s/R_path), q_short = sqrt(s/R_short); fan: fan_dp(q) = s + R_out q^2
    lo, hi = 0.0, P0 * n_rel ** 2
    for _ in range(200):
        s = (lo + hi) / 2
        qp = math.sqrt(s / R_path); qs = 0.0 if R_short == float("inf") else math.sqrt(s / R_short)
        q = qp + qs
        if fan_dp(q, n_rel) - R_out * q ** 2 > s:
            lo = s
        else:
            hi = s
    # split of the through flow at the converter plane (same dp across each parallel branch)
    dpm = R_mid * qp ** 2
    q_inv_branch = math.sqrt(dpm / R_inv)
    q_inv_unit = math.sqrt(dpm / k_of([(g["a_inv_unit"], K_UNIT)]))
    q_chg_branch = math.sqrt(dpm / R_chg)
    q_side = math.sqrt(dpm / R_side)
    return dict(g=g, s=s, q_fan=q, q_path=qp, q_short=qs, q_inv_branch=q_inv_branch, q_inv_unit=q_inv_unit,
                q_chg_branch=q_chg_branch, q_side=q_side, v_inv_face=q_inv_unit / g["a_inv_unit"])

# ---------------- heat (UPS pass-through: inverter 400 W out while the charger runs at full current) ----------------
HEAT = {
    "NTS-400P-112 inverter, 400 W out, eta 91 % (MEAN WELL spec 2026-03-26)": 400 * (1 / 0.91 - 1),
    "NPB-450-12 charger, 25 A x 14.2 V, eta 92 % (MEAN WELL spec 2026-07-06)": 25 * 14.2 * (1 / 0.92 - 1),
    "GV141BAX coil hold, 0.23 A x 12 V = 2.8 W (GV14 datasheet rev 28-Apr-2022)": 2.8,
    "Control board (ESP32 active Wi-Fi ~0.6 W, buck losses, BQ76952, LEDs at low duty) - estimate": 2.0,
    "Tesla shunt module 5 V x ~50 mA - estimate": 0.25,
    "NF-A14 5V PWM motor (0.99 W typ, noctua.at)": 0.99,
    "Power path at 40 A (copper 90 uOhm, MRBF 50 A + 250 A, joints) - from v16-calcs scaling": 40 ** 2 * 400e-6,
}
P = sum(HEAT.values())

# walls: U = 9.5 W/m2K outside (convection + radiation, powder coat) in series with 7 inside (v14 section 11)
U = 1 / (1 / 9.5 + 1 / 7.0)
A_ENC = 2 * (t.L_IN + 2 * t.PT) * 1e-3 * (t.W + t.H) * 1e-3 + 2 * (t.W * t.H) * 1e-6   # box surface [m^2]

def dT(q):
    return P / (RHO * CP * q + U * A_ENC)

def jet_fractions(rh=20.0):
    """Share of the fan's annulus (hub r 20 mm, UNCONFIRMED) projected onto each converter's end face."""
    import numpy as np
    fy, fz = t.FAN_YZ; R = t.FAN[0] / 2
    y = np.linspace(-R, R, 701); z = np.linspace(fz - R, fz + R, 701); Y, Z = np.meshgrid(y, z)
    r = np.hypot(Y - fy, Z - fz); ann = (r <= R) & (r >= rh)
    inv = (abs(Y) <= t.INV[1] / 2) & (Z >= t.Z_T2TOP) & (Z <= t.Z_T2TOP + t.INV[2])
    chg = (abs(Y) <= t.CHG[1] / 2) & (Z >= t.Z_T1TOP) & (Z <= t.Z_T1TOP + t.CHG[2])
    return (ann & inv).sum() / ann.sum(), (ann & chg).sum() / ann.sum()

if __name__ == "__main__":
    REQ_CFM = 10.0
    q_req = REQ_CFM * 0.0283168 / 60                  # 10 CFM in m3/s
    print(f"Heat P = {P:.1f} W; enclosure A = {A_ENC:.3f} m2, UA = {U * A_ENC:.2f} W/K")
    for k, v in HEAT.items():
        print(f"  {v:6.2f} W  {k}")
    print(f"Inverter forced-air rating (MEAN WELL derating curve): 100 % to 40 C, 40 % at 70 C, with a 10 CFM fan 5 cm from the DC end."
          f" Natural convection: ~60 % (240 W) to ~55 C. 10 CFM = {q_req*3600:.1f} m3/h; over the 100.5 x 34 end face = {q_req/ (t.INV[1]*t.INV[2]*1e-6):.2f} m/s")
    rows = []
    for name, kw in (("A: v16 as drawn (full rear grid, 244 front air holes)", dict()),
                     ("B: rear grid blanked outside the fan circle (sheet behind the plate)", dict(blank_rear=True))):
        r = solve(**kw)
        g = r["g"]
        rows.append((name, r))
        print(f"\n{name}")
        print(f"  front air holes {g['n_lo']+g['n_hi']} (of {g['n_air_all']}; {g['n_hi']} straight into the bay), rear holes {g['n_rear']}: {g['n_in']} in the fan circle, {g['n_out']} open around it")
        print(f"  fan {r['q_fan']*3600:.1f} m3/h at {r['s']:.2f} Pa plenum suction; through the box {r['q_path']*3600:.1f} m3/h; short circuit {r['q_short']*3600:.1f} m3/h")
        print(f"  converter plane: inverter branch {r['q_inv_branch']*3600:.1f} m3/h (through the unit {r['q_inv_unit']*3600:.1f} m3/h = {r['q_inv_unit']/q_req:.2f} x 10 CFM, face velocity {r['v_inv_face']:.2f} m/s);"
              f" charger branch {r['q_chg_branch']*3600:.1f}; cell side gaps {r['q_side']*3600:.1f}")
        print(f"  air rise dT = {dT(r['q_path']):.1f} K  (sealed box: {P/(U*A_ENC):.1f} K)")
        fi, fc = jet_fractions()
        print(f"  if the fan is flipped to INTAKE: its jet hits the converter AC ends 40 mm away; {fi*100:.0f} % of the fan annulus faces the inverter end"
              f" ({fi*r['q_fan']*3600:.1f} m3/h = {fi*r['q_fan']/q_req:.2f} x 10 CFM), {fc*100:.0f} % the charger end")
