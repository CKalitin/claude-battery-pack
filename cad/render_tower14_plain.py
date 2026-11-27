"""FAST render of Claude battery pack v14: plain v1-v11 style (flat colours, edge lines), ~10 s/view. Default for iteration."""
import os, glob, sys
os.environ.setdefault("DISPLAY", ":99")
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_tower14")
IMG = os.path.join(OUT, "img"); os.makedirs(IMG, exist_ok=True)
RED, GRAPH = "#B0121C", "#3E4045"
MAT = {"cb_standoffs": ("#C9A94A", 0.5, 1), "screws_strap": ("#C9CCD1", 0.6, 1), "body_half": (RED, 0.7, 1), "lid": (RED, 0.7, 1), "plate": (GRAPH, 0.35, 1), "screws": ("#121214", 0.6, 1),
       "screws_lid": (RED, 0.6, 1), "feet": ("#0C0C0E", 0.1, 1), "pem": ("#B0B4BA", 0.6, 1), "ledboard": ("#1F6B2A", 0.2, 1),
       "pipe": ("#F3ECDD", 0.3, 1), "diffuser": ("#F4F1EA", 0.2, 0.85), "cell_": ("#2B6FC4", 0.3, 1),
       "g10": ("#C9C46A", 0.2, 1), "module_endplates": ("#9EA3AA", 0.5, 1), "rods": ("#C9CCD1", 0.7, 1), "rodnuts": ("#C9CCD1", 0.7, 1),
       "tnuts": ("#C9CCD1", 0.6, 1), "so_": ("#C9A94A", 0.5, 1), "bus_": ("#C8693A", 0.5, 1), "flex": ("#E0A035", 0.2, 1),
       "tray": ("#B8BCC2", 0.5, 1), "mylar": ("#E9E6DA", 0.1, 0.8), "inv_posts": ("#C9A94A", 0.5, 1),
       "charger": ("#8C9096", 0.4, 1), "inverter": ("#6E7278", 0.4, 1), "ctrl_pcb": ("#1E5631", 0.2, 1), "ctrl_": ("#1A1A1C", 0.3, 1),
       "ctrl_shunt": ("#B87333", 0.5, 1), "ctrl_fuse": ("#EDEDED", 0.2, 1), "panel_": ("#1A1A1C", 0.3, 1), "fan_": ("#6B4A3A", 0.3, 1),
       "cable_": ("#1C1C1E", 0.3, 1), "cable_inv_dc_pos": ("#C0282E", 0.3, 1), "cable_chg_dc_pos": ("#C0282E", 0.3, 1),
       "cable_dc_out": ("#C0282E", 0.3, 1), "cable_can": ("#2A6FD0", 0.3, 1), "screws_term": ("#C9CCD1", 0.6, 1),
       "plate_pos": ("#C8693A", 0.5, 1), "term_plates": ("#1A1A1C", 0.3, 1), "term_": ("#C8693A", 0.5, 1), "fuse_": ("#ECE7DA", 0.2, 1), "contactor": ("#232325", 0.3, 1), "mrbf": ("#D84A2A", 0.3, 1), "shunt_bar": ("#B87333", 0.5, 1), "shunt_module": ("#1E5631", 0.2, 1), "g10_power": ("#C9C46A", 0.2, 1), "antenna": ("#C9A94A", 0.4, 1), "panel_standoffs": ("#C9A94A", 0.5, 1), "screws_tap": ("#C9CCD1", 0.6, 1), "cable_ac": ("#3A3A3C", 0.3, 1), "cable_inv_dc_neg": ("#151517", 0.3, 1), "cable_chg_dc_neg": ("#151517", 0.3, 1), "plate_neg": ("#D9824F", 0.5, 1), "insulator": ("#C9C46A", 0.2, 0.9), "spacers_cu": ("#E09060", 0.5, 1)}

