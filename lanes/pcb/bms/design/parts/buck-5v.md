# 5 V buck (B+ → 5 V): TI LMR604305SBRAKRQ1

**Pick:** LMR60430-Q1, 3 A, 5 V fixed, "B" variant, WQFN-HR-9 2.5 × 2 mm. It is the only candidate found that is **in stock, does 3 A and guarantees ≤ 2 µA in shutdown**. Fallback: TPS62933DRLR (§6), if drawing a new footprint isn't wanted and a typical-only 2 µA is accepted.

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | VIN 10.0–14.6 V; survives 20 V design max and the TVS clamp (24.4 V) | intent §2, [input-protection.md](input-protection.md) |
| R2 | ≤ 2 µA from B+ with EN low | team lead; intent §4 (≤ 10 µA board) |
| R3 | EN driven by BQ76952 REG1 (3.3 V, [bq76952.md](bq76952.md)) | v14-design-notes §9 |
| R4 | **Up to 3 A continuous**; real load ≤ 2.45 A peak (LEDs 2 A at the 10 W cap + ESP32, shunt, logic ≈ 0.45 A) | Chris 2026-11-27; intent J5 |
| R5 | 5 V within 4.7–5.3 V (Tesla shunt) | tesla-shunt.md §3 |

## 2. Candidates (datasheets in `datasheets/`, DigiKey API checked 2026-11-27)
| Part | VIN rec / abs [V] | I [A] | Shutdown typ / max [µA] | Package | Stock | Verdict |
|---|---|---|---|---|---|---|
| **LMR604305SBRAKRQ1** (TI) | 36 / 42 | 3 | 0.7 / **1** (T_J 25 °C) | WQFN-HR-9 2.5 × 2 | in stock | **✓** |
| TPS62933DRLR (TI, starting point) | 30 / 32 | 3 | 2 / **none given** | SOT-583 | in stock | Fallback: R2 only typical |
| LMR43620 (TI) | 36 / 42 | 2 | 0.25 / 1 (−40…150 °C) | VQFN-HR-9 2 × 2 | **not stocked** (all variants queried, long lead) | ✗ stock; no 3 A |
| AP63357DV-7 (Diodes) | 32 / 35 | 3.5 | 1 / **3** | V-DFN3020-13 | in stock | ✗ R2 max |
| LMR51430 (TI) | 36 / — | 3 | 3 / 15 | SOT-23-6 | in stock (X variant) | ✗ R2 |
| TPS563300 (TI) | 28 / — | 3 | 2 / none given | SOT-583 | in stock | ✗ no gain over TPS62933 |
| TPS629210 (TI) | 17 / **18** | 1 | 0.25 / 1.5 | SOT-583 | in stock | ✗ R1, R4 |
| AP63200 | — | 2 | 1 / 3 | TSOT23-6 | not stocked | ✗ |

**Not tried:** ADI LT8609/LT8610 class and MPS parts (higher cost, no reason to leave TI), 3 A modules.

## 3. Identity
| Item | Value |
|---|---|
| Datasheet | SNAS875E, Feb 2025, rev. Aug 2026 (`LMR604305SBRAKRQ1.pdf`). Read: §4–8 |
| Orderable | **LMR604305SBRAKRQ1**: 3 A, 5 V fixed/adj, spread spectrum, B variant (UVLO rising 3.5 V, 1 V hysteresis), RAK |
| Lifecycle | ACTIVE (ti.com part-details page and DigiKey API, 2026-11-27) |
| Footprint | ⚠️ **No KiCad library footprint.** Draw it from the datasheet's RAK0009A land pattern (HotRod: no thermal pad, odd pad shapes) |
| Second source | TI only. Pin-compatible family 0.6–6 A (LMR60440 etc.), same footprint |

## 4. Pins and externals (RAK)
| Pin | Name | Connect | Note |
|---|---|---|---|
| 1 | VIN | B+ (after TVS); CIN_HF + CIN at the pin | 50 V parts (§8.2.2.4) |
| 2 | PGND | ground plane, via array | |
| 3 | SW | L1, CBOOT | do not drive externally |
| 4 | BOOT | CBOOT 100 nF to SW | ≥ 10 V (§8.2.2.5) |
| 5 | PG | open | optional (§7.3.8). A pull-up would only add load |
| 6 | FB | 5 V rail directly (fixed-output mode, §7.3.5) | sense at COUT, away from SW |
| 7 | MODE/SYNC | GND = auto (PFM) | **must not float** (§7.3.4) |
| 8 | RT | 33.2 kΩ to GND → 1 MHz | |
| 9 | EN | BQ REG1 net, plus **100 kΩ to GND** | thresholds 1.15–1.35 V rise, 0.9–1.1 V fall |

