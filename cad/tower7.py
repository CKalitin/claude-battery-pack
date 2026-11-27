"""Claude battery pack v7 (baseline): 4S1P EVE LF105 upright, busbars on top, every fabricated part made by SendCutSend.
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

# ======================= cell: EVE LF105 (spec ver F: 130.3 W x 36.7 T x 200.5 total / 195.5 body, poles 67.0, 1980 g) =======================
N = 4
CELL_T, CELL_W, CELL_BODY, CELL_TOT = 36.7, 130.3, 195.5, 200.5
TERM_H = CELL_TOT - CELL_BODY        # 2.8
TERM_OFF = 67.0 / 2                  # 33.5
TERM_D = 18.0                        # pad dia: PLACEHOLDER (not in spec)
TERM_THREAD_R = 3.0                  # M6 (seller listing)
FLEX_Y = -21.0                  # M6 assumed (not in spec)
PITCH_C = CELL_T + G10_SPACER
STACK_L = N * CELL_T + (N + 1) * G10_SPACER + 2 * EP_T
cell_x = [(k - (N - 1) / 2) * PITCH_C for k in range(N)]
ep_x = [-(STACK_L / 2 - EP_T / 2), STACK_L / 2 - EP_T / 2]
spacer_x = [cell_x[0] - PITCH_C / 2 + k * PITCH_C for k in range(N + 1)]
EP_W = 158.0
ROD_Y, ROD_D = 72.0, 5.0

# ======================= vertical stack =======================
Z_FLOOR = T
Z_CELL = Z_FLOOR + G10_FLOOR                     # cells & end plates stand on the G10 floor
Z_CBODY = Z_CELL + CELL_BODY                     # can top
Z_TERM = Z_CELL + CELL_TOT                       # terminal face
Z_G10TOP = Z_CBODY                               # G10 top plate sits on the cans
Z_BB = Z_TERM                                    # busbars on terminals
EP_TOP = Z_CBODY - 10.0                          # 10 mm lower standoff -> top plate underside
ROD_Z = [Z_CELL + 22.0, Z_CELL + 88.0]
SO_UP = 15.0                                     # upper M-F standoff length
Z_TRAY1 = Z_G10TOP + G10_TOP + SO_UP
Z_T1TOP = Z_TRAY1 + T
CHG = (205.0, 135.0, 55.0)                       # MEAN WELL NPB-450-12 (same case as -24: ASSUMED)
INV = (186.0, 100.5, 34.0)                       # MEAN WELL NTS-400P-112 (same case as -124: ASSUMED)
Z_TRAY2 = Z_T1TOP + CHG[2] + 1.8
Z_T2TOP = Z_TRAY2 + T
H = Z_T2TOP + INV[2] + 3.4                       # lid outer top
W = 190.0                                        # body outer width (v4 width)

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
ROWS_F = 32
ROWS_R = 34
HOLE_D = 4.8
SCREW_CLR = 4.5
def node(k, j):                                  # row k counted from the bottom, col j
    return GRID_Y0 + j * PITCH, ZB + k * PITCH
MID_K = 15
SCREW_KJ = [(0, 0), (0, COLS - 1), (0, (COLS - 1) // 2), (MID_K, 0), (MID_K, COLS - 1), (ROWS_F - 1, 0), (ROWS_F - 1, COLS - 1)]
SCREW_YZ = [node(k, j) for (k, j) in SCREW_KJ]
FAN = (140.0, 25.0)
FAN_K = 25
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
SO_Y = 60.0

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
        p = box(x - EP_T / 2, x + EP_T / 2, -EP_W / 2, EP_W / 2, Z_CELL, EP_TOP)
        for y in (-ROD_Y, ROD_Y):
            for z in ROD_Z:
                p -= cyl_x(x - 5, x + 5, y, z, ROD_D / 2 + 0.25)
        for y in (-HOLD_Y, HOLD_Y):
            c, n = tslot(x, y, Z_CELL, +1); p -= c; nuts.append(n)
        for y in (-SO_Y, SO_Y):
            c, n = tslot(x, y, EP_TOP, -1); p -= c; nuts.append(n)
        eps.append(p)
    return Compound(eps), Compound(nuts)

def rods():
    L = STACK_L + 12.0
    r, n = [], []
    for y in (-ROD_Y, ROD_Y):
        for z in ROD_Z:
            r.append(cyl_x(-L / 2, L / 2, y, z, ROD_D / 2))
            for s in (-1, 1):
                x0 = s * STACK_L / 2
                n.append(cyl_x(x0, x0 + s * 4.0, y, z, 4.6) - cyl_x(x0 - 1, x0 + s * 5, y, z, ROD_D / 2))
    return Compound(r), Compound(n)

def cell_pos_y(k):
    """+ terminal y of cell k. Chain: pack+ = cell 3 (front), pack- = cell 0 (rear), both on +y."""
    return TERM_OFF if k % 2 == 1 else -TERM_OFF

def cells():
    out = []
    for k, x in enumerate(cell_x):
        b = box(x - CELL_T / 2, x + CELL_T / 2, -CELL_W / 2, CELL_W / 2, Z_CELL, Z_CBODY)
        for y in (-TERM_OFF, TERM_OFF):
            b += cyl_z(x, y, Z_CBODY, Z_TERM, TERM_D / 2)
        out.append(b)
    return out

def spacers():
    return Compound([box(x - G10_SPACER / 2, x + G10_SPACER / 2, -CELL_W / 2, CELL_W / 2, Z_CELL, Z_CBODY) for x in spacer_x])

def g10_floor():
    f = box(-STACK_L / 2 - 0.5, STACK_L / 2 + 0.5, -72.0, 72.0, Z_FLOOR, Z_CELL)
    for x in ep_x:
        for y in (-HOLD_Y, HOLD_Y):
            f -= cyl_z(x, y, Z_FLOOR - 1, Z_CELL + 1, 2.25)
    return f

def g10_frame():
    z0 = Z_CELL
    xo, yo = STACK_L / 2 + 6.0, EP_W / 2 + 3.0      # 82: clears the floor facets (W 190)
    f = box(-xo, xo, -yo, yo, z0, z0 + G10_FRAME)
    xi = STACK_L / 2 - EP_T
    f -= box(-xi, xi, -(CELL_W / 2 + 0.3), CELL_W / 2 + 0.3, z0 - 1, z0 + G10_FRAME + 1)
    for sx in (-1, 1):
        a, b = sorted((sx * (xi - 0.3), sx * (STACK_L / 2 + 0.3)))
        f -= box(a, b, -(EP_W / 2 + 0.3), EP_W / 2 + 0.3, z0 - 1, z0 + G10_FRAME + 1)
    return f

def g10_top():
    z0 = Z_G10TOP
    t = box(-STACK_L / 2 - 1.0, STACK_L / 2 + 1.0, -70.0, 70.0, z0, z0 + G10_TOP)
    for x in cell_x:
        for y in (-TERM_OFF, TERM_OFF):
            t -= cyl_z(x, y, z0 - 1, z0 + G10_TOP + 1, TERM_D / 2 + 0.3)
        t -= box(x - 6, x + 6, -12, 12, z0 - 1, z0 + G10_TOP + 1)          # vent window (vent between the poles)
    for x in ep_x:
        for y in (-SO_Y, SO_Y):
            t -= cyl_z(x, y, z0 - 1, z0 + G10_TOP + 1, 2.2)
    return t

def standoffs():
    """Lower M4 M-F 10 mm (end plate -> top plate), upper M4 M-F 15 mm (top plate -> tray 1). Hex 7 AF."""
    lo, up, stud = [], [], []
    for x in ep_x:
        for y in (-SO_Y, SO_Y):
            lo.append(Pos(x, y, EP_TOP) * extrude(RegularPolygon(7 / math.sqrt(3), 6), Z_G10TOP - EP_TOP))
            stud.append(cyl_z(x, y, EP_TOP - 10.5, EP_TOP, 1.95))
            up.append(Pos(x, y, Z_G10TOP + G10_TOP) * extrude(RegularPolygon(7 / math.sqrt(3), 6), Z_TRAY1 - Z_G10TOP - G10_TOP)
                      + cyl_z(x, y, Z_G10TOP - 6.0, Z_G10TOP + G10_TOP, 1.95))
    return Compound(lo), Compound(up), Compound(stud)

def holddown_screws():
    out = []
    for x in ep_x:
        for y in (-HOLD_Y, HOLD_Y):
            out.append(cyl_z(x, y, -2.2, 0, 3.8) + cyl_z(x, y, 0, Z_CELL + 9.5, 1.95))
    return Compound(out)

# ---- busbars, C110 copper .125 ----
BB_W = 25.0
def bar_holes(b, pts):
    for (x, y) in pts:
        b -= cyl_z(x, y, Z_BB - 1, Z_BB + CU + 1, 3.3)
    return b

def busbars():
    out = {}
    links = [(3, 2), (2, 1), (1, 0)]                  # (k-, k-1 +)
    for i, (a, b) in enumerate(links):
        y = -cell_pos_y(a)                            # cell a's - terminal
        x0, x1 = cell_x[b], cell_x[a]
        bar = box(x0 - BB_W / 2, x1 + BB_W / 2, y - BB_W / 2, y + BB_W / 2, Z_BB, Z_BB + CU)
        out[f"link_{i+1}"] = bar_holes(bar, [(x0, y), (x1, y)])
    return out

POS_RISER_X = 99.0
RET_Y0, RET_Y1 = 66.0, 80.0
RET_RISER_X = 120.0
Z_CB = Z_T1TOP + 6.0                             # SCS shortest M3 flush standoff .236"
def pack_straps():
    """pack+ : cell 3 + terminal -> riser up to the control board (1 bend).
       pack- : cell 0 - terminal -> flat run along +y edge to the front -> riser up (1 bend). Both .125 copper."""
    yp = cell_pos_y(3)
    xp = cell_x[3]
    pos = box(xp - BB_W / 2, POS_RISER_X + CU, yp - BB_W / 2, yp + BB_W / 2, Z_BB, Z_BB + CU)
    pos += box(POS_RISER_X, POS_RISER_X + CU, yp - BB_W / 2, yp + BB_W / 2, Z_BB + CU, Z_CB)
    pos = bar_holes(pos, [(xp, yp)])
    yn = -cell_pos_y(0)
    xn = cell_x[0]
    neg = box(xn - BB_W / 2, xn + BB_W / 2, yn - BB_W / 2, RET_Y1, Z_BB, Z_BB + CU)
    neg += box(xn - BB_W / 2, RET_RISER_X + CU, RET_Y0, RET_Y1, Z_BB, Z_BB + CU)
    neg += box(RET_RISER_X, RET_RISER_X + CU, RET_Y0, RET_Y1, Z_BB + CU, Z_CB)
    neg = bar_holes(neg, [(xn, yn)])
    return pos, neg

def terminal_screws():
    out = []
    zt = Z_BB + CU
    for x in cell_x:
        for y in (-TERM_OFF, TERM_OFF):
            out.append(cyl_z(x, y, zt, zt + 4.0, 6.0) + cyl_z(x, y, zt - 9.0, zt, 2.95))   # M6 flange button, 8 mm thread
    return Compound(out)

def sense_flex():
    """Flex CCS (PCB fab, not SCS): spine off the vents at y -21, one tab per node, tail up through tray 1."""
    z = Z_BB + CU + 0.05
    f = box(cell_x[0] - 10, 116.0, FLEX_Y - 6, FLEX_Y + 6, z, z + 0.3)
    nodes = [((cell_x[i] + cell_x[i + 1]) / 2, -cell_pos_y(i + 1)) for i in range(N - 1)] + [(cell_x[0] - 14, TERM_OFF), (cell_x[3] - 14, TERM_OFF)]
    for (x, y) in nodes:
        f += box(x - 3, x + 3, min(FLEX_Y, y), max(FLEX_Y, y), z, z + 0.3)
    f += box(110 - 4, 110 + 4, FLEX_Y - 6, FLEX_Y + 6, z, Z_CB - 3)
    return f

# ======================= decks =======================
CHG_X0 = -136.0; CHG_X1 = CHG_X0 + CHG[0]
INV_X0 = -136.0; INV_X1 = INV_X0 + INV[0]
CB_X0, CB_X1, CB_W = 78.0, 138.0, 150.0
CB_T = 1.6
CB_TOP = Z_CB + CB_T
TRAY1_X0, TRAY1_X1 = -137.0, 140.0
TRAY1_Y, TRAY1_FL = 88.0, 12.0
INV_POST_XY = [(x, s * 73.5) for x in (-128.0, 42.0) for s in (-1, 1)]
CB_SO_XY = [(x, s * 68.0) for x in (CB_X0 + 5, CB_X1 - 5) for s in (-1, 1)]
CHG_SCREW_XY = [(x, y) for x in (CHG_X0 + 15, CHG_X1 - 15) for y in (-CHG[1] / 2 + 15, CHG[1] / 2 - 15)]
INV_SCREW_XY = [(x, y) for x in ((INV_X0 + INV_X1) / 2 - 87.3, (INV_X0 + INV_X1) / 2 + 87.3) for y in (-44.3, 44.3)]

TRAY1_CUTS = [  # (x0, x1, y0, y1): riser and flex pass-throughs
    (POS_RISER_X - 1.5, POS_RISER_X + CU + 1.5, cell_pos_y(3) - BB_W / 2 - 1, cell_pos_y(3) + BB_W / 2 + 1),
    (RET_RISER_X - 1.5, RET_RISER_X + CU + 1.5, RET_Y0 - 1, RET_Y1 + 1),
    (105.0, 115.0, FLEX_Y - 7.0, FLEX_Y + 7.0)]

def tray1():
    t = box(TRAY1_X0, TRAY1_X1, -TRAY1_Y, TRAY1_Y, Z_TRAY1, Z_T1TOP)
    for s in (-1, 1):
        y0, y1 = sorted((s * TRAY1_Y, s * (TRAY1_Y - T)))
        t += box(TRAY1_X0, TRAY1_X1, y0, y1, Z_TRAY1 - TRAY1_FL, Z_TRAY1)
    for (x0, x1, y0, y1) in TRAY1_CUTS:
        t -= box(x0, x1, y0, y1, Z_TRAY1 - 1, Z_T1TOP + 1)
    for x in ep_x:
        for y in (-SO_Y, SO_Y):
            t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.2)
    for (x, y) in CB_SO_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 4.22 / 2)          # SO-M3 mounting hole
    for (x, y) in INV_POST_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 4.0 / 2)           # FH-M4 mounting hole
    for (x, y) in CHG_SCREW_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.25)
    return t

def mylar():
    m = box(TRAY1_X0 + 2, TRAY1_X1 - 2, -(TRAY1_Y - T - 0.5), TRAY1_Y - T - 0.5, Z_TRAY1 - MYLAR, Z_TRAY1)
    for (x0, x1, y0, y1) in TRAY1_CUTS:
        m -= box(x0 - 2, x1 + 2, y0 - 2, y1 + 2, Z_TRAY1 - 1, Z_TRAY1 + 1)
    for (x, y) in [(x, y) for x in ep_x for y in (-SO_Y, SO_Y)] + CB_SO_XY + INV_POST_XY + CHG_SCREW_XY:
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
        for y in (-SO_Y, SO_Y):
            out.append(cyl_z(x, y, Z_T1TOP, Z_T1TOP + 2.2, 3.8) + cyl_z(x, y, Z_T1TOP - 8, Z_T1TOP, 1.95))
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
        "terminals": box(78.5, 82, -60, 40, t, t + 8),
        "contactor": box(98, 138, -22.5, 22.5, t, t + 45),
        "fuse": box(83, 97, 22, 62, t, t + 25),
        "shunt": box(83, 97, -62, -22, t, t + 10),
        "precharge": box(99, 117, 28, 44, t, t + 16),
        "afe_bq76952": box(120, 130, 28, 38, t, t + 1.2),
        "esp32": box(115, 132, -64, -46, t, t + 3.2),
        "led_conn": box(133, 138, 52, 64, t, t + 6),
        "buckboost_12v": box(100, 112, 47, 57, t, t + 4),
        "fan_conn": box(100, 108, 61, 67, t, t + 6),
        "ccs_conn": box(104, 116, FLEX_Y - 6, FLEX_Y + 6, Z_CB - 3, Z_CB),
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
        "ac_out": cable([(INV_X1, -30, zt2), (62, -30, zt2), (62, o_y, zt2), (o_x, o_y, H - T - 30)], 3.5),
        "ac_in": cable([(i_x, i_y, H - T - 25), (CH_X, i_y, H - T - 25), (CH_X, 45, zc + 15), (CHG_X1, 45, zc + 15)], 3.5),
        "chg_dc_pos": cable([(CHG_X1, -40, zc), (CH_X, -40, zc), (CH_X, -40, tb), (79, -40, tb)], 3.2),
        "chg_dc_neg": cable([(CHG_X1, -52, zc), (CH_X, -52, zc), (CH_X, -52, tb), (79, -52, tb)], 3.2),
        "inv_dc_pos": cable([(INV_X1, 10, zt2), (CH_X, 10, zt2), (CH_X, 10, tb), (79, 10, tb)], 4.3),
        "inv_dc_neg": cable([(INV_X1, 26, zt2), (CH_X, 26, zt2), (CH_X, 26, tb), (79, 26, tb)], 4.3),
        "dc_out": cable([(d_x, d_y, H - T - d_d), (d_x, d_y, Z_T2TOP + 5), (CH_X + 4, d_y, Z_T2TOP + 5), (CH_X + 4, -28, Z_T2TOP + 5), (CH_X + 4, -28, tb), (79, -28, tb)], 4.3),
        "can": cable([(c_x, c_y, H - T - c_d), (c_x, c_y, CB_TOP + 20), (126, 47, CB_TOP + 4)], 1.8),
        "led_front": cable([(136, 58, CB_TOP + 3), (XF - 3.5, 58, CB_TOP + 3), (XF - 3.5, 58, CB_TOP + 14)], 1.5),
        "fan": cable([(XR + FAN[1] - 1, 62, Z_T1TOP + 5), (XR + FAN[1] + 4, 95, Z_T1TOP + 5), (104, 95, Z_T1TOP + 5),
                      (104, 95, CB_TOP + 14), (104, 64, CB_TOP + 14), (104, 64, CB_TOP + 6)], 1.5),
    }

# ======================= 1S4P kit (not in the assembly; swapped in for 400 A mode) =======================
def kit_1s4p():
    """Two laminated .125 copper plates + .063 G10 insulator + 4 copper spacers. + plate contacts every + terminal, - plate every -.
       Upper plate reaches its terminals through 4 copper spacers (2 x .125 copper stacked = 6.35 mm) placed in clearance windows of the lower plate."""
    zl = Z_BB
    x0, x1 = cell_x[0] - 22, cell_x[-1] + 22
    pos_pts = [(x, cell_pos_y(k)) for k, x in enumerate(cell_x)]
    neg_pts = [(x, -cell_pos_y(k)) for k, x in enumerate(cell_x)]
    lower = box(x0, x1, -TERM_OFF - 14, TERM_OFF + 14, zl, zl + CU)
    for (x, y) in pos_pts:
        lower = lower - cyl_z(x, y, zl - 1, zl + CU + 1, 3.3)
    for (x, y) in neg_pts:
        lower = lower - cyl_z(x, y, zl - 1, zl + CU + 1, 12.0)              # windows for the upper plate's spacers
    for x in cell_x:
        lower -= box(x - 7, x + 7, -14, 14, zl - 1, zl + CU + 1)            # vents
    ins = box(x0, x1, -TERM_OFF - 14, TERM_OFF + 14, zl + CU, zl + CU + G10_TOP)
    for (x, y) in pos_pts + neg_pts:
        ins -= cyl_z(x, y, zl - 1, zl + 10, 10.0 if (x, y) in neg_pts else 7.0)
    for x in cell_x:
        ins -= box(x - 7, x + 7, -14, 14, zl - 1, zl + 10)
    zu = zl + CU + G10_TOP
    upper = box(x0, x1, -TERM_OFF - 14, TERM_OFF + 14, zu, zu + CU)
    for (x, y) in neg_pts:
        upper -= cyl_z(x, y, zu - 1, zu + CU + 1, 3.3)
    for (x, y) in pos_pts:
        upper -= cyl_z(x, y, zu - 1, zu + CU + 1, 7.0)                       # screw-head clearance over the lower plate's bolts
    for x in cell_x:
        upper -= box(x - 7, x + 7, -14, 14, zu - 1, zu + CU + 1)
    spc = Compound([cyl_z(x, y, zl, zu, 9.0) - cyl_z(x, y, zl - 1, zu + 1, 3.3) for (x, y) in neg_pts])
    return {"plate_pos_lower": lower, "insulator_g10": ins, "plate_neg_upper": upper, "spacers_cu": spc}

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
    p["g10_frame"] = g10_frame()
    p["g10_top"] = g10_top()
    lo, up, st = standoffs()
    p["so_lower"] = lo
    p["so_upper"] = up
    p["so_studs"] = st
    p["screws_hold"] = holddown_screws()
    for k, v in busbars().items():
        p[f"bus_{k}"] = v
    ps, ng = pack_straps()
    p["bus_pack_pos"] = ps
    p["bus_pack_neg"] = ng
    p["screws_term"] = terminal_screws()
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
    print(f"Z_TRAY1 {Z_TRAY1:.2f} Z_TRAY2 {Z_TRAY2:.2f}  EP_TOP {EP_TOP:.2f}  LEDs {led_count()}  fan z {FAN_YZ[1]:.2f}  top row z {node(ROWS_F-1,0)[1]:.2f}")
