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
       "plate_pos": ("#C8693A", 0.5, 1), "term_plates": ("#1A1A1C", 0.3, 1), "term_": ("#C8693A", 0.5, 1), "fuse_": ("#ECE7DA", 0.2, 1), "contactor": ("#232325", 0.3, 1), "mrbf": ("#D84A2A", 0.3, 1), "shunt_bar": ("#B87333", 0.5, 1), "shunt_module": ("#1E5631", 0.2, 1), "g10_power": ("#C9C46A", 0.2, 1), "tray1_g10": ("#C9C46A", 0.2, 1), "g10_sb": ("#C9C46A", 0.2, 1), "sb175": ("#8A8D93", 0.3, 1), "bus_pack_pos": ("#D8452F", 0.5, 1), "bus_link": ("#D8452F", 0.5, 1), "bus_pos_out": ("#D8452F", 0.5, 1), "bus_pack_neg": ("#19B5C4", 0.5, 1), "bus_neg_out": ("#19B5C4", 0.5, 1), "cable_shunt_spi": ("#2FA84F", 0.3, 1), "cable_coil": ("#2FA84F", 0.3, 1), "cable_fan": ("#2FA84F", 0.3, 1), "ctrl_": ("#111113", 0.3, 1), "antenna": ("#C9A94A", 0.4, 1), "panel_standoffs": ("#C9A94A", 0.5, 1), "screws_tap": ("#C9CCD1", 0.6, 1), "cable_ac": ("#3A3A3C", 0.3, 1), "cable_inv_dc_neg": ("#151517", 0.3, 1), "cable_chg_dc_neg": ("#151517", 0.3, 1), "plate_neg": ("#D9824F", 0.5, 1), "insulator": ("#C9C46A", 0.2, 0.9), "spacers_cu": ("#E09060", 0.5, 1)}

def mat(n):
    k = max((k for k in MAT if n.startswith(k)), key=len, default=None)
    return MAT.get(k, ("#888888", 0.2, 1))

# (STL name prefix, label). First match wins per entry; entries whose part is hidden or off-screen are skipped.
LABELS = [
    ("sb175", "Anderson SB175 (DC output, 175 A)"),
    ("contactor", "Gigavac GX12 contactor (225 A)"),
    ("mrbf_main", "MRBF 250 A main fuse + block"),
    ("mrbf_branch", "MRBF branch fuses (charger, inverter)"),
    ("shunt_bar", "Shunt (Tesla module)"),
    ("bus_pack_pos", "Pack + riser / collector"),
    ("bus_pack_neg", "Pack - band + riser"),
    ("bus_neg_out", "- output bus"),
    ("bus_pos_out", "+ output bus"),
    ("bus_link", "Fuse -> contactor link"),
    ("bus_B", "Series busbars"),
    ("g10_sb_bracket", "G10 SB175 bracket"),
    ("tray1_g10", "G10 tray 1"),
    ("tray2", "Tray 2 (inverter deck)"),
    ("charger", "MEAN WELL NPB-450-12 charger"),
    ("inverter", "MEAN WELL NTS-400P-112 inverter"),
    ("panel_outlet", "NEMA 5-15 AC outlet"),
    ("panel_inlet", "IEC C14 AC inlet"),
    ("panel_pushbutton", "Wake pushbutton"),
    ("ledboard", "Front PCB (LEDs + control)"),
    ("ctrl_esp32", "ESP32-S3 (Wi-Fi)"),
    ("ctrl_bq76952", "BQ76952 cell monitor"),
    ("ctrl_buck", "5 V buck"),
    ("ctrl_precharge_relay", "Precharge relay"),
    ("ctrl_precharge_r", "Precharge resistor"),
    ("ctrl_conn_harness", "Harness connector"),
    ("ctrl_conn_shunt", "Shunt connector"),
    ("ctrl_fuse", "2 A control fuse"),
    ("flex_ccs", "Cell sense flex"),
    ("fan_", "Noctua NF-A14 fan"),
    ("cell_4", "EVE LF105 cells (4S2P)"),
    ("module_endplates", "Module end plate"),
    ("cable_chg_dc", "Charger DC leads"),
    ("cable_inv_dc", "Inverter DC leads"),
    ("cable_ac_in", "AC in cable"),
]

