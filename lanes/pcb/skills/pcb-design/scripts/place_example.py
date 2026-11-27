"""Worked example (2026 BMS board) of the placement area proof in references/area-budget.md. Copy and edit the regions.
Area proof for the BMS board: put every real footprint from courtyards.BOM on a board of a given size,
grouped in functional blocks, and check that no two courtyards overlap and all sit inside the outline.

This is a floorplan proof of AREA, not the layout: inside a block, parts are shelf-packed, not placed at their pins.
The occupancy figure (sum of courtyards / board area) is what says whether it can be routed.

Usage: python3 place.py W H [out.kicad_pcb]      e.g.  python3 place.py 90 55
"""
import sys, os, itertools
import pcbnew
from courtyards import BOM, LIB, crtyd_bbox

W, H = float(sys.argv[1]), float(sys.argv[2])
OUT = sys.argv[3] if len(sys.argv) > 3 else f"bms_area_{int(W)}x{int(H)}.kicad_pcb"
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
BLOCK_OF = {"AFE": "AFE", "IMD": "AFE", "BTN": "OUT", "MCU": "MCU", "TEST": "MCU", "SHUNT": "SHUNT", "PWR": "PWR",
            "COIL": "OUT", "CHGR": "OUT", "INV": "OUT", "PRE": "PRE"}
CONN_EDGE = {"J1": "CONN_L", "J2": "CONN_L", "J3": "CONN_B", "J4": "CONN_R", "J5": "CONN_R"}

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

def main():
    board = pcbnew.BOARD()
    # outline
    for (a, b) in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]), pcbnew.FromMM(b[1]))); s.SetWidth(pcbnew.FromMM(0.1)); board.Add(s)
    R = regions(W, H)
    groups = {k: [] for k in R}
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
    for k, fps in groups.items():
        unplaced += shelf_pack(fps, R[k])
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
