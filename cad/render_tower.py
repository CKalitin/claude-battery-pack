import os, glob
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_tower")
MAT = {  # prefix: (color, specular, opacity)
    "u_body": ("#9E0F1A", 0.7, 1), "lid": ("#9E0F1A", 0.7, 1), "tabs": ("#9E0F1A", 0.4, 1),
    "plate": ("#3A3C42", 0.35, 1), "screws": ("#121214", 0.6, 1), "feet": ("#0C0C0E", 0.1, 1),
    "pem": ("#B0B4BA", 0.6, 1), "ledboard": ("#1F6B2A", 0.2, 1), "pipe": ("#F3ECDD", 0.3, 1),
    "int_cell": ("#2B6FC4", 0.3, 1), "int_carrier": ("#2E2F33", 0.1, 1), "int_liner": ("#E8A93A", 0.2, 0.55),
    "int_busbar": ("#C8693A", 0.5, 1), "int_riser": ("#C8693A", 0.5, 1), "int_flex": ("#E0A035", 0.2, 1),
    "int_power_pcb": ("#1E5631", 0.2, 1), "int_bms_pcb": ("#2E8B3A", 0.2, 1), "int_imd": ("#7E57C2", 0.2, 1),
    "int_mica": ("#DDD6C2", 0.1, 0.9), "int_pwr_contactor": ("#26272B", 0.3, 1), "int_pwr_fuse": ("#EDEDED", 0.2, 1),
    "int_pwr_shunt": ("#B87333", 0.5, 1), "int_pwr_precharge": ("#5A5D63", 0.2, 1),
    "int_pwr_conn_pwr": ("#1A1A1C", 0.3, 1), "int_pwr_conn_can": ("#1A1A1C", 0.3, 1),
    "int_comp_endplates": ("#9EA3AA", 0.5, 1), "int_comp_rods": ("#C9CCD1", 0.7, 1), "int_comp_rodnuts": ("#C9CCD1", 0.7, 1),
    "int_comp_insul": ("#F2F2EE", 0.1, 1), "int_comp_pcb_standoffs": ("#C9A94A", 0.5, 1),
    "diffuser": ("#F4F1EA", 0.2, 0.85), "screws_lid": ("#9E0F1A", 0.6, 1), "screws_hold": ("#121214", 0.5, 1),
}
EXPLODE = {"plate_front": (110, 0, 0), "screws_f": (150, 0, 0), "plate_rear": (-110, 0, 0), "screws_r": (-150, 0, 0),
           "feet_f": (110, 0, 0), "feet_r": (-110, 0, 0), "pipe_f": (110, 0, 0), "pipe_r": (-110, 0, 0),
           "lid": (0, 0, 190), "pem_lid": (0, 0, 190), "int_mica": (0, 0, 160)}

def mat(n):
    best = max((k for k in MAT if n.startswith(k)), key=len, default=None)
    return MAT.get(best, ("#888888", 0.2, 1))

def load(names=None):
    m = {}
    for f in glob.glob(os.path.join(OUT, "stl", "*.stl")):
        n = os.path.basename(f)[:-4]
        if names is None or any(n.startswith(k) for k in names):
            m[n] = pv.read(f)
    return m

def shot(fname, title, hide=(), only=None, explode=False, view=(1.0, -1.15, 0.62), size=(1800, 1500), zoom=1.0,
         clip=None, dark=True, parallel=False, edges=True):
    p = pv.Plotter(off_screen=True, window_size=size)
    if dark:
        p.set_background("#141416", top="#3A3A40")
    else:
        p.set_background("white")
    p.enable_anti_aliasing("ssaa")
    for n, m in load(only).items():
        if any(n.startswith(h) for h in hide):
            continue
        if explode:
            off = next((v for k, v in EXPLODE.items() if n.startswith(k)), None)
            if off:
                m = m.translate(off, inplace=False)
        if clip is not None and (n.startswith(("u_body", "lid", "plate_rear", "int_liner", "tabs_r"))):
            m = m.clip(normal=clip[0], origin=clip[1], invert=False)
            if m.n_points == 0:
                continue
        col, spec, op = mat(n)
        p.add_mesh(m, color=col, opacity=op, smooth_shading=True, split_sharp_edges=True,
                   specular=spec, specular_power=40, ambient=0.18, diffuse=0.85)
        if edges and n.startswith(("plate", "u_body", "lid")):
            p.add_mesh(m.extract_feature_edges(35, boundary_edges=False, non_manifold_edges=False),
                       color="#0A0A0B", line_width=0.8, opacity=0.6)
    if parallel:
        p.enable_parallel_projection()
    p.camera.position = (view[0] * 1500, view[1] * 1500, 150 + view[2] * 1500)
    p.camera.focal_point = (0, 0, 150)
    p.camera.up = (0, 0, 1)
    p.reset_camera()
    p.camera.zoom(zoom)
    tc = "#EEEEEE" if dark else "#111111"
    p.add_text(title, position=(50, size[1] - 80), font_size=15, color=tc, font="arial")
    p.add_text("Tower A  |  1.28 kWh 8S LFP  |  300 x 206 x 349 mm  |  build123d", position=(50, size[1] - 118),
               font_size=9, color="#9A9AA0", font="courier")
    p.screenshot(os.path.join(OUT, fname))
    p.close()

INT = ("int_cell", "int_carrier", "int_liner", "int_busbar", "int_riser", "int_flex", "int_power", "int_bms", "int_imd", "int_mica", "int_comp", "int_pwr_contactor", "int_pwr_fuse", "int_pwr_shunt", "int_pwr_precharge")
shot("t_hero.png", "Tower A", hide=INT + ("ledboard",), zoom=1.15)
#shot("t_front.png", "Front plate: WE WILL WIN", hide=INT, view=(1, 0.0001, 0), parallel=True, zoom=1.25, size=(1400, 1800))
shot("t_exploded.png", "Exploded: plates, U body, lid", explode=True, view=(1.0, -1.3, 0.75), zoom=1.05, size=(1800, 1500))
shot("t_cutaway.png", "Section: internals inside the U", hide=("lid", "pem_lid", "plate_front", "screws_f", "feet_f", "pipe_f"),
     clip=((0, 1, 0), (0, 0, 0)), view=(1.0, -1.25, 0.7), zoom=1.1)
#shot("t_rear.png", "Rear 3/4", hide=INT + ("ledboard",), view=(-1.0, 1.1, 0.55), zoom=1.15)
shot("t_module.png", "Cell module: LF50K x8, 8 mm end plates, 4 x M5 tie rods",
     only=("int_cell", "int_comp", "int_carrier", "int_busbar", "int_riser", "screws_hold"), view=(1.0, -1.2, 0.8), zoom=1.15)
print("ok")
