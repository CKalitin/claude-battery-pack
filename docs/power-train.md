# Power train: fuse, contactor, shunt, conductors, DC output

**Status 2026-11-24:** v14 power train rejected by the owner (unassemblable, 1 mm clearance to the tray). Three concepts (A, B, C) drafted as diagrams; **no CAD yet, awaiting owner decision.** ⚠️ marks unconfirmed values.

---

## 1. Requirements (first principles), each with its source

### Electrical function
| # | Requirement | Source |
|---|---|---|
| E1 | Carry 210 A continuous, 500 A for 30 s (DC out) | Review D2 ⚠️ cell burst rating unconfirmed (cells.md T4) |
| E2 | Every load and the charger pass through one fuse, one disconnect and one shunt | Protection + coulomb counting |
| E3 | Branch protection for the 6 AWG converter leads (inverter 50 A, charger 30 A) | Wire ampacity |
| E4 | Few series bolted joints (each ≈ 10–30 µΩ ⚠️, ≈ 2.5–7.5 W at 500 A) | Heat, failure points |
| E5 | Precharge before closing onto the inverter's input capacitors | Contactor contact life |

### Protection and failure
| # | Requirement | Source |
|---|---|---|
| P1 | Main fuse as close to the cell as possible: unfused copper is an unprotected fault zone | First principles |
| P2 | Fuse interrupt rating ≥ prospective short-circuit current (5.0–6.9 kA) | Review C2 |
| P3 | Disconnect opens on loss of control power (fail-safe) and on BQ76952 fault independent of firmware | Review M4 |
| P4 | Disconnect hold power small vs. pack self-discharge | EV200 1.66 W = 40 Wh/day = 1.5 %/day |
| P5 | A service disconnect: one part removed = output dead. Install it last, remove it first | Assembly safety |

### Clearance and shorts
| # | Requirement | Source |
|---|---|---|
| C1 | Separate + and − by distance, not by insulation. Plastic is a second barrier, never the first | Owner, 2026-11-24 |
| C2 | No pack conductor passes through a closed hole in chassis metal | Owner (v14 tray slots) |
| C3 | Nothing at pack potential mounts to chassis metal; pack floats (IMD sees the first fault) | N §2 |
| C4 | No single chassis part can touch both + and − copper (that turns two faults into one) | v14 trap T1 |
| C5 | Clearance > the tolerance stack, with margin. 1 mm is less than the stack of 7 cell thicknesses + spacers + bends | v14 trap T2 |
| C6 | Exposed + and − farther apart than a dropped tool can bridge, or shrouded | Assembly safety |

Note on arcing: at ≤ 14.6 V a 1 mm air gap cannot break down (Paschen minimum ≈ 330 V in air). The v14 risk is **mechanical contact** (tolerance, vibration, a burr, chipped powder coat), giving a bolted short of ≈ 6 kA. Arcing matters only when a high current is interrupted.

### Assembly and service
| # | Requirement | Source |
|---|---|---|
| A1 | Top-down assembly: every part drops in vertically, nothing is threaded through a hole | Owner |
| A2 | Every bolt reachable from above with a straight socket after the parts around it are in | Owner |
| A3 | Rigid copper only between points on the same rigid body. Between bodies (module ↔ deck ↔ lid): flexible cable | Over-constraint |
| A4 | Lid removable without unbolting the power path (service loop) | Service |
| A5 | Supplier-made parts only: SendCutSend copper/G10, catalog fuses/contactors, cables crimped to length by a vendor | Owner |
| A6 | Torque on output studs reacted by a plate, never by the M4 cell poles (2 N·m) | Cell terminal strength |

### Measurement and controls
| # | Requirement | Source |
|---|---|---|
| M1 | Tesla shunt in pack−, all load current through it, board ground at node A | tesla-shunt.md, D3 |
| M2 | Short signal harnesses; board gets coil, precharge, shunt SPI, fuse/contactor NTC | — |

## 2. Requirements questioned