def place_labels(im, d, anchors):
    """Callouts in left/right margin columns, leader line to the part, no overlaps."""
    from PIL import ImageFont
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception:
        ft = ImageFont.load_default()
    W, H = im.size
    top, bot, gap = 230, H - 40, 50
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
            d.rectangle([tx - 8, ly - 22, tx + tw + 8, ly + 20], fill="#000000C0", outline="#FFD23F", width=2)
            d.text((tx, ly - 18), text, fill="#FFFFFF", font=ft)

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
        if edges and n.startswith(("plate", "body_half", "lid", "tray")):
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
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 54); f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    except Exception:
        f1 = f2 = ImageFont.load_default()
    d.text((80, 60), title, fill="#EEEEEE", font=f1)
    if anchors:
        place_labels(im, d, anchors)
    d.text((80, 135), "Claude battery pack v15 concept D (plain render)  |  4S2P EVE LF105, 12.8 V 210 Ah 2.69 kWh  |  175 A DC out", fill="#AAAAAA", font=f2)
    im.save(f)

POWER = ("sb175", "contactor", "mrbf", "shunt_bar", "bus_pack", "bus_neg_out", "bus_pos_out", "bus_link")

if __name__ == "__main__":
    M = load()
    which = sys.argv[1:] or ["all"]
    lidoff = ("lid", "screws_lid", "pem_body_lid", "pem_lid_panel", "screws_panel", "panel_")
    front = ("plate_front", "screws_f", "diffuser", "pipe", "screws_panelmount", "antenna")
    if "all" in which or "hero" in which:
        shot("v15p_01_hero.png", "v15 concept D: SB175 output through the lid", M, view=(1.0, -1.25, 0.55), focal=(0, 0, 175), dist=1150,
             labels=("sb175", "panel_", "ledboard", "lid"))
    if "all" in which or "bay" in which:
        shot("v15p_02_bay_minus_side.png", "Power bay from the -y side: shunt + - bus (cyan), contactor + fuses (red)", M,
             hide=lidoff + front + ("body_half_A",), view=(0.35, -1.0, 0.55), focal=(105, 0, 250), dist=520,
             labels=POWER + ("g10_sb", "tray1", "charger", "inverter", "cell_", "ledboard", "cable_chg", "cable_inv"))
    if "all" in which or "bay2" in which:
        shot("v15p_03_bay_top.png", "Power bay from above: - half (cyan) at -y, + half (red) at +y, SB175 between", M,
             hide=lidoff + front, view=(0.15, -0.25, 1.0), focal=(105, 0, 250), dist=560,
             labels=POWER + ("g10_sb", "ledboard", "cable_chg", "cable_inv"))
    if "all" in which or "pcb" in which:
        shot("v15p_04_front_pcb_back.png", "Front PCB back: control circuit faces the bay (z 222-285); flex tail and harnesses", M,
             hide=lidoff + ("plate_front", "screws_f", "diffuser", "pipe", "screws_panelmount", "body_half_B"), view=(-0.6, 1.0, 0.45), focal=(150, 0, 250), dist=520,
             labels=("ctrl_", "ledboard", "flex", "contactor", "sb175", "module_endplates", "cell_"))
    if "all" in which or "pcb2" in which:
        shot("v15p_07_control_zone.png", "Control circuit on the front PCB back, power parts and converters removed", M,
             hide=lidoff + front + ("body_half_B", "contactor", "sb175", "mrbf", "bus_link", "bus_pos_out", "bus_neg_out", "g10_sb",
                                    "charger", "inverter", "tray2", "inv_posts", "cable_", "so_upper", "shunt"),
             view=(-1.0, 0.35, 0.3), focal=(165, 0, 250), dist=380,
             labels=("ctrl_", "ledboard", "flex", "bus_pack", "module_endplates", "tray1"))
    if "all" in which or "path" in which:
        keep = {k: v for k, v in M.items() if k.startswith(("bus_", "shunt", "mrbf", "contactor", "sb175", "cell_"))}
        shot("v15p_05_current_path.png", "Current path only: cells -> + collector -> MRBF 250 -> GX12 -> + bus -> SB175; - band -> shunt -> - bus", keep,
             view=(0.55, -1.0, 1.0), focal=(30, 0, 225), dist=640, labels=POWER + ("bus_B", "cell_"))
    if "all" in which or "section" in which:
        shot("v15p_06_section.png", "Section y = -70: - band, riser tab and shunt outside the G10 tray", M,
             view=(0.02, -1.4, 0.05), clip=((0, -1, 0), (0, -70.0, 0), ""), focal=(40, 0, 230), dist=800,
             labels=("bus_pack_neg", "shunt_bar", "tray1", "tray2", "sb175", "cell_", "charger", "inverter", "ledboard"))
