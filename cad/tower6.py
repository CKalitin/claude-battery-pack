"""Claude battery pack v6: 4S1P EVE LF100MA lying on their narrow edge (terminals face +y wall), every fabricated part from SendCutSend.
Cell axes: thickness 50.1 along x (stack), the 160 width vertical (z), the 118.5 height along y with terminals at +y.
Units mm. x = length (front plate at +x), y = width, z = up. Body bottom at z = 0. One coordinate system for everything.

SendCutSend rules this file is built to (sources: sendcutsend.com bending guidelines + bending calculator, Nov 2026):
  5052 .063: K .42, eff. inner radius .035", die .472", min formed flange .303", min flat flange .255"
  no roll/bump forming (so no R22 radius: 3 x 30 deg bends per corner)
  U/C channel: base >= 2 x flange  (a one-piece 222 x 213 U fails: legs 213 > base/2 -> body split into two L halves)
  no pockets, chamfers or edge taps on laser parts; countersink edge rule unmet beside grid holes -> button heads
  powder coat: 15 stock colours only (Gloss Red RAL 3002, Metallic Gray) ; tapped holes need chasing after coat
"""
import math
from build123d import *

IN = 25.4
C = (Align.CENTER, Align.CENTER, Align.MIN)

def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=C)

def cyl_z(x, y, z0, z1, r):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=C)

def cyl_x(x0, x1, y, z, r):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))

def cyl_y(x, y0, y1, z, r):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, abs(y1 - y0))

# ======================= materials (SCS stock thicknesses) =======================
T = 0.063 * IN            # 1.600  5052 sheet: body halves, lid, trays
PT = 0.187 * IN           # 4.750  6061 end plates
EP_T = 0.313 * IN         # 7.950  6061 module end plates
G10_FLOOR = 0.187 * IN    # 4.750
G10_FRAME = 0.187 * IN   # 4.750  (.125 G10 out of stock at SCS, Nov 2026)
G10_TOP = 0.063 * IN      # 1.600  (LF100 terminals stand only 2.8 mm proud of the can)
G10_SPACER = 0.063 * IN   # 1.600  cell-to-cell / end insulators
CU = 0.125 * IN           # 3.175  copper busbars
ACR_DIFF = 0.118 * IN     # 3.000  white acrylic diffuser (SCS white comes only in .118)
ACR_PIPE = 0.118 * IN     # 3.000  clear acrylic light pipe
MYLAR = 0.010 * IN        # 0.254  Mylar sheet under tray 1

# ======================= SCS bend data, 5052 .063 =======================
K = 0.42
RI = 0.035 * IN           # 0.889 effective inner radius
DIE = 0.472 * IN          # 11.99
MIN_FLAT_FLANGE = 0.255 * IN

# ======================= cell: EVE LF100MA (LF100M spec: 160 x 49.9-50.1 x 118.5 total / 115.7 body, poles 97.0) =======================
N = 4
CELL_T, CELL_W, CELL_BODY, CELL_TOT = 50.1, 160.0, 115.7, 118.5
TERM_H = CELL_TOT - CELL_BODY        # 2.8
TERM_OFF = 97.0 / 2                  # 48.5
TERM_D = 18.0                        # pad dia: PLACEHOLDER (not in spec)
TERM_THREAD_R = 3.0
FLEX_Y = -21.0                  # M6 assumed (not in spec)
PITCH_C = CELL_T + G10_SPACER
STACK_L = N * CELL_T + (N + 1) * G10_SPACER + 2 * EP_T
cell_x = [(k - (N - 1) / 2) * PITCH_C for k in range(N)]
ep_x = [-(STACK_L / 2 - EP_T / 2), STACK_L / 2 - EP_T / 2]
spacer_x = [cell_x[0] - PITCH_C / 2 + k * PITCH_C for k in range(N + 1)]
ROD_Y, ROD_D = 85.0, 5.0

# ======================= module geometry (cells on edge) =======================
YC0 = -58.0                                      # cell base face (old bottom) y
YC1 = YC0 + CELL_BODY                            # terminal face of the can (old top)  57.7
Y_TERM = YC0 + CELL_TOT                          # terminal contact face            60.5
Y_BB0, Y_BB1 = Y_TERM, Y_TERM + 0.125 * IN       # busbar plane                     60.5 .. 63.675
EP_Y0, EP_Y1 = YC0 - 14.0, Y_BB1 + 12.0          # module end plate y extent        -72 .. 75.7
Z_FLOOR = T
Z_CELL = Z_FLOOR + G10_FLOOR                     # cells & end plates stand on the G10 floor
Z_CTOP = Z_CELL + CELL_W                         # top of the cells (160 width vertical)
Z_MID = Z_CELL + CELL_W / 2
Z_ROW = {"hi": Z_MID + TERM_OFF, "lo": Z_MID - TERM_OFF}   # terminal rows
EP_TOP = Z_CTOP
RODS = [(YC0 - 7.0, Z_CELL + 11.0), (YC0 - 7.0, Z_CTOP - 11.0),          # -y rods near the top/bottom corners
        (Y_BB1 + 4.5, Z_MID - 16.0), (Y_BB1 + 4.5, Z_MID + 16.0)]        # +y rods between the busbar rows, outboard of the screw heads
Z_TFRAME = Z_CTOP                                # top G10 frame (same part as the bottom frame)
Z_TRAY1 = Z_TFRAME + G10_FRAME + MYLAR           # tray 1 sits on the top frame + Mylar: no standoffs
Z_T1TOP = Z_TRAY1 + T
CHG = (205.0, 135.0, 55.0)                       # MEAN WELL NPB-450-12 (same case as -24: ASSUMED)
INV = (186.0, 100.5, 34.0)                       # MEAN WELL NTS-400P-112 (same case as -124: ASSUMED)
Z_TRAY2 = Z_T1TOP + CHG[2] + 1.8
Z_T2TOP = Z_TRAY2 + T
H = Z_T2TOP + INV[2] + 3.4                       # lid outer top
W = 180.0                                        # body outer width

