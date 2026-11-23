"""Tower A exterior + v1 internal stack, as one build123d assembly.
Units mm. x = pack length (front plate at +x), y = width, z = up. Body bottom at z = 0.
"""
import math, os
from build123d import *
import packmodel as pm

# ---------------- exterior parameters ----------------
T = 1.6                         # U and lid sheet, 5052 [mm]
W, H = 190.0, pm.SHELL_H + pm.T_SHEET   # body outer width, height [mm]
R = 22.0                        # outer bend radius [mm]
L_IN = 290.0                    # distance between plate inner faces [mm]
SEAM_Z = H - 34.0               # U top edge / lid split [mm]
GAP = 1.0                       # shadow seam [mm]
JOG = 1.7                       # lid joggle offset [mm]
LIP = 12.0                      # lid lip depth (clears top screw tabs) [mm]

PT = 5.0                        # end plate thickness, 6061 [mm]
PW = W + 16.0                   # plate width [mm]
FOOT = 18.0                     # plate below body [mm]
HANDLE = 52.0                   # plate above body [mm]
PZ0, PZ1 = -FOOT, H + HANDLE    # plate z range
PR = 26.7                       # plate corner radius
LEG = 48.3                      # leg width
ARCH_H, ARCH_R = 15.0, 13.3
SLOT_L, SLOT_H, SLOT_TOP = 83.3, 28.3, 15.0
CHAMFER = 0.5

GRID_COLS, GRID_ROWS, PITCH = 21, 25, 8.0
GRID_Y0 = -(GRID_COLS - 1) / 2 * PITCH          # -80
GRID_ZB = 32.0                                   # bottom row z
HOLE_D = 4.8
PIPE_Z, PIPE_H = SEAM_Z - 0.7, 2.2
CSK_D, SCREW_CLR = 8.4, 4.5
CSK = True                      # False: plain clearance holes for button heads
GROOVE_W, GROOVE_D = 2.0, 2.0
TAB_REACH = 6.0                 # tab beyond screw centre
NUT_D, NUT_L = 7.0, 4.0

X_IN = L_IN / 2                 # plate inner face
FONT = {"W": ["10001", "10001", "10101", "10101", "01010"], "E": ["111", "100", "111", "100", "111"],
        "I": ["111", "010", "010", "010", "111"], "L": ["100", "100", "100", "100", "111"],
        "N": ["1001", "1101", "1011", "1001", "1001"]}
TEXT = ["WE", "WILL", "WIN"]

C = (Align.CENTER, Align.CENTER, Align.MIN)

def bitmap(s):
    rows = [""] * 5
    for i, ch in enumerate(s):
        for r in range(5):
            rows[r] += ("0" if i else "") + FONT[ch][r]
    return rows

def grid_yz(i, j):
    """row i from top (0..24), col j (0..20) -> (y, z)"""
    return GRID_Y0 + j * PITCH, GRID_ZB + (GRID_ROWS - 1 - i) * PITCH

MID_R, MID_C = (GRID_ROWS - 1) // 2, (GRID_COLS - 1) // 2
SCREW_IJ = [(0, 0), (0, GRID_COLS - 1), (MID_R, 0), (MID_R, GRID_COLS - 1),
            (GRID_ROWS - 1, 0), (GRID_ROWS - 1, GRID_COLS - 1), (GRID_ROWS - 1, MID_C)]

def text_mask():
    lines = [bitmap(t) for t in TEXT]
    th = len(lines) * 5 + (len(lines) - 1)
    r0 = (GRID_ROWS - th) // 2
    m = set()
    for li, bm in enumerate(lines):
        w = len(bm[0]); c0 = (GRID_COLS - w) // 2
        for ri in range(5):
            for cj in range(w):
                if bm[ri][cj] == "1":
                    m.add((r0 + li * 6 + ri, c0 + cj))
    return m

# ---------------- body ----------------
def section(w, h, r, z0=0.0):
    return Plane.YZ * Pos(0, z0 + h / 2) * RectangleRounded(w, h, r)

