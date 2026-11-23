"""Exploded views of Tower A v4, one per subsystem. Reuses the material table from render_tower2.py."""
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
    annotate(path, title, sub or "Tower A v4  |  1.28 kWh 8S LFP  |  build123d", disp, txt)
    p.close()
    print("ok", fname)


# ---------------------------------------------------------------- 1. whole pack
FULL = {
    "lid": {"t": (0, 0, 470)}, "pem_lid": {"t": (0, 0, 470)}, "screws_lid": {"s": (1, 0.35, 0), "t": (0, 0, 470)},
    "panel_": {"t": (0, 0, 580)}, "screws_panel": {"t": (0, 0, 630)},
    "plate_front": {"t": (230, 0, 0)}, "screws_f": {"t": (290, 0, 0)}, "pipe_f": {"t": (230, 0, 0)}, "feet_f": {"t": (230, 0, 0)},
    "diffuser_f": {"t": (175, 0, 0)}, "ledboard_f": {"t": (130, 0, 0)},
    "plate_rear": {"t": (-230, 0, 0)}, "screws_r": {"t": (-290, 0, 0)}, "screws_fan": {"t": (-290, 0, 0)},
    "feet_r": {"t": (-230, 0, 0)}, "fan_": {"t": (-140, 0, 0)},
    "inverter": {"t": (0, 0, 250)}, "tray2": {"t": (0, 0, 205)}, "inv_posts": {"t": (0, 0, 165)},
    "charger": {"t": (0, 0, 125)}, "ctrl_": {"t": (0, 0, 135)}, "cb_standoffs": {"t": (0, 0, 105)},
    "tray1": {"t": (0, 0, 80)}, "mica_tray": {"t": (0, 0, 62)}, "screws_trays": {"t": (0, 0, 80)},
    "int_pack_": {"t": (0, 0, 40)}, "int_busbar": {"t": (0, 0, 30)}, "int_flex": {"t": (0, 0, 22)},
    "int_comp_pcb_standoffs": {"t": (0, 0, 15)},
    "screws_hold": {"t": (0, 0, -120)},
}
shot("x01_full.png", "Full exploded view: every part", FULL, hide=("cable_",), view=(1.0, -1.25, 0.75), zoom=1.45,
     size=(2200, 2300), ghost=("int_liner",),
     labels={"lid": ("Lid", 6, (0.5, 0, 1)), "panel_": ("Panel connectors", 6, (0.5, 0, 1)),
             "inverter": ("Inverter, tray 2", 6, (0, 0, 1)), "charger": ("Charger", 6, (0, 0, 1)),
             "ctrl_contactor": ("Control board", 6, (1, 0, 1)), "tray1": ("Tray 1 + mica", 6, (0, 0, 0)),
             "int_busbar": ("Busbars, sense flex", 6, (0, 0, 1)), "u_body": ("U body + liner + module", 6, (0.5, 0, 0.3)),
             "plate_front": ("Front plate", 6, (1, 0, 1)), "ledboard_f": ("LED board, diffuser", 6, (0.5, 0, 0.9)),
             "plate_rear": ("Rear plate", 6, (0, 0, 1)), "fan_": ("Fan", 6, (0.5, 0, 1)),
             "screws_hold": ("Hold-down screws", -10, (0.5, 0, 0))})

# ---------------------------------------------------------------- 2. enclosure
ENC = {
    "lid": {"t": (0, 0, 170)}, "pem_lid": {"t": (0, 0, 120)}, "screws_lid": {"s": (1, 0.6, 0), "t": (0, 0, 120)},
    "plate_front": {"t": (160, 0, 0)}, "screws_f": {"t": (215, 0, 0)}, "pipe_f": {"t": (190, 0, 0)}, "feet_f": {"t": (160, 0, -20)},
    "plate_rear": {"t": (-160, 0, 0)}, "screws_r": {"t": (-215, 0, 0)}, "screws_fan": {"t": (-215, 0, 0)},
    "feet_r": {"t": (-160, 0, -20)}, "pem_tab_f": {"t": (-25, 0, 0)}, "pem_tab_r": {"t": (25, 0, 0)},
    "int_liner": {"t": (0, 0, 0)}, "screws_hold": {"t": (0, 0, -70)},
}
shot("x02_enclosure.png", "Enclosure: U body, lid, end plates, tabs, PEM nuts, every screw", ENC,
     only=("u_body", "lid", "pem_", "screws_lid", "plate_", "screws_f", "screws_r", "screws_fan", "pipe_f", "feet_", "tabs_",
           "screws_hold"), view=(1.0, -1.1, 0.7), zoom=1.15,
     labels={"lid": ("Lid, 1.6 mm 5052, joggle lip", 8, (0.3, 0, 1)), "pem_lid": ("4x M3 PEM nuts in lid lip", -6, (0.8, 0, 0)),
             "screws_lid": ("4x M3 red pan heads", 0, (0.2, 0, 0)), "plate_front": ("Front plate: LED matrix", 8, (1, 0, 1)),
             "plate_rear": ("Rear plate: vent + fan", 8, (0, 0, 1)), "screws_f": ("7x M4 button heads", 0, (1, 0, 0.5)),
             "screws_r": ("11x M4 button heads", 0, (0, 0, 0.5)), "u_body": ("U body, R22 bends, red", 0, (0.5, 0, 0.55)),
             "tabs_f": ("Bent tabs + PEM nuts", 0, (0.5, 0, 0.75)),
             "screws_hold": ("4x M4 module hold-down", -10, (0.5, 0, 0)), "feet_f": ("EPDM feet", -8, (0.5, 0, 0))})

