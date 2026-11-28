"""FAST render of Claude battery pack v17 (option D), plain v1-v11 style. Reads cad/out_tower17/stl (run_tower17.py).
Run: xvfb-run -a ~/.venvs/cad/bin/python cad/render_tower17_plain.py [all|hero rear top strip section harness]
Writes JPGs to versions/v17-option-d/renders/v17p_*.jpg. Label placement and shot() from render_tower15_plain.py."""
import os, glob, sys
os.environ.setdefault("DISPLAY", ":99")
import pyvista as pv

D = os.path.dirname(os.path.abspath(__file__))
_V = os.environ.get("V17_FACET", "")
OUT = os.path.join(D, "out_tower17" + (("_" + _V) if _V else ""))
IMG = os.path.join(OUT, "img"); os.makedirs(IMG, exist_ok=True)
JPG = os.path.join(D, "..", "versions", "v17-option-d", "renders"); os.makedirs(JPG, exist_ok=True)
RED, GRAPH = "#B0121C", "#3E4045"
BRASS, STEEL, CU, POS, NEG, G10, NYLON, BLK = "#C9A94A", "#C9CCD1", "#C8693A", "#D8452F", "#19B5C4", "#C9C46A", "#E8E4D8", "#1C1C1E"
MAT = {
    "body_half": (RED, 0.7, 1), "lid": (RED, 0.7, 1), "plate": (GRAPH, 0.35, 1), "screws": ("#121214", 0.6, 1), "screws_lid": (RED, 0.6, 1),
    "screws_term": (STEEL, 0.6, 1), "screws_tap": (STEEL, 0.6, 1), "feet": ("#0C0C0E", 0.1, 1), "pem": ("#B0B4BA", 0.6, 1),
    "ledboard": ("#1F6B2A", 0.2, 1), "pipe": ("#F3ECDD", 0.3, 1), "diffuser": ("#F4F1EA", 0.2, 0.85), "antenna": (BRASS, 0.4, 1),
    "panel_standoffs": (BRASS, 0.5, 1), "panel_spacers": (NYLON, 0.2, 1), "cell_": ("#2B6FC4", 0.3, 1), "g10": (G10, 0.2, 1),
    "module_endplates": ("#9EA3AA", 0.5, 1), "rods": (STEEL, 0.7, 1), "rodnuts": (STEEL, 0.7, 1), "tnuts": (STEEL, 0.6, 1), "so_": (BRASS, 0.5, 1),
    "bus_": (CU, 0.5, 1), "bus_pack_pos": (POS, 0.5, 1), "bus_mod_pos": (POS, 0.5, 1), "bus_mod_in": (POS, 0.5, 1), "strap_main": ("#F06A3A", 0.5, 1),
    "bus_pack_neg": (NEG, 0.5, 1), "bus_mod_neg": (NEG, 0.5, 1), "flex": ("#E0A035", 0.2, 1),
    "deck1": ("#BDB55E", 0.2, 1), "deck2": ("#D2CC7E", 0.2, 1), "posts_d2": (NYLON, 0.2, 1), "bay_standoffs": (NYLON, 0.2, 1),
    "bridge_posts": (NYLON, 0.2, 1), "bms_standoffs": (BRASS, 0.5, 1), "charger": ("#8C9096", 0.4, 1), "inverter": ("#6E7278", 0.4, 1),
    "fan_spacer": ("#9EA3AA", 0.4, 1), "fan_4020": ("#232325", 0.3, 1), "nuts_fan": (STEEL, 0.5, 1), "term_": (STEEL, 0.5, 1),
    "relay_body": ("#2A2A2E", 0.4, 1), "relay_bracket": (STEEL, 0.5, 1), "relay_tab": (BRASS, 0.5, 1),
    "bms_pcb": ("#1E5631", 0.2, 1), "bms_": ("#111113", 0.3, 1), "panel_": (BLK, 0.3, 1),
    "shunt_bar": ("#B87333", 0.5, 1), "shunt_pcb": ("#1E5631", 0.2, 1), "sb175_housing": ("#8A8D93", 0.3, 1), "sb175_contact": (STEEL, 0.6, 1),
    "contactor": ("#232325", 0.35, 1), "bs2151_body": ("#C4322B", 0.3, 1), "bs5191_body": ("#C4322B", 0.3, 1), "bs2151_fuse": ("#ECE7DA", 0.2, 0.9),
    "bs5191_fuse": ("#ECE7DA", 0.2, 0.9), "bs2151_": (CU, 0.5, 1), "bs5191_": (CU, 0.5, 1), "bolt_": (STEEL, 0.6, 1), "nut": (STEEL, 0.6, 1),
    "hw_": (STEEL, 0.6, 1), "lug_pos": (POS, 0.6, 1), "lug_neg": (NEG, 0.6, 1), "ring_pos": (POS, 0.6, 1), "ring_neg": (NEG, 0.6, 1),
    "ring_chassis": ("#3AA655", 0.4, 1), "pe_ring": ("#3AA655", 0.4, 1), "pe_": (STEEL, 0.5, 1), "imd_": (STEEL, 0.5, 1),
    "plug_": ("#2E2E33", 0.3, 1), "plug_pp45_pos": ("#C0282E", 0.3, 1), "plug_j": ("#E8E4D8", 0.2, 1), "fuseholder": ("#3B3B40", 0.3, 1),
    "ntc": ("#111113", 0.3, 1),
    "w_p1": ("#D0222A", 0.3, 1), "w_p3": ("#D0222A", 0.3, 1), "w_p2": ("#151517", 0.3, 1), "w_p4": ("#151517", 0.3, 1),
    "w_a1": ("#EDEDED", 0.3, 1), "w_a2": ("#EDEDED", 0.3, 1), "w_a3": ("#3AA655", 0.3, 1), "w_pe": ("#3AA655", 0.3, 1), "w_h2b": ("#7AC943", 0.3, 1),
    "w_h2_bplus": ("#E04848", 0.3, 1), "w_h2_load": ("#F08030", 0.3, 1), "w_h2_gnd": ("#2A2A2A", 0.3, 1), "w_ring": ("#555555", 0.3, 1),
    "w_h1": ("#2FA84F", 0.3, 1), "w_shunt": ("#8855CC", 0.3, 1), "w_h3": ("#E8C22E", 0.3, 1), "w_h5": ("#E8C22E", 0.3, 1),
    "w_h4": ("#2A6FD0", 0.3, 1), "w_h6": ("#9B59B6", 0.3, 1), "w_h7": ("#00B8D4", 0.3, 1),
}
LABELS = [
    ("sb175_housing", "Anderson SB175 (DC out, 175 A)"),
    ("panel_inlet", "IEC C14 AC inlet"), ("panel_outlet", "NEMA 5-15R outlet"), ("panel_pushbutton", "Wake button"),
    ("contactor", "Gigavac GV141BAX (inverted)"), ("bs5191_fuse_0_body", "MRBF 250 A main (5191)"), ("bs2151_fuse_0_body", "MRBF 30 A (charger)"),
    ("bs2151_fuse_1_body", "MRBF 50 A (inverter)"), ("strap_main", "Z-strap = service disconnect"), ("shunt_bar", "Tesla shunt"),
    ("charger_npb360", "MEAN WELL NPB-360-12TB"), ("inverter_nts400p", "MEAN WELL NTS-400P-112"), ("fan_4020", "40 mm fan (intake)"),
    ("relay_body", "Charger relay (TE F4)"), ("bms_pcb", "BMS board 95 x 55"), ("g10_bms_bridge", "G10 BMS bridge"), ("deck2", "Deck 2 (G10)"),
    ("deck1", "Deck 1 (G10)"), ("g10_bay", "G10 bay plate"), ("bus_mod_pos", "+ rail"), ("bus_mod_neg", "- rail"), ("bus_pack_pos", "Pack + riser"),
    ("bus_pack_neg", "Pack - riser"), ("bus_B", "Series busbars"), ("cell_4", "EVE LF105 cells (4S2P)"), ("ledboard", "LED board (front)"),
    ("module_endplates", "Module end plate"), ("fuseholder_bplus", "B+ 5 A inline fuse"), ("fuseholder_load", "LOAD+ 2 A inline fuse"),
    ("w_p3", "Inverter DC"), ("w_p1b", "Charger + (via relay)"), ("w_a1", "AC in (mains)"), ("w_h3_coil", "GV14 coil leads"),
    ("w_h1", "Shunt harness"), ("w_h4_led", "LED link"), ("w_h7", "Antenna coax"), ("w_a3_pe_in", "PE bond"),
]