# ======================= shell layout =======================
L_IN = 310.0
DX = 10.0
XF = L_IN / 2 - DX                               # front plate inner face  (+145)
XR = -(L_IN / 2 + DX)                            # rear plate inner face   (-165)
XM = (XF + XR) / 2                               # shell centre x (-10)
F = 15.0                                         # facet length on the outer mould line
CNR = F * (math.cos(math.radians(30)) + math.cos(math.radians(60)))  # 20.49: corner size (like an R20.5)
A_FLAT = W / 2 - CNR                             # floor flat half-width (outer)
SEAM_Y = 24.0                                    # floor butt seam between halves (hidden under the G10 floor)
LID_H = 42.0                                     # lid side height (clinch nuts need ~>=6 mm to the wall top edge: SCS flagged 5.5)
SEAM_Z = H - LID_H                               # lid lower edge
LID_GAP = 0.2
WL = W + 2 * (T + LID_GAP)                       # lid outer width: shoebox lid over the body walls, no joggle
WALL_TOP = H - CNR - 2.5                         # body wall top, below the lid's facet zone
LID_SCREW_Z = (SEAM_Z + WALL_TOP) / 2
LID_SCREW_X = [XM - 100.0, XM + 100.0]

# end plate outline (as v4)
PW = W + 16.0
FOOT, HANDLE = 18.0, 52.0
PZ0, PZ1 = -FOOT, H + HANDLE
PR, LEG, ARCH_H, ARCH_R = 26.7, 48.3, 15.0, 13.3
SLOT_L, SLOT_H, SLOT_TOP = 83.3, 28.3, 15.0

# grids
PITCH = 124.5 / 16                               # 7.78125: NF-A14 hole spacing = 16 pitches
COLS = 21
GRID_Y0 = -(COLS - 1) / 2 * PITCH                # -93.375
ZB = 40.0                                        # bottom row: wall tabs must sit >= die + clearance above the facets
ROWS_F = 26
ROWS_R = 28
HOLE_D = 4.8
SCREW_CLR = 4.5
def node(k, j):                                  # row k counted from the bottom, col j
    return GRID_Y0 + j * PITCH, ZB + k * PITCH
