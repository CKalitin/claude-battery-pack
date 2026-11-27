import os, glob, sys
os.environ.setdefault("DISPLAY", ":99")
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_tower6")
IMG = os.path.join(OUT, "img"); os.makedirs(IMG, exist_ok=True)
RED, GRAPH = "#B0121C", "#3E4045"
MAT = {"body_half": (RED, 0.7, 1), "lid": (RED, 0.7, 1), "plate": (GRAPH, 0.35, 1), "screws": ("#121214", 0.6, 1),
       "screws_lid": (RED, 0.6, 1), "feet": ("#0C0C0E", 0.1, 1), "pem": ("#B0B4BA", 0.6, 1), "ledboard": ("#1F6B2A", 0.2, 1),
       "pipe": ("#F3ECDD", 0.3, 1), "diffuser": ("#F4F1EA", 0.2, 0.85), "cell_": ("#2B6FC4", 0.3, 1),
       "g10": ("#C9C46A", 0.2, 1), "module_endplates": ("#9EA3AA", 0.5, 1), "rods": ("#C9CCD1", 0.7, 1), "rodnuts": ("#C9CCD1", 0.7, 1),
       "tnuts": ("#C9CCD1", 0.6, 1), "so_": ("#C9A94A", 0.5, 1), "bus_": ("#C8693A", 0.5, 1), "flex": ("#E0A035", 0.2, 1),
       "tray": ("#B8BCC2", 0.5, 1), "mylar": ("#E9E6DA", 0.1, 0.8), "inv_posts": ("#C9A94A", 0.5, 1),
       "charger": ("#8C9096", 0.4, 1), "inverter": ("#6E7278", 0.4, 1), "ctrl_pcb": ("#1E5631", 0.2, 1), "ctrl_": ("#1A1A1C", 0.3, 1),
       "ctrl_shunt": ("#B87333", 0.5, 1), "ctrl_fuse": ("#EDEDED", 0.2, 1), "panel_": ("#1A1A1C", 0.3, 1), "fan_": ("#6B4A3A", 0.3, 1),
       "cable_": ("#1C1C1E", 0.3, 1), "cable_inv_dc_pos": ("#C0282E", 0.3, 1), "cable_chg_dc_pos": ("#C0282E", 0.3, 1),
       "cable_dc_out": ("#C0282E", 0.3, 1), "cable_can": ("#2A6FD0", 0.3, 1), "screws_term": ("#C9CCD1", 0.6, 1),
       "plate_pos": ("#C8693A", 0.5, 1), "plate_neg": ("#D9824F", 0.5, 1), "insulator": ("#C9C46A", 0.2, 0.9), "spacers_cu": ("#E09060", 0.5, 1)}

def mat(n):
    k = max((k for k in MAT if n.startswith(k)), key=len, default=None)
    return MAT.get(k, ("#888888", 0.2, 1))

def load(folder="stl"):
    return {os.path.basename(f)[:-4]: pv.read(f) for f in glob.glob(os.path.join(OUT, folder, "*.stl"))}

def shot(fname, title, meshes, hide=(), explode=None, view=(1.0, -1.15, 0.62), size=(1920, 1440), zoom=1.0, clip=None,
         focal=(-10, 0, 140), dist=750, edges=True):
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
    d.text((80, 135), "Claude battery pack v6  |  4S1P EVE LF100MA on edge, 12.8 V 1.28 kWh  |  180 x 269 body  |  all SendCutSend", fill="#AAAAAA", font=f2)
    im.save(f)

MAT.update({"g10_frame": ("#C9C46A", 0.2, 1), "screws_strap": ("#C9CCD1", 0.6, 1)})
if __name__ == "__main__":
    M = load()
    which = sys.argv[1:] or ["hero", "section", "xmod", "xif", "busside"]
    if "hero" in which:
        shot("v6_01_hero.png", "v6 hero: 180 x 269 body, the old tall proportion back", M, zoom=1.3, focal=(-10, 0, 150))
    if "section" in which:
        shot("v6_02_section.png", "Section x = 20: cells on edge, busbars on the +y side", M, view=(1.4, -0.3, 0.25),
             clip=((1, 0, 0), (20.0, 0, 0), ""), zoom=1.25, focal=(0, 0, 140))
    keep = ("cell_", "g10", "module_end", "rods", "rodnuts", "tnuts", "bus_", "screws_term", "screws_strap", "flex", "screws_hold",
            "tray1", "mylar", "pem_tray1", "ctrl_", "screws_trays")
    mm = {k: v for k, v in M.items() if k.startswith(keep)}
    if "xmod" in which:
        ex = {"bus_link": (0, 70, 0), "bus_pack": (0, 70, 0), "screws_term": (0, 115, 0), "flex_ccs": (0, 95, 0),
              "g10_frame_top": (0, 0, 45), "mylar": (0, 0, 75), "tray1": (0, 0, 95), "pem_tray1": (0, 0, 95), "screws_trays": (0, 0, 175),
              "ctrl_": (0, 0, 150), "screws_strap": (0, 0, 205), "g10_floor": (0, 0, -40), "screws_hold": (0, 0, -70),
              "g10_frame_bot": (0, 0, -20), "module_endplates": (0, 0, 0), "rods": (0, 0, 0), "rodnuts": (0, 0, 0)}
        for i in range(4):
            ex[f"cell_{i+1}"] = (0, 0, 0)
        shot("v6_03_exploded_module.png", "Exploded: battery module + tray 1 + control board (busbar side)", mm, explode=ex,
             view=(0.75, 1.25, 0.55), zoom=1.05, focal=(10, 40, 140))
    if "xif" in which:
        ex = {"ctrl_": (0, 0, 60), "screws_strap": (0, 0, 100), "screws_trays": (0, 0, 0)}
        mi = {k: v for k, v in mm.items()}
        shot("v6_04_board_interface.png", "Interface: pack+ / pack- straps bend under the board, M6 through board, nut under tab", mi,
             explode=ex, view=(0.9, 1.0, 0.65), zoom=3.0, focal=(85, 55, 170))
    if "busside" in which:
        shot("v6_05_busbar_side.png", "Busbar side, assembled: 3 links, 2 straps, flex CCS", mm, view=(0.15, 1.4, 0.2), zoom=1.7, focal=(10, 60, 110))
