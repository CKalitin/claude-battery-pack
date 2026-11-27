# Inverter remote (NTS-400P CN301): KEMET EE2-5TNUH-L latching relay, 2 × DMN61D8L-7

**Pick:** a double-coil latching DPDT signal relay. Pole A is the dry contact on CN301, pole B reports the state to the ESP32. **No current in either state** (Chris, 2026-11-27). PhotoMOS form A (AQY212S) is the runner-up.

## 1. CN301 facts (MEAN WELL)
| Item | Value | Source |
|---|---|---|
| Connector | JST S2B-XH-A (mate XHP-2 + SXH-001T) | NTS-400P-SPEC 2026-03-26 |
| Logic | pins 1–2 **open = inverter on**, **short = remote off** | same |
| Drive | "dry contact (by RELAY)"; no pin reference to DC−, no voltage or current ⚠️ | SPEC; NTS/NTU manual Ver 12 |
So a bare MOSFET isn't assumed to be safe; an isolated contact is.

## 2. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Isolated dry contact | MEAN WELL |
| R2 | Zero holding current to keep the inverter off | Chris 2026-11-27 |
| R3 | State readable by firmware | self-test |
| R4 | Low-level contacts (signal of unknown, probably mA) | |
| R5 | Height ≤ 12 mm | intent §6 |

## 3. Candidates (DigiKey API 2026-11-27)
| Part | Coil | Latch | Size [mm] | KiCad footprint | Min contact load | Stock | Verdict |
|---|---|---|---|---|---|---|---|
| **KEMET EE2-5TNUH-L** | 5 V, 178 Ω × 2 (28 mA) | **double coil** | 15 × 7.5 × 10.0 | `Relay_SMD:Relay_DPDT_Kemet_EE2_NUH_DoubleCoil` ✓ | 10 µA / 10 mV | in stock | **✓** |
| KEMET EC2-5TNU | same | double | 15 × 7.5 × 9.4 THT | `Relay_THT:..._EC2_NU_DoubleCoil` | same | in stock | THT alternate |
| Panasonic TQ2SA-L2-5V | 5 V, 178 Ω × 2 | double | ≈ 14 × 9 × 5.6 | none ⚠️ | 10 µA class | in stock | lower; needs a footprint |
| Omron G6KU-2F-Y DC5 | 5 V, 237 Ω × 1 | **single** coil | 10 × 6.5 × 5.2 | `Relay_SMD:..._G6K-2F-Y` | 10 µA class | in stock | ✗ needs coil polarity reversal (H-bridge) |
| Omron G6KK (double coil) | — | — | — | — | — | not in the G6K datasheet; not stocked | ✗ |
| Panasonic AQY212S PhotoMOS (form A) | LED ≈ 6 mA | none | SOP4 | custom | — | in stock | runner-up: ✗ R2 (current to hold "off"); state lost on reset |

## 4. Identity
| Item | Value |
|---|---|
| Datasheet | KEMET R7002_EC2_EE2 (2026-07-15), `EE2-5TNUH-L.pdf` |
| Contacts | AgPd/Au-clad silver; 2 A max; 1000 VAC coil–contact and pole–pole (double coil) |
| Timing | operate ≈ 2 ms; **drive pulse > 10 ms**, amplitude within ± 5 % of 5 V |
| Latch life | 1 × 10⁷ mechanical (latching) |
| Shock | 75 G misoperation |
| Lifecycle | Active (DigiKey API) ⚠️ maker page not checked |

## 5. Circuit
| Relay pin | Net |
|---|---|
| 1 (+) / 12 (−) **set** coil | 5 V / drain of Q_SET (DMN61D8L), gate ← GPIO `INV_SET`, 100 k to GND |
| 6 (+) / 7 (−) **reset** coil | 5 V / drain of Q_RST (DMN61D8L), gate ← GPIO `INV_RST`, 100 k to GND |
| 4 (COM A), 5 (NO A) | J7 pins 1, 2 (CN301) |
| 3 (NC A) | open |
| 9 (COM B) | GND |
| 8 (NO B) | GPIO `INV_STATE`, 10 k to 3V3 (low = set) |
| 10 (NC B) | open |
Pin names **confirmed** (R7002_EC2_EE2, 2026-07-15: p. 3 pin diagram, p. 9 footnote 4): set coil 1(+)/12(−), reset coil 6(+)/7(−), COM 4 and 9, NO 5 and 8 (NC 3 and 10) in the reset state. The p. 3 drawing is a **bottom view**: check the KiCad symbol (EC2-5TNU) and footprint numbering against it at schematic.

**Coil clamp:** **no external flyback diodes.** The windings are coupled, so at turn-off of one coil the **idle winding sees the induced voltage in reverse and its FET's body diode conducts** (review n1): about the same ampere-turns (≈ 28 mA) flows from GND through the idle winding back into 5 V, producing flux in the same direction. That holds the switched drain at only ≈ 11 V, below the DMN61D8L's built-in clamp. Harmless: ≤ 28 mA vs 0.5 A body-diode rating, and release speed doesn't matter on a latched contact.

## 6. States
| State | Contact A | Inverter |
|---|---|---|
| Reset (shipping state; may flip from transport shock) | open | on (when it has DC) |
| Set | closed | **off, 0 mA** |
- Firmware **initialises the relay at every boot** (KEMET and Panasonic both require it), then verifies pole B.
- The state holds through ESP32 restarts and SHUTDOWN. A BQ-forced shutdown leaves the last state; the GV14 is open then anyway.
- With no firmware the relay stays where it was (change to intent §4 "safe states": define it as "unchanged").

## 7. Checks
- Coil at 4.90 V rail: 4.90 − 0.028 × 3.1 Ω = 4.81 V (−3.8 %, inside ± 5 %) ✓; set voltage ≤ 3.75 V, ≈ 4.35 V at 60 °C ✓.
- Driver: 28 mA ≪ 0.47 A ✓; gate 3.3 V (R_DS(on) specified at 3 V) ✓.
- Pulse 20–50 ms. Never drive both coils together (firmware rule).
- A stuck-on GPIO: 140 mW continuous, +18 K coil rise: harmless.
- Idle-winding body-diode current at turn-off ≈ 28 mA, decaying (§5) ✓.
- Pole B wetting: 0.33 mA ≥ 10 µA ✓. Sleep: 3V3 and 5 V off → 0 µA ✓.
- Only needs the 5 V buck (not available on USB power alone).

## 8. Open
- ⚠️ Bench: CN301 open voltage and short current.
- ⚠️ Symbol and footprint numbering vs the bottom view at schematic (§5).
