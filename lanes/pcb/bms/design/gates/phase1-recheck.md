# BMS board: phase 1 re-check (fixes for `phase1-review.md`)

**Reviewer:** `pcb-review-parts-recheck` (independent). **Date:** 2026-11-27. **Revision:** `722dfa6`, clean tree at start. **Scope:** intent.md, decisions.md (B8–B12), parts/*.md, datasheets/. No schematic or layout exists, so copper, EMC layout, footprint geometry and silkscreen are **NOT CHECKED**.

**Verdict: not ready for the schematic until R1 and R2 are fixed.** 28 original findings: **23 CLOSED, 4 PARTLY, 0 OPEN, 1 ACCEPTED-RISK.** New: **1 BLOCKER, 1 MAJOR, 4 MINOR, 5 NOTE.** The hardware changes hold up. The blocker is two rows of the OTP register list.

Abbreviations: DS = BQ76952 SLUSE13B; TRM = SLUUBY2B (printed pages); AN = TI **SLUAA84A** "Using Low-Side FETs with the BQ769x2" (https://www.ti.com/lit/pdf/SLUAA84, not in `datasheets/`: add it and its sources.csv row).

## 1. Original findings
| # | Status | Evidence (file, section, recomputed number) |
|---|---|---|
| B1 charge stop | **PARTLY** | charger-relay-driver §5: series pair, DCHG 0xAA, flex NTC 4 on ADC, EPA 0x0C / EPB 0x73 ✓; coil at 10 V hot 9.4 V vs 8.2 V ✓. But bq76952 §7.3 rows leave DCHG unable to go high (**R1**) |
| M1 OTP | **PARTLY** | decisions B9, bq76952 §7: mandatory, thresholds recomputed ✓; register list wrong (**R1**), trial procedure flawed (**R5**) |
| M2 Vcell Mode | CLOSED | bq76952 §7.3 row 1: 0x9304 = 0x8007 = cells 1, 2, 3, 16 (TRM p. 154–155), written first |
| M3 precharge time limit | CLOSED | precharge-fets §5a. My ngspice (3.0–3.3 V, 8–10 nF, β 40–100, −10…60 °C, B+ 10/14.6/24.4 V): on ≤ 0.7 ms, release ≤ 5.5 ms stuck high or low, single edge V_SG < 2 mV. Free-running or re-queued drive stays a firmware rule |
| M4 missing externals | CLOSED | bq76952 §6, ad-dividers, ntc §5: values and MPNs; REGIN 22 nF, BREG 10 M, FCX491 pins 1 B / 2 C / 3 E match KiCad SOT-89-3; FCX, AC05 PDFs archived |
| M5 pin plan | CLOSED | esp32-pinmap: 31 of 33 used (recounted), analog on ADC1 only, no actuator on a reset pull-up (chip DS v2.2 Table 2-1: only MTCK/GPIO39, now an input) or on a glitching pin; text errors in **R7** |
| m1 UV re-close | CLOSED | intent §4 UV latch rule; ALERT carries SSA (CUV). Bench |
| m2 SLEEP | CLOSED | row 2: 0x2982 → 0x2882 clears bit 8 (TRM p. 136) |
| m3 MISO level | CLOSED | bq76952 §8: LV1T34 at 3.3 V, V_IH 1.39 V max (SCLS743E §6.5) vs REG18 1.6 V min |
| m4 REG0 default | **ACCEPTED-RISK** | decisions B12 (author's, not yet the owner's), fallback TP_REG1. The cited SLUAAQ5 §4.7 names the -**02** and says nothing of REG0; §1.1 table gives -04 "REG1 enabled 3.3 V" only |
| m5 sense gate | CLOSED | self-test §3a: 18.9 V + tempco ≈ 19.4 V on ±20 V. Leakage 0.1 µA is specified at 14 V, not 14.6 V ⚠️ bench |
| m6 precharge V_SG | CLOSED | 101/(101 + 26.73) × 24.4 = 19.3 V ≤ 20; 7.8 V at 10 V |
| m7 GV14 upper V_GS | CLOSED | BAS116 anode source, cathode gate: V_GS ≥ ≈ −0.9 V. New side effect **R3** |
| m8 cable series R | CLOSED | J2 4 × 100 Ω; BQ NTC 1 k + 1 nF; ESP32 NTC 10 k. 1 k offsets recomputed (53 °C reads 45.8; row 23–26 thresholds ✓) |
| m9 USB hot plug | CLOSED | usb-c §4: my sim 5.4–5.85 V for 0.5–3 µH at 3.5 µF; 6.0–6.1 V at 4 µH or 3.0 µF effective ⚠️ scope stays required |
| m10 USB earth loop | CLOSED | intent §4 "USB rules"; carry to silk/README |
| m11 USB with BQ off | CLOSED | intent §4; relay also blocked by DCHG hi-Z |
| m12 single source | CLOSED | PJA3441 audited (−40 V, ±20 V, 108 mΩ, V_th −1…−2.5 V, SOT-23 G-S-D); spares table |
| m13 IMD accuracy | CLOSED | ad-dividers §2: ±25.6 mV band, ≤ 27 mV linear error recomputed; 0 dB + commissioning calibration |
| m14 pick-up current | **PARTLY** | gv14-driver §1 and connectors ✓. intent §3 J3 still "≤ 5 A peak (3.9 A)", J4 and §4 "3.9 A": say 5.2 A coil, ≈ 6.5 A J3, traces for 5.5 A |
| n1 latch coil text | CLOSED | inverter-remote §5 corrected |
| n2 balancing | CLOSED | bq76952 §3: Max Cells 1, host ≤ 2, never 3 + 16 |
| n3 button | CLOSED | esd §5: 100 k external, ≈ 27 µA |
| n4 precharge-done | CLOSED | 1 V threshold. Compare PACK with the **sum of cells**, not the ±0.5 V stack reading (halves the worst error) |
| n5 BQ outputs into ESP32 | CLOSED | MISO buffered on 3V3, ALERT open drain, DCHG/DDSG into 7 V tolerant buffers |
| n6 DEEPSLEEP | CLOSED | bq76952 §5 |
| n7 intent contradictions | **PARTLY** | 10.6 µA and README ESP32 row fixed. intent §9 Q3 still "VBUS feeds the 5 V rail through a diode" (conflicts with §3 J10, usb-c) |
| n8 test pulse timing | CLOSED | self-test §5: RMT |

## 2. New findings

### R1. BLOCKER: the OTP list leaves DDSG and DCHG unable to enable anything
- **Where:** bq76952.md §7.3 row 14 (`FET Options` = 0x05) and the missing `Mfg Status Init`; §7.2 warning.
- **Source:** AN §3 p. 9: "`FET Options[FET_CTRL_EN]` is set by default and **must remain set** for the BQ769x2 to control DCHG and DDSG", and "Enable the FETs by setting data memory or with FET_ENABLE". TRM p. 168: FET_CTRL_EN 0 = "FETs will not be turned on". TRM p. 173: `Mfg Status Init` (0x9343) defaults to **0x0040**, FET_EN = 0 = FET Test mode ("will not turn on FETs"); SLUAAQ5 §2.9: that mode disables automatic protection action.
- **Effect:** DDSG and DCHG (active-low) never go to "enabled": the GV14 and the charger relay can never close. Both hardware ANDs of B1 depend on this. Step 7.2-7 would show it only after the OTP is written (8 signatures).
- **Fix:** row 14 → `FET Options` = **0x0D** (default, or delete the row). Add `Mfg Status Init` (0x9343) = **0x0050** (FET_EN + PF_EN). Keep `Chg Pump Control` = 0x00. Replace the §7.2 ⚠️ with this. Prove in RAM (with R5) before the first OTP write.
- **To do.**

### R2. MAJOR: the new 0 Ω tap-0 tie makes the sense flex a second ground and shifts cell 1
- **Where:** bq76952.md §6 "VC0 / tap 0 → VSS 0 Ω net tie on the connector side of R(VC0)".
- **Source:** DS p. 70 (VC0 reaches VSS through the cell input resistor for random attach); DS p. 9 (VC0 −0.2…+0.5 V to VSS); intent §2 (board ground = node A through J3); harnesses.md H2 (J3 GND 200 mm, 18 AWG); v14-design-notes §1 (necked sense traces).
- **Effect:** VC0 is forced to board ground, so cell 1 = V(tap 1) − V(board GND) instead of − V(tap 0). J3 ground path ≈ 4 mΩ wire + ≈ 10 mΩ contact + ring ≈ **15 mΩ** ⚠️ estimate: cell 1 reads **≈ 22 mV low at 1.5 A** board current (LEDs on) and ≈ 100 mV low during the 6.5 A pick-up, against ±5 mV accuracy. The busbar drop between the cell-1 terminal and node A at pack current adds to it (not quantified). A 22 mV low reading lets cell 1 reach 3.665 V before the 3.643 V COV (limit 3.65). Board return current also splits into the flex neck (≈ 3 % at 0.5 Ω ⚠️, ≈ 0.2 A), and all of it if the J3 ground opens.
- **Fix:** replace the 0 Ω with **100 Ω** (ERJ-PA3F1000V, already on the BOM). VC0 then follows the flex tap (error < 1 % of the drop), loop current ≤ ≈ 1 mA, VC0 stays near VSS during attach. Keep "J3 before J1", and state what a lifted J3 ground does with J1 plugged (VC pins go below VSS with or without the tie).
- **To do.**

### MINOR
| # | Where | Finding, source, computed effect | Fix |
|---|---|---|---|
| R3 | gv14-driver §5, §7 | Upper FET: the BAS116 passes the mid-node charging current into the buffer output through only **100 Ω**. Upper C_oss ≈ 400 pF at ≈ 0.7 V/ns (X2, 70 V in ≈ 100 ns) → up to **≈ 0.2–0.3 A peak** ⚠️ estimate, vs LV1T34 I_OK ±20 mA, I_O ±25 mA (SCLS743E §6.1) at every release by the lower FET. The "≈ 10 nC" note has no current limit | Q_BQ gate resistor 100 Ω → **1 kΩ**: current ≤ 20 mA for a gate node up to ≈ 25 V, turn-on still ≈ 6 µs (a step for the coil). Scope with V_GS |
| R4 | self-test §3, §5 | Read at 30 µs is too early. Gate falls from 14.6 V with τ = 100 k × ≈ 100 pF = 10 µs: V(30 µs) = 0.3 + 14.3·e⁻³ = **1.0 V** (1.5 V at 120 pF; zener ≈ 30–50 pF per DS18010 Fig. 4 + BSS138 C_iss 50 pF), above V_th min 0.85 V and the doc's own 0.75 V "low". G3/C3 can report a false shorted coil and lock out the contactor | R_s 100 k → **47 k** 0805 (0.3 V at 30 µs; 2.8 mA into the zener at 150 V, ms only), or 80 µs pulse with read at 60 µs |
| R5 | bq76952 §7.2 | The RAM trial "steps 3 then 7 without the OTP write" cannot work: J1 is unplugged, so leaving CONFIG_UPDATE with `Shutdown Cell Voltage` 2600 shuts down in 5 s, and steps 6–7 start with a power cycle that clears RAM. The step-6 simulator at 12.0 V (3.00 V/cell) is also below CUV recovery 3.036 V, so a tripped CUV stays | Trial path: simulator on J1 before writing, 12.8 V, no power cycle. Use 12.8 V in step 6 too |
| R6 | intent §4 firmware rule; charger-relay-driver | Charge side of m1: COV recovers by itself (≤ 3.34 V) and OTC/UTC likewise, DCHG goes high again and the relay **re-closes** if CHG_RLY_EN is still high: cycling a 20 A contact, both clamps each time | Any ALERT / XCHG drops CHG_RLY_EN and latches until firmware re-qualifies; also wait ≥ CUV delay after leaving CONFIG_UPDATE (self-test) before closing anything |

### NOTE
| # | Note |
|---|---|
| R7 | esp32-pinmap: GPIO3 is **not** "defined at reset" (the only pull-up is the internal one, off at reset): harmless with default eFuses; add 100 k or correct the text. GPIO15/16 (XTAL_32K) also have low glitches (Table 2-2), harmless |
| R8 | Sleep sum omits BSS138 I_GSS (≤ 0.1 µA × 2 nodes at B+): summed max ≈ 10.8 µA. BREG: 100 nA NPN I_CBO × 10 MΩ = 1 V, so a hot, leaky NPN could conduct slightly into REGIN: include 60 °C in the sleep bench test |
| R9 | bq76952 §6 collector R: a continuous REG1 short (80 mA) puts 0.64 W on the 0.5 W ERJ-P06; "brief" is not guaranteed. Relay: after long conduction (coil ≈ 100 °C ⚠️) operate rises to ≈ 9.4 V, equal to the 10 V pack case; first closure is fine |
| R10 | The pump netlist behind precharge-fets §5a is not in the repo: commit it. Self-test P4 follows P2: wait ≥ 10 ms for Q2 to release first |
| R11 | Stale text: intent §4 charger relay row (one FET), §5 "I²C pull-ups"; README open item/MCU row and charger-relay-driver §5/§9 "CHG_RLY_EN must move" (done); DDSG/DCHG V_OH "≥ 2.9 V" is 2.7 V at REG1 min 3.0 V (still > 2.03 V) |

## 3. Special items judged
| Item | Result |
|---|---|
| Charger series pair | AND ✓. DMN61D8L internal drain-gate clamp (DS37630 p. 1) still works with the upper pin held at source − 0.9 V by the BAS116 (≈ 0.3 mA through its internal 10 k); external 10 k limits buffer current to ≤ 14 mA even at 150 V ✓ (< ±20 mA). Stacked clamps ≤ ≈ 150 V assumed: clamp maximum unpublished ⚠️ bench. Upper V_GS on ≥ 3.6 V ✓ |
| AC pump | Fails safe stuck high, stuck low, open D_a. Shorted 10 nF is latent, caught by P4. Free-running defeats it (documented) |
| 18 V zener | m5 above; sleep ✓ within budget if bench confirms 14.6 V leakage |
| OTP list | All listed addresses and defaults match the TRM data-memory table; bit decodes of rows 1–3, 5–9, 12–18, 20–31 checked ✓; CUV 2.783 V / 2.00 s / recover 3.036 V, COV 3.643 / 3.340 V ✓; Vcell Mode written first ✓; row 14 and the missing row: R1; bench steps: R5 (11.3 V gives BAT ≈ 10.5 V, inside 10–12 V ✓) |
| ESP32 pin map | ✓ apart from R7 |
| Sleep budget | 4.6 µA typ, 10.6 µA summed max recomputed (R8) |
| Sourcing | DigiKey API 2026-11-27: 30 new/changed MPNs queried, all Active and stocked |

## 4. Not judged
Footprints and land patterns; layout, creepage, spark gap; all bench items (clamp waveforms, ADC drift, zener leakage, USB ring, DDSG/DCHG on hardware); MLCC bias curves; unchanged audits (buck, LDO, LED switch, connectors) beyond cross-references.
