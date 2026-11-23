"""1 kWh-class battery pack, 8S1P prismatic LFP. Parametric build123d model, v1.
Stack (bottom -> top): shell floor / liner / MJF carrier + cells / busbars / flex CCS /
power PCB (contactor, fuse, shunt, precharge, output connector) / BMS+IMD PCB / mica / lid.
Nothing beside the module: all electronics sit above it.
All dimensions in mm. Cell and component envelopes are PLACEHOLDERS - replace with datasheet values.
"""
from build123d import *

# ---------------- parameters ----------------
N_CELLS = 8
# EVE LF50K (spec LF50K-73103 rev D): 135.3 W x 29.3 T (30-40% SOC) x 180.8 body / 185.3 total
CELL_T, CELL_W, CELL_H = 29.3, 135.3, 180.8    # cell thickness (x), width (y), body height (z)
INSUL_T = 1.0                                   # insulating sheet between cells / at stack ends
CELL_PITCH = CELL_T + INSUL_T
TERM_D, TERM_H, TERM_OFF = 12.0, 4.5, 33.75    # pad dia (PLACEHOLDER), height 185.3-180.8, half of 67.5 mm terminal spacing
EP_T, EP_W, EP_H = 8.0, 156.0, 170.0            # compression end plates, 6061 [mm]
ROD_D = 5.0                                     # M5 tie rods
STACK_L = N_CELLS * CELL_T + (N_CELLS + 1) * INSUL_T + 2 * EP_T

T_SHEET, T_LINER, T_MICA = 1.6, 0.5, 0.5
SHELL_L, SHELL_W = 290.0, 190.0
FLANGE = 12.0
LID_HOLE = 5.5

CARRIER_L, CARRIER_W, CARRIER_H = 276.0, 170.0, 30.0
POCKET_DEPTH, POCKET_CLR = 25.0, 0.3

BB_T, BB_W, STUD_HOLE = 2.0, 20.0, 6.5
RISER_T = 3.0                                   # pack-terminal riser bar thickness (copper)

PWR_L, PWR_W, PWR_T = 270.0, 150.0, 2.4         # power PCB (heavy copper); length set by pack-terminal spacing
PWR_GAP = 8.0                                   # flex CCS top -> power PCB underside
PWR_ENVELOPE = 50.0                             # component height allowance above power PCB (contactor)
BMS_L, BMS_W, BMS_T = 200.0, 150.0, 1.6         # BMS + IMD PCB
BMS_ENVELOPE = 12.0
TOP_CLR = 3.0                                   # BMS component top -> mica

# ---------------- derived stack heights ----------------
z_floor = T_SHEET + T_LINER
z_carrier = z_floor
z_cell = z_carrier + CARRIER_H - POCKET_DEPTH
z_cell_top = z_cell + CELL_H
ROD_ZS = [z_cell + 40.0, z_cell + 150.0]
z_ep_top = z_cell + EP_H
z_bb = z_cell_top + TERM_H
z_ccs = z_bb + BB_T
z_pwr = z_ccs + 0.3 + PWR_GAP
z_pwr_top = z_pwr + PWR_T
z_bms = z_pwr_top + PWR_ENVELOPE + 2.0
z_bms_top = z_bms + BMS_T
z_mica = z_bms_top + BMS_ENVELOPE + TOP_CLR
z_flange_bot = z_mica + T_MICA + 0.1
SHELL_H = z_flange_bot + T_SHEET

_x0 = -STACK_L / 2 + EP_T + INSUL_T + CELL_T / 2
cell_x = [_x0 + i * CELL_PITCH for i in range(N_CELLS)]
sheet_x = [_x0 - CELL_T / 2 - INSUL_T / 2 + i * CELL_PITCH for i in range(N_CELLS + 1)]
ep_x = [-STACK_L / 2 + EP_T / 2, STACK_L / 2 - EP_T / 2]
ROD_Y = CELL_W / 2 + 5.0
ROD_Z = None   # set after z_cell
HOLD_XY = [(sx * (STACK_L / 2 - EP_T / 2), sy * 40.0) for sx in (-1, 1) for sy in (-1, 1)]
Y_LAST = TERM_OFF if (N_CELLS - 2) % 2 == 0 else -TERM_OFF
TERM_REACH = 18.0
NEG_X, POS_X = cell_x[0] - TERM_REACH, cell_x[-1] + TERM_REACH   # pack -/+ lug hole x
BMS_X = -(PWR_L - BMS_L) / 2                    # BMS pushed to -x; +x strip left open for connectors

C = (Align.CENTER, Align.CENTER, Align.MIN)
def box(x, y, z, l, w, h):
    return Pos(x, y, z) * Box(l, w, h, align=C)
def cyl(x, y, z, r, h):
    return Pos(x, y, z) * Cylinder(r, h, align=C)

# ---------------- enclosure ----------------
def lid_hole_locs():
    hx = SHELL_L / 2 - T_SHEET - FLANGE / 2
    hy = SHELL_W / 2 - T_SHEET - FLANGE / 2
    return [(x, s * hy) for x in (-hx, -hx / 2, 0, hx / 2, hx) for s in (-1, 1)] + [(s * hx, 0) for s in (-1, 1)]