def mat(n):
    k = max((k for k in MAT if n.startswith(k)), key=len, default=None)
    return MAT.get(k, ("#888888", 0.2, 1))

def place_labels(im, d, anchors):
    """Callouts in left/right margin columns, leader line to the part, no overlaps."""
    from PIL import ImageFont
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 44)
    except Exception:
        ft = ImageFont.load_default()
    W, H = im.size
    top, bot, gap = 330, H - 40, 76
    xs = sorted(a[1] for a in anchors); mid = xs[len(xs) // 2] if len(anchors) > 3 else W / 2
    left = sorted([a for a in anchors if a[1] < mid], key=lambda a: a[2])
    right = sorted([a for a in anchors if a[1] >= mid], key=lambda a: a[2])
    def column(items):
        n = len(items)
        if not n:
            return []
        ys = [min(max(a[2], top), bot) for a in items]
        for i in range(1, n):                      # push down
            ys[i] = max(ys[i], ys[i - 1] + gap)
        over = ys[-1] - bot
        if over > 0:                               # shift up, keep spacing
            ys = [y - over for y in ys]
            for i in range(n - 2, -1, -1):
                ys[i] = min(ys[i], ys[i + 1] - gap)
        return ys
    def cross(p1, p2, p3, p4):
        def o(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return o(p1, p2, p3) * o(p1, p2, p4) < 0 and o(p3, p4, p1) * o(p3, p4, p2) < 0
    def uncross(items, ys, side):
        """Order labels in their slots to minimise leader-line crossings, then total length (annealing)."""
        import math, random
        rnd = random.Random(0)
        items = list(items); n = len(items)
        if n < 2:
            return items
        def edge(a):
            tw = d.textlength(a[0], font=ft)
            return 40 + tw + 14 if side == "L" else W - 40 - tw - 14
        E = [edge(a) for a in items]
        def cost(perm):
            segs = [((E[i], ys[k]), (items[i][1], items[i][2])) for k, i in enumerate(perm)]
            c = sum(cross(*segs[i], *segs[j]) for i in range(n) for j in range(i + 1, n))
            L = sum(math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]) for s in segs)
            return c * 5000 + L
        cur = list(range(n)); cc = cost(cur); best, bc = cur[:], cc
        T = 3000.0
        for it in range(6000):
            nxt = cur[:]
            i, j = rnd.sample(range(n), 2)
            if rnd.random() < 0.5:
                nxt[i], nxt[j] = nxt[j], nxt[i]
            else:
                nxt.insert(j, nxt.pop(i))
            nc = cost(nxt)
            if nc < cc or rnd.random() < math.exp((cc - nc) / T):
                cur, cc = nxt, nc
                if cc < bc:
                    best, bc = cur[:], cc
            T *= 0.999
        return [items[i] for i in best]
    for items, ys, side in ((left, column(left), "L"), (right, column(right), "R")):
        items = uncross(items, ys, side)
        for (text, ax, ay), ly in zip(items, ys):
            tw = d.textlength(text, font=ft)
            if side == "L":
                tx = 40; ex = tx + tw + 14
            else:
                tx = W - 40 - tw; ex = tx - 14
            d.line([(ex, ly), (ax, ay)], fill="#FFFFFF", width=3)
            d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill="#FFD23F", outline="#000000", width=2)
            d.rectangle([tx - 10, ly - 34, tx + tw + 10, ly + 30], fill="#000000C0", outline="#FFD23F", width=2)
            d.text((tx, ly - 28), text, fill="#FFFFFF", font=ft)

