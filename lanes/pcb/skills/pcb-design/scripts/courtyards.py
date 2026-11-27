"""Courtyard area of every part on a board, read from the KiCad footprint libraries (pcb-design skill, area-budget.md).

Copy this file next to the project and replace BOM with the board's sizing BOM. The BOM below is the worked example:
the 2026 battery-pack BMS board (ESP32-S3 + BQ76952 + coil drivers + precharge), which came to 2,421 mm^2 and
fitted 95 x 55 mm at 49 % occupancy.

Usage: python3 courtyards.py            -> table + totals (markdown)
Each BOM line: (block, function, footprint lib:name or ('box', w, h, note), qty).
Courtyard = bounding box of the footprint's F.CrtYd graphics (KiCad's IPC-7351 courtyard).
"""
import re, sys, os, math
LIB = "/usr/share/kicad/footprints"

def crtyd_bbox(lib, name):
    path = f"{LIB}/{lib}.pretty/{name}.kicad_mod"
    txt = open(path).read()
    xs, ys = [], []
    # every graphic item on F.CrtYd: collect its points (start/end/center/pts xy/mid)
    for m in re.finditer(r"\((fp_line|fp_rect|fp_poly|fp_circle|fp_arc)\b(.*?)\(layer \"F\.CrtYd\"\)", txt, re.S):
        kind, body = m.group(1), m.group(2)
        pts = [(float(a), float(b)) for a, b in re.findall(r"\((?:start|end|xy|mid) ([-\d.]+) ([-\d.]+)\)", body)]
        if kind == "fp_circle":
            c = re.search(r"\(center ([-\d.]+) ([-\d.]+)\)", body); e = re.search(r"\(end ([-\d.]+) ([-\d.]+)\)", body)
            cx, cy, ex, ey = map(float, (*c.groups(), *e.groups())); r = math.hypot(ex - cx, ey - cy)
            pts = [(cx - r, cy - r), (cx + r, cy + r)]
        for x, y in pts: xs.append(x); ys.append(y)
    if not xs:
        raise SystemExit(f"no courtyard in {path}")
    return max(xs) - min(xs), max(ys) - min(ys)

R04 = ("Resistor_SMD", "R_0402_1005Metric"); C04 = ("Capacitor_SMD", "C_0402_1005Metric")
R06 = ("Resistor_SMD", "R_0603_1608Metric"); C06 = ("Capacitor_SMD", "C_0603_1608Metric")
C08 = ("Capacitor_SMD", "C_0805_2012Metric"); C12 = ("Capacitor_SMD", "C_1206_3216Metric")
S23 = ("Package_TO_SOT_SMD", "SOT-23"); SOD323 = ("Diode_SMD", "D_SOD-323"); SMA = ("Diode_SMD", "D_SMA")
TP = ("TestPoint", "TestPoint_Pad_D1.0mm")
MF = lambda n: ("Connector_Molex", n)

