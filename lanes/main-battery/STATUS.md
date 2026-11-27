# main-battery status

Current task: option D follow-ups. The CAD subagent (cad-tower17) is building tower17; harness vendor and shunt connector are being settled.
Blockers: Chris: pick the harness vendor (NextPCB ≈ $495 vs Loombotic ≈ $2,245) and OK ordering Molex 39-01-3103/39-28-1103 for the shunt test-fit. Zep (NextPCB): sponsorship reply.
Next step: review the CAD subagent's result when it finishes (tower17, checks, measured harness lengths, renders), relay it to Chris, then shut the subagent down.
Last result: CAD subagent interim: option D model passes (0 interferences, + to − 12.5 mm, pack copper to chassis 7.3 mm, assembly check PASS); harness docs updated with pcb connector audit.

## Teammates
- cad-tower17 (CAD, started on Sonnet before Chris's Opus rule): model passes checks; now doing renders, cooling, BOM, docs.
- main-battery-shunt-connector: finished and shut down.

- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