def load(folder="stl"):
    return {os.path.basename(f)[:-4]: pv.read(f) for f in glob.glob(os.path.join(OUT, folder, "*.stl"))}

def shot(fname, title, meshes, hide=(), explode=None, view=(1.0, -1.15, 0.62), size=(1920, 1440), zoom=1.0, clip=None,
         focal=(-10, 0, 165), dist=750, edges=True, labels=True):
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
        if edges and n.startswith(("plate", "body_half", "lid", "deck")):
            p.add_mesh(m.extract_feature_edges(25, boundary_edges=False, non_manifold_edges=False), color="#0A0A0B", line_width=1.0, opacity=0.7)
    v = view
    p.camera.position = (focal[0] + v[0] * dist, focal[1] + v[1] * dist, focal[2] + v[2] * dist)
    p.camera.focal_point = focal
    p.camera.up = (0, 0, 1)
    p.camera.zoom(zoom)
    f = os.path.join(IMG, fname)
    p.show(auto_close=False)
    anchors = []
    if labels:
        import numpy as np
        depth = p.get_image_depth(fill_value=np.inf)          # (H, W) camera distance, row 0 = top
        cam = np.array(p.camera.position); fp = np.array(p.camera.focal_point)
        vdir = (fp - cam) / np.linalg.norm(fp - cam)
        ren = p.renderer
        shown = {n: m for n, m in meshes.items() if not any(n.startswith(h) for h in hide)}
        for key, text in LABELS:
            if labels is not True and not any(key.startswith(k) for k in labels):
                continue
            parts = [m for n, m in shown.items() if n.startswith(key)]
            if not parts:
                continue
            m = parts[0] if len(parts) == 1 else parts[0].merge(parts[1:])
            if clip is not None:
                m = m.clip(normal=clip[0], origin=clip[1], invert=True)
                if m.n_points == 0:
                    continue
            m = m.triangulate()
            pts = None
            if pts is None:
                # area-weighted surface samples
                cs = m.compute_cell_sizes(length=False, volume=False)
                a = cs["Area"]; tri = m.faces.reshape(-1, 4)[:, 1:]
                rng = np.random.default_rng(0)
                idx = rng.choice(len(tri), size=4000, p=a / a.sum())
                u, v = rng.random(4000), rng.random(4000)
                flip = u + v > 1; u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
                P = m.points
                pts = P[tri[idx, 0]] + u[:, None] * (P[tri[idx, 1]] - P[tri[idx, 0]]) + v[:, None] * (P[tri[idx, 2]] - P[tri[idx, 0]])
            vis = []
            for q in pts:
                ren.SetWorldPoint(*q, 1.0); ren.WorldToDisplay()
                x, y, _ = ren.GetDisplayPoint()
                col, row = int(round(x)), int(round(size[1] - 1 - y))
                if not (0 <= col < size[0] and 0 <= row < size[1]):
                    continue
                dz = abs(depth[row, col]); dq = float(np.dot(q - cam, vdir))
                if np.isfinite(dz) and dq <= dz + 2.0:        # this sample is the front surface at that pixel
                    vis.append((x, y))
            if len(vis) < 0.08 * len(pts) or len(vis) < 150:   # less than 8 % of its surface in view: no label
                continue
            vis = np.array(vis); c = vis.mean(0)
            x, y = vis[np.argmin(((vis - c) ** 2).sum(1))]     # visible sample nearest the visible centroid
            anchors.append((text, 2 * x, 2 * (size[1] - y)))
    p.screenshot(f, scale=2)
    p.close()
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(f); d = ImageDraw.Draw(im)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 90); f2 = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 56)
    except Exception:
        f1 = f2 = ImageFont.load_default()
    d.text((80, 60), title, fill="#EEEEEE", font=f1)
    if anchors:
        place_labels(im, d, anchors)
    d.text((80, 180), "Claude battery pack v17 option D (plain render)  |  4S2P EVE LF105, 12.8 V 210 Ah 2.69 kWh  |  175 A DC out", fill="#AAAAAA", font=f2)
    im.save(f)

