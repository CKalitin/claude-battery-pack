"""Area proof for the BMS board: put every real footprint from courtyards.BOM on a board of a given size,
grouped in functional blocks, and check that no two courtyards overlap and all sit inside the outline.

This is a floorplan proof of AREA, not the layout: inside a block, parts are shelf-packed, not placed at their pins.
The occupancy figure (sum of courtyards / board area) is what says whether it can be routed.

Usage: python3 place.py W H [out.kicad_pcb]      e.g.  python3 place.py 90 55
"""
import sys, os, itertools
import pcbnew
from courtyards import BOM, LIB, crtyd_bbox
FET = os.environ.get("PRE") == "fet"       # precharge by P-MOSFET instead of the G6S relay
CC = os.environ.get("LAYOUT") == "cc"      # credit-card region template
if FET:
    S23 = ("Package_TO_SOT_SMD", "SOT-23"); R04 = ("Resistor_SMD", "R_0402_1005Metric")
    BOM = [b for b in BOM if not (b[0] == "PRE" and "AC05" not in b[1])]
    BOM += [("PRE", "precharge P-FET 40 V (SOT-23)", S23, 1), ("PRE", "gate pull-down N-FET", S23, 1),
            ("PRE", "gate divider + pulldown", R04, 3)]

W, H = float(sys.argv[1]), float(sys.argv[2])
OUT = sys.argv[3] if len(sys.argv) > 3 else f"bms_area_{W:g}x{H:g}{'_fet' if os.environ.get('PRE') == 'fet' else ''}.kicad_pcb"
GAP = 0.2            # extra space between courtyards [mm] (courtyards already carry IPC-7351 excess)
EDGE = 0.5           # courtyard to board edge [mm]

# --- blocks: region rectangles (x0, y0, x1, y1) in board mm, KiCad frame (x right, y down).
#     Pack frame: board x = pack x + const; board y = -(pack y) + const. Left edge = pack -x (rear), bottom = pack -y.
CON_D = 14.0         # depth of the edge connector band
def regions(W, H):
    m = 8.6          # corner hole courtyard band
    return {
        # left edge (pack -x, plug room): shunt + sense flex
        "CONN_L":  (EDGE, m, EDGE + CON_D, H - m),
        # right edge: outputs + lid/LED link
        "CONN_R":  (W - EDGE - CON_D, m, W - EDGE, H - m),
        # bottom edge near the left end (pack -y, plug room x -105..-62): power taps
        "CONN_B":  (m, H - EDGE - 11.5, m + 16, H - EDGE),
        "AFE":     (EDGE + CON_D + GAP, EDGE, EDGE + CON_D + 24, H * 0.55),
        "SHUNT":   (EDGE + CON_D + GAP, H * 0.55 + GAP, EDGE + CON_D + 24, H - 12.2),
        "PWR":     (m + 16 + GAP, H * 0.62, W * 0.52, H - EDGE),
        "MCU":     (EDGE + CON_D + 24 + GAP, EDGE, W * 0.70, H * 0.62 - GAP),
        "PRE":     (W * 0.52 + GAP, H * 0.62, W - EDGE - CON_D - GAP, H - EDGE),
        "OUT":     (W * 0.70 + GAP, EDGE, W - EDGE - CON_D - GAP, H * 0.62 - GAP),
    }
def regions_cc(W, H):
    m = 8.6; c = EDGE + CON_D; b = H - EDGE - 7.6     # bottom strip holds the 28.3 mm AC05 lying along x
    return {
        "CONN_L": (EDGE, m, c, H - m), "CONN_R": (W - c, m, W - EDGE, H - m),
        "CONN_B": (m, H - EDGE - 11.5, m + 16, H - EDGE),
        "PRE":   (m + 16 + GAP, b, W - c - GAP, H - EDGE),
        "AFE":   (c + GAP, EDGE, c + 24, H * 0.55),
        "SHUNT": (c + GAP, H * 0.55 + GAP, c + 24, H - 12.2),
        "MCU":   (c + 24 + GAP, EDGE, W * 0.70, H * 0.62 - GAP),
        "OUT":   (W * 0.70 + GAP, EDGE, W - c - GAP, H * 0.62 - GAP),
        "PWR":   (c + 24 + GAP, H * 0.62, W - c - GAP, b - GAP),
    }
def regions_split(W, H):
    m = 8.6; c = EDGE + CON_D; b = H - EDGE - 7.6; t = EDGE + 11.2     # top band = right-angle 1x Micro-Fits
    return {
        "CONN_L": (EDGE, m, c, H - m), "CONN_R": (W - c, m, W - EDGE, H - m),
        "CONN_B": (m, H - EDGE - 11.5, m + 16, H - EDGE), "CONN_T": (c + GAP, EDGE, W - c - GAP, t),
        "PRE":   (m + 16 + GAP, b, W - c - GAP, H - EDGE),
        "AFE":   (c + GAP, t + GAP, c + 24, H * 0.58),
        "SHUNT": (c + GAP, H * 0.58 + GAP, c + 24, H - 12.2),
        "MCU":   (c + 24 + GAP, t + GAP, W * 0.70, H * 0.68 - GAP),
        "OUT":   (W * 0.70 + GAP, t + GAP, W - c - GAP, H * 0.68 - GAP),
        "PWR":   (c + 24 + GAP, H * 0.68, W - c - GAP, b - GAP),
    }
