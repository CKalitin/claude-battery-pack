# main-battery status

- **Current task (Chris, 2026-11-27):** reopen the charger/inverter search so that everything above the cells fits in the module footprint (≈ 312 × 158 mm incl. end plates). Brief: `docs/handoff-converters.md`. Deliver `docs/converters.md`, a top-view packing figure per serious candidate, and a recommendation. No CAD until Chris picks.
- **Last result:** `docs/converters.md` written; packing checker `cad/analysis/converter_packing.py`; figures `versions/v16-c1-power-module/renders/conv_{A_multiplus,B_npb450_nts400p,S_stack_top_bay,D_npb360_nts400p}.png`.
  - Recommendation **D: NPB-360-12TB (20 A) + NTS-400P-112 + its 40 mm fan**, bay strip on −y, BMS over the inverter. 0 issues, lid z 333 (+15 mm vs v16.3), ≈ 17.6 L vs 25.2 L.
  - Combined unit: none fits (MultiPlus 12/500/20 only upright, lid ≈ 590). RPB-1600 rejected: 338 mm with its DC tabs.
  - Root cause: the NPB-450's 135 mm width (bay strip needs ≥ 59 mm → converters ≤ 96 wide).
- **Blockers / waiting on:** pcb lane for a BMS board area estimate (scope confirmed by Chris).
- **Next step:** spec/interface.md (shared numbers incl. BMS scope and space claim), then CAD `tower17.py` for option D.
- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
