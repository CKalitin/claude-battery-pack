# pcb status

Current task: BMS phase 1 gate PASSED; no schematic exists yet (Chris asked for a PDF export), it starts on his intent sign-off
Blockers: Chris: sign off lanes/pcb/bms/design/intent.md (BMS requirements) so the schematic can start
Next step: after sign-off, phase 3 schematic (hierarchical, wired, Chris's HVC style) with schlib + a pcb-review-schematic reviewer
Last result: phase 1 closed (gates/phase1.md) after two independent reviews. The re-check's R1 blocker is fixed: the BQ setting that would have stopped DDSG/DCHG ever enabling the contactor and charger relay

## Notes
- Project: `lanes/pcb/bms/` (design/intent.md, parts/, datasheets/, decisions.md). Size proof: `lanes/pcb/bms-area.md`. Skills: `lanes/pcb/skills/` (pcb-design, pcb-review), linked into `~/.claude/skills/`. kicad-happy v3.0.2 is the second reviewer.
- DigiKey API key at `~/.config/pcb-secrets/digikey.env` (mode 600, outside the repo). API stock numbers stay out of the repo (DigiKey terms).
- Key decisions (Chris, 2026-11-27):
  - board 95 × 55 mm final;
  - one connector per destination J1–J10;
  - precharge by 2 series P-FETs, same orientation;
  - firmware self-test instead of per-output LEDs;
  - USB-C for flashing;
  - zero-holding-current inverter remote (latching relay);
  - BMS fab PCBWay, or possibly NextPCB;
  - HVC rev 1.0 is the schematic style reference.
