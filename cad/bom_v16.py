"""v16 BOM cost estimate (USD). Catalog prices dated 2026-11-25 unless noted. SCS flat parts are from a live SCS guest
cart (2026-11-25, $1,661.45 for 20 lines, free shipping, ships Dec 4); bent parts are scaled from the v5 quote. Writes docs/v16-bom.md."""
LIVE = "live SCS guest cart 2026-11-25"
scs = [  # part, qty, each, basis, conf
    ("body_half_A (5052 .063, 12 bends, gloss red; DXF flat from flats15)", 1, 157.85 + 8.0, "live SCS guest quote 2026-11-27: $157.85 with bends + powder; +$8 est. for 8 M4 taps + 2 M3 nuts", "⚠️"),
    ("body_half_B (5052 .063, 10 bends, gloss red)", 1, 153.35 + 6.0, "live SCS guest quote 2026-11-27: $153.35; +$6 est. taps/nuts", "⚠️"),
    ("lid (5052 .063, 6 bends, gloss red)", 1, 121.28 + 10.0, "live SCS guest quote 2026-11-27: $121.28; +$10 est. for 8 M3 clinch nuts", "⚠️"),
    ("plate_front (6061 .125, hole grid; v16.3 was .187)", 1, 266.17 * 232.39 / 300.24, "scaled from the .187 live price by the rear plate's live .125/.187 ratio", "⚠️"),
    ("plate_rear (6061 .125, full hole grid; v16.3 was .187)", 1, 232.39, "live SCS guest quote 2026-11-27 (.187 was $300.24)", "✓"),
    ("module_endplate (6061 .313, both identical since v16.3)", 2, 53.43, "live SCS guest quote 2026-11-27, qty-2 price; tapping not added", "✓"),
    ("g10_floor (G10 .187)", 1, 97.15, LIVE, "✓"),
    ("g10_frame (G10 .187)", 1, 95.70, LIVE, "✓"),
    ("tray1 (G10, design .125 → quoted .187)", 1, 92.85, LIVE + "; .125 out of stock", "⚠️"),
    ("tray2 (G10, design .125 → quoted .187)", 1, 86.89, LIVE + "; .125 out of stock", "⚠️"),
    ("g10_plate (G10, design .125 → quoted .187)", 1, 33.36, LIVE + "; .125 out of stock", "⚠️"),
    ("g10_sb_cheek (G10, design .125 → quoted .187)", 2, 9.23, LIVE, "⚠️"),
    ("mylar_top (Mylar .010; v16.3, was G10)", 1, 19.16, "live SCS guest quote 2026-11-27", "✓"),
    ("mylar_spacers (Mylar .010; v16.3, was G10)", 9, 4.57, "live SCS guest quote 2026-11-27, qty 9", "✓"),
    ("bus_A/B/C (Cu .125, 140 x 25)", 3, 25.47, LIVE, "✓"),
    ("bus_pack_pos (Cu .125, 74.6 x 80.3 flat, 2 bends; v16.2)", 1, 46.98, LIVE + "; v16.1 .187 flat price kept, re-quote bent", "⚠️"),
    ("bus_pack_neg (Cu .125, 229.6 x 76.8 flat, 2 bends; v16.2)", 1, 89.47, LIVE + "; v16.1 .187 flat price kept, re-quote bent", "⚠️"),
    ("bus_mod_in (Cu .125)", 1, 8.95, LIVE, "✓"),
    ("bus_mod_load (Cu .125, deburr)", 1, 34.29, LIVE, "✓"),
    ("bus_mod_neg (Cu .125)", 1, 9.53, LIVE, "✓"),
    ("strap_main (Cu .125, 122 x 19 flat)", 1, 21.63, LIVE + "; 2 bends not priced", "⚠️"),
    ("diffuser_f (white acrylic .118)", 1, 48.86, LIVE, "✓"),
    ("pipe_f (acrylic .118)", 1, 2.00, LIVE, "✓"),
]
cat = [  # item, qty, each, source (dated), conf
    ("EVE LF105 cell", 8, 37.50, "18650batterystore US, 2026-11-24 (cells.md)", "✓"),
    ("MEAN WELL NPB-450-12 charger", 1, 130.00, "Digi-Key EU €121–123 ex VAT (NFC variant), 2026-11-25; US price not pulled", "⚠️"),
    ("MEAN WELL NTS-400P-112 inverter", 1, 116.25, "ichome.com qty 1, 2026-11-25 (Digi-Key ES €87.67 ex VAT)", "⚠️"),
    ("Gigavac GV141BAX contactor", 1, 111.07, "2026-11-24 (contactor-mounting.md)", "✓"),
    ("Anderson SB175 housing + 2 busbar contacts", 1, 26.00, "housing ~$6–10 + contacts, not priced individually", "⚠️"),
    ("Blue Sea 2151 dual MRBF block", 1, 46.99, "Defender, 2026-11-24", "✓"),
    ("Blue Sea 5191 MRBF block", 1, 31.99, "Defender, 2026-11-25", "✓"),
    ("MRBF fuses 250 A (5189), 30 A (5175), 50 A (5177)", 3, 22.08, "Fisheries Supply, 2026-11-25", "✓"),
    ("Noctua NF-A14 5V", 1, 30.95, "Newegg.ca, 2026-11-25 (CAD listing, treated as USD: conservative)", "⚠️"),
    ("Tesla shunt 1016792-00-C", 1, 0.00, "already owned", "✓"),
    ("L-com ACPWRC-C13LR right-angle C13", 1, 28.09, "l-com.com, 2026-11-25", "✓"),
    ("Lid NEMA 5-15 outlet + IEC C14 inlet + push-button", 1, 30.00, "not priced", "⚠️"),
    ("Anderson PP45 1327 + 1327G6 + 2 contacts (inverter mate)", 1, 6.00, "not priced", "⚠️"),
    ("90° lugs (6/8/10 AWG packs) + 1/0 lugs", 1, 30.00, "Del City 929605 $2.55 ea (min 5); MAX 5950 8 AWG $14.29/50", "⚠️"),
    ("Wire: 8 + 10 AWG fine-strand, AC 16 AWG, heat shrink", 1, 35.00, "not priced", "⚠️"),
    ("Inline ATM fuse holder, Eaton Bussmann ATM-FHID (B+, LOAD+)", 2, 9.49, "Zoro G1285042, 2026-11-25", "✓"),
    ("Signal harness: Micro-Fit/Mini-Fit/JST/DF11 housings + pins, rings, 105 C wire, U.FL coax, ATM fuses (docs/signal-wiring.md)", 1, 40.00, "mostly not priced", "⚠️"),
    ("Fasteners: carriage bolts M8/M10, nuts, washers, M3/M4 screws, rods, standoffs, feet", 1, 70.00, "not priced", "⚠️"),
    ("Control PCB, assembled (BQ76952 + ESP32)", 1, 150.00, "README estimate (board not designed)", "⚠️"),
    ("Sense flex PCB", 1, 40.00, "README estimate", "⚠️"),
    ("LED front board", 1, 40.00, "estimate", "⚠️"),
]
other = [("Duty + GST on cells (import to Canada)", 40.00, "README estimate", "⚠️"),
         ("SCS shipping to Canada", 0.0, "not computed", "⚠️")]
