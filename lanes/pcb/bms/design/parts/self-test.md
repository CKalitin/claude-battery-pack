# Firmware self-test of the switched outputs (no per-output LEDs)

**Pick:** one identical "is this node high?" sense per switched output: **BSS138 + 100 kΩ + BAS116 clamp to B+**, read by an ESP32 GPIO with its internal pull-up. Digital only, **no ADC channel**, **no current from B+ in sleep** (the node only drives a gate).

```
NODE ──100k (0603)──┬── G  BSS138  D ── GPIO (internal pull-up)
                    │             S ── GND
        B+ ──K[BAS116]A──┘
GPIO LOW  = node high (> 1.5 V)      GPIO HIGH = node low (< 0.75 V)
```

No per-output LEDs, no force hooks and no test points on switched outputs (Chris): only the rail test points of intent §8 (B+, LOAD+, 5V, 3V3, REG1, GND) and the USB port's IO0/EN/GND pads.

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Detect stuck-on FET, open coil, shorted coil | team lead (Chris) |
| R2 | Cheap, digital (ADC1 is nearly full) | team lead |
| R3 | No sleep current from B+ | intent §4 |
| R4 | Node range 0 … ≈ 80 V (GV14 kick), logic ≤ 3.3 V | gv14-driver.md |

## 2. Candidates
| Sense | Sleep current from B+ | ADC | Open coil | Verdict |
|---|---|---|---|---|
| Resistor divider to GPIO/ADC | 14.6 V / R: ≥ 10 µA per node (or large leakage into the dead 3V3) | yes/no | yes | ✗ R3 |
| Diode + pull-up ("is it low?") | 0 | no | **can't see it** | ✗ R1 |
| N-FET source follower (gate at 3V3) | 0 | needs ADC | yes | ✗ R2 |
| Low-side shunt + NPN | 0 | ADC for open coil | partial | ✗ drops coil voltage |
| **Gate sense (this)** | **0** (gate leakage only) | **no** | **yes**, with a test pulse | **✓** |

## 3. Parts (per node)
| Part | MPN | Footprint | Why |
|---|---|---|---|
| Q | onsemi **BSS138LT1G** | `SOT-23` (1 G, 2 S, 3 D) | V_th **0.85–1.5 V**, V_GS ±20 V, I_GSS ≤ 0.1 µA; datasheet Rev. 15 (Sep 2026), in stock |
| D clamp | **BAS116LT1G** (anode gate, cathode B+) | `SOT-23` (pin 1 anode, pin 3 cathode) | holds gate ≤ B+ + 0.9 V; 5 nA leakage |
| R_s | 100 kΩ **0603** | `R_0603_1608Metric` | sees up to ≈ 65 V at the GV14 kick (0402 is rated 50 V) |
| Pull-up | ESP32 internal (≈ 45 kΩ) | — | |
Drain voltage is only 3.3 V (BSS138 is 50 V).

## 4. Sensed nodes and GPIOs
| Signal | Node | ESP32 GPIO | Extra parts |
|---|---|---|---|
| `SNS_GV14` | X2 (J4) | 1 digital in | 3 |
| `SNS_RLY` | charger-relay drain (J6) | 1 digital in | 3 |
| `SNS_PRE` | precharge mid node M (Q1 drain / Q2 source) | 1 digital in | 3 + **22 kΩ M → GND** (bleed) |
| LOAD+ | BQ76952 PACK pin over SPI | none | pcb (bq76952.md) |
| `INV_STATE` | latching-relay pole B | 1 digital in | 10 k (inverter-remote.md) |
| `LED_FLT` | eFuse FLT | 1 digital in | — (led-link.md) |
| `USB_ST` | TPS2116 ST | 1 digital in (optional) | — |
**Total: 5 digital inputs (+1 optional), 0 ADC.**

**Why the 22 kΩ bleed on M:** with both FETs off, Q1 leakage (≤ 15 µA at 70 °C) would float M high. 15 µA × 22 k = 0.33 V < 0.85 V ✓. When Q1 is on it draws 0.66 mA (10 mW). In sleep it carries only the leakage already in the budget.

## 5. Test procedures (run at boot, contactor open)
Pulse = **50 µs** (≪ operate time: GV14 ≤ 20 ms, relay ≈ 7 ms), read at ≈ 30 µs (sense delay 100 k × 50 pF ≈ 5 µs). "H" = node high = GPIO low.

