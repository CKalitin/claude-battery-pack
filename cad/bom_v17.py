"""v17 (option D) SendCutSend BOM. No new live quotes: each part is scaled from its v16.3 quote (docs/v16-bom.md) by the
model flats: price17 = price16 x (A17/A16 + C17/C16) / 2, A = flat bounding box, C = cut length. Parts without a v16 twin
are scaled from the nearest same-material part, floor $5. Every scaled line is an estimate (⚠️) until re-quoted from the
DXF flats in versions/v17-option-d/scs_dxf (cad/flats17.py). Run after flats17: ~/.venvs/cad/bin/python cad/bom_v17.py
Writes versions/v17-option-d/bom.md and bom.json (read by cad/analysis/budget_D.py)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "concepts", "contactor"))
VER = os.path.join(HERE, "..", "versions", "v17-option-d")

def v16_flats():
    """(bbox area mm2, cut mm) of the v16.3 parts, measured from tower15 / C1 with the same method as flats17."""
    import ezdxf
    from build123d import Plane, section
    import tower15 as t5, flats15
    from c1_power_module import build as c1
    out = {}
    def sec(solid, axis):
        bb = solid.bounding_box()
        c = {"x": (bb.min.X + bb.max.X) / 2, "y": (bb.min.Y + bb.max.Y) / 2, "z": (bb.min.Z + bb.max.Z) / 2}[axis]
        pl = {"x": Plane.YZ.offset(c), "y": Plane.XZ.offset(-c), "z": Plane.XY.offset(c)}[axis]
        faces = [pl.to_local_coords(f) for f in section(solid, section_by=pl).faces()]
        from build123d import Compound
        b = Compound(faces).bounding_box()
        return b.size.X * b.size.Y, sum(w.length for f in faces for w in f.wires())
    def dxf(path):
        msp = ezdxf.readfile(path).modelspace()
        xs, ys, cut = [], [], 0.0
        for e in msp:
            if e.dxf.layer != "CUT":
                continue
            if e.dxftype() == "CIRCLE":
                cut += 2 * math.pi * e.dxf.radius
            else:
                p = [(v[0], v[1]) for v in e.get_points()]
                xs += [a for a, _ in p]; ys += [a for _, a in p]
                cut += sum(math.dist(a, c) for a, c in zip(p, p[1:] + p[:1]))
        return (max(xs) - min(xs)) * (max(ys) - min(ys)), cut
    for side in (-1, 1):
        f = flats15.body_flat(side)[0]
        out["body_half_A" if side < 0 else "body_half_B"] = dxf(f)
    out["lid"] = dxf(flats15.lid_flat()[0])
    out["plate_front"] = sec(t5.plate(True), "x"); out["plate_rear"] = sec(t5.plate(False), "x")
    out["module_endplate"] = sec(t5.module_endplates()[0].solids()[0], "x")
    out["g10_floor"] = sec(t5.g10_floor(), "z"); out["g10_frame"] = sec(t5.g10_frame(), "z")
    out["tray1"] = sec(t5.tray1(), "z"); out["tray2"] = sec(t5.tray2(), "z")
    out["diffuser_f"] = sec(t5.diffuser(), "x"); out["pipe_f"] = sec(t5.light_pipe(), "z")
    out["mylar_top"] = sec(t5.g10_top(), "z"); out["mylar_spacer"] = sec(t5.spacers().solids()[0], "x")
    bars = t5.busbars()
    out["bus_ABC"] = sec(bars["A"], "z")
    c = c1("gv14up")
    out["g10_plate"] = sec(c.parts["g10_plate"], "z"); out["g10_sb_cheek"] = sec(c.parts["g10_sb_cheek_0"], "x")
    for n in ("bus_mod_in", "bus_mod_load", "bus_mod_neg"):
        out[n] = sec(c.parts[n], "z")
    out["bus_pack_pos"] = (74.6 * 80.3, 2 * (74.6 + 80.3)); out["bus_pack_neg"] = (229.6 * 76.8, 2 * (229.6 + 76.8))   # v16-bom.md sizes
    out["strap_main"] = (122.0 * 19.0, 2 * (122.0 + 19.0))
    return out

# v17 part: (label, qty, v16 twin for scaling, v16.3 price each, note, quote status)
PARTS = [
    ("body_half_A", "body_half_A (5052 .063, gloss red, 8 M4 taps)", 1, "body_half_A", 165.85, "v16.3 live quote + taps"),
    ("body_half_B", "body_half_B (5052 .063, gloss red, 6 M4 taps)", 1, "body_half_B", 159.35, "v16.3 live quote + taps"),
    ("lid", "lid (5052 .063, 6 bends, gloss red, 4 clinch nuts)", 1, "lid", 131.28, "v16.3 live quote + clinch nuts"),
    ("plate_front", "plate_front (6061 .125, hole grid)", 1, "plate_front", 206.02, "v16.3"),
    ("plate_rear", "plate_rear (6061 .125, full grid)", 1, "plate_rear", 232.39, "v16.3 live quote"),
    ("module_endplate", "module_endplate (6061 .313)", 2, "module_endplate", 53.43, "v16.3 live quote; SO_Y moved, same part otherwise"),
    ("g10_floor", "g10_floor (G10 .187)", 1, "g10_floor", 97.15, "v16.3 quote, unchanged"),
    ("g10_frame", "g10_frame (G10 .187; 1.2 mm narrower)", 1, "g10_frame", 95.70, "v16.3 quote"),
    ("deck1", "deck1 (G10 .125 design, priced .187)", 1, "tray1", 92.85, "scaled from tray 1"),
    ("deck2", "deck2 (G10 .125 design, priced .187)", 1, "tray2", 86.89, "scaled from tray 2"),
    ("g10_bay", "g10_bay (G10 .125 design, priced .187)", 1, "g10_plate", 33.36, "scaled from the C1 plate"),
    ("g10_bms_bridge", "g10_bms_bridge (G10 .125 design, priced .187) NEW", 1, "g10_plate", 33.36, "scaled from the C1 plate"),
    ("g10_sb_cheek", "g10_sb_cheek (G10)", 2, "g10_sb_cheek", 9.23, "v16.3 quote"),
    ("mylar_top", "mylar_top (Mylar .010)", 1, "mylar_top", 19.16, "v16.3 quote"),
    ("mylar_spacer", "mylar_spacers (Mylar .010)", 9, "mylar_spacer", 4.57, "v16.3 quote"),
    ("bus_A", "bus_A/B/C (Cu .125)", 3, "bus_ABC", 25.47, "v16.3 quote"),
    ("bus_pack_pos", "bus_pack_pos (Cu .125, 2 bends)", 1, "bus_pack_pos", 46.98, "v16.3 flat price, re-quote bent"),
    ("bus_pack_neg", "bus_pack_neg (Cu .125, 2 bends)", 1, "bus_pack_neg", 89.47, "v16.3 flat price, re-quote bent"),
    ("bus_mod_pos", "bus_mod_pos (Cu .125, + rail)", 1, "bus_mod_load", 34.29, "scaled from the C1 load bar"),
    ("bus_mod_neg", "bus_mod_neg (Cu .125, - rail)", 1, "bus_mod_neg", 9.53, "scaled"),
    ("bus_mod_in", "bus_mod_in (Cu .125, in-bar)", 1, "bus_mod_in", 8.95, "scaled"),
    ("strap_main", "strap_main (Cu .125, 2 bends)", 1, "strap_main", 21.63, "v16.3 flat price; bends not priced"),
    ("diffuser_f", "diffuser_f (white acrylic .118)", 1, "diffuser_f", 48.86, "v16.3 quote"),
    ("pipe_f", "pipe_f (clear acrylic .118)", 1, "pipe_f", 2.00, "v16.3 quote"),
]
FLOOR = 5.0
UNCHANGED = ("g10_floor", "mylar_spacer", "bus_A", "pipe_f")   # identical to the v16.3 parts: quote stands

def main():
    st = json.load(open(os.path.join(VER, "scs_dxf", "parts.json")))
    old = v16_flats()
    rows, tot, tot_a, tot_c = [], 0.0, 0.0, 0.0
    for key, label, qty, twin, p16, note in PARTS:
        a17, c17 = st[key]["w"] * st[key]["h"], st[key]["cut"]
        a16, c16 = old[twin]
        f = (a17 / a16 + c17 / c16) / 2
        each = p16 if key in UNCHANGED else max(FLOOR, p16 * f)
        q = "✓" if key in UNCHANGED else "⚠️"
        tot += qty * each
        tot_a += qty * (each if key in UNCHANGED else max(FLOOR, p16 * a17 / a16))
        tot_c += qty * (each if key in UNCHANGED else max(FLOOR, p16 * c17 / c16))
        rows.append(dict(key=key, label=label, qty=qty, p16=p16, f=round(f, 2), each=round(each, 2), total=round(qty * each, 2), note=note, ok=q,
                         w=st[key]["w"], h=st[key]["h"], cut=c17, bends=st[key]["bends"]))
    L = ["# v17 option D: SendCutSend BOM estimate (USD, 2026-11-27)", "",
         "Generated by `cad/bom_v17.py` from the model flats (`cad/flats17.py`, DXFs and `DFM_report.txt` in `scs_dxf/`). "
         "**No new live quote**: price = v16.3 quote × (flat-area ratio + cut-length ratio) / 2. ⚠️ re-quote from the DXFs before ordering.", "",
         "| Part | Qty | Flat w × h [mm] | Cut [mm] | v16.3 ea | Factor | Each | Total | Basis | |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['label']} | {r['qty']} | {r['w']} × {r['h']} | {r['cut']:.0f} | {r['p16']:.2f} | {r['f']:.2f} | {r['each']:.2f} | {r['total']:.2f} | {r['note']} | {r['ok']} |")
    L += [f"| **SCS total** | | | | | | | **{tot:,.0f}** | under the $2,000 sponsorship cap by ${2000 - tot:,.0f} ⚠️ | |", "",
          f"- Sensitivity of the scaling method: area-only **${tot_a:,.0f}**, cut-length-only **${tot_c:,.0f}** (both ⚠️).",
          "- ⚠️ SCS had G10 .125 out of stock (v16-bom.md, 2026-11-25): deck 1, deck 2, bay plate and bridge are priced as .187. If .187 is ordered, deck 2 drops 1.6 mm and clears the charger by 0.9 mm (not 2.5), and the bay plate / bridge grow 1.6 mm (check before ordering).",
          "- ⚠️ Not priced: bends on the pack busbars and Z-strap, taps / clinch hardware changes on the shell, shipping to Canada.", ""]
    open(os.path.join(VER, "bom.md"), "w").write("\n".join(L))
    json.dump(dict(rows=rows, total=tot, total_area=tot_a, total_cut=tot_c), open(os.path.join(VER, "bom.json"), "w"), indent=1)
    print(f"SCS {tot:.0f}  area-only {tot_a:.0f}  cut-only {tot_c:.0f}")
    for r in rows:
        print(f"  {r['key']:16s} x{r['qty']} f {r['f']:.2f} each {r['each']:.2f}")

if __name__ == "__main__":
    main()