MID_K = 12
SCREW_KJ = [(0, 0), (0, COLS - 1), (0, (COLS - 1) // 2), (MID_K, 0), (MID_K, COLS - 1), (ROWS_F - 1, 0), (ROWS_F - 1, COLS - 1)]
SCREW_YZ = [node(k, j) for (k, j) in SCREW_KJ]
FAN = (140.0, 25.0)
FAN_K = 19
FAN_YZ = (0.0, ZB + FAN_K * PITCH)
FAN_HOLE = 124.5 / 2
FAN_SCREW_YZ = [(FAN_YZ[0] + sy * FAN_HOLE, FAN_YZ[1] + sz * FAN_HOLE) for sy in (-1, 1) for sz in (-1, 1)]
PIPE_Z, PIPE_SLOT = ZB + (ROWS_F - 1) * PITCH + 6.6, 3.2                   # slot >= 50 % of plate thickness (2.38)
TAB_H = 10.0                                     # tab height across the bend line
TAB_TAP = 3.3                                    # M4 tap drill, SCS taps
TAB_END = abs(GRID_Y0) - 5.0                     # wall tabs stop short of the col-1 holes (edge 88.0)

FONT = {"W": ["10001", "10001", "10101", "10101", "01010"], "E": ["111", "100", "111", "100", "111"],
        "I": ["111", "010", "010", "010", "111"], "L": ["100", "100", "100", "100", "111"],
        "N": ["1001", "1101", "1011", "1001", "1001"]}
TEXT = ["WE", "WILL", "WIN"]

def text_mask():
    def bitmap(s):
        rows = [""] * 5
        for i, ch in enumerate(s):
            for r in range(5):
                rows[r] += ("0" if i else "") + FONT[ch][r]
        return rows
    lines = [bitmap(t) for t in TEXT]
    th = 5 * len(lines) + len(lines) - 1
    top = (ROWS_F - th) // 2 + th - 1            # k index of the first text row (from bottom)
    m = set()
    for li, bm in enumerate(lines):
        w = len(bm[0]); c0 = (COLS - w) // 2
        for ri in range(5):
            for cj in range(w):
                if bm[ri][cj] == "1":
                    m.add((top - (li * 6 + ri), c0 + cj))
    return m

def front_holes():
    skip = set(SCREW_KJ) | text_mask()
    return [node(k, j) for k in range(ROWS_F) for j in range(COLS) if (k, j) not in skip]

def rear_holes():
    sk = {(round(y, 3), round(z, 3)) for (y, z) in SCREW_YZ + FAN_SCREW_YZ}
    return [node(k, j) for k in range(ROWS_R) for j in range(COLS) if (round(node(k, j)[0], 3), round(node(k, j)[1], 3)) not in sk]

# ======================= sheet profile tools =======================
def offset_polyline(pts, d):
    """Offset an open polyline by d to its LEFT (miter joins)."""
    n = []
    for (a, b) in zip(pts[:-1], pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        n.append((-dy / L, dx / L))
    out = [(pts[0][0] + d * n[0][0], pts[0][1] + d * n[0][1])]
    for j in range(1, len(pts) - 1):
        n0, n1 = n[j - 1], n[j]
        s = 1 + n0[0] * n1[0] + n0[1] * n1[1]
        out.append((pts[j][0] + d * (n0[0] + n1[0]) / s, pts[j][1] + d * (n0[1] + n1[1]) / s))
    out.append((pts[-1][0] + d * n[-1][0], pts[-1][1] + d * n[-1][1]))
    return out

def sheet_extrude(oml, x0, x1, inside_left=True):
    """oml: outer mould line in (y, z). Material lies on the left of the travel direction if inside_left."""
    inner = offset_polyline(oml, T if inside_left else -T)
    poly = oml + inner[::-1]
    face = Plane.YZ * Polygon(*poly, align=None)
    return Pos(x0, 0, 0) * extrude(face, amount=x1 - x0, dir=(1, 0, 0))

c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def half_oml(side):
    """side -1: half A (seam -> -y wall), side +1: half B (seam -> +y wall). Bottom-up."""
    s = side
    pts = [(SEAM_Y + (0.25 if s > 0 else -0.25), 0.0), (s * A_FLAT, 0.0), (s * (A_FLAT + F * c30), F * s30), (s * W / 2, CNR), (s * W / 2, WALL_TOP)]
    return pts, (s < 0)   # A travels toward -y: interior (+z) is on the right -> inside_left False ... see below

def lid_oml():
    a = WL / 2 - CNR
    return [(-WL / 2, SEAM_Z), (-WL / 2, H - CNR), (-WL / 2 + F * s30, H - CNR + F * c30), (-a, H), (a, H),
            (WL / 2 - F * s30, H - CNR + F * c30), (WL / 2, H - CNR), (WL / 2, SEAM_Z)]

# ======================= body halves =======================
def body_half(side):
    pts, _ = half_oml(side)
    # half B travels +y then up: interior is on the left.  half A travels -y then up: interior on the right.
    b = sheet_extrude(pts, XR, XF, inside_left=(side > 0))
    xs = [XF, XR]
    for x_end in xs:
        sgn = 1 if x_end > 0 else -1
        xa, xb = sorted((x_end, x_end - sgn * T))
        for (y, z) in SCREW_YZ:
            if y == 0.0:                                     # floor tab: half A only (seam at +24)
                if side < 0:
                    t = box(xa, xb, -5.0, 5.0, T, z + TAB_H / 2)
                    t -= cyl_x(xa - 1, xb + 1, y, z, TAB_TAP / 2)
                    b += t
                continue
            if (y > 0) != (side > 0):
                continue
            yw = W / 2 - T
            y0, y1 = sorted((math.copysign(yw, y), math.copysign(TAB_END, y)))
            t = box(xa, xb, y0, y1, z - TAB_H / 2, z + TAB_H / 2)
            t -= cyl_x(xa - 1, xb + 1, y, z, TAB_TAP / 2)
            b += t
    for x in ep_x:                                           # module hold-down clearance holes
        for y in (-40.0, 40.0):
            if (y > SEAM_Y) == (side > 0):
                b -= cyl_z(x, y, -1, T + 1, 2.25)
    for x in LID_SCREW_X:                                    # CLS-M3 clinch nut holes (lid screws)
        b -= cyl_y(x, side * (W / 2 + 1), side * (W / 2 - T - 1), LID_SCREW_Z, 4.25 / 2)
    return b

def lid():
    lo = lid_oml()
    L = sheet_extrude(lo, XR + 0.5, XF - 0.5, inside_left=False)
    for (n, (x, y, sx, sy, d)) in CONNS.items():
        L -= box(x - sx / 2 - 0.5, x + sx / 2 + 0.5, y - sy / 2 - 0.5, y + sy / 2 + 0.5, H - 6, H + 1)
        for s in (-1, 1):
            L -= cyl_z(x, y + s * (sy / 2 + CONN_HOLE), H - 6, H + 1, 4.25 / 2)       # CLS-M3 holes
    for x in LID_SCREW_X:
        for s in (-1, 1):
            L -= cyl_y(x, s * (WL / 2 + 1), s * (WL / 2 - T - 1), LID_SCREW_Z, 3.4 / 2)
    return L

def lid_screws():
    out = []
    for x in LID_SCREW_X:
        for s in (-1, 1):
            yh = s * WL / 2
            head = cyl_y(x, yh, yh + s * 1.65, LID_SCREW_Z, 2.75)
            sh = cyl_y(x, yh, s * (W / 2 - T - 2.0), LID_SCREW_Z, 1.45)
            out.append(head + sh)
    return Compound(out)

def pem_body_lid():
    out = []
    for x in LID_SCREW_X:
        for s in (-1, 1):
            yi = s * (W / 2 - T)
            out.append(cyl_y(x, yi, yi - s * 1.5, LID_SCREW_Z, 2.9) - cyl_y(x, yi + s, yi - s * 2.5, LID_SCREW_Z, 1.25))
    return Compound(out)

# ======================= end plates =======================
def plate(front):
    zc = (PZ0 + PZ1) / 2
    with BuildSketch(Plane.YZ) as sk:
        with Locations((0, zc)):
            RectangleRounded(PW, PZ1 - PZ0, PR)
        with Locations((0, PZ0)):
            RectangleRounded(PW - 2 * LEG, 2 * ARCH_H, ARCH_R, mode=Mode.SUBTRACT)
        with Locations((0, PZ1 - SLOT_TOP - SLOT_H / 2)):
            SlotCenterToCenter(SLOT_L - SLOT_H, SLOT_H, mode=Mode.SUBTRACT)
        holes = front_holes() if front else rear_holes()
        with Locations(*holes):
            Circle(HOLE_D / 2, mode=Mode.SUBTRACT)
        with Locations(*(SCREW_YZ + ([] if front else FAN_SCREW_YZ))):
            Circle(SCREW_CLR / 2, mode=Mode.SUBTRACT)
        if front:
            with Locations((0, PIPE_Z)):
                SlotCenterToCenter(2 * abs(GRID_Y0) - PIPE_SLOT, PIPE_SLOT, mode=Mode.SUBTRACT)
    p = extrude(sk.sketch, amount=PT)
    return p.moved(Location((XF, 0, 0))) if front else p.mirror(Plane.YZ).moved(Location((XR, 0, 0)))

def button_screw(y, z, front, shank, nut_x=None):
    """ISO 7380 M4 button head, 2.5 mm hex socket, black."""
    xo = XF + PT if front else XR - PT
    s = 1 if front else -1
    head = cyl_x(xo, xo + s * 2.2, y, z, 3.8)
    head -= Pos(xo + s * 1.4, y, z) * Rot(0, 90, 0) * extrude(RegularPolygon(1.44, 6), 1.0, both=True)
    shank_ = cyl_x(xo, xo - s * shank, y, z, 1.95)
    out = head + shank_
    if nut_x is not None:
        out += cyl_x(nut_x, nut_x - s * 3.2, y, z, 3.6) - cyl_x(nut_x + s, nut_x - s * 4.2, y, z, 2.0)
    return out

def plate_screws(front):
    return Compound([button_screw(y, z, front, PT + T + 2.5) for (y, z) in SCREW_YZ])

def fan_screws():
    return Compound([button_screw(y, z, False, PT + 9.0, nut_x=XR + 4.0) for (y, z) in FAN_SCREW_YZ])

def feet():
    out = []
    for x in (XF + PT / 2, XR - PT / 2):
        for s in (-1, 1):
            out.append(cyl_z(x, s * (PW / 2 - LEG / 2), PZ0 - 2.0, PZ0, 4.0))   # 3M Bumpon SJ-5302 class, stick-on
    return Compound(out)

# ======================= front light: diffuser, LED board, pipe =======================
def _front_panel(x0, x1):
    y1 = abs(GRID_Y0) + 4.0
    p = box(x0, x1, -y1, y1, ZB - 4.0, PIPE_Z - ACR_PIPE / 2 - 1.0)   # top edge under the light pipe (edge-lit from LEDs on this edge)
    for (y, z) in SCREW_YZ:
        if y == 0.0:
            p -= box(x0 - 1, x1 + 1, -5.4, 5.4, ZB - 5, z + TAB_H / 2 + 0.4)
        else:
            p -= box(x0 - 1, x1 + 1, math.copysign(TAB_END - 0.4, y), math.copysign(y1 + 1, y), z - TAB_H / 2 - 0.4, z + TAB_H / 2 + 0.4)
    return p

def diffuser():
    return _front_panel(XF - ACR_DIFF, XF)

def led_board():
    return _front_panel(XF - ACR_DIFF - 1.6, XF - ACR_DIFF)

def light_pipe():
    return box(XF - 5.8, XF + PT - 0.2, -(abs(GRID_Y0) - 0.5), abs(GRID_Y0) - 0.5, PIPE_Z - ACR_PIPE / 2, PIPE_Z + ACR_PIPE / 2)

# ======================= module =======================
NUT_W, NUT_H = 7.0, 3.2
HOLD_Y = 40.0
TRAY_SCREW_Y = 45.0

def tslot(x, y, z_edge, inward):
    z0, z1 = sorted((z_edge - inward * 1, z_edge + inward * 15))
    cut = box(x - 5, x + 5, y - 2.25, y + 2.25, z0, z1)
    n0, n1 = sorted((z_edge + inward * 7.0, z_edge + inward * (7.0 + NUT_H + 0.2)))
    cut += box(x - 5, x + 5, y - NUT_W / 2 - 0.15, y + NUT_W / 2 + 0.15, n0, n1)
    nut = box(x - NUT_W / 2, x + NUT_W / 2, y - NUT_W / 2, y + NUT_W / 2, n0 + 0.1, n1 - 0.1) - cyl_z(x, y, n0 - 1, n1 + 1, 2.0)
    return cut, nut

def module_endplates():
    eps, nuts = [], []
    for x in ep_x:
        p = box(x - EP_T / 2, x + EP_T / 2, EP_Y0, EP_Y1, Z_CELL, EP_TOP)
        for (y, z) in RODS:
            p -= cyl_x(x - 5, x + 5, y, z, ROD_D / 2 + 0.25)
        for y in (-HOLD_Y, HOLD_Y):
            c, n = tslot(x, y, Z_CELL, +1); p -= c; nuts.append(n)
        for y in (-TRAY_SCREW_Y, TRAY_SCREW_Y):
            c, n = tslot(x, y, EP_TOP, -1); p -= c; nuts.append(n)
        eps.append(p)
    return Compound(eps), Compound(nuts)

def rods():
    L = STACK_L + 12.0
    r, n = [], []
    for (y, z) in RODS:
        r.append(cyl_x(-L / 2, L / 2, y, z, ROD_D / 2))
        for s in (-1, 1):
            x0 = s * STACK_L / 2
            n.append(cyl_x(x0, x0 + s * 4.0, y, z, 4.0) - cyl_x(x0 - 1, x0 + s * 5, y, z, ROD_D / 2))
    return Compound(r), Compound(n)

def pos_row(k):
    """row of cell k's + terminal. Chain pack+ = cell 3 +, pack- = cell 0 -, both on the hi row."""
    return "hi" if k % 2 == 1 else "lo"

def neg_row(k):
    return "lo" if k % 2 == 1 else "hi"

def cells():
    out = []
    for k, x in enumerate(cell_x):
        b = box(x - CELL_T / 2, x + CELL_T / 2, YC0, YC1, Z_CELL, Z_CTOP)
        for row in ("hi", "lo"):
            b += Pos(x, YC1, Z_ROW[row]) * Rot(-90, 0, 0) * Cylinder(TERM_D / 2, TERM_H, align=C)
        out.append(b)
    return out

def spacers():
    return Compound([box(x - G10_SPACER / 2, x + G10_SPACER / 2, YC0, YC1, Z_CELL, Z_CTOP) for x in spacer_x])

def g10_floor():
    f = box(-STACK_L / 2 - 0.5, STACK_L / 2 + 0.5, -68.0, 68.0, Z_FLOOR, Z_CELL)
    for x in ep_x:
        for y in (-HOLD_Y, HOLD_Y):
            f -= cyl_z(x, y, Z_FLOOR - 1, Z_CELL + 1, 2.25)
    return f

FRAME_Y0, FRAME_Y1 = EP_Y0 - 3.0, EP_Y1 + 1.0
FRAME_NOTCH = (62.0, 104.0, Y_TERM - 2.5, Y_BB1 + 3.0)   # strap + flex pass-through (harmless on the bottom copy)
def g10_frame(z0):
    xo = STACK_L / 2 + 6.0
    f = box(-xo, xo, FRAME_Y0, FRAME_Y1, z0, z0 + G10_FRAME)
    xi = STACK_L / 2 - EP_T
    f -= box(-xi, xi, YC0 - 0.3, YC1 + 0.3, z0 - 1, z0 + G10_FRAME + 1)
    for sx in (-1, 1):
        f -= box(sx * (xi - 0.3), sx * (STACK_L / 2 + 0.3), EP_Y0 - 0.3, EP_Y1 + 0.3, z0 - 1, z0 + G10_FRAME + 1)
    a, b, c, d = FRAME_NOTCH
    f -= box(a, b, c, d, z0 - 1, z0 + G10_FRAME + 1)
    for (x, y) in CHG_SCREW_XY + INV_POST_XY:
        if abs(x) < xo + 6 and FRAME_Y0 < y < FRAME_Y1:
            f -= cyl_z(x, y, z0 - 1, z0 + G10_FRAME + 1, 5.0)
    return f

def holddown_screws():
    out = []
    for x in ep_x:
        for y in (-HOLD_Y, HOLD_Y):
            out.append(cyl_z(x, y, -2.2, 0, 3.8) + cyl_z(x, y, 0, Z_CELL + 9.5, 1.95))
    return Compound(out)

# ---- busbars, C110 copper .125, standing in the plane y = 60.5 .. 63.7 ----
BB_W = 25.0
def plate_xz(x0, x1, z0, z1):
    return box(x0, x1, Y_BB0, Y_BB1, z0, z1)

def bar_holes(b, pts):
    for (x, z) in pts:
        b -= cyl_y(x, Y_BB0 - 1, Y_BB1 + 1, z, 3.3)
    return b

LINKS = [(3, 2), (2, 1), (1, 0)]                 # (cell with -, cell with +)
def busbars():
    out = {}
    for i, (a, b) in enumerate(LINKS):
        z = Z_ROW[neg_row(a)]
        x0, x1 = sorted((cell_x[a], cell_x[b]))
        bar = plate_xz(x0 - BB_W / 2, x1 + BB_W / 2, z - BB_W / 2, z + BB_W / 2)
        out[f"link_{i+1}"] = bar_holes(bar, [(x0, z), (x1, z)])
    return out

Z_CB = Z_T1TOP + 10.0                            # SCS M3 flush standoff .394": room for the M6 nuts under the strap tabs
POS_RISER = (90.0, 102.0)                        # x span of the pack+ riser (stays clear of the front end plate at 104)
NEG_RISER = (78.0, 88.0)
NEG_RUN_Z = (Z_ROW["hi"] + BB_W / 2 + 2.6, Z_ROW["hi"] + BB_W / 2 + 14.6)
TAB_Y0 = 45.0                                    # bent tabs reach under the control board to y = 45
def pack_straps():
    """Each strap: one flat .125 copper profile in the busbar plane + one 90 deg bend into a tab under the control board."""
    zh = Z_ROW["hi"]
    x3, x0 = cell_x[3], cell_x[0]
    zt0 = Z_CB - CU
    pos = plate_xz(x3 - BB_W / 2, POS_RISER[1], zh - BB_W / 2, zh + BB_W / 2)
    pos += plate_xz(POS_RISER[0], POS_RISER[1], zh + BB_W / 2, zt0)
    pos += box(POS_RISER[0], POS_RISER[1], TAB_Y0, Y_BB1, zt0, Z_CB)
    pos = bar_holes(pos, [(x3, zh)])
    pos -= cyl_z(sum(POS_RISER) / 2, (TAB_Y0 + Y_BB0) / 2, zt0 - 1, Z_CB + 1, 3.3)
    neg = plate_xz(x0 - BB_W / 2, x0 + BB_W / 2, zh - BB_W / 2, NEG_RUN_Z[1])
    neg += plate_xz(x0 - BB_W / 2, NEG_RISER[1], NEG_RUN_Z[0], NEG_RUN_Z[1])
    neg += plate_xz(NEG_RISER[0], NEG_RISER[1], NEG_RUN_Z[1], zt0)
    neg += box(NEG_RISER[0], NEG_RISER[1], TAB_Y0, Y_BB1, zt0, Z_CB)
    neg = bar_holes(neg, [(x0, zh)])
    neg -= cyl_z(sum(NEG_RISER) / 2, (TAB_Y0 + Y_BB0) / 2, zt0 - 1, Z_CB + 1, 3.3)
    return pos, neg

def terminal_screws():
    out = []
    for x in cell_x:
        for row in ("hi", "lo"):
            z = Z_ROW[row]
            out.append(cyl_y(x, Y_BB1, Y_BB1 + 4.0, z, 6.0) + cyl_y(x, Y_BB1 - 9.0, Y_BB1, z, 2.95))
    return Compound(out)

def strap_screws():
    out = []
    for xs in (POS_RISER, NEG_RISER):
        xc = sum(xs) / 2; yc = (TAB_Y0 + Y_BB0) / 2
        out.append(cyl_z(xc, yc, CB_TOP, CB_TOP + 4.0, 6.0) + cyl_z(xc, yc, Z_CB - CU - 4.0, CB_TOP, 2.95)
                   + cyl_z(xc, yc, Z_CB - CU - 5.0, Z_CB - CU, 5.0))   # M6 flange screw down through the board, nut under the tab
    return Compound(out)

FLEX_Z = Z_MID                                   # flex spine between the busbar rows
FLEX_TAIL_X = (70.0, 77.0)
def sense_flex():
    """Flex CCS (PCB fab, not SCS) on the busbar side, one layer outboard of the bars: spine between the rows, a tab per node,
       tail jogs over the pack+ screw head, rises through tray 1 behind the charger, runs under the board to its connector."""
    y0 = Y_BB1 + 0.3; y1 = y0 + 0.3
    f = box(cell_x[0] - 10, 69.0, y0, y1, FLEX_Z - 5, FLEX_Z + 5)
    for (a, b) in LINKS:
        z = Z_ROW[neg_row(a)]
        xm = (cell_x[a] + cell_x[b]) / 2
        f += box(xm - 3, xm + 3, y0, y1, min(FLEX_Z, z), max(FLEX_Z, z))
    f += box(cell_x[0] + 16 - 3, cell_x[0] + 16 + 3, y0, y1, FLEX_Z, Z_ROW["hi"])
    f += box(64.0, 69.0, y0, y1, FLEX_Z, 152.0)
    f += box(64.0, FLEX_TAIL_X[1], y0, y1, 150.0, 156.0)
    f += box(FLEX_TAIL_X[0], FLEX_TAIL_X[1], y0, y1, 150.0, Z_T1TOP + 0.35)
    f += box(FLEX_TAIL_X[0], FLEX_TAIL_X[1], 20.0, y1, Z_T1TOP + 0.05, Z_T1TOP + 0.35)
    f += box(FLEX_TAIL_X[0], 92.0, 20.0, 26.0, Z_T1TOP + 0.05, Z_T1TOP + 0.35)
    f += box(86.0, 92.0, 20.0, 26.0, Z_T1TOP + 0.05, Z_CB - 3.0)
    return f

# ======================= decks =======================
CHG_X0 = -136.0; CHG_X1 = CHG_X0 + CHG[0]
INV_X0 = -136.0; INV_X1 = INV_X0 + INV[0]
CB_X0, CB_X1, CB_W = 78.0, 138.0, 150.0
CB_T = 1.6
CB_TOP = Z_CB + CB_T
TRAY1_X0, TRAY1_X1 = -137.0, 140.0
TRAY1_Y, TRAY1_FL = 85.0, 12.0
INV_POST_XY = [(x, s * 73.0) for x in (-128.0, 42.0) for s in (-1, 1)]
CB_SO_XY = [(x, s * 68.0) for x in (CB_X0 + 5, CB_X1 - 5) for s in (-1, 1)]
CHG_SCREW_XY = [(x, y) for x in (CHG_X0 + 15, CHG_X1 - 15) for y in (-CHG[1] / 2 + 15, CHG[1] / 2 - 15)]
INV_SCREW_XY = [(x, y) for x in ((INV_X0 + INV_X1) / 2 - 87.3, (INV_X0 + INV_X1) / 2 + 87.3) for y in (-44.3, 44.3)]

TRAY1_CUTS = [  # (x0, x1, y0, y1): strap + flex pass-through slot on the busbar side
    (FLEX_TAIL_X[0] - 1.5, POS_RISER[1] + 1.5, Y_BB0 - 1.5, Y_BB1 + 2.0)]

def tray1():
    t = box(TRAY1_X0, TRAY1_X1, -TRAY1_Y, TRAY1_Y, Z_TRAY1, Z_T1TOP)
    for s in (-1, 1):
        y0, y1 = sorted((s * TRAY1_Y, s * (TRAY1_Y - T)))
        t += box(TRAY1_X0, TRAY1_X1, y0, y1, Z_TRAY1 - TRAY1_FL, Z_TRAY1)
    for (x0, x1, y0, y1) in TRAY1_CUTS:
        t -= box(x0, x1, y0, y1, Z_TRAY1 - 1, Z_T1TOP + 1)
    for x in ep_x:
        for y in (-TRAY_SCREW_Y, TRAY_SCREW_Y):
            t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.2)
    for (x, y) in CB_SO_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 4.22 / 2)          # SO-M3 mounting hole
    for (x, y) in INV_POST_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 4.0 / 2)           # FH-M4 mounting hole
    for (x, y) in CHG_SCREW_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.25)
    return t

