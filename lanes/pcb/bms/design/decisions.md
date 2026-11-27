# BMS board decisions log

| # | Date | Decision | Options (incl. not tried) | Why | Sources |
|---|---|---|---|---|---|
| B1 | 2026-11-27 | Board 95 × 55 mm, 4 layers, top-side assembly | 175 × 90; 150 × 90 (guess, withdrawn); credit card 85.6 × 54 (fits with shared connectors only, 61 % with per-destination) | Real-footprint placement proof, 54 % occupancy | ../../bms-area.md |
| B2 | 2026-11-27 | One connector per destination, J1–J9, Micro-Fit 3.0 | Two shared 2×4s; Mini-Fit Jr (2.8× area) | Point-to-point harnesses, independent service (Chris) | ../../bms-area.md §12–13 |
| B3 | 2026-11-27 | Precharge by 2 series P-FETs, same orientation | G6S relay; back-to-back FETs | Single-fault tolerant forward; smaller; no wear (Chris) | ../../bms-area.md §10 |
| B4 | 2026-11-27 | Cell monitor orderable **BQ7695204PFBR** (SPI + CRC, REG1 3.3 V by default) | BQ76952PFBR (I²C, REG1 off: needs OTP; no stock, 26 wk); BQ7695202 (I²C, REG1 3.3 V: no stock); -01 (REG1 off); -03 (REG1 5 V); BQ76942 (same package, no area gain) | Boots without OTP; in stock. Cost: SPI takes HDQ and CFETOFF, so 4 NTCs on the BQ and 3 on ESP32 ADCs | parts/bq76952.md; TI SLUSE13B §5, §12.3.2, Table 6-1 |
| B5 | 2026-11-27 | MCU **ESP32-S3-WROOM-1U-N8** | -N8R2 (no stock); -N16R8/-N8R8 (octal PSRAM takes GPIO35–37) | In stock; PSRAM not needed | parts/esp32-s3.md |
| B6 | 2026-11-27 | BQ pre-regulator NPN **FCX491ATA** (40 V SOT-89) | FCX495TA (TI reference, out of stock, 150 V unneeded); BCX56-16 (no stock) | In stock; ≈ 46 mW | parts/bq76952.md |
