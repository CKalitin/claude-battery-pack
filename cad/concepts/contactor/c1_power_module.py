"""Concept C1: PCB-style power module.

One G10 plate (the 'PCB'). All module copper lies flat on its top face in ONE plane (z 235.1-238.3).
The contactor (Gigavac GV14 PCB-mount, M8 female terminals on its base) and the SB175 (180BBS busbar
contacts) stand on that copper with their terminals pointing DOWN, exactly as a PCB-mount contactor is
meant to be used. Bolts go up through plate + copper into the terminals: the module is built upside-down
on the bench (every bolt from above there), then drops in and joins the two pack risers with bolts from above.
The MRBF bridges the + riser and the module: it is the last part in and the service disconnect.
"""
import sys
from lib import *
from common import *

def build(variant="gv14"):
    c = Concept("c1_module_" + variant, "C1 PCB-style power module" + ({"fet": " (FET switch)", "gv14up": " (GV141BAX upside-down)", "gv14": " (GV14 PCB-mount)"}[variant]))
    Zp0 = 235.14                      # plate top = bottom of the copper plane
    T = 3.175                         # 1/8 in copper bars in the module: 25 x 3.2 = 79 mm2, 2.2 A/mm2 at 175 A
    Y2151 = 74.0                      # v16.1: was 76; the fuses (y <= 87.9) now clear the body's top facets (y 88.6 above z 300)
    Zp1 = Zp0 + T                     # copper top = terminal face of contactor and SB175 busbar face
    X5191, Y5191 = 135.0, -64.5        # v16.2: main-fuse M10 stud on the + flange (was 144, -33.5)
    zc = (Zp0 + Zp1) / 2
    # ---------- output connector ----------
    SBX, SBY = 70.7, 37.8
    sb, sbc, (sbn, sbp), z_bus = sb175_bbs(SBX, SBY, Zp1 + 89.8, axis="y")
    c.add("sb175_housing", sb); c.add("sb175_contact_neg", sbc[0], "neg"); c.add("sb175_contact_pos", sbc[1], "pos")
    c.notes.append(f"SB175 mating face z {Zp1 + 89.8:.1f} = {Zp1 + 89.8 - Z_LID_TOP:.1f} mm above the lid top (v15: 10.0)")
    for i, (x, y) in enumerate((sbn, sbp)):
        c.add(f"hw_stud_sb_{i}", cyl_z(x, y, Zp0 - 3.175 - 7.0, z_bus, 3.175))             # 180BBS 1/4-20 stud
        c.add(f"hw_locknut_sb_{i}", cyl_z(x, y, Zp0 - 3.175 - 5.6, Zp0 - 3.175, 6.4))     # 110G56 lock nut
    # carriage bolts (square neck in a square hole), heads under the copper; M10 for the MRBF blocks, M8 elsewhere
    for i, (x, y, r, rh, top) in enumerate(((X5191, Y5191, 5.0, 12.0, Zp1 + 15.0), (SBX, -54.5, 4.0, 10.0, Zp1 + 22.0),
                                            (113.6, -4.3, 3.0, 6.5, Zp1 + 3.175 + 11.0), (70.7, Y2151, 5.0, 12.5, Zp1 + 15.0))):
        c.add(f"hw_carriage_{i}", cyl_z(x, y, Zp0 - 4.5, top, r))
        c.add(f"hw_carriage_head_{i}", cyl_z(x, y, Zp0 - 4.5 - 5.6, Zp0 - 4.5 + 0.01, rh))
    for i, x0 in enumerate((SBX - 12.7 - 3.2, SBX + 12.7)):        # G10 cheeks bolted through the housing's two mounting holes
        c.add(f"g10_sb_cheek_{i}", box(x0, x0 + 3.2, SBY - 22, SBY + 22, Zp1, Zp1 + 52), "ins")
    # ---------- switch ----------
    CX, CY = 122.0, 32.0                 # turned 90 deg (terminals along x, flange along x): flange stops at y 59.9, so the 2151 fuses lift out
    if variant == "gv14":
        ct, (t1, t2) = gv14_pcb(CX, CY, Zp1, axis="x", flip=True)
        c.add("contactor_gv14_pcb", ct)
    elif variant == "gv14up":
        # GV141BAX upright version mounted upside-down: studs (M8, ~12.7 long UNCONFIRMED) down through the bars,
        # nuts underneath (bench). Body 59.9 x 55.7, mounting flange 72.5 long at the top, unused. UNCONFIRMED outline.
        t1, t2 = (CX - 13.35, CY), (CX + 13.35, CY)                      # t1 = line (-x, over the in-bar), t2 = load (+x)
        ct = box(CX - 29.95, CX + 29.95, CY - 27.85, CY + 27.85, Zp1 + 2.0, Zp1 + 59.9)
        ct += box(CX - 36.25, CX + 36.25, CY - 27.85, CY + 27.85, Zp1 + 53.9, Zp1 + 59.9)
        for (x, y) in (t1, t2):
            ct += cyl_z(x, y, Zp1, Zp1 + 2.0, 8.0)                          # terminal boss on the bar
        c.add("contactor_gv141bax_inverted", ct)
        for i, (x, y) in enumerate((t1, t2)):
            c.add(f"hw_stud_ct_{i}", cyl_z(x, y, Zp0 - 3.175 - 8.0, Zp1 + 2.0, 4.0))          # M8 stud of the contactor
            c.add(f"nut_m8_{i}", cyl_z(x, y, Zp0 - 3.175 - 6.5, Zp0 - 3.175, 7.3))            # M8 flange nut under the plate
    else:   # back-to-back FET board bridging the in-bar and the load bar
        t1, t2 = (CX - 13.35, CY), (CX + 13.35, CY)
        c.add("fet_board", box(CX - 30, CX + 30, CY - 28, CY + 28, Zp1, Zp1 + 1.6), "ins")
        c.add("fet_parts", box(CX - 26, CX + 26, CY - 8, CY + 8, Zp1 + 1.6, Zp1 + 8.0))
        c.add("fet_driver", box(CX - 26, CX - 10, CY + 12, CY + 24, Zp1 + 1.6, Zp1 + 4.0))
    # ---------- + path ----------
    # P4 collector -> vertical riser at the +x end -> flange at the module copper plane (in a plate notch)
    # v16.2: ONE bend-legal 1/8 in part. The riser is a 26 mm tab off the collector's -y edge, bent up, and the flange
    # bends back out to -y (a Z, not a C: SCS U-channel rule base >= 2 x flange fails for any C here, base 31 mm).
    pc = pack_pos_collector()
    pc += zbend_x(122.0, 148.0, -46.0, -1, Z1, Zp0, -77.0)             # riser + flange = 5191 seat, top flush with the module copper
    c.add("bus_pack_pos", pc, "pos")
    inb = box(106.6, 120.6, -17.0, t1[1] + 8.0, Zp0, Zp1)               # straight column: strap foot -> T1 (x >= 106.6: 10.4 mm to the shunt board)
    c.add("bus_mod_in", inb, "pos")                                       # flat-cut L: no bends
    # main fuse: Blue Sea 5191 on the M10 stud in the + flange, pointing -x; MRBF 250 A on it. Output is the fuse TOP,
    # so a Z-strap (1/8 in copper, 22 wide, 2 bends) brings it back down to the in-bar. Strap = last part in = service disconnect.
    mp, mst, mzt = bs_block("5191", X5191, Y5191, Zp1, d=(0, 1), prefix="bs5191")   # v16.2: points +y, back over the collector
    for n, (sh, r) in mp.items():
        c.add(n, sh, r)
    c.add("hw_m10nut_main", cyl_z(X5191, Y5191, Zp1 + 2.5, Zp1 + 10.5, 9.25) - cyl_z(X5191, Y5191, Zp1, Zp1 + 12, 5.0))
    sx, sy = mst[0]; fx = 113.6                                          # fuse stud; strap foot centre over the in-bar
    zs1 = mzt + 3.175
    st = box(sx - 9.5, sx + 9.5, sy - 11.0, -31.0, mzt, zs1)               # pad on the fuse top, runs +y (flat-cut L in plan)
    st += box(fx - 7.0, sx + 9.5, -31.0, -13.8, mzt, zs1)                  # runs -x above the flange and the 5191 tab
    st += box(fx - 7.0, fx + 7.0, -17.0, -13.8, Zp1, zs1) + box(fx - 7.0, fx + 7.0, -17.0, -2.0, Zp1, Zp1 + 3.175)   # leg + foot (v16.1: leg 3 mm further -y, M6 stud at y -4.3 so washer + socket clear the leg and the contactor)
    st -= cyl_z(sx, sy, mzt - 1, zs1 + 1, 4.3) + cyl_z(fx, -4.3, Zp1 - 1, Zp1 + 4.2, 3.3)
    c.add("strap_main", st, "pos")
    c.add("hw_nut_main", stud_stack(sx, sy, zs1) - cyl_z(sx, sy, zs1 - 1, zs1 + 10, 4.0))
    c.add("hw_nut_strapfoot", stud_stack(fx, -4.3 , Zp1 + 3.175 + 0.8, r_w=6.0, r_n=5.75, h_n=5.2) - cyl_z(fx, -4.3, Zp1, Zp1 + 14, 3.0))   # M6: DIN 125 washer 12 mm + 10 AF nut, on the B+ ring
    ld = box(t2[0] - 8.0, t2[0] + 8.0, t2[1] - 8.0, 50.0, Zp0, Zp1)        # T2 pad (x >= 127.35: 9.75 mm to the in-bar)
    ld += box(SBX - 8.0, t2[0] + 8.0, 50.0, 86.0, Zp0, Zp1)                # wide bar y 50-86 (10 mm above the in-bar), under the 2151
    ld += box(SBX - 8.0, 88.7, 43.2, 50.0, Zp0, Zp1)                       # SB+ pad (y >= 43.2: 10.8 mm to the - tab)
    c.add("bus_mod_load", ld, "pos")
    # Blue Sea 2151 dual MRBF on the M10 stud in the branch, along +x by the +y wall; fuses land beside the contactor
    bp, bst, bzt = bs_block("2151", 70.7, Y2151, Zp1, d=(1, 0), prefix="bs2151")
    for n, (sh, r) in bp.items():
        c.add(n, sh, r)
    c.add("hw_m10nut_2151", cyl_z(70.7, Y2151, Zp1 + 2.5, Zp1 + 7.5, 9.25) - cyl_z(70.7, Y2151, Zp1, Zp1 + 12, 5.0))   # v16.1: M10 thin nut (DIN 439, 5 mm) + lock washer: the SB175 housing overhangs at z 248.5
    for (x, y), d, nm, rc, route in zip(bst, ((-1, 0), (1, 0)), ("charger", "inverter"), (3.4, 3.0),   # 8 AWG charger; 10 AWG inverter (PP45 max wire per Anderson 1327)
                                        # to the converter DC terminals (tower15.converter_terminals; charger TB x 23, inverter PP45 x 4)
                                        (lambda p: [p, (p[0], p[1], 298.0), (45.0, p[1], 298.0), (30.0, 5.0, 280.0), (27.5, 9.0, 251.0)],   # V+ on the -y side of the block (NPB drawing: 'V+ V-' left to right, seen from outside)
                                         lambda p: [p, (p[0], p[1], 296.0), (p[0], 55.0, 309.0), (90.0, 55.0, 309.0), (86.0, 71.0, 309.0), (56.0, 70.5, 309.0), (30.0, 40.0, 304.0), (9.0, 37.3, 299.3)])):   # v16.1: never over a 2151 fuse or nut (service)   # PP45 TB1 at y +25..+41
        lug, top = lug90(x, y, bzt, d=d)
        c.add(f"lug_{nm}", lug - cyl_z(x, y, bzt - 1, bzt + 3, 4.0), "pos")
        zn = bzt + 1.8 + (0.8 if nm == "inverter" and variant == "gv14up" else 0.0)      # + LOAD+ sense ring on the inverter stud
        c.add(f"hw_nut_{nm}", stud_stack(x, y, zn) - cyl_z(x, y, bzt, bzt + 12, 4.0))
        c.add(f"cable_{nm}", tube(route(top), rc))
    c.add("cap_2151", bs_cap("2151", 70.7, Y2151, Zp1, d=(1, 0)))
    # Shunt node B: the shunt is a PURCHASED part (Tesla 1016792-00-C) - no new holes. Its own hole 15 mm from the end
    # (tesla-shunt.md sec 2; thread/size UNKNOWN, modelled M8) takes ONE bolt: up through the - tab (our part, square hole)
    # and the shunt's node-B hole. Both converter - lugs stack on top of the bar on that bolt: converter current
    # enters the bar on the node-B side, so the shunt still measures it.
    nbx, nby = SBX, 14.0 - 15.0                                         # sh_y1 (set below) - 15
    zr = Zp1 + 3.2
    c.add("hw_carriage_nodeB", cyl_z(nbx, nby, Zp0 - 4.5, zr + 3.6 + 12.0, 4.0))
    c.add("hw_carriage_head_nodeB", cyl_z(nbx, nby, Zp0 - 4.5 - 5.6, Zp0 - 4.5 + 0.01, 10.0))
    for k, (nm, d, off, rc, route) in enumerate((
            ("charger", (-1, 0), 17.0, 3.4, lambda p: [p, (p[0], p[1], 266.0), (40.0, 22.0, 254.0), (27.5, 17.0, 251.0)]),
            ("inverter", (1, 0), 14.0, 3.0, lambda p: [p, (p[0], p[1], 272.0), (p[0], -13.0, 272.0), (50.0, -13.0, 274.0), (20.0, -1.0, 300.0), (12.0, 26.0, 300.0), (9.0, 29.4, 299.3)]))):   # v16.1: off 14 + this route keep the node-B socket clear
        zk = zr + 1.8 * k                                                   # charger ring on the bar, inverter ring on top of it
        lug, top = lug90(nbx, nby, zk, d=d, off=off, h=24.0 - 1.8 * k)
        c.add(f"lug_neg_{nm}", lug - cyl_z(nbx, nby, zk - 1, zk + 3, 4.0), "neg")
        c.add(f"cable_neg_{nm}", tube(route(top), rc))
    # shunt connector (tesla-shunt.md sec 2): on the 8 mm overhang strip, at one end of the module, top 7 mm above the copper,
    # wires straight up; keep-out = connector footprint x 35 mm above its top. End chosen: -y (away from node B) UNCONFIRMED.
    # v16.1: the keep-out is replaced by the modelled Mini-Fit Jr plug + 7-wire bundle (harness.py)
    c.add("hw_nut_neg_nodeB", stud_stack(nbx, nby, zr + 3.6) - cyl_z(nbx, nby, zr, zr + 14, 4.0))
    # ---------- - path ----------
    nb = pack_neg_band(83.0) - box(58.0, 84.0, -72.0, -65.0, Z0 - 1, Z1 + 1)   # v16.2: band edge cut back to y -72 under the riser
    nb += zbend_x(58.0, 83.0, -72.0, +1, Z1, Zp0, -33.5)               # bend-legal Z, all 1/8 in, 25 wide (2.7 A/mm2 at 215 A); edge at -72 puts
                                                                         # the node-A hole edge 8.8 mm from the bend line (die 0.63 in: 8 mm half-width)
    c.add("bus_pack_neg", nb, "neg")
    sh_y1 = 14.0                                                          # shunt along +y, node B 15 mm from its end
    c.add("shunt_bar", box(SBX - 17.5, SBX + 17.5, sh_y1 - 83.5, sh_y1, Zp1, Zp1 + 3.2), "neg")
    # sensing board crosswise on the bar between the two bolts (owner photo 2026-11-24): flush with the -x edge,
    # connector end overhangs ~8 mm past the +x edge (scaled from the photo, UNCONFIRMED). Role neg: its copper is at shunt potential.
    ym = sh_y1 - 41.75
    c.add("shunt_module", box(SBX - 17.5, SBX - 17.5 + 43.0, ym - 12.5, ym + 12.5, Zp1 + 3.2, Zp1 + 10.2), "neg")
    tab = box(SBX - 8.0, SBX + 8.0, sh_y1 - 22.0, sbn[1] + 8.0, Zp0, Zp1)      # narrow - tab under the shunt's node-B end
    tab += box(SBX - 8.0, SBX + 20.0, sh_y1 - 22.0, sh_y1 - 6.0, Zp0, Zp1)       # converter - stud area
    c.add("bus_mod_neg", tab, "neg")
    # ---------- G10 plate (the 'PCB') + standoffs, tray 1 ----------
    pl = box(54.0, 150.0, -64.0, 88.0, Zp0 - 3.175, Zp0)
    pl -= box(120.0, 151.0, -80.0, -44.0, 200, 300)                       # notch for the + riser flange (v16.2: open to the -y edge)
    pl -= box(53.0, 85.0, -65.0, -31.5, 200, 300)                         # notch for the - riser flange (v16.2: 25 wide, open to -x)
    c.add("g10_plate", pl, "ins")
    for i, (x, y) in enumerate(((58, -20), (146, -12), (58, 60), (146, 82), (100, -56))):
        c.add(f"standoff_{i}", cyl_z(x, y, Z_TRAY_TOP, Zp0 - 3.175, 4.0), "ins")
    c.add("tray1", tray1(cuts=((120.0, 151.0, -80.0, -44.0), (56.0, 85.0, -89.0, -59.0), (44.5, 47.5, -55.0, -50.0), (44.5, 47.5, -44.0, -39.0))), "ins")   # + 2 tie slots for the converter control lead
    # ---------- allow-list ----------
    c.allow += TRAY_ALLOW + [("standoff", "tray1"), ("standoff", "g10_plate"), ("g10_plate", "bus_mod"), ("g10_plate", "shunt"),
                             ("bus_mod", "contactor"), ("nut_m8", "g10_plate"), ("nut_m8", "bus_mod"), ("bus_mod", "fet"), ("bus_mod", "sb175"), ("bus_mod", "mrbf"), ("bus_pack_pos", "mrbf_main"),
                             ("bus_mod_neg", "shunt"), ("bus_pack_neg", "shunt_bar"), ("shunt_module", "shunt_bar"), ("sb175_housing", "sb175_contact"),
                             ("g10_sb_cheek", "sb175_housing"), ("g10_sb_cheek", "g10_plate"), ("g10_sb_cheek", "bus_mod"), ("mrbf_branch", "bus_mod_load"),
                             ("sb175_housing", "lid"), ("bus_pack", "g10_top"), ("bus_pack", "flex_ccs"), ("bus_pack", "screws_term"),
                             ("bus_pack", "cell_"), ("bus_pack", "screws_tap"), ("bus_pack", "tray1"), ("fet_", "fet_"), ("sb175", "bus_mod"), ("contactor", "g10_plate"),
                             ("bus_pack_pos", "bus_mod_in"), ("bs2151_", "bs2151_"), ("bs5191_", "bs5191_"), ("bs2151_strap", "bus_mod_load"),
                             ("bs2151_body", "bus_mod_load"), ("bs5191_strap", "bus_pack_pos"), ("bs5191_body", "bus_pack_pos"),
                             ("hw_m10nut", "bs"), ("hw_carriage", "bus_"), ("hw_carriage", "g10_plate"), ("hw_carriage", "bs"),
                             ("hw_carriage", "hw_m10nut"), ("hw_carriage", "strap_main"), ("hw_carriage", "hw_nut_strapfoot"),
                             ("hw_carriage", "shunt_bar"), ("hw_stud", "bus_mod"), ("hw_stud", "g10_plate"), ("hw_stud", "contactor"),
                             ("hw_stud", "sb175"), ("hw_stud", "nut_m8"), ("hw_locknut", "g10_plate"), ("hw_locknut", "hw_stud"),
                             ("hw_nut", "bs"), ("hw_nut", "lug_"), ("hw_nut", "strap_main"), ("lug_", "bs2151"),
                             ("strap_main", "bs5191"), ("strap_main", "bus_mod_in"), ("cable_", "lug_"), ("cable_", "keepout_"), ("lug_neg", "shunt_bar"), ("lug_neg_charger", "keepout_chg_dc"), ("hw_carriage_nodeB", "shunt_bar"), ("hw_carriage_nodeB", "bus_mod_neg"), ("hw_carriage_nodeB", "g10_plate"), ("hw_carriage", "lug_"), ("hw_carriage_nodeB", "hw_nut"), ("lug_neg_charger", "lug_neg_inverter"), ("hw_nut_neg", "lug_neg"), ("cable_", "term_"), ("cap_", ""), ("hw_carriage", "hw_carriage")]
    # ---------- current paths (centre lines) and joint/bend counts ----------
    zcol = (Z0 + Z1) / 2
    c.paths["pos"] = [(100.0, -33.5, zcol), (126.4, -33.5, zcol), (126.4, -33.5, zc), (144.0, -33.5, zc), (144.0, -33.5, Zp1 + 1.25),
                      (144.0, -54.25, Zp1 + 1.25), (144.0, -54.25, Zp1 + 9.75), (144.0, sy + 8.0, Zp1 + 9.75), (144.0, sy + 8.0, mzt + 1.6),
                      (sx, -21.0, mzt + 1.6), (fx, -21.0, mzt + 1.6), (fx, -15.4, mzt + 1.6), (fx, -15.4, zc), (fx, -4.3, zc), (fx, t1[1], zc), (t1[0], t1[1], zc), (t2[0], t2[1], zc),
                      (t2[0], 58.0, zc), (SBX, 58.0, zc), (SBX, sbp[1], zc)]
    c.paths["neg"] = neg_band_path(71.0, -63.6) + [(71.0, -63.6, zc), (71.0, sh_y1 - 68.5, zc), (71.0, sh_y1 - 15.0, zc),
                      (SBX, sbn[1], zc)]
    c.joints = {"pos (after cell collector)": "5191 tab (M10), fuse bottom, fuse top, strap foot, T1, T2, SB+ = 7", "neg (after band)": "shunt A, shunt B, SB- = 3"}
    c.bends = {"pos": "2 (riser) + 2 (Z-strap) + 0 in the plane bars", "neg": "2 (band riser) + 0 in the module"}
    c.notes += ["Module copper in one plane z 235.1-238.3; contactor/SB terminals face down onto it",
                "Module assembled upside-down on the bench; installs top-down; 2 bolts + MRBF join it to the pack",
                "Main MRBF on a 5191 on the + flange; Z-strap fuse top -> in-bar is installed last = service disconnect",
                "Lid hole moves to the SB175 (x 58-83, y 10-66); v15 hole at x 89-116 must be re-cut"]
    c.labels = [("contactor_gv14_pcb", "Gigavac GV14 PCB-mount (terminals down)"), ("contactor_gv141", "Gigavac GV141BAX, upside-down"), ("hw_stud_ct", "Contactor M8 stud"), ("nut_m8", "M8 nut under the plate"), ("hw_stud_sb", "SB175 contact stud 1/4-20"), ("hw_locknut", "Lock nut under the plate"), ("hw_carriage_head", "Carriage bolt head"), ("hw_carriage_", "M8 carriage bolt"), ("fet_board", "FET switch board"),
                ("sb175_housing", "SB175, busbar contacts, facing up"), ("bs5191_fuse", "MRBF 250 A on 5191 block"), ("strap_main", "Z-strap = service disconnect"),
                ("bs2151_fuse_0", "MRBF 30 A (charger)"), ("bs2151_fuse_1", "MRBF 50 A (inverter)"), ("bs2151_body", "Blue Sea 2151"), ("lug_", "90° lug"), ("cable_charger", "to charger"), ("cable_inverter", "to inverter"), ("cable_neg_charger", "charger − lead"), ("cable_neg_inverter", "inverter − lead"), ("lug_neg", "− lugs on the shunt (node B side)"), ("shunt_module", "Tesla shunt (flat)"), ("g10_plate", "G10 module plate"),
                ("bus_pack_pos", "+ riser from cells 7-8"), ("bus_pack_neg", "- band + riser"), ("bus_mod_load", "+ load bar"),
                ("bus_mod_in", "+ in-bar"), ("bus_mod_neg", "- tab to SB175"), ("tray1", "G10 tray 1"), ("charger", "Charger"),
                ("g10_sb_cheek", "G10 cheeks (SB175 mount)"), ("path_pos", "+ current path"), ("path_neg", "- current path")]
    if variant == "gv14up":
        import harness
        harness.add(c, Zp1, SBX)
    c.lift = {n: 44.5 - 11.0 for n in c.parts if n.startswith(("bs2151_fuse_", "bs5191_fuse_")) and n.endswith("_body")}
    return c