def mylar():
    m = box(-STACK_L / 2 - 6, STACK_L / 2 + 6, FRAME_Y0, FRAME_Y1, Z_TRAY1 - MYLAR, Z_TRAY1)
    for (x0, x1, y0, y1) in TRAY1_CUTS:
        m -= box(x0 - 2, x1 + 2, y0 - 2, y1 + 2, Z_TRAY1 - 1, Z_TRAY1 + 1)
    for (x, y) in [(x, y) for x in ep_x for y in (-TRAY_SCREW_Y, TRAY_SCREW_Y)] + CB_SO_XY + INV_POST_XY + CHG_SCREW_XY:
        m -= cyl_z(x, y, Z_TRAY1 - 1, Z_TRAY1 + 1, 4.6)
    return m

def tray2():
    t = box(INV_X0 - 1, INV_X1 + 4, -79, 79, Z_TRAY2, Z_T2TOP)
    for (x, y) in INV_POST_XY:
        t -= cyl_z(x, y, Z_TRAY2 - 1, Z_T2TOP + 1, 2.2)
    for (x, y) in INV_SCREW_XY:
        t -= cyl_z(x, y, Z_TRAY2 - 1, Z_T2TOP + 1, 1.7)
    return t

def posts():
    return Compound([Pos(x, y, Z_T1TOP) * extrude(RegularPolygon(8 / math.sqrt(3), 6), Z_TRAY2 - Z_T1TOP) for (x, y) in INV_POST_XY])