def mat(n):
    k = max((k for k in MAT if n.startswith(k)), key=len, default=None)
    return MAT.get(k, ("#888888", 0.2, 1))

def load(folder="stl"):
    return {os.path.basename(f)[:-4]: pv.read(f) for f in glob.glob(os.path.join(OUT, folder, "*.stl"))}

def shot(fname, title, meshes, hide=(), explode=None, view=(1.0, -1.15, 0.62), size=(1920, 1440), zoom=1.0, clip=None,
         focal=(-10, 0, 165), dist=750, edges=True):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("#141416", top="#3A3A40")
    p.enable_anti_aliasing("ssaa")
    for n, m in meshes.items():
        if any(n.startswith(h) for h in hide):
            continue
        if explode:
            off = next((v for k, v in sorted(explode.items(), key=lambda kv: -len(kv[0])) if n.startswith(k)), None)
            if off:
                m = m.translate(off, inplace=False)
        if clip is not None and n.startswith(clip[2]):
            m = m.clip(normal=clip[0], origin=clip[1], invert=True)
            if m.n_points == 0:
                continue
        col, spec, op = mat(n)
        p.add_mesh(m, color=col, opacity=op, smooth_shading=True, split_sharp_edges=True, specular=spec, specular_power=40,
                   ambient=0.18, diffuse=0.85)
        if edges and n.startswith(("plate", "body_half", "lid", "tray")):
            p.add_mesh(m.extract_feature_edges(25, boundary_edges=False, non_manifold_edges=False), color="#0A0A0B", line_width=1.0, opacity=0.7)
    v = view
    p.camera.position = (focal[0] + v[0] * dist, focal[1] + v[1] * dist, focal[2] + v[2] * dist)
    p.camera.focal_point = focal
    p.camera.up = (0, 0, 1)
    p.camera.zoom(zoom)
    f = os.path.join(IMG, fname)
    p.screenshot(f, scale=2)
    p.close()
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(f); d = ImageDraw.Draw(im)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 54); f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    except Exception:
        f1 = f2 = ImageFont.load_default()
    d.text((80, 60), title, fill="#EEEEEE", font=f1)
    d.text((80, 135), "Claude battery pack v14 (plain render)  |  4S2P EVE LF105, 12.8 V 210 Ah 2.69 kWh  |  500 A for 30 s", fill="#AAAAAA", font=f2)
    im.save(f)

