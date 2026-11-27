"""Option D cooling check (2026-11-27): no pack fan; MEAN WELL's 40 mm fan at the rear wall blows into the box onto the
inverter's DC end (its rated forced-air condition), the NPB-360 has its own internal fan.

Network (pressures relative to ambient; p_b = box overpressure):
  ambient -> rear-plate holes in front of the 40 mm fan -> fan -> box
  box -> front plate holes + LED board / diffuser holes -> ambient
  box -> the rest of the rear hole grid -> ambient        (the fan's own exhaust can leave next to it)
Two bounds on the air that carries heat out:
  mixed:       all fan flow leaves at the box air temperature  -> dT = P / (rho c q_fan + UA)
  front-only:  only the share leaving through the front counts  -> dT = P / (rho c q_front + UA)   (v16-style pessimism)
Same orifice method and constants as cooling_v16.py. Run: ~/.venvs/cad/bin/python cad/analysis/cooling_D.py
"""
import math

RHO, CP = 1.2, 1005.0
CD = 0.78                                   # short-tube orifice (cooling_v16)
A_HOLE = math.pi * 4.8 ** 2 / 4 * 1e-6      # rear and front plate holes, dia 4.8
A_AIR = math.pi * 6.0 ** 2 / 4 * 1e-6       # LED board + diffuser holes, dia 6
# Sunon MF40201VX-1000U-G99, 12 V: 10.8 CFM free air, 0.29 inH2O (72 Pa) shut-off, 27.5 dBA, 1.11 W
# (Digi-Key / distributor listings 2026-11-27; Sunon's own sheet not found -> UNCONFIRMED). Curve shape as cooling_v16.
Q0, P0 = 10.8 * 0.0283168 / 60, 0.29 * 249.089
def fan_dp(q):
    return P0 * max(0.0, 1 - (q / Q0) ** 1.4)
def R(n, a, K):                              # quadratic resistance of n parallel holes of area a
    return K * RHO / 2 / (n * a) ** 2

# ---- geometry (option D box, UNCONFIRMED until tower17): inside ~314 x 168 x 333
N_REAR = 636            # v16: 703 holes over 186.8 inside -> 19 of 21 columns at 168 inside
N_FAN = 21              # rear holes inside the 40 mm fan circle (pitch 7.78)
N_FRONT = 223           # v16: 244 open front holes on a 175-wide LED board -> scaled to a ~160-wide board

R_fan_in = R(N_FAN, A_HOLE, 1 / CD ** 2)
R_front = R(N_FRONT, A_HOLE, 1 / CD ** 2) + R(N_FRONT, A_AIR, 1 / CD ** 2) + 1.5 * RHO / 2 / (8e-3 * 0.160) ** 2   # + the 8 mm gap behind the board
R_rear = R(N_REAR - N_FAN, A_HOLE, 1 / CD ** 2)

def solve(rear_open=True):
    lo, hi = 0.0, P0
    for _ in range(200):
        pb = (lo + hi) / 2
        q_out = math.sqrt(pb / R_front) + (math.sqrt(pb / R_rear) if rear_open else 0.0)
        # fan must supply q_out against pb + its inlet loss
        if fan_dp(q_out) - R_fan_in * q_out ** 2 > pb:
            lo = pb
        else:
            hi = pb
    qf = math.sqrt(pb / R_front); qr = math.sqrt(pb / R_rear) if rear_open else 0.0
    return pb, qf + qr, qf, qr

# ---- heat, UPS case (inverting at 400 W while charging at 20 A)
HEAT = {
    "NTS-400P-112, 400 W out, eta 89 % (-112 column, NTS-400P-SPEC 2026-03-26; v16 used 91 %, the -212 value)": 400 * (1 / 0.89 - 1),
    "NPB-360-12TB, 20 A x 14.2 V, eta 88.5 % (TB, NPB-360-SPEC 2026-07-06)": 20 * 14.2 * (1 / 0.885 - 1),
    "GV141BAX coil hold 2.8 W": 2.8,
    "BMS board (estimate)": 2.0,
    "Tesla shunt module (estimate)": 0.25,
    "40 mm fan 1.11 W": 1.11,
    "Charger relay coil (estimate, TBD part)": 1.5,
    "Power path at 40 A (cooling_v16 scaling)": 40 ** 2 * 400e-6,
}
P = sum(HEAT.values())
U = 1 / (1 / 9.5 + 1 / 7.0)                                   # W/m2K (v14 section 11)
A_ENC = 2 * (0.322 * 0.174 + 0.322 * 0.345 + 0.174 * 0.345)   # outer box ~322 x 174 x 345 mm
UA = U * A_ENC

if __name__ == "__main__":
    print(f"Heat P = {P:.1f} W (UPS case); enclosure {A_ENC:.3f} m2, UA {UA:.2f} W/K; sealed box dT = {P / UA:.1f} K")
    for k, v in HEAT.items():
        print(f"  {v:6.2f} W  {k}")
    print(f"Inverter alone at 300 W: {300 * (1 / 0.89 - 1):.1f} W loss -> P = {P - 400 * (1 / 0.89 - 1) + 300 * (1 / 0.89 - 1):.1f} W")
    for name, ro in (("full rear grid (as v16, the look Chris likes)", True), ("rear holes only in front of the fan", False)):
        pb, q, qf, qr = solve(ro)
        print(f"\n{name}: box +{pb:.2f} Pa; fan {q * 3600:.1f} m3/h = {q / Q0 * 100:.0f} % of free air "
              f"({q * 60 / 0.0283168:.1f} CFM vs MEAN WELL's 10 CFM condition); out front {qf * 3600:.1f}, out rear {qr * 3600:.1f} m3/h")
        print(f"  dT mixed {P / (RHO * CP * q + UA):.1f} K | front-only {P / (RHO * CP * qf + UA):.1f} K")
        for p_ in (P - 400 * (1 / 0.89 - 1) + 300 * (1 / 0.89 - 1), P - HEAT[list(HEAT)[1]] + 10 * 14.2 * (1 / 0.885 - 1)):
            pass
    pb, q, qf, qr = solve(True)
    P300 = P - 400 * (1 / 0.89 - 1) + 300 * (1 / 0.89 - 1)
    P_cap = P - HEAT[list(HEAT)[1]] + 10 * 14.2 * (1 / 0.885 - 1)
    print(f"\nfull grid, inverter 300 W: dT mixed {P300 / (RHO * CP * q + UA):.1f} | front-only {P300 / (RHO * CP * qf + UA):.1f} K")
    print(f"full grid, 400 W + charge capped at 10 A: dT mixed {P_cap / (RHO * CP * q + UA):.1f} | front-only {P_cap / (RHO * CP * qf + UA):.1f} K")
    print(f"charging only (20 A, inverter off): dT mixed {(P - HEAT[list(HEAT)[0]]) / (RHO * CP * q + UA):.1f} | front-only {(P - HEAT[list(HEAT)[0]]) / (RHO * CP * qf + UA):.1f} K")
    print(f"inverting only (400 W, charger off): dT mixed {(P - HEAT[list(HEAT)[1]] - 1.5) / (RHO * CP * q + UA):.1f} | front-only {(P - HEAT[list(HEAT)[1]] - 1.5) / (RHO * CP * qf + UA):.1f} K")
