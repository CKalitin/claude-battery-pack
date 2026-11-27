"""Pre-CAD harness drawing set for vendor quotes (2026-11-27). One page per assembly, from docs/harnesses.md.
Lengths are PRE-CAD estimates (tower17 will measure them). Writes docs/harness-drawings/harnesses_preCAD.pdf
Run: ~/.venvs/cad/bin/python cad/analysis/harness_drawings.py
"""
import os, textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "harness-drawings")
os.makedirs(OUT, exist_ok=True)
MF = "Molex Micro-Fit 3.0 receptacle housing 43645-0{n}00 + 43030 crimps"
COMMON = ("All wire: UL1007/UL1015 or 105 C rated, stranded tinned copper. Lengths are end-to-end in mm, tolerance +/-10 mm. "
          "Label each branch end with its ID. 100 % continuity test. Qty: 2 sets.")

ASSY = [
    ("A  BMS low-voltage harness (multi-branch, one assembly)", [
        ("A1 B+ tap", "J3 pos 1", MF.format(n=4), "18 AWG thin-wall red", 380, "Inline fuse holder Eaton ATM-FHID with 5 A ATM fuse, holder within 150 mm of the ring; ring terminal 1/4in (M6) for 18 AWG"),
        ("A2 LOAD+ tap", "J3 pos 2", "(same J3 housing)", "18 AWG thin-wall orange", 290, "Inline ATM-FHID with 2 A ATM fuse within 150 mm of the ring; ring terminal 3/8in (M10)"),
        ("A3 GND (shunt node A)", "J3 pos 3", "(same J3 housing)", "18 AWG thin-wall black", 200, "Ring terminal 5/16in (M8)"),
        ("A3b IMD chassis ref", "J3 pos 4", "(same J3 housing)", "22 AWG green/yellow", 160, "Ring terminal M4 (rear-plate -y top screw)"),
        ("A4 Contactor coil", "J4 pos 1 X1 red, pos 2 X2 black", MF.format(n=2), "contactor's own leads", 380, "Gigavac GV141BAX contactor (vendor-procured or consigned) - terminate its 38 cm flying leads at full length, do not cut"),
        ("A5 Charger relay coil", "J6 pos 1 = relay 86, pos 2 = relay 85", MF.format(n=3), "20 AWG", 150, "2 x insulated 6.3 mm FASTON receptacles for TE V23134-B1052-C642 relay pins 86/85"),
        ("A6 AC sense", "J6 pos 3", "(same J6 housing)", "22 AWG", 160, "Insulated 6.3 mm piggyback FASTON on relay pin 30"),
        ("A7 Inverter remote", "J7 pos 1, 2", MF.format(n=2), "22 AWG", 120, "JST XHP-2 + SXH-001T (to MEAN WELL NTS-400P CN301)"),
        ("A8 Lid button", "J8 pos 1 BTN, 2 GND", MF.format(n=2), "22 AWG", 420, "2 x insulated 6.3 mm FASTON receptacles (button TBD)"),
        ("A9 LED board link", "J5 pos 1 5V, 2 DATA, 3 GND", MF.format(n=3), "22 AWG", 260, MF.format(n=3) + " (same pin order)"),
        ("A10 Box-air NTC", "J9 pos 1, 2", MF.format(n=2), "24 AWG", 210, "Vishay NTCLE413E2103F102L 10 kOhm NTC (AWG30 leads): splice to 24 AWG, heat shrink"),
    ]),
    ("B  Charger DC set (3 cables)", [
        ("B1 Charger + to relay", "MEAN WELL NPB-360-12TB terminal V+", "Bootlace ferrule 10 AWG", "10 AWG red", 150, "Insulated 6.3 mm FASTON receptacle for 10-12 AWG (relay pin 30)"),
        ("B2 Relay to fuse", "Relay pin 87", "Insulated 6.3 mm FASTON receptacle 10-12 AWG", "10 AWG red", 390, "Ring terminal 3/8in (M10), adhesive heat shrink"),
        ("B3 Charger -", "NPB-360-12TB terminal V-", "Bootlace ferrule 10 AWG", "10 AWG black", 190, "Ring terminal 5/16in (M8), adhesive heat shrink"),
    ]),
    ("C  Inverter DC set (2 cables)", [
        ("C1 Inverter +", "MEAN WELL NTS-400P TB1 (+)", "Anderson Powerpole 1327 (red) + 261G2-LPBK contact", "10 AWG red", 340, "Ring terminal 3/8in (M10), adhesive heat shrink"),
        ("C2 Inverter -", "NTS-400P TB1 (-)", "Anderson Powerpole 1327G6 (black) + 261G2-LPBK, mated to C1 housing", "10 AWG black", 150, "Ring terminal 5/16in (M8), adhesive heat shrink"),
    ]),
    ("D  Mains set (120 VAC)", [
        ("D1 AC in L/N/PE", "Panel IEC C14 inlet (L, N, PE)", "3 x insulated 6.3 mm FASTON receptacles", "3 x 18 AWG UL1015 black/white/green", 360, "L-com ACPWRC-C13LR right-angle C13 connector (screw terminals) into the charger"),
        ("D2 AC in PE bond", "D1 PE at inlet end (piggyback)", "insulated 6.3 mm piggyback FASTON", "18 AWG green/yellow", 300, "Ring terminal M4 (front-plate +y top screw)"),
        ("D3 AC out", "NTS-400P CN500: pos 6 L, pos 4 N, pos 1 FG", "JST VHR-6N + SVH-21T-P1.1", "3 x 18 AWG UL1015 black/white/green", 250, "3 x insulated 6.3 mm FASTON receptacles to NEMA 5-15R outlet (outlet TBD)"),
        ("D4 AC out ground bond", "D3 ground at outlet end", "insulated 6.3 mm piggyback FASTON", "18 AWG green/yellow", 250, "Ring terminal M4 (front-plate +y top screw)"),
    ]),
    ("E  Inverter fan pigtail", [
        ("E1 Fan lead", "Sunon MF40201VX-1000U-G99 40x40x20 fan (vendor-procured)", "fan's own leads", "fan's own leads", 60, "JST XHP-3 + SXH-001T: pos 1 red (+12 V), pos 2 black (GND), pos 3 empty"),
    ]),
]


