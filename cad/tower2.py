"""Tower A v3 assembly: 400 W NTS-400P inverter + NPB-450 charger + single front control board.
Units mm. x = length (front plate / control end at +x), y = width, z = up. Body bottom at z = 0.

Stack:  cells module (as v2) -> tray 1 (5052, z 200) carrying the charger (rear) and control board (front)
        -> tray 2 on posts carrying the inverter (above the charger) -> lid with panel connectors (front).
Front plate = LED matrix display + charge pipe.  Rear plate = open hole grid = vent.
"""
import math
import packmodel as pm

# ---- vertical budget (set BEFORE importing tower, which derives H from pm.SHELL_H) ----
Z_TRAY1 = pm.z_cell_top + 0.125 * 25.4 + 9.0   # tray 1 underside: cell top + G10 top plate + 9 mm upper standoff
T_TRAY = 1.6
Z_T1TOP = Z_TRAY1 + T_TRAY
CHG = (205.0, 135.0, 55.0)       # MEAN WELL NPB-450-24  L x W x H
INV = (186.0, 100.5, 34.0)       # MEAN WELL NTS-400P-124 (datasheet: 186 x 100.5 x 34)
Z_TRAY2 = Z_T1TOP + CHG[2] + 1.8 # tray 2 underside (clears charger)
Z_T2TOP = Z_TRAY2 + T_TRAY
H_BODY = Z_T2TOP + INV[2] + 3.4  # lid outer top
pm.SHELL_H = H_BODY - pm.T_SHEET
pm.z_pwr = Z_TRAY1               # module standoffs now carry tray 1
pm.EP_H = pm.z_cell_top - 10.0 - pm.z_cell   # end plate top 10 mm below cell top -> standard 10 mm lower standoff
pm.z_ep_top = pm.z_cell + pm.EP_H

import tower as tw
from build123d import *

tw.GRID_ZB = 53.0                # matrix moved up toward the electronics decks
tw.PITCH = 124.5 / 16            # 7.78125 mm: NF-A14 holes (124.5) = 16 pitches, so a centred fan's screws sit on nodes
tw.GRID_Y0 = -(tw.GRID_COLS - 1) / 2 * tw.PITCH
tw.HOLE_D = 4.8                  # >= plate thickness (SCS rule); 2.98 mm web
tw.CSK = False                   # button heads: plain clearance holes, no countersinks (SCS countersink edge rule)
tw.NOTCH = 10.6                  # LED board / diffuser notches around tabs (neighbour hole edge is 5.38 mm from a node)
tw.L_IN = 310.0                  # +20 mm for the rear 140 mm fan (was 290)
tw.X_IN = tw.L_IN / 2
DX = 10.0                        # shell is shifted -DX relative to the internals: all extra length goes to the rear
X_REAR_IN = -(tw.X_IN + DX)      # rear plate inner face in internal coords (-165)
FAN = (140.0, 25.0)              # Noctua NF-A14 PWM: 140 x 140 x 25, hole spacing 124.5
FAN_HOLE = 124.5 / 2             # NF-A14 primary hole pattern = 8 pitches
FAN_YZ = (0.0, 53.0 + 21 * 124.5 / 16)   # centred on y = 0 and on grid row 21 (z 216.4); holes on rows 13 and 29
BT = 0.0                         # no bracket: fan bolts straight through the rear plate
REAR_ROWS = 30                   # rear grid: same 21 columns and pitch as the front, rows up to z 278.7
C = (Align.CENTER, Align.CENTER, Align.MIN)
H, W, T = tw.H, tw.W, tw.T

def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=C)

def cyl_z(x, y, z0, z1, r):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=C)

# ---------------- positions ----------------
CHG_X0 = -136.0; CHG_X1 = CHG_X0 + CHG[0]              # -136 .. 69
INV_X0 = -136.0; INV_X1 = INV_X0 + INV[0]              # -136 .. 50
CB_X0, CB_X1, CB_W = 78.0, 138.0, 150.0                # control board footprint (60 x 150)
CH_X = 73.5                                             # 9 mm cable channel between charger (x<=69) and board
Z_CB = Z_T1TOP + 3.4                                    # control board underside
CB_T = 1.6
CB_TOP = Z_CB + CB_T
POS_RISER = (pm.POS_X + 9.5, pm.Y_LAST)                 # pack+ riser x,y
RET_Y = 55.0                                            # pack- return bar centreline (y)
RET_RISER_X = 128.0

