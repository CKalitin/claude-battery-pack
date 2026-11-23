import os, glob, sys
os.environ.setdefault("DISPLAY", ":99")
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_tower9")
IMG = os.path.join(OUT, "img_module"); os.makedirs(IMG, exist_ok=True)
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
       "plate_pos": ("#C8693A", 0.5, 1), "plate_neg": ("#D9824F", 0.5, 1), "insulator": ("#C9C46A", 0.2, 0.9), "spacers_cu": ("#E09060", 0.5, 1)}

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
    d.text((80, 135), "Tower A v9 cell module  |  4S1P EVE LF105, 12.8 V 105 Ah 1.34 kWh  |  187 x 164 x 212 mm  |  10.4 kg", fill="#AAAAAA", font=f2)
    im.save(f)


if __name__ == "__main__":
    keep = ("cell_", "g10", "module_endplates", "tnuts", "rods", "rodnuts", "so_lower", "so_studs", "bus_", "screws_term", "flex_ccs")
    M = {k: v for k, v in load().items() if k.startswith(keep)}
    F = (0, 0, 105)
    which = sys.argv[1:] or ["all"]
    def want(n): return "all" in which or n in which
    if want("hero"):
        shot("m01_hero.png", "Cell module: 4 x LF105 upright, busbars on top", M, view=(1.0, -1.15, 0.75), zoom=1.9, focal=F)
    if want("rear"):
        shot("m02_rear_left.png", "Rear-left: pack- strap runs along the +y edge to the front", M, view=(-1.1, 1.0, 0.7), zoom=1.9, focal=F)
    if want("exploded"):
        ex = {"g10_top": (0, 0, 70), "bus_": (0, 0, 130), "screws_term": (0, 0, 185), "flex_ccs": (0, 0, 100),
              "so_lower": (0, 0, 40), "so_studs": (0, 0, 40), "g10_frame": (0, 0, -35), "g10_floor": (0, 0, -70),
              "rods": (0, -130, 0), "rodnuts": (0, -130, 0), "tnuts": (0, 0, 0)}
        shot("m03_exploded.png", "Exploded: floor / frame / cells + spacers / top plate / flex / busbars / M6", M, explode=ex,
             view=(1.0, -1.2, 0.55), zoom=1.2, focal=(0, -40, 140), dist=950)
    if want("top"):
        shot("m04_top.png", "Top: series chain, alternating poles, flex CCS spine at y = -21", M, view=(0.001, -0.001, 1.5), zoom=2.1, focal=(0, 0, 215))
    if want("end"):
        shot("m05_end.png", "Front end plate: M5 tie rods, T-slot nuts, standoffs to the top plate", M, view=(1.5, 0.001, 0.15), zoom=2.0, focal=F)
    if want("side"):
        shot("m06_side.png", "Side: 4 cells, 1.6 mm G10 spacers, 7.95 mm 6061 end plates", M, view=(0.001, -1.5, 0.12), zoom=2.0, focal=F)
    if want("detail"):
        shot("m07_terminals.png", "Detail: M6 terminal screws, links, pack+ strap, sense tabs", M, view=(0.9, -0.8, 0.9), zoom=3.0, focal=(45, 10, 200))
    if want("section"):
        shot("m08_section.png", "Section y = 33.5 through the + terminals", M, view=(0.001, -1.5, 0.12), zoom=2.0, focal=F,
             clip=((0, -1, 0), (0, 33.5, 0), ""))
