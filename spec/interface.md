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
| Contactor | Gigavac GV141BAX (GV14), coil 12 V, 3.9 A pick-up ⚠️, 0.23 A hold (2.8 W) | contactor-mounting.md |
| Shunt | Tesla 1016792-00-C, low side; board ground at node A | tesla-shunt.md |

## 2. Converters (D39, 2026-11-27)
| Item | Value | Ref |
|---|---|---|
| Charger | MEAN WELL **NPB-360-12TB**: 20 A, CV set to 14.2 V by VR, 2-stage by DIP. **No remote, no CAN** | converters.md |
| Charger stop | **Normally-open DC relay in the charger + lead**, coil driven by the BMS; closed only after the GV14 is closed. Part ⚠️ TBD (catalog, chassis-mounted, ≥ 20 A DC, rated for closing onto the charger's output capacitors) | D39 |
| Inverter | MEAN WELL **NTS-400P-112**: 400 W, 120 V 60 Hz, power-saving DIP SW4 on; remote off = dry contact on CN301 (relay or PhotoMOS) | NTS-400P-SPEC 2026-03-26 |
| Inverter fan | 40 × 40 × 20, 10 CFM, on the inverter's own CN100 (not a BMS output) | cooling.md, converters.md |
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
- Tesla shunt SPI (TXU0104, 5 V supply);
- GV14 coil driver, enabled by ESP32 **AND** BQ in hardware;
- precharge relay + 10 Ω / 10 W between the B+ and LOAD+ taps;
- inverter remote off;
- charger-relay coil driver;
- 2 A fused pack tap → 5 V buck → 3.3 V, SHUTDOWN ≈ 7 µA, UV latch;
- IMD divider;
- lid button and LED-board link.

No power current on the board. The CAN transceiver and the pack-fan header are dropped.

| Item | Value | Ref |
|---|---|---|
| Size | **150 × 90 × 1.6 mm** ⚠️ estimate (no schematic yet) | spec/requests/pcb-bms-space-claim.md (accepted 2026-11-27) |
| Position | x −105…45, y −15…75, flat over the inverter | same |
| Height | Top parts ≤ 12 mm incl. mated plugs; no bottom parts; THT tails ≤ 2.5 mm | same |
| Mounting | 4 × M3, 5 mm in from the edges, on **3 mm standoffs** on a **G10 .125 bridge** (SCS) spanning the inverter. The bridge stands on 4 M3 posts on deck 2 beyond the inverter's ends (x −109, +105; y −12, +72). Board underside z 317.5, parts top z 331.1, 1.9 mm under the lid. Nothing touches the NTS-400P | converter_packing.py (0 issues) |
| Plug room | 25 mm beyond the −x edge, and beyond the −y edge for x −105…−62 | pcb claim |
| Antenna | U.FL coax from the WROOM-1U to a flex antenna behind the clear acrylic light-pipe slot in the front plate, as in v16; ≈ 150–200 mm coax ⚠️. The lid and shell are aluminium, so a PCB antenna under the lid won't radiate | signal-wiring.md |
| Taps | B+ = in-bar after the main fuse, before the GV14; LOAD+ = 2151 inverter-fuse stud. 18 AWG, 2 A ATM inline fuse at each copper end | signal-wiring.md §3b–3d |
