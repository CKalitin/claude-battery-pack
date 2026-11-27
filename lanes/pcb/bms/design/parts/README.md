# BMS parts: phase 1 picks (2026-11-27)

U1 and U2 are audited by the pcb session; the rest by `pcb-bms-part-audits`. ✓ = picked and checked against the datasheet. ⚠️ = picked with an open item. Nothing here has had the independent gate review yet. No prices or distributor stock numbers (public repo).

| Function | MPN (qty) | Package | KiCad footprint | Why | Status | Audit |
|---|---|---|---|---|---|---|
| Cell monitor | BQ7695204PFBR (1) | TQFP-48 | `Package_QFP:TQFP-48_7x7mm_P0.5mm` | REG1 on at 3.3 V by default | ⚠️ pcb | [bq76952.md](bq76952.md) |
| MCU | ESP32-S3-WROOM-1U-N8 (1) | module | `RF_Module:ESP32-S3-WROOM-1U` | in stock, U.FL | ⚠️ pcb | [esp32-s3.md](esp32-s3.md) |
| 5 V buck | LMR604305SBRAKRQ1 (1) | WQFN-HR-9 | **custom** (TI RAK0009A) | ≤ 1 µA shutdown max, 3 A, in stock | ⚠️ footprint | [buck-5v.md](buck-5v.md) |
| Buck L / Cin / Cout | SRP5030TA-3R3M (1) / C3216X7R1H475K160AE (2) / GRM31CZ71C226ME15L (4: buck 2, LDO 2) / CC0402KRX7R9BB104 | 5030 / 1206 / 1206 / 0402 | `L_Bourns_SRP5030T`, `C_1206…`, `C_0402…` | bias-checked | ⚠️ L land | same |
| 3.3 V LDO | TLV1117LV33DCYR (1) | SOT-223 | `SOT-223-3_TabPin2` (tab = OUT) | 113 °C at 500 mA | ✓ | [reg-3v3.md](reg-3v3.md) |
| Precharge FETs | SI2319DDS-T1-GE3 (2) | SOT-23 | `SOT-23` | 40 V, SOA margin | ⚠️ second source | [precharge-fets.md](precharge-fets.md) |
| Precharge drivers | MMBT3904LT1G (2) + 100 k / 22 k / 1 nF (GRM1555C1H102JA01D) | SOT-23 | `SOT-23` | 50 nA off leakage | ✓ | same |
| GV14 FETs | BSZ146N10LS5ATMA1 (2) | TSDSON-8 FL | **custom** | 100 V, 20.8 mΩ at 4.5 V | ⚠️ footprint | [gv14-driver.md](gv14-driver.md) |
| GV14 gate buffers | SN74LV1T34DBVR (2) | SOT-23-5 | `SOT-23-5` | 3.3 → 5 V, independent channels | ⚠️ DDSG config | same |
| GV14 clamp | **none** (forbidden by Sensata) | — | — | internal TVS | ✓ | same |
| Charger-relay driver | DMN61D8L-7 (1), no diode | SOT-23 | `SOT-23` | built-in clamp, fast release | ✓ | [charger-relay-driver.md](charger-relay-driver.md) |
| Inverter remote | AQY412S (form B) or AQY212S (form A) (1) | SOP4 | **custom** (Panasonic pad) | 60 V, one footprint for both | ⚠️ Q4 | [inverter-remote.md](inverter-remote.md) |
| Shunt translator | TXU0304PWR (1) + 10 k / 18 k OC divider | TSSOP-14 | `TSSOP-14_4.4x5mm_P0.65mm` | 3 out + 1 in | ⚠️ OC polarity | [shunt-spi-translator.md](shunt-spi-translator.md) |
| TVS B+, LOAD+ | SMAJ15A-E3/61 (2) | SMA | `Diode_SMD:D_SMA` | clamps 24.4 V | ✓ | [input-protection.md](input-protection.md) |
| Reverse polarity / bulk cap | **none** | — | — | keyed harness; leakage | ⚠️ accepted risk | same |
| J2 | 43045-0800 (1) | THT R/A 2×4 | `Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal` | 10.82 mm mated | ✓ | [connectors.md](connectors.md) |
| J3, J5, J6 | 43650-0300 (3) | THT R/A 1×3 | `..._43650-0300_1x03_…_Horizontal` | 7.17 mm mated | ✓ | same |
| J4, J7, J8, J9 | 43650-0200 (4) | THT R/A 1×2 | `..._43650-0200_1x02_…_Horizontal` | | ✓ | same |
| J1 flex | FH12-12S-0.5SH(55) (1) | SMT ZIF | `Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal` | footprint exists; bottom contact | ✓ | same |
| Board NTC | NCU15XH103F6SRC (1) | 0402 | `R_0402_1005Metric` | 103AT curve | ✓ | [ntc.md](ntc.md) |
| Box-air NTC (harness) | NTCLE413E2103F102L (1) | lead bead | — | 10 k 3435 K | ⚠️ AWG30 crimp | same |
| ESD J8, J5 | TPD1E10B09DPYR (2) | X1SON | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | ≤ 100 nA | ✓ | [esd.md](esd.md) |
| Button isolation, LED blocking | BAS116LT1G (3) | SOT-23 | `SOT-23` | nA leakage, 75 V | ⚠️ bench V_OL | [esd.md](esd.md) |

