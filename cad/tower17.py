"""Claude battery pack v17, option D (D39): 4S2P EVE LF105, everything above the cells inside the module footprint
(x ±156, y ±79 incl. end plates). MEAN WELL NPB-360-12TB flat on deck 1, NTS-400P-112 flat on deck 2, 40 mm fan at the
rear wall, TE F4 charger relay in the rear +y corner, power-bay strip along -y open to the lid (cad/bay17.py), BMS board
95 x 55 on a G10 bridge over the inverter, lid C14 inlet + NEMA 5-15R over the front corner. Harnesses: cad/harness17.py.
Source of truth for the layout: cad/analysis/converter_packing.py opt_D(); deviations are listed in
versions/v17-option-d/README.md.
Units mm. x = length (front +x), y = width, z = up. Module centred at x = 0. Body bottom at z = 0.

SendCutSend rules this file is built to (sendcutsend.com bending guidelines + calculator, Nov 2026):
  5052 .063: K .42, Ri .035", die .472", min formed flange .303", min flat between bends die/2 + 0.6
  copper .125: die .63", min flange .471", joggle .506"-3.75" (docs/contactor-mounting.md)
  G10 .125 designed; SCS stock out of .125 in Nov 2026 (docs/v16-bom.md) ⚠️
"""
import math
from build123d import *

IN = 25.4
C = (Align.CENTER, Align.CENTER, Align.MIN)

def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=C)

def cyl_z(x, y, z0, z1, r):
    z0, z1 = sorted((z0, z1))
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=C)

def cyl_x(x0, x1, y, z, r):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))

def cyl_y(x, y0, y1, z, r):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, abs(y1 - y0))

def hexz(x, y, z0, z1, af):
    return Pos(x, y, z0) * extrude(RegularPolygon(af / math.sqrt(3), 6), z1 - z0)

# ======================= materials =======================
T = 0.063 * IN            # 1.600  5052 sheet: body halves, lid
PT = 0.125 * IN           # 3.175  6061 front/rear plates
EP_T = 0.313 * IN         # 7.950  6061 module end plates
G10_FLOOR = 0.187 * IN    # 4.750
G10_FRAME = 0.187 * IN    # 4.750
G10_TOP = 0.010 * IN      # 0.254  Mylar cell-top sheet
G10_SPACER = 0.010 * IN   # 0.254  Mylar cell insulators
G125 = 0.125 * IN         # 3.175  deck 1, deck 2, bay plate, BMS bridge ⚠️ .125 out of stock at SCS Nov 2026
CU = 0.125 * IN           # 3.175  every copper part
ACR_DIFF = 0.118 * IN
ACR_PIPE = 0.118 * IN

K = 0.42
RI = 0.035 * IN
DIE = 0.472 * IN
MIN_FLAT_FLANGE = 0.255 * IN

# ======================= cell: EVE LF105 =======================
N = 8
CELL_T, CELL_W, CELL_BODY, CELL_TOT = 36.7, 130.3, 195.5, 200.5
TERM_OFF = 67.0 / 2
TERM_D = 18.0
PITCH_C = CELL_T + G10_SPACER
STACK_L = N * CELL_T + (N + 1) * G10_SPACER + 2 * EP_T          # 311.8
cell_x = [(k - (N - 1) / 2) * PITCH_C for k in range(N)]
ep_x = [-(STACK_L / 2 - EP_T / 2), STACK_L / 2 - EP_T / 2]
spacer_x = [cell_x[0] - PITCH_C / 2 + k * PITCH_C for k in range(N + 1)]
EP_W = 158.0
FX, FY = 156.0, 79.0                                             # footprint rule (owner-req §3)
ROD_Y, ROD_D = 72.0, 6.0

# ======================= vertical stack =======================
Z_FLOOR = T
Z_CELL = Z_FLOOR + G10_FLOOR
Z_CBODY = Z_CELL + CELL_BODY                                     # 201.85
Z_TERM = Z_CELL + CELL_TOT
Z_G10TOP = Z_CBODY
Z_BB = Z_TERM                                                    # 206.85
Z_COP = Z_BB + CU                                                # 210.0 collector / series bar top
EP_TOP = Z_CBODY - 10.0 + 0.063 * IN
ROD_Z = [6.35 + 0.207 * 185.5, 6.35 + 0.793 * 185.5]
SO_UP = 15.0
Z_DECK1 = EP_TOP + 10.0 + SO_UP                                  # deck 1 bottom 218.45
Z_D1 = Z_DECK1 + G125                                            # deck 1 top 221.62
CHG = (182.7, 96.0, 49.0)                                        # MEAN WELL NPB-360-12TB (NPB-360-SPEC 2026-07-06)
INV = (186.0, 100.5, 34.0)                                       # MEAN WELL NTS-400P-112 (SPEC 2026-03-26)
Z_D2 = Z_D1 + CHG[2] + 2.5 + G125                                # deck 2 top 276.3
Z_DECK2 = Z_D2 - G125
Z_INVT = Z_D2 + INV[2]                                           # 310.3
Z_BRIDGE = Z_INVT + 1.0                                          # BMS bridge underside 311.3
Z_BRT = Z_BRIDGE + G125
Z_BMS = Z_BRT + 3.0                                              # board underside 317.5
Z_BMST = Z_BMS + 1.6
LID_IN = 333.0                                                   # lid inside face (spec/interface.md §3)
H = LID_IN + T                                                   # lid outer top 334.6
# copper plane of the power bay (bay17): G10 bay plate on 25.0 mm nylon standoffs
Z_P0 = Z_D1 + 25.0 + G125                                        # copper plane bottom 249.8
Z_P1 = Z_P0 + CU                                                 # copper top 252.97 -> SB175 mating face Z_P1 + 89.8