BOM = {
    "A": [("43645-0400", "Molex Micro-Fit 3.0 receptacle housing 1x4", 1), ("43645-0300", "Molex Micro-Fit 3.0 receptacle housing 1x3", 2), ("43645-0200", "Molex Micro-Fit 3.0 receptacle housing 1x2", 4),
          ("43030-0007", "Molex Micro-Fit 3.0 female crimp terminal 20-24 AWG", 13), ("43030-0038", "Molex Micro-Fit 3.0 female crimp terminal 18 AWG (insulation OD <= 1.85 mm)", 3),
          ("ATM-FHID", "Eaton Bussmann inline ATM fuse holder 16 AWG", 2), ("ATM-5", "ATM fuse 5 A", 1), ("ATM-2", "ATM fuse 2 A", 1),
          ("Ring 1/4in 18AWG", "Insulated ring terminal 1/4in stud, 22-18 AWG", 1), ("Ring 3/8in 18AWG", "Insulated ring terminal 3/8in stud, 22-18 AWG", 1),
          ("Ring 5/16in 18AWG", "Insulated ring terminal 5/16in stud, 22-18 AWG", 1), ("Ring M4 22AWG", "Insulated ring terminal M4, 26-22 AWG", 1), ("FASTON 6.3 insulated", "TE FASTON .250 insulated receptacle 22-18 AWG", 4),
          ("FASTON 6.3 piggyback", "TE FASTON .250 insulated piggyback receptacle 22-18 AWG", 1), ("XHP-2", "JST XH housing 2-pin", 1),
          ("SXH-001T-P0.6", "JST XH crimp terminal", 2), ("NTCLE413E2103F102L", "Vishay 10 kOhm NTC, AWG30 leads: splice to 24 AWG with heat shrink", 1),
          ("GV141BAX", "Gigavac GV14 contactor, consigned by customer (terminate its leads only)", 1),
          ("Wire 18 AWG thin-wall", "18 AWG thin-wall (UL1061 or XLPE UL3266), insulation OD <= 1.85 mm, red/orange/black", 1), ("Wire 20-26 AWG", "UL1007 20/22/26 AWG, total length per drawing", 1)],
    "B": [("Ferrule 10 AWG", "Insulated bootlace ferrule 6 mm2 / 10 AWG", 2), ("FASTON 6.3 10AWG", "TE FASTON .250 insulated receptacle 12-10 AWG", 2),
          ("Ring 3/8in 10AWG", "Tinned copper ring lug 3/8in stud 10 AWG + adhesive heat shrink", 1), ("Ring 5/16in 10AWG", "Tinned copper ring lug 5/16in stud 10 AWG + adhesive heat shrink", 1),
          ("Wire 10 AWG", "10 AWG fine-strand 105 C red 450 mm, black 180 mm", 1)],
    "C": [("1327", "Anderson Powerpole PP15-45 housing red", 1), ("1327G6", "Anderson Powerpole PP15-45 housing black", 1),
          ("261G2-LPBK", "Anderson Powerpole 45 A contact 10-14 AWG", 2), ("Ring 3/8in 10AWG", "Tinned copper ring lug 3/8in 10 AWG + heat shrink", 1),
          ("Ring 5/16in 10AWG", "Tinned copper ring lug 5/16in 10 AWG + heat shrink", 1), ("Wire 10 AWG", "10 AWG fine-strand 105 C red 240 mm, black 130 mm", 1)],
    "D": [("ACPWRC-C13LR", "L-com right-angle IEC C13 field-termination connector", 1), ("VHR-6N", "JST VH housing 6-pin", 1),
          ("SVH-21T-P1.1", "JST VH crimp terminal 18-22 AWG", 3), ("FASTON 6.3 insulated", "TE FASTON .250 insulated receptacle 18 AWG", 6),
          ("FASTON 6.3 piggyback", "TE FASTON .250 insulated piggyback 18 AWG", 2), ("Ring M4 18AWG", "Insulated ring terminal M4 18 AWG", 2),
          ("Wire 18 AWG UL1015", "UL1015 18 AWG black/white/green, total per drawing", 1)],
    "E": [("XHP-3", "JST XH housing 3-pin", 1), ("SXH-001T-P0.6", "JST XH crimp terminal", 2),
          ("MF40201VX-1000U-G99", "Sunon 40x40x20 12 V fan (supplier to procure), terminate its leads", 1)],
}