# ---------------------------------------------------------------- 3. front stack
FR = {"plate_front": {"t": (90, 0, 0)}, "screws_f": {"t": (140, 0, 0)}, "pipe_f": {"t": (115, 0, 0)},
      "diffuser_f": {"t": (55, 0, 0)}, "ledboard_f": {"t": (25, 0, 0)}, "pem_tab_f": {"t": (-14, 0, 0)},
      "feet_f": {"t": (90, 0, -12)}}
shot("x03_front_stack.png", "Front stack: plate, charge pipe, diffuser, LED board, tabs", FR,
     only=("plate_front", "screws_f", "pipe_f", "diffuser_f", "ledboard_f", "tabs_f", "pem_tab_f", "feet_f"),
     view=(1.0, -1.6, 0.5), zoom=1.05,
     labels={"plate_front": ("Front plate, 21x25 holes, 7.78 mm pitch", 8, (0.5, 0, 1)),
             "pipe_f": ("10-seg charge light pipe", 6, (0.5, 0, 1)),
             "diffuser_f": ("2 mm opal diffuser", 0, (0.5, 0, 0.82)), "ledboard_f": ("LED board, 427 LEDs", 0, (0.5, 0, 0.6)),
             "tabs_f": ("U body tabs (bent)", 0, (0.5, 0, 0.38)), "pem_tab_f": ("M4 PEM nuts", 0, (0.5, 0, 0.15)),
             "screws_f": ("7x M4 button heads", -12, (0.5, 0, 0))})

# ---------------------------------------------------------------- 4. rear stack
RR = {"plate_rear": {"t": (-90, 0, 0)}, "screws_r": {"t": (-140, 0, 0)}, "screws_fan": {"t": (-150, 0, 0)},
      "fan_": {"t": (-35, 0, 0)}, "pem_tab_r": {"t": (14, 0, 0)}, "feet_r": {"t": (-90, 0, -12)}}
shot("x04_rear_stack.png", "Rear stack: plate, NF-A14 fan, tabs", RR,
     only=("plate_rear", "screws_r", "screws_fan", "fan_", "tabs_r", "pem_tab_r", "feet_r"),
     view=(-1.0, -1.5, 0.5), zoom=1.05,
     labels={"plate_rear": ("Rear plate, 21x30 holes", 8, (0.5, 0, 1)), "fan_": ("Noctua NF-A14, intake", 8, (0.5, 0, 1)),
             "screws_fan": ("4x M4 button + nut (fan)", 0, (0.5, 0, 1)), "tabs_r": ("U body tabs + PEM nuts", 0, (0.5, 0, 0.3)),
             "screws_r": ("7x M4 button heads", -12, (0.5, 0, 0))})

# ---------------------------------------------------------------- 5. cell module
MOD = {"int_cell_": {"s": (0, 0.55, 0)}, "int_comp_insul": {"s": (0, 0.55, 0)}, "int_comp_endplates": {"s": (0, 0.75, 0)},
       "int_comp_rodnuts": {"s": (0, 0.9, 0)}, "int_comp_rods": {"t": (0, 0, 0)},
       "int_comp_pcb_standoffs": {"s": (0, 0.75, 0), "t": (0, 0, 40)},
       "int_busbar_": {"s": (0, 0.55, 0), "t": (0, 0, 70)}, "int_busbar_screws": {"s": (0, 0.55, 0), "t": (0, 0, 115)},
       "int_flex": {"t": (0, 0, 95)}, "int_pack_": {"t": (0, 0, 140)},
       "int_carrier": {"t": (0, 0, -70)}, "screws_hold": {"s": (0, 0.75, 0), "t": (0, 0, -120)}}
