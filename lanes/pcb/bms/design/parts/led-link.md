# J5 LED link: TI TPS259530DSGR eFuse (5 V switch) + SN74LV1T34 data buffer

**Load:** ≈ 287 WS2812-protocol RGB pixels, firmware cap 5 W typical / 10 W peak (**2 A**), ≈ 310 mm cable.

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | High-side switch, ≥ 2.5 A, low R_on, off by default, GPIO | team lead; intent J5 |
| R2 | ≈ 0 current when off | |
| R3 | A shorted LED cable must not collapse the board's 5 V rail | design (ESP32 hangs off it) |
| R4 | Controlled inrush into the LED board's capacitance ⚠️ unknown | |
| R5 | DATA 3.3 → 5 V (LED V_IH ≈ 0.7 × 5 = 3.5 V), no back-feed into unpowered LEDs | WS2812 class |

## 2. Switch candidates
| Part | I [A] | R_on max (85 °C) [mΩ] | Current limit | Soft start | Package | Stock | Verdict |
|---|---|---|---|---|---|---|---|
| **TPS259530DSGR** | 4 | 47 | **adjustable ±7.5 %**, 5.7 V OV clamp, latch-off + FLT | dVdt cap | WSON-8 2 × 2 | in stock | **✓** R1–R4 |
| TPS259531DSGR | 4 | 47 | same, auto-retry | dVdt | WSON-8 | not checked | retries into a short; latch-off is easier to diagnose |
| TPS22810DBVR | 3 | not compared | none | CT pin | SOT-23-6 | not stocked | ✗ R3 |
| TPS22975DSGR | 6 | low | none | CT | WSON | not stocked | ✗ R3 |
| P-FET + NPN | — | — | none | RC | — | — | ✗ R3, more parts |

## 3. Identity
| Item | Value |
|---|---|
| Datasheet | SLVSE57C (rev. Apr 2018) |
| Lifecycle | Active (DigiKey API) ⚠️ ti.com page not checked for this part |
| Footprint | `Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias` |
| Pins | 1 dVdt, 2 EN/UVLO, 3+4 IN, 5 OUT, 6 FLT, 7 ILM, 8 + pad GND |
| Abs max | IN 20 V, OUT −0.3…V_IN + 0.3 (−1.2 V < 1 µs), EN 7 V (rec ≤ 6), FLT 7 V |
| Off current | 0.04 µA typ at ≤ 5 V (irrelevant in sleep: 5 V is off) |

## 4. Externals and calculations
| Ref | Value | Calculation |
|---|---|---|
| R_ILM | **787 Ω 1 %** | I_LIM = 2000/787 + 0.04 = **2.58 A** (±7.5 % → 2.39–2.78 A). Min 2.39 > 2 A LED peak ✓. Max 2.78 + 0.45 A board = 3.23 A < buck valley limit min 3.4 A ✓ R3 |
| C_dVdt | **47 nF** | SR = 42000/47000 = 0.89 V/ms → ≈ 5.6 ms to 5 V; inrush ≈ 0.45 A per 500 µF of LED-board capacitance ✓ R4 (datasheet Eq. 2–3; ≥ 3300 pF) |
| R_EN | GPIO `LED_EN` with 100 kΩ to GND | off by default; thresholds 1.13–1.27 V ✓ |
| FLT | GPIO with pull-up (open drain, low = fault) | self-test input; clear by toggling EN |
| ILM sense | optional: V_ILM = I × 276 µA/A × 787 Ω = **0.43 V at 2 A** | LED current telemetry if an ADC channel is free; else leave unconnected to the ADC |
| C_IN | GRM31CZ71C226ME15L 22 µF + 100 nF | |
| C_OUT | GRM31CZ71C226ME15L 22 µF at J5 | |
| D_OUT | **SS14-E3/61T** Schottky, OUT → GND (cathode OUT), `Diode_SMD:D_SMA` | datasheet §10.1: absorbs the negative spike from cable inductance on a short |

Loss at 2 A: 4 × 0.047 = 0.19 W; θJA 65.6 °C/W → +12 K ✓. Drop at J5: 2 A × 47 mΩ = 94 mV + 22 AWG round trip (≈ 33 mΩ) ≈ 66 mV → ≈ 4.75 V at the LED board with a 4.90 V rail ✓.

## 5. Data buffer
| Option | Verdict |
|---|---|
| **SN74LV1T34DBVR powered from the switched LED 5 V** | **✓** same MPN as the GV14 buffers; output dies with the LEDs, so DATA can't back-power them; input tolerates 3.3 V with V_CC = 0 (V_I abs 7 V, independent of V_CC) |
| Same buffer on the main 5 V | ✗ holds or drives DIN into unpowered LEDs unless firmware always parks it low |
| 74AHCT1G125 | same function with an OE pin we don't need; second MPN |
| No buffer (3.3 V direct) | ✗ R5 |

Circuit: ESP32 `LED_DATA` (100 k to GND) → A; Y → **100 Ω** → J5 pin 2; TPD1E10B09 from the J5 pin to GND ([esd.md](esd.md)); 100 nF on V_CC.
- V_IH 2.03 V at 5 V vs ESP32 ≥ 2.64 V ✓; V_OH ≥ V_CC − 0.1 at light load ✓ R5.
- Series R: source termination ≈ Z0 (≈ 100 Ω twisted ⚠️) − driver ≈ 40 Ω; 100 Ω also limits ESD current; τ ≈ 150 Ω × 100 pF = 15 ns ≪ 350 ns bit pulse ✓. ⚠️ Check edges at the first pixel; 68–220 Ω is the tuning range.
- Cable: DATA twisted with GND.
Firmware: set LED_EN, wait ≥ 10 ms, then send data; drive LED_DATA low before disabling.

## 6. J5 connector
1×3 Micro-Fit (5V switched, DATA, GND), 20–22 AWG: 2 A ✓ ([connectors.md](connectors.md)).

## 7. Open
- ⚠️ LED-board capacitance (LED-board phase) → recheck C_dVdt.
- ⚠️ LED-board V_IH of the chosen LED (Würth/Inolux audit).