BOM = [
 # block, function, footprint, qty
 ("AFE", "BQ76952PFBR TQFP-48", ("Package_QFP", "TQFP-48_7x7mm_P0.5mm"), 1),
 ("AFE", "cell-input R 20 Ω (VC0-VC4, 5 taps)", R06, 5),
 ("AFE", "cell-input C 220 nF", C04, 5),
 ("AFE", "unused VC5-VC15 tie / VC16 to top cell: no part", None, 0),
 ("AFE", "BAT series diode + R + 2.2 µF", SOD323, 1), ("AFE", "BAT R", R04, 1), ("AFE", "BAT C 2.2 µF", C06, 1),
 ("AFE", "REGIN NPN FCX495 SOT-89", ("Package_TO_SOT_SMD", "SOT-89-3"), 1),
 ("AFE", "NPN collector diode", SOD323, 1),
 ("AFE", "BREG/REGIN/REG1/REG18 caps", C04, 4),
 ("AFE", "I2C pull-ups, RST_SHUT, LD, PACK resistors", R04, 5),
 ("AFE", "board NTC 0402 (6th NTC; 5 are on the flex)", R04, 1),
 ("AFE", "NTC filter caps (TS1, TS3, CFETOFF, DFETOFF, HDQ, DCHG)", C04, 6),
 ("AFE", "SRP/SRN unused, tied to VSS: no part", None, 0),
 ("MCU", "ESP32-S3-WROOM-1U-N8 (U.FL)", ("RF_Module", "ESP32-S3-WROOM-1U"), 1),
 ("MCU", "3V3 decoupling 10 µF + 100 nF ×2", C06, 1), ("MCU", "3V3 100 nF", C04, 2),
 ("MCU", "EN RC (10 k + 1 µF)", R04, 1), ("MCU", "EN C", C04, 1),
 ("MCU", "IO0 / strap resistors", R04, 2),
 ("MCU", "Tag-Connect TC2030-NL programming pads (no part)", ("Connector", "Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical"), 1),
 ("SHUNT", "TXU0304 3-out/1-in translator (TSSOP-14 for sizing)", ("Package_SO", "TSSOP-14_4.4x5mm_P0.65mm"), 1),
 ("SHUNT", "translator decoupling", C04, 2), ("SHUNT", "OC input divider 5 V→3V3", R04, 2),
 ("PWR", "input TVS SMAJ18A", SMA, 1),
 ("PWR", "buck TPS62933 SOT-583", ("Package_TO_SOT_SMD", "SOT-583-8"), 1),
 ("PWR", "buck inductor 4×4 mm", ("Inductor_SMD", "L_Bourns-SRN4018"), 1),
 ("PWR", "buck C_in 10 µF 25 V", C12, 2), ("PWR", "buck C_out 22 µF", C08, 2),
 ("PWR", "buck FB divider, BST cap, SS/EN R/C", C04, 5),
 ("PWR", "3V3 LDO 1 A (SOT-223)", ("Package_TO_SOT_SMD", "SOT-223-3_TabPin2"), 1),
 ("PWR", "LDO in/out caps 10 µF", C08, 2),
 ("COIL", "GV14 coil: 2 × N-FET in series (ESP32 AND BQ DDSG)", S23, 2),
 ("COIL", "gate R + pulldown ×2", R04, 4),
 ("COIL", "coil TVS SMAJ24A", SMA, 1),
 ("CHGR", "charger-relay coil N-FET", S23, 1), ("CHGR", "gate R + pulldown", R04, 2),
 ("CHGR", "flyback diode SOD-123", ("Diode_SMD", "D_SOD-123"), 1),
 ("INV", "inverter remote PhotoMOS (SOP-4)", ("Package_SO", "SOP-4_3.8x4.1mm_P2.54mm"), 1),
 ("INV", "LED resistor", R04, 1),
 ("PRE", "precharge relay Omron G6S-2G (SMD, 2 A)", ("Relay_SMD", "Relay_DPDT_Omron_G6S-2G"), 1),
 ("PRE", "relay driver N-FET + R + flyback", S23, 1), ("PRE", "relay driver R", R04, 2), ("PRE", "relay flyback", SOD323, 1),
 ("PRE", "Vishay AC05 10 Ω 5 W, lying flat (Ø7.5 × 18 body)", ("Resistor_THT", "R_Axial_Power_L20.0mm_W6.4mm_P25.40mm"), 1),
 ("IMD", "divider 4 × 0603 (≥ 1 MΩ each) + filter cap", R06, 4), ("IMD", "IMD filter C", C04, 1),
 ("BTN", "button ESD diode + series R", ("Diode_SMD", "D_SOD-523"), 1), ("BTN", "series R", R04, 1),
 ("TEST", "test points: B+, LOAD+, 5V, 3V3, REG1, GND ×2, SDA, SCL, SPI ×4", TP, 13),
 # connectors (right-angle, at the edges)
 ("CONN", "J1 sense flex FPC 12-pin ZIF (5 VC + 5 NTC + 2 GND)", ("Connector_FFC-FPC", "Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal"), 1),
 ("CONN", "J2 Tesla shunt Micro-Fit 2×4", MF("Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal"), 1),
 ("CONN", "J3 power B+/LOAD+/GND Micro-Fit 1×3", MF("Molex_Micro-Fit_3.0_43650-0300_1x03_P3.00mm_Horizontal"), 1),
 ("CONN", "J4 outputs: GV14 coil ×2, charger relay ×2, inverter remote ×2, Micro-Fit 2×3", MF("Molex_Micro-Fit_3.0_43045-0600_2x03_P3.00mm_Horizontal"), 1),
 ("CONN", "J5 lid button + LED-board link (5V, GND, DATA, BTN), Micro-Fit 2×2... 2×3", MF("Molex_Micro-Fit_3.0_43045-0600_2x03_P3.00mm_Horizontal"), 1),
 ("MECH", "M3 mounting holes (Ø7 washer keep-out); one plated = IMD chassis ref", ("MountingHole", "MountingHole_3.2mm_M3_Pad"), 4),
]

def main():
    rows, tot, byblk = [], 0.0, {}
    for blk, fn, fp, q in BOM:
        if fp is None or q == 0:
            rows.append((blk, fn, "—", "—", 0, 0.0)); continue
        w, h = crtyd_bbox(*fp)
        a = w * h * q
        tot += a; byblk[blk] = byblk.get(blk, 0) + a
        rows.append((blk, fn, f"{fp[1]}", f"{w:.2f} × {h:.2f}", q, a))
    out = ["| Block | Function | Footprint (KiCad 10.0.8) | Courtyard [mm] | Qty | Area [mm²] |", "|---|---|---|---|---|---|"]
    out += [f"| {b} | {f} | {fp} | {wh} | {q} | {a:.0f} |" for b, f, fp, wh, q, a in rows]
    out.append(f"| **Total** | | | | **{sum(r[4] for r in rows)}** | **{tot:.0f}** |")
    out.append("")
    out.append("| Block | Courtyard [mm²] |\n|---|---|")
    out += [f"| {k} | {v:.0f} |" for k, v in sorted(byblk.items(), key=lambda kv: -kv[1])]
    print("\n".join(out))
    return tot, byblk

if __name__ == "__main__":
    main()