def pem_tray1():
    out = []
    for (x, y) in CB_SO_XY:
        out.append(cyl_z(x, y, Z_TRAY1, Z_CB, 2.6) - cyl_z(x, y, Z_TRAY1 - 1, Z_CB + 1, 1.25))
    for (x, y) in INV_POST_XY:
        out.append(cyl_z(x, y, Z_TRAY1 - 0.9, Z_TRAY1, 3.4) + cyl_z(x, y, Z_TRAY1, Z_T1TOP + 10.0, 1.95))
    return Compound(out)

def tray_screws():
    out = []
    for x in ep_x:
        for y in (-TRAY_SCREW_Y, TRAY_SCREW_Y):
            out.append(cyl_z(x, y, Z_T1TOP, Z_T1TOP + 2.2, 3.8) + cyl_z(x, y, EP_TOP - 12, Z_T1TOP, 1.95))
    for (x, y) in INV_POST_XY:
        out.append(cyl_z(x, y, Z_T2TOP, Z_T2TOP + 2.2, 3.8) + cyl_z(x, y, Z_T2TOP - 8, Z_T2TOP, 1.95))
    for (x, y) in CB_SO_XY:
        out.append(cyl_z(x, y, CB_TOP, CB_TOP + 2.0, 2.8) + cyl_z(x, y, CB_TOP - 5, CB_TOP, 1.45))
    for (x, y) in CHG_SCREW_XY:
        out.append(cyl_z(x, y, Z_TRAY1 - 2.2, Z_TRAY1, 3.8) + cyl_z(x, y, Z_TRAY1, Z_T1TOP + 6, 1.95))
    for (x, y) in INV_SCREW_XY:
        out.append(cyl_z(x, y, Z_TRAY2 - 2.0, Z_TRAY2, 2.8) + cyl_z(x, y, Z_TRAY2, Z_T2TOP + 5, 1.45))
    return Compound(out)

