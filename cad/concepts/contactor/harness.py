"""v16 signal and low-power wiring, modelled as real parts: plugs at both ends, wire bundles as tubes along the route,
ring terminals on existing studs (no new holes in purchased parts), inline fuse holders, cable ties through slots in our
own G10 parts. Everything is added to the C1 concept, so c.check() covers it (interference, + to - clearance for the bare
ring terminals) and the renders show it.

Board end: Molex Micro-Fit 3.0 right-angle headers along the top edge of the front board's back face (tower15.CTRL "j_*"),
mated from above. Device ends: the device's own connector (Tesla shunt J1, MEAN WELL DF11 / CN301, Noctua 4-pin, the
contactor's flying leads cut and crimped). Wire: 105 C insulation (ABYC E-11 / 33 CFR 183.425 table 5 basis).

Bundle radius: r = 0.6 * d_wire * sqrt(n) (loose round bundle), d_wire = insulated OD.
"""
import math
from lib import *
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import tower15 as t5

OD = {"24": 1.4, "22": 1.6, "20": 1.9, "18": 2.3}      # UL1007/1015-class insulated OD [mm], typical

def r_bundle(n, awg):
    return round(0.6 * OD[awg] * math.sqrt(n) + 0.3, 2)

XB = t5.XL0                       # board back face x (169.95)
ZH1 = 285.3                       # header top (board top edge)
PLUG_H = 11.0                     # Micro-Fit 3.0 receptacle housing above the header [mm] (Molex 43025 ~ 9.9 + latch)

def ctrl_y(name):
    y0, y1, z0, z1, h = t5.CTRL[name]
    return (y0 + y1) / 2, y0, y1, h

def board_plug(name):
    """Mated Micro-Fit receptacle on a board header; returns (shape, wire exit point on its top)."""
    yc, y0, y1, h = ctrl_y(name)
    shape = box(XB - h + 0.5, XB - 0.5, y0 + 0.4, y1 - 0.4, ZH1, ZH1 + PLUG_H)
    return shape, (XB - h / 2, yc, ZH1 + PLUG_H)

def ring(x, y, z, d, r_ring, hole_r, t=0.8, L=14.0, r_barrel=2.4):
    """Straight ring terminal on a stud at z (ring bottom), tongue + insulated barrel along d. Returns (ring copper, barrel, barrel end)."""
    ex, ey = x + d[0] * max(L, r_ring + 6.0), y + d[1] * max(L, r_ring + 6.0)
    cu = cyl_z(x, y, z, z + t, r_ring)
    cu += box(min(x, x + d[0] * (r_ring + 2)) - (2.5 if d[0] == 0 else 0), max(x, x + d[0] * (r_ring + 2)) + (2.5 if d[0] == 0 else 0),
              min(y, y + d[1] * (r_ring + 2)) - (2.5 if d[1] == 0 else 0), max(y, y + d[1] * (r_ring + 2)) + (2.5 if d[1] == 0 else 0), z, z + t)
    cu -= cyl_z(x, y, z - 1, z + t + 1, hole_r)
    zb = z + t + r_barrel + 0.2                      # insulated barrel rides on the tongue, crimp side up
    b0 = (x + d[0] * (r_ring + 3.5), y + d[1] * (r_ring + 3.5), zb)
    barrel = cyl_between(b0, (ex, ey, zb), r_barrel)
    return cu, barrel, (ex, ey, zb)

def inline_fuse(p, q, wide="x"):
    """Inline ATM fuse holder (Eaton Bussmann ATM-FHID: 1.56 x 0.41 x 0.59 in = 39.6 x 10.4 x 15.0 mm, Zoro listing 2026-11-25)
    as a box from p to q (axis-aligned); the 15 mm side lies along `wide`, the 10.4 mm side along the remaining axis."""
    ax = [i for i in range(3) if abs(p[i] - q[i]) > 1e-6][0]
    c = [(p[i] + q[i]) / 2 for i in range(3)]
    half = [0, 0, 0]
    half[ax] = abs(p[ax] - q[ax]) / 2
    wi = "xyz".index(wide)
    for i in range(3):
        if i != ax:
            half[i] = 7.5 if i == wi else 5.2
    return box(c[0] - half[0], c[0] + half[0], c[1] - half[1], c[1] + half[1], c[2] - half[2], c[2] + half[2])

