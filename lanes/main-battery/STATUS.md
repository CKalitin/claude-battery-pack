# main-battery status

Current task: v16 facet look: variants B and D built, checked and rendered (facet_compare.jpg); waiting on Chris to pick.
Blockers: Chris: pick facet method B (8 mm taller) or D (same height, notched end plates; recommended); shunt harness end Micro-Fit 3.0 or Mini-Fit Jr; send the Docan quote draft? Zep (NextPCB): sponsorship + harness reply.
Next step: make the chosen variant the v17 default, re-run all checks, BOM/flats, update spec + decisions.
Last result: B and D: 0 interferences, clearance PASS; B 414.6 mm tall overall, D 406.6 (same as now). Docan quote email drafted.

## Teammates
- cad-tower17: finished (v17 pushed), shutdown requested.
- main-battery-shunt-connector: finished and shut down.

- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