# ======================= shell =======================
W = 174.0                                                        # body outer width (inside 170.8); D40
W_IN = W - 2 * T
# The rod ends stand 6 mm past each end plate (x ±161.9) and the rear wall tabs are 1.6 thick, so the plates cannot sit
# on the footprint (v17 finding): rear inner face = -156 - 7.95 (the fan spacer's thickness), front = LED zone.
FAN_SP = 0.313 * IN                                              # 7.95: 40 mm fan spacer frame, SCS 6061 .313
XR = -(FX + FAN_SP)                                              # rear plate inner face -163.95
LED_SO = 7.0                                                     # LED board standoffs on the front end plate
XL0 = STACK_L / 2 + LED_SO                                       # LED board back face 162.9
PANEL_GAP = 2.5
XD0 = XL0 + 1.6
XD1 = XD0 + ACR_DIFF
XF = XD1 + PANEL_GAP                                             # front plate inner face 170.0
L_IN = XF - XR
XM = (XF + XR) / 2
F = 8.0                                                          # facet length (v16: 15; D40: floor facets must clear the 158 end plates)
CNR = F * (math.cos(math.radians(30)) + math.cos(math.radians(60)))
A_FLAT = W / 2 - CNR
SEAM_Y = 24.0
LID_H = 42.0
SEAM_Z = H - LID_H
LID_GAP = 0.2
WL = W + 2 * (T + LID_GAP)
_D = T + LID_GAP
LIP_L = 7.7                                                      # SCS min formed flange .303"
LID_SCREW_X = [XM - 140.0, XM, XM + 140.0]
c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
WALL_TOP = H - CNR - _D * s30 + _D * (1 - c30) * c30 / s30 - 0.4     # -0.4: lip tip clears the short (8 mm) lid facet
LID_SCREW_Z = (SEAM_Z + WALL_TOP) / 2

# end plates (front/rear shell plates)
PW = W + 16.0
FOOT, HANDLE = 18.0, 52.0
PZ0, PZ1 = -FOOT, H + HANDLE
PR, LEG, ARCH_H, ARCH_R = 26.7, 40.0, 15.0, 13.3
SLOT_L, SLOT_H, SLOT_TOP = 83.3, 28.3, 15.0

# grids
PITCH = 124.5 / 16                                               # 7.78125
COLS = 21
GRID_Y0 = -(COLS - 1) / 2 * PITCH                                # -77.8
ZB = 40.0
ROWS_F = 34
ROWS_R = 36
HOLE_D = 4.8
FAN_GRID_D = 4.8                                                 # rear holes in front of the 40 mm fan (open cooling item)
SCREW_CLR = 4.5
def node(k, j):
    return GRID_Y0 + j * PITCH, ZB + k * PITCH