def drill(part, z0, depth):
    for (x, y) in lid_hole_locs():
        part = part - cyl(x, y, z0, LID_HOLE / 2, depth)
    return part

def shell():
    s = box(0, 0, 0, SHELL_L, SHELL_W, SHELL_H) - box(0, 0, T_SHEET, SHELL_L - 2 * T_SHEET, SHELL_W - 2 * T_SHEET, SHELL_H)
    fl = (box(0, 0, z_flange_bot, SHELL_L - 2 * T_SHEET, SHELL_W - 2 * T_SHEET, T_SHEET)
          - box(0, 0, z_flange_bot, SHELL_L - 2 * T_SHEET - 2 * FLANGE, SHELL_W - 2 * T_SHEET - 2 * FLANGE, T_SHEET))
    return drill(s + fl, z_flange_bot, T_SHEET)

def liner():
    L, W = SHELL_L - 2 * T_SHEET - 0.4, SHELL_W - 2 * T_SHEET - 0.4
    H = z_flange_bot - T_SHEET - 4.0
    return box(0, 0, T_SHEET, L, W, H) - box(0, 0, T_SHEET + T_LINER, L - 2 * T_LINER, W - 2 * T_LINER, H)

# connector positions on the power PCB's open +x strip (pass through BMS-free zone and lid)
CONN_X = PWR_L / 2 - (PWR_L - BMS_L) / 2 + 2
CONN_PWR = (CONN_X, -25.0, 36.0, 46.0)          # x, y, l, w  (output power connector, PLACEHOLDER)
CONN_CAN = (CONN_X, 45.0, 22.0, 16.0)           # CAN / LV connector

def lid():
    l = drill(box(0, 0, SHELL_H, SHELL_L, SHELL_W, T_SHEET), SHELL_H, T_SHEET)
    for (x, y, cl, cw) in (CONN_PWR, CONN_CAN):
        l = l - box(x, y, SHELL_H, cl + 1, cw + 1, T_SHEET)
    return l

def mica():
    m = box(0, 0, z_mica, SHELL_L - 2 * T_SHEET - 2, SHELL_W - 2 * T_SHEET - 2, T_MICA)
    for (x, y, cl, cw) in (CONN_PWR, CONN_CAN):
        m = m - box(x, y, z_mica, cl + 4, cw + 4, T_MICA)
    return m

# ---------------- module ----------------
def carrier():
    c = box(0, 0, z_carrier, CARRIER_L, CARRIER_W, CARRIER_H)
    c = c - box(0, 0, z_cell, STACK_L + 2 * POCKET_CLR, EP_W + 2 * POCKET_CLR, POCKET_DEPTH + 1)
    for (x, y) in HOLD_XY:          # hold-down screw clearance through pocket floor
        c = c - cyl(x, y, z_carrier - 1, 2.25, z_cell - z_carrier + 2)
    return c

def compression():
    """8 mm end plates + 4 M5 tie rods + nuts + insulating sheets + PCB standoffs."""
    out = {}
    eps = []
    for x in ep_x:
        p = box(x, 0, z_cell, EP_T, EP_W, EP_H)
        for y in (-ROD_Y, ROD_Y):
            for z in ROD_ZS:
                p = p - Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(ROD_D / 2 + 0.25, EP_T + 1)
        for (hx, hy) in HOLD_XY:     # M4 tapped from bottom edge, 12 deep
            if abs(hx - x) < 1:
                p = p - cyl(x, hy, z_cell, 1.65, 12)
        for (sx, sy) in PCB_SO_XY:   # M4 tapped from top edge
            if abs(sx - x) < 1:
                p = p - cyl(x, sy, z_ep_top - 10, 1.65, 10)
        eps.append(p)
    out["endplates"] = Compound(eps)
    rod_l = STACK_L + 2 * 6.0
    rods, nuts = [], []
    for y in (-ROD_Y, ROD_Y):
        for z in ROD_ZS:
            rods.append(Pos(0, y, z) * Rot(0, 90, 0) * Cylinder(ROD_D / 2, rod_l))
            for sx in (-1, 1):
                nuts.append(Pos(sx * (STACK_L / 2 + 2.5), y, z) * Rot(0, 90, 0) * (Cylinder(4.6, 4.0) - Cylinder(ROD_D / 2, 4.0)))
    out["rods"] = Compound(rods)
    out["rodnuts"] = Compound(nuts)
    out["insul_sheets"] = Compound([box(x, 0, z_cell, INSUL_T, CELL_W, CELL_H) for x in sheet_x])
    out["pcb_standoffs"] = Compound([cyl(x, y, z_ep_top, 3.5, z_pwr - z_ep_top) for (x, y) in PCB_SO_XY])
    return out

