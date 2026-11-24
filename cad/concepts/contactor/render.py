"""Fast labelled renders of a contactor concept inside the v15 context. Labels only on parts that are visible."""
import os, sys, glob
os.environ.setdefault("DISPLAY", ":99")
import numpy as np
import pyvista as pv
HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CAD)
from render_tower15_plain import place_labels, mat as v15mat   # same label placer and palette as the v15 renders

CTX_STL = os.path.join(CAD, "out_tower15", "stl")
OUT = os.path.join(HERE, "out")
CTX_KEEP = ("cell_", "bus_A", "bus_B", "bus_C", "g10_top", "flex_ccs", "charger", "inverter", "tray2", "body_half_A",
            "module_endplates", "ledboard_f", "ctrl_", "so_upper", "inv_posts", "screws_term")
LID_KEEP = ("lid", "panel_")
COL = {"pos": "#D8452F", "neg": "#19B5C4", "ins": "#C9C46A", "other": "#2A2A2D"}
SPECIAL = {"contactor": ("#232325", 0.3, 1), "fet": ("#1E5631", 0.2, 1), "sb175": ("#8A8D93", 0.3, 1), "mrbf": ("#E8E2D0", 0.2, 1),
           "shunt_module": ("#1E5631", 0.2, 1), "path_pos": ("#FFD23F", 0.1, 1), "path_neg": ("#7CF2FF", 0.1, 1),
           "cable_out_pos": ("#C0282E", 0.3, 1), "cable_out_neg": ("#151517", 0.3, 1), "lid_ghost": ("#B0121C", 0.3, 0.18),
           "mlrbs_knob": ("#D8452F", 0.3, 1)}

def mat(n, role):
    k = max((k for k in SPECIAL if n.startswith(k)), key=len, default=None)
    if k:
        return SPECIAL[k]
    if role in COL and role != "other":
        return (COL[role], 0.5, 1)
    return v15mat(n)

def load(key, roles, with_lid=False):
    M = {}
    for f in sorted(glob.glob(os.path.join(CTX_STL, "*.stl"))):
        n = os.path.basename(f)[:-4]
        if n.startswith(CTX_KEEP) or (with_lid and n.startswith(LID_KEEP)):
            M[n] = (pv.read(f), "ctx")
    for f in sorted(glob.glob(os.path.join(OUT, key, "*.stl"))):
        n = os.path.basename(f)[:-4]
        M[n] = (pv.read(f), roles.get(n, "path" if n.startswith("path_") else "other"))
    return M

def shot(key, roles, labels, fname, title, subtitle, view=(1.0, -0.9, 0.75), focal=(100, 0, 250), dist=520,
         size=(1600, 1200), hide=(), with_lid=False, ghost_lid=False, clip_x=None, xray=(), up=(0, 0, 1), explode=None, only=None, ctx_only=None, ghost=(), parallel=None, cut=None):
    M = load(key, roles, with_lid=with_lid or ghost_lid)
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("#141416", top="#3A3A40")
    p.enable_anti_aliasing("ssaa")
    shown = {}
    for n, (m, role) in M.items():
        if any(n.startswith(h) for h in hide):
            continue
        if cut is not None:
            try:
                m = m.clip_closed_surface(normal=cut[0], origin=cut[1])
            except Exception:
                m = m.clip(normal=cut[0], origin=cut[1], invert=False)
            if m.n_points == 0:
                continue
        if role == "ctx" and ctx_only is not None and not n.startswith(ctx_only):
            continue
        if role != "ctx" and only is not None and not n.startswith(only):
            continue
        if explode:
            dz = next((v for k, v in sorted(explode.items(), key=lambda kv: -len(kv[0])) if n.startswith(k)), 0.0)
            if dz:
                m = m.translate((0, 0, dz), inplace=False)
        if clip_x is not None and role == "ctx":
            m = m.clip(normal="x", origin=(clip_x, 0, 0), invert=False)
            if m.n_points == 0:
                continue
        if ghost_lid and n.startswith(("lid", "panel_")):
            col, spec, op = SPECIAL["lid_ghost"] if n.startswith("lid") else ("#1A1A1C", 0.3, 0.35)
        else:
            col, spec, op = mat(n, role)
            if any(n.startswith(x) for x in xray):
                op = 0.22
            if any(n.startswith(g) for g in ghost):
                col, op = "#8A8A90", 0.12
        p.add_mesh(m, color=col, opacity=op, smooth_shading=True, split_sharp_edges=True, specular=spec, specular_power=40,
                   ambient=0.2, diffuse=0.85)
        if role in ("pos", "neg", "ins") or n.startswith(("contactor", "sb175", "body_half", "tray")):
            p.add_mesh(m.extract_feature_edges(30, boundary_edges=False, non_manifold_edges=False), color="#0A0A0B", line_width=1.0, opacity=0.6)
        if op > 0.5:
            shown[n] = m
    p.camera.position = (focal[0] + view[0] * dist, focal[1] + view[1] * dist, focal[2] + view[2] * dist)
    p.camera.focal_point = focal; p.camera.up = up
    if parallel:
        p.camera.parallel_projection = True; p.camera.parallel_scale = parallel
    p.show(auto_close=False)
    depth = p.get_image_depth(fill_value=np.inf)
    cam = np.array(p.camera.position); vdir = np.array(p.camera.focal_point) - cam; vdir /= np.linalg.norm(vdir)
    ren = p.renderer
    anchors = []
    for keyp, text in labels:
        parts = [m for n, m in shown.items() if n.startswith(keyp)]
        if not parts:
            continue
        m = (parts[0] if len(parts) == 1 else parts[0].merge(parts[1:])).triangulate()
        cs = m.compute_cell_sizes(length=False, volume=False); a = cs["Area"]
        if a.sum() <= 0:
            continue
        tri = m.faces.reshape(-1, 4)[:, 1:]
        rng = np.random.default_rng(0); N = 3000
        idx = rng.choice(len(tri), size=N, p=a / a.sum()); u, v = rng.random(N), rng.random(N)
        fl = u + v > 1; u[fl], v[fl] = 1 - u[fl], 1 - v[fl]
        P = m.points
        pts = P[tri[idx, 0]] + u[:, None] * (P[tri[idx, 1]] - P[tri[idx, 0]]) + v[:, None] * (P[tri[idx, 2]] - P[tri[idx, 0]])
        vis = []
        for q in pts:
            ren.SetWorldPoint(*q, 1.0); ren.WorldToDisplay()
            x, y, _ = ren.GetDisplayPoint()
            c, r = int(round(x)), int(round(size[1] - 1 - y))
            if 0 <= c < size[0] and 0 <= r < size[1]:
                dz = abs(depth[r, c]); dq = float(np.dot(q - cam, vdir))
                if np.isfinite(dz) and dq <= dz + 2.0:
                    vis.append((x, y))
        if len(vis) < max(60, 0.08 * N):
            continue
        vis = np.array(vis); cc = vis.mean(0)
        x, y = vis[np.argmin(((vis - cc) ** 2).sum(1))]
        anchors.append((text, 2 * x, 2 * (size[1] - y)))
    f = os.path.join(OUT, fname)
    p.screenshot(f, scale=2); p.close()
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(f); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    d.text((70, 50), title, fill="#EEEEEE", font=f1)
    d.text((70, 120), subtitle, fill="#AAAAAA", font=f2)
    if anchors:
        place_labels(im, d, anchors)
    im.convert("RGB").save(f.replace(".png", ".jpg"), quality=88)
    os.remove(f)
    return f.replace(".png", ".jpg")
