# Charger and inverter selection (2026-11-27)

**Trigger:** Chris, 2026-11-27. The rule now is that cells are the dominant constraint: everything above the cells (converters, power bay, fan, a separate BMS board) fits inside the module footprint, **312 × 158 mm including the end plates**. The charger and inverter are what broke this rule, so the search is reopened rather than tweaked (`handoff-converters.md`, `owner-requirements.md` §3, §5).

**Status (2026-11-27):** **Chris picked option D** (D39) and no USB-C for now. Open: charger-stop method (relay vs PB-230-12, §6 Q2) and the BMS board's responsibilities before sizing it (Q3). No CAD until those are settled.

Packing model: `cad/analysis/converter_packing.py` (3D boxes plus a checker for clashes, footprint, lid height, + to − gaps and fuse lift-out). Figures are in `versions/v16-c1-power-module/renders/conv_*.png`.

## 0. Answer

| | |
|---|---|
| **Recommended** | **Option D: MEAN WELL NPB-360-12TB (20 A charger) + MEAN WELL NTS-400P-112 (400 W inverter, kept) + the 40 mm fan MEAN WELL specifies for it.** The charger lies flat on deck 1 and the inverter flat above it on deck 2. The power bay is a strip along the −y wall, open to the lid. The BMS board lies flat over the inverter. |
| Fit | **0 clashes, all inside 312 × 158**, + to − ≥ 10 mm, MRBF fuses lift out (`conv_D_npb360_nts400p.png`). Lid inside z 333: **131 mm above the can tops, vs 116 today (+15 mm)**. |
| Box | ≈ 314 × 168 × 333 inside ≈ **17.6 L, vs 25.2 L today (−30 %)**. No rear void. ⚠️ Inside width: pack copper sits 2 mm inside the footprint edge and needs 7 mm to the wall. |
| What it costs | The NPB-360 has **no remote on/off and no CAN** (R5 ✗). Options are in §6 Q2. Charging is 20 A (≈ 10.5 h) instead of 25 A, and efficiency is 88.5 % instead of 92 %. |
| Combined unit (top priority) | **None fits.** The only catalog inverter-charger near this size, the Victron MultiPlus 12/500/20 120 V, fails all three orientations (`conv_A_multiplus.png`). The only way to use it is upright, which needs the lid at ≈ z 590 (§6 Q1). |
| Root cause, confirmed | **The NPB-450's 135 mm width.** The bay strip needs ≥ 59 mm of width beside the converters, which leaves ≤ 96 mm for them. With the same layout, the NPB-450 clashes with the shunt, SB175, 2151 and + rail (`conv_B_npb450_nts400p.png`). |

## 1. Requirements
| # | Requirement | Source |
|---|---|---|
| F1 | Everything above the cells inside x ±156, y ±79 (module + end plates) | Chris 2026-11-27, owner-req §3 |
| F2 | Height above the cells uncapped, "but be reasonable". Today 116 mm (can top 201.85 → lid inside 318) | Chris 2026-11-27 |
| F3 | Power bay (GV14 kept, 5191, 2151, Tesla shunt, SB175), fan(s), a **separate BMS board** and the lid connectors all placed in the same footprint | handoff §2b, Chris |
| F4 | Every converter in a **datasheet-rated mounting orientation** (horizontal for all MEAN WELL derating curves) | this study, trap T2 |
| F5 | Fuses lift out with the lid off; + to − ≥ 10 mm; pack copper to chassis ≥ 7 mm; top-down assembly | CLAUDE.md, power-train P5 |
| R1 | 4S LFP 10.0–14.6 V, charge to 14.2 V, 2-stage, inhibit below 2 ℃ | v14-baseline |
| R2 | Charge current **≥ 17 A**, internal charger | Chris 2026-11-27 |
| R3 | Inverter **≥ 300 W continuous**, 120 V 60 Hz pure sine, NEMA 5-15. Priority: combined unit > internal inverter > USB-C PD last resort | Chris 2026-11-27 |
| R4 | IEC C14 inlet, universal AC | baseline |
| R5 | Charger controllable from the ESP32: CAN preferred, at minimum remote on/off + CV ≥ 14.2 V | baseline |
| R6 | Catalog parts with manufacturer datasheets; no emailing vendors | CLAUDE.md |
| R7 | Purchased parts never modified (no cutting cords) | CLAUDE.md |
| R8 | Thermal path shown at the rated load | cooling.md |
| R9 | Branch fusing stays MRBF; re-size for the new input currents | baseline |