def tie(p, r):
    """Cable tie around a bundle at p (2.5 mm wide band, shown as a ring)."""
    return cyl_z(p[0], p[1], p[2] - 1.25, p[2] + 1.25, r + 1.2) - cyl_z(p[0], p[1], p[2] - 2, p[2] + 2, r)

def tie_x(p, r):
    return cyl_between((p[0] - 1.25, p[1], p[2]), (p[0] + 1.25, p[1], p[2]), r + 1.2) - cyl_between((p[0] - 2, p[1], p[2]), (p[0] + 2, p[1], p[2]), r)

def tie_y(p, r):
    return cyl_between((p[0], p[1] - 1.25, p[2]), (p[0], p[1] + 1.25, p[2]), r + 1.2) - cyl_between((p[0], p[1] - 2, p[2]), (p[0], p[1] + 2, p[2]), r)

HARNESS = {}      # name -> dict(wires, awg, length_mm, from, to, notes) for the doc and BOM

def add(c, Zp1, SBX):
    """Add the v16 harness to concept c. Zp1 = module copper top (238.3), SBX = shunt x (70.7)."""
    def wire(name, pts, n, awg, frm, to, note=""):
        r = r_bundle(n, awg)
        c.add(f"sig_{name}", tube(pts, r), "sig")
        L = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))
        HARNESS[name] = dict(n=n, awg=awg, r=r, length_mm=round(L), frm=frm, to=to, note=note)
        return r

    # ---------------- 1. Tesla shunt J1 -> j_shunt (7 x 22 AWG) ----------------
    # J1: Molex Mini-Fit Jr 2 x 5 (tesla-shunt.md: 10-pin Mini-Fit, UNCONFIRMED) on the 8 mm overhang strip, +x side of the bar,
    # i.e. the side that faces the front board. Wires leave the plug straight up. The plug envelope covers the whole strip
    # length (21 mm of 25), so it holds for either end of the strip (the end is still UNCONFIRMED).
    zj = Zp1 + 3.2 + 2.0 + 5.0                    # bar top + PCB + header = 248.5 (tesla-shunt.md: top 7 mm above the copper)
    c.add("plug_shunt_j1", box(SBX + 16.1, SBX + 25.7, -38.25, -17.25, zj, zj + 13.0), "other")   # Mini-Fit Jr receptacle 2x5: 9.6 x 21 x 13
    p0 = (SBX + 20.9, -27.75, zj + 13.0)
    pb, pe = board_plug("j_shunt"); c.add("plug_j_shunt", pb)
    XBUS = 165.0                                  # 'plug-top run': wires reach their plugs along x 162-168 above the plug tops (z 303-310)
    wire("shunt", [p0, (p0[0], p0[1], 280.0), (p0[0], 7.0, 304.0), (p0[0] + 6, 7.0, 312.0), (150.0, 7.0, 312.0), (XBUS, 3.0, 310.0), (XBUS, pe[1], 306.0), pe], 7, "22",
         "Tesla shunt J1 (Mini-Fit Jr 2x5)", "j_shunt (Micro-Fit 3.0 2x4)", "5V, GND, NSS, SCK, MISO, MOSI, OC (J1 pins 1-7); pins 8-10 unused")

    # ---------------- 2. power taps -> j_pwr (3 x 18 AWG): B+ (line), LOAD+ (precharge / sense), GND (node A) ----------------
    pb, pe = board_plug("j_pwr"); c.add("plug_j_pwr", pb)
    # GND: ring under the node-A nut (the - flange + shunt bar joint, the cell side of the shunt: tesla-shunt.md sec 5)
    za = Zp1 + 3.2                                  # shunt bar top
    cu, bar, e = ring(SBX, -54.5, za, (1, 0), 6.4, 4.3)
    c.add("ring_gnd_nodeA", cu, "neg"); c.add("sig_gnd_barrel", bar, "sig")
    c.add("hw_nut_nodeA", stud_stack(SBX, -54.5, za + 0.8) - cyl_z(SBX, -54.5, za, za + 12, 4.0))
    wire("gnd", [e, (84.0, e[1], e[2]), (84.0, -54.5, 280.0), (84.0, 2.0, 280.0), (84.0, 2.0, 303.0), (90.0, 6.0, 313.5), (150.0, 6.0, 313.5), (XBUS - 2.5, 2.0, 309.0), (XBUS - 2.5, -3.0, 304.0), (pe[0] - 2.5, -3.0, pe[2])],
         1, "18", "node A nut (ring M8)", "j_pwr pin 3", "board ground = cell side of the shunt")
    # B+: ring under the Z-strap foot nut (in-bar = after the main fuse, before the contactor); fused at the source
    zf = Zp1 + 3.175
    cu, bar, e = ring(113.6, -4.3, zf, (-1, 0), 5.6, 3.3, L=16.0)                    # M6 ring (the strap-foot stud is M6 from v16.1)
    c.add("ring_bplus_strapfoot", cu, "pos"); c.add("sig_bplus_barrel", bar, "sig")
    f0 = (e[0], e[1], e[2] + 6.0); f1 = (e[0], e[1], e[2] + 45.6)
    c.add("fuse_inline_bplus", inline_fuse(f0, f1, wide="x"), "other")
    wire("bplus", [e, f0], 1, "18", "", "")
    wire("bplus2", [f1, (e[0], 6.0, 304.0), (e[0] + 6, 9.5, 313.0), (150.0, 9.5, 313.0), (XBUS, 2.0, 309.0), (pe[0], -1.0, 304.0), (pe[0], -1.0, pe[2])], 1, "18",
         "Z-strap foot stud (ring M6) + 2 A ATM inline fuse", "j_pwr pin 1", "board supply (2 A fuse on board too) and precharge source")
    # LOAD+: ring on the 2151's inverter-fuse stud, stacked on the inverter's 90 deg lug under the washer + nut (no new hole;
    # the stud already carries a ring terminal). Senses / precharges the load bus through the 50 A MRBF. Fused at the source.
    zl = 265.6 + 1.8                                     # fuse top + lug ring
    cu, bar, e = ring(131.1, 74.0, zl, (0, -1), 7.0, 4.3, L=12.0)
    c.add("ring_loadplus_2151", cu, "pos"); c.add("sig_loadplus_barrel", bar, "sig")
    # holder flat on the contactor top, along -y, under the S-run (ABYC E-11: within 7 in / 178 mm of the source; ~110 mm here)
    fz0, fz1 = (120.0, 44.0, 303.8), (120.0, 4.4, 303.8)
    c.add("fuse_inline_loadplus", inline_fuse(fz0, fz1, wide="x"), "other")
    wire("loadplus", [e, (131.1, 63.5, e[2]), (131.1, 63.5, 300.0), (120.0, 50.0, 303.8), fz0], 1, "18", "", "")
    wire("loadplus2", [fz1, (120.0, 2.0, 303.8), (124.0, 11.0, 314.5), (150.0, 11.0, 314.5), (XBUS + 2.5, 3.0, 310.0), (pe[0] + 2.5, -1.0, 305.0), (pe[0] + 2.5, -1.0, pe[2])], 1, "18",
         "2151 inverter-fuse stud (ring M8, on the lug) + 2 A ATM inline fuse", "j_pwr pin 2", "precharge target + load-bus sense (through the 50 A MRBF)")

    # ---------------- 3. contactor coil -> j_coil (2 x 20 AWG, the GV141BAX's own 38 cm flying leads, cut + crimped) ----------------
    # Lead exit (GV14 datasheet p.3, upright-mount top view, checked 2026-11-27): X1/X2 leave through notches in the CAP rim
    # (terminal end), on the side 90 deg from the A1-A2 axis, opposite the aux-lead notches. Inverted with A1(+) at -x, that is
    # the +y side, down at the copper. Leads rise along the +y face of the body, then over the top.
    pb, pe = board_plug("j_coil"); c.add("plug_j_coil", pb)
    # The rim there faces the 2151 (contactor body to y 59.85, 2151 base from y 64.0): the leads leave the notch, lie in that
    # 4.2 mm slot below the MRBFs (fuse bottoms at z 250.3) and run -x to x 89, past the 2151's end, then rise. ⚠️ slot height.
    zc = Zp1 + 3.7
    wire("coil", [(122.0, 61.9, zc), (89.0, 61.9, zc), (88.0, 62.0, 296.0), (100.0, 40.0, 312.0), (104.0, 14.0, 314.0), (XBUS, 14.0, 309.0), (pe[0], pe[1], 304.0), pe], 2, "20",
         "GV141BAX flying leads (red X1+, black X2-)", "j_coil", "coil B 12 V: 3.9 A pick-up 75 ms, 0.23 A hold (GV14 rev 28-Apr-2022)")

    # ---------------- 4. converter control -> j_conv (charger DF11 4 x 24 AWG + inverter CN301 2 x 24 AWG) ----------------
    pb, pe = board_plug("j_conv"); c.add("plug_j_conv", pb)
    c.add("plug_chg_df11", box(25.0, 33.0, -49.5, -36.5, 228.0, 239.5))          # Hirose DF11 receptacle (UNCONFIRMED pin count)
    c.add("plug_inv_cn301", box(6.0, 16.0, -23.5, -16.5, 294.5, 302.0))          # JST XHP-2 on CN301
    rj = r_bundle(6, "24")
    j = (50.0, -52.0, 300.0)                                                      # junction: both converter leads meet
    wire("chg_ctl", [(33.0, -43.0, 234.0), (40.0, -45.0, 226.0), (46.0, -47.0, 224.0), (50.0, -50.0, 232.0), (50.0, -52.0, 262.0), j], 4, "24",
         "charger DF11 (remote ON/OFF + CAN H/L)", "junction", "")
    wire("inv_ctl", [(16.0, -20.0, 298.0), (24.0, -26.0, 300.0), (40.0, -46.0, 300.0), j], 2, "24",
         "inverter CN301 (JST XH 2-pin: short = remote off)", "junction", "")
    wire("conv", [j, (58.0, -84.0, 290.0), (95.0, -86.5, 290.0), (155.0, -86.5, 292.0), (XBUS, -84.0, 303.0), (XBUS, pe[1], 305.0), pe], 6, "24", "junction", "j_conv (2x4)", "")
    c.add("tie_conv_a", tie_y((46.0, -47.0, 224.0), r_bundle(4, "24")))         # through the two slots in tray 1 at x 46

    # ---------------- 5. lid push-button -> j_btn (2 x 22 AWG, 250 mm service loop so the lid can be set beside the pack) ----------------
    pb, pe = board_plug("j_btn"); c.add("plug_j_btn", pb)
    zb = 288.1                                                                    # switch body bottom (tower15 pushbutton depth 30)
    wire("button", [(75.0, -58.0, zb), (75.0, -58.0, 284.0), (90.0, -84.0, 286.0), (152.0, -84.0, 288.0), (XBUS, -82.0, 300.0), (pe[0], pe[1], 300.0), pe], 2, "22",
         "lid push-button", "j_btn", "lid off: unplug j_btn first (loop lets the lid stand on its side beside the pack)")

    # ---------------- 6. NF-A14 fan -> j_fan (4 x 24 AWG, Noctua cable + NA-EC1 extension) ----------------
    pb, pe = board_plug("j_fan"); c.add("plug_j_fan", pb)
    f_exit = (t5.XR + 26.0, 62.0, 296.0)                                          # frame corner strut on the inside face
    wire("fan", [f_exit, (t5.XR + 34.0, 64.0, 287.0), (-150.0, 64.0, 285.6), (-20.0, 64.0, 285.6), (8.0, 64.0, 286.0), (50.0, 68.5, 287.0),
                 (60.0, 68.5, 300.0), (86.0, 68.5, 300.0), (91.0, 50.0, 302.0), (150.0, 50.0, 302.0), (pe[0], pe[1] + 2.0, 302.0), pe], 4, "24", "NF-A14 5V PWM 4-pin", "j_fan", "lies on tray 2 beside the inverter, tied through tray-2 slots")
    rf = r_bundle(4, "24")
    for x in (-150.0, -20.0):
        c.add(f"tie_fan_{int(-x)}", tie_x((x, 64.0, 285.6), rf))

    c.allow += [("ring_", "hw_carriage"), ("ring_", "hw_nut"), ("ring_gnd", "shunt_bar"), ("ring_bplus", "strap_main"), ("ring_loadplus", "bs2151_strap"),
                ("ring_loadplus", "hw_m10nut"), ("hw_nut_nodeA", "hw_carriage"), ("sig_", "ring_"), ("sig_", "fuse_inline"), ("sig_", "plug_"),
                ("plug_j_", "ctrl_j_"), ("sig_", "tie_"), ("sig_coax", "ctrl_esp32"), ("sig_coax", "antenna"), ("sig_coax", "ledboard_f"),
                ("plug_shunt_j1", "shunt_module"), ("plug_inv_cn301", "keepout_inv_dc_mirror"), ("sig_inv_ctl", "keepout_inv_dc_mirror"), ("ring_loadplus", "lug_inverter"), ("ring_loadplus", "hw_nut_inverter"), ("sig_loadplus_barrel", "lug_inverter"), ("plug_chg_df11", "term_chg_sig"), ("plug_inv_cn301", "term_inv_sig"), ("sig_", "sig_"), ("tie_conv", "tray1")]

    # ---------------- AC (mains, 3 x 16 AWG SJT-class each): v15 routes, dropped from v16 by the bay-prefix filter, restored ----------------
    cab = t5.cables()
    for k in ("ac_in", "ac_out"):
        c.add(f"sig_{k}", cab[k], "sig")
        HARNESS[k] = dict(n=3, awg="16", r=3.5, length_mm=0, frm={"ac_in": "lid IEC C14 inlet", "ac_out": "inverter CN500 (JST VH)"}[k],
                          to={"ac_in": "charger C14 via right-angle C13 (L-com ACPWRC-C13LR)", "ac_out": "lid NEMA 5-15 outlet"}[k], note="mains: own route at the rear, never bundled with the low-voltage leads")
    c.allow += [("sig_ac", "panel_"), ("sig_ac", "keepout_"), ("sig_ac", "term_")]
    c.allow += [("contactor_gv141bax", "sig_coil")]                # the coil leads leave the cap-rim notch (GV14 p.3)

    # ---------------- 7. antenna coax (ESP32-S3-WROOM-1U U.FL -> flex antenna above the board edge) ----------------
    xa = XB - 2.2
    c.add("sig_coax", tube([(xa, -77.0, 273.5), (xa, -77.0, 275.3), (xa, 18.5, 275.3), (xa, 18.5, 289.0), (t5.XL0 + 0.9, 21.0, 289.0)], 0.7), "sig")
    HARNESS["coax"] = dict(n=1, awg="1.13 mm coax", r=0.7, length_mm=110, frm="ESP32 U.FL", to="antenna U.FL", note="")