LIDOFF = ("lid", "screws_lid", "pem_body_lid", "pem_lid_panel", "screws_panel", "panel_inlet", "panel_outlet", "panel_pushbutton")
FRONT = ("plate_front", "screws_front", "diffuser", "pipe", "screws_panelmount", "antenna", "ledboard", "panel_", "pe_", "w_pe", "plug_led", "screws_pe")
BAY = ("g10_bay", "bay_standoffs", "shunt", "sb175", "g10_sb", "contactor", "bs2151", "bs5191", "bus_", "strap_main", "bolt_", "nut", "hw_",
       "lug_", "ring_pos", "ring_neg", "screws_bay", "screws_sb")

def jpg(name):
    from PIL import Image
    Image.open(os.path.join(IMG, name)).convert("RGB").resize((2400, 1800)).save(os.path.join(JPG, name.replace(".png", (f"_facet{_V}" if _V else "") + ".jpg")), quality=88)

if __name__ == "__main__":
    M = load()
    which = sys.argv[1:] or ["all"]
    def want(k):
        return "all" in which or k in which
    if want("hero"):
        shot("v17p_01_hero.png", "v17 option D: everything above the cells inside the module footprint", M, view=(1.0, -1.25, 0.55),
             focal=(5, 0, 190), dist=860, labels=("sb175", "panel_", "lid"))
        jpg("v17p_01_hero.png")
    if want("rear"):
        shot("v17p_02_rear.png", "Rear: full hole grid; the 40 mm fan draws through the holes in front of it", M, view=(-1.0, -0.45, 0.28),
             focal=(-10, 0, 190), dist=860, labels=("sb175", "panel_"))
        jpg("v17p_02_rear.png")
    if want("top"):
        shot("v17p_03_lid_off_top.png", "Lid off, from above: power strip on -y, BMS over the inverter", M, hide=LIDOFF,
             view=(0.0, -0.001, 1.0), focal=(3, 0, 270), dist=720, edges=False,
             labels=("sb175", "contactor", "bs5191_fuse", "bs2151_fuse", "strap_main", "shunt_bar", "inverter", "bms_pcb", "relay_body",
                     "fan_4020", "fuseholder", "ledboard", "w_a1", "w_p3", "w_p1b"))
        jpg("v17p_03_lid_off_top.png")
    if want("strip"):
        shot("v17p_04_power_strip.png", "Power strip: shunt (rear) - SB175 - 2151 - GV14 - 5191 + Z-strap (front)", M,
             hide=LIDOFF + FRONT + ("body_half_A", "w_a", "plug_c13"), view=(0.25, -1.0, 0.85), focal=(10, -35, 268), dist=470,
             labels=("sb175", "contactor", "bs5191_fuse", "bs2151_fuse", "strap_main", "shunt_bar", "bus_mod_pos", "bus_mod_neg",
                     "bus_pack_neg", "fuseholder", "g10_bay"))
        jpg("v17p_04_power_strip.png")
    if want("section"):
        shot("v17p_05_section.png", "Section at y = 10: cells, deck 1 charger, deck 2 inverter + fan, BMS under the lid", M,
             view=(0.02, -1.0, 0.03), clip=((0, -1, 0), (0, 10.0, 0), ""), focal=(3, 0, 185), dist=820,
             labels=("cell_4", "charger_npb360", "inverter_nts400p", "fan_4020", "bms_pcb", "g10_bms", "deck1", "deck2", "module_endplates",
                     "ledboard", "panel_inlet", "bus_B"))
        jpg("v17p_05_section.png")
    if want("harness"):
        keep = {k: v for k, v in M.items() if not k.startswith(LIDOFF + ("plate_", "body_half", "screws_", "feet", "diffuser", "pipe"))}
        shot("v17p_06_harness.png", "Harnesses: signal, DC leads, mains (lid off, shell hidden)", keep, view=(-0.45, -0.7, 0.9),
             focal=(5, -5, 270), dist=680, edges=False,
             labels=("w_", "fuseholder", "bms_pcb", "relay_body", "shunt_bar", "sb175", "contactor"))
        jpg("v17p_06_harness.png")
        shot("v17p_07_harness_top.png", "Harness plan view (lid off, shell hidden)", keep, view=(0.0, -0.001, 1.0), focal=(3, 0, 285), dist=700,
             edges=False, labels=("w_", "fuseholder", "bms_pcb"))
        jpg("v17p_07_harness_top.png")
