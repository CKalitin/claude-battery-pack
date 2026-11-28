# main-battery status

Current task: v16 facet look (F 15) per Chris: building variants B (8 mm deeper) and D (notched end plates), checks + exterior renders.
Blockers: Chris: shunt harness end Micro-Fit 3.0 (as J2) or Mini-Fit Jr; cell order route (Docan quote for 8?). Zep (NextPCB): sponsorship + harness reply.
Next step: send B/D renders + check results; Chris picks B or D; then make it the v17 default.
Last result: cells: no US reseller has 8 in stock today; Docan Houston ~1-1.5 wk to Blaine (min 16, quote for 8); Full Battery 3 in stock (cells.md 4a).

## Teammates
- cad-tower17: finished (v17 pushed), shutdown requested.
- main-battery-shunt-connector: finished and shut down.

- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
