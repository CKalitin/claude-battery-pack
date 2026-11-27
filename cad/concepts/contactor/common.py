"""Parts every concept shares: pack + collector (cells 7-8), pack - band from the rear (as v15), tray 1."""
from lib import *

Z0, Z1 = Z_TERM, Z_TERM + 3.15          # collector / band copper, same as the v15 series bars
TRAY_Z0, TRAY_Z1 = 218.45, Z_TRAY_TOP

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..")))
import tower15 as _t
CX = _t.cell_x                          # v16.3: collectors follow the cell pitch (Mylar insulators: 36.95 mm, was 38.30)
SB_B_X0 = CX[2] - _t.BB_W / 2           # series bar B, -x end
PP_X0, PP_X1 = CX[6] - 12.5, CX[7] + 12.5   # + collector (cells 7-8): 79.9 .. 141.8

def pack_pos_collector():
    """Cells 7-8 + terminals (y -46..-21). v16.3: x from the cell positions; ends 12.5 mm past the terminal centres."""
    s = box(PP_X0, PP_X1, -46.0, -21.0, Z0, Z1)
    return s - box(PP_X1 - 4.0, PP_X1 + 1.0, -47.0, -41.0, Z0 - 1, Z1 + 1)   # corner chamfer toward the upper standoff

def pack_neg_band(x_end):
    """P1 collector at the rear (cells 1-2), down the -y side at y -86..-66 to x_end (v15 band).
    v16.3: x0 -140.5 keeps 7 mm to the rear upper standoffs (x -151.9); the upper arm stops 10.05 mm short of series bar B."""
    x0 = -140.5
    s = box(x0, SB_B_X0 - 10.05, -46.0, -21.0, Z0, Z1)
    s += box(x0, CX[0] + 7.45, -86.0, -21.0, Z0, Z1)
    s += box(x0, x_end, -86.0, -66.0, Z0, Z1)
    return s

def tray1(cuts=()):
    t = box(-170.0, 163.0, -88.0, 88.0, TRAY_Z0, TRAY_Z1)
    for c in cuts:
        t -= box(*c, TRAY_Z0 - 1, TRAY_Z1 + 1)
    return t

TRAY_ALLOW = [("tray1", "charger"), ("tray1", "so_upper"), ("tray1", "screws_trays"), ("tray1", "inv_posts"), ("tray1", "pem_"),
              ("tray1", "flex_ccs")]

def neg_band_path(x_riser, y_riser):
    """Centre line of the - band from where it enters the bay (x 50) to the riser foot."""
    zc = (Z0 + Z1) / 2
    return [(50.0, -76.0, zc), (x_riser, -76.0, zc), (x_riser, y_riser, zc)]