## Sleep (SHUTDOWN) budget from B+, 25 °C
| Load | Typ [µA] | Datasheet max [µA] |
|---|---|---|
| BQ76952 ([bq76952.md](bq76952.md)) | 1.0 | 3.1 |
| IMD divider, 14.6 V / 3.2 MΩ | 4.6 | 4.6 |
| Buck LMR60430 | 0.7 | 1.0 |
| B+ TVS | ≪ 1 | 1.0 |
| Precharge P-FETs (series) + NPNs | ≈ 0.1 | 1.1 |
| GV14 FETs (series) | ≈ 0.1 | 1.0 |
| Relay driver | ≈ 0.1 ⚠️ | ≈ 1.0 |
| B+ MLCCs | ≈ 0.1 | 0.3 |
| **Total** | **≈ 6.8** | **≈ 13** |
**≤ 10 µA is met typically, not by summed datasheet maxima.** FET leakage also rises with temperature. The lever is the IMD divider (pcb's choice). Bench-measure it.

## Open questions for the owner
- **Q1 LED board current** (still open): the buck handles 3 A electrically; 3 A continuous needs generous copper (thermal ⚠️).
- **Q4 inverter default:** recommend **form B** (off unless the BMS says on; ≈ 7 mA while on). Same footprint as form A.
- Q2, Q3, Q5, Q6: unaffected by these parts.

## Changes these picks make to intent.md / sizing list
1. GV14 coil: **delete the coil TVS**; "coil kick clamped" = the GV14's internal TVS. FETs are 100 V, 3.3 × 3.3 mm, plus two SOT-23-5 buffers on 5 V.
2. Charger relay: **no flyback diode** (DMN61D8L).
3. TVS is SMAJ15A (was SMAJ18A), one more on LOAD+.
4. Button: needs 1 kΩ + TVS to TS2 and a **BAS116 to the ESP32 pin** (otherwise the dead ESP32 holds TS2 low).
5. Board NTC goes to an ESP32 ADC channel ([bq76952.md](bq76952.md)).

## For other lanes
- Harness (main-battery): Micro-Fit **wire insulation ≤ 1.85 mm**; 18 AWG terminal 43030-0038; box NTC lead is AWG30.

## Custom footprints to draw
TI RAK0009A, Infineon PG-TSDSON-8 FL, Panasonic SOP4. Check `L_Bourns_SRP5030T` against the SRP5030TA drawing.