shot("x05_cell_module.png", "Cell module: 8x LF50K, G10 sheets, end plates, tie rods, busbars, sense flex", MOD,
     only=("int_cell", "int_comp", "int_busbar", "int_flex", "int_pack", "int_carrier", "screws_hold"),
     view=(0.8, -1.3, 0.75), zoom=1.1,
     labels={"int_cell_1": ("Cell 1 (pack -)", 6), "int_cell_8": ("Cell 8 (pack +)", 6),
             "int_comp_endplates": ("8 mm 6061 end plates", 6, (1, 0, 1)), "int_comp_rods": ("4x M5 tie rods", 0, (0.55, 0, 0)),
             "int_busbar_screws": ("16x M4 terminal screws", 6, (0.15, 0.5, 1)), "int_busbar_": ("Copper busbars", 0, (0.9, 0, 0.5)),
             "int_flex": ("Flex sense CCS + NTCs", 6, (0.6, 0.5, 1)),
             "int_pack_": ("Pack- return bar to front", 6, (0.3, 0.5, 1)), "int_carrier": ("MJF PA12 carrier", 0, (0.6, 0, 0)),
             "screws_hold": ("4x M4 hold-down", -8, (1, 0, 0)), "int_comp_insul": ("1 mm G10 sheets", 6, (0.0, 0, 1)),
             "int_comp_pcb_standoffs": ("Tray standoffs", 6, (1, 0, 1)), "int_comp_rodnuts": ("Rod nuts", 0, (1, 0, 0))})

# ---------------------------------------------------------------- 6. electronics stack
EL = {"inverter": {"t": (0, 0, 190)}, "screws_trays": {"t": (0, 0, 0)}, "tray2": {"t": (0, 0, 140)},
      "inv_posts": {"t": (0, 0, 100)}, "charger": {"t": (0, 0, 60)}, "ctrl_": {"t": (0, 0, 90)},
      "cb_standoffs": {"t": (0, 0, 45)}, "tray1": {"t": (0, 0, 0)}, "mica_tray": {"t": (0, 0, -25)},
      "int_comp_pcb_standoffs": {"t": (0, 0, -45)}, "int_comp_endplates": {"t": (0, 0, -45)}}
shot("x06_electronics.png", "Electronics decks: tray 1 (charger + control board), tray 2 (inverter)", EL,
     only=("inverter", "tray", "inv_posts", "charger", "ctrl_", "cb_standoffs", "mica_tray", "int_comp_pcb_standoffs",
           "int_comp_endplates"), view=(1.0, -1.15, 0.6), zoom=0.95, ghost=("int_comp_endplates",),
     labels={"inverter": ("MEAN WELL NTS-400P, 4x M3", 8, (0.3, 0, 1)), "tray2": ("Tray 2, 5052", 0, (0.2, 0, 0)),
             "inv_posts": ("4x posts", 0, (0, 0, 0.5)), "charger": ("MEAN WELL NPB-450, 4x M4", 0, (0.3, 0, 0.6)),
             "ctrl_contactor": ("Control board", 10, (1, 0, 1)), "cb_standoffs": ("4x M3 standoffs", 0, (1, 0, 0)),
             "tray1": ("Tray 1, 5052, flanged", 0, (0.2, 0, 0.2)), "mica_tray": ("Mica sheet", 0, (0.5, 0, 0)),
             "int_comp_pcb_standoffs": ("Standoffs on module end plates", 0, (0, 0, 0))})

# ---------------------------------------------------------------- 7. control board
CB = {"ctrl_contactor": {"t": (0, 0, 140)}, "ctrl_fuse": {"t": (0, 0, 55)}, "ctrl_shunt": {"t": (0, 0, 30)},
      "ctrl_precharge": {"t": (0, 0, 75)}, "ctrl_afe": {"t": (0, 0, 40)}, "ctrl_esp32": {"t": (0, 0, 25)},
      "ctrl_buck": {"t": (0, 0, 50)}, "ctrl_fan_conn": {"t": (0, 0, 65)}, "ctrl_led_conn": {"t": (0, 0, 45)},
      "ctrl_terminals": {"t": (0, 0, 35)}, "ctrl_ccs_conn": {"t": (0, 0, -22)}, "ctrl_pcb": {"t": (0, 0, 0)},
      "cb_standoffs": {"t": (0, 0, -35)}, "int_pack_pos": {"t": (0, 0, -60)}}
