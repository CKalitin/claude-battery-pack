"""Exploded views of Claude battery pack v4, one per subsystem. Reuses the material table from render_tower2.py."""
import os, glob
import numpy as np
import pyvista as pv

_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_tower2.py")).read()
exec(_src[:_src.index("EXPLODE")])          # D, OUT, MAT, mat()
def mat(n):
    best = max((k for k in MAT if n.startswith(k)), key=len, default=None)
    return MAT.get(best, ("#888888", 0.2, 1))

EX = os.path.join(OUT, "exploded")
os.makedirs(EX, exist_ok=True)
MESH = {os.path.basename(f)[:-4]: pv.read(f) for f in glob.glob(os.path.join(OUT, "stl", "*.stl"))}


from PIL import Image, ImageDraw, ImageFont
def _font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def annotate(path, title, sub, disp, txt):
    """Margin labels with leader lines (no overlaps), title block top-left."""
    im = Image.open(path).convert("RGB"); W, H = im.size; d = ImageDraw.Draw(im)
    f = _font(int(W / 95)); ft = _font(int(W / 55)); fs = _font(int(W / 140))
    d.text((int(W * 0.025), int(H * 0.025)), title, fill=(238, 238, 238), font=ft)
    d.text((int(W * 0.025), int(H * 0.025) + int(W / 55) + 18), sub, fill=(150, 150, 156), font=fs)
    items = sorted(zip(disp, txt), key=lambda t: t[0][1])
    side = {"L": [], "R": []}
    for (x, y), t in items:
        side["L" if x < W / 2 else "R"].append([x, y, t])
    gap = int(W / 95 * 1.9)
    for k, lst in side.items():
        ys = []
        y_min = H * 0.12
        for it in lst:
            ly = max(it[1], y_min if not ys else ys[-1] + gap)
            ys.append(ly)
        over = ys[-1] - H * 0.96 if ys else 0
        if over > 0:
            ys = [v - over for v in ys]
        for it, ly in zip(lst, ys):
            x, y, t = it
            tw = d.textlength(t, font=f)
            lx = W * 0.03 if k == "L" else W * 0.97 - tw
            ax = lx + tw + 14 if k == "L" else lx - 14
            d.line([(ax, ly), (x, y)], fill=(200, 200, 205), width=3)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 196, 64))
            d.rectangle([lx - 10, ly - int(W / 95 * 0.75), lx + tw + 10, ly + int(W / 95 * 0.75)], fill=(28, 28, 32))
            d.text((lx, ly), t, fill=(242, 242, 242), font=f, anchor="lm")
    im.save(path)

def rule_for(name, rules):
    best = max((k for k in rules if name.startswith(k)), key=len, default=None)
    return rules.get(best) if best is not None else None


def place(name, m, rule):
    """rule: dict with optional t=(dx,dy,dz) translate, s=(axis, factor, centre) spread each body about centre."""
    if rule is None:
        return m
    if "s" in rule:
        ax, f, c0 = rule["s"]
        bodies = m.split_bodies()
        parts = []
        for b in bodies:
            b = b.extract_surface()
            off = [0.0, 0.0, 0.0]
            off[ax] = f * (b.center[ax] - c0)
            parts.append(b.translate(off, inplace=False))
        m = parts[0].merge(parts[1:]) if len(parts) > 1 else parts[0]
    if "t" in rule:
        m = m.translate(rule["t"], inplace=False)
    return m


