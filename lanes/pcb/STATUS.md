# pcb status

- Current task: none. BMS area estimate for `main-battery` delivered (2026-11-27). No schematic or layout started.
- Last result: `lanes/pcb/bms-area.md`, `spec/requests/pcb-bms-space-claim.md`: 150 × 90 mm, top parts ≤ 12 mm ⚠️.
- Blockers / waiting on: Chris for design work; `main-battery` to freeze the claim and provide the standoff support. `spec/interface.md` not written yet.
- Next step: wait for instructions.
- Key decisions so far (with reasons):
  - 150 × 90 mm: ≈ 7110 mm² of courtyards is 53 % fill; 120 × 90 is tight with no schematic.
  - ≤ 12 mm tall: a mated right-angle Micro-Fit is ≈ 10 mm; 15 mm is available under the lid.
  - Plugs on the −x edge and rear of the −y edge: clear of MRBF lift-out columns, SB175 and mains.
  - `pcb` edits only its PCB work; shared numbers go through `spec/requests/`.
