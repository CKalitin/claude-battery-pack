# Area budget: size a board from real footprints

**Never quote a board size from per-block guesses.** Guesses pad every block "to be safe" and the padding compounds. On the 2026 BMS board, guesses gave 7,110 mm²; real footprints gave 2,421 mm², and the board went from 150 × 90 to 95 × 55 mm.

## Method
1. **Sizing BOM.** One line per function, each with a real catalog part and its exact KiCad footprint. Include everything that takes area:
   - every passive, at its intended size;
   - connectors at their real series and orientation;
   - mounting holes with the washer or standoff keep-out;
   - test points, programming pads (Tag-Connect needs no part), fiducials if the fab asks;
   - THT parts lying flat at their formed lead pitch.

   Mark functions with no part ("tied to VSS: no part") so the reader sees they were considered.
2. **Courtyards from the library**, never by hand: `scripts/courtyards.py` reads each footprint's `F.CrtYd` bounding box (IPC-7351 courtyard) and prints a table by block. Copy it and replace its `BOM` list for a new board.
3. **Occupancy bands** (courtyards ÷ board area):

   | Occupancy | Verdict | Means |
   |---|---|---|
   | < 40 % | relaxed | 2-layer may work; probably too big |
   | 40–60 % | normal | 4-layer comfortable: **aim here** |
   | 60–75 % | dense | 4-layer, zone floorplan, mostly 0402, more effort |
   | > 75 % | too dense | remove parts, change packages, grow the board, or go double-sided |

   *(Band values: studio-edul/pcb-layout-skill, MIT. Rule of thumb ⚠️.)* Above 70 %, propose part changes before growing the board: smaller connectors, pads instead of headers, a MOSFET instead of a relay, no optional LEDs.
4. **Placement proof.** Load every footprint into a `pcbnew.BOARD` and place it:
   - connectors on their edges with mating faces out;
   - holes at the agreed positions;
   - each block packed into its region.

   Fail on any courtyard overlap, any part outside the outline, or any part not placed. Try the candidate sizes, keep the smallest that passes in the 40–60 % band, and report the one below it that failed and why. Render it (`kicad-cli pcb render`) and look at it. Reference implementation: `lanes/pcb/bms-size/place.py` in the battery-pack repo.
5. **Edges and heights.** The connectors' total width along their allowed edges is often the real limit, not the area. Check part heights, mated plug included, against the envelope.
6. **Write it up** (requirements, candidate sizes with numbers, traps, open items) and hand the claim to whoever owns the mechanical envelope.

## What the proof is not
It's an area proof, not a layout: shelf-packed passives are not at their pins. Say so in its caption. Re-run it when the real BOM replaces the sizing BOM after the schematic.

## Typical courtyards (KiCad 10.0.8 libraries)
| Footprint | Courtyard [mm] | Area [mm²] |
|---|---|---|
| R/C 0402 | 1.86 × 0.94 | 1.7 |
| R/C 0603 | 2.96 × 1.46 | 4.3 |
| C 0805 / 1206 | 3.40 × 1.96 / 4.60 × 2.30 | 6.7 / 10.6 |
| SOT-23 / SOT-23-5 / SOT-89 / SOT-223 | 3.86 × 3.40 / — / 5.10 × 5.04 / 8.80 × 7.24 | 13 / — / 26 / 64 |
| SMA diode | 7.01 × 3.50 | 25 |
| TQFP-48 7×7 | 10.30 × 10.30 | 106 |
| ESP32-S3-WROOM-1U | 19.50 × 20.15 | 393 |
| Micro-Fit 3.0 right-angle 1×3 / 2×3 / 2×4 | 13.7 × 10.9 / 14.2 × 13.7 / 17.2 × 13.7 | 149 / 194 / 235 |
| FPC 12-pin 0.5 mm (Hirose FH12) | 12.1 × 7.9 | 96 |
| M3 hole with pad | 6.4 × 6.4 | 41 |
| Axial power resistor L20 lying flat, P25.4 | 28.3 × 6.9 | 195 |

Connectors and modules dominate small control boards: 36 % and 18 % of the BMS board.