| Ref | Part | Value | Footprint | Stock |
|---|---|---|---|---|
| L1 | Bourns SRP5030TA-3R3M | 3.3 µH, DCR ≤ 38 mΩ, Irms 5 A, Isat 8 A (−20 %), 5.7 × 5.2 × 3 mm | `Inductor_SMD:L_Bourns_SRP5030T` ⚠️ verify TA land pattern | in stock |
| C_IN ×2 | TDK C3216X7R1H475K160AE | 4.7 µF 50 V X7R 1206 | `Capacitor_SMD:C_1206_3216Metric` | in stock |
| C_INHF | Yageo CC0402KRX7R9BB104 | 100 nF 50 V X7R 0402 | `Capacitor_SMD:C_0402_1005Metric` | in stock |
| C_OUT ×2 | Murata GRM31CZ71C226ME15L | 22 µF 16 V X7R 1206 | `Capacitor_SMD:C_1206_3216Metric` | in stock |
| C_BOOT | CC0402KRX7R9BB104 | 100 nF | 0402 | |
| R_T | 1 % | 33.2 kΩ | 0402 | |
| R_EN | 1 % | 100 kΩ | 0402 | |

## 5. Calculations
**Frequency** (B variant, §7.3.3): f_sw = 1 / (R_T × 2.825×10⁻¹¹ + 69.6 ns) = 1 / (937.9 + 69.6 ns) = **993 kHz** (table 8-2 uses 33.2 kΩ for 1 MHz).

