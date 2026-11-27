"""Claude battery pack v14: 4S2P EVE LF105 (12.8 V, 210 Ah, 2.69 kWh), 500 A for 30 s / 210 A continuous. Power train in bolted copper:
Class T JJN-500 -> TE EV200 contactor; Tesla shunt low side; MRBF branches; M10 terminal risers through the lid. Controls-only board.
G10 deck 2 isolates the inverter. Checkerboard front panel for airflow; rear grille only inside the fan circle. See docs/v14-baseline.md.
Was v13: v12 + body lead-in lip (30 deg, nests the lid facet), tie rods at 0.207h/0.793h, Z (joggle) pack straps.
Was v12: 8S1P LF105 (25.6 V, 105 Ah, 2.69 kWh). Inverter stacked on the charger (v8 decks); control board flat on deck 1 in front of the stack.
Was v8 compact: 4S1P EVE LF105 upright, busbars on top, control board standing in front of the cells, 270 inside.
Every fabricated part made by SendCutSend. Module centred at x = 0; the shell and decks are placed around it.
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
CU = 0.125 * IN           # 3.175  copper busbars (series bars)
CU2 = 0.187 * IN          # 4.750  COP-187 pack straps, line bar, MRBF bar
CU3 = 0.250 * IN          # 6.350  COP-250 DC output terminal risers
G10_PWR = 0.250 * IN      # 6.350  G10 power deck under shunt + fuse
G10_DECK2 = 0.125 * IN    # 3.175  G10 deck 2 (inverter isolation)
ACR_DIFF = 0.118 * IN     # 3.000  white acrylic diffuser (SCS white comes only in .118)
ACR_PIPE = 0.118 * IN     # 3.000  clear acrylic light pipe
MYLAR = 0.010 * IN        # 0.254  Mylar sheet under tray 1

# ======================= SCS bend data, 5052 .063 =======================
K = 0.42
RI = 0.035 * IN           # 0.889 effective inner radius
DIE = 0.472 * IN          # 11.99
MIN_FLAT_FLANGE = 0.255 * IN

# ======================= cell: EVE LF105 (spec ver F: 130.3 W x 36.7 T x 200.5 total / 195.5 body, poles 67.0, 1980 g) =======================
N = 8
CELL_T, CELL_W, CELL_BODY, CELL_TOT = 36.7, 130.3, 195.5, 200.5
TERM_H = CELL_TOT - CELL_BODY        # 2.8
TERM_OFF = 67.0 / 2                  # 33.5
TERM_D = 18.0                        # pad dia: PLACEHOLDER (not in spec)
TERM_THREAD_R = 2.0                  # M4 x 6 mm deep (EVE spec rev B) -- UNCONFIRMED on delivered cells
FLEX_Y = -17.0                       # flex spine centre (between the vent window and the -y bars)
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
ROD_Z = [6.35 + 0.207 * 185.5, 6.35 + 0.793 * 185.5]   # end plate z 6.35..191.85: two-row optimum (equal hogging/sagging moment)
SO_UP = 15.0                                     # upper M-F standoff length
Z_TRAY1 = Z_G10TOP + G10_TOP + SO_UP
Z_T1TOP = Z_TRAY1 + T
CHG = (205.0, 135.0, 55.0)                       # MEAN WELL NPB-450-12
INV = (186.0, 100.5, 34.0)                       # MEAN WELL NTS-400P-112
Z_TRAY2 = Z_T1TOP + CHG[2] + 2.5                 # inverter screw heads under tray 2 clear the charger top
Z_T2TOP = Z_TRAY2 + G10_DECK2                    # deck 2 is G10 (isolates the inverter case from the chassis)
H = Z_T2TOP + INV[2] + 3.4                       # lid outer top
W = 190.0                                        # body outer width (v4 width)

# ======================= shell layout =======================
L_IN = 375.0                                     # v14: +10 mm, all at the rear (front plate unchanged) -> 37 mm charger bay
REAR_EXTRA = 10.0
DX = -(L_IN / 2 - (STACK_L / 2 + 1.0 + 25.0 + REAR_EXTRA))   # rear plate inner face = module rear - 1 mm - fan depth - extra
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
_D = T + LID_GAP
LIP_L = 10.0                                     # lead-in lip flange length (SCS min formed flange .303" = 7.7 mm)
LID_SCREW_X = [XM - 140.0, XM, XM + 140.0]

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

def air_holes():
    """Checkerboard: every other front hole passes straight through diffuser + LED board."""
    skip = set(SCREW_KJ) | text_mask()
    return [node(k, j) for k in range(ROWS_F) for j in range(COLS) if (k, j) not in skip and (k + j) % 2 == 1]

def panel_screw_yz():
    """4 panel screws hidden behind text pixels (solid metal in front), within the module end plate (z <= 185)."""
    pts = [node(k, j) for (k, j) in text_mask() if node(k, j)[1] <= 185.0]
    lo = min(p[1] for p in pts); hi = max(p[1] for p in pts)
    c = []
    for zz in (lo, hi):
        row = [p for p in pts if abs(p[1] - zz) < 1e-6]
        c += [min(row, key=lambda p: p[0]), max(row, key=lambda p: p[0])]
    return c

def rear_holes():
    """Full rear grid (owner: looks better). Cooling check (docs/v14-design-notes.md section 11): with the front checkerboard open,
    ~37 % of the fan flow still goes through the box -> ~10 K air rise at 75 W; blanking the extra holes would give ~5.5 K."""
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
WALL_TOP = H - CNR - _D * s30 + _D * (1 - c30) * c30 / s30   # where the lid's inner facet (offset by the gap) meets the wall
LID_SCREW_Z = (SEAM_Z + WALL_TOP) / 2
def half_oml(side):
    """side -1: half A (seam -> -y wall), side +1: half B (seam -> +y wall). Bottom-up."""
    s = side
    pts = [(SEAM_Y + (0.25 if s > 0 else -0.25), 0.0), (s * A_FLAT, 0.0), (s * (A_FLAT + F * c30), F * s30), (s * W / 2, CNR), (s * W / 2, WALL_TOP), (s * (W / 2 - LIP_L * s30), WALL_TOP + LIP_L * c30)]   # 30 deg lead-in lip parallel to the lid facet
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
    for cc in CONNS.values():
        x, y, sx, sy = cc[:4]
        if cc[5] == "n":
            L -= cyl_z(x, y, H - 6, H + 1, sx / 2 + 0.2)
            continue
        L -= box(x - sx / 2 - 0.5, x + sx / 2 + 0.5, y - sy / 2 - 0.5, y + sy / 2 + 0.5, H - 6, H + 1)
    for (x0, x1, y0, y1) in terminal_slots():
        L -= box(x0, x1, y0, y1, H - 6, H + 1)
        for (xx, yy) in conn_holes(cc):
            L -= cyl_z(xx, yy, H - 6, H + 1, 4.25 / 2)       # CLS-M3 holes
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
PANEL_GAP = 2.5                                   # diffuser face to front plate: room for M3 button heads
PANEL_Y = W / 2 - T - 0.5                         # fit inside the walls (v13 panel at +-97.4 clashed with the +-93.4 interior)
def _front_panel(x0, x1):
    y1 = PANEL_Y
    p = box(x0, x1, -y1, y1, ZB - 4.0, PIPE_Z - ACR_PIPE / 2 - 1.0)   # top edge under the light pipe (edge-lit from LEDs on this edge)
    for (y, z) in SCREW_YZ:
        if y == 0.0:
            p -= box(x0 - 1, x1 + 1, -5.4, 5.4, ZB - 5, z + TAB_H / 2 + 0.4)
        else:
            p -= box(x0 - 1, x1 + 1, math.copysign(TAB_END - 0.4, y), math.copysign(y1 + 1, y), z - TAB_H / 2 - 0.4, z + TAB_H / 2 + 0.4)
    for (y, z) in air_holes():
        p -= cyl_x(x0 - 1, x1 + 1, y, z, 3.0)       # Dia 6.0 vs 4.8 in the plate: +-0.6 mm stack-up tolerance
    for (y, z) in panel_screw_yz():
        p -= cyl_x(x0 - 1, x1 + 1, y, z, 1.7)
    return p

XD1 = XF - PANEL_GAP                               # diffuser front face
XD0 = XD1 - ACR_DIFF
XL0 = XD0 - 1.6                                    # LED board back face
def diffuser():
    return _front_panel(XD0, XD1)

def led_board():
    return _front_panel(XL0, XD0)

def panel_mount():
    """4 x M3 x 8 standoffs (module front end plate -> LED board) + 4 x M3 button screws through the diffuser."""
    xe = ep_x[1] + EP_T / 2
    so, sc = [], []
    for (y, z) in panel_screw_yz():
        so.append(Pos(0, y, z) * Pos((xe + XL0) / 2, 0, 0) * Rot(0, 90, 0) * extrude(RegularPolygon(5.5 / math.sqrt(3), 6), (XL0 - xe) / 2, both=True))
        sc.append(cyl_x(XD1, XD1 + 1.65, y, z, 2.85) + cyl_x(XD1 - 8.0, XD1, y, z, 1.45))
    return Compound(so), Compound(sc)

def antenna():
    """2.4 GHz adhesive flex antenna behind the light-pipe slot (slot 187 mm ~ 3 x lambda/2 radiates out of the metal box)."""
    return box(XL0 + 0.6, XL0 + 1.2, 20.0, 60.0, PIPE_Z - 1.5, PIPE_Z + 8.5)

def light_pipe():
    return box(XF - 5.8, XF + PT - 0.2, -(abs(GRID_Y0) - 0.5), abs(GRID_Y0) - 0.5, PIPE_Z - ACR_PIPE / 2, PIPE_Z + ACR_PIPE / 2)

# ======================= module =======================
NUT_W, NUT_H = 7.0, 3.2
HOLD_Y = 40.0
SO_Y = 55.0

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
        if x > 0:
            for (yy, zz) in CB_SO_YZ:                       # SCS-tapped M3 in the front end plate face (board standoffs)
                p -= cyl_x(x + EP_T / 2 - 6.0, x + EP_T / 2 + 1, yy, zz, 1.25)
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
    """+ terminal y of cell k. 4S2P: pairs (0,1)(2,3)(4,5)(6,7) alternate orientation; pack- = pair 0 (rear), pack+ = pair 3 (front), both on -y."""
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

TAP_Y = TERM_OFF - 7.5                             # flex tap: 5 mm in from the bar's inner edge (bar edge at +-21)
def tap_pts():
    """5 sense taps (VC0..VC4): pack-, A, B, C, pack+ ; mid-gap x so tabs cross between vents."""
    return [((cell_x[0] + cell_x[1]) / 2, -TAP_Y),            # VC0 pack- collector
            ((cell_x[1] + cell_x[2]) / 2, TAP_Y),             # VC1 bar A
            ((cell_x[3] + cell_x[4]) / 2, -TAP_Y),            # VC2 bar B
            ((cell_x[5] + cell_x[6]) / 2, TAP_Y),             # VC3 bar C
            ((cell_x[6] + cell_x[7]) / 2, -TAP_Y)]            # VC4 pack+ collector

def busbars():
    """3 series bars, each across 4 terminals (pair p + and pair p+1 -)."""
    out = {}
    taps = tap_pts()
    for p, name in enumerate("ABC"):
        a, b = 2 * p, 2 * p + 3
        y = cell_pos_y(2 * p)
        bar = box(cell_x[a] - BB_W / 2, cell_x[b] + BB_W / 2, y - BB_W / 2, y + BB_W / 2, Z_BB, Z_BB + CU)
        bar = bar_holes(bar, [(cell_x[k], y) for k in range(a, b + 1)])
        tx, ty = taps[p + 1]
        bar -= cyl_z(tx, ty, Z_BB - 1, Z_BB + CU + 1, 1.25)      # M3 tap drill, SCS-tapped
        out[name] = bar
    return out

RET_Y0, RET_Y1 = 62.0, 74.0
XT = cell_x[N - 1] + 16.0                        # x of the strap riser (outer face); 2 mm past the terminal screw head
FL = 20.0                                        # strap top flange (forward), SCS COP-125 min formed flange .471" = 12 mm
XH = XT - CU + FL / 2                            # M6 hole x on the flange
CB_T = 1.6
CB_SO = 6.0                                      # SCS flush standoffs (M3 x .236") pressed into tray 1
# ---- power train geometry (v14) ----
Z_PD = Z_T1TOP + G10_PWR                           # G10 power deck top (shunt + fuse sit on it)
FUSE_L, FUSE_D, FUSE_BL = 77.8, 31.8, 14.0         # JJN-500 overall 3.06", body dia 1.25"; blade length ~14 (UNCONFIRMED)
FUSE_BT, FUSE_BW = 4.8, 25.4                       # blade thickness / width (UNCONFIRMED)
FUSE_Y = -27.5                                     # fuse axis y
FUSE_X1 = XT - CU2 - 0.2                           # front blade tip, just behind the pack+ riser
FUSE_X0 = FUSE_X1 - FUSE_L
FUSE_Z = Z_PD + FUSE_D / 2                         # body rests on the G10 deck
Z_BLADE = FUSE_Z - FUSE_BT / 2                     # blade underside = top of the bars it bolts to
SH_X0, SH_L, SH_W = 61.5, 83.5, 35.0               # Tesla shunt bar (UNCONFIRMED dims)
SH_Y = -68.5                                       # bar centre line y
SH_BOLT = [SH_X0 + 15.0, SH_X0 + SH_L - 15.0]      # node B (load side), node A (cell side)
CT_X, CT_Y = 120.0, 35.0                            # EV200 centre (UNCONFIRMED outline: 66 x 81 base, ~85 tall)
CT_BASE, CT_H, CT_STUD = (66.0, 81.0), 72.3, 12.6
Z_CT = Z_T1TOP + CT_H                              # stud seat (top of contactor body)
CT_STUDS = [(CT_X, CT_Y - 26.0), (CT_X, CT_Y + 26.0)]   # line (from fuse), load (to outputs)
RET_Y0, RET_Y1 = -81.0, -56.0                      # pack- return strap band (y) over the -y cell edge

def pack_straps():
    """COP-187 Z straps. pack+: collector (cells 6,7, -y) -> riser at XT -> flange back to the fuse front blade.
    pack-: collector (cells 0,1, -y) -> return band -> riser at XT -> flange back onto the shunt node-A end."""
    zt = Z_BB + CU2
    yp = cell_pos_y(6)                              # -33.5
    pos = box(cell_x[6] - BB_W / 2, XT, yp - BB_W / 2, yp + BB_W / 2, Z_BB, zt)
    pos += box(XT - CU2, XT, yp - BB_W / 2, yp + BB_W / 2, Z_BB, Z_BLADE)
    pos += box(FUSE_X1 - FUSE_BL - 4.0, XT, FUSE_Y - FUSE_BW / 2 - 1.0, yp + BB_W / 2, Z_BLADE - CU2, Z_BLADE)
    pos = bar_holes(pos, [(cell_x[6], yp), (cell_x[7], yp)])
    pos -= cyl_z(FUSE_X1 - FUSE_BL / 2, FUSE_Y, Z_BLADE - CU2 - 1, Z_BLADE + 1, 5.25)   # M10 fuse bolt
    tx, ty = tap_pts()[4]
    pos -= cyl_z(tx, ty, Z_BB - 1, zt + 1, 1.25)
    yn = -cell_pos_y(0)                             # -33.5
    zf = Z_PD + CU                                  # shunt bar top (bar is 1/8")
    neg = box(cell_x[0] - BB_W / 2, cell_x[1] + BB_W / 2, RET_Y0, yn + BB_W / 2, Z_BB, zt)
    neg += box(cell_x[0] - BB_W / 2, XT, RET_Y0, RET_Y1, Z_BB, zt)
    neg += box(XT - CU2, XT, RET_Y0, RET_Y1, Z_BB, zf + CU2)
    neg += box(SH_BOLT[1] - 12.0, XT, RET_Y0, RET_Y1, zf, zf + CU2)
    neg = bar_holes(neg, [(cell_x[0], yn), (cell_x[1], yn)])
    neg -= cyl_z(SH_BOLT[1], SH_Y, zf - 1, zf + CU2 + 1, 4.3)     # shunt bolt (thread UNCONFIRMED, M8 placeholder)
    tx, ty = tap_pts()[0]
    neg -= cyl_z(tx, ty, Z_BB - 1, zt + 1, 1.25)
    return pos, neg

def power_train():
    """Bolted copper power path. All envelopes; UNCONFIRMED dims flagged in docs/v14-baseline.md."""
    p = {}
    # G10 power deck (insulates shunt + fuse from tray 1 / chassis)
    deck = box(61.0, 143.0, -86.0, -15.0, Z_T1TOP, Z_PD)
    deck -= box(XT - CU2 - 1.0, XT + 1.0, RET_Y0 - 1, RET_Y1 + 1, Z_T1TOP - 1, Z_PD + 1)
    for x in SH_BOLT:
        deck -= cyl_z(x, SH_Y, Z_T1TOP - 1, Z_PD + 1, 4.3)
    p["g10_power_deck"] = deck
    # Tesla shunt: bar + module PCB (overhang 8 mm to +y) + connector at the +x end + wire keepout (not a part: reported)
    zb = Z_PD
    bar = box(SH_X0, SH_X0 + SH_L, SH_Y - SH_W / 2, SH_Y + SH_W / 2, zb, zb + CU)
    for x in SH_BOLT:
        bar -= cyl_z(x, SH_Y, zb - 1, zb + CU + 1, 4.3)
    xc = SH_X0 + SH_L / 2
    pcb = box(xc - 12.5, xc + 12.5, SH_Y - SH_W / 2, SH_Y + SH_W / 2 + 8.0, zb + CU, zb + CU + 5.0)
    # owner 2026-11-24: connector sits on top of the 8 mm overhang strip, at one end (exact spot UNCONFIRMED)
    conn = box(xc + 2.0, xc + 12.5, SH_Y + SH_W / 2 - 2.5, SH_Y + SH_W / 2 + 7.5, zb + CU + 2.0, zb + CU + 7.0)
    p["shunt_bar"] = bar
    p["shunt_module"] = pcb + conn
    # Class T JJN-500, horizontal along x, body resting on the deck
    body = Pos(0, FUSE_Y, FUSE_Z) * Pos((FUSE_X0 + FUSE_X1) / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(FUSE_D / 2, FUSE_L - 2 * FUSE_BL)
    bl = box(FUSE_X0, FUSE_X0 + FUSE_BL, FUSE_Y - FUSE_BW / 2, FUSE_Y + FUSE_BW / 2, Z_BLADE, Z_BLADE + FUSE_BT)
    br = box(FUSE_X1 - FUSE_BL, FUSE_X1, FUSE_Y - FUSE_BW / 2, FUSE_Y + FUSE_BW / 2, Z_BLADE, Z_BLADE + FUSE_BT)
    p["fuse_jjn500"] = body + bl + br
    # line bar: fuse rear blade -> down the drop zone? no: up the x~60 riser -> over to the contactor line stud
    xr0, xr1 = FUSE_X0 - CU2, FUSE_X0
    yl0, yl1 = FUSE_Y - 13.0, FUSE_Y + 11.0
    line = box(xr0, FUSE_X0 + FUSE_BL + 1.0, yl0, yl1, Z_BLADE - CU2, Z_BLADE)
    line += box(xr0, xr1, yl0, yl1, Z_BLADE - CU2, Z_CT + CU2)
    line += box(xr0, CT_X - 12.5, yl0 + 15.5, yl0 + 40.5, Z_CT, Z_CT + CU2)                 # band along x
    line += box(CT_X - 12.5, CT_X + 12.5, CT_STUDS[0][1] - 12.5, CT_STUDS[0][1] + 12.5, Z_CT, Z_CT + CU2)   # stud pad
    line += box(CT_X - 12.5 - 25.0, CT_X - 12.5, yl0 + 15.5, CT_STUDS[0][1] + 12.5, Z_CT, Z_CT + CU2)  # corner
    line -= cyl_z(FUSE_X0 + FUSE_BL / 2, FUSE_Y, Z_BLADE - CU2 - 1, Z_BLADE + 1, 5.25)
    line -= cyl_z(*CT_STUDS[0], Z_CT - 1, Z_CT + CU2 + 1, 4.3)
    p["bus_line"] = line
    # EV200 contactor (on tray 1 directly; plastic body)
    bx, by = CT_BASE
    ct = box(CT_X - bx / 2, CT_X + bx / 2, CT_Y - by / 2, CT_Y + by / 2, Z_T1TOP, Z_T1TOP + 8.0)
    ct += cyl_z(CT_X, CT_Y, Z_T1TOP + 8.0, Z_CT, 30.0)
    for (x, y) in CT_STUDS:
        ct += cyl_z(x, y, Z_CT, Z_CT + CT_STUD, 4.0)
    p["contactor_ev200"] = ct
    # load bus: MRBF bar on the load stud, drop riser at x 54 with 2 MRBFs (inverter 50 A, charger 30 A)
    yl, ym0, ym1 = CT_STUDS[1][1], 36.0, 84.0
    XM0 = 86.0
    mb = box(XM0, CT_X + 12.5, ym0, ym1, Z_CT, Z_CT + CU2)
    mb += box(XM0, XM0 + CU2, ym0, ym1, Z_CT - 18.0, Z_CT + CU2)
    mb -= cyl_z(*CT_STUDS[1], Z_CT - 1, Z_CT + CU2 + 1, 4.3)
    p["bus_load"] = mb
    p["mrbf"] = Compound([box(XM0 - 8.0, XM0, yc - 11.0, yc + 11.0, Z_CT - 16.0, Z_CT + 4.0) for yc in (48.0, 72.0)])   # MRBF ~22 x 20 x 8 (UNCONFIRMED)
    # DC output terminal risers (COP-250) through lid slots; M10 hole horizontal near the top
    ztop = H + 30.0
    XTR = 62.0                                      # both terminal risers share this x plane (faces at x 62 / 68.35)
    pr = box(XTR, CT_X + 12.5, yl - 12.5, yl + 12.5, Z_CT + CU2, Z_CT + CU2 + CU3)
    pr += box(XTR, XTR + CU3, yl - 12.5, yl + 12.5, Z_CT + CU2, ztop)
    pr -= cyl_z(*CT_STUDS[1], Z_CT - 1, Z_CT + 2 * CU2 + 1, 4.3)
    pr -= cyl_x(XTR - 2, XTR + CU3 + 2, yl, ztop - 12.0, 5.25)
    p["term_pos"] = pr
    xb = SH_BOLT[0]
    nr = box(62.0, 83.5, -81.0, -46.0, zb + CU, zb + CU + CU3)
    nr += box(62.0, 62.0 + CU3, -71.0, -46.0, zb + CU, ztop)
    nr -= cyl_z(xb, SH_Y, zb - 1, zb + CU + CU3 + 1, 4.3)
    nr -= cyl_x(60, 70, -58.5, ztop - 12.0, 5.25)   # same z and x plane as the + hole
    p["term_neg"] = nr
    return p

def terminal_slots():
    yl = CT_STUDS[1][1]
    return [(62.0 - 3.0, 62.0 + CU3 + 3.0, yl - 15.5, yl + 15.5),
            (62.0 - 3.0, 62.0 + CU3 + 3.0, -74.0, -43.0)]

def terminal_plates():
    """G10 .250 insulating plates on the lid top around the terminal slots (2 x M3 each into lid clinch nuts)."""
    out = []
    for (x0, x1, y0, y1) in terminal_slots():
        pl = box(x0 - 12.0, x1 + 12.0, y0 - 6.0, y1 + 6.0, H, H + G10_PWR)
        pl -= box(x0 + 2.0, x1 - 2.0, y0 + 2.0, y1 - 2.0, H - 1, H + G10_PWR + 1)
        out.append(pl)
    return Compound(out)

def terminal_screws():
    """M4 x 8 A2 flange head (+ washer) into the M4 x 6 pole thread; collectors/straps are COP-187 so their heads sit higher."""
    out = []
    for k, x in enumerate(cell_x):
        for y in (-TERM_OFF, TERM_OFF):
            strap = (k in (0, 1) and y == -cell_pos_y(0)) or (k in (6, 7) and y == cell_pos_y(6))
            zt = Z_BB + (CU2 if strap else CU)
            out.append(cyl_z(x, y, zt, zt + 3.0, 4.5) + cyl_z(x, y, Z_BB - 4.0, zt, 1.95))
    return Compound(out)

def tap_screws():
    """M3 x 6 pan screws through the flex ring pads (+FR4 stiffener) into the SCS-tapped busbar holes."""
    out = []
    for k, (x, y) in enumerate(tap_pts()):
        zt = Z_BB + (CU2 if k in (0, 4) else CU) + 0.3 + 1.0
        out.append(cyl_z(x, y, zt, zt + 2.0, 2.75) + cyl_z(x, y, Z_BB + 0.5, zt, 1.45))
    return Compound(out)

def sense_flex():
    """Flex CCS (PCB fab): spine at y -17 (between the vent window and the -y bars), 5 S-loop tabs to ring pads (+FR4 stiffener),
    tail rises at x 146-148 through tray 1 + the power deck to the control board underside."""
    z = Z_BB + CU2 + 0.05                            # spine floats just above the thickest copper
    f = box(cell_x[0] - 6, 148.0, FLEX_Y - 4, FLEX_Y + 4, z, z + 0.3)
    for k, (x, y) in enumerate(tap_pts()):
        zr = Z_BB + (CU2 if k in (0, 4) else CU)
        f += box(x - 3, x + 3, min(FLEX_Y, y), max(FLEX_Y, y), z, z + 0.3)              # tab (S-loop not drawn)
        f += cyl_z(x, y, zr, zr + 1.3, 4.0) - cyl_z(x, y, zr - 1, zr + 2, 1.7)          # ring + stiffener
        yt = y + (-6.5 if y > FLEX_Y else 6.5)
        f += box(x - 0.8, x + 0.8, yt - 0.4, yt + 0.4, zr + 1.3, zr + 1.8)              # 0603 NTC on the clamped tab (thermal path via the screw joint)
    f += box(146.0, 148.0, FLEX_Y - 4, FLEX_Y + 4, z, CBZ0 - 4.0)
    return f

# ======================= decks =======================
DECK_SH = XR + 29.0 - (-136.0)                     # decks keep their position relative to the rear plate
CHG_X0 = XR + 43.0; CHG_X1 = CHG_X0 + CHG[0]   # v14: 18 mm from the fan face (was 10) for assembly
INV_X0 = XR + 43.0; INV_X1 = INV_X0 + INV[0]
TRAY1_X0, TRAY1_X1 = XR + 28.0, XF - 8.0          # v14: ends before the LED board (XL0)
TRAY1_Y, TRAY1_FL = 88.0, 12.0
INV_POST_XY = [(x, s * 73.5) for x in (INV_X0 + 12.0, INV_X1 - 12.0) for s in (-1, 1)]
CB_SO_YZ = panel_screw_yz()                      # SCS-tapped M3 in the module front end plate (LED panel standoffs)
CBX0, CBX1 = 82.0, 150.0                         # v14 controls-only board, above the shunt + fuse
CBY0, CBY1 = -86.0, -14.0                        # main body y; plus a tongue x 131..150 to y -2 for the flex tail
CBZ0 = Z_PD + FUSE_D + 3.8 if False else 262.0   # board underside (fuse top ~258)
CBZ1 = CBZ0 + CB_T
CB_SO_XY = [(86.25, -48.25), (125.0, -48.25), (141.0, -10.0)]   # M3 standoffs (non-plated holes: board GND is pack-)
CHG_SCREW_XY = [(x, y) for x in (CHG_X0 + 15, CHG_X1 - 15) for y in (-CHG[1] / 2 + 15, CHG[1] / 2 - 15)]
INV_SCREW_XY = [(x, y) for x in ((INV_X0 + INV_X1) / 2 - 87.3, (INV_X0 + INV_X1) / 2 + 87.3) for y in (-44.3, 44.3)]

TRAY1_CUTS = [(XT - CU2 - 1.0, XT + 1.0, -33.5 - BB_W / 2 - 1, -33.5 + BB_W / 2 + 1),   # pack+ riser
              (XT - CU2 - 1.0, XT + 1.0, RET_Y0 - 1.0, RET_Y1 + 1.0),                  # pack- riser
              (145.0, 149.0, FLEX_Y - 5.0, FLEX_Y + 5.0)]                             # flex tail

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
    for (x, y) in INV_POST_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 4.0 / 2)           # FH-M4 mounting hole
    for (x, y) in CHG_SCREW_XY:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.25)
    t -= cyl_z(CB_SO_XY[2][0], CB_SO_XY[2][1], Z_TRAY1 - 1, Z_T1TOP + 1, 1.7)   # board standoff screw
    for (x, y) in [(CT_X - 30.0, CT_Y), (CT_X + 30.0, CT_Y)]:
        t -= cyl_z(x, y, Z_TRAY1 - 1, Z_T1TOP + 1, 2.75)               # EV200 M5 body screws (UNCONFIRMED pattern)
    for x in SH_BOLT:
        t -= cyl_z(x, SH_Y, Z_TRAY1 - 1, Z_T1TOP + 1, 8.0)             # clearance for the shunt bolt heads under the G10 deck
    return t

def mylar():
    m = box(TRAY1_X0 + 2, TRAY1_X1 - 2, -(TRAY1_Y - T - 0.5), TRAY1_Y - T - 0.5, Z_TRAY1 - MYLAR, Z_TRAY1)
    for (x0, x1, y0, y1) in TRAY1_CUTS:
        m -= box(x0 - 2, x1 + 2, y0 - 2, y1 + 2, Z_TRAY1 - 1, Z_TRAY1 + 1)
    for (x, y) in [(x, y) for x in ep_x for y in (-SO_Y, SO_Y)] + INV_POST_XY + CHG_SCREW_XY + [CB_SO_XY[2]]:
        m -= cyl_z(x, y, Z_TRAY1 - 1, Z_TRAY1 + 1, 4.6)
    for x in SH_BOLT:
        m -= cyl_z(x, SH_Y, Z_TRAY1 - 1, Z_TRAY1 + 1, 9.0)
    return m

def tray2():
    """v14: G10BLACK-125 flat plate (was 5052). Isolates the inverter (DC input assumed bonded to its case)."""
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
        out.append(cyl_z(x, y, CBZ1, CBZ1 + 2.0, 2.8) + cyl_z(x, y, CBZ0 - 4.0, CBZ1, 1.45))
    for (x, y) in CHG_SCREW_XY:
        out.append(cyl_z(x, y, Z_TRAY1 - 2.2, Z_TRAY1, 3.8) + cyl_z(x, y, Z_TRAY1, Z_T1TOP + 6, 1.95))
    for (x, y) in INV_SCREW_XY:
        out.append(cyl_z(x, y, Z_TRAY2 - 2.0, Z_TRAY2, 2.8) + cyl_z(x, y, Z_TRAY2, Z_T2TOP + 1.8, 1.45))   # M3 x 5: 1.8 mm into the case (<= 2.5)
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
    """Controls only (v14). Power never touches it. Cutout for the shunt connector's vertical wire keepout."""
    pcb = box(CBX0, CBX1, CBY0, CBY1, CBZ0, CBZ1) + box(131.0, CBX1, CBY1, -2.0, CBZ0, CBZ1)
    xc = SH_X0 + SH_L / 2
    pcb -= box(xc + 1.5, xc + 13.0, SH_Y + SH_W / 2 - 4.5, SH_Y + SH_W / 2 + 9.5, CBZ0 - 1, CBZ1 + 1)   # shunt harness keepout (>= 35 mm straight up)
    for (x, y) in CB_SO_XY:
        pcb -= cyl_z(x, y, CBZ0 - 1, CBZ1 + 1, 1.7)
    def c(x0, x1, y0, y1, h):
        return box(x0, x1, y0, y1, CBZ1, CBZ1 + h)
    comps = {
        "esp32s3_1u": c(86.0, 104.0, -40.0, -20.8, 3.2),
        "bq76952": c(110.0, 119.0, -40.0, -31.0, 1.2),
        "buck_5v": c(86.0, 98.0, -84.0, -74.0, 4.0),
        "ldo_3v3": c(100.0, 106.0, -84.0, -78.0, 2.0),
        "precharge_relay": c(122.0, 142.0, -40.0, -28.0, 15.0),
        "precharge_r": c(122.0, 146.0, -26.0, -18.0, 8.0),
        "can_txu_photomos": c(108.0, 120.0, -26.0, -18.0, 2.0),
        "conn_npb_inv_fan_led_btn": c(88.0, 102.0, -64.0, -53.0, 9.0),
        "conn_shunt": c(120.0, 130.0, -84.0, -74.0, 9.0),
        "fuse_2a": c(132.0, 146.0, -84.0, -78.0, 6.0),
        "ccs_conn": box(144.0, 150.0, FLEX_Y - 6, FLEX_Y + 6, CBZ0 - 4.0, CBZ0),
    }
    return pcb, comps

