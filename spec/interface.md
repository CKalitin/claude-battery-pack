# Interface spec: shared numbers (owner: main-battery)

Single source of truth for numbers that more than one lane uses. Only `main-battery` edits this file. Others file `spec/requests/<lane>-<name>.md` and message `main-battery`. ⚠️ marks unconfirmed values. Started 2026-11-27 from v16.3 + D39 (option D).

## 1. Pack
| Item | Value | Ref |
|---|---|---|
| Cells | 8 × EVE LF105, **4S2P**, 12.8 V nominal, 210 Ah, 2.69 kWh | cells.md |
| Voltage window | 10.0–14.6 V; charge CV **14.2 V**, 2-stage, charge inhibit < 2 ℃ | v14-baseline |
| UV ladder (per cell) | 2.90 firmware off → 2.80 BQ UV → 2.75 inverter off (firmware, via remote) → 2.60 BQ SHUTDOWN | v14-baseline |
| DC out | SB175 on the lid, **175 A** continuous; hardware 500 A / 30 s, firmware-limited to EVE rev E Tables 12–13 | D37 |
| Main fuse | MRBF 250 A in Blue Sea 5191 | power-train.md |
| Branch fuses | MRBF on Blue Sea 2151: inverter **50 A**, charger **30 A** | converters.md §4 |
| Contactor | Gigavac GV141BAX (GV14): round body Ø59.9, 55.7 to the stud seat, M8 studs 26.7 apart; coil 12 V, 3.9 A pick-up ⚠️, 0.23 A hold (2.8 W) | Sensata GV14 datasheet; converters.md §4b |
| Shunt | Tesla 1016792-00-C, low side; board ground at node A | tesla-shunt.md |

## 2. Converters (D39, 2026-11-27)
| Item | Value | Ref |
|---|---|---|
| Charger | MEAN WELL **NPB-360-12TB**: 20 A, CV set to 14.2 V by VR, 2-stage by DIP. **No remote, no CAN** | converters.md |
| Charger stop | **TE V23134-B1052-C642** N.O. relay (Mini ISO F4, bracket, 12 V 90 Ω coil, 1.6–2.4 W, operate 7.2 V) in the charger + lead, next to the charger TB. BMS drives the coil (low side + flyback diode); closes only after the GV14 is closed and AC is present; opens on cold (< 2 ℃), full, fault, or box air over the thermostat limit (cooling decision pending) | converters.md §4a |
| Inverter | MEAN WELL **NTS-400P-112**: 400 W, 120 V 60 Hz, power-saving DIP SW4 on; remote off = dry contact on CN301 (relay or PhotoMOS) | NTS-400P-SPEC 2026-03-26 |
| Inverter fan | Sunon MF40201VX-1000U-G99, 40 × 40 × 20, 10.8 CFM, intake at the rear wall 5 cm from the DC end, on the inverter's own CN100 (not a BMS output) | converters.md §4 |
| Pack fan | **none** (NF-A14 dropped) ⚠️ pending the cooling re-run | converters.md §4 |

## 3. Envelope
| Item | Value | Ref |
|---|---|---|
| Footprint for everything above the cells | **x ±156, y ±79** (module incl. end plates, 312 × 158) | owner-req §3 |
| Lid inside | **z 333** (can tops z 201.85) | converters.md §3 |
| Deck 1 / deck 2 tops | z 221.6 / 276.3 | converter_packing.py |
| Power-bay strip | y −79…−20, the full length, open to the lid (fuse lift-out) | converters.md §3 |