**Inductor** (Eq. 8), VIN 14.6 V, VOUT 5 V:
- ΔI = (14.6 − 5) × (5/14.6) / (3.3 µH × 993 kHz) = **1.00 A** (33 % of 3 A; target 20–40 %). At 20 V: 1.14 A.
- Peak at 3 A = 3.5 A. I_sat 8 A ≥ high-side limit max 7.5 A (§8.2.2.2: don't saturate in a short) ✓
- Subharmonic minimum (Eq. 9): 0.34 × 5 / 0.993 MHz = 1.71 µH; TI asks 2× = 3.4 µH. 3.3 µH is TI's own table value for 5 V / 1 MHz (nominal 3 % under) ✓
- Copper loss at 2 A: 4 × 0.038 = 0.15 W.

**Capacitors, DC bias** (maker curves, typical):
| Cap | Nominal | Bias | Effective |
|---|---|---|---|
| C3216X7R1H475K160AE | 4.7 µF | 14.6 V | ≈ 3.3 µF each (TDK product page graph, read by eye) → 6.6 µF |
| GRM31CZ71C226ME15L | 22 µF | 5 V | ≈ −27 % → 16 µF each (Murata characteristic data; 0.5 Vrms) → 32 µF, ≈ 28 µF at small ripple ⚠️ |

- COUT rated 44 µF matches table 8-2 (44 µF rated for 1 MHz / 5 V; TI assumed 16 V X7R) ✓
- Output ripple (Eq. 10): ΔI / (8 f C) = 1.0 / (8 × 993k × 28 µF) = **4.5 mV** + ESR ≈ 1 mV ✓
- Input ripple (Eq. 11), 10 V, 3 A: 0.25 × 3 / (6.6 µF × 993k) = 114 mV ✓. RMS ≈ 1.5 A, shared by two 1206 ✓

**EN:** leakage ≤ 665 nA × 100 kΩ = 67 mV < 0.9 V ✓. REG1 load 33 µA ✓. The external resistor is needed: REG1 is only ≈ 10 MΩ to VSS in SHUTDOWN (BQ §12.3.2), and 665 nA × 10 MΩ would enable the buck.

**FB divider (only if the adjustable mode is used instead):** R_T 100 kΩ, R_B = 100k × 1/(5 − 1) = 25 k → **24.9 kΩ** → VOUT = 1.00 × (1 + 100/24.9) = **5.016 V**. Fixed mode needs no divider and draws less.

**Output accuracy:** 4.90–5.075 V (fixed 5 V, FPWM) ✓ R5. LDO abs max 6 V: 5.075 V + transient ✓.

**Load budget and margin:**
| Load on 5 V | Typical [A] | Peak [A] |
|---|---|---|
| LED board (J5, firmware cap 5 W / 10 W) | 1.0 | 2.0 |
| 3.3 V via the LDO (ESP32 + logic) | 0.13 | 0.37 |
| Shunt, translator, buffers, relay pulses | 0.06 | 0.08 |
| **Total** | **≈ 1.2** | **≈ 2.45** |
Rated 3 A: **margin 0.55 A (18 % of rating) at the peak**, 60 % typical. The LED eFuse limits at ≤ 2.78 A, so even a shorted LED cable keeps the total under the 3.4 A minimum valley limit ([led-link.md](led-link.md)).

**Input current:** 3 A out → 15/(0.93 × 10 V) = 1.6 A from B+. With the worst GV14 pick-up (5.2 A cold at 14.6 V, 75 ms; review m14) the 5 A ATM sees ≈ 6.5 A for 75 ms (130 %) ✓.

**Thermal at 3 A continuous** (typical efficiency curves §8.2.3, 12 V in, 5 V out, TI circuit): ≈ 94.5 % at 400 kHz (Fig. 8-9), ≈ 92 % at 2 MHz (Fig. 8-7); ≈ 93 % assumed at 1 MHz ⚠️.
- Total loss 15 W × (1/0.93 − 1) = 1.1 W; inductor copper 9 × 0.038 = 0.34 W; **IC ≈ 0.75 W**.
- At 60 °C board air: θJA 55 °C/W (assumed 4-layer board) → **≈ 101 °C** ✓; JEDEC 84.5 °C/W → 123 °C ✓ (limit 150 °C). TI shows the 4 A sister part at 3 A to 125 °C ambient on its EVM (Fig. 8-13).
- Option not taken: 400 kHz (RT 86.6 k, L 8.2 µH, COUT 54 µF) saves ≈ 0.25 W but needs a bigger inductor. Switch if the bench runs hot.

## 6. Fallback: TPS62933DRLR (SOT-583, `Package_TO_SOT_SMD:SOT-583-8`)
| Item | Value |
|---|---|
| Datasheet | SLUSEA4D (rev. Aug 2022), ACTIVE |
| FB | R_T 53.6 k / R_B 10.2 k → 0.8 × (1 + 53.6/10.2) = **5.004 V** (§10.2.2.2) |
| L | 6.8 µH at 500 kHz (RT open); ΔI = 0.97 A; Isat ≥ 5.8 A (SRP5030TA-6R8M class ⚠️ not audited) |
| C | CIN 2 × 4.7 µF + 100 nF; COUT 2 × 22 µF (typ effective 20 µF, min 10 µF ✓); CBOOT 100 nF |
| SS | 33 nF → 4.8 ms (min 6.8 nF, never float) |
| EN | abs max **6 V** (REG1 3.3 V ✓); 100 k pull-down: 0.7 µA × 100 k = 70 mV ✓ |
| Gaps | shutdown 2 µA typical only; VIN abs 32 V (✓ vs 24.4 V clamp) |

## 7. Absolute maximum vs worst case (LMR60430)
| Pin | Abs max | Worst case | |
|---|---|---|---|
| VIN | 42 V | 24.4 V (TVS at 16 A) | ✓ |
| EN | 42 V | 3.3 V (REG1) | ✓ |
| FB | 20 V | 5.1 V | ✓ |
| BOOT−SW | 5.5 V | internal | ✓ |
| MODE/SYNC, RT | 42 V (rec. 5.5 V) | 0 / bias | ✓ |

## 8. Layout (§8.4) → placement rules
- CIN_HF then CIN directly across pins 1–2, shortest loop; solid ground plane on layer 2.
- CBOOT short and wide at pins 3–4. SW copper small.
- FB trace from COUT, away from SW and L1.
- Wide VIN/VOUT/GND, thermal vias into inner planes. TI asks 1–2 oz outer copper ⚠️ check the stack-up.

## 9. Open
- ⚠️ Draw and check the RAK0009A footprint (gate item).
- ⚠️ Bench: case temperature at 3 A continuous in the closed box; copper per §8 (thermal vias, 1 oz outer minimum).
- ⚠️ Shutdown max is specified at 25 °C only.
- Price: not recorded (public repo).
Buy: ti.com / DigiKey by MPN.
