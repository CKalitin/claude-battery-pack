import os, glob
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out")
COL = {"shell": "#AEB3BA", "lid": "#C3C7CC", "liner": "#E8A93A", "carrier": "#3A3B40", "cell": "#2B6FC4",
       "busbar": "#C8693A", "riser": "#C8693A", "flex": "#E0A035", "power_pcb": "#1E5631", "bms_pcb": "#2E8B3A",
       "imd": "#7E57C2", "mica": "#DDD6C2", "pwr_contactor": "#26272B", "pwr_fuse": "#EDEDED", "pwr_shunt": "#B87333",
       "pwr_precharge": "#5A5D63", "pwr_conn_pwr": "#C0392B", "pwr_conn_can": "#3A3B40"}
OPAC = {"liner": 0.55, "mica": 0.9}
EXPLODE = {"shell": 0, "liner": 300, "carrier": 560, "cell": 560, "busbar": 620, "riser": 620, "flex": 665,
           "power_pcb": 720, "pwr_": 720, "bms_pcb": 800, "imd": 800, "mica": 860, "lid": 900}
SPEC = "1.28 kWh | 8S1P LFP | 25.6 V nom | 290 x 190 x 283 mm | modelled in build123d"

def key(n):
    return next(k for k in COL if n.startswith(k))

def ekey(n):
    return next(k for k in EXPLODE if n.startswith(k))

def load(cut=False):
    m = {os.path.basename(f)[:-4]: pv.read(f) for f in glob.glob(os.path.join(OUT, "stl", "*.stl"))}
    if cut:
        for f in glob.glob(os.path.join(OUT, "stl_cut", "*.stl")):
            m[os.path.basename(f)[:-4]] = pv.read(f)
    return m

def render(fname, title, explode=False, cut=False, hide=(), view=(1, -1.25, 0.9), size=(1600, 1600), zoom=1.0):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    p.enable_anti_aliasing("ssaa")
    for n, m in load(cut).items():
        k = key(n)
        if any(n.startswith(h) for h in hide):
            continue
        if explode:
            m = m.translate((0, 0, EXPLODE[ekey(n)]), inplace=False)
        p.add_mesh(m, color=COL[k], opacity=OPAC.get(k, 1.0), smooth_shading=False,
                   specular=0.25, specular_power=20, ambient=0.25, diffuse=0.8)
        p.add_mesh(m.extract_feature_edges(25, boundary_edges=False, non_manifold_edges=False),
                   color="#1a1a1a", line_width=1.2)
    p.enable_parallel_projection()
    p.camera_position = "iso"
    p.camera.position = tuple(v * 1000 for v in view)
    p.camera.focal_point = (0, 0, 0)
    p.camera.up = (0, 0, 1)
    p.reset_camera()
    p.camera.zoom(zoom)
    p.add_text(title, position=(40, size[1] - 70), font_size=16, color="#111111", font="arial")
    p.add_text(SPEC, position=(40, size[1] - 105), font_size=9, color="#555555", font="courier")
    p.screenshot(os.path.join(OUT, fname))
    p.close()

render("render_exploded.png", "1 kWh pack: exploded assembly", explode=True, size=(1400, 2200), zoom=1.05)
render("render_cutaway.png", "1 kWh pack: section cutaway, lid off", cut=True, hide=("lid", "mica"), zoom=1.1)
render("render_closed.png", "1 kWh pack: assembled", zoom=1.1)
render("render_electronics.png", "Electronics stack: power PCB under BMS + IMD PCB", hide=("lid", "mica", "bms_pcb", "imd"), cut=True, zoom=1.1)
render("render_top.png", "Top view: busbars + flex CCS (one tap per series node)",
       hide=("lid", "mica", "bms", "imd", "power_pcb", "pwr_"), view=(0, -0.001, 1), zoom=0.95)
print("ok")