# lid connectors: name: (x, y, sx, sy, depth)  depth = below lid underside
CONNS = {
    "outlet_nema515": (80.0, -45.0, 38.0, 30.0, 30.0),
    "inlet_iec_c14": (86.0, 40.0, 27.0, 20.0, 25.0),
    "dc_sb50": (124.0, -48.0, 28.0, 36.0, 42.0),
    "can_m12": (124.0, 40.0, 16.0, 16.0, 20.0),
}

# ---------------- trays & supports ----------------
def tray1():
    L0, L1 = -pm.STACK_L / 2, pm.STACK_L / 2
    t = box(L0, L1, -80, 80, Z_TRAY1, Z_T1TOP)
    for s in (-1, 1):                                    # stiffening flanges bent down
        t += box(L0, L1, s * 80 - (0 if s > 0 else 1.6) - (1.6 if s > 0 else 0) + (1.6 if s < 0 else 0), s * 80 + (0 if s > 0 else 0), Z_TRAY1 - 15, Z_TRAY1) if False else \
             box(L0, L1, (78.4 if s > 0 else -80), (80 if s > 0 else -78.4), Z_TRAY1 - 15, Z_TRAY1)
    t -= box(115, 136, 18, 72, Z_TRAY1 - 1, Z_T1TOP + 1)          # riser pass-through
    t -= box(92, 110, -16, 16, Z_TRAY1 - 1, Z_T1TOP + 1)           # sense-flex tail pass-through
    for (x, y) in pm.PCB_SO_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.2)
    return t

def mica_under_tray():
    m = box(-pm.STACK_L / 2 + 2, pm.STACK_L / 2 - 2, -76, 76, Z_TRAY1 - 0.6, Z_TRAY1 - 0.1)
    m -= box(113, 138, 16, 74, Z_TRAY1 - 2, Z_TRAY1 + 1)
    m -= box(90, 112, -18, 18, Z_TRAY1 - 2, Z_TRAY1 + 1)
    for (x, y) in pm.PCB_SO_XY:
        m -= cyl_z(x, y, Z_TRAY1 - 2, Z_TRAY1 + 1, 4.0)
    for x in (CHG_X0 + 15, CHG_X1 - 15):               # charger screw heads
        for y in (-CHG[1] / 2 + 15, CHG[1] / 2 - 15):
            m -= cyl_z(x, y, Z_TRAY1 - 2, Z_TRAY1 + 1, 4.5)
    return m

INV_POST_XY = [(x, s * 73.5) for x in (-128.0, 42.0) for s in (-1, 1)]
CB_SO_XY = [(x, s * 68.0) for x in (CB_X0 + 5, CB_X1 - 5) for s in (-1, 1)]

def tray2():
    t = box(INV_X0 - 1, INV_X1 + 4, -79, 79, Z_TRAY2, Z_T2TOP)
    for (x, y) in INV_POST_XY:
        t -= cyl_z(x, y, Z_TRAY2 - 1, Z_T2TOP + 1, 2.2)
    return t

def posts():
    return Compound([cyl_z(x, y, Z_T1TOP, Z_TRAY2, 4.0) for (x, y) in INV_POST_XY])

def cb_standoffs():
    return Compound([cyl_z(x, y, Z_T1TOP, Z_CB, 3.0) for (x, y) in CB_SO_XY])

def screw_head(x, y, z, r=3.6, h=2.6, shank=8.0, down=True):
    head = Pos(x, y, z) * Cylinder(r, h, align=C)
    sh = Pos(x, y, z - shank) * Cylinder(r * 0.52, shank, align=C) if down else Pos(x, y, z + h) * Cylinder(r * 0.52, shank, align=C)
    return head + sh