def cb_standoffs():
    """M3 F-F standoffs: two on the G10 power deck, one on tray 1. Non-plated board holes (board GND = pack-)."""
    out = []
    for i, (x, y) in enumerate(CB_SO_XY):
        z0 = Z_PD if i < 2 else Z_T1TOP
        out.append(cyl_z(x, y, z0, CBZ0, 2.5) - cyl_z(x, y, z0 - 1, CBZ0 + 1, 1.25))
    return Compound(out)

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

# lid connectors: name: (x, y, sx, sy, depth below lid, clinch-nut axis)
CONN_HOLE = 7.5                                  # clinch-nut hole centre beyond the cutout edge (SCS edge rule)
CONN_XC = XF - 0.5 - 6.5 - 22.5                  # front column over the board (bodies end above the contactor)
CONNS = {
    "outlet_nema515": (CONN_XC, -56.0, 30.0, 38.0, 30.0, "x"),
    "inlet_iec_c14": (CONN_XC, -17.0, 20.0, 27.0, 25.0, "x"),
    "pushbutton": (100.0, -60.0, 19.0, 19.0, 30.0, "n"),        # 19 mm illuminated momentary, own nut (no clinch nuts)
}

def conn_holes(c):
    x, y, sx, sy, d, ax = c
    if ax == "n":
        return []
    if ax == "x":
        return [(x + s * (sx / 2 + CONN_HOLE), y) for s in (-1, 1)]
    return [(x, y + s * (sy / 2 + CONN_HOLE)) for s in (-1, 1)]