def bom_page(pdf, key, title):
    fig = plt.figure(figsize=(16.5, 11.7), dpi=100)
    fig.text(0.03, 0.95, "Bill of materials - harness " + title, fontsize=16, weight="bold")
    ax = fig.add_axes([0.03, 0.05, 0.94, 0.86]); ax.axis("off")
    cell = [[pn, d, str(q)] for pn, d, q in BOM[key]]
    t = ax.table(cellText=cell, colLabels=["Part number", "Description", "Qty"], loc="upper center", cellLoc="left", colWidths=[0.2, 0.7, 0.08])
    t.auto_set_font_size(False); t.set_fontsize(10)
    for (r, c), cl in t.get_celld().items():
        cl.set_height(0.04)
        if r == 0:
            cl.set_text_props(weight="bold"); cl.set_facecolor("#eeeeee")
    pdf.savefig(fig); plt.close(fig)

def page(pdf, title, rows):
    fig = plt.figure(figsize=(16.5, 11.7), dpi=100)   # A3 landscape
    fig.text(0.03, 0.95, "Claude battery pack - wire harness  " + title, fontsize=18, weight="bold")
    fig.text(0.03, 0.92, "Rev B (lengths from the v17 CAD routes + 30 mm per end + 150 mm lid loops), 2026-11-27. " + COMMON, fontsize=9.5, wrap=True)
    ax = fig.add_axes([0.02, 0.05, 0.96, 0.84]); ax.axis("off")
    cols = ["Branch", "End 1 (pin)", "End 1 connector / terminal", "Wire", "Length mm", "End 2 connector / terminal"]
    W = [18, 26, 34, 18, 8, 60]
    cell = [[textwrap.fill(str(v), w) for v, w in zip([r[0], r[1], r[2], r[3], r[4], r[5]], W)] for r in rows]
    t = ax.table(cellText=cell, colLabels=cols, loc="upper center", cellLoc="left", colWidths=[0.11, 0.15, 0.2, 0.11, 0.05, 0.38])
    t.auto_set_font_size(False); t.set_fontsize(9)
    for (r, c), cl in t.get_celld().items():
        cl.set_height(0.075 if r else 0.04)
        if r == 0:
            cl.set_text_props(weight="bold"); cl.set_facecolor("#eeeeee")
    pdf.savefig(fig); plt.close(fig)

if __name__ == "__main__":
    allp = os.path.join(OUT, "harnesses_preCAD.pdf")
    with PdfPages(allp) as pdf:
        for title, rows in ASSY:
            page(pdf, title, rows); bom_page(pdf, title[0], title)
    for title, rows in ASSY:
        p = os.path.join(OUT, f"harness_{title[0]}_preCAD.pdf")
        with PdfPages(p) as pdf:
            page(pdf, title, rows); bom_page(pdf, title[0], title)
    print(allp)