MID_K = 15
TOP_SCREW_K = 35                                                 # z 312.35: above the LED board and light pipe (PE lug)
SCREW_KJ = [(0, 0), (0, COLS - 1), (0, (COLS - 1) // 2), (MID_K, 0), (MID_K, COLS - 1), (TOP_SCREW_K, 0), (TOP_SCREW_K, COLS - 1)]
SCREW_YZ = [node(k, j) for (k, j) in SCREW_KJ]
PE_YZ = node(TOP_SCREW_K, COLS - 1)                              # front plate, +y top screw = chassis PE lug
FAN40 = (40.0, 20.0)
FAN_Y, FAN_Z = 10.0, Z_D2 + 1.2 + 20.0                           # fan centre (packing: y -10..30)
FAN_SCREW_YZ = [(FAN_Y + sy * 16.0, FAN_Z + sz * 16.0) for sy in (-1, 1) for sz in (-1, 1)]
FAN_R = 20.0                                                     # fan opening radius: grid holes inside it feed the fan
PIPE_Z, PIPE_SLOT = ZB + (ROWS_F - 1) * PITCH + 6.6, 3.2         # 303.4
TAB_H = 10.0
TAB_TAP = 3.3
TAB_END = abs(GRID_Y0) - 5.0

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
    top = (ROWS_F - th) // 2 + th - 1
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

PANEL_Y = 80.0                                                   # LED board / diffuser half-width (drops in past the lips)
def air_holes():
    """Checkerboard holes through diffuser + LED board. The control board left the front board in option D: no keep-outs."""
    skip = set(SCREW_KJ) | text_mask()
    h = [node(k, j) for k in range(ROWS_F) for j in range(COLS) if (k, j) not in skip and (k + j) % 2 == 1]
    return [(y, z) for (y, z) in h if abs(y) + 4.0 <= PANEL_Y]

def panel_screw_yz():
    pts = [node(k, j) for (k, j) in text_mask() if node(k, j)[1] <= 185.0]
    lo = min(p[1] for p in pts); hi = max(p[1] for p in pts)
    c = []
    for zz in (lo, hi):
        row = [p for p in pts if abs(p[1] - zz) < 1e-6]
        c += [min(row, key=lambda p: p[0]), max(row, key=lambda p: p[0])]
    return c

def rear_holes():
    """Full rear grid (owner: looks better); holes under a fan screw are dropped."""
    sk = {(round(y, 3), round(z, 3)) for (y, z) in SCREW_YZ}
    out = []
    for k in range(ROWS_R):
        for j in range(COLS):
            y, z = node(k, j)
            if (round(y, 3), round(z, 3)) in sk:
                continue
            if any(math.hypot(y - fy, z - fz) < 1.7 + HOLE_D / 2 + 1.2 for fy, fz in FAN_SCREW_YZ):
                continue
            out.append((y, z))
    return out

def fan_holes():
    return [(y, z) for (y, z) in rear_holes() if math.hypot(y - FAN_Y, z - FAN_Z) <= FAN_R]

# ======================= sheet tools =======================
def offset_polyline(pts, d):
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
    inner = offset_polyline(oml, T if inside_left else -T)
    face = Plane.YZ * Polygon(*(oml + inner[::-1]), align=None)
    return Pos(x0, 0, 0) * extrude(face, amount=x1 - x0, dir=(1, 0, 0))

def half_oml(side):
    s = side
    pts = [(SEAM_Y + (0.25 if s > 0 else -0.25), 0.0), (s * A_FLAT, 0.0), (s * (A_FLAT + F * c30), F * s30), (s * W / 2, CNR), (s * W / 2, WALL_TOP),
           (s * (W / 2 - LIP_L * s30), WALL_TOP + LIP_L * c30)]
    return pts, (s < 0)

def lid_oml():
    a = WL / 2 - CNR
    return [(-WL / 2, SEAM_Z), (-WL / 2, H - CNR), (-WL / 2 + F * s30, H - CNR + F * c30), (-a, H), (a, H),
            (WL / 2 - F * s30, H - CNR + F * c30), (WL / 2, H - CNR), (WL / 2, SEAM_Z)]

# ======================= body halves, lid =======================
def body_half(side):
    pts, _ = half_oml(side)
    b = sheet_extrude(pts, XR, XF, inside_left=(side > 0))
    for x_end in (XF, XR):
        sgn = 1 if x_end > 0 else -1
        xa, xb = sorted((x_end, x_end - sgn * T))
        for (y, z) in SCREW_YZ:
            if abs(y) < 1e-6:                                    # floor tab: half A only
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
    for x in ep_x:
        for y in (-HOLD_Y, HOLD_Y):
            if (y > SEAM_Y) == (side > 0):
                b -= cyl_z(x, y, -1, T + 1, 2.25)
    for x in LID_SCREW_X:
        b -= cyl_y(x, side * (W / 2 + 1), side * (W / 2 - T - 1), LID_SCREW_Z, 4.25 / 2)
    return b

SB_C = (-32.0, -47.0)                                            # SB175 centre (long axis along x)
SB_HOUS = (55.6, 25.4)
# lid connectors: name: (x, y, sx, sy, depth below the lid inside face, clinch-nut axis)
CONN_HOLE = 7.5
CONNS = {
    "inlet_iec_c14": (144.0, 0.0, 20.0, 27.0, 25.0, "x"),       # packing (138, 20): moved off the 5191 fuse / lid facet
    "outlet_nema515": (138.0, 44.0, 30.0, 38.0, 30.0, "x"),     # packing (138, 58)
    "pushbutton": (-120.0, -55.0, 19.0, 19.0, 30.0, "n"),
}

def conn_holes(c):
    x, y, sx, sy, d, ax = c
    if ax == "n":
        return []
    return [(x + s * (sx / 2 + CONN_HOLE), y) for s in (-1, 1)]

def lid():
    L = sheet_extrude(lid_oml(), XR + 0.5, XF - 0.5, inside_left=False)
    for cc in CONNS.values():
        x, y, sx, sy = cc[:4]
        if cc[5] == "n":
            L -= cyl_z(x, y, H - 8, H + 1, sx / 2 + 0.2)
            continue
        L -= box(x - sx / 2 - 0.5, x + sx / 2 + 0.5, y - sy / 2 - 0.5, y + sy / 2 + 0.5, H - 8, H + 1)
    L -= box(SB_C[0] - SB_HOUS[0] / 2 - 1.0, SB_C[0] + SB_HOUS[0] / 2 + 1.0, SB_C[1] - SB_HOUS[1] / 2 - 1.0, SB_C[1] + SB_HOUS[1] / 2 + 1.0, H - 8, H + 1)
    for cc in CONNS.values():
        for (xx, yy) in conn_holes(cc):
            L -= cyl_z(xx, yy, H - 8, H + 1, 4.25 / 2)
    for x in LID_SCREW_X:
        for s in (-1, 1):
            L -= cyl_y(x, s * (WL / 2 + 1), s * (WL / 2 - T - 1), LID_SCREW_Z, 3.4 / 2)
    return L

def lid_screws():
    out = []
    for x in LID_SCREW_X:
        for s in (-1, 1):
            yh = s * WL / 2
            out.append(cyl_y(x, yh, yh + s * 1.65, LID_SCREW_Z, 2.75) + cyl_y(x, yh, s * (W / 2 - T - 2.0), LID_SCREW_Z, 1.45))
    return Compound(out)

def pem_body_lid():
    out = []
    for x in LID_SCREW_X:
        for s in (-1, 1):
            yi = s * (W / 2 - T)
            out.append(cyl_y(x, yi, yi - s * 1.5, LID_SCREW_Z, 2.9) - cyl_y(x, yi + s, yi - s * 2.5, LID_SCREW_Z, 1.45))
    return Compound(out)

def lid_connectors():
    out = {}
    for n, cc in CONNS.items():
        x, y, sx, sy, d, ax = cc
        if ax == "n":
            out[n] = cyl_z(x, y, LID_IN - d, H, sx / 2) + cyl_z(x, y, H, H + 3.0, sx / 2 + 2.5)
            continue
        body = box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, LID_IN - d, H + 6)
        ex = CONN_HOLE + 3
        flange = box(x - sx / 2 - ex, x + sx / 2 + ex, y - sy / 2 - 3, y + sy / 2 + 3, H, H + 2)
        for (xx, yy) in conn_holes(cc):
            flange -= cyl_z(xx, yy, H - 1, H + 3, 1.6)
        out[n] = body + flange
    return out

def pem_lid_panel():
    out = []
    for cc in CONNS.values():
        for (xx, yy) in conn_holes(cc):
            out.append(cyl_z(xx, yy, H - T - 2.0, H - T, 2.6) - cyl_z(xx, yy, H - T - 3, H + 1, 1.25))
    return Compound(out)

def panel_screws():
    out = []
    for cc in CONNS.values():
        for (xx, yy) in conn_holes(cc):
            out.append(cyl_z(xx, yy, H + 2, H + 3.4, 2.2) + cyl_z(xx, yy, H - T - 2.5, H + 2, 1.25))
    return Compound(out)

# ======================= front / rear plates =======================
def plate(front):
    zc = (PZ0 + PZ1) / 2
    with BuildSketch(Plane.YZ) as sk:
        with Locations((0, zc)):
            RectangleRounded(PW, PZ1 - PZ0, PR)
        with Locations((0, PZ0)):
            RectangleRounded(PW - 2 * LEG, 2 * ARCH_H, ARCH_R, mode=Mode.SUBTRACT)
        with Locations((0, PZ1 - SLOT_TOP - SLOT_H / 2)):
            SlotCenterToCenter(SLOT_L - SLOT_H, SLOT_H, mode=Mode.SUBTRACT)
        if front:
            with Locations(*front_holes()):
                Circle(HOLE_D / 2, mode=Mode.SUBTRACT)
        else:
            fh = set(fan_holes())
            with Locations(*[p for p in rear_holes() if p not in fh]):
                Circle(HOLE_D / 2, mode=Mode.SUBTRACT)
            with Locations(*fan_holes()):
                Circle(FAN_GRID_D / 2, mode=Mode.SUBTRACT)
        with Locations(*SCREW_YZ):
            Circle(SCREW_CLR / 2, mode=Mode.SUBTRACT)
        if not front:
            with Locations(*FAN_SCREW_YZ):
                Circle(1.7, mode=Mode.SUBTRACT)
        if front:
            with Locations((0, PIPE_Z)):
                SlotCenterToCenter(2 * abs(GRID_Y0) - PIPE_SLOT, PIPE_SLOT, mode=Mode.SUBTRACT)
    p = extrude(sk.sketch, amount=PT)
    return p.moved(Location((XF, 0, 0))) if front else p.mirror(Plane.YZ).moved(Location((XR, 0, 0)))

def button_screw(y, z, front, shank):
    """ISO 7380 M4 button head."""
    xo = XF + PT if front else XR - PT
    s = 1 if front else -1
    head = cyl_x(xo, xo + s * 2.2, y, z, 3.8)
    head -= Pos(xo + s * 1.4, y, z) * Rot(0, 90, 0) * extrude(RegularPolygon(1.44, 6), 1.0, both=True)
    return head + cyl_x(xo, xo - s * shank, y, z, 1.65 if shank > 10 else TAB_TAP / 2)

def plate_screws(front):
    out = []
    for (y, z) in SCREW_YZ:
        if front and (y, z) == PE_YZ:
            continue
        out.append(button_screw(y, z, front, PT + T + 0.5))
    return Compound(out)

def pe_stack():
    """PE lug on the +y top front screw: longer M4, tab, star washer, ring (harness17), nut."""
    y, z = PE_YZ
    xi = XF - T                                                  # inner face of the wall tab
    screw = button_screw(y, z, True, PT + T + 7.0)
    star = cyl_x(xi - 1.0, xi, y, z, 4.5) - cyl_x(xi - 2, xi + 1, y, z, 1.7)
    nut = cyl_x(xi - 5.0, xi - 1.8, y, z, 4.0) - cyl_x(xi - 6, xi, y, z, 1.65)
    return screw, star, nut

def feet():
    out = []
    for x in (XF + PT / 2, XR - PT / 2):
        for s in (-1, 1):
            out.append(cyl_z(x, s * (PW / 2 - LEG / 2), PZ0 - 2.0, PZ0, 4.0))
    return Compound(out)

# ======================= front zone: LED board only =======================
LED_HDR_Y = -60.0
def _front_panel(x0, x1):
    p = box(x0, x1, -PANEL_Y, PANEL_Y, ZB - 4.0, PIPE_Z - ACR_PIPE / 2 - 1.0)
    for (y, z) in SCREW_YZ:
        if abs(y) < 1e-6:
            p -= box(x0 - 1, x1 + 1, -5.4, 5.4, ZB - 5, z + TAB_H / 2 + 0.4)
        else:
            p -= box(x0 - 1, x1 + 1, math.copysign(TAB_END - 0.4, y), math.copysign(PANEL_Y + 1, y), z - TAB_H / 2 - 0.4, z + TAB_H / 2 + 0.4)
    for (y, z) in air_holes():
        p -= cyl_x(x0 - 1, x1 + 1, y, z, 3.0)
    for (y, z) in panel_screw_yz():
        p -= cyl_x(x0 - 1, x1 + 1, y, z, 1.7)
    return p

def diffuser():
    return _front_panel(XD0, XD1)

def led_board():
    return _front_panel(XL0, XD0)

def led_header():
    """LED link header on the board's back, top edge, mating from above (Micro-Fit 1x3 envelope)."""
    return box(XL0 - 6.0, XL0, LED_HDR_Y - 6.0, LED_HDR_Y + 6.0, 290.0, 298.0)

def panel_mount():
    xe = ep_x[1] + EP_T / 2
    so, sc = [], []
    for (y, z) in panel_screw_yz():
        s = Pos(0, y, z) * Pos((xe + XL0) / 2, 0, 0) * Rot(0, 90, 0) * extrude(RegularPolygon(5.5 / math.sqrt(3), 6), (XL0 - xe) / 2, both=True)
        so.append(s - cyl_x(xe - 1, XL0 + 1, y, z, 1.45))
        sc.append(cyl_x(XD1, XD1 + 1.65, y, z, 2.85) + cyl_x(XD1 - 8.0, XD1, y, z, 1.45))
    return Compound(so), Compound(sc)

def antenna():
    return box(XL0 + 0.6, XL0 + 1.2, -40.0, 0.0, PIPE_Z + ACR_PIPE / 2 + 0.2, PIPE_Z + 10.0)

def light_pipe():
    return box(XF - 5.8, XF + PT - 0.2, -(abs(GRID_Y0) - 0.5), abs(GRID_Y0) - 0.5, PIPE_Z - ACR_PIPE / 2, PIPE_Z + ACR_PIPE / 2)

# ======================= module =======================
NUT_W, NUT_H = 7.0, 3.2
HOLD_Y = 40.0
SO_Y = 48.0                    # v16: 55. Moved so the deck-1 screw at the rear +y end clears the relay (y >= 53)

def tslot(x, y, z_edge, inward):
    z0, z1 = sorted((z_edge - inward * 1, z_edge + inward * 15))
    cut = box(x - 5, x + 5, y - 2.25, y + 2.25, z0, z1)
    n0, n1 = sorted((z_edge + inward * 7.0, z_edge + inward * (7.0 + NUT_H + 0.2)))
    cut += box(x - 5, x + 5, y - NUT_W / 2 - 0.15, y + NUT_W / 2 + 0.15, n0, n1)
    nut = box(x - NUT_W / 2, x + NUT_W / 2, y - NUT_W / 2, y + NUT_W / 2, n0 + 0.1, n1 - 0.1) - cyl_z(x, y, n0 - 1, n1 + 1, 2.0)
    return cut, nut

CB_SO_YZ = panel_screw_yz()

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
        for (yy, zz) in CB_SO_YZ:
            p -= cyl_x(x - EP_T / 2 - 1, x + EP_T / 2 + 1, yy, zz, 1.25)
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
                n.append(cyl_x(x0, x0 + s * 5.0, y, z, 5.8) - cyl_x(x0 - 1, x0 + s * 6, y, z, ROD_D / 2))
    return Compound(r), Compound(n)

def cell_pos_y(k):
    return TERM_OFF if (k // 2) % 2 == 0 else -TERM_OFF

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
    xo, yo = STACK_L / 2 + 6.0, EP_W / 2 + 2.4                   # y 81.4 (v16: 82): drops past the lips (inner |y| 81.76)
    f = box(-xo, xo, -yo, yo, z0, z0 + G10_FRAME)
    xi = STACK_L / 2 - EP_T
    f -= box(-xi, xi, -(CELL_W / 2 + 0.3), CELL_W / 2 + 0.3, z0 - 1, z0 + G10_FRAME + 1)
    for sx in (-1, 1):
        a, b = sorted((sx * (xi - 0.3), sx * (STACK_L / 2 + 0.3)))
        f -= box(a, b, -(EP_W / 2 + 0.3), EP_W / 2 + 0.3, z0 - 1, z0 + G10_FRAME + 1)
    return f

def g10_top():
    z0 = Z_G10TOP
    t = box(-STACK_L / 2 - 0.5, STACK_L / 2 + 0.5, -70.0, 70.0, z0, z0 + G10_TOP)
    for x in cell_x:
        for y in (-TERM_OFF, TERM_OFF):
            t -= cyl_z(x, y, z0 - 1, z0 + G10_TOP + 1, TERM_D / 2 + 0.3)
        t -= box(x - 6, x + 6, -12, 12, z0 - 1, z0 + G10_TOP + 1)
    for x in ep_x:
        for y in (-SO_Y, SO_Y):
            t -= cyl_z(x, y, z0 - 1, z0 + G10_TOP + 1, 4.5)
    return t

def standoffs():
    lo, up, stud = [], [], []
    for x in ep_x:
        for y in (-SO_Y, SO_Y):
            lo.append(hexz(x, y, EP_TOP, EP_TOP + 10.0, 7.0) - cyl_z(x, y, EP_TOP - 1, EP_TOP + 11, 1.95))
            stud.append(cyl_z(x, y, EP_TOP - 10.5, EP_TOP + 4.0, 1.95))
            up.append((hexz(x, y, EP_TOP + 10.0, Z_DECK1, 7.0) - cyl_z(x, y, Z_DECK1 - 9.0, Z_DECK1 + 1, 1.95))
                      + (cyl_z(x, y, EP_TOP + 4.0, EP_TOP + 10.0, 1.95)))
    return Compound(lo), Compound(up), Compound(stud)

def holddown_screws():
    out = []
    for x in ep_x:
        for y in (-HOLD_Y, HOLD_Y):
            out.append(cyl_z(x, y, -2.2, 0, 3.8) + cyl_z(x, y, 0, Z_CELL + 9.5, 1.95))
    return Compound(out)

BB_W = 25.0
TAP_Y = TERM_OFF - 7.5
def tap_pts():
    return [((cell_x[0] + cell_x[1]) / 2, -TAP_Y), ((cell_x[1] + cell_x[2]) / 2, TAP_Y), ((cell_x[3] + cell_x[4]) / 2, -TAP_Y),
            ((cell_x[5] + cell_x[6]) / 2, TAP_Y), ((cell_x[6] + cell_x[7]) / 2, -TAP_Y)]

def busbars():
    out = {}
    taps = tap_pts()
    for p, name in enumerate("ABC"):
        a, b = 2 * p, 2 * p + 3
        y = cell_pos_y(2 * p)
        bar = box(cell_x[a] - BB_W / 2, cell_x[b] + BB_W / 2, y - BB_W / 2, y + BB_W / 2, Z_BB, Z_COP)
        for k in range(a, b + 1):
            bar -= cyl_z(cell_x[k], y, Z_BB - 1, Z_COP + 1, 3.3)
        tx, ty = taps[p + 1]
        bar -= cyl_z(tx, ty, Z_BB - 1, Z_COP + 1, 1.25)
        out[name] = bar
    return out

def terminal_screws():
    out = []
    for x in cell_x:
        for y in (-TERM_OFF, TERM_OFF):
            out.append(cyl_z(x, y, Z_COP, Z_COP + 3.0, 4.5) + cyl_z(x, y, Z_BB - 4.0, Z_COP, 1.95))
    return Compound(out)

def tap_screws():
    out = []
    for (x, y) in tap_pts():
        zt = Z_COP + 0.3 + 1.0
        out.append(cyl_z(x, y, zt, zt + 2.0, 2.75) + cyl_z(x, y, Z_BB + 0.5, zt, 1.25))
    return Compound(out)

FLEX_Y = -17.0
FLEX_TAIL_X = (-125.5, -118.5)
BMS = (-105.0, -10.0, -15.0, 40.0)                               # board x0 x1 y0 y1 (spec/interface.md §4)
J1_Y = 24.5

def sense_flex():
    """Flex CCS (PCB fab, pcb lane): spine at y -17 along the cell tops, ring tabs on the 5 taps, tail up beside the
    charger's -y face into J1 (FPC) on the BMS board's -x edge. Envelope only: outline not designed yet."""
    z = Z_COP + 1.65
    f = box(cell_x[0] - 6, cell_x[7] - 10, FLEX_Y - 4, FLEX_Y + 4, z, z + 0.3)
    for (x, y) in tap_pts():
        f += box(x - 3, x + 3, min(FLEX_Y, y), max(FLEX_Y, y), z, z + 0.3)
        f += cyl_z(x, y, Z_COP, Z_COP + 1.3, 4.0) - cyl_z(x, y, Z_COP - 1, Z_COP + 2, 1.7)
        f += box(x - 3, x + 3, y - 3, y + 3, Z_COP + 1.3, z + 0.3) - cyl_z(x, y, Z_COP - 1, z + 1, 1.7)
    for (x, y) in tap_pts():
        f -= cyl_z(x, y, Z_COP + 1.3, z + 1, 2.8)                # screw head seat
    x0, x1 = FLEX_TAIL_X
    zt = 319.6
    f += box(x0, x1, -18.65, -17.0, z, z + 0.3)                  # jog to the tail plane
    f += box(x0, x1, -18.65, -18.35, z, zt + 0.3)                # vertical, 0.35 mm beside the charger's -y face
    f += box(x0, x1, -18.65, J1_Y + 4, zt, zt + 0.3)             # over the top, in the BMS -x plug room
    f += box(x0, BMS[0] + 1.0, J1_Y - 4, J1_Y + 4, zt, zt + 0.3)
    return f

# ======================= decks =======================
NEG_CUT = (-149.0, -114.0, -73.0, -47.0)                         # deck-1 passage for the pack- riser + flange
POS_CUT = (102.5, 135.0, -14.0, 10.0)                            # deck-1 passage: pack+ riser, flange, 5191 bolt head
CHG_X0, CHG_X1 = -126.0, -126.0 + CHG[0]
CHG_Y0, CHG_Y1 = FY - CHG[1], FY
CHG_SCREW_XY = [(x, y) for x in (CHG_X0 + 15.0, CHG_X1 - 15.0) for y in (CHG_Y0 + 8.0, CHG_Y1 - 8.0)]   # ⚠️ NPB-360 hole pattern unread
INV_X0, INV_X1 = -86.0, 100.0
INV_Y0, INV_Y1 = FY - INV[1], FY
INV_YC = (INV_Y0 + INV_Y1) / 2
INV_SCREW_XY = [(x, y) for x in ((INV_X0 + INV_X1) / 2 - 87.3, (INV_X0 + INV_X1) / 2 + 87.3) for y in (INV_YC - 44.3, INV_YC + 44.3)]
RELAY = (-156.0, -126.2, 53.2, 79.0)
RELAY_SCREW_XY = (-141.0, 66.0)
BAY_SO_XY = [(-135.0, -27.0), (-55.0, -72.0), (40.0, -72.0), (90.0, -73.0), (95.0, -25.0)]
D2_POST_XY = [(-150.0, -15.0), (-150.0, 38.0), (104.5, -20.0), (115.0, 74.0)]
BRIDGE_POST_XY = [(-109.0, -19.0), (-109.0, 40.0), (105.0, -12.0), (105.0, 40.0)]      # spec/interface.md §4; -x/-y post y -14 -> -19 (PP45)
BMS_HOLE_XY = [(-100.0, -10.0), (-100.0, 35.0), (-15.0, -10.0), (-15.0, 35.0)]
TIE_SLOTS_D1 = []

def deck1():
    t = box(-FX, FX, -FY, FY, Z_DECK1, Z_D1)
    for (x0, x1, y0, y1) in (NEG_CUT, POS_CUT):
        t -= box(x0, x1, y0, y1, Z_DECK1 - 1, Z_D1 + 1)
    t -= box(FLEX_TAIL_X[0] - 1, FLEX_TAIL_X[1] + 1, -20.5, -17.0, Z_DECK1 - 1, Z_D1 + 1)   # flex tail slot
    for x in ep_x:
        for y in (-SO_Y, SO_Y):
            t -= cyl_z(x, y, Z_DECK1 - 1, Z_D1 + 1, 2.2)
    for (x, y) in CHG_SCREW_XY:
        t -= cyl_z(x, y, Z_DECK1 - 1, Z_D1 + 1, 1.7)
    for (x, y) in BAY_SO_XY + D2_POST_XY + [RELAY_SCREW_XY]:
        t -= cyl_z(x, y, Z_DECK1 - 1, Z_D1 + 1, 2.2)
    return t

def deck2_outline():
    return [(-FX, -21.5), (-113.5, -21.5), (-113.5, -23.0), (-104.5, -23.0), (-104.5, -21.5), (98.0, -21.5), (98.0, -24.5), (109.0, -24.5), (109.0, -21.5), (108.0, -21.5), (108.0, 68.0), (121.0, 68.0), (121.0, FY), (-126.0, FY),
            (-126.0, 53.0), (-FX, 53.0)]

def deck2():
    face = Polygon(*deck2_outline(), align=None)
    t = Pos(0, 0, Z_DECK2) * extrude(face, G125)
    t -= box(FLEX_TAIL_X[0] - 1, FLEX_TAIL_X[1] + 1, -20.0, -17.0, Z_DECK2 - 1, Z_D2 + 1)
    for (x, y) in D2_POST_XY:
        t -= cyl_z(x, y, Z_DECK2 - 1, Z_D2 + 1, 2.2)
    for (x, y) in INV_SCREW_XY + BRIDGE_POST_XY:
        t -= cyl_z(x, y, Z_DECK2 - 1, Z_D2 + 1, 1.7)
    return t

def d2_posts():
    """Nylon M4 F-F hex standoffs, deck 1 -> deck 2 (51.5 mm: 50 mm catalog + 1.5 washer ⚠️)."""
    return Compound([hexz(x, y, Z_D1, Z_DECK2, 8.0) - cyl_z(x, y, Z_D1 - 1, Z_DECK2 + 1, 1.95) for (x, y) in D2_POST_XY])

def d2_screws_bottom():
    """Nylon M4 from under deck 1 into the deck-2 posts (bench)."""
    return Compound([cyl_z(x, y, Z_DECK1 - 2.4, Z_DECK1, 3.8) + cyl_z(x, y, Z_DECK1, Z_D1 + 8.0, 1.95) for (x, y) in D2_POST_XY])

def d2_screws_top():
    return Compound([cyl_z(x, y, Z_D2, Z_D2 + 2.4, 3.8) + cyl_z(x, y, Z_D2 - 10.0, Z_D2, 1.95) for (x, y) in D2_POST_XY])

def deck1_screws():
    return Compound([cyl_z(x, y, Z_D1, Z_D1 + 2.2, 3.8) + cyl_z(x, y, Z_DECK1 - 8, Z_D1, 1.95) for x in ep_x for y in (-SO_Y, SO_Y)])

def charger():
    b = box(CHG_X0, CHG_X1, CHG_Y0, CHG_Y1, Z_D1, Z_D1 + CHG[2])
    b -= box(CHG_X0 - 1, CHG_X0 + 4, 6.0, 50.0, Z_D1 + 8, Z_D1 + 30)       # DC terminal block recess (rear) ⚠️ position
    b -= box(CHG_X1 - 4, CHG_X1 + 1, 36.0, 64.0, Z_D1 + 12, Z_D1 + 36)     # C14 inlet recess (front, +y half) ⚠️ position
    for (x, y) in CHG_SCREW_XY:
        b -= cyl_z(x, y, Z_D1 - 1, Z_D1 + 5.0, 1.3)
    return b

CHG_VPOS = (CHG_X0 + 2.0, 38.0, 240.0)                           # V+ / V- screw terminals ⚠️ positions unread
CHG_VNEG = (CHG_X0 + 2.0, 18.0, 240.0)

def charger_tb():
    return {"term_chg_tb": box(CHG_X0 + 2.0, CHG_X0 + 4.0, 9.0, 47.0, 232.0, 248.0),
            "term_chg_c14": box(CHG_X1 - 4.0, CHG_X1 - 2.0, 37.0, 63.0, 235.0, 255.0)}

def charger_screws():
    return Compound([cyl_z(x, y, Z_DECK1 - 2.0, Z_DECK1, 2.8) + cyl_z(x, y, Z_DECK1, Z_D1 + 4.0, 1.3) for (x, y) in CHG_SCREW_XY])

def inverter():
    b = box(INV_X0, INV_X1, INV_Y0, INV_Y1, Z_D2, Z_INVT)
    b -= box(INV_X0 - 1, INV_X0 + 3, -14.0, 53.0, Z_D2 + 8, Z_D2 + 26)     # DC end: TB1, CN100, CN301
    b -= box(INV_X1 - 3, INV_X1 + 1, 54.0, 75.0, Z_D2 + 9, Z_D2 + 22)      # AC end: CN500
    for (x, y) in INV_SCREW_XY:
        b -= cyl_z(x, y, Z_D2 - 1, Z_D2 + 2.0, 1.3)
    return b

def inverter_screws():
    return Compound([cyl_z(x, y, Z_DECK2 - 2.0, Z_DECK2, 2.8) + cyl_z(x, y, Z_DECK2, Z_D2 + 1.8, 1.3) for (x, y) in INV_SCREW_XY])

FAN_X0 = -FX                                                     # fan inlet face (footprint edge); spacer behind it

def fan_spacer():
    """40 x 40 frame, bore 37, 4 x M3: closes the 7.95 gap so the fan draws only through the rear grid."""
    f = box(XR, FAN_X0, FAN_Y - 20, FAN_Y + 20, FAN_Z - 20, FAN_Z + 20)
    f -= cyl_x(XR - 1, FAN_X0 + 1, FAN_Y, FAN_Z, 18.5)
    for (y, z) in FAN_SCREW_YZ:
        f -= cyl_x(XR - 1, FAN_X0 + 1, y, z, 1.7)
    return f

def fan():
    x0 = FAN_X0
    f = box(x0, x0 + FAN40[1], FAN_Y - 20, FAN_Y + 20, FAN_Z - 20, FAN_Z + 20)
    f -= cyl_x(x0 - 1, x0 + FAN40[1] + 1, FAN_Y, FAN_Z, 18.5)
    f += cyl_x(x0 + 1.0, x0 + FAN40[1] - 1.0, FAN_Y, FAN_Z, 9.0)
    for a in range(5):
        f += Pos(x0 + 10, FAN_Y, FAN_Z) * Rot(a * 72, 0, 0) * Pos(0, 0, 13.4) * Rot(0, 0, 30) * Box(1.5, 8, 11)
    for (y, z) in FAN_SCREW_YZ:
        f -= cyl_x(x0 - 1, x0 + FAN40[1] + 1, y, z, 1.7)
    return f

def fan_screws():
    out = []
    for (y, z) in FAN_SCREW_YZ:
        xo = XR - PT
        out.append(cyl_x(xo - 1.65, xo, y, z, 2.85) + cyl_x(xo, FAN_X0 + FAN40[1] + 3.5, y, z, 1.45))
    return Compound(out)

def fan_nuts():
    x = FAN_X0 + FAN40[1]
    return Compound([cyl_x(x, x + 3.0, y, z, 3.1) - cyl_x(x - 1, x + 5, y, z, 1.45) for (y, z) in FAN_SCREW_YZ])

# ---- charger stop relay: TE V23134-B1052-C642 (Mini ISO, bracket) ----
RELAY_PINS = {"30": (-141.0, 59.0), "87": (-141.0, 73.0), "86": (-146.0, 66.0), "85": (-136.5, 66.0)}   # ⚠️ pin map from ISO 7588 layout, not read
def relay():
    x0, x1, y0, y1 = RELAY
    p = {}
    brk = box(x0, x1, y0, y1, Z_D1, Z_D1 + 0.8)
    brk -= cyl_z(*RELAY_SCREW_XY, Z_D1 - 1, Z_D1 + 2, 2.2)
    body = box(x0, x1, y0, y1, Z_D1 + 0.8, 262.0)
    body -= cyl_z(*RELAY_SCREW_XY, Z_D1 - 1, Z_D1 + 4.0, 4.0)
    p["relay_bracket"] = brk
    p["relay_body"] = body
    for n, (x, y) in RELAY_PINS.items():
        p[f"relay_tab_{n}"] = box(x - 3.15, x + 3.15, y - 0.4, y + 0.4, 262.0, 273.5)
    p["screws_relay"] = cyl_z(*RELAY_SCREW_XY, Z_DECK1 - 2.4, Z_DECK1, 3.8) + cyl_z(*RELAY_SCREW_XY, Z_DECK1, Z_D1 + 3.5, 1.95)
    return p

# ---- BMS bridge + board envelope (pcb lane; connectors J1-J9, spec/interface.md §4) ----
BMS_J = {   # name: (edge, position along the edge, pins, rows)
    "j2": ("-x", 9.0, 4, 2), "j3": ("-y", -89.5, 3, 1), "j4": ("+x", 25.0, 2, 1), "j5": ("+x", 10.0, 3, 1),
    "j6": ("+y", -87.0, 3, 1), "j7": ("+y", -72.0, 2, 1), "j8": ("+y", -59.0, 2, 1), "j9": ("+y", -46.0, 2, 1),
}
def jwidth(pins):
    return 3.0 * (pins - 1) + 6.9                                # Micro-Fit 3.0 single/dual row housing width

def jgeom(name):
    """-> (header box on the board, plug box outside the edge, wire exit point, outward unit vector)."""
    edge, p, pins, rows = BMS_J[name]
    w = jwidth(pins) / 2
    x0, x1, y0, y1 = BMS
    zh, zp = (Z_BMST, Z_BMST + 10.0), (Z_BMST + 0.5, Z_BMST + 9.5)
    if edge == "-x":
        return box(x0, x0 + 9, p - w, p + w, *zh), box(x0 - 12, x0, p - w, p + w, *zp), (x0 - 12, p, Z_BMST + 5.0), (-1, 0)
    if edge == "+x":
        return box(x1 - 9, x1, p - w, p + w, *zh), box(x1, x1 + 12, p - w, p + w, *zp), (x1 + 12, p, Z_BMST + 5.0), (1, 0)
    if edge == "-y":
        return box(p - w, p + w, y0, y0 + 9, *zh), box(p - w, p + w, y0 - 12, y0, *zp), (p, y0 - 12, Z_BMST + 5.0), (0, -1)
    return box(p - w, p + w, y1 - 9, y1, *zh), box(p - w, p + w, y1, y1 + 12, *zp), (p, y1 + 12, Z_BMST + 5.0), (0, 1)

ESP_UFL = (-23.0, 34.0, Z_BMST + 3.4)

def bms():
    p = {}
    br = box(-112.0, 108.0, -15.0, 43.0, Z_BRIDGE, Z_BRT) + box(-113.0, -105.0, -22.5, -15.0, Z_BRIDGE, Z_BRT)   # ear for the -y rear post
    for (x, y) in BRIDGE_POST_XY + BMS_HOLE_XY:
        br -= cyl_z(x, y, Z_BRIDGE - 1, Z_BRT + 1, 1.7)
    p["g10_bms_bridge"] = br
    p["bridge_posts"] = Compound([hexz(x, y, Z_D2, Z_BRIDGE, 6.0) - cyl_z(x, y, Z_D2 - 1, Z_BRIDGE + 1, 1.45) for (x, y) in BRIDGE_POST_XY])
    p["screws_bridge_posts_bot"] = Compound([cyl_z(x, y, Z_DECK2 - 2.0, Z_DECK2, 2.8) + cyl_z(x, y, Z_DECK2, Z_D2 + 6.0, 1.45) for (x, y) in BRIDGE_POST_XY])
    p["screws_bridge"] = Compound([cyl_z(x, y, Z_BRT, Z_BRT + 2.0, 2.8) + cyl_z(x, y, Z_BRIDGE - 6.0, Z_BRT, 1.45) for (x, y) in BRIDGE_POST_XY])
    p["bms_standoffs"] = Compound([hexz(x, y, Z_BRT, Z_BMS, 5.5) - cyl_z(x, y, Z_BRT - 1, Z_BMS + 1, 1.45) for (x, y) in BMS_HOLE_XY])
    p["screws_bms_bot"] = Compound([cyl_z(x, y, Z_BRIDGE - 0.9, Z_BRIDGE, 2.8) + cyl_z(x, y, Z_BRIDGE, Z_BRT + 1.4, 1.45) for (x, y) in BMS_HOLE_XY])
    p["screws_bms"] = Compound([cyl_z(x, y, Z_BMST, Z_BMST + 2.0, 2.8) + cyl_z(x, y, Z_BRT + 1.6, Z_BMST, 1.45) for (x, y) in BMS_HOLE_XY])
    x0, x1, y0, y1 = BMS
    pcb = box(x0, x1, y0, y1, Z_BMS, Z_BMST)
    for (x, y) in BMS_HOLE_XY:
        pcb -= cyl_z(x, y, Z_BMS - 1, Z_BMST + 1, 1.6)
    p["bms_pcb"] = pcb
    for n in BMS_J:
        p[f"bms_hdr_{n}"] = jgeom(n)[0]
    p["bms_hdr_j1"] = box(x0, x0 + 6.0, J1_Y - 7, J1_Y + 7, Z_BMST, Z_BMST + 3.0)
    p["bms_esp32"] = box(-38.0, -20.0, 14.0, 33.0, Z_BMST, Z_BMST + 3.2)
    p["bms_ac05"] = box(-68.0, -40.0, -12.0, -3.0, Z_BMST, Z_BMST + 10.0)
    p["bms_bq76952"] = box(-80.0, -71.0, 6.0, 15.0, Z_BMST, Z_BMST + 1.2)
    p["bms_power"] = box(-62.0, -44.0, 2.0, 12.0, Z_BMST, Z_BMST + 4.0)
    return p

# ======================= assemble =======================
def build(harness=True):
    import bay17
    p = {}
    p["body_half_A"] = body_half(-1)
    p["body_half_B"] = body_half(+1)
    p["lid"] = lid()
    p["plate_front"] = plate(True)
    p["plate_rear"] = plate(False)
    p["screws_front"] = plate_screws(True)
    p["screws_rear"] = plate_screws(False)
    p["screws_pe"], p["pe_star"], p["pe_nut"] = pe_stack()
    p["screws_lid"] = lid_screws()
    p["pem_body_lid"] = pem_body_lid()
    p["feet"] = feet()
    p["diffuser_f"] = diffuser()
    p["ledboard_f"] = led_board()
    p["ledboard_hdr"] = led_header()
    p["pipe_f"] = light_pipe()
    p["panel_standoffs"], p["screws_panelmount"] = panel_mount()
    p["antenna"] = antenna()
    for i, c in enumerate(cells()):
        p[f"cell_{i+1}"] = c
    p["g10_spacers"] = spacers()
    p["module_endplates"], p["tnuts"] = module_endplates()
    p["rods"], p["rodnuts"] = rods()
    p["g10_floor"] = g10_floor()
    p["g10_frame"] = g10_frame()
    p["g10_top"] = g10_top()
    p["so_lower"], p["so_upper"], p["so_studs"] = standoffs()
    p["screws_hold"] = holddown_screws()
    for k, v in busbars().items():
        p[f"bus_{k}"] = v
    p["screws_term"] = terminal_screws()
    p["screws_tap"] = tap_screws()
    p["flex_ccs"] = sense_flex()
    p["deck1"] = deck1()
    p["screws_deck1"] = deck1_screws()
    p["charger_npb360"] = charger()
    p.update(charger_tb())
    p["screws_chg"] = charger_screws()
    p.update(relay())
    p["posts_d2"] = d2_posts()
    p["screws_d2_bot"] = d2_screws_bottom()
    p["deck2"] = deck2()
    p["screws_d2_top"] = d2_screws_top()
    p["inverter_nts400p"] = inverter()
    p["screws_inv"] = inverter_screws()
    p["fan_spacer"] = fan_spacer()
    p["fan_4020"] = fan()
    p["screws_fan"] = fan_screws()
    p["nuts_fan"] = fan_nuts()
    p.update(bms())
    for k, v in lid_connectors().items():
        p[f"panel_{k}"] = v
    p["pem_lid_panel"] = pem_lid_panel()
    p["screws_panel"] = panel_screws()
    p.update(bay17.build())
    if harness:
        import harness17
        p.update(harness17.build()[0])
    return p

def led_count():
    return len(front_holes())

if __name__ == "__main__":
    print(f"STACK_L {STACK_L:.2f}  inside L {L_IN:.1f} x W {W_IN:.1f} x lid {LID_IN:.1f}  H {H:.2f}  W {W}  PW {PW}  CNR {CNR:.2f}  "
          f"WALL_TOP {WALL_TOP:.2f}  SEAM_Z {SEAM_Z:.2f}")
    print(f"outer: {XF + PT - (XR - PT):.1f} long x {PW:.1f} wide x {PZ1 - PZ0 + 2:.1f} tall incl. feet")
    print(f"front holes {len(front_holes())}, LED/diffuser air holes {len(air_holes())}, rear holes {len(rear_holes())}, in fan circle {len(fan_holes())}")