## 4. BMS board (pcb lane)
**Scope (Chris, 2026-11-27):**
- BQ76952: 5 flex taps, 6 NTCs, balancing, protection;
- ESP32-S3-WROOM-1U (18 × 19.2 mm ⚠️) with Wi-Fi;
- Tesla shunt SPI (**TXU0304**: 3 out + 1 in, TI SCES935A; was TXU0104, corrected by pcb 2026-11-27; 5 V supply);
- GV14 coil driver, enabled by ESP32 **AND** BQ in hardware;
- precharge switch = **2 P-MOSFETs in series, same orientation** (either one alone blocks B+ → LOAD+; the body diodes can pass LOAD+ → B+ through the 10 Ω, < ≈ 1 A, only with a welded charger relay and the GV14 open: accepted), replacing the G6S relay (Chris to pcb, 2026-11-27) + **Vishay AC05 10 Ω 5 W cemented wirewound (AC05000001009JAC00), axial, through-hole on the BMS board, no heatsink** between the B+ and LOAD+ taps (power-train.md §9);
- inverter remote off;
- charger-relay coil driver;
- 2 A fused pack tap → 5 V buck → 3.3 V, SHUTDOWN ≈ 7 µA, UV latch;
- IMD divider;
- lid button and LED-board link;
- **AC-present sense**: one wire from the charger side of the charger relay to a divider into an ESP32 ADC (the NPB-360 has no AC-OK signal);
- **box-air NTC** on an ESP32 ADC (all BQ76952 thermistor pins are used), for the charge-pause thermostat.

No power current on the board. The CAN transceiver and the pack-fan header are dropped.

| Item | Value | Ref |
|---|---|---|
| Size | **95 × 55 × 1.6 mm, 4 layers, FINAL** (credit-card target dropped by Chris 2026-11-27), proven by pcb with real footprints (109 parts, 0 overlaps, 49 % occupancy). Chris rejected 150 × 90 | spec/requests/pcb-bms-space-claim.md rev 2026-11-27 (accepted) |
| Position | x −105…−10, y −15…40, flat over the inverter | same |
| Height | Top parts ≤ 12 mm incl. mated plugs; no bottom parts; THT tails ≤ 2.5 mm | same |
| Mounting | 4 × M3, 5 mm in from the edges, on **3 mm standoffs** on a **G10 .125 bridge** (SCS) spanning the inverter. The bridge stands on 4 M3 posts on deck 2 beyond the inverter's ends (x −109 / +105; y −14 / −12 / +40); the bridge is 220 × 58 mm. The −x post screw heads stay below the board top (z 319.1): they sit inside the board's −x plug room (pcb, 2026-11-27). Board underside z 317.5, parts top z 331.1, 1.9 mm under the lid. Nothing touches the NTS-400P | converter_packing.py (0 issues) |
| Plug room | 25 mm beyond the −x edge, the +x edge (x −10…15, z 318–333: confirmed free), the −y edge for x −105…−84, and the **+y edge (y 40…65, x −105…−10, z 318–333: confirmed free)** | pcb claim; converter_packing.py 0 issues |
| Connectors | **One per destination** (Chris, 2026-11-27): −x J1 flex FPC, J2 shunt 2×4; −y J3 power **1×4** (B+, LOAD+, GND, CHASSIS); +x J4 GV14 coil 1×2, J5 LED 1×3; +y J6 charger relay 1×3 (86, 85, AC_SENSE), J7 CN301 1×2, J8 button 1×2, J9 box NTC 1×2. Micro-Fit 3.0, 43650 right-angle on the board, 43645 on the cables. Pins are proposals until the schematic | pcb bms-area.md §13; docs/harnesses.md |
| Antenna | U.FL coax from the WROOM-1U to a flex antenna behind the clear acrylic light-pipe slot in the front plate, as in v16; ≈ 150–200 mm coax ⚠️. The lid and shell are aluminium, so a PCB antenna under the lid won't radiate | signal-wiring.md |
| Taps | B+ = in-bar after the main fuse, before the GV14; LOAD+ = 2151 inverter-fuse stud. 18 AWG. **B+ fuse 5 A ATM** (was 2 A: the GV14's 3.9 A, 75 ms pick-up is 195 % of a 2 A fuse; 5 A still protects 18 AWG). LOAD+ fuse 2 A ATM (precharge peak 1.46 A) | signal-wiring.md §3b–3d; pcb 2026-11-27 |
| IMD chassis reference | The BMS board sits on the G10 bridge, so no mounting hole reaches chassis metal. Instead, one 22 AWG lead from J3-4 to an M4 ring under a rear-plate screw (top-row +y corner ⚠️, tower17 sets it). Replaces v16's plated mounting hole (Chris OK'd, 2026-11-27) | harnesses.md H2b |
