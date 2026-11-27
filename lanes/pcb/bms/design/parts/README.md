# BMS parts: phase 1 picks (2026-11-27)

U1 and U2 are audited by the pcb session; the rest by `pcb-bms-part-audits`. ✓ = picked and checked against the datasheet. ⚠️ = picked with an open item. Nothing here has had the independent gate review yet. No prices or distributor stock numbers (public repo).

| Function | MPN (qty) | Package | KiCad footprint | Why | Status | Audit |
|---|---|---|---|---|---|---|
| Cell monitor | BQ7695204PFBR (1) | TQFP-48 | `Package_QFP:TQFP-48_7x7mm_P0.5mm` | REG1 on at 3.3 V by default | ⚠️ pcb | [bq76952.md](bq76952.md) |
| MCU | ESP32-S3 module (pcb picks) | module | `RF_Module:ESP32-S3-WROOM-1U` | — | pcb | [esp32-s3.md](esp32-s3.md) |
| 5 V buck (3 A) | LMR604305SBRAKRQ1 (1) | WQFN-HR-9 | **custom** (TI RAK0009A) | ≤ 1 µA shutdown max, 3 A, in stock | ⚠️ footprint | [buck-5v.md](buck-5v.md) |
| Buck L / Cin / Cout | SRP5030TA-3R3M (1) / C3216X7R1H475K160AE (2) / GRM31CZ71C226ME15L (6: buck 2, LDO 2, LED 2) / CC0402KRX7R9BB104 | 5030 / 1206 / 1206 / 0402 | `L_Bourns_SRP5030T`, `C_1206…`, `C_0402…` | bias-checked | ⚠️ L land | same |
| 3.3 V LDO | TLV1117LV33DCYR (1) | SOT-223 | `SOT-223-3_TabPin2` (tab = OUT) | 113 °C at 500 mA | ✓ | [reg-3v3.md](reg-3v3.md) |
| USB-C | USB4105-GF-A (1) | SMT R/A | `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | maker drawing, 3.31 mm | ⚠️ footprint check | [usb-c.md](usb-c.md) |
| USB ESD / CC | USBLC6-2SC6 (ST) (1) + 2 × 5.1 k + 2 × 22 Ω | SOT-23-6 | `SOT-23-6` | 3.5 pF | ✓ | same |
| 3V3 source mux | TPS2116DRLR (1) | SOT-583 | `SOT-583-8` | no back-feed either way | ✓ | same |
| Precharge FETs | SI2319DDS-T1-GE3 (2) | SOT-23 | `SOT-23` | 40 V, SOA margin | ⚠️ second source | [precharge-fets.md](precharge-fets.md) |
| Precharge drivers | MMBT3904LT1G (2) + 100 k / 22 k / 1 nF (GRM1555C1H102JA01D); 22 k mid-node bleed | SOT-23 | `SOT-23` | 50 nA off leakage | ✓ | same |
| GV14 FETs | BSZ146N10LS5ATMA1 (2) | TSDSON-8 FL | **custom** | 100 V, 20.8 mΩ at 4.5 V | ⚠️ footprint | [gv14-driver.md](gv14-driver.md) |
| Gate / data buffers | SN74LV1T34DBVR (3: GV14 2, LED data 1) | SOT-23-5 | `SOT-23-5` | 3.3 → 5 V | ⚠️ DDSG config | gv14, led-link |
| GV14 clamp | **none** (forbidden by Sensata) | — | — | internal TVS | ✓ | gv14-driver |
| Relay drivers | DMN61D8L-7 (3: charger 1, latch set/reset 2), no diodes | SOT-23 | `SOT-23` | built-in clamp | ✓ | [charger-relay-driver.md](charger-relay-driver.md) |
| Inverter remote | EE2-5TNUH-L latching relay (1) | SMT 15 × 7.5 × 10 | `Relay_SMD:Relay_DPDT_Kemet_EE2_NUH_DoubleCoil` | no holding current, state readback | ⚠️ pin names | [inverter-remote.md](inverter-remote.md) |
| LED 5 V switch | TPS259530DSGR (1) + 787 Ω, 47 nF, SS14-E3/61T | WSON-8 / SMA | `Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias`, `D_SMA` | 2.58 A limit, FLT | ✓ | [led-link.md](led-link.md) |
| Self-test senses | BSS138LT1G (3) + 100 k 0603 + BAS116 clamp | SOT-23 | `SOT-23` | digital, no sleep current | ⚠️ bench | [self-test.md](self-test.md) |
| Shunt translator | TXU0304PWR (1) + 10 k / 18 k OC divider | TSSOP-14 | `TSSOP-14_4.4x5mm_P0.65mm` | 3 out + 1 in | ⚠️ OC polarity | [shunt-spi-translator.md](shunt-spi-translator.md) |
| TVS B+, LOAD+ | SMAJ15A-E3/61 (2) | SMA | `Diode_SMD:D_SMA` | clamps 24.4 V | ✓ | [input-protection.md](input-protection.md) |
| Reverse polarity / bulk cap | **none** | — | — | keyed harness; leakage | ⚠️ accepted risk | same |
| J2 | 43045-0800 (1); option Mini-Fit 39-30-1102 | THT R/A 2×4 | `Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal` | 10.82 mm (Mini-Fit 13.8 ✗) | ⚠️ test fit | [connectors.md](connectors.md) |
| J3 | 43650-0400 (1) | THT R/A 1×4 | `..._43650-0400_1x04_…_Horizontal` | chassis pin | ✓ | same |
| J5, J6 | 43650-0300 (2) | THT R/A 1×3 | `..._43650-0300_1x03_…_Horizontal` | 7.17 mm mated | ✓ | same |
| J4, J7, J8, J9 | 43650-0200 (4) | THT R/A 1×2 | `..._43650-0200_1x02_…_Horizontal` | | ✓ | same |
| J1 flex | FH12-12S-0.5SH(55) (1) | SMT ZIF | `Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal` | footprint exists; bottom contact | ✓ | same |
| Board NTC | NCU15XH103F6SRC (1) + 15 k bias | 0402 | `R_0402_1005Metric` | 0.55–2.44 V on ADC1 | ✓ | [ntc.md](ntc.md) |
| Box-air NTC (harness) | NTCLE413E2103F102L (1) | lead bead | — | 10 k 3435 K | ⚠️ AWG30 crimp | same |
| ESD J8, J5 | TPD1E10B09DPYR (2) | X1SON | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | ≤ 100 nA | ✓ | [esd.md](esd.md) |
| Button isolation + sense clamps | BAS116LT1G (4) | SOT-23 | `SOT-23` (pin 1 anode, pin 3 cathode) | nA leakage, 75 V | ⚠️ bench V_OL | esd, self-test |

## Sleep (SHUTDOWN) budget from B+, 25 °C
| Load | Typ [µA] | Datasheet max [µA] |
|---|---|---|
| BQ76952 ([bq76952.md](bq76952.md)) | 1.0 | 3.1 |
| IMD divider (pcb's; value from decisions B7, update if raised) | 2.3 | 2.3 |
| Buck LMR60430 | 0.7 | 1.0 |
| B+ TVS | ≪ 1 | 1.0 |
| Precharge P-FETs (series) + NPNs | ≈ 0.1 | 1.1 |
| GV14 FETs (series) | ≈ 0.1 | 1.0 |
| Relay driver | ≈ 0.1 ⚠️ | ≈ 1.0 |
| Self-test gates (X2 and relay drain high) | ≈ 0 | 0.2 |
| B+ MLCCs | ≈ 0.1 | 0.3 |
| **Total** | **≈ 4.5** | **≈ 11** |
**≤ 10 µA is met typically; the summed 25 °C maxima are still ≈ 11 µA**, and FET leakage rises with temperature. Bench-measure it. USB, the LED eFuse, the latching relay and the 3V3 mux draw nothing from B+ in sleep.

## Open questions for the owner
- **J2:** the Mini-Fit option is 13.8 mm mated (limit 12 mm): only with main-battery's agreement, after the test fit.
- Q1 (LED load), Q2 (chassis pin), Q3 (USB-C), Q4 (latching relay): answered 2026-11-27 and folded in.

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

## For other lanes
- Harness (main-battery): Micro-Fit **wire insulation ≤ 1.85 mm**; 18 AWG terminal 43030-0038; box NTC lead is AWG30.
- main-battery: Mini-Fit J2 would need 13.8 mm under the lid.

## Custom footprints to draw
TI RAK0009A, Infineon PG-TSDSON-8 FL (Panasonic SOP4 only if the PhotoMOS runner-up is used). Check `L_Bourns_SRP5030T` and the USB4105 footprint against their drawings.
