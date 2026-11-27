# NTCs: Murata NCU15XH103F6SRC (board), Vishay NTCLE413E2103F102L (box air, J9)

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | 10 kΩ at 25 °C, B25/85 ≈ 3435 K (same curve as the BQ's default 18 k model, Semitec 103AT class) | BQ SLUUBY2B §4 (18 k model intended for 103AT) |
| R2 | Usable on a BQ76952 TS pin if needed: V within −0.2 V … V_REG18 | SLUSE13B §7 |
| R3 | Board: small 0402, −10…+60 °C | intent §2 |
| R4 | Box air: sealed tip on a catalog lead ≈ 200 mm | intent §3 J9 |

Where they're read: per [bq76952.md](bq76952.md), the BQ takes flex NTCs 1–4; **the board NTC, flex NTC 5 and the box NTC go to ESP32 ADC1** (SPI took two TS pins).

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

## 4. Ranges (resistances: Vishay table 3 for the 3435 K curve; Murata is within its tolerance ⚠️ not re-tabulated)
| T [°C] | R [kΩ] | BQ TS pin, 18 k to 1.8 V [V] | ESP32, 10 k to 3.3 V [V] |
|---|---|---|---|
| −40 | 191 | 1.65 | 3.14 |
| −10 | 42.6 | 1.27 | 2.67 |
| 25 | 10.0 | 0.64 | 1.65 |
| 60 | 3.02 | 0.26 | 0.77 |
| 85 | 1.45 | 0.13 | 0.42 |
- BQ: 0.13–1.65 V inside −0.2 … 1.8 V ✓ R2 (internal pull-up 14.4–21.6 kΩ, factory-measured and used in the calculation).
- ESP32 (ATTEN 12 dB ⚠️ usable to ≈ 3.1 V): −10…+85 °C in range ✓; −40 °C reads at the limit.
- Self-heating on ESP32 bias: ≤ 3.3²/(4 × 10 k) = 0.27 mW → ≈ 0.1 K on the bead ✓.

## 5. Externals (each ESP32 channel)
10 kΩ 1 % (0402) from 3V3, 100 nF at the ADC pin. J9: add 1 kΩ series to the ADC pin (cable-borne ESD) ⚠️ optional.

## 6. Open
- ⚠️ Harness: AWG30 PVC lead in a Micro-Fit needs 43030-0010 (26–30 AWG); ask the vendor, or use a splice to 24 AWG.
- ⚠️ Flex NTCs (main flex design) should use the same curve.