| Requirement | What it costs | Question for the owner |
|---|---|---|
| **500 A DC out** (D2) | Class T fuse, EV200, COP-250 risers, M10 studs, boots, G10 plates. Rests on a reseller "3C / 30 s" figure ⚠️ | What actually draws 500 A? (jump-start?) At ≤ 215 A total: MRBF main fuse (10 kA at 14 V), 1/0 cable, Anderson SB175 |
| **DC studs on the lid** | Copper must climb past both converter decks | Keep, or accept a connector? |
| **EV200** | 1.66 W hold (1.5 %/day), needs precharge | Blue Sea ML-RBS 7713: 13 mA when on (0.17 W), auto-release (fail-open), manual LOCKED-OFF knob = service disconnect; but 0.94 kg vs 0.43 kg ⚠️ size |
| **Cell count / config** | — | No change. The lever is current, not cells; 8S1P would halve it but D1 fixed 12 V |

## 3. Candidates

| | v14 (rejected) | A: one bay on the module | B: two bays, poles apart | C: B, downsized to 175 A |
|---|---|---|---|---|
| Idea | Both poles converge in the front bay on tray 1 | Same bay, but mounted to the module on G10; − returns as a cable | Rear bay holds only − (shunt), front bay only + (fuse, contactor); converters in the middle | B with MRBF main fuse and one Anderson SB175 |
| + to − separation | 10 mm (risers), through one Al tray | ≈ 75 mm | **≈ 290 mm** | in one shrouded connector |
| Pass-throughs of chassis metal | 2 tray + 2 lid | 0 | 0 | 0 |
| Module ↔ lid link | Rigid COP-250 | Cable | Cable | Cable |
| Series joints after the cells | 8 | 7 | 6 | 6 |
| Cost | — | Long − cable along the cells | Charger moves ≈ 44 mm forward; rear service bay shrinks ⚠️ check converter connector ends | Gives up the 500 A spec |

## 4. Traps found in v14
| # | Trap | Rule now |
|---|---|---|
| T1 | Both risers in slots of the same Al tray, 10 mm apart, 1 mm clearance: one tray shift = + to − short through the tray | C2, C4 |
| T2 | 1 mm clearance set below the tolerance stack | C5 |
| T3 | Z-strap flanges wider than the slots; the cell screws under the tray can't be reached after the tray is in → unassemblable. The interference check passed because touching-with-1-mm is not an interference | A1, A2. Add an assembly-sequence check and a min-clearance check between opposite potentials and chassis |
| T4 | pack− dragged 300 mm to sit next to pack+, 10 mm from busbar B, 7 mm under an Al tray with only Mylar | C1, C3 |
| T5 | Rigid risers from a tray-mounted contactor through the lid: over-constrained | A3 |
| T6 | Root cause: the original "one PCB for all contactors and shunt" requirement fixed the location; deleting it didn't move the parts | Re-derive layout when a requirement is deleted |

## 5. Sources
- TE EV200 datasheet (catalog 5-1773450-5): 0.13 A hold at 12 V, 1.7 W, M8 studs ✓
- Blue Sea 7713 product page: 500 A continuous, 13 mA on, auto-release, 0.94 kg, 3/8" studs ✓
- Blue Sea / Eaton MRBF: 30–300 A, 10 kA at 14 VDC ✓; must use a terminal fuse block, ring ≥ 3/8" ✓
- Anderson SB175: 175 A, wire up to 1/0 ✓; panel/flange mounting part ⚠️ not yet found
- Cable heating, adiabatic, 500 A for 30 s: 2/0 (67.4 mm²) ΔT = 8.2 K; 1/0 (53.5 mm²) 13.1 K

## 6. Open items
- Owner decisions: 500 A or not; A/B/C; EV200 vs ML-RBS.
- ⚠️ Converter connector ends (B moves the charger forward).
- ⚠️ ML-RBS outline drawing; Anderson SB175 panel mount.
- Add coded checks to `run_tower14.py`: min clearance between opposite-potential copper and to chassis; assembly order.
