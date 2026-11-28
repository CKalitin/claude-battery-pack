"""Option D cooling check (2026-11-27, as-built geometry from cad/tower17.py): no pack fan; MEAN WELL's 40 mm fan at the rear wall blows into the box onto the
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
import math, os, sys

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

# ---- geometry: as built in cad/tower17.py (2026-11-27)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import tower17 as t
BORE_R = 18.5                                # the fan's own Ø37 inlet, flat on the rear plate (D41a): only this opening feeds the fan
def lens(d, r, R_):                          # overlap area of a hole (radius r) with the bore (radius R_), centres d apart
    if d >= r + R_: return 0.0
    if d <= R_ - r: return math.pi * r * r
    a = r * r * math.acos((d * d + r * r - R_ * R_) / (2 * d * r)); b = R_ * R_ * math.acos((d * d + R_ * R_ - r * r) / (2 * d * R_))
    return a + b - 0.5 * math.sqrt((-d + r + R_) * (d + r - R_) * (d - r + R_) * (d + r + R_))
def fan_open_area(hole_d):                   # m^2 of rear-grid holes open into the spacer bore
    return sum(lens(math.hypot(y - t.FAN_Y, z - t.FAN_Z), hole_d / 2, BORE_R) for y, z in t.rear_holes()) * 1e-6
IN_SQUARE = [p for p in t.rear_holes() if abs(p[0] - t.FAN_Y) <= 20 and abs(p[1] - t.FAN_Z) <= 20]   # behind the 40 x 40 spacer
N_REAR = len(t.rear_holes()) - len(IN_SQUARE)        # rear holes open to the box
N_FRONT = len(t.air_holes())                         # diffuser + LED board holes (the front path)

def R_area(area, K):
    return K * RHO / 2 / area ** 2
# front path: plate holes (4.8) -> diffuser holes (6) -> 3 mm gap -> LED board holes (6) -> the 6 mm standoff gap behind it
R_front = (R(N_FRONT, A_HOLE, 1 / CD ** 2) + 2 * R(N_FRONT, A_AIR, 1 / CD ** 2) + 1.5 * RHO / 2 / (7e-3 * 0.160) ** 2)
R_rear = R(N_REAR, A_HOLE, 1 / CD ** 2)

def solve(R_in, rear_open=True):
    lo, hi = 0.0, P0
    for _ in range(200):
        pb = (lo + hi) / 2
        q_out = math.sqrt(pb / R_front) + (math.sqrt(pb / R_rear) if rear_open else 0.0)
        if fan_dp(q_out) - R_in * q_out ** 2 > pb:
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
    "Charger relay coil, TE F4 90 ohm at 13.2 V": 13.2 ** 2 / 90,
    "Front LED board, firmware cap, typical (spec/interface.md §5; peak 10 W)": 5.0,
    "Power path at 40 A (cooling_v16 scaling)": 40 ** 2 * 400e-6,
}
P = sum(HEAT.values())
U = 1 / (1 / 9.5 + 1 / 7.0)                                   # W/m2K (v14 section 11)
_L, _W, _H = (t.XF + 2 * t.PT - t.XR) / 1000, t.WL / 1000, t.H / 1000
A_ENC = 2 * (_L * _W + _L * _H + _W * _H)                     # outer box as built
UA = U * A_ENC

def air(q_m3s):
    return q_m3s * 60 / 0.0283168                             # CFM

if __name__ == "__main__":
    K = 1 / CD ** 2
    out = []
    say = lambda x="": out.append(x)
    say("v17 option D cooling, as built (cad/analysis/cooling_D.py, 2026-11-27). Fan curve UNCONFIRMED (distributor data).")
    say(f"box: inside {t.L_IN:.1f} x {t.W_IN:.1f} x {t.LID_IN:.0f} mm; enclosure {A_ENC:.3f} m2, UA {UA:.2f} W/K; fan at x {t.FAN_X0:.0f}..{t.FAN_X0 + 20:.0f}, "
        f"{t.INV_X0 - (t.FAN_X0 + 20):.0f} mm from the inverter DC face")
    say(f"rear holes {len(t.rear_holes())} (Ø{t.HOLE_D}); {len(t.fan_holes())} in the R20 fan circle, {len(IN_SQUARE)} behind the 40 x 40 spacer; "
        f"open into the Ø37 bore at Ø4.8: {fan_open_area(4.8) * 1e6:.0f} mm2; front air holes {N_FRONT}")
    say(f"Heat, UPS case P = {P:.1f} W (sealed box {P / UA:.1f} K); without the LED board {P - 5:.1f} W")
    for k, v in HEAT.items():
        say(f"  {v:6.2f} W  {k}")
    say()
    say(f"{'rear-plate case':52s} {'fan CFM':>8s} {'front m3/h':>10s} {'dT mixed':>9s} {'dT front-only':>13s}")
    cases = [("as drawn: Ø4.8 grid holes", R_area(CD * fan_open_area(4.8), 1.0), True),
             ("Ø6.5 holes at the same positions", R_area(CD * fan_open_area(6.5), 1.0), True),
             ("Ø37 cutout + 40 mm wire guard (+1 part)", R_area(CD * math.pi * 0.0185 ** 2, 1.0) + R_area(math.pi * 0.0185 ** 2, 0.3), True),
             ("Ø37 cutout, rear grid blanked (+1 sheet)", R_area(CD * math.pi * 0.0185 ** 2, 1.0), False),
             ("Ø6.5 holes, rear grid blanked (+1 sheet)", R_area(CD * fan_open_area(6.5), 1.0), False)]
    res = {}
    for name, rin, ro in cases:
        pb, q, qf, qr = solve(rin, ro)
        dm, df = P / (RHO * CP * q + UA), P / (RHO * CP * qf + UA)
        res[name] = (q, qf, dm, df)
        say(f"{name:52s} {air(q):8.1f} {qf * 3600:10.1f} {dm:8.1f}K {df:12.1f}K")
    say()
    q, qf, _, _ = res["Ø6.5 holes at the same positions"]
    for name, p_ in (("inverting 400 W only (charger off, relay open)", P - HEAT[list(HEAT)[1]] - 13.2 ** 2 / 90),
                     ("charging 20 A only (inverter off)", P - HEAT[list(HEAT)[0]]),
                     ("UPS with inverter at 300 W", P - 400 * (1 / 0.89 - 1) + 300 * (1 / 0.89 - 1))):
        say(f"Ø6.5, {name:48s} P {p_:5.1f} W: dT mixed {p_ / (RHO * CP * q + UA):4.1f} K | front-only {p_ / (RHO * CP * qf + UA):4.1f} K")
    q, qf, _, _ = res["as drawn: Ø4.8 grid holes"]
    for name, p_ in (("inverting 400 W only", P - HEAT[list(HEAT)[1]] - 13.2 ** 2 / 90), ("charging 20 A only", P - HEAT[list(HEAT)[0]])):
        say(f"Ø4.8, {name:48s} P {p_:5.1f} W: dT mixed {p_ / (RHO * CP * q + UA):4.1f} K | front-only {p_ / (RHO * CP * qf + UA):4.1f} K")
    txt = "\n".join(out)
    print(txt)
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "versions", "v17-option-d")
    open(os.path.join(d, "cooling.txt"), "w").write(txt + "\n")