def charger():
    b = box(CHG_X0, CHG_X1, -CHG[1] / 2, CHG[1] / 2, Z_T1TOP, Z_T1TOP + CHG[2])
    b -= box(CHG_X0 - 1, CHG_X0 + 2, -25, 25, Z_T1TOP + 10, Z_T1TOP + 45)
    return b

def inverter():
    b = box(INV_X0, INV_X1, -INV[1] / 2, INV[1] / 2, Z_T2TOP, Z_T2TOP + INV[2])
    b -= box(INV_X0 - 1, INV_X0 + 2, -20, 20, Z_T2TOP + 6, Z_T2TOP + 26)
    return b

def control_board():
    pcb = box(CB_X0, CB_X1, -CB_W / 2, CB_W / 2, Z_CB, CB_TOP)
    for (x, y) in CB_SO_XY:
        pcb -= cyl_z(x, y, Z_CB - 1, CB_TOP + 1, 1.7)
    t = CB_TOP
    comps = {
        "terminals": box(78.5, 82, -60, -14, t, t + 8),
        "contactor": box(98, 138, -30, 15, t, t + 40),
        "fuse": box(83, 97, -10, 30, t, t + 25),
        "shunt": box(83, 97, -62, -22, t, t + 10),
        "precharge": box(112, 130, 28, 44, t, t + 16),
        "afe_bq76952": box(100, 110, 18, 28, t, t + 1.2),
        "esp32": box(115, 132, -64, -46, t, t + 3.2),
        "led_conn": box(133, 138, 52, 64, t, t + 6),
        "buckboost_12v": box(118, 130, 47, 57, t, t + 4),
        "fan_conn": box(132, 138, 30, 38, t, t + 6),
        "ccs_conn": box(84, 96, 20, 32, Z_CB - 3, Z_CB),
    }
    return pcb, comps

