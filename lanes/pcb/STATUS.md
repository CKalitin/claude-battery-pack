# pcb status

Current task: BMS phase 1 gate: independent parts review (`pcb-review-parts`) running on 15 audits
Blockers: none hard. Chris: sign off `lanes/pcb/bms/design/intent.md` (phase 0) before the schematic starts. main-battery: shunt pigtail test-fit (J2 Micro-Fit 2×4 vs Mini-Fit Jr 2×5)
Next step: fix the review findings, close the phase 1 gate, then the schematic (after Chris signs off intent.md)
Last result: all part audits committed (619abc4): latching relay KEMET EE2 for the inverter remote (zero holding current), USB-C via a TPS2116 mux to 3V3 only, LED eFuse TPS259530, digital self-test senses, J3 1×4. Teammate pcb-bms-part-audits shut down

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
