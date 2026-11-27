# Request (pcb → main-battery): BMS board space claim, revised 2026-11-27 — FINAL (Chris, 2026-11-27)

**Replaces 150 × 90 mm with 95 × 55 mm.** Chris rejected 150 × 90. The new size is proven by placing every real footprint: 109 parts, 0 overlaps, 49 % occupancy. Details: `lanes/pcb/bms-area.md`.

- Board 95 × 55 × 1.6 mm, 4 layers. Keep the −x edge at x −105 and the −y edge at y −15 → x −105…−10, y −15…40.
- Top side ≤ 12 mm including mated plugs; bottom side no parts; THT tails ≤ 2.5 mm (unchanged).
- 4 × M3, 5 mm in from the edges; one plated (IMD chassis reference). Still 3 mm standoffs on the G10 bridge, which can shrink to suit.
- Right-angle plug room, 25 mm beyond:
  - the −x edge (shunt, sense flex);
  - the +x edge, now at x −10 over the inverter (outputs, lid/LED link) ⚠️ please confirm it's free;
  - the −y edge for x −105…−84 (power taps).

- **Final** (Chris, 2026-11-27): keep 95 × 55 reserved. The credit-card target was dropped (Chris, 2026-11-27); the board is 95 × 55.
- Connector edges (Chris approved one connector per destination, 2026-11-27): −x J1 flex, J2 shunt; −y J3 power; +x J4 GV14, J5 LED; **+y** J6 charger relay + AC_SENSE, J7 CN301, J8 button, J9 box NTC. 25 mm of plug room beyond each (the +y room confirmed free by main-battery).
