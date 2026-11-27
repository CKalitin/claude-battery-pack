# Analog inputs: AC-present sense and insulation monitor (IMD) (review M4, m13)

ADC facts: ESP32-S3 chip datasheet v2.2 (`datasheets/esp32-s3_datasheet_en.pdf`). Calibrated total error ±5 mV at 0 dB (0–850 mV), ±6 mV (0–1100), ±10 mV (0–1600), ±50 mV (0–2900), at 25 °C with 100 nF at the pin and Wi-Fi off (Tables 5-5, 5-6). Pin leakage ≤ 50 nA (Table 5-4). Pin abs max ≈ VDD + 0.3. NTC channels: [ntc.md](ntc.md).

## 1. AC_SENSE (J6-3 → GPIO2)

### Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Tell whether the charger output is live (charger side of the charger relay; CV 14.2 V) | interface §4 (NPB-360 has no AC-OK) |
| R2 | Survive the cable: ESD, a short to B+ or to the coil node next to it (≤ ≈ 150 V transient) | review M4 |
| R3 | Harmless with the ESP32 unpowered (charger live, pack off) | review M4 |
| R4 | No current from B+ in sleep | intent §4 |

### Circuit
```
J6-3 ── 100 k ── 100 k ──┬── GPIO2 (ADC1_CH1)
                         ├── 15 k ── GND
                         └── 100 nF ── GND
```
| Ref | MPN | Package | Note |
|---|---|---|---|
| R_top (2 in series) | RC0805FR-07100KL × 2 | 0805, 150 V each | two in series for voltage and ESD |
| R_bot | RC0402FR-0715KL | 0402 | |
| C | CC0402KRX7R9BB104 | 0402 | τ = (200 k ∥ 15 k) × 100 nF = 1.4 ms |

### Checks
| Case | Result | |
|---|---|---|
| Ratio | 15/215 = 0.0698: 12 V → 0.84 V, 14.2 V → **0.99 V**, 15 V → 1.05 V; ADC range 0–1100 mV (±6 mV ≈ ±0.09 V at J6) ✓ R1 | ✓ |
| Pin abs max | reached at ≈ 51 V in; 150 V transient → ≤ 0.75 mA into the clamp | ✓ R2 |
| ESD on the cable (150 pF, 8 kV ⚠️ not tested) | ≤ 40 mA for µs through 200 kΩ into the clamp / 100 nF | ⚠️ add a TPD1E10B09 only if the bench shows a need |
| ESP32 unpowered, J6-3 at 14.6 V | pin sits near a diode drop; ≈ 35 µA into the dead 3V3, ≈ 33 µA in R_bot ✓ harmless | ✓ R3 |
| Sleep | relay open: the node is the charger side, no path from B+ | ✓ R4 |

- With the relay **closed**, J6-3 is the battery bus: AC loss can't be seen here. Firmware detects it from the shunt current (no charge current) → open the relay → re-read AC_SENSE.
- With AC off and the relay open, the charger's output capacitors discharge slowly into 215 kΩ plus their own bleed ⚠️ measure the decay; threshold in firmware.

## 2. IMD (chassis → GPIO1)

### Values (intent §4, decision B7)
```
B+ ── 2.2 M ── 2.2 M ──┬── CHASSIS (J3-4 → ring lug)
                       └── 1.8 M ──┬── GPIO1 (ADC1_CH0)
                                   ├── 200 k ── GND
                                   └── 100 nF ── GND
```
| Ref | MPN (Vishay CRCW, 1 %, ±100 ppm/K) | Package | Voltage across, normal / chassis shorted to a rail |
|---|---|---|---|
| R+ (2) | CRCW08052M20FKEA | 0805 | ≈ 5 V each / ≤ 7.3 V ✓ (150 V rating) |
| R− upper | CRCW08051M80FKEA | 0805 | 3.6 V / ≤ 13.1 V ✓ |
| R sense | CRCW0805200KFKEA | 0805 | 0.46 V / ≤ 1.46 V ✓ |
| C | CC0402KRX7R9BB104 | 0402 | τ = (200 k ∥ 6.2 M) × 100 nF ≈ 19 ms ✓ |
Sleep: 14.6 V / 6.4 MΩ = **2.3 µA** (in the budget). X7R insulation resistance ⚠️ (≥ 5 GΩ class) vs 194 kΩ: negligible.

**Chassis-lead ESD (review M4):** no TVS (leakage biases the reading, [input-protection.md](input-protection.md) §4a). Add a **copper spark gap ≈ 0.3 mm from the J3-4 net to ground** at the connector (no part, no leakage; TI uses board spark gaps, SLUSE13B §18.2) and keep the chassis net ≥ 1 mm from B+/LOAD+ copper ⚠️ layout and fab clearance rules. Behind it, 1.8 MΩ limits the current into the ADC clamp to a few mA. ⚠️ Pulse behaviour of the 0805 resistors not verified.

### ADC settings and error budget (review m13)
| Setting | Value |
|---|---|
| Converter | ADC1 CH0, **0 dB** attenuation, ESP-IDF calibration (curve fitting) |
| Averaging | ≥ 64 samples spread over ≥ 20 ms (one 50 Hz or 60 Hz period) ⚠️ tune with Wi-Fi on |
| Pack voltage used for r | **sum of the four BQ cell voltages** (≈ ±20 mV), not the BQ stack reading (±0.5 V = ±0.012 in r, more than half the alarm band) |
| r | V_ADC × 2.0 M / 0.2 M / V_pack; healthy 0.3125; alarm \|r − 0.312\| > 0.02 |

| At 12.8 V | mV at the ADC node |
|---|---|
| Healthy reading | 400 (456 at 14.6 V ✓ inside 850) |
| **Alarm band** (±0.02) | **±25.6** |
| ADC calibrated error | ±5 |
| Pin leakage 50 nA max × 194 kΩ | ≤ 9.7 |
| 1 % resistors, 200 k vs 1.8 M | ≤ ±7.2 |
| 1 % resistors, R+ vs R− | ≤ ±5.5 |
| **Linear sum** | **≤ 27** ⚠️ equals the band |

So **calibrate at commissioning**: with a healthy pack store r₀ and alarm on the deviation from the stored value. The remaining drift (resistor tempco ±100 ppm/K ≈ ±1 mV over 35 K, ADC drift ⚠️ unspecified) fits the band. A chassis short to B+ clips the ADC high (1.46 V), a short to pack− reads 0: both far outside the band.

## 3. Open
- ⚠️ ADC noise and drift with Wi-Fi on and over temperature (datasheet gives 25 °C, Wi-Fi off).
- ⚠️ Recheck the fault-resistance sensitivity table of v14-design-notes §4 at the doubled values (intent §4).
- ⚠️ AC_SENSE decay and ESD on the bench.