def u_body():
    ring = section(W, H, R) - section(W - 2 * T, H - 2 * T, R - T, T)
    clip = Plane.YZ * Pos(0, SEAM_Z / 2 - 5) * Rectangle(W + 10, SEAM_Z + 10)
    prof = ring & clip
    u = extrude(prof, amount=X_IN + GROOVE_D - 0.2, both=True)
    # lid screw holes through walls (4)
    for sx in (-100, 100):
        for sy in (-1, 1):
            u -= Pos(sx, sy * (W / 2 - T / 2), SEAM_Z - 8) * Rot(90, 0, 0) * Cylinder(1.7, 4)
    for (x, y) in pm.HOLD_XY:                         # module hold-down screws from below
        u -= Pos(x, y, -1) * Cylinder(2.25, T + 2, align=C)
    return u

def holddown_screws():
    out = []
    for (x, y) in pm.HOLD_XY:
        head = Pos(x, y, -2.2) * Cylinder(3.8, 2.2, align=C)
        shank = Pos(x, y, 0) * Cylinder(1.95, pm.z_cell + 10, align=C)
        out.append(head + shank)
    return out

def lid_screws():
    out = []
    for sx in (-100, 100):
        for s in (-1, 1):
            head = Pos(sx, s * (W / 2 + 0.8), SEAM_Z - 8) * Rot(90, 0, 0) * Cylinder(2.8, 1.6)
            shank = Pos(sx, s * (W / 2 - 3.5), SEAM_Z - 8) * Rot(90, 0, 0) * Cylinder(1.45, 7.0)
            out.append(head + shank)
    return out