def fan():
    x0 = XR
    y, z = FAN_YZ
    xc = x0 + FAN[1] / 2
    f = Pos(xc, y, z) * Box(FAN[1], FAN[0], FAN[0])
    f -= cyl_x(x0 - 1, x0 + FAN[1] + 1, y, z, 67.5)
    f += cyl_x(x0 + 0.5, x0 + FAN[1] - 0.5, y, z, 20)
    for a in range(7):
        f += Pos(xc, y, z) * Rot(a * 360 / 7, 0, 0) * Pos(0, 0, 44) * Rot(0, 0, 25) * Box(3, 18, 47)
    for (yy, zz) in FAN_SCREW_YZ:
        f -= cyl_x(x0 - 1, x0 + FAN[1] + 1, yy, zz, 2.25)
        f -= Pos(xc, yy, zz) * Box(FAN[1] - 8, 11, 11)
    return f

# lid connectors: name: (x, y, sx, sy, depth below lid)
CONNS = {
    "outlet_nema515": (70.0, -35.0, 38.0, 30.0, 30.0),
    "inlet_iec_c14": (72.0, 35.0, 27.0, 20.0, 25.0),
    "dc_anderson": (118.0, -38.0, 28.0, 36.0, 36.0),
    "can_m12": (118.0, 35.0, 16.0, 16.0, 20.0),
}
CONN_HOLE = 7.5                                  # clinch-nut hole centre beyond the cutout edge (SCS edge rule)

def lid_connectors():
    out = {}
    for n, (x, y, sx, sy, d) in CONNS.items():
        body = box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, H - T - d, H + 6)
        flange = box(x - sx / 2 - 3, x + sx / 2 + 3, y - sy / 2 - CONN_HOLE - 3, y + sy / 2 + CONN_HOLE + 3, H, H + 2)
        out[n] = body + flange
    return out

def pem_lid_panel():
    out = []
    for n, (x, y, sx, sy, d) in CONNS.items():
        for s in (-1, 1):
            yy = y + s * (sy / 2 + CONN_HOLE)
            out.append(cyl_z(x, yy, H - T - 2.0, H - T, 2.6) - cyl_z(x, yy, H - T - 3, H + 1, 1.25))
    return Compound(out)

def panel_screws():
    out = []
    for n, (x, y, sx, sy, d) in CONNS.items():
        for s in (-1, 1):
            yy = y + s * (sy / 2 + CONN_HOLE)
            out.append(cyl_z(x, yy, H + 2, H + 3.4, 2.2) + cyl_z(x, yy, H - T - 2.5, H + 2, 1.25))
    return Compound(out)

