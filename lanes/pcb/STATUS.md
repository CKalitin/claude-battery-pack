# pcb status

Current task: BMS board phase 1, part selection and datasheet audits (BQ76952 + ESP32 by me; support parts by teammate `pcb-bms-part-audits`)
Blockers: none hard. Chris: sign off `lanes/pcb/bms/design/intent.md` (phase 0) before the schematic starts. main-battery: shunt pigtail test-fit (J2 Micro-Fit 2×4 vs Mini-Fit Jr 2×5)
Next step: teammate round 2 (latching relay, USB-C, LED switch and buffer, J3 1×4, J2 Mini-Fit Jr option, self-test senses); then the phase 1 gate with a pcb-review-parts reviewer
Last result: round 1 of the support-part audits committed (11 audits, 45 datasheets). Key findings: GV14 FETs must be 100 V (Sensata forbids an external coil diode); charger relay needs no flyback (clamping FET). IMD resistance doubled for sleep current

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
