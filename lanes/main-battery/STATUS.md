# main-battery status

- **Current task (Chris, 2026-11-27):** reopen the charger/inverter search so that everything above the cells fits in the module footprint (≈ 312 × 158 mm incl. end plates). Brief: `docs/handoff-converters.md`. Deliver `docs/converters.md`, a top-view packing figure per serious candidate, and a recommendation. No CAD until Chris picks.
- **Last result (2026-11-27):** option D follow-ups done and pushed.
  - Cooling: `cad/analysis/cooling_D.py`, converters.md §4. The 40 mm fan gets only 5.4 CFM through the Ø4.8 grid; with Ø6.5 holes 7.7 CFM. The UPS case is ≈ 15 K mixed; single loads 7–9 K.
  - Charger relay: TE V23134-B1052-C642 (§4a).
  - GV14 and NTS connector dims confirmed (§4b).
  - BMS 95 × 55 accepted (spec §4).
  - Budget: `docs/budget.md`, ≈ $2,930, SCS ≈ $1,580.
  - New docs: `docs/afe.md`, `docs/enclosure.md`.
- **Blockers / waiting on:** Chris: go for CAD (cooling and fan-hole spacing deferred to after the CAD, his call). pcb: proving sizes. Zep's (NextPCB) reply.
- **Next step:** CAD `tower17.py` once Chris says go.
- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
