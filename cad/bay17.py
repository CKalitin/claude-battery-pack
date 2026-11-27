"""v17 power-bay strip (-y, open to the lid), on one flat copper plane on a G10 bay plate (C1 convention, contactor-mounting.md):
GV141BAX inverted and SB175 busbar contacts face down onto 1/8 in copper; heads of carriage bolts under the plate/flange.
Rear -> front: Tesla shunt (node A on the pack- riser flange, node B on the - rail), SB175 (- rail -> + rail, contacts
along x), Blue Sea 2151 (30 A charger, 50 A inverter) on the + rail, GV141BAX at the front (A1 = line at -y, A2 = load
at +y), Z-strap (service disconnect) from the 250 A MRBF on the 5191 down to the in-bar.
+ path: pack+ riser flange -> 5191 tab -> MRBF 250 A -> strap_main -> bus_mod_in -> GV14 A1 -> A2 -> bus_mod_pos (rail)
-> 2151 / SB175+.  - path: cells -> pack- riser flange -> shunt A -> shunt B -> bus_mod_neg -> SB175-.
Deviations from converter_packing.py opt_D(): SB175 long axis along x (the packing box 55.6 x 44), centre y -47;
shunt bar x -149..-65.5 (7.5 mm to the rear plate); 2151 at y -45; GV14 as packed (126, -49)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
import lib
from lib import cyl_x, zbend_x, bs_block, stud_stack
from build123d import Polygon, extrude, Pos, Rot, Plane, Compound
import tower17 as t
from tower17 import box, cyl_z, hexz, Z_P0, Z_P1, Z_COP, Z_BB, CU, G125, Z_D1, Z_DECK1, SB_C

lib.BS["5191"]["L"] = 61.9                       # Eaton Bussmann CF bar drawing (docs/v16-decisions.md); lib default 60.9

Z_PL = Z_P0 - G125                                # bay plate underside (= 25.0 mm standoff top)

def zbend_y(y0, y1, x_edge, s, z_low_top, z_high_bot, x_end):
    """zbend_x mirrored in the plane x = y: bend lines along y, riser in a y-z plane, flange offset along x."""
    return zbend_x(y0, y1, x_edge, s, z_low_top, z_high_bot, x_end).mirror(Plane(origin=(0, 0, 0), z_dir=(1, -1, 0)))

# ---------------- positions ----------------
SH = (-149.0, -65.5, -76.5, -41.5)               # Tesla shunt bar x0 x1 y0 y1 (tesla-shunt.md: 83.5 x 35 x 3.2, UNCONFIRMED)
NODE_A, NODE_B = (-134.0, -59.0), (-80.5, -59.0)
Z_SHT = Z_P1 + CU                                 # shunt bar top
SBN, SBP = (SB_C[0] - 13.4, SB_C[1]), (SB_C[0] + 13.4, SB_C[1])      # SB175 busbar contacts, pitch 26.8 (UNCONFIRMED)
X2151, Y2151 = 11.0, -45.0                        # 2151 M10 hole; fuses at x 45.2 (charger) and 71.4 (inverter)
ST_CHG, ST_INV = (X2151 + 34.2, Y2151), (X2151 + 60.4, Y2151)
CT = (126.0, -49.05)
T1, T2 = (126.0, CT[1] - 13.35), (126.0, CT[1] + 13.35)              # A1 line (-y), A2 load (+y); coil leads exit the -x face
X5191, Y5191 = 123.0, -2.0                        # 5191 M10 hole on the pack+ flange, block along +y
ST_MAIN = (X5191, Y5191 + 34.4)
ZF = Z_P1 + 11.0 + 16.3                           # MRBF top face (strap / lugs sit here)
FOOT = (143.0, -10.0)                             # strap foot M6 on the in-bar
BAY_SO = t.BAY_SO_XY

def pack_straps():
    zt = Z_COP
    pos = box(t.cell_x[6] - t.BB_W / 2, 140.5, -46.0, -21.0, Z_BB, zt)
    pos += box(t.cell_x[6] - t.BB_W / 2, 103.0, -21.0, 8.0, Z_BB, zt)                # tongue to the riser
    pos += zbend_y(-12.0, 8.0, 103.0, +1, zt, Z_P0, 130.0)                           # riser x 104.3..107.4, flange = 5191 seat
    for k in (6, 7):
        pos -= cyl_z(t.cell_x[k], t.cell_pos_y(6), Z_BB - 1, zt + 1, 3.3)
    pos -= cyl_z(*t.tap_pts()[4], Z_BB - 1, zt + 1, 1.25)
    pos -= cyl_z(X5191, Y5191, Z_P0 - 1, Z_P1 + 1, 4.9)
    neg = box(-140.5, t.cell_x[1] + t.BB_W / 2, -46.0, -21.0, Z_BB, zt)
    neg += box(-115.0, -88.0, -71.0, -46.0, Z_BB, zt)                                # arm over the cell edge to the riser
    neg += zbend_y(-71.0, -48.5, -115.0, -1, zt, Z_P0, -147.5)                       # riser x -119.4..-116.3, flange = shunt node A seat
    for k in (0, 1):
        neg -= cyl_z(t.cell_x[k], -t.cell_pos_y(0), Z_BB - 1, zt + 1, 3.3)
    neg -= cyl_z(*t.tap_pts()[0], Z_BB - 1, zt + 1, 1.25)
    neg -= cyl_z(*NODE_A, Z_P0 - 1, Z_P1 + 1, 4.3)
    return pos, neg

def bay_copper():
    p = {}
    nr = box(-92.0, -70.0, -73.0, -45.0, Z_P0, Z_P1) + box(-92.0, -39.0, -58.0, -39.0, Z_P0, Z_P1)       # 19 mm: 2.9 A/mm2 at 175 A
    for (x, y), r in ((NODE_B, 4.3), (SBN, 3.3)):
        nr -= cyl_z(x, y, Z_P0 - 1, Z_P1 + 1, r)
    p["bus_mod_neg"] = nr
    pr = box(-26.5, 112.0, -55.0, -35.0, Z_P0, Z_P1) + box(104.0, 132.0, -45.0, -27.0, Z_P0, Z_P1)
    for (x, y), r in ((SBP, 3.3), ((X2151, Y2151), 4.9), (T2, 4.3)):
        pr -= cyl_z(x, y, Z_P0 - 1, Z_P1 + 1, r)
    p["bus_mod_pos"] = pr
    ib = box(136.5, 152.0, -66.0, 6.0, Z_P0, Z_P1) + box(118.0, 152.0, -72.0, -55.0, Z_P0, Z_P1)
    for (x, y), r in ((T1, 4.3), (FOOT, 3.2)):
        ib -= cyl_z(x, y, Z_P0 - 1, Z_P1 + 1, r)
    p["bus_mod_in"] = ib
    z1 = ZF + CU
    st = box(114.0, 151.5, 24.0, 41.0, ZF, z1) + box(136.5, 151.5, 2.7, 41.0, ZF, z1)
    st += box(136.5, 151.5, 2.7, 2.7 + CU, Z_P1, z1) + box(136.5, 151.5, -18.0, 2.7 + CU, Z_P1, Z_P1 + CU)
    st -= cyl_z(*ST_MAIN, ZF - 1, z1 + 1, 4.3) + cyl_z(*FOOT, Z_P1 - 1, Z_P1 + CU + 1, 3.2)
    p["strap_main"] = st
    return p

def bay_plate():
    pl = box(-150.0, 152.0, -t.FY, -20.0, Z_PL, Z_P0) + box(136.0, 152.0, -20.0, 7.0, Z_PL, Z_P0)
    pl -= box(-151.0, -111.0, -73.0, -46.0, Z_PL - 1, Z_P0 + 1)                      # pack- riser / flange / node A head
    pl -= cyl_z(*t.D2_POST_XY[2], Z_PL - 1, Z_P0 + 1, 5.3)                               # passage for the deck-2 post
    holes = [(NODE_B, 4.3), (SBN, 3.3), (SBP, 3.3), ((X2151, Y2151), 4.9), (T1, 4.3), (T2, 4.3), (FOOT, 3.2)]
    for (x, y), r in holes:
        pl -= cyl_z(x, y, Z_PL - 1, Z_P0 + 1, r)
    for (x, y) in BAY_SO:
        pl -= cyl_z(x, y, Z_PL - 1, Z_P0 + 1, 2.2)
    return pl

def standoffs():
    so = Compound([hexz(x, y, Z_D1, Z_PL, 7.0) - cyl_z(x, y, Z_D1 - 1, Z_PL + 1, 1.95) for (x, y) in BAY_SO])
    top = Compound([cyl_z(x, y, Z_P0, Z_P0 + 2.2, 3.8) + cyl_z(x, y, Z_P0 - 10.0, Z_P0, 1.95) for (x, y) in BAY_SO])
    bot = Compound([cyl_z(x, y, Z_DECK1 - 2.4, Z_DECK1, 3.8) + cyl_z(x, y, Z_DECK1, Z_D1 + 8.0, 1.95) for (x, y) in BAY_SO])
    return so, top, bot

def carriage(x, y, r, rh, z_under, z_top):
    """Carriage bolt: head under the copper or plate (underside z_under), shank up to z_top."""
    return cyl_z(x, y, z_under - 4.2, z_under - 0.01, rh) + cyl_z(x, y, z_under - 0.05, z_top, r)

def shunt():
    x0, x1, y0, y1 = SH
    bar = box(x0, x1, y0, y1, Z_P1, Z_SHT)
    for (x, y) in (NODE_A, NODE_B):
        bar -= cyl_z(x, y, Z_P1 - 1, Z_SHT + 1, 4.3)
    xm = (x0 + x1) / 2
    pcb = box(xm - 12.5, xm + 12.5, y0, y1 + 8.0, Z_SHT, Z_SHT + 7.0)               # 25 along the bar, 8 overhang +y, 7 tall
    return {"shunt_bar": bar, "shunt_pcb": pcb}

def sb175():
    p = {}
    cx, cy = SB_C
    zb, zt = Z_P1 + 10.2, Z_P1 + 89.8
    h = box(cx - 27.8, cx + 27.8, cy - 12.7, cy + 12.7, zb, zt)
    for s in (-1, 1):
        h -= box(cx + s * 13.4 - 10.0, cx + s * 13.4 + 10.0, cy - 9.0, cy + 9.0, zt - 20.0, zt + 1)
    for dx in (-16.0, 16.0):
        h -= lib.Solid.make_cylinder(2.1, 34.0, Plane(origin=(cx + dx, cy - 17.0, Z_P1 + 25.0), z_dir=(0, 1, 0)))
    p["sb175_housing"] = h
    for n, (x, y) in (("neg", SBN), ("pos", SBP)):
        p[f"sb175_contact_{n}"] = box(x - 6.35, x + 6.35, y - 6.35, y + 6.35, Z_P1, zb)
        p[f"hw_sb_stud_{n}"] = cyl_z(x, y, Z_PL - 7.0, Z_P1, 3.175)
        p[f"hw_sb_nut_{n}"] = cyl_z(x, y, Z_PL - 5.6, Z_PL, 6.4) - cyl_z(x, y, Z_PL - 8, Z_PL + 1, 3.175)
    for i, s in enumerate((-1, 1)):
        c = box(cx - 22.0, cx + 22.0, cy + s * 12.7, cy + s * 15.9, Z_P0, Z_P1 + 52.0)
        for dx in (-16.0, 16.0):
            c -= lib.Solid.make_cylinder(2.1, 40.0, Plane(origin=(cx + dx, cy - 20.0, Z_P1 + 25.0), z_dir=(0, 1, 0)))
        p[f"g10_sb_cheek_{i}"] = c
    sc = []
    for dx in (-16.0, 16.0):
        sc.append(lib.Solid.make_cylinder(1.95, 31.8, Plane(origin=(cx + dx, cy - 15.9, Z_P1 + 25.0), z_dir=(0, 1, 0)))
                  + lib.Solid.make_cylinder(3.6, 2.2, Plane(origin=(cx + dx, cy - 18.1, Z_P1 + 25.0), z_dir=(0, 1, 0)))
                  + lib.Solid.make_cylinder(3.5, 3.0, Plane(origin=(cx + dx, cy + 15.9, Z_P1 + 25.0), z_dir=(0, 1, 0))))
    p["screws_sb_cheek"] = Compound(sc)
    return p

def contactor():
    """Gigavac GV141BAX (upright version) inverted: round body 59.9, 55.7 to the stud seat, flange 80.5 x holes 68.3
    turned diagonal at the top. Flange width and coil-notch height UNCONFIRMED."""
    cx, cy = CT
    b = cyl_z(cx, cy, Z_P1 + 2.0, Z_P1 + 55.7, 29.95)
    fl = Pos(cx, cy, Z_P1 + 49.7) * (Rot(0, 0, 45) * (box(-35.25, 35.25, -5.0, 5.0, 0, 6.0) + cyl_z(-35.25, 0, 0, 6.0, 5.0) + cyl_z(35.25, 0, 0, 6.0, 5.0)))
    for s in (-1, 1):
        fl -= cyl_z(cx + s * 34.15 * math.cos(math.pi / 4), cy + s * 34.15 * math.sin(math.pi / 4), Z_P1 + 49, Z_P1 + 57, 2.75)
    b += fl
    for (x, y) in (T1, T2):
        b += cyl_z(x, y, Z_P1, Z_P1 + 2.0, 8.0)
        b -= cyl_z(x, y, Z_P1 - 1, Z_P1 + 12.0, 4.0)
    p = {"contactor_gv141bax": b}
    for i, (x, y) in enumerate((T1, T2)):
        p[f"hw_ct_stud_{i}"] = cyl_z(x, y, Z_PL - 8.0, Z_P1 + 12.0, 4.0)                 # M8 stud
        p[f"nut_ct_{i}"] = cyl_z(x, y, Z_PL - 6.5, Z_PL, 7.3) - cyl_z(x, y, Z_PL - 8, Z_PL + 1, 4.0)
    return p

def fuse_blocks():
    p = {}
    parts, _, zf = bs_block("5191", X5191, Y5191, Z_P1, d=(0, 1), prefix="bs5191")
    assert abs(zf - ZF) < 1e-6
    p.update({k: v for k, (v, r) in parts.items()})
    parts, studs, _ = bs_block("2151", X2151, Y2151, Z_P1, d=(1, 0), prefix="bs2151")
    assert abs(studs[0][0] - ST_CHG[0]) < 1e-6 and abs(studs[1][0] - ST_INV[0]) < 1e-6
    p.update({k: v for k, (v, r) in parts.items()})
    # M10 studs of the two blocks: carriage bolts from under the copper
    p["bolt_5191"] = carriage(X5191, Y5191, 4.75, 11.0, Z_P0, Z_P1 + 15.0)
    p["nut_5191_m10"] = cyl_z(X5191, Y5191, Z_P1 + 2.5, Z_P1 + 10.5, 9.25) - cyl_z(X5191, Y5191, Z_P1, Z_P1 + 12, 4.75)
    p["bolt_2151"] = carriage(X2151, Y2151, 4.75, 12.0, Z_PL, Z_P1 + 14.0)
    p["nut_2151_m10"] = cyl_z(X2151, Y2151, Z_P1 + 2.5, Z_P1 + 7.5, 9.25) - cyl_z(X2151, Y2151, Z_P1, Z_P1 + 12, 4.75)   # thin M10 (DIN 439)
    return p

def joints():
    """Bolted copper joints made in the pack (nuts from above). Rings and lugs of the harness sit under these nuts."""
    p = {}
    zb = Z_SHT
    p["bolt_nodeA"] = carriage(*NODE_A, 4.0, 10.0, Z_P0, zb + 0.8 + 1.6 + 6.5 + 3.0)
    p["nut_nodeA"] = stud_stack(*NODE_A, zb + 0.8) - cyl_z(*NODE_A, zb, zb + 14, 4.0)
    p["bolt_nodeB"] = carriage(*NODE_B, 4.0, 10.0, Z_PL, zb + 3.6 + 1.6 + 6.5 + 3.0)
    p["nut_nodeB"] = stud_stack(*NODE_B, zb + 3.6) - cyl_z(*NODE_B, zb, zb + 16, 4.0)
    zf = Z_P1 + CU
    p["bolt_foot"] = carriage(*FOOT, 3.0, 8.0, Z_PL, zf + 0.8 + 1.6 + 5.2 + 2.0)
    p["nut_foot"] = stud_stack(*FOOT, zf + 0.8, r_w=6.0, r_n=5.75, h_n=5.2) - cyl_z(*FOOT, zf, zf + 14, 3.0)
    z1 = ZF + CU
    p["nut_strap_top"] = stud_stack(*ST_MAIN, z1) - cyl_z(*ST_MAIN, z1 - 1, z1 + 10, 4.0)
    p["nut_2151_chg"] = stud_stack(*ST_CHG, ZF + 1.8) - cyl_z(*ST_CHG, ZF, ZF + 14, 4.0)
    p["nut_2151_inv"] = stud_stack(*ST_INV, ZF + 2.6) - cyl_z(*ST_INV, ZF, ZF + 14, 4.0)
    return p

def build():
    p = {}
    pos, neg = pack_straps()
    p["bus_pack_pos"], p["bus_pack_neg"] = pos, neg
    p.update(bay_copper())
    p["g10_bay"] = bay_plate()
    p["bay_standoffs"], p["screws_bay_top"], p["screws_bay_bot"] = standoffs()
    p.update(shunt())
    p.update(sb175())
    p.update(contactor())
    p.update(fuse_blocks())
    p.update(joints())
    return p
