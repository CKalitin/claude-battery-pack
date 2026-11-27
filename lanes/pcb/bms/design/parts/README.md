# BMS parts: phase 1 picks (2026-11-27)

U1 and U2 are audited by the pcb session; the rest by `pcb-bms-part-audits`. The phase-1 review findings ([../gates/phase1-review.md](../gates/phase1-review.md)) were folded in on 2026-11-27 by `pcb-bms-review-fixes`: not yet re-reviewed. ✓ = picked and checked against the datasheet. ⚠️ = picked with an open item. No prices or distributor stock numbers (public repo).

| Function | MPN (qty) | Package | KiCad footprint | Why | Status | Audit |
|---|---|---|---|---|---|---|
| Cell monitor | BQ7695204PFBR (1) + externals: BAS116LT1G ×2, 100 Ω (ERJ-PA3F1000V, ERJ-P06F1000V), 1 µF ×2, 10 M, 22 nF, 2.2 µF, 4.7 µF, 20 Ω ERJ-PA3F20R0V ×5, 220 nF ×5, TS 1 k ×3 + 1 nF ×3, PACK 10 k | TQFP-48 | `Package_QFP:TQFP-48_7x7mm_P0.5mm` | REG1 on at 3.3 V by default; **OTP mandatory** | ⚠️ REG0 default, DDSG/DCHG bench | [bq76952.md](bq76952.md) |
| BQ pre-regulator NPN | FCX491ATA (1) | SOT-89 | `Package_TO_SOT_SMD:SOT-89-3` | 40 V, h_FE ≥ 300 | ⚠️ pin numbering | same |
| MCU | ESP32-S3-WROOM-1U-N8 (1) | module | `RF_Module:ESP32-S3-WROOM-1U` | in stock, U.FL | ✓ pin plan (GPIO39 resolved) | [esp32-s3.md](esp32-s3.md), [esp32-pinmap.md](esp32-pinmap.md) |
| 5 V buck (3 A) | LMR604305SBRAKRQ1 (1) | WQFN-HR-9 | **custom** (TI RAK0009A) | ≤ 1 µA shutdown max, 3 A, in stock | ⚠️ footprint | [buck-5v.md](buck-5v.md) |
| Buck L / Cin / Cout | SRP5030TA-3R3M (1) / C3216X7R1H475K160AE (2) / GRM31CZ71C226ME15L (6: buck 2, LDO 2, LED 2) / CC0402KRX7R9BB104 | 5030 / 1206 / 1206 / 0402 | `L_Bourns_SRP5030T`, `C_1206…`, `C_0402…` | bias-checked | ⚠️ L land | same |
| 3.3 V LDO | TLV1117LV33DCYR (1) | SOT-223 | `SOT-223-3_TabPin2` (tab = OUT) | 113 °C at 500 mA | ✓ | [reg-3v3.md](reg-3v3.md) |
| USB-C | USB4105-GF-A (1) | SMT R/A | `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | maker drawing, 3.31 mm | ⚠️ footprint check | [usb-c.md](usb-c.md) |
| USB ESD / CC | USBLC6-2SC6 (ST) (1) + 2 × 5.1 k + 2 × 22 Ω; VBUS damper 1.8 Ω + 4.7 µF + 100 nF | SOT-23-6 | `SOT-23-6` | 3.5 pF; hot plug ≤ 5.85 V simulated | ⚠️ scope | same |
| 3V3 source mux | TPS2116DRLR (1) | SOT-583 | `SOT-583-8` | no back-feed either way | ✓ | same |
| Precharge FETs | SI2319DDS-T1-GE3 (2); alternate **PJA3441** | SOT-23 | `SOT-23` | 40 V, SOA margin | ⚠️ alternate has no SOA chart | [precharge-fets.md](precharge-fets.md) |
| Precharge drivers | MMBT3904LT1G (2) + 100 k / **27 k** / 1 nF (GRM1555C1H102JA01D); T2 behind a diode pump: BAT54SLT1G, 1 k, 10 nF, 100 nF, 100 k, 33 k; 22 k mid-node bleed | SOT-23 | `SOT-23` | channel 2 releases ≤ 6.5 ms after toggling stops (sim) | ⚠️ bench | same |
| GV14 FETs | BSZ146N10LS5ATMA1 (2) | TSDSON-8 FL | **custom** | 100 V, 20.8 mΩ at 4.5 V | ⚠️ footprint | [gv14-driver.md](gv14-driver.md) |
| Gate / data buffers | SN74LV1T34DBVR (**6**: GV14 2, charger relay 2, LED data 1, BQ MISO 1) | SOT-23-5 | `SOT-23-5` | 3.3 → 5 V; 1.8 → 3.3 V | ⚠️ DDSG/DCHG config | gv14, relay, led-link, bq76952 |
| GV14 clamp | **none** (forbidden by Sensata) | — | — | internal TVS | ✓ | gv14-driver |
| Relay drivers | DMN61D8L-7 (**4**: charger 2 in series, latch set/reset 2); charger upper gate 10 k 0805 + BAS116 | SOT-23 | `SOT-23` | built-in clamp; hardware charge stop | ⚠️ bench X ≤ 150 V | [charger-relay-driver.md](charger-relay-driver.md) |
| Inverter remote | EE2-5TNUH-L latching relay (1) | SMT 15 × 7.5 × 10 | `Relay_SMD:Relay_DPDT_Kemet_EE2_NUH_DoubleCoil` | no holding current, state readback | ✓ pin names (datasheet); ⚠️ symbol numbering | [inverter-remote.md](inverter-remote.md) |
| LED 5 V switch | TPS259530DSGR (1) + 787 Ω, 47 nF, SS14-E3/61T | WSON-8 / SMA | `Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias`, `D_SMA` | 2.58 A limit, FLT | ✓ | [led-link.md](led-link.md) |
| Self-test senses | BSS138LT1G (3) + 100 k 0805 + MMSZ5248B-7-F 18 V zener (3) | SOT-23 / SOD-123 | `SOT-23`, `D_SOD-123` | digital; gate ≤ 19.5 V; ≤ 0.2 µA sleep | ⚠️ bench | [self-test.md](self-test.md) |
| Shunt translator | TXU0304PWR (1) + 10 k / 18 k OC divider + 4 × 100 Ω series | TSSOP-14 | `TSSOP-14_4.4x5mm_P0.65mm` | 3 out + 1 in | ⚠️ OC polarity | [shunt-spi-translator.md](shunt-spi-translator.md) |
| TVS B+, LOAD+ | SMAJ15A-E3/61 (2) | SMA | `Diode_SMD:D_SMA` | clamps 24.4 V | ✓ | [input-protection.md](input-protection.md) |
| Reverse polarity / bulk cap | **none** | — | — | keyed harness; leakage | ⚠️ accepted risk | same |
| J2 | 43045-0800 (1); option Mini-Fit 39-30-1102 | THT R/A 2×4 | `Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal` | 10.82 mm (Mini-Fit 13.8 ✗) | ⚠️ test fit | [connectors.md](connectors.md) |
| J3 | 43650-0400 (1) | THT R/A 1×4 | `..._43650-0400_1x04_…_Horizontal` | chassis pin | ✓ | same |
| J5, J6 | 43650-0300 (2) | THT R/A 1×3 | `..._43650-0300_1x03_…_Horizontal` | 7.17 mm mated | ✓ | same |
| J4, J7, J8, J9 | 43650-0200 (4) | THT R/A 1×2 | `..._43650-0200_1x02_…_Horizontal` | | ✓ | same |
| J1 flex | FH12-12S-0.5SH(55) (1) | SMT ZIF | `Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal` | footprint exists; bottom contact | ✓ | same |
| Board NTC | NCU15XH103F6SRC (1) + **33 k** bias, 10 k series, 100 nF (same circuit for flex NTC 4, 5 and box) | 0402 | `R_0402_1005Metric` | 0.27–1.93 V; ≤ ±1.3 K at 0…60 °C | ✓ | [ntc.md](ntc.md) |
| Box-air NTC (harness) | NTCLE413E2103F102L (1) | lead bead | — | 10 k 3435 K | ⚠️ AWG30 crimp | same |
| ESD J8, J5 | TPD1E10B09DPYR (2) | X1SON | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | ≤ 100 nA | ✓ | [esd.md](esd.md) |
| AC-present sense | 2 × 100 k 0805 + 15 k + 100 nF | 0805 / 0402 | `R_0805…` | 14.2 V → 0.99 V | ⚠️ bench | [ad-dividers.md](ad-dividers.md) |
| IMD divider | CRCW08052M20FKEA ×2, CRCW08051M80FKEA, CRCW0805200KFKEA, 100 nF; copper spark gap | 0805 | `R_0805_2012Metric` | 2.3 µA; calibrate at commissioning | ⚠️ | same |
| Low-leakage diodes | BAS116LT1G (**5**: button, BQ BAT, BQ collector, GV14 upper gate, relay upper gate) + 100 k button pull-up | SOT-23 | `SOT-23` (pin 1 anode, pin 3 cathode) | nA leakage, 75 V | ⚠️ bench V_OL | esd, bq76952, gv14, relay |

## Sleep (SHUTDOWN) budget from B+, 25 °C
| Load | Typ [µA] | Datasheet max [µA] |
|---|---|---|
| BQ76952 ([bq76952.md](bq76952.md)) | 1.0 | 3.1 |
| BQ REG0 NPN I_CBO (BREG held by 10 MΩ; the resistor itself draws nothing from B+) | ≪ 0.1 | 0.1 |
| IMD divider | 2.3 | 2.3 |
| Buck LMR60430 | 0.7 | 1.0 |
| B+ TVS | ≪ 1 | 1.0 |
| Precharge P-FETs (series) + NPNs | ≈ 0.1 | 1.1 |
| GV14 FETs (series) | ≈ 0.1 | 1.0 |
| Charger-relay FETs (two in series) | ≈ 0.1 | 0.5 |
| Self-test zeners (X2 and relay drain sit at B+) | ≈ 0.05 | 0.2 (at 14 V; ⚠️ 14.6 V) |
| B+ MLCCs | ≈ 0.1 | 0.3 |
| **Total** | **≈ 4.6** | **≈ 10.6** |
**≤ 10 µA is met typically; the summed 25 °C maxima are still ≈ 10.6 µA**, and leakage rises with temperature. Bench-measure it. USB, the LED eFuse, the latching relay, the 3V3 mux, the MISO buffer, AC_SENSE and the precharge pump draw nothing from B+ in sleep.

## Single-source parts: spares plan (review m12; 5 boards)
| Part | Per board | Buy | Fallback (not audited unless said) |
|---|---|---|---|
| BQ7695204PFBR | 1 | 5 + 2 | none (BQ7695201 needs the REG1 overdrive for first power-up) |
| LMR604305SBRAKRQ1 | 1 | 5 + 2 | TPS62933 (buck-5v.md §6, new layout) |
| TPS259530DSGR | 1 | 5 + 2 | TPS259531 (auto-retry, same package) |
| TXU0304PWR | 1 | 5 + 2 | TXU0304RUTR (other footprint) |
| EE2-5TNUH-L | 1 | 5 + 2 | TQ2SA-L2-5V (other footprint) |
| BSZ146N10LS5ATMA1 | 2 | 10 + 4 | SiS892ADN |
| DMN61D8L-7 | 4 | 20 + 10 | none |
| SI2319DDS-T1-GE3 | 2 | 10 + 4 | **PJA3441 (audited, same footprint)** |
Order these at schematic freeze and consign them to the fab (or have the fab buy early) instead of waiting for turnkey sourcing. Re-check stock at each hand-off.

## Open questions for the owner
- **J2:** the Mini-Fit option is 13.8 mm mated (limit 12 mm): only with main-battery's agreement, after the test fit.
- Q1 (LED load), Q2 (chassis pin), Q3 (USB-C), Q4 (latching relay): answered 2026-11-27 and folded in.

## Open items (parts, after the review fixes)
- ⚠️ **Pin plan:** `CHG_RLY_EN` off GPIO39 ([esp32-s3.md](esp32-s3.md)).
- ⚠️ BQ: REG0 default (B12); DDSG/DCHG behaviour vs `FET Options` and GPO self-test; balancing adjacency; discharge temperature limits; flex NTC B value; tap-0 / board-ground tie.
- ⚠️ Precharge: the pump limits stuck pins, not firmware that keeps re-queuing bursts. `PRE_PUMP` must not be free-running LEDC.
- ⚠️ Bench: charger-relay drain up to ≈ 150 V when both clamps act (layout clearance ≥ 1.25 mm); GV14 upper-gate waveform; VBUS hot plug; zener leakage; sleep current; shorted-coil sense at 10 V.
- ⚠️ IMD static error ≈ the alarm band without commissioning calibration.

## Changes these picks make to intent.md
1. GV14 coil: **no coil TVS** ("coil kick clamped" = the GV14's internal TVS); 100 V FETs and two 5 V buffers.
2. Charger relay: **no flyback diode** (DMN61D8L).
3. TVS is SMAJ15A, also on LOAD+.
4. Button: 1 kΩ + TVS to TS2 and a **BAS116 to the ESP32 pin** (else the dead ESP32 holds TS2 low).
5. Inverter remote: latching relay; "safe state with no firmware" = **unchanged** (initialise at boot).
6. USB VBUS feeds the **3.3 V LDO through a power mux**, not the 5 V rail: the buck cannot be back-driven at its output (usb-c.md §4a).
7. Self-test replaces per-output LEDs: 5 digital GPIOs (+1 optional), 0 ADC.
8. LED rail via an eFuse (2.58 A limit); data buffer powered from the switched rail.
9. Test points: rails only (§8); no output test points. Tag-Connect is replaced by USB-C plus IO0/EN/GND pads.
10. OTP bring-up pads: `TP_BAT`, `TP_VC16`, `TP_REG1`, `GND` (two more than intent §8: BAT and VC16).

## For other lanes
- Harness (main-battery): Micro-Fit **wire insulation ≤ 1.85 mm**; 18 AWG terminal 43030-0038; box NTC lead is AWG30.
- main-battery: Mini-Fit J2 would need 13.8 mm under the lid.

## Custom footprints to draw
TI RAK0009A, Infineon PG-TSDSON-8 FL (Panasonic SOP4 only if the PhotoMOS runner-up is used). Check `L_Bourns_SRP5030T` and the USB4105 footprint against their drawings.
