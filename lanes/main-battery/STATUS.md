# main-battery status

Current task: option D CAD delivered (v17, all checks pass); verifying it and relaying it to Chris.
Blockers: Chris: pick the harness vendor (NextPCB ≈ $495 vs Loombotic ≈ $2,245) and OK ordering Molex 39-01-3103/39-28-1103 for the shunt test-fit. Zep (NextPCB): sponsorship reply.
Next step: re-run checks to verify, regenerate harness drawings with CAD lengths, then wait for Chris on vendor, test-fit, fan spacer and look change (F 8 mm).
Last result: v17 CAD pushed: 0 interferences, + to − 12.5 mm, pack-to-chassis 7.3 mm, assembly PASS, box 19.2 L (−24 %), SCS ≈ $1,823; cooling UPS case 15–21 K still open.

## Teammates
- cad-tower17: finished (v17 pushed), shutdown requested.
- main-battery-shunt-connector: finished and shut down.

- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
