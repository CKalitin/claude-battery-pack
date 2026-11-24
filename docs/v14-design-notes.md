# v14 design notes and justifications

Decisions made after v13, to be built into the v14 CAD and schematic. Each item records the decision, why it was made, and the calculation behind it.

| # | Item | Status |
|---|---|---|
| 1 | Sense flex: M3 tapped hole + S-loop tab per node. 4S2P → 5 taps. **Flex chosen over rigid FR4 (2026-11-24)** | **Baselined** |
| 2 | Pack floats from chassis | **Baselined** |
| 3 | Inverter electrically isolated from chassis | **Baselined**, superseded by the review (§M6): deck 2 becomes G10, not nylon posts |
| 4 | Simple insulation monitor (IMD): asymmetric divider read by the ESP32 | **Baselined** |
| 5 | Per-group resistance check in firmware (detects an open cell) | **Baselined** |
| 6 | Charger current corrected; 4S2P vs 8S1P charge time | Correction |
| 7 | 4S2P: risks of pair-level monitoring and cell matching | Open decision |

---

## 1. Sense flex attachment: M3 tapped hole + S-loop tab

**Decision.** Each series link, plus the pack+ and pack− terminals, gets one M3 tapped hole (9 sense points, VC0–VC8):
- mid-span between the two terminals;
- near the busbar edge on the flex-spine side (y = −21 mm).

SendCutSend taps the holes. Each flex tab ends in a ring pad with an FR4 stiffener and is held by one M3 screw with blue threadlocker. The tab itself is an in-plane zigzag (S-loop) cut into the flex outline.

**Rejected alternatives**

| Option | Why not |
|---|---|
| Solder each tab to its busbar | Needs a hot plate (the bar is 79 mm² of copper, too much heat sink for an iron) and a heating cycle per bar |
| Clamp the tab under the M6 terminal bolt | Zero parts, but the polyimide and adhesive creep under load and drop preload on a joint that carries 315 A |
| Nickel tab + spot weld | Copper doesn't resistance-weld well, and it needs a welder |

**Checks**
- **SendCutSend tapping:** copper is tappable from 0.063" to 0.250"; our bar is 0.125". ✓ (sendcutsend.com/services/tapping)
- **Thread engagement:** M3 pitch is 0.5 mm, so 3.175 mm of copper gives 6.35 threads. The joint carries µA of sense current and essentially no mechanical load. ✓
- **Hole-to-edge distance:** centre ≥ (2.60 mm / 2) + the material minimum from SendCutSend's copper page. Place at 5 mm from the edge and confirm on the SendCutSend material page.
- **Cross-section lost at the hole:** the 2.6 mm tap drill removes 2.6/25 = 10.4 % at one section.

  $$\Delta T_{30s} = \frac{J^2\rho t}{c_v}, \quad J = \frac{315}{(25-2.6)\times 3.175} = 4.43\ \text{A/mm}^2 \Rightarrow \Delta T = 2.9\ \text{K (vs 2.4 K without the hole)}$$
  - $J$ = current density [A/mm²]
  - $\rho$ = 1.72×10⁻⁸ [Ω·m]
  - $t$ = 30 [s]
  - $c_v$ = 3.45×10⁶ [J/(m³·K)]

  The hole is local and the surrounding copper conducts the extra heat away, so this is negligible. ✓
- **Why preload loss doesn't matter here:** the joint carries µA, so even 10 mΩ of contact resistance gives a µV error. ✓
- **S-loop:** cell thickness tolerance accumulates over 8 cells, and swelling plus thermal expansion move the busbars relative to the spine by a few mm. A straight tab fixed at both ends would put that strain into the trace or the screw. The meander flexes like a spring instead. Commercial cell-contact flexes use the same feature. No extra part.

**Part cost:** M3 × 6 mm screws, 5 in 4S2P. Accepted; it beats a hot-plate process.

**Flex vs rigid FR4 (decided 2026-11-24: flex).**
- Rigid FR4 with slotted pads would need a separate harness, 1 cable and 1 connector more, because it can't make the 90° turn up through tray 1.
- Cost difference: JLCPCB flex starts at $2 for 5 boards (≤ 100 × 100 mm). At ~330 × 70 mm with stiffeners, an estimated $20–60 vs $10–25 rigid, so tens of dollars. Owner preference plus no harness decides it.
- MOQ 5, so 4 spares. A swap is about 15 min (5 screws + 1 connector).

