# Charger-relay coil driver: 2 × Diodes DMN61D8L-7 in series (ESP32 AND BQ76952 DCHG)

**Pick:** two SOT-23 N-FETs with built-in clamps in series in the J6-85 low side, each gate from its own SN74LV1T34: upper from the ESP32, lower from BQ76952 **DCHG** (hardware charge stop, decision B8, review B1). No flyback diode (TE wants fast release). The upper gate needs 10 kΩ + a BAS116 source-to-gate (§5a).

## 1. Relay facts (TE Power Relay F4, Rev. 0217, `V23134-B1052-C642.pdf`)
| Item | Value |
|---|---|
| V23134-B1052-C642 | bracket, 1 form A, **no built-in suppression**, coil code 052 |
| Coil | 12 V, 90 Ω ± 10 %, 1.6 W; operate ≤ 7.2 V, release ≥ 1.6 V (23 °C) |
| Footnote 5 | "A low resistive suppression device in parallel to the relay coil increases the release time and reduces the lifetime… higher risk of contact tack welding" |
| Load here | 20 A, 14 V DC (charger lead) |

## 2. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | Sink ≤ 0.21 A from B+ (cold coil) | calc §5 |
| R2 | Closes only if ESP32 **and** BQ DCHG agree; off with no firmware, BQ hi-Z or SHUTDOWN | decision B8; intent §4 |
| R3 | Fast release (don't slow the armature) | TE footnote 5 |
| R4 | Coil still operates at 10 V pack | |
| R5 | Leakage fits sleep budget | |

## 3. Candidates
| Option | Parts | Release | Verdict |
|---|---|---|---|
| N-FET + plain flyback diode (as briefed) | 2 | slow (L/R ring-down), TE warns | ✗ R3 |
| N-FET + diode + 15–18 V zener | 3 | fast | works, one more part |
| **DMN61D8L-7** (clamp inside) | **1** | fast: coil sees ≈ 45 V reverse | **✓** |
| ZXMS6004 (protected switch) | 1 | fast | ✗ FF not stocked; SG is SOT-223, larger; not audited |
| NUD3124 / NUD3160 | 1 | fast | ✗ obsolete, 150 mA < 207 mA |

**AND topology:** two series FETs (chosen, as for the GV14) beat one FET behind a logic AND (one short defeats both) and a high-side P-FET on coil 86 (adds an NPN, a gate network and a clamp for the negative spike; not pursued).

## 4. Identity
| Item | Value |
|---|---|
| Datasheet | DS37630 Rev. 4-2, June 2018 |
| Lifecycle | Active (DigiKey API) ⚠️ diodes.com page timed out |
| Stock | in stock |
| Footprint | `Package_TO_SOT_SMD:SOT-23`, 1 G, 2 S, 3 D |

## 5. Circuit
```
B+ ── coil 86 … 85 (J6-2, node X) ── D[Q_ESP]S ──M── D[Q_BQ]S ── GND
ESP32 CHG_RLY_EN ─┬─ A [LV1T34] Y ── 10 kΩ ──┬── G(Q_ESP)
                  └─ 100 k → GND             └──|◄── M   (BAS116: anode M, cathode gate)
BQ DCHG ──────────┬─ A [LV1T34] Y ── 100 Ω ───── G(Q_BQ)
                  └─ 100 k → GND
LV1T34 VCC = 5 V, 100 nF each
```
- **Order matters:** the ESP32 FET is on top, so a normal firmware stop turns the upper FET off first and only one clamp acts. The upper gate protection (§5a) is stressed only when DCHG trips while the ESP32 still commands on, or when the rails die.
- BQ DCHG setup: `DCHG Pin Config` = 0xAA, in OTP ([bq76952.md](bq76952.md) §7). Active-low: low or hi-Z = blocked.
- Levels: LV1T34 V_IH ≤ 2.03 V at 5 V; ESP32 ≥ 2.64 V ✓; DCHG ≈ 0.9 × REG1 ≥ 2.9 V ⚠️.
- ⚠️ **Pin plan:** GPIO39 (MTCK) has a weak pull-up (45 kΩ) after reset with the JTAG eFuse at its default (ESP32-S3 datasheet v2.2 Table 2-1, note 7). Against the 100 kΩ pull-down that gives 2.3 V ≥ V_IH: the upper FET would be on at every reset. **CHG_RLY_EN must move off GPIO39** (swap with INV_STATE on GPIO42; pcb pin plan).

### 5a. Upper gate with its source in the air
When Q_BQ is off and Q_ESP is commanded on, M rises with the coil current, far above the 5 V gate drive. DMN61D8L has 10 kΩ + zeners + 100 kΩ from the gate pin to source inside, rated V_GS ±12 V.
| Item | Value |
|---|---|
| BAS116 (anode M, cathode gate) | holds V_GS ≥ −0.9 V; reverse-biased at ≤ 4.9 V when on ✓ (5 nA) |
| 10 kΩ gate resistor (0805, RC0805FR-0710KL) | limits current from M into the buffer: (75 − 0.9 − 4.9)/10 k = **6.9 mA** < 25 mA output rating ✓; ≈ 0.5 W for the ≈ 2 ms decay ⚠️ |
| On-state V_GS | gate drive 4.9 V, source ≈ 0.4 V, divider 10 k/100 k, gate leakage ≤ 90 µA (includes the 100 kΩ) → ≥ **3.6 V** ≥ the 3 V R_DS(on) spec ✓ |
Without these two parts V_GS would reach about −55 V.

### 5b. Coil voltage and loss
- 25 °C, 14.6 V: I = 14.6/(90 + 3.6) = **0.156 A**. Cold (−10 °C, −10 % R, 70 Ω): ≈ 0.20 A < 0.37 A at 70 °C ✓ R1.
- **10 V pack, coil 60 °C** (+10 % tolerance, R ≈ 113 Ω), FETs at 2.4 Ω max × 1.4 hot each: drop 6.7 Ω × 0.083 A = 0.56 V → coil **9.4 V** ≥ hot operate ≈ 7.2 × (1 + 0.00393 × 37) = 8.2 V ✓ R4. (With 1.8 Ω max at 5 V: 0.42 V.) The coil never overlaps the GV14 pick-up (relay closes only after the GV14).
- Loss per FET ≤ 0.2² × 3.4 = 0.14 W → +44 K at 321 °C/W ⚠️ worst cold-coil corner; typical 0.04 W.

### 5c. Turn-off with two clamps
| Case | What clamps | Drain X [V] | Check |
|---|---|---|---|
| ESP32 off, DCHG high (normal stop) | Q_ESP alone | ≈ 60–75 | as the single-FET design ✓ |
| DCHG trips, ESP32 still on, or 5 V rail dies | both in series (upper follows, then both clamps) | up to ≈ 2 × clamp ≈ **120–150** ⚠️ clamp max unpublished | each FET only sees its own clamp ✓; release faster than single |
| Energy | coil ½LI² ≤ 10 mJ (L ⚠️ ≤ 0.5 H), shared | | ≤ 200 mJ per FET ✓ |
- Everything on X must stand ≈ 150 V: Q drains ✓, sense resistor 0805 150 V ([self-test.md](self-test.md)), Micro-Fit 600 V ✓, copper clearance on X **≥ 1.25 mm** ⚠️ check at layout; M ≥ 0.6 mm.
- ⚠️ Bench: X and M waveforms for both cases.

## 6. Abs max
| Item | Abs max | Worst | |
|---|---|---|---|
| V_DS per FET | 60 V min, clamps | its own clamp; 24.4 V static | ✓ |
| V_GS | ±12 V | upper: −0.9 … +4.9 (§5a); lower: 0 … 5 | ✓ |
| I_D | 0.47 A (25 °C), 0.37 A (70 °C) | 0.20 A | ✓ |
| Load dump, drain | 60 V pulse rating | TVS 24.4 V | ✓ |
| Reverse battery | −14 V, 10 min | not expected | — |

## 7. Externals
| Ref | Value | MPN | Note |
|---|---|---|---|
| Buffers (2) | SN74LV1T34DBVR + 100 nF | | inputs from ESP32 and DCHG |
| R_pd (2) | 100 kΩ buffer input → GND | RC0402FR-07100KL | off while the GPIO or DCHG floats |
| R_g upper | 10 kΩ 0805 | RC0805FR-0710KL | §5a |
| R_g lower | 100 Ω | RC0402FR-07100RL | |
| D upper | BAS116LT1G, anode M, cathode gate | | §5a |
| Self-test | `SNS_RLY` BSS138 gate sense on X ([self-test.md](self-test.md)) | | no indicator LED (Chris, 2026-11-27) |

Both gates also have the FET's internal 100 kΩ gate-source, so a dead 5 V rail leaves V_GS = 0.

## 8. Sleep leakage
Two FETs in series: I_DSS ≤ 0.5 µA at 12 V each (25 °C) → ≈ 0.1 µA typ, ≈ 0.5 µA max from B+ through the coil.

## 9. Open
- ⚠️ CHG_RLY_EN GPIO move (§5).
- ⚠️ Bench: X/M waveforms (§5c), coil inductance, DCHG behaviour ([bq76952.md](bq76952.md) §7.2).
- ⚠️ A cold coil (70 Ω) is just under the 80 Ω condition of the 200 mJ rating; margin ≈ 20×.
- AC_SENSE shares J6; it reads the battery while the relay is closed ([ad-dividers.md](ad-dividers.md)).
- Relay coil tab size and harness: docs/harnesses.md (main-battery).
- Qty of DMN61D8L-7: 4 per board (2 here, 2 inverter relay).
