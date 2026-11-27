# Shunt level translator: TI TXU0304PWR (TSSOP-14), plus the OC divider

**Pick:** TXU0304 in TSSOP-14 (3 outputs ESP32 → shunt, 1 input back). OC line: 10 k / 18 k divider.

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | NSS, SCK, MOSI 3.3 → 5 V; MISO 5 → 3.3 V; SPI mode 0, 500 kHz | tesla-shunt.md §3 |
| R2 | STM8 V_IH = 3.5 V; ESP32 pins ≤ 3.6 V | same |
| R3 | Safe when either rail is off | intent §4 |

## 2. Package candidates (DigiKey API 2026-11-27)
| Orderable | Package | Size [mm] | Stock | Verdict |
|---|---|---|---|---|
| **TXU0304PWR** | TSSOP-14 | 5 × 4.4 (6.4 with leads) | in stock | **✓** leaded, inspectable, KiCad footprint, already in the area proof |
| TXU0304RUTR | UQFN-12 | 2 × 1.7 | in stock | saves ≈ 35 mm²; keep as the area fallback |
| TXU0304BQAR | WQFN-14 | 3 × 2.5 | not stocked | ✗ |
| TXU0304DTR | X2SON-12 | 1.7 × 1 | not checked | ✗ fine pitch |
TXU0104 / TXB0104: ✗ wrong directions / auto-direction.

## 3. Identity
| Item | Value |
|---|---|
| Datasheet | SCES935A (May 2021, rev. Nov 2021) |
| Lifecycle | ACTIVE (ti.com part-details, 2026-11-27) |
| Footprint | `Package_SO:TSSOP-14_4.4x5mm_P0.65mm` |
| Supplies | V_CCA, V_CCB 1.08–5.5 V; abs max 6.5 V (§7.1) ✓ |

## 4. Pin map
| Pin | Name | Net | |
|---|---|---|---|
| 1 | VCCA | 3V3 | 100 nF |
| 2 / 13 | A1 → B1Y | NSS | **100 kΩ pull-up on A1 to 3V3** (idle high while ESP32 pins float) |
| 3 / 12 | A2 → B2Y | SCK | |
| 4 / 11 | A3 → B3Y | MOSI | |
| 5 / 10 | A4Y ← B4 | MISO | |
| 6, 9 | NC | open | |
| 7 | GND | | |
| 8 | OE | 3V3 through 10 kΩ | floating or low = all outputs Hi-Z (§9.1) |
| 14 | VCCB | 5V | 100 nF |

- Inputs have ≈ 5 MΩ internal pull-downs (§9.3.1): unused/unplugged MISO sits low. External pull-ups ≤ 1 MΩ ✓.
- V_CC < 100 mV on either side → outputs Hi-Z (R3) ✓; I_off for partial power-down ✓.

## 5. Level checks
| Path | Limit | Actual | |
|---|---|---|---|
| ESP32 → A at V_CCA 3.3 | V_T+ max 1.92 V at 3.0 V, ≈ 2.1 V at 3.6 V (interpolated) | ESP32 V_OH ≥ 2.64 V | ✓ |
| B → STM8 at V_CCB 5 | V_OH ≥ V_CCO − 0.1 (100 µA) | ≥ 4.8 V vs 3.5 V | ✓ |
| STM8 → B4 | V_T+ max 3.33 V at 5.5 V | STM8 V_OH ≈ V_DD − small ⚠️ | ✓ |
| Supply current | ≤ 2.5 µA at 25 °C | rails off in sleep | ✓ |
Layout (§12.1): 100 nF at pins 1 and 14; short, matched-enough routes (500 kHz).

## 6. OC line (shunt J1 pin 7)
**What it is** (shunt repo `schematic/connections.csv`, commit 84f7515): LM2903B-Q1 open-collector outputs wired together, with **R5 2.7 kΩ pull-up to +5 V on the module** (measured). Polarity ⚠️ unknown (the repo's netlist reconstruction doesn't explain an idle-high line): bench-check before firmware uses it.

Divider: **R_top 10 kΩ** (J2 → GPIO), **R_bot 18 kΩ** (GPIO → GND).
| Case | V at GPIO | Limit |
|---|---|---|
| High, 5.0 V rail | 5 × 18/(2.7 + 10 + 18) = **2.93 V** | ≥ V_IH 2.475 V ✓ |
| High, 4.7 V | 2.76 V ✓ | |
| Line hard-shorted to 5.3 V | 5.3 × 18/28 = 3.41 V | < 3.6 V ✓ |
| Low (open collector on) | ≈ 0.2 V | ≤ 0.825 V ✓ |
Current drawn when high: 0.16 mA ✓. Add 1 nF at the GPIO if the bench shows noise ⚠️ (leave DNP out unless needed).

**Not chosen:** a TXU channel (none spare); 10 k / 20 k (3.53 V in the short case, too close).

## 7. Open
- ⚠️ OC polarity and levels on the real module.
- ⚠️ J2 pinout and harness: tesla-shunt.md §3a (connector still unidentified).