**Flex robustness rules:**
- Inside corners R ≥ 1 mm, with copper tear-stops at slit ends and tab roots.
- Tail bend radius ≥ 3 mm (static, once). No vias, pads or pours in the bend; traces perpendicular to the bend line.
- FR4 stiffener behind every ring pad.
- Spine taped down at 2–3 points, clear of busbar edges and screw heads.
- **Fusible necked trace at each tap**, so a damaged flex shorting two taps opens in ms instead of dumping a cell pair into a hair trace.
- A broken trace fails safe: the BQ76952 detects the open wire and the contactor opens.

## 2. Pack floats from chassis

**Decision.** No connection from pack− (or any pack node) to the chassis.

**Why not bond pack− to the chassis.** A fuse only clears a fault whose current flows through it. A short from a busbar between cells to the chassis returns through the bond to pack− without ever passing through the main fuse, so nothing interrupts it. Floating makes the first fault harmless (no current path), as long as it is detected (§4) before a second fault happens.

**Touch safety.** Maximum pack voltage is 29.2 V (8S) or 14.6 V (4S), below the 60 V DC SELV limit, so a single fault to the chassis is not a shock hazard.

## 3. Converter isolation, from the datasheets

**Charger (NPB-450).** MEAN WELL specifies withstand voltages of I/P-O/P 3 kVAC, I/P-FG 2 kVAC and **O/P-FG 0.5 kVAC**, with isolation resistance of 100 MΩ at 500 VDC.
- The DC output is isolated from FG, so the charger can bolt straight to the chassis.
- Its FG terminal earths the chassis through the IEC inlet whenever it is plugged in.
- ✓ No change.

**Inverter (NTS-400P-124).** MEAN WELL specifies DC I/P to AC O/P 3.0 kVAC and AC O/P to FG 1.5 kVAC.
- **No DC I/P to FG rating is given**, and the block diagram doesn't show how −V relates to FG.
- An unlisted rating is not an isolation guarantee. **Assume the DC input is referenced to FG and the case.**

**Decision.** Isolate **deck 2 and the inverter together** from the chassis by making deck 2's 4 hex posts **nylon (PA66), M4, 57.5 mm long, female-female**.
- **Correction:** an earlier note said the inverter sits on 6 mm nylon standoffs. In the CAD it bolts flat to aluminium tray 2 with 4 M3 screws from below. Tray 2 sits on 4 M4 hex posts, which sit on FH-M4 clinch studs in tray 1.
- The steel studs and screws stay metal. Inside each post, the stud reaches 10 mm in and the screw tip 6.4 mm, leaving **41 mm of nylon** between them. Nothing metal bridges to the chassis.
- **Can't be forgotten:** the posts are the only support for the deck, so there is no washer to leave out. Same part count; only the material changes.
- **Strength check** (5 g lateral shock, deck plus inverter about 1.05 kg):
  - Force: 5 × 9.81 × 1.05 = 51.5 N, so 12.9 N per post.
  - Moment at the 57.5 mm length: M = 0.74 N·m.
  - Section modulus, treating the 8 mm hex as Ø8: W = πd³/32 = 50 mm³.
  - Bending stress: σ = 0.74×10³ / 50 = **15 MPa**. Conditioned PA66 is about 50 MPa, so the margin is 3.3×. ✓
  - Nylon creeps, so check post preload once after the first month.
- Tray 2 sits 14 mm from the body walls (y ±79 vs ±93.4) and touches nothing else. ✓
- Do **not** connect the inverter's FG terminal to anything.
- **Inverter screw length:** the datasheet drawing carries a "2.5 mm (Max.)" note. Treat it as a screw-penetration limit. Use **M3 × 4** screws: tray 1.6 mm + 2.4 mm into the case, ≤ 2.5 mm. The CAD currently shows 5 mm of penetration; fix this in v14.
- **Self-check:** if the isolation is ever bypassed, the IMD (§4) reads a hard short at node 0 (r ≈ 0.000) on first power-up and alarms.

This baseline doesn't depend on measuring the unit first. When the inverter arrives, a continuity check from DC− to its case confirms whether the precaution was needed.