def tray_screws():
    out = [screw_head(x, y, Z_T1TOP) for (x, y) in pm.PCB_SO_XY]                       # tray1 -> module standoffs
    out += [screw_head(x, y, Z_T2TOP) for (x, y) in INV_POST_XY]                       # tray2 -> posts
    out += [screw_head(x, y, CB_TOP, r=2.8, h=2.0, shank=5) for (x, y) in CB_SO_XY]    # control board -> standoffs
    # charger & inverter fixed from below through their trays (4 each, M4)
    # charger: M4 into its base (foot-pad holes; positions TBC from drawing)
    for x in (CHG_X0 + 15, CHG_X1 - 15):
        for y in (-CHG[1] / 2 + 15, CHG[1] / 2 - 15):
            out.append(Pos(x, y, Z_TRAY1 - 2.6) * Cylinder(3.6, 2.6, align=C) + Pos(x, y, Z_TRAY1) * Cylinder(1.9, T_TRAY + 6, align=C))
    # inverter: M3 on its datasheet pattern 174.6 x 88.6
    xc = (INV_X0 + INV_X1) / 2
    for x in (xc - 87.3, xc + 87.3):
        for y in (-44.3, 44.3):
            out.append(Pos(x, y, Z_TRAY2 - 2.0) * Cylinder(2.8, 2.0, align=C) + Pos(x, y, Z_TRAY2) * Cylinder(1.45, T_TRAY + 5, align=C))
    return Compound(out)

# ---------------- rear fan (intake) ----------------
def fan():
    x0 = X_REAR_IN + BT
    y, z = FAN_YZ
    f = Pos(x0 + FAN[1] / 2, y, z) * Box(FAN[1], FAN[0], FAN[0])
    f -= Pos(x0 + FAN[1] / 2, y, z) * Rot(0, 90, 0) * Cylinder(67.5, FAN[1] + 1)
    f += Pos(x0 + FAN[1] / 2, y, z) * Rot(0, 90, 0) * Cylinder(20, FAN[1] - 1)        # hub
    for a in range(7):                                                                 # blades (flat approx)
        f += Pos(x0 + FAN[1] / 2, y, z) * Rot(a * 360 / 7, 0, 0) * Pos(0, 0, 44) * Rot(0, 0, 25) * Box(3, 18, 47)
    for (yy, zz) in fan_screw_yz():
        f -= Pos(x0 + FAN[1] / 2, yy, zz) * Rot(0, 90, 0) * Cylinder(2.25, FAN[1] + 1)
        f -= Pos(x0 + FAN[1] / 2, yy, zz) * Box(FAN[1] - 8, 11, 11)          # open corner between the two 4 mm flanges
    return f

def fan_screw_yz():
    return [(FAN_YZ[0] + sy * FAN_HOLE, FAN_YZ[1] + sz * FAN_HOLE) for sy in (-1, 1) for sz in (-1, 1)]


def button_screw(y, z, sign, shank, nut_at=None):
    """ISO 7380 M4 button head, hex socket, black. Head on the plate's outer face. sign: +1 front, -1 rear (shell coords)."""
    xf = tw.X_IN + tw.PT
    head = Pos(xf, y, z) * Rot(0, 90, 0) * Cylinder(3.8, 2.2, align=C)
    try:
        head = fillet(head.edges().sort_by(Axis.X)[-1:], 1.4)
    except Exception:
        pass
    head -= Pos(xf + 0.7, y, z) * Rot(0, 90, 0) * extrude(RegularPolygon(1.44, 6), 1.6)     # 2.5 mm hex socket
    shank_ = Pos(xf, y, z) * Rot(0, -90, 0) * Cylinder(1.95, shank, align=C)
    s_ = head + shank_
    if nut_at is not None:
        s_ += Pos(nut_at, y, z) * Rot(0, -90, 0) * (Cylinder(3.6, 3.2, align=C) - Cylinder(2.0, 3.2, align=C))
    return s_ if sign > 0 else s_.mirror(Plane.YZ)

def plate_screws(sign):
    return Compound([button_screw(*tw.grid_yz(i, j), sign, 10.0) for (i, j) in tw.SCREW_IJ])

def fan_screws_rear():
    """4 more of the same button heads through the rear plate and the fan's front flange, nut behind the flange."""
    return Compound([button_screw(y, z, -1, 12.0, nut_at=tw.X_IN - 4.0) for (y, z) in fan_screw_yz()])

def rear_holes():
    """Rear plate: one uniform 21 x 30 grid, same columns and pitch as the front. 11 nodes carry screws instead of holes."""
    skip = {(round(y, 3), round(z, 3)) for (y, z) in [tw.grid_yz(i, j) for (i, j) in tw.SCREW_IJ] + fan_screw_yz()}
    pts = []
    for k in range(REAR_ROWS):
        for j in range(tw.GRID_COLS):
            y, z = tw.GRID_Y0 + j * tw.PITCH, tw.GRID_ZB + k * tw.PITCH
            if (round(y, 3), round(z, 3)) not in skip:
                pts.append((y, z))
    return pts

