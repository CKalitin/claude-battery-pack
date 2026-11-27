# Precharge switch: 2 × Vishay SI2319DDS-T1-GE3 + 2 × onsemi MMBT3904LT1G

**Pick:** two 40 V P-FETs in series, same orientation (Chris, 2026-11-27), each with its own NPN gate puller and its own ESP32 line. Gate ratio 100 k / 22 k, plus 1 nF across each gate-source.

```
B+ ─┬─ S Q1 D ─┬─ S Q2 D ── AC05 10 Ω ── LOAD+
    │          │
   100k∥1nF   100k∥1nF            (each gate-source)
    G1─22k─C(T1)  G2─22k─C(T2)    E = GND
    CTRL1 ─10k─ B(T1) ─100k─ GND  (same for T2, CTRL2)
```

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Block B+ → LOAD+ with either FET shorted | Chris 2026-11-27; spec §4 |
| R2 | V_DS ≥ 40 V; \|V_GS\| ≤ 20 V at all inputs; ≥ ≈ 8 V on from 10 V pack | team lead; intent §2 |
| R3 | 1.46 A peak decaying (normal), 1.43 A for 0.5 s (shorted bus) | power-train.md §9 |
| R4 | Off leakage fits the ≤ 10 µA sleep budget | intent §4 |
| R5 | Off with no firmware | intent §4 |

## 2. FET candidates (DigiKey API checked 2026-11-27)
| Part | V_DS [V] | R_DS(on) max @ −4.5 V / −10 V [mΩ] | Single-pulse P at 0.5 s (chart) | Stock | Verdict |
|---|---|---|---|---|---|
| **SI2319DDS-T1-GE3** | −40, V_GS ±20 | 100 / 75 | ≈ 2.5 W | in stock ⚠️ re-check quantity before order | **✓** |
| SI2309CDS-T1-GE3 | −60, ±20 | 450 / 345 | ≈ 1.1 W | in stock | ✗ 1.2 W conduction hot at 0.5 s: no margin |
| SI2319CDS-T1-GE3 | −40 | 77 @ −10 V | — | not stocked, NRND | ✗ |
| DMP4065S-7 (Diodes) | −40, ±20 | 80 @ −10 V (DigiKey parameters) | not checked | not stocked | second-source candidate ⚠️ not audited |
| SSM3J351R (Toshiba) | −60, +10/−20 | 134 @ −10 V (DigiKey parameters) | not checked | in stock | ⚠️ datasheet blocked (not audited) |
| AO3401A / BSS308PE class | −30 | — | — | — | ✗ voltage |

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
| Q V_GS | ±20 V | 0.82 × (24.4 − 0.1) = **19.9 V** at the SMAJ15A full clamp current (16 A) | ✓ (nil margin only at full surge) |
| Q I_D / I_DM | −2.7 A / −15 A | 1.46 A | ✓ |
| Q body diode I_S (T_A 25 °C) | −0.8 A cont. | reverse path LOAD+ → B+: charger 14.2 V, pack 10 V, two diodes ≈ 1.6 V: (14.2 − 10 − 1.6)/10 Ω = **0.26 A** (welded charger relay + GV14 open) | ✓ |
| T V_CEO | 40 V | 24.4 V | ✓ |

## 5. Calculations
**Gate drive:** V_SG = (V_S − V_CE(sat)) × 100/(100 + 22) = 0.820 × (V_S − 0.1) (V_CE(sat) at 0.12 mA ⚠️ typical)
| V_B+ [V] | 10.0 | 14.6 | 20 | 24.4 |
|---|---|---|---|---|
| V_SG [V] | **8.1** | 11.9 | 16.3 | 19.9 |

**NPN saturation:** I_B = (3.3 − 0.65)/10 k − 0.65/100 k = 0.26 mA; I_C ≤ 14.6/122 k = 0.12 mA → forced β ≈ 0.5 ✓.
**Base off:** I_CEX 50 nA × 100 k = 5 mV on V_SG ✓. GPIO high-Z at reset: 100 k base pull-down holds off ✓ (R5).
**Conduction, shorted bus:** I = 14.6/(10 + 0.2) = 1.43 A. R_DS hot ≈ 1.4 × 100 mΩ = 0.14 Ω → **P = 0.29 W for 0.5 s** per FET vs ≈ 2.5 W single-pulse at 0.5 s (T_A 25 °C; derate by (150 − 60)/125 → 1.8 W) ✓.
**Normal precharge:** τ = 10 Ω × 4.7 mF ⚠️ = 47 ms; FET energy ≈ ½CV² × 0.14/10 ≈ 7 mJ ✓.
**Turn-on:** C_gs total ≈ 650 + 1000 pF; τ = (100 k ∥ 22 k) × 1.65 nF = **30 µs**; Miller Q_gd 2 nC at ≈ 0.5 mA → 4 µs. SOA: peak FET power in a resistive 10 Ω load = 14.6²/40 = 5.3 W for µs, inside the 100 µs line (datasheet p. 4) ✓.
**Hot-plug dv/dt** (B+ steps, FET must stay off): ΔV_SG ≈ ΔV × (C_rss + C_CE ≈ 47 pF)/(C_iss + 1 nF) = 14.6 × 47/1650 = **0.42 V < V_th min 1 V** ✓. Without the 1 nF it would be ≈ 1.0 V.
**Divider current on:** 14.6/122 k = 0.12 mA ✓.

## 6. Off leakage
Q I_DSS ≤ 1 µA at 25 °C (≤ 15 µA at 70 °C, spec at −40 V) in series; two NPN ≤ 0.1 µA. See sleep budget in [README.md](README.md).

## 7. Externals (per channel)
| Ref | Value | Package |
|---|---|---|
| R_gs | 100 kΩ 1 % | 0402 |
| C_gs | 1 nF 50 V C0G, Murata GRM1555C1H102JA01D (in stock) | 0402 |
| R_g | 22 kΩ 1 % (10 mW) | 0402 |
| R_b | 10 kΩ | 0402 |
| R_be | 100 kΩ | 0402 |
| R_M | **22 kΩ mid node → GND** (self-test bleed; 0.66 mA when Q1 is on) | 0603 |
| Sense | `SNS_PRE` BSS138 gate sense on the mid node ([self-test.md](self-test.md)); LOAD+ via BQ PACK | no indicator LEDs (Chris, 2026-11-27) |
| TP | each gate, mid node, Q2 drain | |

## 8. Rules / traps
- Q2's source is the mid node: its R_gs and C_gs go to the **mid node**, not B+.
- Q2 alone commanded on: the mid node is pulled low (22 k bleed and 122 k gate divider); nothing flows from B+. Q1 alone: mid node = B+. Firmware tests each FET with `SNS_PRE` and PACK (self-test.md).
- The two control lines must be separate GPIOs without power-up high glitches ⚠️ (ESP32-S3 datasheet; pcb pin plan).
- AC05 resistor sees the same current; its audit is power-train.md §9.

## 9. Open
- ⚠️ Load-bus capacitance (≤ 4.7 mF) is unmeasured; time out at 0.5 s per power-train.md §9.
- ⚠️ Second source: audit DMP4065S-7 if SI2319DDS stock is short.