**AC outlet grounding.**
- The inverter's AC output is isolated from the DC input (3 kV) and from FG (1.5 kV), so the 120 V outlet floats, like a portable generator.
- The outlet's ground pin bonds to the chassis, which is earthed through the inlet while charging.
- A floating output has no return path through earth, so a GFCI would have nothing to detect. Skip it. MEAN WELL's datasheet mentions no GFCI.
- Re-check this if the outlet is ever tied to building wiring (it won't be).

## 4. IMD: asymmetric divider read by the ESP32

**Goal.** Detect the first cell-to-chassis fault before a second one creates an unfused short.

**Circuit**
- R₊ = 2.2 MΩ from pack+ to chassis.
- R₋ = 900 kΩ + 100 kΩ from chassis to pack−.
- The ESP32 ADC reads across the 100 kΩ, with a 100 nF filter cap.
- Parts: 3 resistors + 1 capacitor.

**Measured quantity.** The ratio $r = V_\text{ch}/V_\text{pack}$:
- $V_\text{ch}$ = chassis voltage relative to pack− [V]
- $V_\text{pack}$ = pack voltage from the BQ76952 [V]

Using a ratio cancels changes in state of charge.

**Healthy value**

$$r_0 = \frac{R_-}{R_+ + R_-} = \frac{1.0}{3.2} = 0.312$$

The cell junctions (nodes) sit at $k/8$ = 0, 0.125, … 1, and none equals 0.312. A symmetric divider (r₀ = 0.5) would sit exactly on node 4, so a short there would be invisible.

**Fault of resistance $R_f$ from node $k$ to the chassis** (nodal analysis, $V_\text{pack} = 1$):

$$r = \frac{1/R_+ + (k/8)/R_f}{1/R_+ + 1/R_- + 1/R_f}$$

| $R_f$ | Ratio at nodes 0 … 8 | Worst-case shift |
|---|---|---|
| 100 Ω (hard short) | 0.000, 0.125, … 1.000: equals k/8 | Identifies the node |
| 100 kΩ | 0.040 … 0.913 | ≥ 0.055 |
| 1 MΩ | 0.185 … 0.593 | ±0.025 at nodes 2 and 3 |
| 10 MΩ | 0.292 … 0.357 | ≈ 0.005, below the threshold |

**Rule:** alarm and open the contactor if |r − 0.312| > 0.02, averaged over 1 s. Averaging handles the AC noise coupled through the charger's output-to-earth filter caps while plugged in. A hard short also reports *which* node.

**Resolution:** 0.02 × 25.6 V = 0.51 V at the chassis, which is 51 mV at the ADC. The ESP32 ADC averages to a few mV. ✓

**Standby drain:** 29.2 V / 3.2 MΩ = 9.1 µA, which would take 1.3 × 10³ years to empty 105 Ah. ✓

**For 4S2P:** nodes sit at k/4 (0, 0.25, 0.5, 0.75, 1). r₀ = 0.312 still matches none of them.

**Upgrade path if ever needed:** switch a second resistor in with a MOSFET. That gives two equations, so the leakage resistance can be solved exactly; it's the same principle as EV insulation monitors. Not needed now.

## 5. Per-group resistance check

The series current step ΔI is common to every group. The BQ76952 measures each group's own ΔV, so for group $g$:

$$R_g = \frac{\Delta V_g}{\Delta I}$$

- $R_g$ = resistance of group g [mΩ]
- $\Delta V_g$ = change in group voltage over the step [mV]
- $\Delta I$ = current step from the shunt [A]

Sample within about 1 s of the step, before cell diffusion adds to the reading.

| Group state (4S2P) | $R_g$ | ΔV for a 100 A step |
|---|---|---|
| Healthy pair (2 × 0.5 mΩ in parallel) | ≈ 0.25 mΩ | ≈ 25 mV |
| One cell open or loose | ≈ 0.5 mΩ | ≈ 50 mV |

**Rule:** flag any group with more than 1.6× the median of the other groups. It costs zero parts. In 8S1P, the same check tracks each cell's resistance over its life.

## 6. Charger current correction

The NPB-450-12 delivers **25 A**, not the 32 A used earlier (MEAN WELL datasheet).

| Configuration | Charger | Time ≈ C / I_chg |
|---|---|---|
| 8S1P, 105 Ah | NPB-450-24, 13.5 A | 7.8 h |
| 4S2P, 210 Ah | NPB-450-12, 25 A | **8.4 h** (earlier "6.6 h" was wrong) |

Charge time is set by the 450 W charger size, not by the configuration. MEAN WELL also makes the NPB-750-12 (750 W). Its output current hasn't been checked yet; check it before considering faster charging.

## 7. 4S2P: open decision

**What pair-level monitoring hides**

| Fault in one cell | Effect | Mitigation |
|---|---|---|
| Low capacity | The pair still has the sum of its capacities. Series strings are actually *less* sensitive, because pairing averages out the weak cell. | None needed |
| Higher resistance | Current splits as $I_a = I R_b/(R_a+R_b)$. A 10 % mismatch at 630 A gives 330 A, i.e. 3.14C, on one cell | Symmetric busbar paths; cap bursts at 600 A |
| Open terminal | The surviving cell carries the full current (6C at 630 A) | §5 resistance check |
| Internal short | The partner cell discharges into it, with no fuse between the two | Rare in new Grade A cells; the one real downside of unfused parallel cells |

**Assembly rule: voltage-match before bolting a pair together.** Inrush current is $I_0 = \Delta V/R_\text{loop}$: 0.1 V / 1 mΩ = 100 A. The equalising time constant is

$$\tau = R_\text{loop}\, C_\text{eff}$$

- $R_\text{loop}$ = 1 mΩ
- $C_\text{eff} = 3600/(2s) = 2.2\times10^{6}$ F, where $s$ ≈ 0.83 mV/Ah is the slope of the voltage-vs-charge curve at mid-charge (estimate)

That gives τ ≈ 36 min. At mid-charge, 0.1 V of difference means about 60 Ah of charge difference. So match the cells at full charge (3.65 V), where the curve is steep and equal voltage really means equal charge. This happens **once** in fixed 4S2P; it would happen on every reconfiguration in the dual-mode design, which is another argument against dual-mode.

**Matching:** buy all cells from one date code, then pair them by 1 kHz AC resistance or a 4-wire measurement.

## 8. Control board = controls only (decided 2026-11-24)

R4 is resolved: **one board, controls only**. It carries the BQ76952, ESP32, contactor and precharge drive, IMD, CAN, sense connectors and the low-current rails. All power current is in bolted copper (fuse, contactor, shunt, MRBF branches); no separate slot-in BMS board.

## 9. Board power and the "critically low" mechanism

- **Supply:** taken **battery-side of the contactor**, from pack+ through a 2 A fuse. It has to be there so the board can close the contactor in the first place.
- **Power tree:** pack 10–14.6 V → buck 5 V (shunt module, fan) → 3.3 V (ESP32).
- **The buck's EN pin is driven from the BQ76952's REG1 output.** When the BQ76952 enters SHUTDOWN, REG1 drops and the whole board turns off.
- **Autonomous hardware cutoff, independent of firmware.** The BQ76952 enters SHUTDOWN by itself when the minimum cell voltage falls below *Power:Shutdown:Shutdown Cell Voltage*, or the stack falls below *Shutdown Stack Voltage* (TI datasheet). SHUTDOWN draws **1 µA**.
- **Threshold ladder:**
  - 2.90 V/cell: firmware opens the contactor, turns the inverter off and puts the ESP32 to sleep.
  - 2.80 V: BQ76952 undervoltage protection.
  - 2.75 V: the inverter's own low-voltage shutdown (11 V).
  - **2.60 V: BQ76952 SHUTDOWN**, taking the board with it.
  - 2.50 V: EVE cutoff.
- **Draw in SHUTDOWN:**

  | Item | Current |
  |---|---|
  | BQ76952 | 1 µA |
  | Buck in shutdown | ≈ 1 µA |
  | IMD divider | 14.6 V / 3.2 MΩ = 4.6 µA |
  | **Total** | **≈ 7 µA** |

  At 7 µA, even 1 Ah left below 2.6 V lasts 1 / 7×10⁻⁶ h ≈ 16 years, so LFP self-discharge dominates.
- **Wake, with no extra parts:**
  - **Push-button → TS2.** A falling edge below 0.7–1.1 V wakes the device; TS2 is weakly driven to ~5 V in SHUTDOWN.
  - **Charger plugged in → LD pin.** The LD pin sits on the load bus. With the contactor open, the charger's output appears there, and a rising edge above VWAKEONLD (≈ 1.45 V) wakes the device.
- **Caveat (TI FAQ):** if TS2 is held low or LD is held high when SHUTDOWN starts, the device sticks in "Soft SHUTDOWN". The button must be momentary, and LD must read low with the contactor open and the charger unplugged.

## 10. Front panel airflow: checkerboard perforation (baseline)

- **Problem:** the diffuser and LED board block the whole front grid (review C4).
- **Baseline:** lit and air holes alternate in a checkerboard. Air holes go straight through matching holes in the diffuser and the LED board. Lit holes are backed by solid diffuser with an LED behind it. No spacers, no new parts.
  - Open area ≈ 287 holes × 18.1 mm² ≈ **5,200 mm²**, against 3,420 mm² for the "shrink the panel" option, and the full face still glows.
  - The "WE WILL WIN" text pixels stay unholed (dark).
- **Alternatives considered:**
  - (a) Shrink the panel to the module zone: fewer LEDs, but the top third goes unlit.
  - (c) Offset perforation with an air gap: every hole glows, but it needs a ~2 mm spacer between plate and diffuser, which adds parts, and it is the most restrictive path.
- **Check in the v14 CAD:** the current front panel spans y ±97.4, past the body's ±93.4 interior. Fit it inside the walls.

### 9a. Wake, power-on sequence and anti-oscillation (2026-11-24)

**Power chain:** pack → 2 A fuse → 5 V buck (EN ← BQ76952 REG1) → 3.3 V regulator → ESP32. With the 5 V regulator off, everything is off except the BQ76952 (1 µA) and the IMD divider (4.6 µA).

**Push-button (lid, momentary):**
- **From SHUTDOWN:** the button pulls TS2 low → the BQ76952 boots → REG1 on → 5 V and 3.3 V up → the ESP32 boots and self-checks (cells, temperatures, IMD). Then precharge → contactor closed → inverter enabled if configured. **One press = pack on.**
- **When on:** the same button also goes to an ESP32 GPIO. A long press tells the BQ76952 to enter SHUTDOWN, which is pack off.
- It must be momentary: TS2 held low during shutdown entry sticks the device in Soft SHUTDOWN.

**Charger wake: DEFERRED (owner, 2026-11-24). Do not rely on the charger for wake.**
- **Baseline: wake is button-only (TS2).** A charger plugged into a shut-down pack does nothing until the button is pressed.
- LD is not used as a wake source. Hold it low, so it can never stick the device in Soft SHUTDOWN. Exact termination per TI, set in the schematic.
- Candidates for later: +12Vaux (first check whether it's live with AC off), the NPB *Charger OK* pin, or an AC-present optocoupler. Edge-triggered either way, decoupled from contactor state.

**Under-voltage relaxation latch.**
- The real oscillation risk: at low charge, cutting the load lets the cells relax upward, e.g. 2.9 V under load → about 3.1 V at rest. A cutoff that auto-recovers would reconnect, sag and cut again.
- **Rule:** every under-voltage trip (the firmware 2.90 V cutoff and BQ SHUTDOWN at 2.60 V) **latches**. Re-enabling needs the charger plugged in or a button press with the minimum cell ≥ 3.00 V, giving ≥ 100 mV of hysteresis.

### 10a. Diffuser and LED board mounting: one drop-in sandwich

- **Stack:** diffuser and LED board are one sandwich with the same 4 hole positions.
- **Mounting:** **4 M3 screws** through both into **4 M3 standoffs on the module's front end plate** (SendCutSend-tapped M3). Installed before the front plate, with no separate alignment step.
- **Tolerance:** the stack is located by the module and the front plate by the body tabs, a chain of about ±1 mm. So the air holes in the diffuser and LED board are **Ø6.0 mm against Ø4.8 mm in the front plate**, keeping airflow under misalignment. The lit holes need no precise registration.
- **Fallback:** if CAD shows the tolerance chain is worse, locate the stack on the front plate instead (2 locating pins in text pixels).

## 11. Cooling: is through-flow needed? (2026-11-24)

**Heat in the deck zone, worst sustained case.** Inverter at 400 W out and charger at full, i.e. UPS pass-through:

| Source | Heat |
|---|---|
| NTS-400P-112, η 91 % (MEAN WELL) | 400 (1/0.91 − 1) = **39.6 W** |
| NPB-450-12, 25 A × 14.2 V, η 92 % (**assumed**) | **30.9 W** |
| Control board + EV200 hold coil | **4.7 W** |
| **Total** | **P = 75 W** |

**Air temperature rise inside the box:**

$$\Delta T = \frac{P}{\rho c_p Q + UA}$$

- $\Delta T$ = rise of the internal air above ambient [K]
- $P$ = heat [W]
- $\rho$ = 1.2 [kg/m³]
- $c_p$ = 1005 [J/(kg·K)]
- $Q$ = airflow through the box [m³/s]
- $A$ = enclosure surface, 0.49 [m²]
- $U$ = overall wall coefficient: 9.5 W/(m²·K) outside (convection plus radiation, powder coat ε ≈ 0.9) in series with 7 W/(m²·K) inside, so $UA$ = 1.98 [W/K]

| Case | Q through the box | ΔT at 75 W |
|---|---|---|
| Sealed (walls only) | 0 | **38 K**, so 63 °C at 25 °C ambient. The inverter derates toward its 70 °C limit (MEAN WELL). ✗ |
| Rear only: intake and exhaust both at the rear, front holes closed | ≈ 0 to a few m³/h (only what the converter fans mix in) | **20–38 K** ✗ |
| **Full rear grid + front checkerboard** (crude area-ratio split: 5,193 mm² front / (5,193 + 8,867) = 37 % through; fan ≈ 45 m³/h) | ≈ 17 m³/h | **≈ 10 K** ✓ |
| Rear grille only inside the fan circle (blanked) | 35–60 m³/h | **3.4–5.5 K** ✓ |

**Conclusions:**
- **Through-flow matters.** The **front air holes are what make it work**: without an inlet on the opposite end, the box behaves close to sealed.
- **The full rear grid is acceptable**, at about 10 K. The area-ratio split ignores the through path's extra restriction, so allow 10–15 K. **Decision: full rear grid restored** for looks.
- A blanking sheet behind the rear plate is the drop-in upgrade if bench ΔT exceeds 15 K. A **second Noctua isn't needed**, and at the rear it wouldn't fix the short circuit anyway.
- **DC 210 A continuous case:**
  - 44 W in the cells. Their mass of 16 kg × ~1000 J/(kg·K) = 16 kJ/K gives about 2.8 K/h, and the pack only lasts about 1 h at 210 A, so this is negligible.
  - About 30 W in the power path (contactor, fuse, joints) in the deck zone: less than the UPS case above.
- **Bench check:** at 400 W inverter load, log inlet and exhaust air temperature (telemetry list). Target ≤ 15 K.

## 12. Converter service bays (option 2, decided 2026-11-24)

**Problem.** v13 and v14 left 10–13 mm at the converter ends, too little to plug anything in. The NTS-400P DC input is an Anderson 1327 (SB50-style) and its AC output a JST VH 6-pin; the NPB-450 has an AC input with an on/off switch and DC output V+/V− (MEAN WELL spec sheets). Which end each connector is on is **not yet confirmed**; get the mechanical drawing.

**Option 2 as built** (same 365 mm box):

| Gap | v14 first cut | Now | How |
|---|---|---|---|
| Fan face → converter rears | 10 mm | **18 mm** | Both converters moved 8 mm forward |
| Charger front → contactor (y −5 … 67) | 12 mm | **27 mm** | Contactor moved forward to x 87–153. It stops there because the module's front standoff screw heads at (158, ±55) sit under it. The first plan said 37 mm; that wasn't achievable. |
| Charger front → line riser / − riser / G10 deck (y −86 … −16) | — | 1–2.5 mm | **The charger's connectors must face the +y half** of its front end. |
| Inverter front → MRBFs (y 37 … 83) | 13 mm | **37 mm** | MRBF riser moved behind the contactor, above the charger |
| Inverter front → line bar / + terminal tab (z ≥ 292) | — | 21 mm | — |

**Consequences:**
- **Charger:** use a right-angle C13 (about 25–30 mm); 27 mm is marginal.
- **Inverter:** replace the SB50 plug with ring lugs on its DC terminals, as planned in option 2.
- **Lid:** inlet moved to y −17 in the front column; push-button moved to (100, −60).
- **Board:** third standoff moved to (141, −10).
- **Open:** confirm the connector ends from the MEAN WELL drawings. If the charger's AC inlet sits in its −y half, flip the charger 180° about z (its terminals then face the +y side) or move the line riser.

**Update (owner OK'd +5–10 mm):** inside length **365 → 375 mm**, all of it added at the rear (front plate unchanged). Converters move back with the rear plate:

| Gap | Value |
|---|---|
| Fan → converters | **18 mm** |
| Charger front → contactor | **37 mm** |
| Charger front → line riser / − riser (−y half) | 12.5 mm |
| Inverter front → line bar | **31.5 mm** |
| Inverter front → MRBFs | **47 mm** |

Overall envelope 389 × 206 × 390 mm.