def rear_screws():
    """Same black M4 flat heads as the front; longer shank (plate + bracket + tab + nut)."""
    out = []
    csk_h = (tw.CSK_D - tw.SCREW_CLR) / 2
    xf = tw.X_IN + tw.PT
    for (i, j) in tw.SCREW_IJ:
        y, z = tw.grid_yz(i, j)
        head = Pos(xf - csk_h, y, z) * Rot(0, 90, 0) * Cone(2.0, tw.CSK_D / 2 - 0.05, csk_h, align=C)
        head -= Pos(xf - 1.2, y, z) * Rot(0, 90, 0) * Cylinder(1.25, 1.3, align=C)
        shank = Pos(xf - csk_h, y, z) * Rot(0, -90, 0) * Cylinder(1.95, 11.0, align=C)
        out.append((head + shank).mirror(Plane.YZ))
    return Compound(out)

# ---------------- boxes & boards ----------------
def charger():
    b = box(CHG_X0, CHG_X1, -CHG[1] / 2, CHG[1] / 2, Z_T1TOP, Z_T1TOP + CHG[2])
    b -= box(CHG_X0 - 1, CHG_X0 + 2, -25, 25, Z_T1TOP + 10, Z_T1TOP + 45)   # fan grille (rear)
    return b

def inverter():
    b = box(INV_X0, INV_X1, -INV[1] / 2, INV[1] / 2, Z_T2TOP, Z_T2TOP + INV[2])
    b -= box(INV_X0 - 1, INV_X0 + 2, -20, 20, Z_T2TOP + 6, Z_T2TOP + 26)
    return b

def control_board():
    pcb = box(CB_X0, CB_X1, -CB_W / 2, CB_W / 2, Z_CB, CB_TOP)
    for (x, y) in CB_SO_XY:
        pcb -= cyl_z(x, y, Z_CB - 1, CB_TOP + 1, 1.7)
    comps = {
        "terminals": box(78.5, 82, -60, 40, CB_TOP, CB_TOP + 8),      # screw terminal strip for cables
        "contactor": box(98, 138, -22.5, 22.5, CB_TOP, CB_TOP + 45),
        "fuse": box(83, 97, 22, 62, CB_TOP, CB_TOP + 25),
        "shunt": box(83, 97, -62, -22, CB_TOP, CB_TOP + 10),
        "precharge": box(99, 117, 28, 44, CB_TOP, CB_TOP + 16),
        "afe_bq76952": box(120, 130, 28, 38, CB_TOP, CB_TOP + 1.2),
        "esp32": box(115, 132, -64, -46, CB_TOP, CB_TOP + 3.2),
        "led_conn": box(133, 138, 52, 64, CB_TOP, CB_TOP + 6),
        "buck_12v": box(100, 112, 47, 57, CB_TOP, CB_TOP + 4),            # 24 V -> 12 V for the fan
        "fan_conn": box(100, 108, 61, 67, CB_TOP, CB_TOP + 6),            # 4-pin PWM header
        "ccs_conn": box(95, 107, -6, 6, Z_CB - 3, Z_CB),
    }
    return pcb, comps

def risers():
    """pack+ riser at the front, and the pack- return bar running the module top to the front."""
    zb = pm.z_bb + pm.BB_T
    out = {}
    out["pack_pos_riser"] = box(POS_RISER[0] - 1.5, POS_RISER[0] + 1.5, POS_RISER[1] - 10, POS_RISER[1] + 10, zb, Z_CB)
    xr0 = pm.NEG_X - 8
    bar = box(xr0, RET_RISER_X + 1.5, RET_Y - 10, RET_Y + 10, pm.z_bb, pm.z_bb + 3)      # along module top
    bar += box(xr0, xr0 + 16, pm.TERM_OFF - 8, RET_Y + 10, zb, zb + 3)                  # strap onto pack- lug
    bar += box(RET_RISER_X - 1.5, RET_RISER_X + 1.5, RET_Y - 10, RET_Y + 10, pm.z_bb + 3, Z_CB)
    out["pack_neg_return"] = bar
    return out