L = ["# v16 BOM cost estimate (USD, 2026-11-25)", "",
     "Generated by `cad/bom_v16.py`. ✓ = priced from a dated source; ⚠️ = estimate.",
     "SendCutSend: live guest prices 2026-11-25 (flat parts) and 2026-11-27 (bent shell from DXF flats, Mylar, .125 plates, identical end plates) (cart $1,661.45 for 20 lines, free US shipping, ships Dec 4). Bent body halves and lid are quoted from DXF flats with bend lines (cad/flats15.py): SCS's importer refused the bent STEPs, not the parts.", "",
     "## SendCutSend parts", "| Part | Qty | Each | Total | Basis | |", "|---|---|---|---|---|---|"]
ts = 0
for p, q, e, b, c in scs:
    ts += q * e; L.append(f"| {p} | {q} | {e:.2f} | {q*e:.2f} | {b} | {c} |")
L += [f"| **SCS subtotal** | | | **{ts:.0f}** | | |", "", "## Catalog parts", "| Item | Qty | Each | Total | Source | |", "|---|---|---|---|---|---|"]
tc = 0
for p, q, e, s, c in cat:
    tc += q * e; L.append(f"| {p} | {q} | {e:.2f} | {q*e:.2f} | {s} | {c} |")
L += [f"| **Catalog subtotal** | | | **{tc:.0f}** | | |", "", "## Other", "| Item | Total | Source | |", "|---|---|---|---|"]
to = 0
for p, e, s, c in other:
    to += e; L.append(f"| {p} | {e:.2f} | {s} | {c} |")
tot = ts + tc + to
L += ["", f"## Total ≈ **${tot:,.0f}** (SCS {ts:,.0f} = {100*ts/tot:.0f} %, catalog {tc:,.0f}, other {to:,.0f})", "",
      "## Findings from the live SCS pass",
      "- ⚠️ **SCS has G10 .063 and .125 out of stock** (only .187 / .250 / .375 / .500). tray1, tray2, g10_plate, cheeks, g10_top and the 9 spacers were quoted at .187. That changes the stack heights (+1.6 mm per .125 part, +3.1 mm per .063 part; +28 mm over the 9 spacers) and must be resolved before ordering.",
      "- **v16.3 budget: SCS must stay under the $2,000 sponsorship.** Levers taken: Mylar top + spacers ($470 → $60), identical end plates ($163 → $107), .125 front/rear plates ($566 → ≈ $438). Still unpriced: taps/PEM on the shell (estimated in), bends on the two pack busbars and the Z-strap ⚠️.",
      f"- **End plates:** ${2*266.17:.0f} for the two hole-grid plates ({100*2*266.17/tot:.0f} % of the pack). v5 found 5052 .125 about 33 % cheaper than 6061 .187.",
      "- **bus_pack_pos / bus_pack_neg are bend-legal 1/8 in Zs since v16.2** (v16-decisions D28). The prices are still the v16.1 .187 flat quotes ⚠️: re-quote as bent COP-125.",
      "- Bending, tapping and powder coat on the flat parts were not added; the bent-part prices include them from v5.",
      ]
open("docs/v16-bom.md", "w").write("\n".join(L) + "\n")
print(f"SCS {ts:.0f}  catalog {tc:.0f}  other {to:.0f}  total {tot:.0f}")
