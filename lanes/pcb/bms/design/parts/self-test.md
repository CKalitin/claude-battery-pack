# Firmware self-test of the switched outputs (no per-output LEDs)

**Pick:** one identical "is this node high?" sense per switched output: **BSS138 + 100 kΩ + 18 V zener gate clamp to GND**, read by an ESP32 GPIO with its internal pull-up. Digital only, **no ADC channel**, **no current from B+ in sleep** (the node only drives a gate).

```
NODE ──100k (0805)──┬── G  BSS138  D ── GPIO (internal pull-up)
                    │             S ── GND
                    └──K[18 V zener]A── GND
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
| D clamp | Diodes **MMSZ5248B-7-F**, 18 V ±5 % (cathode gate, anode GND) | `Diode_SMD:D_SOD-123` | DS18010 Rev. 28-2: 17.1–18.9 V at 7 mA; I_R ≤ **0.1 µA at 14 V**; in stock |
| R_s | 100 kΩ **0805** (RC0805FR-07100KL, 150 V) | `R_0805_2012Metric` | sees ≤ ≈ 62 V at the GV14 kick, ≈ 132 V when both relay clamps act ([charger-relay-driver.md](charger-relay-driver.md) §5c) |
| Pull-up | ESP32 internal (≈ 45 kΩ) | — | |
Drain voltage is only 3.3 V (BSS138 is 50 V).

### 3a. Gate clamp (review m5)
The old BAS116 clamp followed B+: at the TVS clamp (24.4 V) the gate saw 25.3 V on a ±20 V part.
| Clamp | Gate max | Sleep current from B+ | Detection threshold | Verdict |
|---|---|---|---|---|
| BAS116 to B+ (old) | B+ + 0.9 = 25.3 V ✗ | ≤ 5 nA | 0.85–1.5 V | ✗ |
| ±30 V sense FET, Microchip 2N7002-G (DS20005797A) | 25.3 V on ±30 ✓ | ≤ 5 nA | V_th 1.0–2.5 V | ✗ the shorted GV14 coil reads as low as ≈ 1.8 V: not guaranteed above V_th |
| **18 V zener, gate to GND** | **≤ 19.5 V** hot (18.9 V + tempco) ✓ ±20 | ≤ 0.1 µA per high node at 14 V; ⚠️ unspecified at 14.6 V and hot | BSS138 unchanged ✓ | **✓** |
| Zener or diode to 3V3 / 5 V | low | ✗ rails are 0 V in sleep: ≈ 150 µA | | ✗ |
| Resistor gate-to-source (divider) | set by ratio | ✗ draws from B+ in sleep | | ✗ |
Two nodes sit at B+ in sleep (X2 and the relay drain) → ≤ 0.2 µA.

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
Pulse = **50 µs** (≪ operate time: GV14 ≤ 20 ms, relay ≈ 7 ms), read at ≈ 30 µs (sense delay 100 k × ≈ 100 pF (gate + zener) ≈ 10 µs). "H" = node high = GPIO low. **Generate every pulse with the RMT peripheral, never a software delay** (a shorted coil draws ≈ 80 A; review n8).

**Driving the BQ side** (OTP configures DDSG and DCHG from boot): in CONFIG_UPDATE write the pin config to GPO, `0x29` (RAM only), exit, use `DDSG_LO/HI`, `DCHG_LO/HI` (TRM p. 58); afterwards write `0xAA` back and read it. A reset restores OTP. ⚠️ Bench-check that CONFIG_UPDATE and the GPO writes behave as described.

### GV14 (Q_ESP from the ESP32, Q_BQ from DDSG)
| Step | Command | Expect | Fault if not |
|---|---|---|---|
| G0 | both off (DDSG as GPO, low) | H | node low: coil open, or both FETs shorted (then LOAD+ = B+ with precharge off) |
| G1 | Q_ESP on only | stays H | **Q_BQ shorted** |
| G2 | `DDSG_HI`; Q_BQ on only | stays H | **Q_ESP shorted** |
| G3 | pulse both | **L during the pulse** | H during pulse: **shorted coil** (X2 ≈ 0.3 × B+ ≈ 3–4 V) or a FET stuck open → don't close |
| G4 | 1 ms after the pulse | H | L: **open coil** (nothing recharges X2) |

### Charger relay (Q_ESP from the ESP32, Q_BQ from DCHG)
| Step | Command | Expect | Fault if not |
|---|---|---|---|
| C0 | both off (DCHG as GPO, low) | H | node low: coil open, or both FETs shorted (shows as charge current with the command off) |
| C1 | Q_ESP on only | stays H | **Q_BQ shorted** |
| C2 | `DCHG_HI`; Q_BQ on only | stays H | **Q_ESP shorted** |
| C3 | DCHG high, pulse CHG_RLY_EN | L during | H: shorted coil (FETs saturate ≈ 0.8 A for 50 µs ✓) or a FET open |
| C4 | 1 ms after | H | L: open coil |

### Precharge (contactor open, LOAD+ discharged first: check PACK)
| Step | Command | M (`SNS_PRE`) | LOAD+ (BQ PACK) | Fault if not |
|---|---|---|---|---|
| P0 | both off | L | stays low | M high: **Q1 shorted**; LOAD+ rising: both shorted (or GV14 welded) |
| P1 | Q1 only | H | stays low | M low: **Q1 open**; LOAD+ rising: **Q2 shorted** |
| P2 | Q2 only (`PRE_PUMP` toggling; read after ≥ 10 ms) | L | stays low | LOAD+ rising: Q1 shorted |
| P4 | Q1 on, `PRE_PUMP` held **static high** 50 ms, then static low (run **before** P3) | H | stays low | LOAD+ rising: the AC coupling is broken (10 nF or pump shorted) or Q2 shorted → abort |
| P3 | Q1 on and `PRE_PUMP` toggling | H | rises to ≈ B+ in ≈ 0.15 s | no rise: Q2, pump or AC05 open, or LOAD+ shorted (0.5 s timeout) |

### Others
- Inverter relay: after each 20–50 ms pulse, `INV_STATE` must match; else relay or driver fault.
- LED switch: `LED_FLT` low after enabling = short or overtemperature.

## 6. Checks
| Case | Node | vs V_th 0.85–1.5 V | |
|---|---|---|---|
| GV14 on (5.2 A × ≈ 62 mΩ) | ≈ 0.32 V | reads low ✓ | |
| Relay on, two FETs (0.16 A × 2 × 2.4 Ω max × 1.3 hot) | ≤ 1.0 V (typ ≈ 0.4 V) | ⚠️ **above V_th min** at the worst corner | pulse tests read ≈ 0 V (coil current hasn't built up in 50 µs) ✓; firmware doesn't use `SNS_RLY` as a continuous "on" confirmation |
| Shorted GV14 coil in pulse | ≈ 3–4 V (≥ 1.8 V with a long-wire short) | reads high ✓ | |
| Node high, 10 V pack | 10 V on the gate | on ✓ | |
| Gate abs ±20 V | B+ normally (≤ 14.6 V); zener limits to ≤ 19.5 V at any surge | ✓ intent §2 | |
| GV14 kick | zener current (80 − 18)/100 k = 0.62 mA ✓; relay both-clamp case (150 − 18)/100 k = 1.3 mA, 24 mW | R 0805 ✓ | |
| Sleep | zener leakage ≤ 0.1 µA per high node (14 V, 25 °C) + I_GSS | ⚠️ bench at 14.6 V, 60 °C | ✓ R3 |
| Shorted-coil pulse energy | ≈ 80 A for ≤ 50 µs through the BSZ146 (176 A pulse rating); 5 A ATM I²t ≈ 0.3 A²s ⚠️ well below melting | | |

## 7. Rules
- Restore both BQ pin configs to `0xAA` before anything may close; a failed restore is a latched fault.
- Pulses only with the contactor open and no precharge in progress.
- Precharge steps P0–P2 and P4 are valid only with LOAD+ low. A charged load bus back-feeds M through Q2's body diode, and the 22 k bleed empties it slowly (22 k × 4.7 mF ⚠️ ≈ 100 s): if PACK reads high, skip them and report "not tested".
- A failed step latches the fault and is reported over Wi-Fi; nothing closes.

## 8. Open
- ⚠️ Bench: pulse test on a real GV14 (economizer behaviour with 50 µs pulses; datasheet note 7), shorted-coil node voltage at 10 V pack (≈ 1.8 V vs V_th ≤ 1.5 V), X2 recharge time, zener leakage.
