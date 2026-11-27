# Charger-relay coil driver: Diodes DMN61D8L-7 (N-FET with built-in clamp)

**Pick:** one SOT-23 part, no flyback diode. Its 60 V clamp releases the relay fast, which TE asks for.

## 1. Relay facts (TE Power Relay F4, Rev. 0217, `V23134-B1052-C642.pdf`)
| Item | Value |
|---|---|
| V23134-B1052-C642 | bracket, 1 form A, **no built-in suppression**, coil code 052 |
| Coil | 12 V, 90 Ω ± 10 %, 1.6 W; operate ≤ 7.2 V, release ≥ 1.6 V (23 °C) |
| Footnote 5 | "A low resistive suppression device in parallel to the relay coil increases the release time and reduces the lifetime… higher risk of contact tack welding" |
| Load here | 20 A, 14 V DC (charger lead) |

## 2. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Sink ≤ 0.21 A from B+ (cold coil) | calc §5 |
| R2 | 3.3 V logic from ESP32; off with no firmware | intent §4 |
| R3 | Fast release (don't slow the armature) | TE footnote 5 |
| R4 | Coil still operates at 10 V pack | |
| R5 | Leakage fits sleep budget | |

## 3. Candidates
| Option | Parts | Release | Verdict |
|---|---|---|---|
| N-FET + plain flyback diode (as briefed) | 2 | slow (L/R ring-down), TE warns | ✗ R3 |
| N-FET + diode + 15–18 V zener | 3 | fast | works, one more part |
| **DMN61D8L-7** (clamp inside) | **1** | fast: coil sees ≈ 45 V reverse | **✓** |
| ZXMS6004 (protected switch) | 1 | fast | ✗ FF not stocked; SG is SOT-223, larger; not audited |
| NUD3124 / NUD3160 | 1 | fast | ✗ obsolete, 150 mA < 207 mA |

## 4. Identity
| Item | Value |
|---|---|
| Datasheet | DS37630 Rev. 4-2, June 2018 |
| Lifecycle | Active (DigiKey API) ⚠️ diodes.com page timed out |
| Stock | in stock |
| Footprint | `Package_TO_SOT_SMD:SOT-23`, 1 G, 2 S, 3 D |

## 5. Calculations
- 25 °C: I = 14.6/(90 + 1.8) = **0.159 A**. Cold (−10 °C, −10 % R): R = 81 × (1 − 0.00393 × 35) = 70 Ω → **0.20 A** < 0.47 A rated ✓ R1.
- V_DS(on) at 3 V gate: 0.16 A × 2.4 Ω max = 0.38 V → coil **9.6 V** at 10 V pack ≥ 7.2 V ✓. Hot coil 60 °C: operate ≈ 7.2 × (1 + 0.00393 × 37) = 8.2 V ✓ R4.
- Loss: 0.16² × 2.4 = 61 mW → θJA 321 °C/W → +20 K ✓.
- Clamp energy: allowed E_Z 200 mJ for inductive loads ≥ 80 Ω; the coil stores ½LI² (L ⚠️ unpublished; ≤ 0.5 H → ≤ 10 mJ) ✓. ⚠️ A cold coil (70 Ω) is just under the 80 Ω rating condition; the energy margin is ≈ 20×.
- Gate: V_GS ±12 V; V_th 1.3–2.0 V; R_DS(on) specified at 3 V ✓ (ESP32 V_OH ≈ 3.3 V at light load). The part has gate leakage ≤ 60 µA at 3 V (internal ESD structure) ✓ GPIO.

## 6. Abs max
| Item | Abs max | Worst | |
|---|---|---|---|
| V_DS | 60 V (clamps; BV_DSS ≥ 60 V, max not given ⚠️) | 24.4 V static | ✓ |
| I_D | 0.47 A (25 °C), 0.37 A (70 °C) | 0.20 A | ✓ |
| Load dump, drain | 60 V pulse rating | TVS 24.4 V | ✓ |
| Reverse battery | −14 V, 10 min | not expected | — |

## 7. Externals
| Ref | Value | Note |
|---|---|---|
| R_pd | 100 kΩ gate → GND | off while GPIO floats (R2) |
| R_g | 100 Ω–1 kΩ optional | not required |
| Self-test | `SNS_RLY` BSS138 gate sense on the drain ([self-test.md](self-test.md)) | no indicator LED (Chris, 2026-11-27) |
| TP | gate, drain | |

## 8. Sleep leakage
I_DSS ≤ 0.5 µA at 12 V, ≤ 50 µA at 60 V (25 °C). At 14.6 V ≈ 0.5–1 µA ⚠️.

## 9. Open
- ⚠️ Bench: drain waveform at release; relay coil inductance.
- Relay coil tab size and harness: docs/harnesses.md (main-battery).
- The same MPN drives the latching inverter relay (2 more).
