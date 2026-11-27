# U2 MCU: Espressif ESP32-S3-WROOM-1U-N8 (8 MB flash, no PSRAM, U.FL antenna)

Datasheet: Espressif "ESP32-S3-WROOM-1 & WROOM-1U datasheet" ⚠️ download the current revision and read §pins, strapping, electrical, layout, at schematic. Footprint: `RF_Module:ESP32-S3-WROOM-1U` (KiCad 10.0.8, courtyard 19.5 × 20.15 mm).
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
- **ADC: only ADC1 (GPIO1–10) works while Wi-Fi is on.** That's 10 channels; this board needs about 9 (AC sense, box NTC, flex NTC5, board NTC, IMD, LOAD+/B+ ⚠️, three self-test senses). It's tight: list them in the pin plan first.
- Strapping pins GPIO0, 3, 45, 46: keep them free or set them safely. GPIO19/20 = USB D−/D+ (USB-C).
- 3.3 V supply: 500 mA rated, Wi-Fi TX peaks ≈ 350 mA ⚠️ (datasheet); bulk 10 µF + 100 nF at the pins.
- EN: RC delay (10 k / 1 µF class) per Espressif; USB-Serial-JTAG auto-reset handles flashing.
- U.FL: 50 Ω coax to the front-plate flex antenna (spec §4).