def shot(fname, title, rules, only=None, hide=(), view=(1.0, -1.2, 0.8), zoom=1.0, labels=None,
         size=(2000, 1700), ghost=(), sub=None, focal=None, dist=400):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("#141416", top="#3A3A40")
    p.enable_anti_aliasing("ssaa")
    placed = {}
    for n, m in sorted(MESH.items()):
        if only is not None and not any(n.startswith(k) for k in only):
            continue
        if any(n.startswith(h) for h in hide):
            continue
        m = place(n, m, rule_for(n, rules))
        placed[n] = m
        col, spec, op = mat(n)
        if any(n.startswith(g) for g in ghost):
            op = 0.18
        p.add_mesh(m, color=col, opacity=op, smooth_shading=True, split_sharp_edges=True,
                   specular=spec, specular_power=40, ambient=0.2, diffuse=0.85)
        if op > 0.5:
            p.add_mesh(m.extract_feature_edges(40, boundary_edges=False, non_manifold_edges=False),
                       color="#0A0A0B", line_width=0.6, opacity=0.5)
    allb = np.array([m.bounds for m in placed.values()])
    c = focal or [(allb[:, 0].min() + allb[:, 1].max()) / 2, (allb[:, 2].min() + allb[:, 3].max()) / 2,
                  (allb[:, 4].min() + allb[:, 5].max()) / 2]
    v = np.array(view, float)
    v /= np.linalg.norm(v)
    p.camera.focal_point = c
    p.camera.position = list(np.array(c) + v * 2500)
    p.camera.up = (0, 0, 1)
    if focal is None:
        p.reset_camera()
    else:
        p.camera.position = list(np.array(c) + v * dist)
        p.reset_camera_clipping_range()
    p.camera.zoom(zoom)
    pts, txt = [], []
    for pref, spec in (labels or {}).items():
        lab, dz = spec[0], spec[1]
        fx, fy, fz = spec[2] if len(spec) > 2 else (0.5, 0.5, 1.0)
        ms = [m for n, m in placed.items() if n.startswith(pref)]
        if not ms:
            continue
        bb = np.array([m.bounds for m in ms])
        lo = [bb[:, 0].min(), bb[:, 2].min(), bb[:, 4].min()]
        hi = [bb[:, 1].max(), bb[:, 3].max(), bb[:, 5].max()]
        pts.append([lo[0] + fx * (hi[0] - lo[0]), lo[1] + fy * (hi[1] - lo[1]), lo[2] + fz * (hi[2] - lo[2]) + dz])
        txt.append(lab)
    p.render()
    SC = 2
    disp = []
    import vtk
    for q in pts:
        co = vtk.vtkCoordinate(); co.SetCoordinateSystemToWorld(); co.SetValue(*q)
        x, y = co.GetComputedDoubleDisplayValue(p.renderer)
        disp.append((x * SC, (size[1] - y) * SC))
    path = os.path.join(EX, fname)
    p.screenshot(path, scale=SC)
    annotate(path, title, sub or "Claude battery pack v4  |  1.28 kWh 8S LFP  |  build123d", disp, txt)
    p.close()
    print("ok", fname)



EL = {"inverter": {"t": (0, 0, 190)}, "tray2": {"t": (0, 0, 140)}, "inv_posts": {"t": (0, 0, 70)},
      "charger": {"t": (0, 0, 115)}, "ctrl_": {"t": (0, 0, 45)}, "screws_trays": {"t": (0, 0, 45)},
      "tray1": {}, "pem_tray1": {}, "mica_tray": {"t": (0, 0, -25)}}
shot("p01_tray1_pem.png", "Tray 1 with pressed-in PEM hardware: no loose screws underneath", EL,
     only=("tray1", "pem_tray1", "inv_posts", "ctrl_pcb", "ctrl_terminals", "ctrl_contactor", "mica_tray", "charger"),
     ghost=("charger",), view=(1.0, -1.1, 0.75), zoom=1.15,
     labels={"pem_tray1": ("8x PEM: 4 FH-M4 studs + 4 SO-M3 standoffs", 0, (0.85, 0.2, 0.2)),
             "inv_posts": ("Inverter posts spin onto studs", 0, (0, 0, 1)),
             "ctrl_pcb": ("Control board screws into SO standoffs", 0, (1, 0, 0.5)),
             "tray1": ("Tray 1 (5052)", 0, (0.2, 0, 0.5)), "mica_tray": ("Mica sheet", 0, (0.5, 0, 0))})
LID = {"panel_": {"t": (0, 0, 120)}, "screws_panel": {"t": (0, 0, 185)}, "pem_lid_panel": {}, "pem_lid": {"t": (0, 0, -45)},
       "screws_lid": {"s": (1, 0.9, 0), "t": (0, 0, -45)}}
shot("p02_lid_pem_from_below.png", "Lid from below: 8 CLS-M3 clinch nuts behind the panel connectors", LID,
     only=("lid", "panel_", "screws_panel", "pem_lid_panel"), view=(0.7, -0.8, -0.9), zoom=1.2,
     labels={"pem_lid_panel": ("8x CLS-M3 nuts pressed into lid", 0, (0.5, 0.5, 0)),
             "panel_dc": ("Anderson SB50", 0, (1, 0, 0.5)), "panel_outlet": ("NEMA 5-15R", 0, (0, 0, 0.5)),
             "lid": ("Lid (inside face)", 0, (0.15, 0, 0.6))})