def lid_connectors():
    out = {}
    for n, (x, y, sx, sy, d) in CONNS.items():
        body = box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, H - T - d, H + 6)
        flange = box(x - sx / 2 - 5, x + sx / 2 + 5, y - sy / 2 - 3, y + sy / 2 + 3, H, H + 2)
        out[n] = body + flange
    return out

def lid_connector_screws():
    out = []
    for n, (x, y, sx, sy, d) in CONNS.items():
        for s in (-1, 1):
            out.append(Pos(x + s * (sx / 2 + 2.5), y, H + 2) * Cylinder(2.2, 1.4, align=C) +
                       Pos(x + s * (sx / 2 + 2.5), y, H - 6) * Cylinder(1.25, 8, align=C))
    return Compound(out)

def busbar_screws():
    out = []
    zt = pm.z_bb + pm.BB_T
    for x in pm.cell_x:
        for y in (-pm.TERM_OFF, pm.TERM_OFF):
            out.append(Pos(x, y, zt) * Cylinder(3.5, 2.8, align=C) + Pos(x, y, zt - 8) * Cylinder(1.95, 8, align=C))
    return Compound(out)

# ---------------- wiring ----------------
def cable(points, r):
    segs = []
    for a, b in zip(points[:-1], points[1:]):
        va, vb = Vector(*a), Vector(*b)
        d = vb - va
        L = d.length
        if L < 1e-6:
            continue
        segs.append(Solid.make_cylinder(r, L, Plane(origin=va, z_dir=d)))
    for p in points[1:-1]:
        segs.append(Pos(*p) * Sphere(r))
    out = segs[0]
    for s in segs[1:]:
        out = out + s
    return out

def cables():
    zc = Z_T1TOP + 20
    o_x, o_y, *_ = CONNS["outlet_nema515"]; i_x, i_y, *_ = CONNS["inlet_iec_c14"]
    d_x, d_y, _, _, d_d = CONNS["dc_sb50"]; c_x, c_y, _, _, c_d = CONNS["can_m12"]
    zt2 = Z_T2TOP + INV[2] / 2
    tb = CB_TOP + 6                                     # terminal strip height
    return {
        "ac_out": cable([(INV_X1, -30, zt2), (62, -30, zt2), (62, o_y, zt2), (o_x, o_y, H - T - 30)], 3.5),
        "ac_in": cable([(i_x, i_y, H - T - 25), (CH_X, i_y, H - T - 25), (CH_X, 45, zc + 15), (CHG_X1, 45, zc + 15)], 3.5),
        "chg_dc_pos": cable([(CHG_X1, -40, zc), (CH_X, -40, zc), (CH_X, -40, tb), (79, -40, tb)], 2.6),
        "chg_dc_neg": cable([(CHG_X1, -52, zc), (CH_X, -52, zc), (CH_X, -52, tb), (79, -52, tb)], 2.6),
        "inv_dc_pos": cable([(INV_X1, 10, zt2), (CH_X, 10, zt2), (CH_X, 10, tb), (79, 10, tb)], 3.0),
        "inv_dc_neg": cable([(INV_X1, 24, zt2), (CH_X, 24, zt2), (CH_X, 24, tb), (79, 24, tb)], 3.0),
        "dc_out": cable([(d_x, d_y, H - T - d_d), (d_x, d_y, 232), (d_x, -30, 232), (CH_X + 4, -30, 232), (CH_X + 4, -30, tb), (79, -28, tb)], 3.0),
        "can": cable([(c_x, c_y, H - T - c_d), (c_x, c_y, CB_TOP + 20), (126, 47, CB_TOP + 4)], 1.8),
        "led_front": cable([(136, 58, CB_TOP + 3), (140.3, 58, CB_TOP + 3), (140.3, 58, CB_TOP + 14)], 1.5),
        "ccs_tail": cable([(100, 0, pm.z_ccs + 0.3), (100, 0, Z_CB - 3)], 1.0),
        "fan": cable([(X_REAR_IN + FAN[1] - 1, 62, 158), (X_REAR_IN + FAN[1] + 4, 87, 158), (104, 87, 158),
                      (104, 87, CB_TOP + 14), (104, 64, CB_TOP + 14), (104, 64, CB_TOP + 6)], 1.5),
    }