shot("x07_control_board.png", "Control board: power path, AFE, ESP32, fan buck, connectors", CB,
     only=("ctrl_", "cb_standoffs", "int_pack_pos"), view=(0.3, -1.0, 0.7), zoom=1.05,
     labels={"ctrl_contactor": ("Contactor (MiniTACTOR class)", 6), "ctrl_fuse": ("Main fuse", 6),
             "ctrl_shunt": ("Shunt", 6), "ctrl_precharge": ("Precharge relay", 6), "ctrl_afe": ("BQ76952 AFE", 6),
             "ctrl_esp32": ("ESP32 (Wi-Fi debug)", 6), "ctrl_buck": ("24->12 V fan buck", 14),
             "ctrl_fan_conn": ("Fan header", 22), "ctrl_led_conn": ("LED header", 6),
             "ctrl_terminals": ("Cable terminal strip", 6), "ctrl_ccs_conn": ("Sense flex connector", -24),
             "int_pack_pos": ("Pack+ riser", -6, (0.5, 0.5, 0)), "cb_standoffs": ("4x M3 standoffs", -6, (0.5, 0, 0))})

# ---------------------------------------------------------------- 8. lid + panel connectors (from below)
LID = {"panel_": {"t": (0, 0, 120)}, "screws_panel": {"t": (0, 0, 185)}, "pem_lid": {"t": (0, 0, -45)},
       "screws_lid": {"s": (1, 0.9, 0), "t": (0, 0, -45)}}
shot("x08_lid_connectors.png", "Lid: NEMA 5-15R, IEC C14, Anderson SB50, CAN M12", LID,
     only=("lid", "panel_", "screws_panel", "pem_lid", "screws_lid"), view=(0.9, -1.0, 0.9), zoom=1.2,
     labels={"panel_outlet": ("NEMA 5-15R 120 V out", 0, (0, 0, 0.5)), "panel_inlet": ("IEC C14 inlet", 6, (0.5, 0.5, 1)),
             "panel_dc": ("Anderson SB50 DC", 0, (1, 0, 0.4)), "panel_can": ("CAN M12", 6, (0.5, 0.5, 1)),
             "screws_panel": ("8x panel screws", 8, (0.5, 0.5, 1)),
             "pem_lid": ("M3 PEM nuts in lip", -10, (0.5, 0, 0)), "screws_lid": ("M3 lid screws", 0, (0, 0, 0)),
             "lid": ("Lid, joggle lip nests inside U", 0, (0.15, 0, 0.6))})

# ---------------------------------------------------------------- 9. wiring (assembled, shell hidden)
WR = {}
shot("x09_wiring.png", "Wiring: every cable run to its terminal", WR,
     only=("cable_", "ctrl_", "charger", "inverter", "panel_", "fan_", "int_pack_pos"),
     ghost=("charger", "inverter", "fan_", "panel_", "ctrl_contactor"), view=(1.0, -0.9, 0.8), zoom=1.3,
     labels={"cable_ac_out": ("AC out: inverter -> outlet", 4, (0.6, 0.5, 1)), "cable_ac_in": ("AC in: C14 -> charger", 4, (0.2, 0.5, 0.6)),
             "cable_chg_dc_pos": ("Charger DC -> terminals", 0, (0.3, 0.5, 0.2)),
             "cable_inv_dc_pos": ("Inverter DC <- terminals", 0, (0.3, 0.5, 1)),
             "cable_dc_out": ("SB50 <- terminals", 0, (0.7, 0.5, 0.6)), "cable_can": ("CAN", 4, (0.5, 0.5, 1)),
             "cable_fan": ("Fan PWM, along side gap", 4, (0.3, 0.5, 0)), "cable_led": ("LED data", 4, (1, 0.5, 1)),
             "cable_ccs": ("Sense flex tail", -6, (0.5, 0.5, 0)), "int_pack_pos": ("Pack+ riser", -4, (0.5, 0.5, 0))})

# ---------------------------------------------------------------- 10. module + electronics, shell removed, nothing exploded
shot("x10_internals_assembled.png", "Internals assembled, shell removed", {},
     hide=("u_body", "lid", "pem_", "screws_lid", "plate_", "screws_f", "screws_r", "pipe_f", "feet_", "tabs_", "int_liner",
           "diffuser", "ledboard", "panel_", "screws_panel"), view=(-0.9, -1.1, 0.7), zoom=1.2)