if CC:
    regions = regions_cc
if os.environ.get("LAYOUT") == "split":
    regions = regions_split

BLOCK_OF = {"AFE": "AFE", "IMD": "AFE", "BTN": "OUT", "MCU": "MCU", "TEST": "MCU", "SHUNT": "SHUNT", "PWR": "PWR",
            "COIL": "OUT", "CHGR": "OUT", "INV": "OUT", "PRE": "PRE"}
CONN_EDGE = {"J1": "CONN_L", "J2": "CONN_L", "J3": "CONN_B", "J4": "CONN_R", "J5": "CONN_R",
             "J6": "CONN_T", "J7": "CONN_T", "J8": "CONN_T", "J9": "CONN_T"}

def load(lib, name):
    fp = pcbnew.FootprintLoad(f"{LIB}/{lib}.pretty", name)
    if fp is None:
        raise SystemExit(f"cannot load {lib}:{name}")
    return fp

def crt_bbox(fp):
    """Courtyard bbox of a placed footprint, in mm (x0, y0, x1, y1)."""
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    s = pcbnew.ToMM
    return s(bb.GetX()), s(bb.GetY()), s(bb.GetX() + bb.GetWidth()), s(bb.GetY() + bb.GetHeight())

def move_bbox_to(fp, x0, y0):
    """Move footprint so its courtyard's top-left corner is at (x0, y0)."""
    bx0, by0, _, _ = crt_bbox(fp)
    p = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(p.x + pcbnew.FromMM(x0 - bx0), p.y + pcbnew.FromMM(y0 - by0)))

def shelf_pack(fps, rect):
    """Rows, tallest first, left to right. Rotates a part 90 deg if that fits the row better. Returns unplaced."""
    x0, y0, x1, y1 = rect
    def wh(fp):
        a, b, c, d = crt_bbox(fp); return c - a, d - b
    fps = sorted(fps, key=lambda f: -max(wh(f)))
    left, x, y, row_h = [], x0, y0, 0.0
    for fp in fps:
        w, h = wh(fp)
        if w > h and w > (x1 - x0) * 0.6:        # long parts lie along x
            pass
        placed = False
        for attempt in range(2):
            w, h = wh(fp)
            if x + w <= x1 + 1e-6 and y + h <= y1 + 1e-6:
                move_bbox_to(fp, x, y); x += w + GAP; row_h = max(row_h, h); placed = True; break
            if x > x0 and y + row_h + GAP + h <= y1 + 1e-6 and x0 + w <= x1:    # new row
                y += row_h + GAP; x, row_h = x0, 0.0
                move_bbox_to(fp, x, y); x += w + GAP; row_h = h; placed = True; break
            fp.SetOrientationDegrees(fp.GetOrientationDegrees() + 90)
        if not placed:
            left.append(fp)
    return left

def orient_out(fp, outward):
    """Turn a right-angle connector so its mating face points out of the board (outward = unit vector).
    Mating direction = pad centroid -> courtyard centre (the housing sits in front of the pins)."""
    best, bestdot = 0, -9
    for k in range(4):
        fp.SetOrientationDegrees(k * 90)
        pads = list(fp.Pads())
        px = sum(pcbnew.ToMM(q.GetPosition().x) for q in pads) / len(pads)
        py = sum(pcbnew.ToMM(q.GetPosition().y) for q in pads) / len(pads)
        a, b, c, d = crt_bbox(fp); cx, cy = (a + c) / 2, (b + d) / 2
        dot = (cx - px) * outward[0] + (cy - py) * outward[1]
        if dot > bestdot: best, bestdot = k, dot
    fp.SetOrientationDegrees(best * 90)

def edge_pack(fps, rect, axis):
    """Connectors in a line along one edge (axis 'y' = stacked along a vertical edge), mating face at the edge."""
    x0, y0, x1, y1 = rect
    left, pos = [], (y0 if axis == "y" else x0)
    for fp in fps:
        orient_out(fp, ((-1, 0) if rect[0] < W / 2 else (1, 0)) if axis == "y" else (0, 1))
        a, b, c, d = crt_bbox(fp); w, h = c - a, d - b
        if axis == "y":
            if pos + h > y1: left.append(fp); continue
            move_bbox_to(fp, x0 if rect[0] < W / 2 else x1 - w, pos); pos += h + GAP
        else:
            if pos + w > x1: left.append(fp); continue
            move_bbox_to(fp, pos, y1 - h); pos += w + GAP
    return left

