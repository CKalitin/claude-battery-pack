# pcb status

- Current task: toolchain proposal for the coming BMS board design (`lanes/pcb/toolchain.md`). BMS area estimate for `main-battery` delivered (2026-11-27). No schematic or layout started.
- Last result: `lanes/pcb/bms-area.md`, `spec/requests/pcb-bms-space-claim.md`: 150 × 90 mm, top parts ≤ 12 mm ⚠️. Accepted in `spec/interface.md` §4 (`aa40b9f`): 3 mm standoffs on a G10 bridge, parts top 1.9 mm under the lid.
- Blockers / waiting on: Chris: toolchain go-ahead, reference schematic, DigiKey/Mouser API keys, review-subagent permission.
- Next step: wait for instructions. Precharge resistor is now the AC05 (5 W), see `bms-area.md`.
- Key decisions so far (with reasons):
  - 150 × 90 mm: ≈ 7110 mm² of courtyards is 53 % fill; 120 × 90 is tight with no schematic.
  - ≤ 12 mm tall: a mated right-angle Micro-Fit is ≈ 10 mm; 15 mm is available under the lid.
  - Plugs on the −x edge and rear of the −y edge: clear of MRBF lift-out columns, SB175 and mains.
  - `pcb` edits only its PCB work; shared numbers go through `spec/requests/`.