if __name__ == "__main__":
    M = load()
    which = sys.argv[1:]
    hide = ("lid", "screws_lid", "pem_body_lid", "pem_lid_panel", "screws_panel", "panel_", "term_plates", "body_half_A",
            "plate_front", "screws_f", "ledboard", "diffuser", "pipe", "screws_panelmount", "panel_standoffs", "antenna")
    if "power" in which:
        shot("v14p_04_power_pcb.png", "Power train with the control board installed (z 262, over fuse + shunt)", M, hide=hide,
             view=(0.85, -1.0, 0.75), focal=(100, -20, 255), dist=520, zoom=1.0)
    if "conn" in which:
        shot("v14p_11_connections.png", "Converter wiring: + via MRBFs on the load bus, - to shunt node B; AC in/out to the lid", M,
             hide=hide + ("body_half_B",), view=(0.55, 1.0, 0.7), focal=(40, 10, 265), dist=560, zoom=1.0)
    if "top" in which:
        shot("v14p_08_terminals.png", "M10 terminals: both risers in one plane (x 62), holes at the same height, 114 mm apart", M,
             view=(0.9, -0.35, 0.55), focal=(65, 0, 330), dist=520, zoom=1.0)
    if "bays" in which:
        shot("v14p_12_service_bays.png", "Service bays: fan 18 mm | charger front 27 mm | inverter front 21-37 mm (section y = +30)", M,
             hide=hide + ("body_half_B",), view=(0.02, -1.4, 0.05), clip=((0, -1, 0), (0, 30.0, 0), ""), focal=(-10, 0, 255), dist=520, zoom=1.0)
    def keep(*pre):
        return {k: v for k, v in M.items() if k.startswith(pre)}
    if "all" in which or "hero" in which:
        shot("v14p_01_hero.png", "Claude battery pack v14", M, view=(1.0, -1.25, 0.55), focal=(0, 0, 175), dist=1150)
    if "all" in which or "rear" in which:
        shot("v14p_02_rear.png", "Rear: full grid, NF-A14 exhaust", M, view=(-1.1, 0.9, 0.45), focal=(0, 0, 175), dist=1150)
    if "all" in which or "open" in which:
        shot("v14p_03_lid_off.png", "Lid off", M, hide=("lid", "screws_lid", "pem_body_lid", "pem_lid_panel", "screws_panel", "panel_", "term_plates"),
             view=(0.9, -0.75, 1.05), focal=(20, 0, 245), dist=950, zoom=1.1)
    if "all" in which:
        shot("v14p_04_power_pcb.png", "Power train with the control board installed", M, hide=hide, view=(0.85, -1.0, 0.75), focal=(100, -20, 255), dist=520)
        bb = keep("cell_", "g10_spacers", "g10_top", "module_endplates", "rods", "rodnuts", "bus_A", "bus_B", "bus_C", "bus_pack", "screws_term", "screws_tap", "flex")
        shot("v14p_05_busbars.png", "4S2P busbars + sense flex (5 M3 taps, NTC on each tab)", bb, view=(0.55, -0.6, 1.3), focal=(0, 0, 200), dist=650)
        shot("v14p_06_front.png", "Front: checkerboard (lit + air holes)", M, view=(1.0, -0.35, 0.25), focal=(177, 0, 170), dist=650)
        shot("v14p_07_panel.png", "LED panel sandwich on module standoffs", M, hide=("plate_front", "screws_f", "pipe", "lid", "screws_lid", "panel_", "term_plates", "pem_lid_panel", "screws_panel"),
             view=(1.0, -0.6, 0.35), focal=(170, 0, 160), dist=600)
        shot("v14p_08_terminals.png", "Lid: M10 terminals in one plane, outlet, C14 inlet, push-button", M, view=(0.9, -0.35, 0.75), focal=(60, 0, 330), dist=600)
        shot("v14p_09_section.png", "Section at the fuse axis (y = -27.5)", M, view=(0.02, 1.4, 0.05), clip=((0, 1, 0), (0, -27.5, 0), ""), focal=(0, 0, 200), dist=950)
        ex = {"lid": (0, 0, 420), "screws_lid": (0, 0, 420), "pem_lid_panel": (0, 0, 420), "panel_": (0, 0, 470), "screws_panel": (0, 0, 490),
              "term_plates": (0, 0, 440), "ctrl_": (0, 0, 190), "cb_standoffs": (0, 0, 95), "inverter": (0, 0, 120), "tray2": (0, 0, 100), "inv_posts": (0, 0, 80), "cable_": (0, 0, 3000)}
        shot("v14p_10_pcb_exploded.png", "Control board lifted 190 mm from its spot above the fuse + shunt", M, explode=ex,
             hide=("body_half_A", "plate_front", "screws_f", "ledboard", "diffuser", "pipe", "screws_panelmount", "panel_standoffs", "antenna"),
             view=(0.75, -1.0, 0.85), focal=(90, -30, 300), dist=800)
        shot("v14p_11_connections.png", "Converter wiring: + via MRBFs, - to shunt node B", M, hide=hide + ("body_half_B",), view=(0.55, 1.0, 0.7), focal=(40, 10, 265), dist=560)
        shot("v14p_12_service_bays.png", "Service bays: fan 18 mm | charger 37 mm | inverter 31-47 mm", M, hide=hide + ("body_half_B",),
             view=(0.02, -1.4, 0.05), clip=((0, -1, 0), (0, 30.0, 0), ""), focal=(-15, 0, 255), dist=540)