**Width budget, which decides the search.** The bay strip needs:
- the GV14 body, 55.7 mm, plus clearance;
- two copper rails (20 + 10 gap + 20 mm);
- the SB175 with its G10 cheeks (44 mm), and the shunt with its PCB overhang (43 mm).

So the strip is **≥ 59 mm**, which leaves **≤ 96 mm of width for the converter column**. The column's length per deck, plug room included, must be ≤ 312 mm. Any flat converter wider than ≈ 96 mm forces either a third deck (option S, +99 mm) or an unrated on-its-side mounting (F4).

## 2. Candidates

### 2a. Combined inverter-chargers (searched first)
| Unit | Inverter / charger | Size [mm], mass | Verdict |
|---|---|---|---|
| **Victron MultiPlus 12/500/20-16 120 V** (PMP121500100) | 430 W at 25 ℃, 400 W at 40 ℃ / 20 A. Zero-load 6 W (2 W search mode). VE.Bus; remote on/off/charger-only | **311.9 × 183 × 101, 4.4 kg**; DC and AC connections on the 183 × 101 end | ✗ **Flat:** 183 > 158. **On its side:** 312 + ≈ 50 cable room ⚠️ > 312. **Upright:** fits in plan, but the lid goes to ≈ z 590 (388 mm above the cells, vs 116). Victron also asks for 10 cm clearance all round and "never directly above batteries" (T3). Figure A |
| Victron MultiPlus 12/800/35 120 V | 700 W / 35 A | 360 × 240 × 100, 6.4 kg | ✗ longer and wider than the footprint |
| Xantrex Freedom XC 1000 | 1000 W / 50 A | 360 × 270 × 95, 6.1 kg | ✗ |
| MEAN WELL NTU-1200 | 1200 W, UPS **bypass only, no charger** | — | ✗ not a charger |
| MEAN WELL NTN-5K | 5 kW inverter + charger | 24/48 V only | ✗ no 12 V model |
| MEAN WELL BIC-2200-12 (bidirectional) | 2160 W | 330 × 140 × 41 | ✗ AC side 180–264 V only, and it is grid-tied (needs mains to run) |
| Samlex EVO, Go Power IC, Mastervolt CombiMaster, Renogy, AIMS | ≥ 1000 W | all ≥ 360 mm long ⚠️ (not opened one by one) | ✗ **not checked individually**: every unit found is ≥ 1 kW and larger than the Xantrex |
| Power-station inverter-charger boards (EcoFlow and similar) | — | — | ✗ **not tried**: not catalog parts, no datasheets (R6) |

**Conclusion:** no combined unit fits the footprint at a reasonable height. The smallest one on the market is still 183 mm wide.

