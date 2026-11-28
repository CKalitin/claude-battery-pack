# main-battery status

Current task: v17 follow-ups: fan moved flat onto the rear plate (Chris), facet options diagram sent, re-running checks.
Blockers: Chris: pick the shell facet option A–D (versions/v17-option-d/renders/facet_options.png). Zep (NextPCB): sponsorship + harness reply (vendor choice waits on it).
Next step: confirm checks pass with the flush fan, commit, then the cooling hole-spacing iteration (agreed open item).
Last result: decisions recorded: fan flush on rear plate (D41a), no Molex order (UBC Solar has housings), harness vendor waits for Zep; @loombotic on X: 11 posts since Jun 2025.

## Teammates
- cad-tower17: finished (v17 pushed), shutdown requested.
- main-battery-shunt-connector: finished and shut down.

- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
  - **D39: option D picked (NPB-360-12TB + NTS-400P-112 + 40 mm fan), no USB-C** (Chris 2026-11-27). Charger stop = NPB-360 + N.O. DC relay. BMS scope confirmed (owner-req §5).
