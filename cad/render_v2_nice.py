"""Studio renders of Claude battery pack v12: PBR materials, procedural studio environment map, SSAO, ground shadow."""
import os, sys, glob
os.environ.setdefault("DISPLAY", ":99")
import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(D, "out_tower", "stl")
OUT = os.path.join(D, "out_tower", "img_nice"); os.makedirs(OUT, exist_ok=True)
ENV = os.path.join(OUT, "_env"); os.makedirs(ENV, exist_ok=True)

# ---------- procedural studio cube map: soft grey gradient + two softboxes ----------
def face(kind, n=512):
    y = np.linspace(0, 1, n)[:, None]
    base = (0.26 + 0.12 * (1 - y)) * np.ones((n, n))            # darker toward the floor
    if kind == "top":
        base = 0.42 * np.ones((n, n))
        xx, yy = np.meshgrid(np.linspace(-1, 1, n), np.linspace(-1, 1, n))
        base += 0.9 * np.exp(-((xx / 0.45) ** 8 + (yy / 0.25) ** 8))   # overhead strip softbox
    if kind == "bottom":
        base = 0.18 * np.ones((n, n))
    if kind == "side_box":
        xx, yy = np.meshgrid(np.linspace(-1, 1, n), np.linspace(-1, 1, n))
        base += 0.75 * np.exp(-((xx / 0.35) ** 8 + ((yy + 0.2) / 0.5) ** 8))  # key softbox
    img = (np.clip(base, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([img, img, (img * 1.02).clip(0, 255).astype(np.uint8)]))
names = {"posx": "side_box", "negx": "side", "posy": "top", "negy": "bottom", "posz": "side", "negz": "side_box"}
paths = []
for k in ("posx", "negx", "posy", "negy", "posz", "negz"):
    p = os.path.join(ENV, f"{k}.png"); face(names[k]).save(p); paths.append(p)
CUBE = pv.cubemap_from_filenames(paths)

# ---------- materials: (color, metallic, roughness, opacity) ----------
RED = "#B0101A"
MAT = [
    ("u_body", RED, 0.05, 0.42, 1), ("int_cell", "#2C67B8", 0.1, 0.35, 1), ("int_busbar", "#C96E3E", 1.0, 0.25, 1), ("int_carrier", "#3A3A3E", 0.0, 0.6, 1),
    ("int_power_pcb", "#1C5B33", 0.0, 0.35, 1), ("int_bms_pcb", "#1C5B33", 0.0, 0.35, 1), ("int_comp_endplates", "#B9BEC5", 0.9, 0.35, 1),
    ("int_mica", "#D9D0B0", 0.0, 0.5, 1), ("int_liner", "#ECE9DE", 0.0, 0.5, 1), ("tabs", "#B9BEC5", 0.9, 0.35, 1), ("int_pwr", "#1B1B1D", 0.0, 0.45, 1),
    ("body_half", RED, 0.05, 0.42, 1), ("lid", RED, 0.05, 0.42, 1), ("screws_lid", RED, 0.15, 0.3, 1),
    ("plate", "#3A3D42", 0.55, 0.45, 1), ("feet", "#111113", 0.0, 0.8, 1),
    ("screws", "#18181A", 0.6, 0.35, 1), ("pem", "#C9CDD2", 0.9, 0.3, 1),
    ("cell_", "#2C67B8", 0.1, 0.35, 1), ("g10", "#C4B95A", 0.0, 0.55, 1),
    ("module_endplates", "#B9BEC5", 0.9, 0.35, 1), ("rods", "#D6D9DD", 1.0, 0.2, 1), ("rodnuts", "#D6D9DD", 1.0, 0.25, 1),
    ("tnuts", "#D6D9DD", 1.0, 0.3, 1), ("so_", "#C8A64A", 1.0, 0.3, 1), ("bus_", "#C96E3E", 1.0, 0.25, 1),
    ("flex", "#E2A23A", 0.0, 0.4, 1), ("tray", "#C6CAD0", 0.9, 0.35, 1), ("mylar", "#ECE9DE", 0.0, 0.5, 0.85),
    ("inv_posts", "#C8A64A", 1.0, 0.3, 1), ("charger", "#9A9EA4", 0.85, 0.4, 1), ("inverter", "#7E8288", 0.85, 0.4, 1),
    ("ctrl_pcb", "#1C5B33", 0.0, 0.35, 1), ("ctrl_shunt", "#B8743A", 1.0, 0.3, 1), ("ctrl_fuse", "#EDEDED", 0.0, 0.4, 1),
    ("ctrl_", "#1B1B1D", 0.0, 0.45, 1), ("cb_standoffs", "#C8A64A", 1.0, 0.3, 1),
    ("panel_", "#141416", 0.0, 0.5, 1), ("fan_", "#6A4A3A", 0.0, 0.5, 1),
    ("cable_inv_dc_pos", "#C0282E", 0.0, 0.45, 1), ("cable_chg_dc_pos", "#C0282E", 0.0, 0.45, 1), ("cable_dc_out", "#C0282E", 0.0, 0.45, 1),
    ("cable_can", "#2A6FD0", 0.0, 0.45, 1), ("cable_", "#1C1C1E", 0.0, 0.5, 1),
    ("ledboard", "#1F6B2A", 0.0, 0.4, 1), ("pipe", "#F3ECDD", 0.0, 0.2, 1), ("diffuser", "#F4F1EA", 0.0, 0.3, 0.9),
    ("screws_term", "#D6D9DD", 1.0, 0.25, 1), ("screws_strap", "#D6D9DD", 1.0, 0.25, 1),
]
def mat(n):
    best = max((m for m in MAT if n.startswith(m[0])), key=lambda m: len(m[0]), default=(None, "#888888", 0.0, 0.5, 1))
    return best[1:]

M = {os.path.basename(f)[:-4]: pv.read(f) for f in glob.glob(os.path.join(STL, "*.stl")) if os.path.getsize(f) > 100}
B = np.array([m.bounds for m in M.values()])
ZMIN = B[:, 4].min()

def shot(fname, title, keep=None, hide=(), explode=None, view=(1.0, -1.1, 0.6), focal=(0, 0, 150), dist=900, zoom=1.0,
         clip=None, floor=True, sub="Claude battery pack v2-v3  |  8S1P EVE LF50K, 25.6 V 50 Ah 1.28 kWh  |  R22 rolled corners, joggle lid"):
    p = pv.Plotter(off_screen=True, window_size=(1920, 1440), lighting="none")
    p.set_background("black")
    p.set_environment_texture(CUBE, is_srgb=True)
    for pos, inten in (((900, -1100, 1300), 1.6), ((-1200, 600, 700), 0.7), ((200, 1400, 300), 0.6)):
        p.add_light(pv.Light(position=pos, focal_point=focal, intensity=inten, positional=False))
    for n, m in M.items():
        if keep and not n.startswith(keep):
            continue
        if any(n.startswith(h) for h in hide):
            continue
        if explode:
            off = next((v for k, v in sorted(explode.items(), key=lambda kv: -len(kv[0])) if n.startswith(k)), None)
            if off:
                m = m.translate(off, inplace=False)
        if clip is not None:
            m = m.clip(normal=clip[0], origin=clip[1], invert=True)
            if m.n_points == 0:
                continue
        col, met, rough, op = mat(n)
        p.add_mesh(m, color=col, pbr=True, metallic=met, roughness=rough, opacity=op, smooth_shading=True,
                   split_sharp_edges=True, feature_angle=30)
    if False:
        fl = pv.Disc(center=(focal[0], focal[1], ZMIN - 0.5), inner=0, outer=900, normal=(0, 0, 1), c_res=120)
        p.add_mesh(fl, color="#2E2F33", pbr=True, metallic=0.0, roughness=0.95)
    p.camera.position = tuple(np.array(focal) + np.array(view) / np.linalg.norm(view) * dist)
    p.camera.focal_point = focal
    p.camera.up = (0, 0, 1)
    p.camera.view_angle = 24
    p.camera.zoom(zoom)
    p.enable_ssao(radius=12, bias=0.5, kernel_size=128, blur=True)
    p.enable_anti_aliasing("ssaa")
    f = os.path.join(OUT, fname)
    p.screenshot(f, scale=2, transparent_background=True)
    p.close()
    fg = Image.open(f).convert("RGBA")
    W, Hh = fg.size
    yy = np.linspace(0, 1, Hh)[:, None]
    top, bot = np.array([70, 72, 78]), np.array([44, 45, 50])
    bgarr = (top * (1 - yy) + bot * yy)[:, None, :].repeat(W, axis=1).reshape(Hh, W, 3)
    xx = np.linspace(-1, 1, W)[None, :]
    vign = 1 - 0.25 * (xx ** 2)
    bgarr = (bgarr * vign[..., None]).clip(0, 255).astype(np.uint8)
    bg = Image.fromarray(bgarr).convert("RGBA")
    if floor:
        from PIL import ImageFilter
        a = np.array(fg)[..., 3]
        rows = np.where(a.max(axis=1) > 0)[0]
        if len(rows):
            ybot = rows.max()
            cols = np.where(a[max(ybot - 40, 0):ybot + 1].max(axis=0) > 0)[0]
            sh = Image.new("L", (W, Hh), 0); sd = ImageDraw.Draw(sh)
            cx, wid = (cols.min() + cols.max()) / 2, (cols.max() - cols.min())
            sd.ellipse([cx - wid * 0.62, ybot - 40, cx + wid * 0.62, ybot + 60], fill=235)
            sh = sh.filter(ImageFilter.GaussianBlur(45))
            drop = Image.fromarray(a).filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.35))
            sh = Image.fromarray(np.maximum(np.array(sh), np.array(drop)))
            black = Image.new("RGBA", (W, Hh), (8, 8, 10, 255))
            bg = Image.composite(black, bg, sh)
    im = Image.alpha_composite(bg, fg).convert("RGB"); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 58)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    d.text((90, 70), title, fill="#F2F2F2", font=f1)
    d.text((92, 150), sub, fill="#B4B4B8", font=f2)
    im.save(f)
    print(fname)

if __name__ == "__main__":
    shot("v02_01_hero.png", "Claude battery pack v2-v3: first exterior", view=(1.0, -1.25, 0.55), focal=(0, 0, 140), dist=1500)
    shot("v02_02_cutaway.png", "v2-v3 cutaway: v1 internal stack inside the tower", clip=((0, -1, 0), (0, 0, 0)), view=(0.4, -1.0, 0.35), focal=(0, 0, 140), dist=1500, floor=False)
