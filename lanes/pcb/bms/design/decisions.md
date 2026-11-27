# BMS board decisions log

| # | Date | Decision | Options (incl. not tried) | Why | Sources |
|---|---|---|---|---|---|
| B1 | 2026-11-27 | Board 95 × 55 mm, 4 layers, top-side assembly | 175 × 90; 150 × 90 (guess, withdrawn); credit card 85.6 × 54 (fits with shared connectors only, 61 % with per-destination) | Real-footprint placement proof, 54 % occupancy | ../../bms-area.md |
| B2 | 2026-11-27 | One connector per destination, J1–J9, Micro-Fit 3.0 | Two shared 2×4s; Mini-Fit Jr (2.8× area) | Point-to-point harnesses, independent service (Chris) | ../../bms-area.md §12–13 |
| B3 | 2026-11-27 | Precharge by 2 series P-FETs, same orientation | G6S relay; back-to-back FETs | Single-fault tolerant forward; smaller; no wear (Chris) | ../../bms-area.md §10 |