def tabs(sign):
    """Tabs bent off the U, lying on the plate inner face, one per screw. Returns (tabs, nuts)."""
    xs = sign * (X_IN - T / 2)
    out, nuts = [], []
    for (i, j) in SCREW_IJ:
        y, z = grid_yz(i, j)
        # tabs sized to stay clear of neighbouring LED holes (hole edge sits 5.6 mm from a grid point)
        if j == MID_C:                                   # floor tab
            t = Pos(xs, 0, T) * Box(T, 10, z + 5 - T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        else:                                            # wall tab
            yw = W / 2 - T
            y1 = abs(y) - 5
            t = Pos(xs, math.copysign((yw + y1) / 2, y), z) * Box(T, yw - y1, 10)
        t -= Pos(xs, y, z) * Rot(0, 90, 0) * Cylinder(SCREW_CLR / 2, T + 1)
        out.append(t)
        nut = Pos(sign * (X_IN - T - NUT_L / 2), y, z) * Rot(0, 90, 0) * (Cylinder(NUT_D / 2, NUT_L) - Cylinder(1.7, NUT_L))
        nuts.append(nut)
    return out, nuts

def lid():
    ring = section(W, H, R) - section(W - 2 * T, H - 2 * T, R - T, T)
    clip = Plane.YZ * Pos(0, (SEAM_Z + GAP + H + 5) / 2) * Rectangle(W + 10, H + 5 - SEAM_Z - GAP)
    Lx = L_IN - 1.0
    lid = extrude(ring & clip, amount=Lx / 2, both=True)
    for s in (-1, 1):
        y_lip = s * (W / 2 - T - 0.1 - T / 2)
        lid += Pos(0, y_lip, SEAM_Z - LIP) * Box(Lx, T, LIP + GAP + T, align=C)
        y_j = s * (W / 2 - T - 0.1 - T + (T + 0.1 + T) / 2)
        lid += Pos(0, y_j, SEAM_Z + GAP) * Box(Lx, T + 0.1 + T, T, align=C)
    for (x, y, cl, cw) in (pm.CONN_PWR, pm.CONN_CAN):
        lid -= Pos(x, y, H - 6) * Box(cl + 1, cw + 1, 12, align=C)
    return lid

def lid_nuts():
    out = []
    for sx in (-100, 100):
        for s in (-1, 1):
            y = s * (W / 2 - T - 0.1 - T - NUT_L / 2)
            out.append(Pos(sx, y, SEAM_Z - 8) * Rot(90, 0, 0) * (Cylinder(3.0, NUT_L) - Cylinder(1.3, NUT_L)))
    return out

# ---------------- end plate ----------------
def plate(sign, with_text, pipe=True, hole_yz=None, screw_yz=None):
    zc = (PZ0 + PZ1) / 2
    with BuildSketch(Plane.YZ) as sk:
        with Locations((0, zc)):
            RectangleRounded(PW, PZ1 - PZ0, PR)
        with Locations((0, PZ0)):
            RectangleRounded(PW - 2 * LEG, 2 * ARCH_H, ARCH_R, mode=Mode.SUBTRACT)
        with Locations((0, PZ1 - SLOT_TOP - SLOT_H / 2)):
            SlotCenterToCenter(SLOT_L - SLOT_H, SLOT_H, mode=Mode.SUBTRACT)
    p = extrude(sk.sketch, amount=PT)                      # x from 0 to PT
    # chamfer outer outline + handle slot on the visible face (x = PT)
    face = p.faces().sort_by(Axis.X)[-1]
    try:
        p = chamfer(face.edges(), CHAMFER)
    except Exception as e:
        print("chamfer skipped:", e)
    # LED holes, screw countersinks, charge pipe slot (all from visible face)
    mask = text_mask() if with_text else set()
    holes = []
    if hole_yz is None:
        hole_yz = [grid_yz(i, j) for i in range(GRID_ROWS) for j in range(GRID_COLS)
                   if (i, j) not in SCREW_IJ and (i, j) not in mask]
    for (y, z) in hole_yz:
        holes.append(Pos(PT / 2, y, z) * Rot(0, 90, 0) * Cylinder(HOLE_D / 2, PT + 2))
    p -= Compound(holes)
    csk_h = (CSK_D - SCREW_CLR) / 2
    if screw_yz is None:
        screw_yz = [grid_yz(i, j) for (i, j) in SCREW_IJ]
    for (y, z) in screw_yz:
        p -= Pos(PT / 2, y, z) * Rot(0, 90, 0) * Cylinder(SCREW_CLR / 2, PT + 2)
        if CSK:
            p -= Pos(PT - csk_h, y, z) * Rot(0, 90, 0) * Cone(SCREW_CLR / 2, CSK_D / 2, csk_h, align=C)
    if pipe:
        p -= extrude(Plane.YZ.offset(-1) * Pos(0, PIPE_Z) * SlotCenterToCenter(2 * abs(GRID_Y0) - PIPE_H, PIPE_H), amount=PT + 2)
    # groove on inner face (x = 0), following the U up to the seam
    ring = section(W + 0.4, H + 0.4, R + 0.2, -0.2) - section(W - 2 * T - 0.4, H - 2 * T - 0.4, R - T - 0.2, T + 0.2)
    clip = Plane.YZ * Pos(0, (SEAM_Z - 2) / 2) * Rectangle(W + 10, SEAM_Z + 2)
    p -= extrude(ring & clip, amount=GROOVE_D)
    # foot recesses
    for s in (-1, 1):
        p -= Pos(PT / 2, s * (PW / 2 - LEG / 2), PZ0) * Box(4, 40, 1.0, align=C)
    # place: inner face at x = sign * X_IN
    if sign > 0:
        return p.moved(Location((X_IN, 0, 0)))
    return p.mirror(Plane.YZ).moved(Location((-X_IN, 0, 0)))

def screws(sign):
    out = []
    csk_h = (CSK_D - SCREW_CLR) / 2
    for (i, j) in SCREW_IJ:
        y, z = grid_yz(i, j)
        xf = X_IN + PT
        head = Pos(xf - csk_h, y, z) * Rot(0, 90, 0) * Cone(2.0, CSK_D / 2 - 0.05, csk_h, align=C)
        head -= Pos(xf - 1.2, y, z) * Rot(0, 90, 0) * Cylinder(1.25, 1.3, align=C)  # hex socket (round approx)
        shank = Pos(xf - csk_h, y, z) * Rot(0, -90, 0) * Cylinder(1.95, 8.0, align=C)
        s = head + shank
        out.append(s if sign > 0 else s.mirror(Plane.YZ))
    return out

def feet(sign):
    out = []
    for s in (-1, 1):
        f = Pos(sign * (X_IN + PT / 2), s * (PW / 2 - LEG / 2), PZ0 - 1.5) * Box(3.8, 40, 2.5, align=C)
        out.append(f)
    return out

NOTCH = 12.0
DIFF_T = 2.0                    # opal acrylic diffuser [mm]

def _grid_panel(sign, xc, t):
    z0, z1 = GRID_ZB - 4, GRID_ZB + (GRID_ROWS - 1) * PITCH + 4
    b = Pos(sign * xc, 0, z0) * Box(t, 2 * abs(GRID_Y0) + 8, z1 - z0, align=C)
    for (i, j) in SCREW_IJ:                              # clearance around each tab / nut
        y, z = grid_yz(i, j)
        b -= Pos(sign * xc, y, z) * Box(t + 1, NOTCH, NOTCH)
    return b

def diffuser(sign):
    return _grid_panel(sign, X_IN - DIFF_T / 2, DIFF_T)

def led_board(sign):
    return _grid_panel(sign, X_IN - DIFF_T - T / 2, T)

def light_pipe(sign):
    return Pos(sign * (X_IN + PT / 2), 0, PIPE_Z) * Box(PT - 0.4, 2 * abs(GRID_Y0) - 1, PIPE_H - 0.3)

# ---------------- internals (from v1 stack) ----------------
def internals():
    parts = pm.build()
    for k in ("shell_5052", "lid_5052", "liner_formex", "mica_barrier"):
        parts.pop(k)
    Lr = L_IN - 2 * (T + NUT_L + 0.6)
    z_top = SEAM_Z - LIP - 1.0                       # stop below the lid lip
    out_sec = section(W - 2 * T - 0.4, H - 2 * T, R - T - 0.2, T)
    in_sec = section(W - 2 * T - 0.4 - 2 * pm.T_LINER, H - 2 * T - 2 * pm.T_LINER, R - T - 0.2 - pm.T_LINER, T + pm.T_LINER)
    clip = Plane.YZ * Pos(0, z_top / 2) * Rectangle(W, z_top)
    liner = extrude((out_sec - in_sec) & clip, amount=Lr / 2, both=True)
    for sx in (-1, 1):                               # folded end flaps
        liner += extrude((out_sec & clip).moved(Location((sx * (Lr / 2 - pm.T_LINER / 2) - pm.T_LINER / 2, 0, 0))), amount=pm.T_LINER)
    for (x, y) in pm.HOLD_XY:
        liner -= Pos(x, y, 0) * Cylinder(2.5, T + 3, align=C)
    parts["liner_formex"] = liner
    # MJF carrier follows the U's bottom radius (printed part, free to shape)
    cav = extrude(section(W - 2 * T - 0.4 - 2 * pm.T_LINER - 0.6, H, R - T - 0.2 - pm.T_LINER - 0.3, T + pm.T_LINER), amount=Lr / 2, both=True)
    parts["carrier_mjf_pa12"] = parts["carrier_mjf_pa12"] & cav
    mica = Pos(0, 0, pm.z_mica) * Box(Lr, 160.0, pm.T_MICA, align=C)
    for (x, y, cl, cw) in (pm.CONN_PWR, pm.CONN_CAN):
        mica -= Pos(x, y, pm.z_mica) * Box(cl + 4, cw + 4, pm.T_MICA, align=C)
    parts["mica_barrier"] = mica
    return parts

def build():
    parts = {"u_body": u_body(), "lid": lid(),
             "plate_front": plate(+1, True), "plate_rear": plate(-1, False)}
    for sign, tag in ((1, "f"), (-1, "r")):
        t, n = tabs(sign)
        parts[f"tabs_{tag}"] = Compound(t)
        parts[f"pem_tab_{tag}"] = Compound(n)
        parts[f"screws_{tag}"] = Compound(screws(sign))
        parts[f"feet_{tag}"] = Compound(feet(sign))
        parts[f"ledboard_{tag}"] = led_board(sign)
        parts[f"diffuser_{tag}"] = diffuser(sign)
        parts[f"pipe_{tag}"] = light_pipe(sign)
    parts["pem_lid"] = Compound(lid_nuts())
    parts["screws_lid"] = Compound(lid_screws())
    parts["screws_hold"] = Compound(holddown_screws())
    for k, v in internals().items():
        parts[f"int_{k}"] = v
    return parts