# ---------------- cell retention (no printed carrier) ----------------
G10_FLOOR_T = 0.187 * 25.4       # 4.75 mm G10 floor: supports cells + end plates, insulates from the U floor
G10_FRAME_T = 0.125 * 25.4       # 3.18 mm G10 frame: bottom x/y locator around the stack footprint
G10_TOP_T = 0.125 * 25.4         # 3.18 mm G10 top locator: terminal holes fix every cell top in x/y
NUT_W, NUT_H = 7.0, 3.2          # M4 square nut (DIN 562)
FLOOR_Y = 72.5                   # floor stays on the flat of the U (bend radius starts at |y| = 73)

def tslot(x, y, z_edge, inward):
    """Laser-cut T-slot from a plate edge: screw slot + captive square-nut pocket. inward = +1 (from bottom) / -1 (from top)."""
    zc = lambda a, b: (z_edge + inward * a, z_edge + inward * b)
    z0, z1 = sorted(zc(-1, 15))
    cut = box(x - 5, x + 5, y - 2.25, y + 2.25, z0, z1)
    n0, n1 = sorted(zc(7.0, 7.0 + NUT_H + 0.2))
    cut += box(x - 5, x + 5, y - NUT_W / 2 - 0.15, y + NUT_W / 2 + 0.15, n0, n1)
    nut = box(x - NUT_W / 2, x + NUT_W / 2, y - NUT_W / 2, y + NUT_W / 2, n0 + 0.1, n1 - 0.1)
    nut -= cyl_z(x, y, n0 - 1, n1 + 1, 2.0)
    return cut, nut

def endplates_tslot():
    """Module end plates: edge-tapped holes replaced by laser-cut T-slots (SendCutSend can't tap into a plate edge)."""
    eps, nuts = [], []
    for x in pm.ep_x:
        p = box(x - pm.EP_T / 2, x + pm.EP_T / 2, -pm.EP_W / 2, pm.EP_W / 2, pm.z_cell, pm.z_ep_top)
        for y in (-pm.ROD_Y, pm.ROD_Y):
            for z in pm.ROD_ZS:
                p -= Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(pm.ROD_D / 2 + 0.25, pm.EP_T + 1)
        for (hx, hy) in pm.HOLD_XY:
            if abs(hx - x) < 1:
                c, n = tslot(x, hy, pm.z_cell, +1); p -= c; nuts.append(n)
        for (sx, sy) in pm.PCB_SO_XY:
            if abs(sx - x) < 1:
                c, n = tslot(x, sy, pm.z_ep_top, -1); p -= c; nuts.append(n)
        eps.append(p)
    return Compound(eps), Compound(nuts)

def standoff_studs():
    """M4 male end of the lower M-F standoffs, threaded down into the top square nuts."""
    return Compound([cyl_z(x, y, pm.z_ep_top - 10.5, pm.z_ep_top, 1.95) for (x, y) in pm.PCB_SO_XY])

def standoffs_split():
    """Two M4 M-F hex standoffs per corner clamp the G10 top plate: lower 10 mm (end plate -> plate), upper 9 mm (plate -> tray 1)."""
    zt = pm.z_cell_top + G10_TOP_T
    lower = Compound([cyl_z(x, y, pm.z_ep_top, pm.z_cell_top, 3.5) for (x, y) in pm.PCB_SO_XY])
    upper = Compound([cyl_z(x, y, zt, Z_TRAY1, 3.5) + cyl_z(x, y, pm.z_cell_top - 6.0, zt, 1.95) for (x, y) in pm.PCB_SO_XY])
    return lower, upper

def g10_floor():
    f = box(-pm.STACK_L / 2 - 0.5, pm.STACK_L / 2 + 0.5, -FLOOR_Y, FLOOR_Y, pm.z_floor, pm.z_floor + G10_FLOOR_T)
    for (x, y) in pm.HOLD_XY:
        f -= cyl_z(x, y, pm.z_floor - 1, pm.z_floor + G10_FLOOR_T + 1, 2.25)
    return f

def g10_frame():
    z0 = pm.z_floor + G10_FLOOR_T
    xo, yo = pm.STACK_L / 2 + 6.0, pm.EP_W / 2 + 6.0
    f = box(-xo, xo, -yo, yo, z0, z0 + G10_FRAME_T)
    xi = pm.STACK_L / 2 - pm.EP_T                                    # end plate inner faces
    f -= box(-xi, xi, -(pm.CELL_W / 2 + 0.3), pm.CELL_W / 2 + 0.3, z0 - 1, z0 + G10_FRAME_T + 1)          # cell stack window
    for sx in (-1, 1):                                               # end plate windows (wider)
        a, b = sorted((sx * (xi - 0.3), sx * (pm.STACK_L / 2 + 0.3)))
        f -= box(a, b, -(pm.EP_W / 2 + 0.3), pm.EP_W / 2 + 0.3, z0 - 1, z0 + G10_FRAME_T + 1)
    return f

