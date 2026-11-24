# v14 design review: whole-pack audit before CAD

**Scope:** every v13 subsystem (`cad/tower13.py`, `docs/control-board-electrical.md`, `docs/v14-design-notes.md`), checked against datasheets fetched on 2026-11-24 and recomputed with first-principles calculations.

**Verdict:**
- The mechanical architecture of the module, enclosure and decks is sound.
- v13 is **not buildable as drawn**. It has 7 critical findings, mostly in the power path, thermal and RF, where the CAD held placeholders.
- All of them have concrete fixes below. After these, v14 should be close to final, pending 3 owner decisions.

Severity:
- **C (critical):** breaks function or safety.
- **M (major):** must be designed before ordering.
- **m (minor):** spec or documentation.

---

## 0. Decisions for Chris (they block the v14 CAD)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | Pack configuration | (a) 8S1P fixed · (b) 4S2P fixed · (c) keep dual-mode 8S / 1S8P | **(a) 8S1P fixed**, unless there is a concrete load above 300 A. Dual-mode needs voltage matching at every swap and wears the M4 terminals (§C3). It also adds the parallel kit, INA228, Kelvin taps, J1 ID pin and buck-boost. 4S2P gives up per-cell monitoring (§v14-notes 7). |
| D2 | Anderson DC-out rating | 30 A (fused on the PCB) · 50 A (fused on copper) · high-current stud | **30 A on an SB50**: 770 W at 25.6 V, enough for tools and accessories. It lets every branch live on the PCB (§M1). |
| D3 | Tesla shunt vs a plain shunt into the BQ76952 | keep Tesla module · $10 busbar shunt on the BQ76952 coulomb counter | **Keep the Tesla shunt** (owner's want, and it showcases the project), with the costs stated: 5 V rail, level shifter, SPI port, orientation test. A plain shunt would remove 3 board parts and one risk. |

## 1. Critical findings

### C1. Power current enters the PCB at the strap bolts
- **What:** the v13 Z-straps end in M6 flanges bolted *to the control board* (`strap_pts`). The earlier open item "rework so the Z-straps bolt to the contactor and shunt, not to PCB pads" was never done. 315 A through PCB pads violates the design rule "power current never flows through PCB copper".
- **Fix:** the straps land directly on the power components, and the board only carries sense and drive.
  - **pack+:** strap → **Class T fuse** (bolted blade, §C2) → **contactor** stud A. Contactor stud B → load bus.
  - **pack−:** strap → **Tesla shunt** node A. Node B → load-negative bus.
  - Both straps rise through board cutouts, or the power parts sit beside the board on tray 1.
  - Re-check the SendCutSend COP-125 rules on the new strap shapes: min flange 12.0 mm, min joggle 12.9 mm.

### C2. No main fuse is specified; the placeholder is too small
- **Why Class T:** prospective short-circuit current for 8S1P is $I_{sc} = N_s V_{oc} / R_\text{loop}$.
  - $N_s = 8$
  - $V_{oc}$ = 3.3 V per cell
  - $R_\text{loop}$ = 5.26 mΩ, including 0.5 mΩ contactor, 0.1 mΩ shunt and 0.2 mΩ fuse

  That gives **$I_{sc}$ = 5.0 kA**, and **6.9 kA** with new cells at 0.32 mΩ.
  - MRBF terminal fuses are rated for only 5 kA at 32 VDC (Eaton figures, as quoted on DIY Solar Forum), so they're too low. ✗
  - Class T is rated **20 kA at 160 VDC**. ✓
- **Selection: Bussmann JJN-300** (or Littelfuse JLLN-300 / Mersen A3T300).
  - Size: 1.00" dia × 2.75" (25 × 70 mm), bolted blades.
  - It sits 5 % above the 315 A burst, so bursts never stress the element. A very-fast Class T sized at 200 A would be at 158 % during every 30 s burst.
  - The fuse is there for **short circuits only**. The firmware's I²t limit and the BQ76952 handle overload.
- **Coordination:**
  - The contactor's short-circuit withstand is 8 kA for ≤ 5 ms with no smoke or ignition (Panasonic). Class T is current-limiting and clears 5–7 kA faults in well under one cycle. ✓
  - The EV-B datasheet says nothing about polarity. ✓
- **Mount:** bolted directly between the pack+ strap and the contactor stud, with no holder. Best part is no part. Add a G10 saddle for mechanical support. The 34 × 30 × 25 mm CAD placeholder is replaced by 25 × 70 mm plus blades.

### C3. Cell terminal thread: stock LF105 is M4 × 6 mm, not M6
- EVE spec rev B: the poles have M4 internal threads with 6 mm effective depth.
- NKON lists "terminal type M4". Only some resellers weld on M6 studs.
- The CAD assumes M6 with 8 mm engagement. On stock cells that bottoms out and leaves the busbar unclamped.
- **Fix:**
  - Keep the 6.6 mm busbar holes (they clear M6 and M4 alike).
  - Screw: **M4 × 8 A2 flange-head + 0.8 mm washer**, giving 4.0 mm engagement (5.7 threads). Torque about 2 N·m. DIY reports of stripped M6 threads at 6–7 N·m suggest ≤ 4 N·m even for M6 in these aluminium poles.
  - Re-check the joint: clamp force at M4 / 2 N·m is about 2.5 kN; the contact is pad-on-bar over Ø18 mm. ✓ for 315 A.
  - Confirm the thread on the first delivered cell. It's a physical check; the vendor listing doesn't say.

### C4. The enclosure has no air inlet
- The diffuser and LED board (`_front_panel`) cover the **whole** front grid (z 36 → 285 mm). The rear grid has 703 holes around the fan.
- Result: the fan recirculates air through rear holes centimetres from itself, and nothing flows over the board or the converters. The 80 W budget (inverter 40 W at 91 % per the MEAN WELL datasheet, charger about 29 W, board) has no exhaust path.
- **Fix, with no new parts:**
  1. Shrink the diffuser and LED board to the **module zone** (z ≲ 210). Move the "WE WILL WIN" text into that band.
  2. Leave the front holes **above z = 215 open** as the intake. That's 9 rows × 21 = 189 holes = 3,420 mm², facing the board and both converters.
  3. On the rear plate, **delete the holes in the deck zone outside the fan circle**, so the fan can only draw air through the box.
- **Check:** the intake is 24 % of the fan's swept area (14,100 mm²). Expect about 50 % of free-air flow, ≈ 35–60 m³/h. At 80 W:

  $$\Delta T = \frac{P}{\rho c_p Q} = \frac{80}{1.2 \times 1005 \times 35/3600} = 6.8\ \text{K}$$
  - $P$ = heat [W]
  - $\rho$ = air density [kg/m³]
  - $c_p$ = specific heat of air [J/(kg·K)]
  - $Q$ = airflow [m³/s]

  ✓. If the measured ΔT exceeds 15 K, open 3 more rows.
- Both converters have their own fans (MEAN WELL lists a 10 CFM fan on the NTS-400P, and a fan on the NPB-450). Point their intakes toward the board side in the CAD.

### C5. Wi-Fi inside a closed aluminium box
- At 2.44 GHz, λ = 123 mm (λ/2 = 61 mm). Each Ø4.8 mm hole through 4.75 mm plate is a waveguide far below cutoff ($f_c$ ≈ 37 GHz).
- Estimated attenuation of the grid: $SE \approx 20\log(\lambda/2d) - 10\log n + 32\,t/d$ = 22 − 28 + 32 ≈ **26 dB**. The lid and body are solid.
- R7 (Wi-Fi debug) is at risk.
- **Fix:** use the **ESP32-S3-WROOM-1U** (U.FL version, same 18 × 19.2 mm footprint) plus a 2.4 GHz adhesive flex antenna behind the **light-pipe slot**. The 187 × 3.2 mm slot is about 3 × λ/2, so it radiates well. One small part.
- Fallback with no part: put the PCB antenna directly under the NEMA outlet's plastic body. That's unpredictable, so not recommended.

### C6. The contactor is modelled 2× too small and mounted on the PCB
- **Real AEVB9251 (Panasonic):**
  - Outline about 84.5 × 62.5 × 56.5 mm including the mounting flange.
  - 2 × Ø6 mounting holes at 70.5 mm (M5, 3–4 N·m).
  - Main terminals M6 (6–8 N·m), 360 g.
- **CAD:** 42 × 45 × 45 mm, sitting on the PCB.
- **Fix:**
  - Mount the body **through a board cutout onto tray 1** with 2 × M5, so the 360 g goes to the chassis. The contactor body is plastic, so isolation is OK.
  - Coil wires go to the board.
  - Height: 56.5 mm against **87.3 mm** of clearance from the board top to the lid. ✓
  - Keep it clear of the Anderson body (bottom at z 281): the contactor top lands at about z 284 if it sits under the connectors, so keep its x-range out of x ≥ 133 mm.

### C7. No precharge, so the contactor would weld closing onto the inverter's capacitors
- The inverter's input capacitance is unpublished. Design for ≤ 4.7 mF.
- **Fix:** a 10 Ω / 10 W wirewound resistor plus a small 12 V relay in parallel with the contactor.
  - 3RC = **0.14 s** to 95 %.
  - Peak current 2.9 A.
  - Energy in the resistor ½CV² = **2.0 J**.
- Close the contactor only when the BQ76952 PACK pin reads ≥ 95 % of the stack voltage. Time out after 0.5 s and report a fault, which flags a short on the load bus.

## 2. Major findings

| # | Finding | Fix | Check |
|---|---|---|---|
| M1 | Branch circuits are unprotected. The 300 A main fuse doesn't protect 10–12 AWG branch wire. | Branches on the **PCB with ATO fuse holders**: inverter 25 A, charger 20 A, Anderson 30 A (D2). The board becomes the distribution panel. Relax the copper rule to "≤ 30 A per branch on 2 oz with wide pours". | Inverter draws 20 A typical (MEAN WELL). 30 A pour: ≈ 12 mm at 2 oz outer for ~20 K rise (IPC-2152; size in layout). |
| M2 | Standby drain and no on/off control. | One **illuminated momentary push-button** (lid) and a state machine: OFF (≈ 50 µA) → ON. The inverter's **power-saving DIP (SW4)** cuts no-load draw from 10 W to 1.3 W. Inverter **remote off** through a PhotoMOS on its dry contact. Wake on the charger's +12 V aux when AC is plugged in (one divider, no part). | ON-idle: 6 W coil + 1.3 W + 0.4 W = 7.7 W → **13.8 days**; without saving mode 16.4 W → 6.5 days. OFF: about 240 years, so self-discharge dominates. |
| M3 | No low-temperature charge inhibit. The LF105 can charge only from 0 to 55 °C. | ESP32 ↔ NPB-450 over **CANbus 2.0B** (on the non-NFC model): output on/off, curve, internal temperature. One SN65HVD230 transceiver. Also wire the NPB **Remote ON-OFF** (pin 7 to +12Vaux pin 8). Inhibit below 2 °C cell temperature. | Gives a second, independent overcharge path if the contactor ever welds. |
| M4 | Protection depends on firmware. | Contactor driver enable = ESP32 GPIO **AND** BQ76952 DDSG/DCHG status, in hardware. | A BQ fault opens the contactor even with the ESP32 hung. |
| M5 | Board power over-specified for dual-mode. | With D1 = 8S: drop the buck-boost. Use one buck, 20–29.2 V → 12 V / 1 A (coil 0.5 A, fan, NPB logic), then a 5 V LDO or buck (Tesla shunt) and 3.3 V (ESP32). | Coil range 10–16 V with ≤ 5 % ripple (Panasonic): run it from the regulated 12 V. No PWM economizer: Panasonic gives no hold-voltage data. |
| M6 | Inverter isolation via nylon posts: creep and drop-load concern. | **Make deck 2 from G10** (SendCutSend G10BLACK-125, in stock). The aluminium posts stay. The inverter bolts to an insulating plate: no creep, no added part, and G10's flexural strength is about 8× nylon's. Supersedes v14-notes §3. | M3 × 4 inverter screws: 3.2 mm G10 + 0.8 mm → keep screw penetration ≤ 2.5 mm. Use M3 × 6 (6 − 3.2 = 2.8 mm; trim with a washer to ≤ 2.5). |
| M7 | No earth bond. | Bond inlet PE and outlet ground to the body with a ring lug under an existing front-plate M4 screw. No new part. | Chassis earthed while charging (the NPB FG is isolated from its output); the IMD keeps working. |
| M8 | The lid is tethered by 4 connectors' wiring. | Use 150 mm service loops. FASTON tabs on the inlet and outlet, ring lugs on the Anderson. Write down the disconnect order. | Lid removal ≤ 2 min. |
| M9 | The Tesla shunt is a 34 × 18 × 10 mm placeholder, and its bonded end is still unknown. | **Chris measures:** overall length, bolt spacing, bolt size, height, harness exit. Then run the ≥ 5 A bolt-to-bolt test in the repo's probe plan. | Physical part: can't be checked online. |

## 3. Minor findings

- **m1. G10 stock is no longer a blocker.** SendCutSend lists G10BLACK in .063, .125, .187, .250 and .375, all in stock. The .063 spacers and top plate are buildable. Close the open item.
- **m2. Busbar joints:** Scotch-Brite plus an oxide inhibitor on bare SendCutSend copper; flange-head screws (no extra washers); paint-mark after torque.
- **m3. Module compression procedure:**
  - Assemble the cells at 30–40 % SOC (the condition for EVE's 36.7 ± 0.5 mm thickness).
  - Tension each rod to 736 N (2.94 kN / 4): M5 torque ≈ $T = KFd$ = 0.2 × 736 × 0.005 = **0.74 N·m**.
  - Re-torque after 1 cycle.
- **m4. Remove the lid M12 CAN port.** CAN is internal now (M3). One fewer connector and lid cutout.
- **m5. Thermistors:** 4 on the flex (cells 1, 3, 6, 8), 1 on the board near the contactor and fuse. Charger temperature comes over CAN. The BQ76952 takes up to 9 thermistor inputs.
- **m6. Charger:**
  - 2-stage mode (DIP1 ON), no float.
  - Boost 28.4 V (3.55 V/cell) set over CAN. The default 28.8 V gives 3.6 V/cell, inside the 3.65 V limit but harder on the cells.
- **m7. Protection thresholds (BQ76952):**

  | Threshold | Value |
  |---|---|
  | Cell overvoltage | 3.65 V |
  | Cell undervoltage | 2.80 V |
  | Discharge overcurrent | 130 A for 60 s |
  | Burst I²t | 315 A for 30 s |
  | Charge temperature | 2–50 °C |
  | Discharge temperature | −20 to 55 °C |

  The inverter's own low-voltage shutdown is 22 V = 2.75 V/cell, which backs up the 2.80 V trip. Its 33 V overvoltage shutdown is above the 29.2 V maximum. ✓
- **m8. Powder coat:** keep coat off tapped holes and clinch nuts, and off the earth-lug face (M7). Specify masking at SendCutSend.

## 4. Checks performed: passing

| Check | Result |
|---|---|
| Charger DC output isolated from FG | O/P-FG 0.5 kVAC, 100 MΩ ✓ |
| Inverter input range vs pack | 20–33 V vs 20–29.2 V ✓ |
| Contactor rating | 250 A continuous vs 105 A; I²t 900² × 20 = 1.6×10⁷ A²s vs 315² × 30 = 3.0×10⁶ A²s ✓ |
| Short-circuit current vs fuse interrupt rating | 5–7 kA vs 20 kA Class T ✓ |
| Cell ratings | 1C continuous, 3C for 30 s discharge, 1C charge; charger 13.5 A = 0.13C ✓ |
| End-plate deflection (FE) | 0.078 mm ✓ (v13) |
| Floor under a 5 g drop | G10 floor carries ≈ 87 % of the bending (EI ratio). σ_G10 ≈ 20 MPa vs ~400 MPa ✓ |
| Handle → plate → wall tabs | 7 × M4 in 1.6 mm 5052. Strip capacity ≈ 1.1 kN per screw vs 55 N at 3 g ✓ |
| Clearance, board top to lid | 87.3 mm vs contactor 56.5 mm ✓ |
| AC inlet current | 4.2 A charger input vs C14 10 A ✓ |
| SendCutSend copper tapping (flex M3) | copper .063–.250" offered ✓ |
| IMD, floating pack, group-R check | v14-notes §2–5 ✓ |

## 5. Requirements re-examined

| Req | Original | Keep or change | Why |
|---|---|---|---|
| R1 | 1 kWh | Changed to 2.69 kWh | Cost per Wh and the sponsorship (v10) |
| R2 | One night of assembly | Keep | Part count stays about 83 + fuse + button + antenna |
| R3 | Supplier-made parts | Keep | Deck 2 moves to G10 (still SendCutSend) |
| R4 | One PCB, BMS slots on top | **One board** (BMS merged) | Two boards would add a board and a connector for no function. Chris to confirm. |
| R5 | 120 V in and out | Keep, plus pass-through | Charger and inverter run together, like a UPS |
| R6 | DC outlet (Anderson?) | **Define rating** (D2) | Unrated, it can't be fused |
| R7 | Wi-Fi debug | Keep, **needs an antenna** (C5) | Metal box |
| R8 | Off-the-shelf AFE | Keep (BQ76952) | — |
| R9 | No email-only parts, no doubtful datasheets | Keep | All parts above have web checkout and full datasheets. The Tesla shunt is salvage. |
| R10 | Busbars on top | Keep | — |
| R11 | Beautiful, Roadster red | Keep | LED panel shrinks to the module zone (C4) |
| **R12 (new)** | Defined OFF state and standby | Add | M2 |
| **R13 (new)** | Charge only from 0 to 55 °C | Add | M3, EVE spec |
| **R14 (new)** | Floating pack with IMD | Add | v14-notes |
| **R15 (new)** | Lid removable in ≤ 2 min | Add | M8 |

## 6. v14 change list

**CAD**
1. Straps land on the fuse and shunt; contactor on tray 1 through a board cutout; real EV-B and JJN-300 envelopes (C1, C2, C6).
2. Terminal screws M4 × 8 (C3).
3. LED panel limited to z ≲ 210, front intake rows open, rear deck-zone holes removed (C4).
4. Antenna behind the light-pipe slot (C5).
5. Deck 2 in G10 .125; inverter screws set for ≤ 2.5 mm penetration (M6).
6. Remove the M12 port; add the lid push-button (m4, M2).
7. Flex: M3 tapped tabs with S-loops (v14-notes §1).
8. Tesla shunt real envelope once measured (M9).

**Schematic**
1. Precharge relay and resistor (C7).
2. ATO branch fuses (M1).
3. PhotoMOS for inverter remote off; CAN transceiver to the NPB (M2, M3).
4. Hardware AND for the contactor enable (M4).
5. Single buck → 12 / 5 / 3.3 V (M5).
6. IMD divider; thermistors; WROOM-1U.

**Docs**
- v13 open items (G10 stock) closed.
- Thresholds table and assembly torque table.

## Sources

| Source | Used for |
|---|---|
| EVE LF105 spec F (batteryjunction) and spec rev B (globalsources) | Thermal limits, ratings, M4 thread |
| NKON LF105 listing | M4 terminal type |
| MEAN WELL NTS-400P and NPB-450 spec sheets | Power, protections, remote control, CANbus, isolation |
| Panasonic EV-B (AEVB9251) product page and datasheet (Mouser) | Contactor ratings, mounting, coil |
| Eaton JJN-300 listings | Class T size and interrupt rating |
| Eaton MRBF ratings, as quoted on DIY Solar Forum | MRBF interrupt rating |
| SendCutSend specs JSON and tapping page | G10 stock, copper tapping |
| Espressif ESP32-S3-WROOM-1/1U datasheet | U.FL module |
