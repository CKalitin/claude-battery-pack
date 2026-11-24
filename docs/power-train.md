# Power train: fuse, contactor, shunt, conductors, DC output

**Status 2026-11-24 (11:40):** v14 power train rejected. **Owner baselined 175 A DC out (SB175).** Owner prefers busbars to cables for assembly effort. Concept D in CAD as **v15** (`versions/v15-concept-d/`). ⚠️ marks unconfirmed values.

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

## 7. Update 2026-11-24: 175 A baselined → Concept D

### Owner inputs
- DC out **175 A** (Anderson SB175). 500 A dropped.
- **Busbars preferred over cables** (assembly effort).
- The control PCB must have a defined zone (v14 left it floating in the middle of the power copper).
- Converter cable runs must be supported.

### Why D replaces B
- The SB175 brings + and − together at one shrouded connector anyway, so B's 290 mm pole separation buys little.
- B needed 3 long cables: SB175 −, inverter −, charger −. D needs one long rigid − bar, with both ends on the module.

### Concept D
| Item | D |
|---|---|
| Decks | Tray 1 → G10 .187, ends at the charger (x ≈ 50). The front bay floor is a G10 power deck on the module. No metal plate over any pack copper. |
| − path | P1 collector → COP-187 bar, 20 mm wide, along the −y cell-top edge (y −60…−80: 14 mm to busbar B, 13 mm to the wall) → rises in the bay → shunt node A; node B → − bus → SB175 − contact + converter − stud |
| + path | P4 collector extended to a tab at the front end (x 147–152), rising at the bay centre → MRBF 250 A (5191 block) → contactor line stud; load stud → + bus → SB175 + contact + dual MRBF 2151 (inverter 50 A, charger 30 A) |
| Polarity zoning | Bay −y half = − (shunt, − bus); +y half = + (contactor, MRBFs). ≥ 25 mm between opposite potentials everywhere ⚠️ verify in CAD |
| Output | SB175 mounted on a G10 bracket on the power deck with Anderson 924 bracket kit; busbar contacts bolted to the + and − buses; the face pokes through a lid opening. **No cables in the main path. Lid carries no power copper.** |
| Control PCB | Vertical, on the −y body wall beside the charger: x −150…+45, z 230–312 (≈ 195 × 82 mm, 3.3× v14's 68 × 72 mm). ≥ 20 mm above the − bar; + hardware ≥ 100 mm away. Short runs: flex tail (−y taps), shunt SPI, charger CAN and inverter remote (DC ends face front), fan (rear), LED board and antenna (front). ⚠️ mounting: PEM standoffs in the body wall vs a G10 bracket, depends on body assembly order |
| Converters | **Both DC ends face the front bay** (checked: the NPB-450 and NTS-400P each have DC and AC on opposite ends). Leads ≤ 150 mm, tied through slots cut in the G10 decks (no added parts). Inverter: Anderson PP75 (1327/1327G6) on the unit, so it unplugs. Charger: screw terminal block. AC ends face the rear: charger IEC C14 inlet + fan; inverter CN500 |
| Joints after the cells | 7 |

### MEAN WELL connector check (datasheet photos, 2026-11-24)
| Unit | DC end | Other end | Source |
|---|---|---|---|
| NPB-450-12 | "DC output side": screw terminal block V+/V−, DIP switch, LEDs, DF11-14 signal connector | "AC input side": IEC 320-C14 inlet, on/off switch, fan | MEAN WELL NPB-450-SPEC (2023) p.1 photos ✓ |
| NTS-400P-112 | "DC input side": TB1 Anderson 1327 (red) / 1327G6 (black), contact 261G2-LPBK; CN301 remote on/off | "AC output side": CN500 JST B6P-VH, DIP switch, CN50 TX/RX | NTS-400P-SPEC (2026-03-26) p.1 photos ✓ |

### Main fuse: Class T vs MRBF (prices checked 2026-11-24, USD)
| | Class T (JJN / JLLN) | MRBF + 5191 block |
|---|---|---|
| Price at 200–250 A | JLLN-200 $40 (Zoro), JJN-200 $88–145 | fuse ≈ $22 + block ≈ $27–32 |
| Price at 500 A | JJN-500 $185 (Zoro) to $445 | not available (max 300 A) |
| Interrupt rating | 20 kA at 160 VDC | 10 kA at 14 VDC (5 kA at 32 V) vs 6.5–6.9 kA prospective: 1.45× margin ⚠️ pack max 14.6 V is just above the 14 V rating point |
| Current limiting | Yes: clears in under ½ cycle, low let-through I²t (protects contactor contacts from welding) | Not marketed as current-limiting ⚠️ |
| Mounting | Bolted blades: needs 2 bars + 2 joints | Stacks on a 3/8" stud; ring ≥ 3/8"; must use the terminal block |
| Size | JJN-200: 0.88" × 2.44" | ≈ 25 × 25 × 13 mm |
- **Choice for 175 A: MRBF 250 A.** Max discharge = 175 A out + ≈ 40 A inverter = 215 A. Cheaper by ~$15–120, one bar and one joint fewer, adequate AIC. What you give up is current limiting.

### Contactor on both poles?
No. Two-pole switching is for HV packs (> 60 V DC), where a stuck pole must not leave a lethal touch voltage. At ≤ 14.6 V the pack is SELV, and it floats, so opening + alone breaks every load loop. A second contactor would add a part, a coil, precharge logic and a failure mode, to protect against a single welded contact. That case is covered by the fuse plus the charger and inverter remote-off.

## 8. Control PCB placement: merged into the front LED PCB (proposed 2026-11-24)

| Option | Result |
|---|---|
| Vertical board on the −y wall (§7) | Works, but it's a separate PCB, needs mounting that depends on body assembly order, and needs a harness to the LED board and antenna |
| **Integrated into the front LED PCB** | **Recommended.** One PCB fewer, no LED harness, antenna already at the front light pipe. LED/air-hole side faces out; control components on the back |
| Mezzanine slotted onto the LED PCB | Rejected: the gap from the LED board's back face to the module front end plate is **8.0 mm** (`XL0` − end-plate face in `tower14.py`). A stacked board plus board-to-board connector needs ≈ 15–18 mm ⚠️, so the front plate would move forward ≈ 10 mm (dead length) |

- Board: 187 × 246 mm (±93.4 mm wide, z ≈ 36–282).
- Control zone on the back, z 40–190: in front of the aluminium module end plate, away from the bay copper (bay starts at z 218). That is ≈ 187 × 150 mm vs v14's 68 × 72 mm.
- Back-side height limit: 8.0 mm minus clearance → components ≤ 5 mm ⚠️. ESP32-S3-WROOM-1U is 3.2 mm thick ⚠️ (check the datasheet). Harness connectors must be low-profile right-angle at the board's top edge.
- Air holes: the checkerboard has Ø6 holes on a 7.78 mm pitch. Routing the BQ76952 + ESP32 cluster between them is impractical, so a solid zone of ≈ 60 × 80 mm loses ≈ 40 of ≈ 287 air holes (≈ −14 % inlet area) ⚠️. Re-run the cooling check (N §11).
- Board ground = pack−. Mounting holes into the end-plate standoffs are non-plated, with a ≥ 2 mm copper keep-out (floating pack, IMD).
- Harness lengths: flex tail over the end-plate top into an FPC connector on the back (≈ 40 mm); shunt SPI ≈ 80 mm; contactor coil ≈ 100 mm; converter CAN/remote ≈ 150 mm; fan (rear) ≈ 350 mm; lid button ≈ 150 mm.

## 9. v15 CAD (2026-11-24): what changed from the §7 concept
- **Contactor → Gigavac GX12** (225 A continuous, M10 studs, dual-coil economizer, $125 at Waytek ⚠️ outline not fetched). The EV200 (81 × 66) left no room for the SB175 and both fuses. The M10 studs also take Blue Sea MRBF blocks directly.
- **Shunt stands vertical**, bolted to the − riser tab with horizontal bolts. That lets the riser stand outside the tray outline, so the tray can be lowered after it (the v14 Z-flange trap).
- **+ tab flange sits in a tray notch open to the front edge**, for the same reason.
- **Control circuit on the front PCB's back, facing the bay** (owner, 2026-11-24), not facing the module end plate. The bay side has ≥ 18 mm depth, versus 8 mm in front of the end plate.
- Measured: + to − ≥ 13.7 mm; pack to chassis ≥ 7.4 mm; 0 pass-throughs (`clearance_v15.py`).