### GV14 (Q_ESP from the ESP32, Q_BQ from DDSG)
| Step | Command | Expect | Fault if not |
|---|---|---|---|
| G0 | both off, **before** the DDSG pin is configured (Q_BQ off by default) | H | node low: coil open, or both FETs shorted (then LOAD+ = B+ with precharge off) |
| G1 | Q_ESP on only | stays H | **Q_BQ shorted** |
| G2 | configure DDSG (goes high); Q_BQ on only | stays H | **Q_ESP shorted** |
| G3 | pulse both | **L during the pulse** | H during pulse: **shorted coil** (X2 ≈ 0.3 × B+ ≈ 3–4 V) or a FET stuck open → don't close |
| G4 | 1 ms after the pulse | H | L: **open coil** (nothing recharges X2) |

### Charger relay (one FET)
| Step | Command | Expect | Fault if not |
|---|---|---|---|
| C0 | off | H | node low: FET shorted **or** coil open (same reading; both are latched faults. A shorted FET shows as charge current with the command off) |
| C1 | pulse | L during | H: shorted coil (FET saturates ≈ 0.8 A, ≈ 11 W for 50 µs ✓) or FET open |
| C2 | 1 ms after | H | L: open coil |

### Precharge (contactor open, LOAD+ discharged first: check PACK)
| Step | Command | M (`SNS_PRE`) | LOAD+ (BQ PACK) | Fault if not |
|---|---|---|---|---|
| P0 | both off | L | stays low | M high: **Q1 shorted**; LOAD+ rising: both shorted (or GV14 welded) |
| P1 | Q1 only | H | stays low | M low: **Q1 open**; LOAD+ rising: **Q2 shorted** |
| P2 | Q2 only | L | stays low | LOAD+ rising: Q1 shorted |
| P3 | both | H | rises to ≈ B+ in ≈ 0.15 s | no rise: Q2 or AC05 open, or LOAD+ shorted (0.5 s timeout) |

### Others
- Inverter relay: after each 20–50 ms pulse, `INV_STATE` must match; else relay or driver fault.
- LED switch: `LED_FLT` low after enabling = short or overtemperature.

## 6. Checks
| Case | Node | vs V_th 0.85–1.5 V | |
|---|---|---|---|
| GV14 on (3.9 A × ≈ 55 mΩ) | ≈ 0.2 V | reads low ✓ | |
| Relay on, hot (≤ 0.16 A × 3.1 Ω) | ≤ 0.5 V | below V_th min (≈ 0.75 V at 60 °C ⚠️) | ⚠️ bench |
| Shorted GV14 coil in pulse | ≈ 3–4 V (≥ 1.8 V with a long-wire short) | reads high ✓ | |
| Node high, 10 V pack | 10 V on the gate | on ✓ | |
| Gate abs ±20 V | B+ + 0.9 V: 15.5 V normal; 25 V for the µs of a 24.4 V B+ surge, through 100 kΩ ⚠️ | | |
| GV14 kick | clamp current (80 − 15)/100 k = 0.65 mA into B+ | BAS116 ✓, R 0603 ✓ | |
| Sleep | no DC path from B+; I_GSS ≤ 0.1 µA per high node | | ✓ R3 |
| Shorted-coil pulse energy | ≈ 80 A for ≤ 50 µs through the BSZ146 (176 A pulse rating); 5 A ATM I²t ≈ 0.3 A²s ⚠️ well below melting | | |

## 7. Rules
- Run G0 before configuring DDSG, or force the pin unused again (CONFIG_UPDATE) ⚠️ (bq76952.md).
- Pulses only with the contactor open and no precharge in progress.
- Precharge steps P0–P2 are valid only with LOAD+ low. A charged load bus back-feeds M through Q2's body diode, and the 22 k bleed empties it slowly (22 k × 4.7 mF ⚠️ ≈ 100 s): if PACK reads high, skip them and report "not tested".
- A failed step latches the fault and is reported over Wi-Fi; nothing closes.

## 8. Open
- ⚠️ Bench: pulse test on a real GV14 (economizer behaviour with 50 µs pulses; datasheet note 7), relay on-state margin when hot, X2 recharge time.
- ⚠️ ADC alternative not needed.
