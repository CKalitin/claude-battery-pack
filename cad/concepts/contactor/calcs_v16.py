"""v16 calculations: every number quoted in docs/v16-decisions.md comes from here. Run: python calcs_v16.py > ../../../docs/v16-calcs.txt"""
import json, math
RHO_CU = 1.72e-8          # ohm*m, annealed copper at 20 C (IACS)
IN = 25.4

def r_bar(L_mm, w_mm, t_mm):
    return RHO_CU * (L_mm / 1000) / ((w_mm * t_mm) / 1e6)

print("== 1. Currents ==")
I_OUT = 175.0                                   # A, SB175 DC output (pack spec)
P_INV, V_PACK, ETA_INV = 400.0, 12.0, 0.91     # W, V (low-ish pack voltage, conservative), NTS-400P-112 efficiency (spec)
I_INV = P_INV / (V_PACK * ETA_INV)
I_CHG = 25.0                                    # A, NPB-450-12 rated output (Digi-Key attribute)
print(f"I_inv = P/(V*eta) = {P_INV}/({V_PACK}*{ETA_INV}) = {I_INV:.1f} A")
print(f"I_main (worst: SB175 out + inverter) = {I_OUT} + {I_INV:.1f} = {I_OUT + I_INV:.1f} A  vs MRBF 250 A -> {250/(I_OUT+I_INV):.2f}x")
print(f"charger fuse 30 A / {I_CHG} A = {30/I_CHG:.2f}x ; inverter fuse 50 A / {I_INV:.1f} A = {50/I_INV:.2f}x")
print(f"PP45 rating 45 A / {I_INV:.1f} A = {45/I_INV:.2f}x (continuous)")

print("\n== 2. + path copper (C1, 1/8 in = 3.175 mm bars) ==")
T = 3.175
segs = [  # name, length mm (centre line from the model path), width mm, thickness mm, current A
    ("riser (2 x 3/16 in pack strap)", 28.0, 25.0, 4.76, I_OUT + I_INV),
    ("flange to M10 stud", 18.0, 25.0, T, I_OUT + I_INV),
    ("5191 tab + strap (Blue Sea, UNCONFIRMED width)", 40.0, 16.0, 2.5, I_OUT + I_INV),
    ("Z-strap (pad + run + leg + foot)", 100.0, 19.0, T, I_OUT + I_INV),
    ("in-bar column to T1", 41.0, 14.0, T, I_OUT + I_INV),
    ("load bar T2 pad", 25.0, 16.0, T, I_OUT + I_INV),
    ("load bar wide run y 50-86", 70.0, 36.0, T, I_OUT + I_INV),
    ("SB+ pad", 8.0, 26.0, T, I_OUT),
]
Rt = 0.0; Pt = 0.0
for n, L, w, t, I in segs:
    R = r_bar(L, w, t); P = I * I * R; Rt += R; Pt += P
    print(f"{n:48s} L {L:5.0f} mm  A {w*t:6.1f} mm^2  J {I/(w*t):4.1f} A/mm^2  R {R*1e6:6.1f} uOhm  P {P:5.2f} W")
print(f"total copper (excl. joints, fuse, contactor): R {Rt*1e6:.0f} uOhm, P {Pt:.1f} W at {I_OUT+I_INV:.0f} A")

print("\n== 3. Leads ==")
AMP_90C = {10: 40, 8: 55, 6: 75}               # A, NEC Table 310.16, 90 C copper (not more than 3 conductors)
OD = {10: 5.6, 8: 6.9, 6: 8.6}                 # mm, fine-strand 105 C insulated, typical UNCONFIRMED
for awg, I, who in ((10, I_INV, "inverter (PP45 max 10 AWG)"), (8, I_CHG, "charger")):
    print(f"{who}: {awg} AWG {AMP_90C[awg]} A @90C vs {I:.1f} A -> {AMP_90C[awg]/I:.2f}x ; bend R = 4*OD = {4*OD[awg]:.0f} mm")

print("\n== 4. Plug keep-outs (room needed vs room in v16) ==")
need = {"charger DC (8 AWG ring + bend)": 27, "inverter DC (PP45 24.6 + 10 AWG bend 22 -> 42 with margin)": 42,
        "charger AC (RA C13, worst 37.9 + 2)": 40, "inverter AC (VH plug + wires)": 20}
have = {"charger DC (8 AWG ring + bend)": 30.2, "inverter DC (PP45 24.6 + 10 AWG bend 22 -> 42 with margin)": 50.8,
        "charger AC (RA C13, worst 37.9 + 2)": 40.0, "inverter AC (VH plug + wires)": 40.0}
for k in need:
    print(f"{k:60s} need {need[k]:5.1f}  have {have[k]:5.1f}  margin {have[k]-need[k]:+5.1f} mm")

print("\n== 5. Length growth ==")
L0, L1 = 375.0, 424.0
print(f"inside length {L0:.0f} -> {L1:.0f} mm (+{L1-L0:.0f}): converters -27 mm (DC room) + rear gap 18 -> 40 mm (+22)")
P_SECT = 2 * 307.4 + 190 + 2 * 42 + 190        # mm, body walls + floor + lid skirts + lid top (approx section perimeter)
dm_sheet = P_SECT * (L1 - L0) * 1.6 * 2.68e-3   # g, 5052 1.6 mm
dm_g10 = 2 * 176 * (L1 - L0) * 3.175 * 1.85e-3  # g, tray 1 + G10 floor strips (approx)
print(f"added mass ~ sheet {dm_sheet:.0f} g + G10 {dm_g10:.0f} g = {dm_sheet+dm_g10:.0f} g (UNCONFIRMED estimate)")
print(f"body half flat ~ {L1+10:.0f} x {307.4+95+20:.0f} mm = {(L1+10)/IN:.1f} x {(307.4+95+20)/IN:.1f} in vs SCS 30 x 44 in (bend), 30 x 36 in (powder)")

print("\n== 6. Fuse service ==")
print("MRBF lift = stud above block top = 44.5 - 11.0 = 33.5 mm; fuse top while lifting = z 249.3 + 16.3 + 33.5 = 299.1")
print("GV141BAX flange (turned 90 deg) reaches y 59.85; 2151 fuse housings start y 62.1 -> 2.25 mm clear")

print("\n== 7. Clearances (model checks, all 3 contactor variants) ==")
for v in ("gv14up", "gv14", "fet"):
    r = json.load(open(f"out/c1_module_{v}.json"))
    print(f"{v:7s} interferences {len(r['interferences'])}  + to - {r['pos_to_neg'][0]} mm ({r['pos_to_neg'][1]} / {r['pos_to_neg'][2]})  "
          f"pack to chassis {r['pack_to_chassis'][0]} mm  + path {r['paths']['pos']['length_mm']} mm  - path {r['paths']['neg']['length_mm']} mm")

print("\n== 8. Converter - lugs on the shunt node-B bolt (shunt unmodified) ==")
from c1_power_module import build
c = build("gv14up")
for a, b in (("lug_neg_inverter", "shunt_module"), ("lug_neg_charger", "shunt_module"), ("lug_neg_inverter", "contactor_gv141bax_inverted"),
             ("lug_neg_charger", "sb175_housing"), ("keepout_shunt_conn", "strap_main")):
    print(f"{a} to {b}: {c.parts[a].distance_to(c.parts[b]):.2f} mm")
