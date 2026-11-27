# Inverter remote (NTS-400P CN301): Panasonic AQY412S (form B) or AQY212S (form A), same footprint

**Pick:** PhotoMOS, SOP4. The board takes either; the MPN decides the default. **Recommendation for Q4: form B (AQY412S)**: the inverter stays off unless the BMS says on.

## 1. CN301 facts (MEAN WELL)
| Item | Value | Source |
|---|---|---|
| Connector | JST S2B-XH-A (mate XHP-2 + SXH-001T) | NTS-400P-SPEC 2026-03-26 |
| Logic | pins 1–2 **open = inverter on**, **short = remote off** | same |
| Drive | "dry contact … by relay" | SPEC; NTS/NTU manual Ver 12 (2026.03) |
| Open-circuit voltage / short current | **not published** ⚠️ (spec and manual searched) | — |
The PhotoMOS isolates it, so it doesn't matter which side of the shunt the inverter's DC− sits on.

## 2. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Dry contact, either polarity, isolated | MEAN WELL; intent §4 |
| R2 | Rating well above the unknown CN301 signal (assume ≤ 12 V, ≤ 10 mA ⚠️) → 60 V / 0.5 A | |
| R3 | Driven by ESP32 3.3 V | |
| R4 | Defined state with no firmware | intent §4 |

## 3. Candidates (DigiKey API 2026-11-27)
| Part | Form | V / I | R_on max | LED | Stock | Verdict |
|---|---|---|---|---|---|---|
| **AQY412S** | **B** | 60 V / 0.5 A | 2.5 Ω | 3 mA max to switch | in stock | **✓ recommended** |
| **AQY212S** | **A** | 60 V / 0.5 A | 2.5 Ω | 3 mA max | in stock | ✓ if Q4 = form A |
| TLP172AM (Toshiba) | A | 60 V / 0.5 A | 2 Ω | — | in stock | A alternate ⚠️ not audited (land pattern differs) |
| AQY412EHA(X) | B | 60 V / 0.55 A | 2.5 Ω | — | tape in stock | DIP4-SMD, larger |
| CPC1017N / CPC1117N | A / B | 60 V | 16 Ω | — | **obsolete** | ✗ |
| Signal relay | A or B | — | — | coil ≥ 100 mW | — | ✗ size, power |

## 4. Form A vs B (Q4)
| State | Form B (AQY412S) | Form A (AQY212S) |
|---|---|---|
| BMS asleep / unpowered / in reset | contact **closed** → inverter off | open → inverter "on" (it has no DC while the GV14 is open) |
| Welded contactor + dead BMS | inverter held off ✓ | inverter runs ✗ |
| Current while inverter on | ≈ 7 mA from 3V3 | 0 |
| Fails open (part fault) | inverter on | inverter on |
| Sleep current | 0 | 0 |

## 5. Identity
| Item | Value |
|---|---|
| Datasheets | AQY212S: Panasonic ASCTB464E 202601; AQY412S: ASCTB140E 202601 |
| Lifecycle | Active (DigiKey API) ⚠️ Panasonic status page not checked |
| Abs max | I_F 50 mA, V_R 5 V, load 60 V, 0.5 A, T_op −40…+85 °C |
| Recommended | **I_F 5–30 mA**, load ≤ 48 V |
| Footprint | ⚠️ custom: Panasonic pad 0.8 × 1.2 mm, pitch 2.54, row spacing 6.0 mm (package 4.3 × 4.4 × 2.1, lead span 6.8). KiCad `Package_SO:SOP-4_3.8x4.1mm_P2.54mm` is narrower (row 5.5) |
| Pins | 1 LED anode, 2 cathode, 3–4 contact |

## 6. Calculation
R = **270 Ω**, GPIO 3.3 V: I_F typ (3.25 − 1.2)/270 = 7.6 mA; min (3.1 − 1.5)/270 = **5.9 mA ≥ 5 mA** ✓; max (3.35 − 1.0)/270 = 8.7 mA ✓. Resistor 20 mW ✓. Off leakage ≤ 1 µA ✓.

## 7. Externals
- 270 Ω (0402) from the GPIO; 100 kΩ GPIO → GND (LED off in reset).
- Indicator LED + R in parallel from the same GPIO (not in series: no headroom on 3.3 V).
- TP across the contact (J7 side) and on the GPIO.

## 8. Open
- ⚠️ Q4 (Chris).
- ⚠️ Bench: measure CN301 open voltage and short current before first connection.