def edge_pack_top(fps, rect):
    x0, y0, x1, y1 = rect; left, pos = [], x0
    for fp in fps:
        orient_out(fp, (0, -1)); a, b, c, d = crt_bbox(fp); w = c - a
        if pos + w > x1: left.append(fp); continue
        move_bbox_to(fp, pos, y0); pos += w + 1.0
    return left

def main():
    board = pcbnew.BOARD()
    # outline
    for (a, b) in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]), pcbnew.FromMM(b[1]))); s.SetWidth(pcbnew.FromMM(0.1)); board.Add(s)
    R = regions(W, H)
    groups = {k: [] for k in R}
    groups.setdefault("CONN_T", [])
    holes, n = [], 0
    jn = 0
    for blk, fn, fp_id, q in BOM:
        if fp_id is None or q == 0:
            continue
        for i in range(q):
            n += 1
            fp = load(*fp_id)
            if blk == "CONN":
                jn += 1; ref = f"J{jn}"; groups[CONN_EDGE[ref]].append(fp)
            elif blk == "MECH":
                ref = f"H{len(holes) + 1}"; holes.append(fp)
            else:
                ref = f"{blk[:3]}{n}"; groups[BLOCK_OF[blk]].append(fp)
            fp.SetReference(ref); fp.SetValue(fn[:40]); board.Add(fp)
    # corner holes, 4.3 mm from the edges (M3 centre 5 mm from the edges per the space claim)
    for fp, (cx, cy) in zip(holes, [(5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)]):
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
    unplaced = []
    unplaced += edge_pack(groups.pop("CONN_L"), R["CONN_L"], "y")
    unplaced += edge_pack(groups.pop("CONN_R"), R["CONN_R"], "y")
    unplaced += edge_pack(groups.pop("CONN_B"), R["CONN_B"], "x")
    if "CONN_T" in groups:
        unplaced += edge_pack_top(groups.pop("CONN_T"), R["CONN_T"])
    for k, fps in groups.items():
        unplaced += shelf_pack(fps, R[k])
    # fallback: any part a block region could not hold goes to the first free spot on the board (0.25 mm grid scan),
    # reported by name. Honest for test points; for a decoupling cap it means "check it can reach its pin".
    fallback = []
    if unplaced and os.environ.get("FALLBACK", "1") == "1":
        placed = [crt_bbox(f) for f in board.GetFootprints() if f not in unplaced]
        still = []
        for fp in sorted(unplaced, key=lambda f: -(lambda b: (b[2]-b[0])*(b[3]-b[1]))(crt_bbox(f))):
            ok = False
            for rot in (0, 90):
                fp.SetOrientationDegrees(rot); a, b, c, d = crt_bbox(fp); w, h = c - a, d - b
                y = EDGE
                while y + h <= H - EDGE and not ok:
                    x = EDGE
                    while x + w <= W - EDGE:
                        cand = (x, y, x + w, y + h)
                        if all(not (cand[0] < B[2] + GAP and B[0] < cand[2] + GAP and cand[1] < B[3] + GAP and B[1] < cand[3] + GAP) for B in placed):
                            move_bbox_to(fp, x, y); placed.append(crt_bbox(fp)); ok = True; break
                        x += 0.25
                    y += 0.25
                if ok: break
            (fallback if ok else still).append(fp)
        unplaced = still
    print(f"fallback-placed {len(fallback)}: {[f.GetReference() for f in fallback]}")
    # checks
    fps = list(board.GetFootprints())
    bbs = {f.GetReference(): crt_bbox(f) for f in fps}
    over = [(a, b) for (a, A), (b, B) in itertools.combinations(bbs.items(), 2)
            if A[0] < B[2] - 1e-3 and B[0] < A[2] - 1e-3 and A[1] < B[3] - 1e-3 and B[1] < A[3] - 1e-3]
    outside = [r for r, (a, b, c, d) in bbs.items() if a < -1e-3 or b < -1e-3 or c > W + 1e-3 or d > H + 1e-3]
    area = sum((c - a) * (d - b) for a, b, c, d in bbs.values())
    pcbnew.SaveBoard(OUT, board)
    print(f"board {W:.0f} x {H:.0f} mm = {W * H:.0f} mm^2; parts {len(fps)}; courtyards {area:.0f} mm^2; "
          f"occupancy {100 * area / (W * H):.0f} %")
    print(f"unplaced {len(unplaced)}: {[f.GetReference() for f in unplaced]}")
    print(f"overlapping courtyard pairs {len(over)}: {over[:10]}")
    print(f"outside outline {len(outside)}: {outside}")
    for k, (x0, y0, x1, y1) in regions(W, H).items():
        print(f"  region {k:7s} {x1 - x0:5.1f} x {y1 - y0:5.1f}")
    return 0 if not (unplaced or over or outside) else 1

if __name__ == "__main__":
    sys.exit(main())
