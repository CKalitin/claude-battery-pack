"""FAST render of Claude battery pack v15: plain v1-v11 style (flat colours, edge lines), ~10 s/view. Default for iteration."""
import os, glob, sys
os.environ.setdefault("DISPLAY", ":99")
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_tower15")
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
       "plate_pos": ("#C8693A", 0.5, 1), "term_plates": ("#1A1A1C", 0.3, 1), "term_": ("#C8693A", 0.5, 1), "fuse_": ("#ECE7DA", 0.2, 1), "contactor": ("#232325", 0.3, 1), "mrbf": ("#D84A2A", 0.3, 1), "shunt_bar": ("#B87333", 0.5, 1), "shunt_module": ("#1E5631", 0.2, 1), "g10_power": ("#C9C46A", 0.2, 1), "tray1_g10": ("#C9C46A", 0.2, 1), "g10_sb": ("#C9C46A", 0.2, 1), "sb175": ("#8A8D93", 0.3, 0.55), "bus_pack_pos": ("#D8452F", 0.5, 1), "bus_link": ("#D8452F", 0.5, 1), "bus_pos_out": ("#D8452F", 0.5, 1), "bus_pack_neg": ("#19B5C4", 0.5, 1), "bus_neg_out": ("#19B5C4", 0.5, 1), "cable_shunt_spi": ("#2FA84F", 0.3, 1), "cable_coil": ("#2FA84F", 0.3, 1), "cable_fan": ("#2FA84F", 0.3, 1), "ctrl_": ("#111113", 0.3, 1), "antenna": ("#C9A94A", 0.4, 1), "panel_standoffs": ("#C9A94A", 0.5, 1), "screws_tap": ("#C9CCD1", 0.6, 1), "cable_ac": ("#3A3A3C", 0.3, 1), "cable_inv_dc_neg": ("#151517", 0.3, 1), "cable_chg_dc_neg": ("#151517", 0.3, 1), "plate_neg": ("#D9824F", 0.5, 1), "insulator": ("#C9C46A", 0.2, 0.9), "spacers_cu": ("#E09060", 0.5, 1)}

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
    d.text((80, 135), "Claude battery pack v15 concept D (plain render)  |  4S2P EVE LF105, 12.8 V 210 Ah 2.69 kWh  |  175 A DC out", fill="#AAAAAA", font=f2)
    im.save(f)

if __name__ == "__main__":
    M = load()
    which = sys.argv[1:] or ["all"]
    lidoff = ("lid", "screws_lid", "pem_body_lid", "pem_lid_panel", "screws_panel", "panel_")
    front = ("plate_front", "screws_f", "diffuser", "pipe", "screws_panelmount", "antenna")
    if "all" in which or "hero" in which:
        shot("v15p_01_hero.png", "v15 concept D: SB175 output through the lid", M, view=(1.0, -1.25, 0.55), focal=(0, 0, 175), dist=1150)
    if "all" in which or "bay" in which:
        shot("v15p_02_bay_minus_side.png", "Power bay from the -y side: shunt + - bus (cyan), contactor + fuses (red)", M,
             hide=lidoff + front + ("body_half_A",), view=(0.35, -1.0, 0.55), focal=(105, 0, 250), dist=520)
    if "all" in which or "bay2" in which:
        shot("v15p_03_bay_top.png", "Power bay from above: - half (cyan) at -y, + half (red) at +y, SB175 between", M,
             hide=lidoff + front, view=(0.15, -0.25, 1.0), focal=(105, 0, 250), dist=560)
    if "all" in which or "pcb" in which:
        shot("v15p_04_front_pcb_back.png", "Front PCB back: control circuit faces the bay (z 222-285); flex tail and harnesses", M,
             hide=lidoff + ("plate_front", "screws_f", "diffuser", "pipe", "screws_panelmount", "body_half_B"), view=(-0.6, 1.0, 0.45), focal=(150, 0, 250), dist=520)
    if "all" in which or "path" in which:
        keep = {k: v for k, v in M.items() if k.startswith(("bus_", "shunt", "mrbf", "contactor", "sb175", "cell_"))}
        shot("v15p_05_current_path.png", "Current path only: cells -> + collector -> MRBF 250 -> GX12 -> + bus -> SB175; - band -> shunt -> - bus", keep,
             view=(0.55, -1.0, 1.0), focal=(30, 0, 225), dist=640)
    if "all" in which or "section" in which:
        shot("v15p_06_section.png", "Section y = -70: - band, riser tab and shunt outside the G10 tray", M,
             view=(0.02, -1.4, 0.05), clip=((0, -1, 0), (0, -70.0, 0), ""), focal=(40, 0, 230), dist=800)