def cells():
    out = []
    for x in cell_x:
        b = box(x, 0, z_cell, CELL_T, CELL_W, CELL_H)
        for y in (-TERM_OFF, TERM_OFF):
            b = b + cyl(x, y, z_cell_top, TERM_D / 2, TERM_H)
        out.append(b)
    return out

def busbar(x0, x1, y):
    b = box((x0 + x1) / 2, y, z_bb, abs(x1 - x0) + TERM_D + 4, BB_W, BB_T)
    for x in (x0, x1):
        b = b - cyl(x, y, z_bb, STUD_HOLE / 2, BB_T)
    return b

def busbars():
    out = [busbar(cell_x[i], cell_x[i + 1], -TERM_OFF if i % 2 == 0 else TERM_OFF) for i in range(N_CELLS - 1)]
    out.append(busbar(cell_x[0], NEG_X, TERM_OFF))
    out.append(busbar(cell_x[-1], POS_X, Y_LAST))
    return out

def risers():
    """Copper risers: pack -/+ lug -> power PCB underside, bolted at both ends."""
    h = z_pwr - (z_bb + BB_T)
    out = []
    for x, y in ((NEG_X, TERM_OFF), (POS_X, Y_LAST)):
        xr = x + (1 if x > 0 else -1) * (TERM_D / 2 + 2 + RISER_T / 2)
        out.append(box(xr, y, z_bb, RISER_T, BB_W, h + BB_T))
    return out

def sense_nodes():
    n = [((cell_x[i] + cell_x[i + 1]) / 2, -TERM_OFF if i % 2 == 0 else TERM_OFF) for i in range(N_CELLS - 1)]
    return n + [(cell_x[0] - 9, TERM_OFF), (cell_x[-1] + 9, Y_LAST)]

def flex_ccs():
    f = box(0, 0, z_ccs, cell_x[-1] - cell_x[0] + 20, 24, 0.3)
    for (x, y) in sense_nodes():
        L = abs(y) - 12 + BB_W / 2 - 2
        f = f + box(x, (12 + L / 2) * (1 if y > 0 else -1), z_ccs, 6, L, 0.3)
    return f

# ---------------- electronics stack ----------------
PCB_SO_XY = [(sx * (STACK_L / 2 - EP_T / 2), sy * 70.0) for sx in (-1, 1) for sy in (-1, 1)]  # on end-plate top edges

def power_pcb():
    """Power PCB + component envelopes. Contactor: PCB-mount, bolt-through (e.g. Gigavac MiniTACTOR P105/P115 class)."""
    b = box(0, 0, z_pwr, PWR_L, PWR_W, PWR_T)
    t = z_pwr_top
    comps = {
        "contactor": box(30, -30, t, 45, 40, 45),
        "fuse": box(-55, -30, t, 60, 22, 25),
        "shunt": box(-55, 30, t, 50, 15, 10),
        "precharge": box(30, 35, t, 22, 16, 16),
        "conn_pwr": box(CONN_PWR[0], CONN_PWR[1], t, CONN_PWR[2], CONN_PWR[3], SHELL_H + T_SHEET + 8 - t),
        "conn_can": box(CONN_CAN[0], CONN_CAN[1], t, CONN_CAN[2], CONN_CAN[3], SHELL_H + T_SHEET + 6 - t),
    }
    return b, comps

def bms_pcb():
    """BMS + IMD board, stacked directly on the power PCB via standoffs at its corners."""
    b = box(BMS_X, 0, z_bms, BMS_L, BMS_W, BMS_T)
    t = z_bms_top
    b = b + box(BMS_X - 40, -20, t, 14, 14, 1.2) + box(BMS_X + 10, 20, t, 10, 10, 1.2)
    for (x, y) in [(BMS_X + sx * (BMS_L / 2 - 8), sy * (BMS_W / 2 - 8)) for sx in (-1, 1) for sy in (-1, 1)]:
        b = b + cyl(x, y, z_pwr_top, 3, z_bms - z_pwr_top)
    imd = box(BMS_X + 60, -40, t, 50, 40, 8)        # IMD zone (isolation barrier region) - space allocation
    return b, imd

def build():
    pwr, comps = power_pcb()
    bms, imd = bms_pcb()
    parts = {"shell_5052": shell(), "liner_formex": liner(), "carrier_mjf_pa12": carrier(),
             "flex_ccs": flex_ccs(), "power_pcb": pwr, "bms_pcb": bms, "imd_zone": imd,
             "mica_barrier": mica(), "lid_5052": lid()}
    parts.update({f"pwr_{k}": v for k, v in comps.items()})
    parts.update({f"cell_{i+1}": c for i, c in enumerate(cells())})
    parts.update({f"busbar_{i+1}": b for i, b in enumerate(busbars())})
    parts.update({f"riser_{i+1}": r for i, r in enumerate(risers())})
    parts.update({f"comp_{k}": v for k, v in compression().items()})
    return parts

def cutaway(p, z_min=30.0):
    return p - Pos(0, -SHELL_W, z_min) * Box(SHELL_L, SHELL_W, SHELL_H * 2, align=(Align.MIN, Align.MIN, Align.MIN))