def lid_connectors():
    out = {}
    for n, cc in CONNS.items():
        x, y, sx, sy, d, ax = cc
        body = box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, H - T - d, H + 6)
        if ax == "n":
            out[n] = cyl_z(x, y, H - T - d, H, sx / 2) + cyl_z(x, y, H, H + 3.0, sx / 2 + 2.5)
            continue
        ex, ey = (CONN_HOLE + 3, 3) if ax == "x" else (3, CONN_HOLE + 3)
        flange = box(x - sx / 2 - ex, x + sx / 2 + ex, y - sy / 2 - ey, y + sy / 2 + ey, H, H + 2)
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

def cables():
    """Routing envelopes (approximate)."""
    o = CONNS["outlet_nema515"]; i_ = CONNS["inlet_iec_c14"]
    zc = Z_T1TOP + 20
    zi = Z_T2TOP + INV[2] / 2
    xd = CHG_X1 + 3.0
    return {
        "ac_out": cable([(INV_X1, -30, zi), (xd, -30, zi), (o[0] - 25, o[1], zi), (o[0], o[1], H - T - o[4])], 3.5),
        "ac_in": cable([(i_[0], i_[1], H - T - i_[4]), (i_[0] - 14, i_[1], 284.0), (xd, 45, 284.0), (xd, 45, zc), (CHG_X1, 45, zc)], 3.5),
        "chg_dc_pos": cable([(CHG_X1, 20, zc), (xd, 20, zc), (xd, 72, Z_CT - 6.0), (78.0, 72, Z_CT - 6.0)], 3.6),
        "chg_dc_neg": cable([(CHG_X1, -20, zc), (xd, -20, zc), (xd, -62, zc), (64, -62, 240.0)], 3.6),
        "inv_dc_pos": cable([(INV_X1, 10, zi), (INV_X1 + 8.0, 48, Z_CT - 6.0), (78.0, 48, Z_CT - 6.0)], 5.0),
        "inv_dc_neg": cable([(INV_X1, -10, zi), (xd, -10, zi), (xd, -62, 250.0), (64, -62, 250.0)], 5.0),
        "fan": cable([(XR + FAN[1] - 1, 62, Z_T1TOP + 5), (XR + FAN[1] + 4, 84, Z_T1TOP + 5), (CBX0 + 4, 84, Z_T1TOP + 5),
                      (CBX0 + 4, -60, CBZ1 + 6)], 1.5),
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
    so, sc = panel_mount()
    p["panel_standoffs"] = so
    p["screws_panelmount"] = sc
    p["antenna"] = antenna()
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
    p["screws_tap"] = tap_screws()
    for k, v in power_train().items():
        p[k] = v
    p["term_plates"] = terminal_plates()
    p["cb_standoffs"] = cb_standoffs()
    p["flex_ccs"] = sense_flex()
    p["tray1"] = tray1()
    p["mylar_tray1"] = mylar()
    p["tray2"] = tray2()
    p["inv_posts"] = posts()
    p["pem_tray1"] = pem_tray1()
    p["screws_trays"] = tray_screws()
    p["charger_npb450_24"] = charger()
    p["inverter_nts400p_124"] = inverter()
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