# ---- cables (routing envelopes) ----
def cable(points, r):
    segs = []
    for a, b in zip(points[:-1], points[1:]):
        va, vb = Vector(*a), Vector(*b)
        d = vb - va
        if d.length < 1e-6:
            continue
        segs.append(Solid.make_cylinder(r, d.length, Plane(origin=va, z_dir=d)))
    for p in points[1:-1]:
        segs.append(Pos(*p) * Sphere(r))
    out = segs[0]
    for s in segs[1:]:
        out = out + s
    return out

CH_X = 73.5
def cables():
    zc = Z_T1TOP + 20
    o_x, o_y, *_ = CONNS["outlet_nema515"]; i_x, i_y, *_ = CONNS["inlet_iec_c14"]
    d_x, d_y, _, _, d_d = CONNS["dc_anderson"]; c_x, c_y, _, _, c_d = CONNS["can_m12"]
    zt2 = Z_T2TOP + INV[2] / 2
    tb = CB_TOP + 6
    return {
        "ac_out": cable([(INV_X1, -30, zt2), (60, -30, zt2), (60, o_y, H - T - 30), (o_x, o_y, H - T - 30)], 3.5),
        "ac_in": cable([(i_x, i_y, H - T - 25), (CH_X, i_y, H - T - 25), (CH_X, 45, zc + 15), (CHG_X1, 45, zc + 15)], 3.5),
        "chg_dc_pos": cable([(CHG_X1, -40, zc), (CH_X, -40, zc), (CH_X, -40, tb), (79, -40, tb)], 3.2),
        "chg_dc_neg": cable([(CHG_X1, -52, zc), (CH_X, -52, zc), (CH_X, -52, tb), (79, -52, tb)], 3.2),
        "inv_dc_pos": cable([(INV_X1, 10, zt2), (CH_X, 10, zt2), (CH_X, 10, tb), (79, 10, tb)], 4.3),
        "inv_dc_neg": cable([(INV_X1, 26, zt2), (CH_X, 26, zt2), (CH_X, 26, tb), (79, 26, tb)], 4.3),
        "dc_out": cable([(d_x, d_y, H - T - d_d), (d_x, d_y, Z_T2TOP + 5), (CH_X + 4, d_y, Z_T2TOP + 5), (CH_X + 4, -28, Z_T2TOP + 5), (CH_X + 4, -28, tb), (79, -28, tb)], 4.3),
        "can": cable([(c_x, c_y, H - T - c_d), (c_x, c_y, CB_TOP + 20), (126, 47, CB_TOP + 4)], 1.8),
        "led_front": cable([(136, 58, CB_TOP + 3), (XF - 4.8, 58, CB_TOP + 3), (XF - 4.8, 58, CB_TOP + 14)], 1.5),
        "fan": cable([(XR + FAN[1] - 1, 62, Z_T1TOP + 5), (XR + FAN[1] + 4, 78, Z_T1TOP + 5), (134, 78, Z_T1TOP + 5),
                      (134, 78, CB_TOP + 14), (134, 34, CB_TOP + 14), (134, 34, CB_TOP + 6)], 1.5),
    }

# ======================= assemble =======================
def build():
    p = {}
    p["body_half_A"] = body_half(-1)
    p["body_half_B"] = body_half(+1)
    p["lid"] = lid()
    p["plate_front"] = plate(True)
    p["plate_rear"] = plate(False)
    p["screws_f"] = plate_screws(True)
    p["screws_r"] = plate_screws(False)
    p["screws_fan"] = fan_screws()
    p["screws_lid"] = lid_screws()
    p["pem_body_lid"] = pem_body_lid()
    p["feet"] = feet()
    p["diffuser_f"] = diffuser()
    p["ledboard_f"] = led_board()
    p["pipe_f"] = light_pipe()
    for i, c in enumerate(cells()):
        p[f"cell_{i+1}"] = c
    p["g10_spacers"] = spacers()
    ep, nuts = module_endplates()
    p["module_endplates"] = ep
    p["tnuts"] = nuts
    r, rn = rods()
    p["rods"] = r
    p["rodnuts"] = rn
    p["g10_floor"] = g10_floor()
    p["g10_frame_bot"] = g10_frame(Z_CELL)
    p["g10_frame_top"] = g10_frame(Z_TFRAME)
    p["screws_hold"] = holddown_screws()
    for k, v in busbars().items():
        p[f"bus_{k}"] = v
    ps, ng = pack_straps()
    p["bus_pack_pos"] = ps
    p["bus_pack_neg"] = ng
    p["screws_term"] = terminal_screws()
    p["screws_strap"] = strap_screws()
    p["flex_ccs"] = sense_flex()
    p["tray1"] = tray1()
    p["mylar_tray1"] = mylar()
    p["tray2"] = tray2()
    p["inv_posts"] = posts()
    p["pem_tray1"] = pem_tray1()
    p["screws_trays"] = tray_screws()
    p["charger_npb450_12"] = charger()
    p["inverter_nts400p_112"] = inverter()
    pcb, comps = control_board()
    p["ctrl_pcb"] = pcb
    for k, v in comps.items():
        p[f"ctrl_{k}"] = v
    p["fan_nfa14"] = fan()
    for k, v in lid_connectors().items():
        p[f"panel_{k}"] = v
    p["pem_lid_panel"] = pem_lid_panel()
    p["screws_panel"] = panel_screws()
    for k, v in cables().items():
        p[f"cable_{k}"] = v
    return p

def led_count():
    return len(front_holes())

if __name__ == "__main__":
    print(f"STACK_L {STACK_L:.2f}  H {H:.2f}  W {W}  WL {WL:.2f}  SEAM_Z {SEAM_Z:.2f}  WALL_TOP {WALL_TOP:.2f}  CNR {CNR:.2f}")
    print(f"Z_TRAY1 {Z_TRAY1:.2f} Z_TRAY2 {Z_TRAY2:.2f}  Z_CB {Z_CB:.2f}  EP_TOP {EP_TOP:.2f}  LEDs {led_count()}  fan z {FAN_YZ[1]:.2f}  top row z {node(ROWS_F-1,0)[1]:.2f}")
