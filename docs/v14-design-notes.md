# v14 design notes and justifications

Decisions made after v13, to be built into the v14 CAD and schematic. Each item records the decision, why it was made, and the calculation behind it.

| # | Item | Status |
|---|---|---|
| 1 | Sense flex: M3 tapped hole + S-loop tab per node | **Baselined** |
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

**Part cost:** 9 M3 × 6 mm screws. Accepted; it beats a hot-plate process.

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