### 2b. Chargers (12 V, ≥ 17 A)
| Charger | I [A] | Size L × W × H [mm] | η | Control | Cooling | Price (2026-11-27) | Verdict |
|---|---|---|---|---|---|---|---|
| **MEAN WELL NPB-360-12TB** | **20** (adj. 10–20) | **182.7 × 96 × 49**, 1.3 kg | 88.5 % (TB) | DIP 2/3-stage, VR for V (10.5–15.2) and I. **No remote, no CAN** | internal fan, on at ≥ 50 ℃ | **CAD 125.10** (Sager, 64 in stock) | **✓ picked.** The only ≥ 17 A charger ≤ 96 mm wide with a manufacturer datasheet and no cords |
| MEAN WELL NPB-450-12 (today) | 25 | 205 × **135** × 55, 1.38 kg | 92 % | **CAN 2.0B + remote** | fan | CAD 199.48 (Sager) | ✗ 135 wide: clashes with the bay (Figure B). Fits only in a three-deck stack (Figure S, +99 mm) |
| MEAN WELL NPP-450-12 | 25 | 205 × 135 × 55 | 92 % | remote | fan | — | ✗ same case as the NPB-450 |
| MEAN WELL NPB-240-12 | 13.5 | 182.7 × 96 × 49 | 88.5 % | — | fan | — | ✗ < 17 A |
| MEAN WELL PB-230-12 | **16** | 190 × 96 × 49, 1.21 kg | **81.5 %** | **remote ✓** | fan | — | ✗ 16 A < 17 A, poor efficiency. Fallback if R2 drops to 16 A (13.1 h) |
| MEAN WELL PB-300 / PB-360 | 20.85 / 24.3 | 253 × 135 × 48.5 | — | remote | fan | — | ✗ 135 wide |
| MEAN WELL HEP-600C-12 | 17.5–35 | 280 × **144** × 48.5, **3.9 kg** | 93.5 % | remote, 5VSB | **fanless** (potted, IP-rated) | CAD 357.33 | ✗ 144 wide; on its side it is outside the HORIZONTAL derating curve (T2) |
| **MEAN WELL RPB-1600-12** | 20–100 (programmable) | 300 × **85** × 41 **+ ≈ 38 DC busbar tabs**, 2.1 kg | 91 % | **PMBus / CANBus, remote, PV/PC** | fan | CAD 641.58 (Bravo, 9) | ✗ **338 mm long with its tabs** (T1). Best electrically (3–4 h charge, CAN); lost on 26 mm of length |
| MEAN WELL ENC-360-12 | 24 | 192 × **178** × 45.5 | 91 % | — | — | — | ✗ 178 wide |
| MEAN WELL PB-600-12 / NPB-750 / NPB-1200 | 35–70 | 230–250 × 158 × 67 | — | some CAN | fan | — | ✗ 158 wide = the whole footprint |
| MEAN WELL HLG-320H-15A (LED driver, CV+CC) | 19 | 252 × 90 × 43.8 | ≈ 94 % | A-type: none | fanless | — | ✗ an LED driver, not a charger: no battery-charging rating, backfeed from the battery unspecified ⚠️ |
| MEAN WELL RSP-320-15 (CV supply) | 21 | 215 × 115 × 30 | — | — | fan | — | ✗ no programmed CC: overload limit is 105–125 % of rating |
| Victron Blue Smart IP67 12/17, 12/25 120 V | 17 / 25 | 219 × 99 × 65, 2.4 kg | 95 % | **Bluetooth only** | fanless | not priced | ✗ factory AC cord with NEMA plug and 1.68 m DC leads (can't be cut, R7), no wired control, 99 wide |
| Victron Blue Smart IP22 / Phoenix IP43 | 20–30 | ≥ 108 wide ⚠️ | — | BT / VE.Smart | fan | — | ✗ **not opened**: wider than the NPB-360 and cord-attached ⚠️ |
| Cotek CX1225 | 25 | ≈ 243 × 183 × 72 ⚠️ (retailer) | — | optional CR-1 remote | fan | — | ✗ 183 wide |

### 2c. Inverters (12 V, ≥ 300 W, 120 V)
| Inverter | P_cont | Size [mm], mass | Idle | Control | Cooling | Price | Verdict |
|---|---|---|---|---|---|---|---|
| **MEAN WELL NTS-400P-112 (kept)** | **400 W** with a 10 CFM fan 5 cm from the DC end (40 ℃); ≈ 240 W natural convection | **186 × 100.5 × 34, 0.75 kg** | 10 W; ≤ 1.5 W in saving mode | remote (CN301), DIP | **no fan of its own**; CN100 drives an optional 40 mm fan | **CAD 148.68** (TRC) | **✓ kept.** The smallest ≥ 300 W unit found by far (0.64 L). The 40 mm fan the datasheet asks for now has a designed spot, which closes the cooling.md open item |
| MEAN WELL NTS-250P-112 | 250 W | 186 × 100.5 × 34 | same | same | — | — | ✗ < 300 W |
| MEAN WELL NTS-450-112 | 450 W | 210 × **130** × 55, 1.66 kg | 10 W | remote | **own fan** | — | ✗ 130 wide |
| MEAN WELL TS-400-112 | 400 W | 205 × 158 × 67 | 15 W | remote | — | — | ✗ 158 wide, 84.5 % efficient |
| Victron Phoenix 12/375 120 V (PIN123750500) | 375 W at 25 ℃, 300 W at 40 ℃ | 260 × **165** × 86, 3.0 kg | 6 W; ECO mode | **VE.Direct**, remote | fan | USD 117.30 (NAZ Solar) | ✗ 165 > 158 flat; on its side it is 165 tall and its orientation is unrated |
| Victron Phoenix 12/500 120 V | 460 / 380 W | 275 × 172 × 86 | 7 W | VE.Direct | fan | — | ✗ 172 wide |
| Samlex PST-300-12 | 300 W | ≈ 246 × 155 × 66 ⚠️ (retailer) | < 6 W | — | fan | — | ✗ 155 wide, GFCI outlets on the unit |
| Cotek SE350-112 | 350 W | 187.5 × 150 × 68, 1.33 kg | < 7.8 W | remote | fan | — | ✗ 150 wide |

### 2d. Last resort (USB-C PD, no internal inverter)
**Not needed:** an internal inverter fits (§3). For reference, 12 V panel-mount 100 W PD sockets exist (e.g. Powerwerx 100 W, 12–24 V in), but no manufacturer datasheet of the quality R6 asks for was found ⚠️. Adding a USB-C PD port alongside the inverter is a separate, optional decision (§6 Q4).

## 3. Packing results (pack first, claim second)
| Option | Parts | Lid inside z (mm above can tops) | Checker | Figure |
|---|---|---|---|---|
| A | MultiPlus 12/500/20 | ≈ 590 (388) upright; doesn't fit flat or on its side | ✗ | `conv_A_multiplus.png` |
| B | NPB-450 + NTS-400P, layout D | 333 (131) | **✗ 7 clashes**: charger × shunt, SB175, 2151, + rail, bay plate | `conv_B_npb450_nts400p.png` |
| S | NPB-450 + NTS-400P + a **top deck** carrying the C1 module, BMS and lid connectors | **417 (215)** | ✓ 0. ⚠️ C1 is 165 wide as built and would need to shrink 7 mm; deck 2 leaves a 57 × 312 × 34 mm void beside the inverter (dead space) | `conv_S_stack_top_bay.png` |
| **D** | **NPB-360 + NTS-400P + 40 mm fan** | **333 (131)** | **✓ 0** | `conv_D_npb360_nts400p.png` |

**Option D layout.** Rear is −x, front is +x. Pack− comes from the rear cells; pack+ rises at the front, as in C1.
- **Deck 1 (z 221.6–270.6):**
  - NPB-360 flat against +y (y −17…+79), DC terminal block at the rear, C14 inlet at the front;
  - power-bay strip y −79…−20, open to the lid. Rear to front: Tesla shunt → SB175 (straddling the − rail, outer lane, and the + rail, inner lane, 10 mm apart) → 2151 with the charger 30 A and inverter 50 A MRBFs → GV14 at the front corner;
  - the 5191 sits on the + riser's in-bar in the front corner beyond the charger.
- **Deck 2 (z 276.3–310.3):**
  - NTS-400P flat over the charger, DC end (PP45) at the rear;
  - MEAN WELL's 40 × 40 × 20 fan at the rear wall, 50 mm from the DC face (its rated condition), drawing air in through the rear grid;
  - CN500 at the front.
- **Under the lid:**
  - BMS board 175 × 90 ⚠️ (size to be confirmed by the pcb lane) on 6 mm standoffs over the inverter;
  - C14 inlet and NEMA outlet above the front corner, next to the charger's C14 and the inverter's CN500 (short AC runs);
  - button at the rear;
  - SB175 through the lid over the strip (mating face 8.4 mm above the lid top, as in C1).
- **Row budgets (x):**
  - deck 1: 30 TB + 182.7 + 40 C13 = 253 of 312;
  - deck 2: 20 fan + 50 + 186 + 20 CN500 = 276 of 312;
  - strip: shunt 83.5, SB175 55.6, 2151 88.5, GV14 59.9 = 288 with gaps, of 312.
- **Width budget (y):** charger 96 + gap 3 + strip 59 = 158.
- **Leads:**
  - charger and inverter − go to shunt node B at the rear (≈ 60–80 mm);
  - their + leads go to the 2151 (≈ 150–200 mm);
  - the charger's DC tabs no longer have to reach a far bay.
- **Where D's free space is:**
  - deck 1 front corner beyond the C13 plug (≈ 35 × 96 mm);
  - over the rear half of the strip above the shunt.

  The rest is service access (fuse lift-out, SB175, sockets).
- **Not modelled yet (CAD phase):** harness and lead routing, the sense-flex tail to the BMS board, exact copper (rails, in-bar under the GV14), the socket sweep (`assembly_v16.py`), the true GV14, 5191 and SB175 outlines ⚠️.

## 4. Thermal and electrical checks (option D)
- **Branch fuses (R9):** inverter input at 400 W / 11 V / 0.89 ≈ 41 A → **MRBF 50 A kept**. Charger 20 A → **MRBF 30 A kept**.
- **Undervoltage ladder:** NTS-400P cuts out at 10.0 ± 0.3 V (2.5 V/cell) and alarms at 11 V. The ladder (2.90 firmware → 2.80 BQ UV → 2.75 inverter) stays enforced by firmware and the BQ, as today. The inverter is unchanged.
- **Standby:** unchanged, since the inverter is the same; the NPB-360 leaks < 1 mA from the battery. **13.8 days ON-idle** as today.
- **Heat, UPS case** (inverting and charging at once):

  | Source | Loss |
  |---|---|
  | Inverter at 400 W (η 89 %) | 49 W |
  | NPB-360 at 20 A × 14.2 V (η 88.5 %) | 37 W |
  | GV14 coil | 2.8 W |
  | BMS board | 2 W |
  | **Total** | **≈ 91 W** (77 W today) |

  At 300 W inverter output the total is ≈ 79 W.
- **Air path:**
  - MEAN WELL's 10 CFM fan blows rear → front along the inverter, which **meets the inverter's rated condition**: 100 % load to 40 ℃.
  - The NPB-360's own fan (switched on at 50 ℃ internal) cools the charger.
  - ⚠️ **Box air rise with only the converter fans:** about 10 K if both fans move air through the box (≈ 27 m³/h), up to about 24 K if only the 40 mm fan does (≈ 11 m³/h effective). The NPB-360 fan's flow is not published ⚠️.
  - Re-run `cooling_v16.py` in the CAD phase. If the rise is above 15 K, either:
    - cap the charge current at 10 A while the inverter runs above 300 W (firmware, no parts); or
    - add a second 40 mm fan at the rear wall over the charger's DC end (space exists at x −156…−136, y −17…+5).
- **The NF-A14 pack fan is no longer needed for the converters,** and it doesn't fit under the new rule: 140 mm is taller than the deck.

## 5. Path taken (this session)
1. **The rule.** The footprint is fixed (312 × 158) and height is free. So the question became which converters, packed with the bay, fit that plan.
2. **Combined units first.** Victron's own 120 V manual (§7.6 drawing) shows the MultiPlus 12/500/20 is 311.9 × 183 × 101 with every connection on the narrow end. Every other inverter-charger is ≥ 1 kW and larger. ✗
3. **Wide datasheet sweep:**
   - 20 MEAN WELL datasheets: NPB, NPP, PB, HEP, ENC, HLG, RSP, RPB, NTS, TS, BIC, NTN;
   - Victron: MultiPlus, Phoenix 120 V, IP67;
   - Samlex, Cotek, Xantrex.
4. **RPB-1600-12 looked like the winner:** 1U, 85 wide, PMBus/CAN, 20–100 A, all connections on one end. The mechanical drawing then showed the "300" excludes ≈ 38 mm of DC busbar tabs, giving 338 > 312. ✗ (trap T1)
5. **The width budget explained everything.** The bay strip needs ≥ 59 mm, so a flat converter must be ≤ 96 mm wide. The NPB-450 (135) was the root cause, not the inverter: the NTS-400P (100.5) sits on deck 2 over the charger, where only the bay's tall parts (GV14, 5191) need the width, and those sit beyond the inverter's ends.
6. **The NPB-360 is 96 wide and 20 A,** from the same family as today's charger. Packed: 0 issues.
7. **The three-deck stack (S)** was packed as the "keep NPB-450" alternative: +99 mm and a void beside the inverter.

## 6. Decisions for Chris (answers 2026-11-27 in brackets)
- **Q1 Combined unit.** [**Separate units, D.**] The MultiPlus fits only standing upright: the lid goes to ≈ z 590 (≈ 590 mm inside height vs 318), +2.3 kg, plus Victron's 10 cm-clearance and not-over-batteries notes. Separate units (D): z 333.
- **Q2 Charger control for the NPB-360** (it has no remote and no CAN). [Chris likes the relay; asked whether the PB-230-12 has CAN. **It doesn't:** it has only a remote-stop input (CN105), a fixed 3-stage curve (14.4 / 13.6 V, no voltage adjustment found), 16 A and 81.5 % efficiency (≈ 52 W loss at 16 A, vs 37 W for the NPB-360 at 20 A). Its case is 190 × 96 × 49, 7.3 mm longer than the NPB-360, which still fits deck 1 (260 of 312). Pending.]
  - (a) a normally-open DC relay in the charger + lead, closed by the BMS (+1 part, fail-safe);
  - (b) stop charging by opening the GV14 (no part, but it drops the outlets too);
  - (c) PB-230-12: 16 A, has a remote, 81.5 % efficient;
  - (d) keep the NPB-450 and go to three decks (S, +99 mm).
- **Q3** [Chris: define the board's responsibilities first, then size and place it.] BMS board space claim 175 × 90 mm over the inverter, or a different size (pcb lane).
- **Q4** [**No USB-C for now.**] Optional USB-C PD output alongside the inverter (not needed to meet R3).

## 7. Sources
| Value | Source | Conf. |
|---|---|---|
| NPB-360-12: 20 A, 10.5–15.2 V, 182.7 × 96 × 49, η 87 % (XLR/AD1) / 88.5 % (TB), no remote | MEAN WELL NPB-360-SPEC 2026-07-06 | ✓ |
| NPB-450-12: 25 A, 205 × 135 × 55, CAN | NPB-450-SPEC 2026-07-06 | ✓ |
| NTS-400P-112: 400 W, 186 × 100.5 × 34, 10 CFM fan condition, LV shutdown 10 V | NTS-400P-SPEC 2026-03-26 | ✓ |
| RPB-1600-12: 300 × 85 × 41 body, DC tabs ≈ 30–38 mm beyond | RPB-1600-SPEC 2026-06-15, mechanical drawing p.7 (tab length scaled from the drawing) | ✓ / ⚠️ tab length |
| HEP-600C-12, PB-230/300/360/600, NPB-240/750/1200, NPP-450, ENC-360, HLG-320H, RSP-320, NTS-250P/450, TS-400, BIC-2200, NTN-5K | MEAN WELL SPEC PDFs (dates in file footers, 2020–2026) | ✓ |
| All MEAN WELL derating curves are drawn for HORIZONTAL mounting | same | ✓ |
| MultiPlus 12/500/20 120 V: 430/400 W, 20 A, 311.9 × 183 × 101, connections at the bottom, 10 cm clearance, not above batteries | Victron Datasheet-MultiPlus-500-1200VA-120V-EN; MultiPlus 12V 500–1200VA 120Vac manual §4.1, §7.2, §7.6 | ✓ |
| Phoenix 12/375 120 V: 375/300 W, 260 × 165 × 86, 3.0 kg | Victron Datasheet-Inverter-VE.Direct-250W-1600W-120V-EN | ✓ |
| Blue Smart IP67 120 V: 17/25 A, 219 × 99 × 65, cords | Victron Datasheet-Blue-Smart-IP67-Charger-120VAC (FR) | ✓ |
| Cotek SE350: 187.5 × 150 × 68 | Cotek SE350 SPEC A1 | ✓ |
| Samlex PST-300-12 size, Cotek CX1225 size | retailer listings | ⚠️ |
| Xantrex Freedom XC 1000: 360 × 270 × 95 | Xantrex Freedom XC datasheet 2024-06-11 | ✓ |
| GV14, 5191, 2151, SB175, Tesla shunt outlines | contactor-mounting.md, lib.BS, tesla-shunt.md | ⚠️ as flagged there |
| BMS board 175 × 90 | space claim, estimate (v15 board 195 × 82) | ⚠️ |
| 50 mm cable room at the MultiPlus connection end | estimate (16 mm² cable bend + G-ST18i plug) | ⚠️ |

## 8. Traps found
| # | Trap | Rule |
|---|---|---|
| T1 | MEAN WELL's "DIMENSION L × W × H" excludes protruding DC busbar tabs: the RPB-1600 is 300 on the spec line and ≈ 338 on the drawing | Size every part from its mechanical drawing, never the spec-table line |
| T2 | Every MEAN WELL derating curve is drawn for HORIZONTAL mounting; on its side a converter is outside its rating (and another orientation needs an email to MEAN WELL, which R6 rules out) | Converters lie flat (F4) |
| T3 | Victron asks for 10 cm clearance around the MultiPlus and "never directly above batteries" | Read the manual's installation chapter, not just the datasheet |
| T4 | Wall-mount units put their connections on the bottom end, so the long axis plus cable room sets the length | Add connection room on the connector face before comparing sizes |
| T5 | Victron's 120 V Blue Smart chargers have factory cords that can't be cut (R7) | Prefer terminal-block or inlet units |
| T6 | The old 130 mm can-width target made the NPB-450 look like the wrong part on its own. Against the 158 footprint it fits alone; it fails with the bay beside it | Check every candidate against the full space claim (handoff §2b), never alone |
| T7 | Digi-Key and Mouser show bot walls to the automated browser | Price via Octopart (same authorized-distributor data) and name the distributor |

## 9. Buy links and prices (read 2026-11-27, qty 1)
| Part | Price | Where |
|---|---|---|
| MEAN WELL NPB-360-12TB | CAD 125.10 (64 in stock) | Sager via [Octopart](https://octopart.com/search?q=NPB-360-12TB) |
| MEAN WELL NTS-400P-112 | CAD 148.68 (1 in stock) | TRC via [Octopart](https://octopart.com/search?q=NTS-400P-112) |
| 40 × 40 × 20 fan, 10.8 CFM (Sunon MF40201VX-1000U-G99) | USD 7.25 | Digi-Key (cooling.md, 2026-11-27) |
| MEAN WELL NPB-450-12 (today) | CAD 199.48 (19) | Sager via Octopart |
| MEAN WELL HEP-600C-12 | CAD 357.33 (68) | Sager via Octopart |
| MEAN WELL RPB-1600-12 | CAD 641.58 (9); USD 484.07 at TRC (0) | Bravo via Octopart; [TRC](https://www.trcelectronics.com/search?q=RPB-1600-12) |
| Victron MultiPlus 12/500/20-16 120 V | USD 261.81 | [NAZ Solar Electric](https://www.solar-electric.com/catalogsearch/result/?q=multiplus+12%2F500%2F20) |
| Victron Phoenix 12/375 120 V | USD 117.30 | [NAZ Solar Electric](https://www.solar-electric.com/victron-phoenix-12-375-120v-nema-5-15r-inverter.html) |

**Option D converter cost:** CAD 125.10 + 148.68 + ≈ CAD 10 fan ≈ **CAD 284**, vs CAD 348 for today's pair (NPB-450 + NTS-400P).

## 10. Open items
- Chris: Q1–Q4 (§6).
- ⚠️ NPB-360 fan flow and direction; box air rise without the NF-A14 (re-run `cooling_v16.py`).
- ⚠️ BMS board size and connector edge (pcb lane).
- ⚠️ Inside width: pack copper on the strip at y −77 needs 7 mm to the wall (inside ≥ 168) or rails moved 5 mm inboard.
- ⚠️ True outlines: GV14, 5191, SB175, NTS CN500/TB1 positions, NPB-360 C14 position.
- After the pick: `tower17.py` + bay module, interference/clearance/assembly checks, fast renders, BOM and SCS total.
