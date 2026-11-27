# GV14 coil driver: 2 × Infineon BSZ146N10LS5 in series, each gate from its own TI SN74LV1T34

**Pick:** two 100 V N-FETs in series from J4-X2 to GND. FET A's gate comes from the ESP32 and FET B's from the BQ76952 DDSG, each through its own 3.3 V → 5 V buffer. This is the hardware AND. **No external clamp of any kind on the coil.**

## 1. Coil facts (Sensata GV14, Rev 28-Apr-2022, `GV141BAX.pdf`)
| Item | Value |
|---|---|
| Coil B | 12 V, max 16 V; pick-up max 8 V; drop-out max 0.5 V (table values) |
| Pick-up current | **3.9 A max for 75 ms**, then one coil is switched out internally: **0.23 A hold** |
| Suppression | **"Internal transient voltage suppressor… No external diodes should be added across the coil."** Coil back-EMF **55 V** ⚠️ (listed value, treated as the clamp) |
| Timing | operate ≤ 20 ms, release ≤ 12 ms |
| Note 7 | Voltage must be applied as a step (no slow ramp) → hard switching, no PWM |
| Polarity | X1 +, X2 − (red / black leads) |

**Consequence:** when the switch opens, X2 rises to **B+ + 55 V** = 69.6 V (14.6 V), 75 V at 20 V, ≈ 80 V with B+ at the 24.4 V TVS clamp. **The FETs need ≥ 100 V.** The sizing list's SMAJ24A and any drain-to-ground TVS are removed: a clamp below 55 V + B+ would override the internal suppressor and slow the release, which is what the datasheet forbids.

## 2. Topology candidates
| Option | Parts | One FET shorted | Verdict |
|---|---|---|---|
| Two series FETs, gates driven straight from 3.3 V | 2 | other still controls | ✗ no stocked 100 V FET found with R_DS(on) guaranteed at ≤ 3.3 V (upper FET only gets ≈ 3 V) |
| 5 V AND gate + one 100 V FET | 2 | **coil stays on** | ✗ one short defeats both signals |
| **Two series FETs, one 5 V buffer each** | 4 | other still controls | **✓** |
| One AND gate + two series FETs on the same output | 3 | still one point of failure at the gate | ✗ |
| Cascode: two 30 V FETs + one 100 V FET with gate at 5 V | 3 | 100 V FET short exposes the others to 80 V | ✗ mid-node transient needs analysis |
| P-FET on X1 + N-FET on X2 | 2 + level shift | other still controls | ✗ needs a 100 V P-FET too, X1 switched |
| Smart low-side switch (40–60 V clamp) | 1–2 | — | ✗ clamp below the coil's 80 V |

## 3. FET candidates (100 V; DigiKey API 2026-11-27)
| Part | R_DS(on) max @ 4.5 V | V_th max | Package / KiCad | Stock | Verdict |
|---|---|---|---|---|---|
| **BSZ146N10LS5ATMA1** | **20.8 mΩ** | 2.3 V, plateau ≈ 3.2 V | PG-TSDSON-8 FL 3.3 × 3.3 / ⚠️ custom | in stock | **✓** |
| DMN10H170SFG-13 | 133 mΩ | 3.0 V, plateau ≈ 4.1 V | PowerDI3333-8 / `Package_TO_SOT_SMD:Diodes_PowerDI3333-8` ⚠️ | in stock | ✗ plateau too close to the 4.4 V the upper FET gets |
| SiS892ADN (Vishay) | 33 mΩ @ 10 A (DigiKey parameters) | 3.0 V | PowerPAK 1212-8 | in stock | ⚠️ alternate, datasheet not audited |
| IRLML0100 (SOT-23) | 235 mΩ | 2.5 V | SOT-23 | in stock | ✗ 3.9 A in SOT-23, I²R ≈ 5 W for 75 ms |
| SSM3K361R, DMN10H220L, DMT10H072 | — | — | — | not stocked | ✗ |

## 4. Identity
| Item | FET (×2) | Buffer (×2) |
|---|---|---|
| MPN | BSZ146N10LS5ATMA1 | SN74LV1T34DBVR |
| Datasheet | Infineon Rev. 2.3, 2021-03-17 | SCLS743E (rev. Feb 2024) |
| Lifecycle | "Active and preferred" (infineon.com, 2026-11-27) | ACTIVE (ti.com) |
| Footprint | ⚠️ custom PG-TSDSON-8 FL (Infineon land pattern) | `Package_TO_SOT_SMD:SOT-23-5`: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC |

## 5. Circuit
```
X1 (B+ from J3) ── coil ── X2 ── D[Q_BQ]S ── D[Q_ESP]S ── GND
ESP32 GPIO ─┬─ A [LV1T34 #1] Y ─100Ω─ G(Q_ESP), 100k G→GND
            └─100k→GND
BQ DDSG  ───┬─ A [LV1T34 #2] Y ─100Ω─ G(Q_BQ),  100k G→GND (to GND, not source)
            └─100k→GND
VCC = 5 V, 100 nF each
```
Q_BQ (upper) source = lower drain, ≈ 0.1 V at pick-up → V_GS ≈ 4.9 V ✓.

## 6. BQ76952 DDSG setup (SLUUBY2B §6.7, §13.3.2.17) ⚠️ pcb to confirm
`Settings:Configuration:DDSG Pin Config` = **0xAA**: PIN_FXN = 10 (alternate = DDSG), OPT5 = 1 (**active-low: DDSG low when DSG is disabled**), OPT3 = 1 (drive from REG1), OPT1 = 1 (drive high).
- Before configuration, and in SHUTDOWN, the pin is high-impedance → buffer input pulled low → coil off ✓.
- ⚠️ DDSG follows **protection faults** that would disable DSG. Whether a host FET-off command also drives it isn't stated: bench-test.

## 7. Levels, power-up and failure states
| Check | Value | |
|---|---|---|
| LV1T34 V_IH at V_CC 4.5–5 V | 2.03 V max | ESP32 V_OH ≥ 2.64 V ✓; DDSG V_OH ≈ 0.9 × REG1 ≥ 2.9 V ⚠️ (spec given at REG1 5 V) |
| Input tolerance | 7 V abs, independent of V_CC | ✓ |
| LV1T34 V_OH at 5 V, 20 µA | ≥ V_CC − 0.1 | gate ≈ 4.9 V ✓ |
| 5 V rail off | output undriven, 100 k gate pull-down | off ✓ |
| ESP32 in reset | 100 k input pull-down | off ✓ (avoid GPIOs with power-up high glitches ⚠️) |
| One FET shorted | the other signal still opens the coil | ✓ |
| One buffer stuck high | the other signal still opens | ✓ |

## 8. Electrical checks
| Item | Value | |
|---|---|---|
| V_DS 100 V vs 80 V worst | 80 % | ✓ (69.6 V = 70 % at 14.6 V) |
| V_GS ±20 V | 5.1 V max | ✓ |
| I pulse 3.9 A vs I_D 44 A | | ✓ |
| Loss at pick-up (hot R ≈ 1.5 × 20.8 mΩ) | 3.9² × 0.031 = 0.48 W per FET for 75 ms | ✓ |
| Hold loss | 0.23² × 0.031 = 1.6 mW | ✓ |
| Gate charge 9.5 nC through 100 Ω | ≈ 0.2 µs turn-on | ✓ step, no ramp |
| I_DSS ≤ 1 µA @ 100 V, 25 °C | sleep budget | ✓ |

**Pick-up voltage at the coil, pack 10.0 V** (⚠️ estimated path resistances): ATM 5 A fuse ≈ 18 mΩ, 4 Micro-Fit contacts ≤ 40 mΩ, coil leads 2 × 0.38 m 20 AWG ≈ 26 mΩ, harness 18 AWG ≈ 8 mΩ, board ≈ 20 mΩ, FETs ≤ 62 mΩ → ≈ 0.17 Ω → 0.68 V → **9.3 V ≥ 8 V** ✓. With a hot coil (+14 % at 60 °C, pick-up ≈ 9.1 V ⚠️) the margin is only 0.2 V at 10 V: firmware shouldn't close below ≈ 10.5 V.

## 9. Self-test and test points
- No indicator LED (Chris, 2026-11-27). `SNS_GV14` senses X2 (BSS138 gate sense): both-FET short, single-FET short (each tested alone), open coil and shorted coil. Procedure in [self-test.md](self-test.md).
- TP on X2, both gates, both buffer inputs.

## 10. Layout
Power loop J3 → J4 → Q_BQ → Q_ESP → GND: ≥ 2 mm traces (3.9 A pulse). Creepage on X2 ≥ 80 V: ≥ 0.6 mm to logic.

## 11. Open
- ⚠️ Draw the TSDSON-8 footprint.
- ⚠️ Bench: X2 waveform at turn-off (confirm ≤ B+ + 55 V), DDSG behaviour, pick-up at 10 V hot, 50 µs test pulses.
- ⚠️ Intent §4 says "coil kick clamped": met by the GV14's internal TVS; update wording.
