# Input protection on B+ and LOAD+: 2 × Vishay SMAJ15A, ceramic caps only, no reverse-polarity FET

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Stand off ≥ 15 V; start conducting below the 20 V design abs max | team lead; intent §2 |
| R2 | Clamp below every downstream absolute maximum | |
| R3 | Handle J3 hot-plug and load-bus switching spikes ⚠️ (amplitude unmeasured) | intent §2 |
| R4 | Fit the ≤ 10 µA sleep budget | intent §4 |

## 2. TVS candidates (Vishay doc 88390, 09-Jan-2024; 400 W, 10/1000 µs)
| Part | V_WM | V_BR @ 1 mA | V_C @ I_PP | I_R @ V_WM | Verdict |
|---|---|---|---|---|---|
| **SMAJ15A** | 15 V | 16.7–18.5 V | **24.4 V @ 16.4 A** | 1 µA | **✓** lowest clamp that meets R1; keeps precharge V_GS ≤ 20 V at full surge |
| SMAJ16A | 16 V | 17.8–19.7 V | 26.0 V @ 15.4 A | 1 µA | more leakage margin, but V_GS reaches 21.2 V at full surge |
| SMAJ18A (sizing list) | 18 V | 20.0–22.1 V | 29.2 V @ 13.7 A | 1 µA | ✗ starts above 20 V |
| SMBJ15A (600 W) | 15 V | — | — | — | not needed ⚠️ revisit after measuring spikes |

- V_BR at −10 °C: 16.7 × (1 − 0.00088 × 35) = **16.2 V > 14.6 V** ✓.
- Margin to the 14.6 V pack maximum is small (0.4 V below V_WM): leakage is specified at 15 V, so it's inside the rating.
- No snap-back device (the buck datasheets forbid it): SMAJ is avalanche ✓.

## 3. Identity
| Item | Value |
|---|---|
| MPN | SMAJ15A-E3/61 (unidirectional), qty 2 |
| Datasheet | `SMAJ15A-E3.pdf` |
| Lifecycle | Active (DigiKey API) ⚠️ Vishay page gave no status text |
| Stock | in stock |
| Footprint | `Diode_SMD:D_SMA` (DO-214AC), cathode to the rail |
| Second sources | Littelfuse, Bourns, Diodes SMAJ15A ✓ multi-source |

## 4. Clamp vs downstream abs max (24.4 V worst)
| Part on the rail | Abs max | |
|---|---|---|
| LMR60430 VIN | 42 V | ✓ |
| C 50 V X7R | 50 V | ✓ |
| BQ76952 BAT / PACK (via R) | 85 V | ✓ |
| SI2319DDS V_DS / V_GS | 40 / 20 V (19.9 V) | ✓ |
| MMBT3904 V_CE | 40 V | ✓ |
| BSZ146N10LS5 (via GV14 coil + 55 V kick) | 100 V (≈ 80 V) | ✓ |
| DMN61D8L | 60 V | ✓ |
| BAS116 (LED blockers) | 75 V | ✓ |
| B+/LOAD+ dividers (pcb) | check resistor voltage ratings | ⚠️ |

## 5. Reverse polarity: no series part
- J3 is a keyed Micro-Fit with a vendor-built, tested harness; at the copper end B+ is an M6 ring under the Z-strap foot and GND an M8 ring at node A: different ring sizes (signal-wiring.md).
- If B+/GND were swapped anyway, the B+ TVS conducts forward and the 5 A ATM should open (SMAJ surge 40 A, 8.3 ms: ⚠️ the TVS may fail first, shorted). The buck (VIN min −0.3 V) is **not** guaranteed to survive. Accepted risk ⚠️.
- LOAD+ and GND rings are both M8: swapping them puts LOAD+ on board ground and the board doesn't power; no reverse voltage. Label both.
- A series ideal-diode FET would add parts and voltage drop in the 3.9 A pick-up path for an assembly error only.

## 6. Capacitance
- B+: only the buck input MLCCs (2 × 4.7 µF + 100 nF) and BQ's own filter. **No electrolytic or polymer bulk cap**: its leakage (typically several µA ⚠️) would break R4.
- Hot-plug: L ≈ 0.5 µH ⚠️, C ≈ 6.6 µF effective, R ≈ 0.1 Ω → ring to ≈ 23 V, undamped limit 29 V; the TVS clamps it near 20 V; 50 V caps ✓.
- LOAD+: no capacitor on the board (the load bus has the inverter's).

## 7. Layout
TVS directly at J3 pins, short fat return to the ground plane, before any branch.

## 8. Open
- ⚠️ Scope LOAD+ during inverter start and charger relay switching.
- ⚠️ If the charger fails high (> 16.2 V) with the relay closed and GV14 open, the LOAD+ TVS conducts and the 2 A tap fuse is the limit (intended: fuse opens; TVS may fail shorted).
