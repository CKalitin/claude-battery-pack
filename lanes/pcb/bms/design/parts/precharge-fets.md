# Precharge switch: 2 × Vishay SI2319DDS-T1-GE3 + 2 × onsemi MMBT3904LT1G

**Pick:** two 40 V P-FETs in series, same orientation (Chris, 2026-11-27), each with its own NPN gate puller and its own ESP32 line. Gate ratio 100 k / **27 k**, plus 1 nF across each gate-source. **Channel 2 is AC-coupled** (diode pump, §5a): it conducts only while its GPIO toggles = hardware time limit (decision B10, review M3). Alternate FET: Panjit PJA3441 (§2a).

```
B+ ─┬─ S Q1 D ─┬─ S Q2 D ── AC05 10 Ω ── LOAD+
    │          │
   100k∥1nF   100k∥1nF            (each gate-source)
    G1─27k─C(T1)  G2─27k─C(T2)    E = GND
    PRE_EN1 ─10k─ B(T1) ─100k─ GND
    PRE_PUMP ─1k─ 10n ─┬──|>|──┬──33k── B(T2) ─100k─ GND
                       │  D_b  │
                  GND ─|>|─┘   ├── 100n ── GND
                       D_a     └── 100k ── GND      (D_a + D_b = one BAT54S)
```

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Block B+ → LOAD+ with either FET shorted | Chris 2026-11-27; spec §4 |
| R2 | V_DS ≥ 40 V; \|V_GS\| ≤ 20 V at all inputs; ≥ ≈ 8 V on from 10 V pack | team lead; intent §2 |
| R3 | 1.46 A peak decaying (normal), 1.43 A for 0.5 s (shorted bus) | power-train.md §9 |
| R4 | Off leakage fits the ≤ 10 µA sleep budget | intent §4 |
| R5 | Off with no firmware | intent §4 |
| R6 | A control pin stuck high **or** low must end precharge within ≤ 1 s | decision B10; review M3 (20 W on the 5 W AC05) |

## 2. FET candidates (DigiKey API checked 2026-11-27)
| Part | V_DS [V] | R_DS(on) max @ −4.5 V / −10 V [mΩ] | Single-pulse P at 0.5 s (chart) | Stock | Verdict |
|---|---|---|---|---|---|
| **SI2319DDS-T1-GE3** | −40, V_GS ±20 | 100 / 75 | ≈ 2.5 W | in stock ⚠️ re-check quantity before order | **✓** |
| SI2309CDS-T1-GE3 | −60, ±20 | 450 / 345 | ≈ 1.1 W | in stock | ✗ 1.2 W conduction hot at 0.5 s: no margin |
| SI2319CDS-T1-GE3 | −40 | 77 @ −10 V | — | not stocked, NRND | ✗ |
| DMP4065S-7 (Diodes) | −40, ±20 | 80 @ −10 V (DigiKey parameters) | not checked | not stocked | second-source candidate ⚠️ not audited |
| SSM3J351R (Toshiba) | −60, +10/−20 | 134 @ −10 V (DigiKey parameters) | not checked | in stock | ⚠️ datasheet blocked (not audited) |
| AO3401A / BSS308PE class | −30 | — | — | — | ✗ voltage |

### 2a. Second source (review m12)
| Part | V_DS / V_GS | R_DS(on) max @ −4.5 V | I_DSS | V_th | Package, pinout | Verdict |
|---|---|---|---|---|---|---|
| **Panjit PJA3441** (REV.00S, Feb 2015) | −40 V / ±20 V | 108 mΩ | ≤ 1 µA at −40 V | −1.0…−2.5 V | SOT-23, 1 G 2 S 3 D (same) | **✓ drop-in alternate**, stocked. 1.43 A² × 0.108 × 1.5 = 0.33 W vs 1.25 W continuous (θJA 100 °C/W) ✓; I_S 1 A ≥ 0.26 A ✓. ⚠️ **No SOA or transient-thermal chart**: turn-on and release (≤ 5.3 W for ms) unproven on this part |
| Vishay SQ2361CEES | −60 / ±20 | 230 mΩ | ≤ 1 µA | −1.5…−2.5 | SOT-23 | ✗ gate has ESD diodes: I_GSS up to 30 mA at ±20 V, which the 100 k/27 k divider can't feed |
| Vishay SI2319CDS-T1-BE3, DMP4065S | −40 | — | — | — | — | not stocked |
| Nexperia PMV100EPAR | −60 / ±20 | — | — | ≤ 3.2 V | SOT-23 | stocked, datasheet blocked ⚠️ not audited |

