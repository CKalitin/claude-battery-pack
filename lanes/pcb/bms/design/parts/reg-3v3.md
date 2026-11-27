# 3.3 V regulator (5 V → 3.3 V): TI TLV1117LV33DCYR (LDO)

**Pick:** 1 A LDO in SOT-223. Two capacitors, no inductor, and it stays below T_J 125 °C even at 500 mA continuous.

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | ≥ 500 mA supply (ESP32 I_VDD min 0.5 A; TX peak 355 mA) | ESP32-S3-WROOM-1/1U datasheet v1.8, §6 |
| R2 | 3.0–3.6 V (ESP32 abs max 3.6 V) | same |
| R3 | Input 4.88–5.08 V from the buck through the TPS2116 mux, or ≈ 4.7–5.25 V from USB ([usb-c.md](usb-c.md)) | |
| R4 | T_J ≤ 125 °C at 60 °C board air | intent §2 |
Load: ESP32 ≈ 100 mA average, 355 mA peak; others ≈ 15 mA.

## 2. Candidates
P = (5.0 − 3.3) × I: **0.20 W** at 115 mA avg, **0.63 W** at 370 mA peak, **0.85 W** at 500 mA.
| Part | I [A] | Package, θJA [°C/W] (JEDEC) | T_J at 0.85 W, 60 °C | Dropout max | Stock | Verdict |
|---|---|---|---|---|---|---|
| **TLV1117LV33DCYR** | 1 | SOT-223, 62.9 | **113 °C** | 700 mV @ 1 A | in stock | **✓** |
| TLV75733P (DRV / DBV) | 1 | WSON 2 × 2, 100 / SOT-23-5, 231 | 145 / 256 °C | 425 mV | not stocked | ✗ thermal, stock |
| AP7361C-33E | 1 | SOT-223, 110 | 154 °C | 360 mV typ | not stocked | ✗ |
| AP2112K-3.3 | 0.6 | SOT-23-5 (not audited) | — ⚠️ | — | in stock | ✗ small package for 0.85 W; datasheet not opened |
| TLV62569 buck | 2 | SOT-23-6 | low loss (≈ 0.15 W) | — | in stock | ✗ adds inductor + divider and a second switcher to save ≈ 0.7 W on a 2.7 kWh pack |

## 3. Identity
| Item | Value |
|---|---|
| Datasheet | SBVS160C (May 2011, rev. Jan 2023), `TLV1117LV33DCYR.pdf` |
| Lifecycle | ACTIVE (ti.com part-details, 2026-11-27) |
| Footprint | `Package_TO_SOT_SMD:SOT-223-3_TabPin2`: 1 GND, 2 OUT (tab), 3 IN. **The tab is OUT**, not ground |

## 4. Externals
| Ref | Part | Note |
|---|---|---|
| C_IN | GRM31CZ71C226ME15L, 22 µF 16 V (same MPN as the buck output) | ≥ 1 µF required |
| C_OUT | GRM31CZ71C226ME15L | ≥ 1 µF; the ESP32 module also needs 10 µF + 100 nF at its pins |

## 5. Checks
- Abs max VIN 6 V (rec. 5.5 V) vs 5.075 V ✓. ⚠️ Anything that back-feeds 5 V above 5.5 V (bench supply) breaks it; label the test point.
- Output ±1.5 % → 3.25–3.35 V ✓ R2.
- Headroom 4.90 − 3.35 = 1.55 V > 0.7 V ✓. Current limit ≥ 1.1 A ✓ R1.
- Thermal: 0.85 W × 62.9 = +53 K → 113 °C ✓; average 0.2 W → +13 K.
- IQ ≤ 100 µA: irrelevant in sleep (its input is off).

## 6. Layout
Tab copper is the 3V3 net: give it a pour (it is also the heatsink). Caps at pins 3–2 and 1.

## 7. Open
- None blocking. If area gets tight, a 2 × 2 mm buck is the fallback.
