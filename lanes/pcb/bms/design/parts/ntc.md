# NTCs: Murata NCU15XH103F6SRC (board), Vishay NTCLE413E2103F102L (box air, J9)

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | 10 kΩ at 25 °C, B25/85 ≈ 3435 K (same curve as the BQ's default 18 k model, Semitec 103AT class) | BQ SLUUBY2B §4 (18 k model intended for 103AT) |
| R2 | Usable on a BQ76952 TS pin if needed: V within −0.2 V … V_REG18 | SLUSE13B §7 |
| R3 | Board: small 0402, −10…+60 °C | intent §2 |
| R4 | Box air: sealed tip on a catalog lead ≈ 200 mm | intent §3 J9 |

Where they're read: per [bq76952.md](bq76952.md), the BQ takes **flex NTCs 1–3** (TS1, TS3, DFETOFF; DCHG became the charge gate, decision B8); **flex NTCs 4 and 5, the board NTC and the box NTC go to ESP32 ADC1** ([esp32-pinmap.md](esp32-pinmap.md)).

## 2. Candidates
| Part | Type | R / B25/85 | Verdict |
|---|---|---|---|
| **NCU15XH103F6SRC** | 0402 | 10 k ±1 % / 3434 K (B25/50 3380 K ±1 %) | **✓ board**; Active, "In Production" (murata.com) |
| NCP15XH103F03RC | 0402 | same curve | ✗ NRND |
| **NTCLE413E2103F102L** | epoxy bead, 1000 mm PVC AWG30 twin lead | 10 k ±1 % / 3435 K ±1 % | **✓ box air**; in stock; vendor cuts to length |
| NTCLE413E2103F520L / F524A | same, 52 mm | same | ✗ too short |
| NTCLE433E3103F106A | multistranded, for crimping | same | better for crimping; not stocked ⚠️ |
| Semitec 103AT-11 | resin probe, 585 mm | 10 k / 3435 | not stocked |
| Semitec 103AT-2 | 12.5 mm leads | 10 k / 3435 | ✗ no lead |
| Murata NXFT15XH103FA2B150 | lead type | 10 k / 3380 | ✗ obsolete |
| Vishay NTCLP100E3103H | probe, 375 mm | 10 k / 3977 | alternate (different curve) |

## 3. Identity
| Item | Board | Box air |
|---|---|---|
| Datasheet | Murata NCU15 series (`NCU15XH103F6SRC.pdf`) | Vishay 29078, rev. 15-Oct-2026 |
| Limits | −55…+150 °C; 100 mW max | −40…+105 °C; 100 mW at 55 °C; 500 VRMS lead-to-body; **not for water immersion** |
| Footprint | `Resistor_SMD:R_0402_1005Metric` | harness (J9, 43645-0200) |
Dissipation factor of the bead ≈ 3 mW/K (still air).

## 4. Ranges (computed with R = 10 k × exp(3435 (1/T − 1/298.15)); Murata is within its tolerance ⚠️ not re-tabulated)
ESP32 channels (flex NTC 4 and 5, board, box): **33 kΩ from 3V3** (was 15 kΩ), NTC to GND. BQ pins: internal 18 kΩ to 1.8 V with **1 kΩ in series** with the NTC.
| T [°C] | R [kΩ] | BQ TS pin incl. 1 k [V] | ESP32, 33 k [V] | ESP32 sensitivity [mV/K] |
|---|---|---|---|---|
| −20 | 77.5 | 1.46 | 2.32 | 37 |
| −10 | 46.3 | 1.30 | 1.93 | 40 |
| 0 | 28.7 | 1.11 | **1.54** | 38 |
| 2 | 26.2 | 1.08 | 1.46 | 37 |
| 25 | 10.0 | 0.68 | 0.77 | 23 |
| 45 | 4.85 | 0.44 | 0.42 | 12.5 |
| 60 | 2.98 | 0.32 | **0.27** | 7.8 |
- BQ: 0.32–1.46 V inside −0.2 … 1.8 V ✓ R2 (internal pull-up 14.4–21.6 kΩ, factory-measured and used in the calculation).
- **Why 33 k:** ESP32-S3 calibrated ADC error is ±5 mV (0 dB, 0–850 mV), ±6 mV (0–1100), ±10 mV (0–1600) and **±50 mV** at the top range (chip datasheet v2.2 Table 5-6). With 15 k the cold end needed the top range: ±50 mV ≈ ±2–4 K. With 33 k, ≥ 0 °C fits the 0–1600 mV range (±0.3 K at 2 °C, ±1.3 K at 60 °C, plus ≈ 0.6 K from the 1.5 % rail ratio). Firmware switches to the top range only above 1.6 V (below ≈ 0 °C, charging already inhibited).
- Open wire reads 3.3 V, short reads 0 V → both detectable. Self-heating ≤ 3.3²/(4 × 33 k) = 0.08 mW ✓.

### 4a. 1 kΩ series error on the BQ pins (review m8)
| True T [°C] | −20 | 1 | 25 | 45 | 53 | 60 |
|---|---|---|---|---|---|---|
| BQ reports [°C] | −20.2 | 0.2 | 22.6 | 39.6 | 45.8 | 50.9 |
| Error [K] | −0.2 | −0.8 | −2.5 | −5.4 | −7.2 | −9.1 |
Reads colder, so uncorrected over-temperature trips would be late: the OTP thresholds are entered in BQ-reported degrees ([bq76952.md](bq76952.md) §7.3) and firmware removes the 1 kΩ before display. 100 Ω would cut the error to < 1 K but let a flex fault push ≈ 120 mA into the pin: rejected.

## 5. Externals
| Channel | Bias | Series | Capacitor | Note |
|---|---|---|---|---|
| BQ TS1, TS3, DFETOFF | internal 18 k | **1 kΩ** ERJ-PA3F1001V (0603, 0.33 W: 0.15 W in a fault to 14.6 V) | **1 nF** at the pin (GRM155R71H102KA01D), < 4 nF (SLUSE13B p. 65) | τ ≈ 20 µs vs 3 ms conversion ✓ |
| ESP32: flex NTC 4, 5, box (J9), board | **33 kΩ 1 %** (RC0402FR-0733KL) at the connector-side node | **10 kΩ** (RC0402FR-0710KL) from that node to the ADC pin | 100 nF at the pin (CC0402KRX7R9BB104) | series R is after the bias node, so **no temperature error**; fault to 14.6 V: ≤ 1.1 mA into the pin clamp, 0.35 mA into 3V3. Leakage 50 nA × 10 k = 0.5 mV ✓. Used 10 k instead of the review's 1 k for that reason; the board NTC doesn't need it but keeps one circuit |

## 6. Open
- ⚠️ Harness: AWG30 PVC lead in a Micro-Fit needs 43030-0010 (26–30 AWG); ask the vendor, or use a splice to 24 AWG.
- ⚠️ Flex NTCs (main flex design) should use the same 3435 K curve; otherwise recompute §4 and the OTP temperature thresholds.
- ⚠️ BQ pin survival with ≈ 12 mA clamp current in a flex fault isn't specified.
