import os, glob
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_tower2")
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
    "diffuser": ("#F4F1EA", 0.2, 0.85), "tray": ("#B8BCC2", 0.5, 1), "mica_tray": ("#DDD6C2", 0.1, 0.9),
    "inv_posts": ("#C9A94A", 0.5, 1), "cb_standoffs": ("#C9A94A", 0.5, 1), "screws_trays": ("#121214", 0.5, 1),
    "screws_panel": ("#121214", 0.5, 1), "int_busbar_screws": ("#C9CCD1", 0.6, 1),
    "charger": ("#8C9096", 0.4, 1), "inverter": ("#6E7278", 0.4, 1), "ctrl_pcb": ("#1E5631", 0.2, 1),
    "ctrl_contactor": ("#26272B", 0.3, 1), "ctrl_fuse": ("#EDEDED", 0.2, 1), "ctrl_shunt": ("#B87333", 0.5, 1),
    "ctrl_precharge": ("#5A5D63", 0.2, 1), "ctrl_afe": ("#111111", 0.3, 1), "ctrl_esp32": ("#B0B4BA", 0.5, 1),
    "ctrl_terminals": ("#2F7D3A", 0.3, 1), "ctrl_": ("#1A1A1C", 0.3, 1), "panel_": ("#1A1A1C", 0.3, 1),
    "int_pack_": ("#C8693A", 0.5, 1), "cable_ac": ("#1C1C1E", 0.3, 1), "cable_chg_dc_pos": ("#C0282E", 0.3, 1),
    "cable_inv_dc_pos": ("#C0282E", 0.3, 1), "cable_dc_out": ("#C0282E", 0.3, 1), "cable_chg_dc_neg": ("#151515", 0.3, 1),
    "cable_inv_dc_neg": ("#151515", 0.3, 1), "cable_can": ("#2A6FD0", 0.3, 1), "cable_led": ("#E0E0E0", 0.3, 1),
    "cable_ccs": ("#E0A035", 0.3, 1), "fan_bracket": ("#1A1A1C", 0.3, 1), "fan_": ("#6B4A3A", 0.3, 1), "screws_fan": ("#121214", 0.5, 1), "cable_fan": ("#E8E8E8", 0.3, 1), "ctrl_buck": ("#2A2A2E", 0.3, 1), "screws_lid": ("#9E0F1A", 0.6, 1), "screws_hold": ("#121214", 0.5, 1),
}
EXPLODE = {"plate_front": (110, 0, 0), "screws_f": (150, 0, 0), "plate_rear": (-110, 0, 0), "screws_r": (-150, 0, 0),
           "feet_f": (110, 0, 0), "feet_r": (-110, 0, 0), "pipe_f": (110, 0, 0), "pipe_r": (-110, 0, 0),
           "lid": (0, 0, 230), "pem_lid": (0, 0, 230), "panel_": (0, 0, 230), "screws_panel": (0, 0, 230), "screws_lid": (0, 0, 260), "ledboard_f": (60, 0, 0), "diffuser_f": (85, 0, 0)}

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
    p.add_text("Tower A  |  1.28 kWh 8S LFP  |  320 x 206 x 369 mm (body 297)  |  build123d", position=(50, size[1] - 118),
               font_size=9, color="#9A9AA0", font="courier")
    p.screenshot(os.path.join(OUT, fname))
    p.close()

INT = ("fan_", "int_", "tray", "mica_tray", "inv_posts", "cb_standoffs", "screws_trays", "charger", "inverter", "ctrl_", "cable_", "panel_")
SHELL = ("u_body", "lid", "pem_lid", "screws_lid", "plate_", "screws_f", "screws_r", "feet_", "pipe_f", "tabs_", "pem_tab", "diffuser", "ledboard", "screws_hold", "int_liner")
shot("t_hero.png", "Tower A v4", hide=("fan_", "int_", "tray", "mica_tray", "inv_posts", "cb_standoffs", "screws_trays", "charger", "inverter", "ctrl_", "cable_", "ledboard"), zoom=1.15)
shot("t_rear_flat.png", "Rear elevation: fan visible through the grid", hide=(), view=(-1, -0.0001, 0), parallel=True, zoom=1.2, size=(1400, 1800))
shot("t_screw_detail.png", "Detail: M4 button heads on the grid", hide=INT + ("ledboard",), view=(-1.0, 0.35, 0.25), zoom=3.2)
shot("t_rear.png", "Rear: 21x30 grid, 7.78 mm pitch, 11 button heads on nodes", hide=INT + ("ledboard",), view=(-1.0, 1.1, 0.55), zoom=1.15)
shot("t_front.png", "Front: 21x25 LED matrix, 7.78 mm pitch, WE WILL WIN", hide=INT + ("ledboard",), view=(1, 0.0001, 0), parallel=True, zoom=1.2, size=(1400, 1800))
shot("t_exploded.png", "Exploded: plates, LED board, diffuser, lid + panel connectors", explode=True, view=(1.0, -1.3, 0.75), zoom=1.0)
shot("t_cutaway.png", "Section y=0: module / tray 1 (charger + control board) / tray 2 (inverter)",
     hide=("lid", "pem_lid", "screws_lid", "plate_front", "screws_f", "feet_f", "pipe_f", "diffuser", "ledboard", "panel_", "screws_panel"),
     clip=((0, 1, 0), (0, 0, 0)), view=(1.0, -1.25, 0.7), zoom=1.1)
shot("t_internals.png", "Internals, shell hidden: wire paths", hide=SHELL, view=(1.0, -1.1, 0.75), zoom=1.2)
shot("t_ctrl.png", "Control end: board, risers, terminal strip, lid connectors", hide=SHELL + ("charger", "inverter"),
     only=("ctrl_", "int_pack", "cable_", "panel_", "tray1", "cb_standoffs", "int_busbar", "int_cell", "screws_trays", "int_flex"),
     view=(0.9, -1.0, 0.9), zoom=1.0)
shot("t_rear_open.png", "Rear, plate hidden: NF-A14 bolted through the plate", hide=("plate_rear", "screws_r", "feet_r", "lid", "pem_lid", "screws_lid", "panel_", "screws_panel"), view=(-1.0, 0.9, 0.6), zoom=1.15)
shot("t_side.png", "Side section x-z (y=0)", hide=("lid", "pem_lid"), clip=((0, 1, 0), (0, 0, 0)), view=(0.0001, -1, 0), parallel=True, zoom=1.15, size=(1900, 1400))
print("ok")
