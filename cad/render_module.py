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



MODR = {"int_cell_": {"s": (0, 0.55, 0)}, "int_comp_insul": {"s": (0, 0.55, 0)}, "int_comp_endplates": {"s": (0, 0.75, 0)},
        "int_tnuts": {"s": (0, 0.98, 0)}, "int_comp_rodnuts": {"s": (0, 0.95, 0)}, "int_comp_rods": {},
        "int_comp_pcb_standoffs": {"s": (0, 0.75, 0), "t": (0, 0, 22)}, "int_so_studs": {"s": (0, 0.75, 0), "t": (0, 0, 22)},
        "int_g10_top": {"t": (0, 0, 45)}, "int_so_upper": {"s": (0, 0.75, 0), "t": (0, 0, 100)},
        "int_busbar_": {"s": (0, 0.55, 0), "t": (0, 0, 95)}, "int_busbar_screws": {"s": (0, 0.55, 0), "t": (0, 0, 140)},
        "int_flex": {"t": (0, 0, 118)}, "int_pack_": {"t": (0, 0, 165)},
        "int_g10_frame": {"t": (0, 0, -40)}, "int_g10_floor": {"t": (0, 0, -75)},
        "screws_hold": {"s": (0, 0.75, 0), "t": (0, 0, -135)}}
ONLY = ("int_so_upper", "int_cell", "int_comp", "int_busbar", "int_flex", "int_pack", "int_g10", "int_tnuts", "int_so_studs", "screws_hold")
LAB = {"int_cell_1": ("Cell 1 (pack -)", 6), "int_cell_8": ("Cell 8 (pack +)", 6),
       "int_comp_endplates": ("8 mm 6061 end plates, laser T-slots", 6, (1, 0, 1)),
       "int_tnuts": ("8x M4 square nuts (captive)", 0, (1, 0, 0)),
       "int_comp_rods": ("4x M5 tie rods: x clamp", 0, (0.55, 0, 0)),
       "int_comp_rodnuts": ("Rod nuts", 0, (0, 0, 0)),
       "int_g10_top": ("G10 top plate: x/y at terminals, z-stop, clamped", 6, (0.35, 0, 1)),
       "int_so_upper": ("Upper 9 mm standoffs (clamp plate)", 6, (1, 1, 1)),
       "int_busbar_": ("Copper busbars", 0, (0.9, 0, 0.5)),
       "int_busbar_screws": ("16x M4 terminal screws", 6, (0.15, 0.5, 1)),
       "int_flex": ("Flex sense CCS + NTCs", 6, (0.6, 0.5, 1)),
       "int_pack_": ("Pack- return bar", 6, (0.3, 0.5, 1)),
       "int_comp_pcb_standoffs": ("Lower 10 mm standoffs into T-slot nuts", 6, (1, 0, 1)),
       "int_comp_insul": ("1 mm G10 separators", 6, (0.0, 0, 1)),
       "int_g10_frame": ("G10 frame: bottom x/y locator", 0, (0.5, 0, 0)),
       "int_g10_floor": ("G10 floor 4.75 mm: z support + insulation", 0, (0.5, 0, 0)),
       "screws_hold": ("4x M4 hold-down into T-slot nuts", -8, (1, 0, 0))}
shot("m01_module_exploded.png", "Cell module, exploded: no printed parts", MODR, only=ONLY, view=(0.8, -1.3, 0.75), zoom=1.05,
     labels=LAB, size=(2000, 1700))
shot("m02_module_exploded_below.png", "Cell module from below: floor, frame, T-slots, hold-downs", MODR, only=ONLY,
     view=(0.7, -1.2, -0.65), zoom=1.05, size=(2000, 1700),
     labels={"int_g10_floor": ("G10 floor", 0, (0.5, 0, 0)), "int_g10_frame": ("G10 frame", 0, (0.5, 0, 0)),
             "int_tnuts": ("Square nuts", 0, (1, 0, 0)), "screws_hold": ("Hold-down screws", 0, (1, 0, 0)),
             "int_comp_endplates": ("T-slots in end plates", 0, (1, 0, 0))})
shot("m03_module_assembled.png", "Cell module, assembled", {}, only=ONLY, view=(0.8, -1.3, 0.75), zoom=1.25, size=(2000, 1600))
shot("m04_tslot_detail.png", "Detail: laser-cut T-slots + captive square nuts in the module end plate",
     {"int_tnuts": {"s": (0, 1.18, 0)}, "screws_hold": {"t": (0, 0, -30)}, "int_so_studs": {"t": (0, 0, 30)},
      "int_comp_pcb_standoffs": {"t": (0, 0, 30)}, "int_so_upper": {"t": (0, 0, 60)}},
     only=("int_comp_endplates", "int_tnuts", "screws_hold", "int_so_studs", "int_comp_pcb_standoffs"),
     view=(1.0, -0.42, 0.12), zoom=1.0, size=(1800, 1600), focal=(150.0, 0, 95), dist=520,
     labels={"int_tnuts": ("M4 square nuts: slide in from the face", 0, (1, 0.25, 0.04)),
             "screws_hold": ("Hold-down screws (from under the U floor)", 0, (1, 0.3, 0.3)),
             "int_so_studs": ("Tray standoffs thread into top nuts", 0, (1, 0.9, 0.1)),
             "int_comp_endplates": ("T-slot: profile cut, no edge tapping", 0, (1, 0.24, 0.0))})
