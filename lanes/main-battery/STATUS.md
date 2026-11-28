# main-battery status

Current task: cell shipping time to the Blaine, WA parcel depot (Chris); v17 fan flush done.
Blockers: Chris: facet option A–D (facet_options.png); shunt harness end Micro-Fit 3.0 (as J2) or Mini-Fit Jr. Zep (NextPCB): sponsorship + harness reply.
Next step: read vendor shipping policies / transit to Blaine 98230, update cells.md §4–5.
Last result: fan flat on rear plate, checks PASS (cfc1fc2); new shunt harness: cut 200 mm (route 142).

## Teammates
- cad-tower17: finished (v17 pushed), shutdown requested.
- main-battery-shunt-connector: finished and shut down.

- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