def g10_top():
    z0 = pm.z_cell_top
    t = box(-pm.STACK_L / 2 - 1.0, pm.STACK_L / 2 + 1.0, -76.5, 76.5, z0, z0 + G10_TOP_T)
    for x in pm.cell_x:
        for y in (-pm.TERM_OFF, pm.TERM_OFF):
            t -= cyl_z(x, y, z0 - 1, z0 + G10_TOP_T + 1, pm.TERM_D / 2 + 0.3)
        t -= box(x - 4, x + 4, -9, 9, z0 - 1, z0 + G10_TOP_T + 1)        # keep each cell's vent clear
    for (x, y) in pm.PCB_SO_XY:
        t -= cyl_z(x, y, z0 - 1, z0 + G10_TOP_T + 1, 2.2)        # stud clearance only: plate is clamped between standoffs
    return t

# ---------------- vendor-pressed PEM hardware (no loose nuts / screws under tray 1 or behind the lid) ----------------
def pem_tray1():
    """SO-M3 self-clinching standoffs (control board screws straight into them) and FH-M4 studs (inverter posts thread on),
    all pressed into tray 1 by SendCutSend."""
    out = []
    for (x, y) in CB_SO_XY:
        out.append(cyl_z(x, y, Z_TRAY1, Z_CB, 2.6) - cyl_z(x, y, Z_TRAY1 - 1, Z_CB + 1, 1.25))
    for (x, y) in INV_POST_XY:
        out.append(cyl_z(x, y, Z_TRAY1, Z_TRAY1 + 0.9, 3.4) + cyl_z(x, y, Z_TRAY1, Z_T1TOP + 10.0, 1.95))
    return Compound(out)

def pem_lid_panel():
    """CLS-M3 clinch nuts in the lid at every panel-connector screw: connectors screw in from outside only."""
    out = []
    for n, (x, y, sx, sy, d) in CONNS.items():
        for s_ in (-1, 1):
            xx = x + s_ * (sx / 2 + 2.5)
            out.append(cyl_z(xx, y, H - T - 2.0, H, 2.6) - cyl_z(xx, y, H - T - 3, H + 1, 1.25))
    return Compound(out)

# ---------------- assemble ----------------
def liner_shell():
    """Same as tower.internals' liner, built in shell coords (hold-down holes shifted)."""
    T_, W_, R_ = tw.T, tw.W, tw.R
    Lr = tw.L_IN - 2 * (T_ + tw.NUT_L + 0.6)
    z_top = tw.SEAM_Z - tw.LIP - 1.0
    out_sec = tw.section(W_ - 2 * T_ - 0.4, H - 2 * T_, R_ - T_ - 0.2, T_)
    in_sec = tw.section(W_ - 2 * T_ - 0.4 - 2 * pm.T_LINER, H - 2 * T_ - 2 * pm.T_LINER, R_ - T_ - 0.2 - pm.T_LINER, T_ + pm.T_LINER)
    clip = Plane.YZ * Pos(0, z_top / 2) * Rectangle(W_, z_top)
    liner = extrude((out_sec - in_sec) & clip, amount=Lr / 2, both=True)
    for sx in (-1, 1):
        liner += extrude((out_sec & clip).moved(Location((sx * (Lr / 2 - pm.T_LINER / 2) - pm.T_LINER / 2, 0, 0))), amount=pm.T_LINER)
    for (x, y) in pm.HOLD_XY:
        liner -= Pos(x + DX, y, 0) * Cylinder(2.5, T_ + 3, align=C)
    liner -= Pos(139.0 + DX, 58, CB_TOP + 3) * Rot(0, 90, 0) * Cylinder(3.0, 4)     # LED cable pass-through
    liner -= box(-Lr / 2 - 2, -Lr / 2 + 2, -88, 88, 45, 293)                          # rear flap: open for vent + fan
    return liner

