# ESD on J8 (button) and J5 (LED data): TI TPD1E10B09DPYR, plus a BAS116 for the button-to-ESP32 path

The USB port has its own array: ST USBLC6-2SC6 ([usb-c.md](usb-c.md)).

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | IEC 61000-4-2 protection at the connector | intent §2 |
| R2 | Working voltage above TS2's ≈ 5 V (TS2 up to 6 V in SHUTDOWN) | SLUSE13B §7 |
| R3 | **Leakage ≪ 1 µA**: TS2 in SHUTDOWN is pulled up by only ≈ 4.6 MΩ (≈ 1 µA); more leakage pulls it low and wakes the pack, or leaves it stuck in soft SHUTDOWN | SLUSE13B §7 (R_OH) |
| R4 | LED data (3.3 V, ≤ 1 MHz): low capacitance | |

## 2. Candidates
| Part | V_RWM | Leakage max | C | Verdict |
|---|---|---|---|---|
| **TPD1E10B09DPYR** | ±9 V | **100 nA at 5 V** | 10 pF | **✓ both** (one MPN) |
| TPD1E10B06 | ±5.5 V | not checked | — | ✗ below TS2's 6 V |
| PESD12VS1UB (12 V) | 12 V | not checked ⚠️ | — | not needed |
Worst case 100 nA × 4.6 MΩ = 0.46 V drop → TS2 ≈ 4.5 V, above the 1.1 V wake threshold ✓.

## 3. Identity
| Item | Value |
|---|---|
| Datasheet | SLLSEB0E (rev. Sep 2023) |
| Lifecycle | ACTIVE (ti.com part-details, 2026-11-27) |
| Package | DPY X1SON 1.0 × 0.6 mm, `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` |
| Ratings | IEC 61000-4-2 ±20 kV contact; 4.5 A 8/20 µs; clamp ≤ 13 V at 1 A; V_BR ≥ 9.5 V |
| Stock | in stock |

## 4. Circuits
- **J8:** pin → TPD1E10B09 to GND → 1 kΩ → TS2. The resistor limits strike current into TS2 (abs max 6 V). No capacitor on TS2.
- **J5 DATA:** buffer Y → 100 Ω → pin, TPD1E10B09 at the pin ([led-link.md](led-link.md)).
- J9 and J1 NTC lines, J6 AC_SENSE: series resistors ([ntc.md](ntc.md), [ad-dividers.md](ad-dividers.md)); J2 shunt SPI: 100 Ω ([shunt-spi-translator.md](shunt-spi-translator.md)). Add the same TVS only if the bench shows a need.

## 5. Trap: the button also goes to an ESP32 GPIO
In SHUTDOWN the ESP32 is unpowered; a pin wired straight to the button node is clamped by its internal diode to the dead 3V3 rail. That holds TS2 low: **no wake, soft-SHUTDOWN stuck**.

Fix: GPIO10 with an **external 100 kΩ pull-up to 3V3** (RC0402FR-07100KL; internal pull-up disabled; review n3) → anode of **BAS116LT1G**, cathode → button node.
| State | Result |
|---|---|
| Button pressed | node 0 V; diode conducts ≈ 27 µA (was ≈ 60 µA on the internal pull-up); GPIO ≈ V_F ≈ 0.6 V at −10 °C ⚠️ (V_F ≤ 0.9 V at 1 mA; typical curve) < V_IL 0.825 V ✓ |
| Released, awake | diode reverse; GPIO high through the 100 kΩ (5 nA × 100 k = 0.5 mV) ✓ |
| SHUTDOWN, 3V3 = 0 | diode reverse, ≤ 5 nA at 25 °C ✓ R3 |
⚠️ Bench-check the low level at −10 °C. A Schottky is the wrong choice here (µA leakage). BAS116LT1G: `Package_TO_SOT_SMD:SOT-23`, **pin 1 anode, pin 3 cathode**, pin 2 NC (style 8), V_R 75 V, Active (onsemi.com), in stock, onsemi BAS116LT1/D Rev. 14.

## 6. Open
- ⚠️ pcb: BQ TS2 external network: 1 kΩ, no capacitor (above); check against TI app notes at schematic.
