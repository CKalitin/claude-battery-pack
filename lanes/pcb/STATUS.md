# pcb status

- Current task: (1) prove the BMS board size (Chris rejected 150 × 90); (2) build general PCB skills from existing ones.
- Last result: BMS area proven at **95 × 55 mm** (109 real KiCad footprints, 0 overlaps, 49 % occupancy): `lanes/pcb/bms-area.md`, `lanes/pcb/bms-size/` (courtyards.py, place.py, render). Revised claim: `spec/requests/pcb-bms-space-claim.md`. KiCad 10.0.8 installed (PPA). Default model set to Opus 5.5 high in `~/.claude/settings.json` (Chris).
- Blockers / waiting on: main-battery to accept 95 × 55 and confirm +x plug room. Chris: toolchain go-ahead items in `toolchain.md`.
- Next step: general skills in `lanes/pcb/skills/` (pcb-design, pcb-review), linked into `~/.claude/skills/`.
- Key decisions so far (with reasons):
  - 95 × 55 mm: courtyards 2,421 mm² from real footprints; 49 % occupancy sits in the 40–60 % "4-layer comfortable" band.
  - 150 × 90 withdrawn: built on guessed allowances 3× too high (trap T1 in bms-area.md).
  - Plugs on the −x and +x edges and the rear of the −y edge.
  - BMS fab: PCBWay full PCBA (Chris).
