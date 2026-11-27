# pcb status

- Current task: none; waiting for Chris (BMS design to start). Done today: BMS size proof; general PCB skills.
- Last result: BMS area proven at **95 × 55 mm** (109 real KiCad footprints, 0 overlaps, 49 % occupancy): `lanes/pcb/bms-area.md`, `lanes/pcb/bms-size/` (courtyards.py, place.py, render). Revised claim: `spec/requests/pcb-bms-space-claim.md`. KiCad 10.0.8 installed (PPA). Default model set to Opus 5.5 high in `~/.claude/settings.json` (Chris).
- Skills: `lanes/pcb/skills/` (pcb-design, pcb-review; README lists sources and licences), symlinked into `~/.claude/skills/`. Vendored Diode663 `schlib.py` (MIT), smoke-tested on KiCad 10.0.8.
- main-battery accepted 95 × 55 (spec/interface.md §4), added the AC-present sense and box-air NTC (ESP32 ADC), moved the B+ tap to a 5 A ATM, and corrected TXU0304.
- Blockers / waiting on: Chris: DigiKey/Mouser API keys, OK for review subagents, kicad-happy install (`toolchain.md`).
- Next step: on go — BMS phase 0 intent + phase 1 part audits (evaluate BQ76942 vs BQ76952 per main-battery's docs/afe.md note; P-FET precharge as an option).
- Key decisions so far (with reasons):
  - **Precharge = 2 series P-MOSFETs, same orientation** (Chris 2026-11-27): either one blocks B+ → LOAD+ (single-fault tolerant); the reverse body-diode path is accepted.
  - **95 × 55 final, credit card dropped; one connector per destination, J1–J9** (Chris 2026-11-27).
  - Reference schematic: Chris's UBC Solar **HVC rev 1.0** (A365 `E_BMS_HVC`); style captured in `skills/pcb-design/references/owner-style-chris.md` (style only, no UBC Solar content).
  - 95 × 55 mm: courtyards 2,421 mm² from real footprints; 49 % occupancy sits in the 40–60 % "4-layer comfortable" band.
  - 150 × 90 withdrawn: built on guessed allowances 3× too high (trap T1 in bms-area.md).
  - Plugs on the −x and +x edges and the rear of the −y edge.
  - BMS fab: PCBWay full PCBA, **or possibly NextPCB** (Chris, 2026-11-27, not final). Design to both fabs' common rules; MPN-based BOM works at both.
