"""Parts every concept shares: pack + collector (cells 7-8), pack - band from the rear (as v15), tray 1."""
from lib import *

Z0, Z1 = Z_TERM, Z_TERM + 3.15          # collector / band copper, same as the v15 series bars
TRAY_Z0, TRAY_Z1 = 218.45, Z_TRAY_TOP

def pack_pos_collector():
    """Cells 7-8 + terminals (x 77-152, y -46..-21)."""
    s = box(77.4, 152.0, -46.0, -21.0, Z0, Z1)
    return s - box(148.0, 153.0, -47.0, -41.0, Z0 - 1, Z1 + 1)      # corner chamfer: v15 had 6.8 mm to the upper standoff

def pack_neg_band(x_end):
    """P1 collector at the rear (cells 1-2), down the -y side at y -86..-66 to x_end (v15 band)."""
    s = box(-146.6, -80.0, -46.0, -21.0, Z0, Z1)                    # v15 ended at -76.6: 6.6 mm to series bar B
    s += box(-146.6, -126.6, -86.0, -21.0, Z0, Z1)
    s += box(-146.6, x_end, -86.0, -66.0, Z0, Z1)
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