**Gate puller:** MMBT3904LT1G (I_CEX ≤ **50 nA** at 30 V) beats 2N7002 (I_DSS ≤ 1 µA) and DMN61D8L (≤ 0.5 µA) on sleep leakage (R4); cost: one base resistor.

## 3. Identity
| Item | Q1, Q2 | T1, T2 |
|---|---|---|
| MPN | SI2319DDS-T1-GE3 (alt. site -BE3) | MMBT3904LT1G |
| Datasheet | Vishay 79400, Rev. B, 23-Sep-2024 | MMBT3904LT1/D Rev. 15, Sep 2026 |
| Lifecycle | Active (DigiKey API) ⚠️ Vishay page gave no status text | Active (onsemi page, DigiKey API) |
| Footprint | `Package_TO_SOT_SMD:SOT-23`, 1 G, 2 S, 3 D | SOT-23, 1 B, 2 E, 3 C |

## 4. Abs max vs worst case
| Item | Abs max | Worst case | |
|---|---|---|---|
| Q V_DS | −40 V | B+ 24.4 V (TVS) with LOAD+ 0; shared across two FETs, one alone must hold it (R1) | ✓ |
| Q V_GS | ±20 V | **19.25 V** (1 % corners) at the SMAJ15A full clamp current (16 A) | ✓ |
| Q I_D / I_DM | −2.7 A / −15 A | 1.46 A | ✓ |
| Q body diode I_S (T_A 25 °C) | −0.8 A cont. | reverse path LOAD+ → B+: charger 14.2 V, pack 10 V, two diodes ≈ 1.6 V: (14.2 − 10 − 1.6)/10 Ω = **0.26 A** (welded charger relay + GV14 open) | ✓ |
| T V_CEO | 40 V | 24.4 V | ✓ |

## 5. Calculations
**Gate drive:** V_SG = (V_S − V_CE(sat)) × 100/(100 + 27) = 0.787 × (V_S − 0.1) (V_CE(sat) at 0.12 mA ⚠️ typical). R_g was 22 k: 20.0 V at the surge corner, zero margin (review m6).
| V_B+ [V] | 10.0 | 14.6 | 20 | 24.4 | 24.4, 1 % corners |
|---|---|---|---|---|---|
| V_SG [V] | **7.8** | 11.4 | 15.7 | 19.1 | **19.25** ✓ ±20 |

**NPN saturation:** T1: I_B = (3.3 − 0.65)/10 k − 0.65/100 k = 0.26 mA. T2 (pumped): (1.94 − 0.65)/33 k − 6.5 µA ≈ 33 µA. I_C ≤ 14.6/127 k = 0.115 mA → forced β ≤ 3.5 ✓.
**Base off:** I_CEX 50 nA × 100 k = 5 mV on V_SG ✓. GPIO high-Z at reset: 100 k base pull-down holds off ✓ (R5).
**Conduction, shorted bus:** I = 14.6/(10 + 0.2) = 1.43 A. R_DS hot ≈ 1.4 × 100 mΩ = 0.14 Ω → **P = 0.29 W for 0.5 s** per FET vs ≈ 2.5 W single-pulse at 0.5 s (T_A 25 °C; derate by (150 − 60)/125 → 1.8 W) ✓.
**Normal precharge:** τ = 10 Ω × 4.7 mF ⚠️ = 47 ms; FET energy ≈ ½CV² × 0.14/10 ≈ 7 mJ ✓.
**Turn-on:** C_gs total ≈ 650 + 1000 pF; τ = (100 k ∥ 27 k) × 1.65 nF = **35 µs**; Miller Q_gd 2 nC at ≈ 0.5 mA → 4 µs. SOA: peak FET power in a resistive 10 Ω load = 14.6²/40 = 5.3 W for µs, inside the 100 µs line (datasheet p. 4) ✓.
**Hot-plug dv/dt** (B+ steps, FET must stay off): ΔV_SG ≈ ΔV × (C_rss + C_CE ≈ 47 pF)/(C_iss + 1 nF) = 14.6 × 47/1650 = **0.42 V < V_th min 1 V** ✓. Without the 1 nF it would be ≈ 1.0 V.
**Divider current on:** 14.6/127 k = 0.115 mA ✓.

### 5a. AC-coupled channel 2 (decision B10)
GPIO → 1 kΩ → 10 nF → pump (BAT54S) → 100 nF reservoir with 100 kΩ bleed → 33 kΩ → T2 base. No toggling = no charge through the 10 nF = Q2 off.

