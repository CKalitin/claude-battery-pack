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
    Zp1 = Zp0 + T                     # copper top = terminal face of contactor and SB175 busbar face
    zc = (Zp0 + Zp1) / 2
    # ---------- output connector ----------
    SBX, SBY = 70.7, 37.8
    sb, sbc, (sbn, sbp), z_bus = sb175_bbs(SBX, SBY, Zp1 + 89.8, axis="y")
    c.add("sb175_housing", sb); c.add("sb175_contact_neg", sbc[0], "neg"); c.add("sb175_contact_pos", sbc[1], "pos")
    c.notes.append(f"SB175 mating face z {Zp1 + 89.8:.1f} = {Zp1 + 89.8 - Z_LID_TOP:.1f} mm above the lid top (v15: 10.0)")
    for i, x0 in enumerate((SBX - 12.7 - 3.2, SBX + 12.7)):        # G10 cheeks bolted through the housing's two mounting holes
        c.add(f"g10_sb_cheek_{i}", box(x0, x0 + 3.2, SBY - 22, SBY + 22, Zp1, Zp1 + 52), "ins")
    # ---------- switch ----------
    CX, CY = 120.0, 41.2
    if variant == "gv14":
        ct, (t1, t2) = gv14_pcb(CX, CY, Zp1, axis="y", flip=True)
        c.add("contactor_gv14_pcb", ct)
    elif variant == "gv14up":
        # GV141BAX upright version mounted upside-down: studs (M8, ~12.7 long UNCONFIRMED) down through the bars,
        # nuts underneath (bench). Body 59.9 x 55.7, mounting flange 72.5 long at the top, unused. UNCONFIRMED outline.
        t1, t2 = (CX, CY - 13.35), (CX, CY + 13.35)
        ct = box(CX - 27.85, CX + 27.85, CY - 29.95, CY + 29.95, Zp1 + 2.0, Zp1 + 59.9)
        ct += box(CX - 27.85, CX + 27.85, CY - 36.25, CY + 36.25, Zp1 + 53.9, Zp1 + 59.9)
        for (x, y) in (t1, t2):
            ct += cyl_z(x, y, Zp1, Zp1 + 2.0, 8.0)                          # terminal boss on the bar
        c.add("contactor_gv141bax_inverted", ct)
        for i, (x, y) in enumerate((t1, t2)):
            c.add(f"nut_m8_{i}", cyl_z(x, y, Zp0 - 3.175 - 7.0, Zp0 - 3.175, 7.5))   # flange nut under the plate
    else:   # back-to-back FET board bridging the in-bar and the load bar
        t1, t2 = (CX, CY - 13.35), (CX, CY + 13.35)
        c.add("fet_board", box(CX - 30, CX + 30, CY - 28, CY + 28, Zp1, Zp1 + 1.6), "ins")
        c.add("fet_parts", box(CX - 26, CX + 26, CY - 8, CY + 8, Zp1 + 1.6, Zp1 + 8.0))
        c.add("fet_driver", box(CX - 26, CX - 10, CY + 12, CY + 24, Zp1 + 1.6, Zp1 + 4.0))
    # ---------- + path ----------
    # P4 collector -> vertical riser at the +x end -> flange at the module copper plane (in a plate notch)
    pc = pack_pos_collector()
    pc += box(138.0, 142.76, -46.0, -21.0, Z0, Zp1)                    # riser (x 138: >= 10 mm from the upper standoff)
    pc += box(136.0, 152.0, -46.0, -21.0, Zp0, Zp1)                     # flange, top flush with the module copper
    c.add("bus_pack_pos", pc, "pos")
    inb = box(136.0, 152.0, -9.0, t1[1] + 8.0, Zp0, Zp1) + box(t1[0] - 8.0, 152.0, t1[1] - 8.0, t1[1] + 8.0, Zp0, Zp1)
    c.add("bus_mod_in", inb, "pos")                                       # flat-cut L: no bends
    c.add("mrbf_main", mrbf_link((144.0, -33.5), (144.0, -1.0), Zp1), "pos")
    ld = box(SBX - 8.0, t2[0] + 8.0, t2[1] - 8.0, t2[1] + 8.0, Zp0, Zp1)  # load bar: T2 -> SB+ (straight)
    ld += box(SBX - 8.0, SBX + 8.0, sbp[1] - 8.0, t2[1] + 8.0, Zp0, Zp1)
    ld += box(78.0, 100.0, t2[1] + 8.0, 84.0, Zp0, Zp1)                  # branch tab for the converter fuses
    c.add("bus_mod_load", ld, "pos")
    c.add("mrbf_branch_dual", box(77.0, 101.0, 72.0, 92.0, Zp1, Zp1 + 20.0))   # Blue Sea 2151 dual MRBF block UNCONFIRMED size
    # ---------- - path ----------
    nb = pack_neg_band(80.0)
    nb += box(62.0, 80.0, -66.0, -61.24, Z0, Zp1)                       # riser in the band corridor
    nb += box(62.0, 80.0, -66.0, -33.5, Zp0, Zp1)                        # flange up to the shunt's node A
    c.add("bus_pack_neg", nb, "neg")
    sh_y1 = 14.0                                                          # shunt along +y, node B 15 mm from its end
    c.add("shunt_bar", box(SBX - 17.5, SBX + 17.5, sh_y1 - 83.5, sh_y1, Zp1, Zp1 + 3.2), "neg")
    c.add("shunt_module", box(SBX - 12.5, SBX + 12.5, sh_y1 - 63.0, sh_y1 - 20.0, Zp1 + 3.2, Zp1 + 10.2))
    tab = box(SBX - 8.0, SBX + 8.0, sh_y1 - 22.0, sbn[1] + 8.0, Zp0, Zp1)      # narrow - tab under the shunt's node-B end
    tab += box(SBX - 8.0, SBX + 20.0, sh_y1 - 22.0, sh_y1 - 6.0, Zp0, Zp1)       # converter - stud area
    c.add("bus_mod_neg", tab, "neg")
    # ---------- G10 plate (the 'PCB') + standoffs, tray 1 ----------
    pl = box(54.0, 150.0, -64.0, 88.0, Zp0 - 3.175, Zp0)
    pl -= box(133.0, 151.0, -48.0, -19.0, 200, 300)                       # notch for the + riser flange
    pl -= box(60.0, 82.0, -65.0, -31.5, 200, 300)                         # notch for the - riser flange
    c.add("g10_plate", pl, "ins")
    for i, (x, y) in enumerate(((58, -56), (146, -12), (58, 82), (146, 82), (100, -56))):
        c.add(f"standoff_{i}", cyl_z(x, y, Z_TRAY_TOP, Zp0 - 3.175, 4.0), "ins")
    c.add("tray1", tray1(cuts=((136.0, 164.0, -48.0, -19.0), (60.0, 82.0, -89.0, -59.0))), "ins")
    # ---------- allow-list ----------
    c.allow += TRAY_ALLOW + [("standoff", "tray1"), ("standoff", "g10_plate"), ("g10_plate", "bus_mod"), ("g10_plate", "shunt"),
                             ("bus_mod", "contactor"), ("nut_m8", "g10_plate"), ("nut_m8", "bus_mod"), ("bus_mod", "fet"), ("bus_mod", "sb175"), ("bus_mod", "mrbf"), ("bus_pack_pos", "mrbf_main"),
                             ("bus_mod_neg", "shunt"), ("bus_pack_neg", "shunt_bar"), ("shunt_module", "shunt_bar"), ("sb175_housing", "sb175_contact"),
                             ("g10_sb_cheek", "sb175_housing"), ("g10_sb_cheek", "g10_plate"), ("g10_sb_cheek", "bus_mod"), ("mrbf_branch", "bus_mod_load"),
                             ("sb175_housing", "lid"), ("bus_pack", "g10_top"), ("bus_pack", "flex_ccs"), ("bus_pack", "screws_term"),
                             ("bus_pack", "cell_"), ("bus_pack", "screws_tap"), ("bus_pack", "tray1"), ("fet_", "fet_"), ("sb175", "bus_mod"), ("contactor", "g10_plate"),
                             ("bus_pack_pos", "bus_mod_in")]
    # ---------- current paths (centre lines) and joint/bend counts ----------
    zcol = (Z0 + Z1) / 2
    c.paths["pos"] = [(134.0, -33.5, zcol), (140.4, -33.5, zcol), (140.4, -33.5, zc), (144.0, -33.5, zc), (144.0, -1.0, zc),
                      (144.0, t1[1], zc), (t1[0], t1[1], zc), (t2[0], t2[1], zc), (SBX, t2[1], zc), (SBX, sbp[1], zc)]
    c.paths["neg"] = neg_band_path(71.0, -63.6) + [(71.0, -63.6, zc), (71.0, sh_y1 - 68.5, zc), (71.0, sh_y1 - 15.0, zc),
                      (SBX, sbn[1], zc)]
    c.joints = {"pos (after cell collector)": "MRBF in, MRBF out, T1, T2, SB+ = 5", "neg (after band)": "shunt A, shunt B, SB- = 3"}
    c.bends = {"pos": "2 (riser) + 0 in the module (flat-cut L)", "neg": "2 (band riser) + 0 in the module"}
    c.notes += ["Module copper in one plane z 235.1-238.3; contactor/SB terminals face down onto it",
                "Module assembled upside-down on the bench; installs top-down; 2 bolts + MRBF join it to the pack",
                "MRBF bridges + riser and module: installed last = service disconnect",
                "Lid hole moves to the SB175 (x 58-83, y 10-66); v15 hole at x 89-116 must be re-cut"]
    c.labels = [("contactor_gv14_pcb", "Gigavac GV14 PCB-mount (terminals down)"), ("contactor_gv141", "Gigavac GV141BAX, upside-down"), ("fet_board", "FET switch board"),
                ("sb175_housing", "SB175, busbar contacts, facing up"), ("mrbf_main", "MRBF 250 A = service disconnect"),
                ("mrbf_branch", "Dual MRBF: charger, inverter"), ("shunt_module", "Tesla shunt (flat)"), ("g10_plate", "G10 module plate"),
                ("bus_pack_pos", "+ riser from cells 7-8"), ("bus_pack_neg", "- band + riser"), ("bus_mod_load", "+ load bar"),
                ("bus_mod_in", "+ in-bar"), ("bus_mod_neg", "- tab to SB175"), ("tray1", "G10 tray 1"), ("charger", "Charger"),
                ("g10_sb_cheek", "G10 cheeks (SB175 mount)"), ("path_pos", "+ current path"), ("path_neg", "- current path")]
    return c

if __name__ == "__main__":
    import json
    for v in sys.argv[1:] or ["gv14"]:
        c = build(v)
        r = c.check()
        c.export()
        print(json.dumps(r, indent=1))
