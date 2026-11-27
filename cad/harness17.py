"""v17 harnesses (docs/harnesses.md) as real parts: device-end connectors, BMS-end Micro-Fit plugs (J2-J9, one per
destination), wire bundles as tubes along top-down routes, lugs and rings on existing studs, inline ATM holders.
Naming: w_* wire tubes (insulated), plug_* connector bodies (insulated), lug_pos_/lug_neg_/ring_pos_/ring_neg_ bare
metal, fuseholder_*, ntc_probe, pe_ring.
Lengths: centre line of the modelled route from connector exit to connector exit (ring: from the ring barrel). Lid-mounted
ends get +150 mm service loop (W6). Connector dimensions are envelopes (UNCONFIRMED unless a datasheet is named).
Bundle radius r = 0.6 * d_wire * sqrt(n) + 0.3 (v16 rule); 10 AWG single r 2.9; mains 3 x 18 AWG UL1015 r 3.3."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
from lib import tube, cyl_between
from build123d import Pos, Rot
import tower17 as t
import bay17 as b
from tower17 import box, cyl_z, cyl_x, cyl_y, Z_P1, CU, Z_D1, Z_D2, LID_IN

LOOP = 150.0
OD = {"26": 1.3, "22": 1.6, "20": 1.9, "18": 1.85}     # 18 AWG: thin-wall, Micro-Fit crimps take <= 1.85 mm (harnesses.md)
def rb(n, awg):
    return round(OD[awg] / 2 + 0.05, 2) if n == 1 else round(0.6 * OD[awg] * math.sqrt(n) + 0.3, 2)

def lug90(x, y, z, ang, off, h, r_ring=8.5, r_barrel=5.0, th=1.8, hole=4.2):
    """90 deg ring lug (outline UNCONFIRMED): ring on the stud at z, tongue at angle ang [deg] about z, barrel up at `off`.
    Returns (solid, barrel top point)."""
    a = math.radians(ang)
    bx, by = x + off * math.cos(a), y + off * math.sin(a)
    tongue = Pos(x, y, z) * (Rot(0, 0, ang) * box(0, off, -4.5, 4.5, 0, th))
    s = cyl_z(x, y, z, z + th, r_ring) + tongue + cyl_z(bx, by, z, z + h, r_barrel)
    s -= cyl_z(x, y, z - 1, z + th + 1, hole)
    return s, (bx, by, z + h)

def ring(x, y, z, ang, r_ring, hole, L=14.0, th=0.8, r_barrel=2.4):
    """Straight insulated ring terminal: bare ring + tongue (returned as metal), barrel (insulated). Returns (metal, barrel, end)."""
    a = math.radians(ang)
    d = (math.cos(a), math.sin(a))
    L = max(L, r_ring + 6.0)
    cu = cyl_z(x, y, z, z + th, r_ring) + Pos(x, y, z) * (Rot(0, 0, ang) * box(0, r_ring + 2.0, -2.5, 2.5, 0, th))
    cu -= cyl_z(x, y, z - 1, z + th + 1, hole)
    zb = z + th + r_barrel
    p0 = (x + d[0] * (r_ring + 2.0), y + d[1] * (r_ring + 2.0), zb)
    p1 = (x + d[0] * L, y + d[1] * L, zb)
    return cu, cyl_between(p0, p1, r_barrel), p1

def length(pts):
    return sum(math.dist(a, c) for a, c in zip(pts[:-1], pts[1:]))

def build():
    p, H = {}, []
    def wire(name, pts, r):
        p[name] = tube(pts, r)
        return length(pts)
    def rec(hid, run, L, lid=False, note=""):
        H.append(dict(id=hid, run=run, model=L, lid=lid, note=note))
    zb = b.Z_SHT                                   # shunt bar top
    zf = b.ZF                                      # MRBF top face
    J = {n: t.jgeom(n)[2] for n in t.BMS_J}
    for n in t.BMS_J:
        p[f"plug_{n}"] = t.jgeom(n)[1]

    # ------------------------------------------------ lugs and rings on existing studs
    lc, topP1b = lug90(*b.ST_CHG, zf, -90.0, 20.0, 24.0)
    li, topP3 = lug90(*b.ST_INV, zf, -90.0, 20.0, 24.0)
    ln2, topP2 = lug90(*b.NODE_B, zb, 90.0, 17.0, 24.0)
    ln4, topP4 = lug90(*b.NODE_B, zb + 1.8, 47.0, 17.5, 22.2)
    p["lug_pos_chg"], p["lug_pos_inv"], p["lug_neg_chg"], p["lug_neg_inv"] = lc, li, ln2, ln4
    cu, bar, e_gnd = ring(*b.NODE_A, zb, 90.0, 7.0, 4.2)
    p["ring_neg_gnd"], p["w_ring_gnd"] = cu, bar
    cu, bar, e_load = ring(*b.ST_INV, zf + 1.8, 0.0, 7.0, 5.0, L=14.0)                  # M10 / 3/8 in ring on the inverter stud
    p["ring_pos_load"], p["w_ring_load"] = cu, bar
    cu, bar, e_bp = ring(*b.FOOT, Z_P1 + CU, -45.0, 5.8, 3.2, L=13.0)                   # M6 ring under the strap-foot nut
    p["ring_pos_bplus"], p["w_ring_bplus"] = cu, bar

    # ------------------------------------------------ device-end connectors
    p["plug_pp45_pos"] = box(-111.0, -86.0, -13.0, -5.0, 286.0, 294.0)                  # Anderson 1327 housing 7.9 x 7.9 x 24.6
    p["plug_pp45_neg"] = box(-111.0, -86.0, -5.0, 3.0, 286.0, 294.0)
    p["plug_cn100"] = box(-94.0, -86.0, 28.0, 36.0, 288.0, 296.0)                       # JST XHP-3 (position ⚠️)
    p["plug_cn301"] = box(-94.0, -86.0, 45.0, 52.5, 288.0, 296.0)                       # JST XHP-2 (position ⚠️)
    p["plug_cn500"] = box(100.0, 110.0, 54.0, 75.0, 288.0, 298.0)                       # JST VHR-6N (position ⚠️)
    p["plug_c13"] = box(t.CHG_X1, t.CHG_X1 + 36.0, 37.0, 63.0, 235.0, 257.0)            # L-com ACPWRC-C13LR right angle (depth 35.6-37.9)
    p["plug_shunt_pair"] = box(-105.0, -75.0, -76.0, -54.0, 288.0, 298.0)               # pigtail receptacle + mating 2x5 plug (tesla-shunt.md §3a) ⚠️
    p["plug_led"] = box(t.XL0 - 6.0, t.XL0, t.LED_HDR_Y - 6.0, t.LED_HDR_Y + 6.0, 298.0, 308.0)
    for n, (x, y) in t.RELAY_PINS.items():
        p[f"plug_relay_{n}"] = box(x - 4.25, x + 4.25, y - 3.25, y + 3.25, 266.0, 286.0) - box(x - 3.2, x + 3.2, y - 0.5, y + 0.5, 265.0, 274.0)
    p["fuseholder_bplus"] = box(96.4, 136.0, -31.5, -16.5, 315.8, 326.2)                # Eaton ATM-FHID 39.6 x 10.4 x 15.0
    p["fuseholder_load"] = box(-59.6, -20.0, -31.5, -16.5, 312.8, 323.2)
    p["ntc_probe"] = box(92.0, 100.0, 57.5, 62.5, 314.0, 319.0)

    # ------------------------------------------------ DC power (10 AWG fine strand, r 2.9)
    R10 = 2.9
    vp, vn = t.CHG_VPOS, t.CHG_VNEG
    pts = [vp, (-130.0, 43.0, 243.0), (-130.0, 49.0, 268.0), (-130.0, 56.2, 270.0), (-130.0, 56.2, 293.0), (-141.0, 59.0, 293.0), (-141.0, 59.0, 286.0)]
    rec("P1a", "charger TB V+ -> relay pin 30", wire("w_p1a", pts, R10))
    pts = [(-141.0, 73.0, 286.0), (-141.0, 74.5, 300.0), (-129.0, 74.0, 304.0), (-129.0, 50.0, 304.0), (-132.0, 40.0, 303.0), (-132.0, -18.0, 303.0),
           (-122.0, -26.0, 303.0), (0.0, -26.0, 303.0), (14.0, -45.0, 308.0), (29.0, -63.0, 312.0), (topP1b[0], topP1b[1], 312.0), topP1b]
    rec("P1b", "relay pin 87 -> 2151 charger stud", wire("w_p1b", pts, R10))
    pts = [vn, (-132.0, 18.0, 241.0), (-136.0, 6.0, 248.0), (-136.0, -18.0, 262.0), (-122.0, -27.0, 272.0), (-96.0, -30.0, 278.0), (-84.0, -39.0, 288.0),
           (topP2[0], topP2[1], 290.0), topP2]
    rec("P2", "charger TB V- -> shunt node B", wire("w_p2", pts, R10))
    pts = [(-111.0, -9.0, 290.0), (-122.0, -9.0, 290.0), (-130.0, -13.0, 291.0), (-130.0, -24.0, 292.0), (-117.0, -27.0, 292.0), (0.0, -27.0, 292.0),
           (8.0, -50.0, 294.0), (14.0, -73.5, 298.0), (50.0, -74.5, 300.0), (65.0, -70.0, 308.0), (topP3[0], topP3[1], 311.0), topP3]
    rec("P3", "inverter TB1 (PP45 red) -> 2151 inverter stud", wire("w_p3", pts, R10))
    pts = [(-111.0, -1.0, 290.0), (-115.0, -1.0, 289.0), (-114.0, -3.0, 281.0), (-102.0, -12.0, 280.0), (-96.0, -22.0, 283.0), (-88.0, -29.5, 286.0), (-76.0, -37.0, 292.0),
           (topP4[0], topP4[1], 292.0), topP4]
    rec("P4", "inverter TB1 (PP45 black) -> shunt node B", wire("w_p4", pts, R10))

    # ------------------------------------------------ H1 shunt: module pigtail (soldered to the module, ~300 mm) -> mating plug -> J2
    pts = [(-107.25, -37.5, zb + 7.0), (-107.0, -45.0, 272.0), (-135.0, -50.0, 275.0), (-141.0, -70.0, 276.0), (-100.0, -73.0, 278.0),
           (-76.0, -70.0, 281.0), (-77.0, -56.0, 285.0), (-100.0, -51.0, 285.0), (-130.0, -62.0, 286.0), (-100.0, -70.0, 280.0),
           (-68.0, -68.0, 282.0), (-68.0, -65.0, 293.0), (-75.0, -65.0, 293.0)]
    wire("w_shunt_pigtail", pts, rb(8, "26"))
    rec("pigtail", "module pigtail -> 2x5 receptacle (existing, ~300 mm ⚠️)", length(pts))
    pts = [(-105.0, -65.0, 293.0), (-112.0, -65.0, 293.0), (-118.0, -66.0, 295.0), (-135.0, -62.0, 301.0), (-135.0, -43.0, 314.0), (-129.0, -30.0, 320.0),
           (-128.0, J["j2"][1], J["j2"][2]), J["j2"]]
    rec("H1", "2x5 mating plug -> J2", wire("w_h1_shunt", pts, rb(7, "22")))

    # ------------------------------------------------ H2 power taps -> J3 (18 AWG, fused at the source)
    j3 = J["j3"]
    pin = {n: j3[0] + dx for n, dx in (("bplus", 4.5), ("load", 1.5), ("gnd", -1.5), ("chassis", -4.5))}     # J3 1x4 (pins ⚠️)
    a = [e_bp, (154.5, -15.5, 262.0), (154.5, -15.5, 312.0), (150.0, -21.5, 321.0), (136.0, -24.0, 321.0)]
    a2 = [(96.4, -24.0, 321.0), (62.0, -24.0, 327.0), (-72.0, -24.0, 327.0), (pin["bplus"], -33.0, 326.0), (pin["bplus"], j3[1], j3[2])]
    L = wire("w_h2_bplus_a", a, rb(1, "18")) + wire("w_h2_bplus_b", a2, rb(1, "18")) + 39.6
    rec("H2", "B+: strap-foot ring -> 5 A ATM holder -> J3-1", L, note=f"holder starts {length(a):.0f} mm from the ring")
    a = [e_load, (87.0, -44.0, 288.0), (88.0, -38.0, 296.0), (88.0, -26.0, 312.0), (82.0, -24.0, 318.0), (-20.0, -24.0, 318.0)]
    a2 = [(-59.6, -24.0, 318.0), (-76.0, -25.0, 319.0), (pin["load"], -34.0, 321.0), (pin["load"], j3[1], j3[2])]
    L = wire("w_h2_load_a", a, rb(1, "18")) + wire("w_h2_load_b", a2, rb(1, "18")) + 39.6
    rec("H2", "LOAD+: 2151 inverter-stud ring -> 2 A ATM holder -> J3-2", L, note=f"holder starts {length(a):.0f} mm from the ring")
    a = [e_gnd, (-134.0, -43.0, 264.0), (-143.0, -42.0, 280.0), (-143.0, -40.0, 325.0), (-134.0, -40.0, 329.0), (-108.0, -41.0, 329.0),
         (pin["gnd"], -37.0, 326.0), (pin["gnd"], j3[1], j3[2])]
    rec("H2", "GND: node-A ring -> J3-3", wire("w_h2_gnd", a, rb(1, "18")))

    # H2b: IMD chassis reference, J3-4 -> M4 ring under the rear -y top screw
    y, z = t.IMD_YZ
    xi = t.XR + t.T
    m = cyl_x(xi + 1.0, xi + 1.8, y, z, 5.0) - cyl_x(xi, xi + 3, y, z, 2.1)
    p["ring_chassis"] = m + box(xi + 1.0, xi + 1.8, y + 4.0, -68.0, z - 2.5, z + 2.5)
    p["w_ring_chassis"] = cyl_y(xi + 1.9, -68.0, -62.0, z, 2.4)
    a = [(xi + 2.2, -62.0, z), (-155.0, -48.0, 306.0), (-150.0, -33.0, 320.0), (-134.0, -33.0, 327.0), (-104.0, -32.0, 326.0), (pin["chassis"], -31.0, 325.0),
         (pin["chassis"], j3[1], j3[2])]
    rec("H2b", "J3-4 -> chassis ring (rear -y top screw)", wire("w_h2b_chassis", a, rb(1, "22")))

    # ------------------------------------------------ H3 outputs: GV14 flying leads -> J4; relay coil + AC sense -> J6; CN301 -> J7
    j4 = J["j4"]
    pts = [(b.CT[0] - 29.95, b.CT[1], Z_P1 + 5.0), (93.0, -49.0, Z_P1 + 6.0), (91.5, -49.5, 266.0), (92.0, -47.0, 312.0), (91.0, -36.0, 328.5),
           (84.0, -12.0, 329.0), (60.0, 6.0, 328.0), (20.0, 25.0, 326.0), j4]
    rec("H3", "GV14 flying leads (38 cm) -> J4", wire("w_h3_coil", pts, rb(2, "20")), note="GV14 lead 380 mm: not cut")
    j6 = J["j6"]
    trunk = [j6, (j6[0] - 5.0, 58.0, 322.0), (-115.0, 59.0, 318.0), (-120.0, 63.0, 296.0), (-135.0, 63.0, 296.0)]
    wire("w_h3_relay", trunk, rb(3, "22"))
    tails = {"86": [(-135.0, 63.0, 296.0), (-146.0, 66.0, 294.0), (-146.0, 66.0, 286.0)],
             "85": [(-135.0, 63.0, 296.0), (-136.5, 66.0, 294.0), (-136.5, 66.0, 286.0)],
             "30": [(-135.0, 63.0, 296.0), (-143.5, 57.0, 297.0), (-143.5, 57.0, 286.0)]}
    for n, tl in tails.items():
        wire(f"w_h3_relay_{n}" if n != "30" else "w_h5_acsense", tl, rb(1, "22"))
        rec("H3" if n != "30" else "H5", f"J6 -> relay pin {n}" + (" (AC sense piggyback)" if n == "30" else ""), length(trunk) + length(tl))
    j7 = J["j7"]
    pts = [j7, (j7[0] - 2.0, 56.0, 321.0), (-87.0, 55.0, 316.0), (-100.0, 50.0, 308.0), (-101.0, 48.75, 292.0), (-94.0, 48.75, 292.0)]
    rec("H3", "J7 -> inverter CN301", wire("w_h3_cn301", pts, rb(2, "22")))

    # ------------------------------------------------ H4: button (lid) -> J8, LED board -> J5, box NTC -> J9
    j8, j5, j9 = J["j8"], J["j5"], J["j9"]
    pts = [(-120.0, -55.0, LID_IN - 30.0), (-122.0, -55.0, 299.0), (-128.0, -45.0, 308.0), (-128.8, -30.0, 312.0), (-128.8, 40.0, 312.0),
           (-126.0, 55.0, 320.0), (-100.0, 64.0, 327.0), (-60.0, 63.0, 326.0), (j8[0], 56.0, 324.5), j8]
    rec("H4", "lid button -> J8", wire("w_h4_btn", pts, rb(2, "22")), lid=True)
    pts = [j5, (14.0, 8.0, 323.0), (30.0, 2.0, 322.0), (74.0, -9.0, 322.5), (98.0, -14.0, 329.0), (127.0, -18.0, 329.5), (137.0, -38.0, 329.0),
           (148.0, -56.0, 322.0), (t.XL0 - 3.0, -60.0, 314.0), (t.XL0 - 3.0, -60.0, 308.0)]
    rec("H4", "J5 -> LED board header", wire("w_h4_led", pts, rb(3, "22")))
    pts = [j9, (j9[0] + 2.0, 58.0, 322.0), (-20.0, 64.0, 321.0), (60.0, 61.0, 318.0), (92.0, 60.0, 316.5)]
    rec("H4", "J9 -> box-air NTC", wire("w_h4_ntc", pts, rb(2, "22")))

    # ------------------------------------------------ H6 fan -> CN100, H7 antenna
    pts = [(t.FAN_X0 + t.FAN40[1], 17.0, 284.0), (-128.0, 22.0, 286.0), (-108.0, 32.0, 292.0), (-94.0, 32.0, 292.0)]
    rec("H6", "40 mm fan -> inverter CN100", wire("w_h6_fan", pts, rb(2, "26")), note="fan's own leads (length unread ⚠️)")
    u = t.ESP_UFL
    pts = [u, (-20.0, 35.0, 324.0), (-8.0, 36.0, 322.0), (4.0, 36.0, 318.0), (40.0, 6.0, 316.0), (90.0, -6.0, 319.0), (105.0, -5.0, 319.0), (114.0, -12.0, 316.0),
           (122.0, -17.0, 312.5), (137.0, -19.5, 312.0), (151.0, -19.5, 312.0), (t.XL0 + 0.8, -20.0, 310.0)]
    rec("H7", "ESP32 U.FL -> flex antenna", wire("w_h7_coax", pts, 0.7))

    # ------------------------------------------------ mains (UL 1015 18 AWG, own front corner, never bundled with LV)
    pts = [(t.CHG_X1 + 36.0, 50.0, 246.0), (100.0, 50.0, 247.0), (108.0, 55.0, 255.0), (117.0, 56.5, 262.0), (144.0, 56.5, 270.0),
           (151.5, 50.0, 294.0), (152.0, 38.0, 297.5), (152.0, 12.0, 298.0), (145.0, 2.0, 301.0), (144.0, 0.0, LID_IN - 25.0)]
    rec("A1", "charger C13 -> lid C14 inlet", wire("w_a1_ac_in", pts, 3.3), lid=True)
    pts = [(110.0, 62.0, 293.0), (118.0, 60.0, 293.0), (129.0, 55.0, 297.0), (141.0, 52.0, 297.0), (141.0, 49.0, LID_IN - 30.0)]
    rec("A2", "inverter CN500 -> lid NEMA 5-15R", wire("w_a2_ac_out", pts, 3.3), lid=True)
    y, z = t.PE_YZ
    xi = t.XF - t.T
    ring_m = cyl_x(xi - 1.8, xi - 1.0, y, z, 5.0) - cyl_x(xi - 3, xi, y, z, 2.1)
    ring_m += box(xi - 1.8, xi - 1.0, 68.0, y - 4.0, z - 2.5, z + 2.5)
    p["pe_ring"] = ring_m
    p["w_pe_barrel"] = cyl_y(xi - 1.9, 62.0, 68.0, z, 2.4)
    node = (156.0, 62.0, 308.0)
    a = [(xi - 2.2, 62.0, z), (160.0, 61.0, 311.0), node]
    wire("w_a3_pe_trunk", a, 2.0)
    to_out = [node, (155.0, 66.0, 299.0), (149.0, 61.0, 298.0), (147.0, 59.0, LID_IN - 30.0)]
    to_in = [node, (157.0, 44.0, 304.0), (157.0, 0.0, 303.0), (151.0, -5.0, 304.0), (150.0, -5.0, LID_IN - 25.0)]
    wire("w_a3_pe_out", to_out, 1.45)
    wire("w_a3_pe_in", to_in, 1.45)
    rec("A3", "PE: inlet -> chassis lug", length(a) + length(to_in), lid=True)
    rec("A3", "PE: outlet ground (= inverter FG via A2) -> chassis lug", length(a) + length(to_out), lid=True)
    return p, H

def table(H):
    rows = []
    for h in H:
        L = h["model"] + (LOOP if h["lid"] else 0.0)
        rows.append((h["id"], h["run"], round(h["model"]), "+150" if h["lid"] else "", int(math.ceil(L / 10.0) * 10), h["note"]))
    return rows

if __name__ == "__main__":
    _, H = build()
    for r in table(H):
        print(f"{r[0]:4s} {r[1]:58s} model {r[2]:4d} {r[3]:5s} -> {r[4]:4d} mm  {r[5]}")