def build():
    mv = lambda part: part.moved(Location((-DX, 0, 0)))
    # ---- shell, built in shell coords, then shifted -DX ----
    hold0 = list(pm.HOLD_XY)
    pm.HOLD_XY = [(x + DX, y) for (x, y) in hold0]
    shell = {"u_body": tw.u_body(),
             "plate_front": tw.plate(+1, True, pipe=True),
             "plate_rear": tw.plate(-1, False, pipe=False, hole_yz=rear_holes(),
                                    screw_yz=[tw.grid_yz(i, j) for (i, j) in tw.SCREW_IJ] + fan_screw_yz())}
    pm.HOLD_XY = hold0
    o, c = CONNS["outlet_nema515"], CONNS["inlet_iec_c14"]
    pm.CONN_PWR = (o[0] + DX, o[1], o[2], o[3])
    pm.CONN_CAN = (c[0] + DX, c[1], c[2], c[3])
    lid = tw.lid()
    for n in ("dc_sb50", "can_m12"):
        x, y, sx, sy, d = CONNS[n]
        lid -= box(x + DX - sx / 2 - 0.5, x + DX + sx / 2 + 0.5, y - sy / 2 - 0.5, y + sy / 2 + 0.5, H - 12, H + 1)
    for n, (x, y, sx, sy, d) in CONNS.items():
        for s in (-1, 1):
            lid -= cyl_z(x + DX + s * (sx / 2 + 2.5), y, H - 12, H + 1, 1.4)
    shell["lid"] = lid
    for sign, tag in ((1, "f"), (-1, "r")):
        t, n = tw.tabs(sign)
        shell[f"tabs_{tag}"], shell[f"pem_tab_{tag}"] = Compound(t), Compound(n)
        shell[f"screws_{tag}"] = plate_screws(sign)
    shell["screws_fan"] = fan_screws_rear()
    for sign, tag in ((1, "f"), (-1, "r")):
        shell[f"feet_{tag}"] = Compound(tw.feet(sign))
    shell["ledboard_f"] = tw.led_board(+1)
    shell["diffuser_f"] = tw.diffuser(+1)
    shell["pipe_f"] = tw.light_pipe(+1)
    shell["pem_lid"] = Compound(tw.lid_nuts())
    shell["screws_lid"] = Compound(tw.lid_screws())
    shell["int_liner_formex"] = liner_shell()
    p = {k: mv(v) for k, v in shell.items()}
    # ---- internals (internal coords) ----
    p["screws_hold"] = Compound(tw.holddown_screws())
    internals = tw.internals()
    for k in list(internals):
        if k.startswith(("power_pcb", "bms_pcb", "imd_zone", "pwr_", "riser_", "mica_barrier", "liner_formex", "carrier")):
            internals.pop(k)
    for k, v in internals.items():
        p[f"int_{k}"] = v
    p["int_busbar_screws"] = busbar_screws()
    ep, nuts = endplates_tslot()
    p["int_comp_endplates"] = ep
    p["int_tnuts"] = nuts
    p["int_so_studs"] = standoff_studs()
    lo, up = standoffs_split()
    p["int_comp_pcb_standoffs"] = lo
    p["int_so_upper"] = up
    p["int_g10_floor"] = g10_floor()
    p["int_g10_frame"] = g10_frame()
    p["int_g10_top"] = g10_top()
    for k, v in risers().items():
        p[f"int_{k}"] = v
    p["tray1"] = tray1()
    p["mica_tray"] = mica_under_tray()
    p["tray2"] = tray2()
    p["inv_posts"] = posts()
    p["screws_trays"] = tray_screws()
    p["charger_npb450"] = charger()
    p["inverter_nts400p"] = inverter()
    p["fan_nfa14"] = fan()

    pcb, comps = control_board()
    p["ctrl_pcb"] = pcb
    for k, v in comps.items():
        p[f"ctrl_{k}"] = v
    for k, v in lid_connectors().items():
        p[f"panel_{k}"] = v
    p["screws_panel"] = lid_connector_screws()
    p["pem_tray1"] = pem_tray1()
    p["pem_lid_panel"] = pem_lid_panel()
    for k, v in cables().items():
        p[f"cable_{k}"] = v
    return p

def led_count():
    mask = tw.text_mask()
    n = sum(1 for i in range(tw.GRID_ROWS) for j in range(tw.GRID_COLS)
            if (i, j) not in tw.SCREW_IJ and (i, j) not in mask)
    return n
