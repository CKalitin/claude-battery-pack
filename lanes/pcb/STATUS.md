# pcb status

Current task: BMS phase 1 gate: fixing the independent review's findings (1 blocker, 5 major, 14 minor); teammate `pcb-bms-review-fixes` updating the audits
Blockers: none hard. Chris: sign off `lanes/pcb/bms/design/intent.md` (phase 0) before the schematic starts. main-battery: shunt pigtail test-fit (J2 Micro-Fit 2×4 vs Mini-Fit Jr 2×5)
Next step: review the teammate's fixes, a short re-review, close the phase 1 gate, then the schematic (after Chris signs off intent.md)
Last result: review in (gates/phase1-review.md). Decided B8–B12: hardware charge stop via BQ DCHG, mandatory OTP at bring-up, precharge hardware time limit, BQ MISO buffer, REG0 per TI FAQ. ESP32 pin plan done (31 of 33 pins)

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