| Item | Value / MPN | Note |
|---|---|---|
| Drive | **10 kHz, 50 % square wave** on `PRE_PUMP` | from a source that **stops by itself**: RMT finite burst (≤ 50 ms, re-queued only inside the supervised 0.5 s window) or a software toggle. **Not free-running LEDC/MCPWM**: that hardware keeps toggling through a hung CPU or a logic bug and defeats the limit |
| R_s | 1 kΩ (RC0402FR-071KL) | GPIO peak ≤ 3.3 mA; τ 10 µs ≪ 50 µs half period |
| C_c | 10 nF 50 V X7R (CC0402KRX7R9BB103) | sees ≤ 3.3 V |
| D_a, D_b | onsemi **BAT54SLT1G** (Rev. 18): pin 1 anode (GND), pin 3 junction (C_c), pin 2 cathode (reservoir); `SOT-23` | V_F ≤ 0.24 V at 0.1 mA; 30 V |
| C_r / R_bleed | 100 nF (CC0402KRX7R9BB104) / 100 kΩ (RC0402FR-07100KL) | |
| R_b / R_be (T2) | **33 kΩ** (RC0402FR-0733KL) / 100 kΩ | |

**ngspice results** (generic diode and NPN models, β 40; 3.0–3.3 V drive, 8–10 nF; B+ 10 / 14.6 / 24.4 V):
| Quantity | Result |
|---|---|
| Reservoir while toggling | 1.94–2.23 V |
| Q2 on after first edge (V_SG ≥ 4 V) | ≤ 1.5 ms |
| V_SG while toggling | full (7.84 / 11.46 / 19.17 V): T2 stays saturated |
| Release after toggling stops, pin left **high** or **low** (V_SG ≤ 1 V) | **≤ 6.5 ms** ✓ R6 (≤ 1 s) |
| Pin stuck high from the start (one edge) | V_SG ≤ 10 µV: never turns on ✓ |

- Q2 passes through its linear region for a few ms at release: ≤ 14.6²/40 = 5.3 W, inside the SI2319DDS pulse curves ⚠️ bench.
- **What it doesn't cover:** firmware that keeps re-queuing bursts. A shorted 10 nF removes the AC coupling (latent): self-test step P4 ([self-test.md](self-test.md)) finds it at every boot. T1, or T2, shorted: the other channel still opens the path.
- Sleep: the pump has no B+ connection; T2 collector leakage as before.

## 6. Off leakage
Q I_DSS ≤ 1 µA at 25 °C (≤ 15 µA at 70 °C, spec at −40 V) in series; two NPN ≤ 0.1 µA. See sleep budget in [README.md](README.md).

## 7. Externals (per channel)
| Ref | Value | Package |
|---|---|---|
| R_gs | 100 kΩ 1 % | 0402 |
| C_gs | 1 nF 50 V C0G, Murata GRM1555C1H102JA01D (in stock) | 0402 |
| R_g | **27 kΩ** 1 % (CRCW040227K0FKED; ≤ 1 mW) | 0402 |
| R_b | T1: 10 kΩ; T2: 33 kΩ after the pump (§5a) | 0402 |
| R_be | 100 kΩ | 0402 |
| R_M | **22 kΩ mid node → GND** (self-test bleed; 0.66 mA when Q1 is on) | 0603 |
| Sense | `SNS_PRE` BSS138 gate sense on the mid node ([self-test.md](self-test.md)); LOAD+ via BQ PACK | no indicator LEDs (Chris, 2026-11-27) |

## 8. Rules / traps
- Q2's source is the mid node: its R_gs and C_gs go to the **mid node**, not B+.
- Q2 alone commanded on: the mid node is pulled low (22 k bleed and 127 k gate divider); nothing flows from B+. Q1 alone: mid node = B+. Firmware tests each FET with `SNS_PRE` and PACK (self-test.md).
- The two control lines are separate GPIOs without power-up high glitches or reset pull-ups: `PRE_EN1` GPIO46, `PRE_PUMP` GPIO38 ✓ (datasheet v2.2 Tables 2-1, 2-2).
- AC05 resistor sees the same current; its audit is power-train.md §9.

## 9. Open
- ⚠️ Load-bus capacitance (≤ 4.7 mF) is unmeasured; time out at 0.5 s per power-train.md §9.
- ⚠️ Bench: Q2 release waveform with the pump; PJA3441 turn-on/release if it is ever fitted.
