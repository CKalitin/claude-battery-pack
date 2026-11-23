# Version history

Each folder holds the renders for one design iteration. Its source is `cad/towerN.py` (v5 onward), `cad/tower.py` / `tower2.py` (v2–v4), or `cad/packmodel.py` (v1).

| Version | Cells | What changed | Why it moved on |
|---|---|---|---|
| v01-pack-concept | — | First concept: shoebox shell, MJF carrier, separate BMS + power PCBs | Replaced by the Tower A form |
| v02-v03-tower | — | Tower A: U-body, end plates with handles, lid | Iterated on details |
| v04-tower-pem | — | PEM hardware, exploded views, module detail | Not all parts could be made at SendCutSend |
| v05-scs-lf100 | LF100MA 4S | Every part SendCutSend-makeable: 3×30° bends instead of radii, two L-halves, button heads; DXFs + quote | Too fat |
| v06-cells-on-edge | 4S | Cells on edge to narrow the box (W 180) | Busbars ended up on the side; busbars belong on top |
| v07-lf105-4s | LF105 4S1P | Switched to LF105, upright, busbars on top | Baseline for the compact layout |
| v08-compact-4s | LF105 4S1P | Module moved forward; control board stands in front of the cells; charger + inverter stacked on two decks | Wanted the inverter to move |
| v09-inverter-front-bay | LF105 4S1P | Inverter stands beside the board in the front bay; one deck; 279 mm tall | Decided to increase capacity |
| v10-8s-inverter-front-bay | LF105 8S1P | 8 cells in series, 24 V gear | Wanted converters on top, not at the side |
| v11-8s-single-deck | LF105 8S1P | Charger + inverter end to end on one deck | Wanted them stacked as in v8 |
| v12-8s-stacked-board-on-deck | LF105 8S1P | Inverter stacked on the charger; control board flat on deck 1; Z-straps rise to the board | **Current** |
