# U2 MCU: Espressif ESP32-S3-WROOM-1U-N8 (8 MB flash, no PSRAM, U.FL antenna)

Datasheets: module v1.8 (`datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf`; pin plan in [esp32-pinmap.md](esp32-pinmap.md)) and chip v2.2 (`datasheets/esp32-s3_datasheet_en.pdf`; read §2.2 Tables 2-1, 2-2, §5.4, §5.5). Footprint: `RF_Module:ESP32-S3-WROOM-1U` (KiCad 10.0.8, courtyard 19.5 × 20.15 mm).
Lifecycle: ACTIVE (DigiKey API, 2026-11-27).

| Variant | Flash / PSRAM | DigiKey (API, 2026-11-27) | Verdict |
|---|---|---|---|
| **-1U-N8** | 8 MB / none | in stock, 8 wk lead | **✓ chosen** |
| -1U-N8R2 | 8 MB / 2 MB quad | no stock | ✗ (was my proposal) |
| -1U-N16R8 | 16 MB / 8 MB **octal** | in stock | ✗ octal PSRAM takes GPIO35–37; not needed |
| -1U-N8R8 | 8 MB / 8 MB octal | — | ✗ same GPIO cost |

**Why no PSRAM:** the telemetry page (telemetry-ideas.md) is a small web server and a JSON stream; 512 kB of SRAM is enough ⚠️ (revisit if the dashboard grows). 8 MB flash holds two OTA app slots plus web assets.

**Chris (2026-11-27):** "I don't mind which ESP32 module you use."

## Constraints for the schematic
- **ADC: only ADC1 (GPIO1–10) works while Wi-Fi is on.** That's 10 channels; the pin plan uses 6 for analog (IMD, AC sense, box NTC, flex NTC 4 and 5, board NTC) and puts the self-test senses on digital pins ([esp32-pinmap.md](esp32-pinmap.md)).
- Strapping pins GPIO0, 3, 45, 46: keep them free or set them safely. GPIO19/20 = USB D−/D+ (USB-C).
- 3.3 V supply: 500 mA rated, Wi-Fi TX peaks ≈ 350 mA ⚠️ (datasheet); bulk 10 µF + 100 nF at the pins.
- EN: RC delay (10 k / 1 µF class) per Espressif; USB-Serial-JTAG auto-reset handles flashing.
- U.FL: 50 Ω coax to the front-plate flex antenna (spec §4).

## Chip datasheet v2.2: reset pulls, power-up glitches, ADC
| Finding | Source | Effect |
|---|---|---|
| ⚠️ **MTCK = GPIO39 has a weak pull-up (45 kΩ) after reset** while `EFUSE_DIS_PAD_JTAG` = 0 (default) | Table 2-1 note 7; Table 5-4 | `CHG_RLY_EN` can't sit there: 3.3 × 100/145 = 2.3 V ≥ LV1T34 V_IH 2.03 V. Swap with `INV_STATE` (GPIO42); no other actuator pin has a reset pull-up |
| Power-up glitches (≈ 60 µs): GPIO1–14, 17: low only; GPIO18: low and high; GPIO19, 20: high | Table 2-2 | no glitch listed on GPIO35–48, so `GV14_EN`, `PRE_EN1`, `PRE_PUMP`, `INV_SET/RESET`, `LED_EN`, `LED_DATA` are clean ✓ (closes the pin plan's ⚠️). GPIO18 (`SH_MOSI`) harmless |
| Calibrated ADC error: ±5 / ±6 / ±10 / ±50 mV for ranges 0–850 / 1100 / 1600 / 2900 mV (25 °C, 100 nF, Wi-Fi off) | Tables 5-5, 5-6 | [ntc.md](ntc.md), [ad-dividers.md](ad-dividers.md) |
| Pin leakage ≤ 50 nA | Table 5-4 | IMD error budget |