def lift_check(c):
    """Fuse removal: lid, cables, lugs, nuts and the Z-strap off; slide each fuse housing straight up by the stud length."""
    from build123d import Pos
    C = ctx(tuple(p for p in CHASSIS + OBSTACLES if p not in ("lid", "panel_", "screws_lid", "pem_")))
    gone = ("lug_", "hw_nut", "cable_", "strap_main", "cap_", "hw_m10nut", "path_", "ring_", "sig_loadplus", "fuse_inline_loadplus", "sig_bplus")
    out = {}
    for n, dz in c.lift.items():
        pre = n.split("_fuse_")[0]; me = n.replace("_body", "")
        sweep = c.parts[n]
        for k in range(1, 8):
            sweep = sweep + Pos(0, 0, dz * k / 7) * c.parts[n]
        hits = []
        for m, sh in list(c.parts.items()) + list(C.items()):
            if m.startswith(gone) or m.startswith(me) or m.startswith(pre + "_stud") or m.startswith(pre + "_body") or m == n:
                continue
            x = sweep & sh
            if x is not None and x.volume > 0.5:
                hits.append((m, round(x.volume, 1)))
        out[n] = hits
    return out

if __name__ == "__main__":
    import json
    for v in sys.argv[1:] or ["gv14"]:
        c = build(v)
        r = c.check()
        r["fuse_lift_out"] = lift_check(c)
        c.export()
        print(json.dumps(r, indent=1))
