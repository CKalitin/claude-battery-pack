# ESP32-S3-WROOM-1U-N8 pin plan (phase 1, answers review M5)

Source: Espressif ESP32-S3-WROOM-1/1U datasheet **v1.8** (`datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf`): §3 pins (36 GPIOs), Table 4-1 strapping (GPIO0 weak pull-up, GPIO3 floating, GPIO45 and GPIO46 weak pull-down), Table 4-3 boot mode (download needs GPIO0 = 0 and GPIO46 = 0), Table 4-4 VDD_SPI (GPIO45 must be 0 at reset for 3.3 V flash).
Only ADC1 (GPIO1–10) is usable while Wi-Fi runs.

Available: GPIO1–18, 21, 35–48 = 33 (GPIO19/20 = USB D−/D+; GPIO0 = BOOT pad only; GPIO35–37 free because N8 has no PSRAM). **Used: 31. Spare: 2** (GPIO43/44 = UART0, brought to pads for a fallback console).

| GPIO | Net | Dir | Notes (why this pin) |
|---|---|---|---|
| 1 | IMD_ADC | ADC1_CH0 | 200 k / 100 nF source; 0 dB atten, calibrated (review m13) |
| 2 | AC_SENSE_ADC | ADC1_CH1 | divider from J6-3 |
| 4 | BOX_NTC_ADC | ADC1_CH3 | J9 |
| 5 | FLEX_NTC4_ADC | ADC1_CH4 | moved off the BQ (review B1: DCHG becomes the charge gate) |
| 6 | FLEX_NTC5_ADC | ADC1_CH5 | |
| 7 | BOARD_NTC_ADC | ADC1_CH6 | 33 k bias (ntc.md; review m8) |
| 3 | SNS_PRE | in | **strap pin, no internal pulls**: add a **100 k external pull-up to 3V3** so it's defined at reset (the internal pull-up is off at reset; recheck R7). JTAG strap ignored with default eFuses anyway |
| 8 | SNS_GV14 | in | self-test |
| 9 | SNS_RLY | in | self-test |
| 10 | BUTTON | in | via BAS116 from TS2; 100 k external pull-up (review n3); **internal pull-up off** |
| 11 | BQ_SCLK | out | SPI (BQ7695204), own bus |
| 12 | BQ_MOSI | out | |
| 13 | BQ_MISO | in | through an SN74LV1T34 at 3.3 V: the BQ may drive MISO at REG18 = 1.8 V until configured (review m3) |
| 14 | BQ_CS | out | idle high (pull-up) |
| 15 | BQ_ALERT | in | interrupt; active-low open drain, external pull-up to 3V3 |
| 16 | BQ_RST_SHUT | out | 100 k pull-down; hold high ≥ 1 s = SHUTDOWN ("pack off") |
| 17 | SH_SCK | out | → TXU0304 A1 |
| 18 | SH_MOSI | out | → A2 |
| 35 | SH_NSS | out | → A3 |
| 21 | SH_MISO | in | ← A4Y |
| 36 | SH_OC | in | 10 k / 18 k divider |
| 37 | GV14_EN | out | → LV1T34 → upper GV14 FET; 100 k pull-down |
| 46 | PRE_EN1 | out | **strap**: weak pull-down at reset = off ✓; download mode needs it low ✓; plus 100 k external pull-down |
| 38 | PRE_PUMP | out (**RMT finite burst or software toggle, never free-running LEDC**: a free-running timer would keep toggling through a hang) | AC-coupled second precharge channel (B10): on ≤ 1.5 ms after toggling starts, off ≤ 6.5 ms after it stops |
| 39 | INV_STATE | in | latch pole B readback. **GPIO39 = MTCK has a 45 k pull-up after reset** (chip DS v2.2 Table 2-1 note 7): fine for an input, not for an actuator |
| 40 | INV_SET | out | latch coil pulse (hardware timer) |
| 41 | INV_RESET | out | latch coil pulse |
| 42 | CHG_RLY_EN | out | → LV1T34 → upper relay FET; lower FET gated by BQ DCHG (B8). Moved from GPIO39 (reset pull-up would turn the ESP32 FET on at every reset; review-fixes 2026-11-27) |
| 45 | LED_EN | out | **strap**: weak pull-down at reset = LEDs off ✓ and VDD_SPI = 3.3 V ✓; drives the eFuse EN (high-Z input) |
| 47 | LED_DATA | out (RMT) | → LV1T34 on the switched 5 V |
| 48 | LED_FLT | in | eFuse FLT (open drain), pull-up |
| 43 | (TXD0 pad) | — | boot log; spare / UART console |
| 44 | (RXD0 pad) | — | spare / UART console |
| 0 | BOOT pad | — | weak pull-up; short to GND for ROM download (USB auto-download normally) |
| EN | EN pad + RC | — | |

**Dropped to fit:** the LOAD+ ADC divider (review n4). "Precharge done" uses the BQ PACK reading with a 1 V threshold (PACK and stack are each ±0.5 V, DS p. 10).

**Power-up glitches** ✓ (chip DS v2.2 Table 2-2): glitches only on GPIO1–14, 17 (low), 18 (low/high), 19, 20; none on GPIO35–48, where every actuator sits. Every actuator needs two independent signals (GV14: GV14_EN + DDSG; precharge: PRE_EN1 + PRE_PUMP; relay: CHG_RLY_EN + DCHG), so one glitch can't fire it. The latching relay's INV_SET/RESET (GPIO40/41) are glitch-free and have no reset pull-up ✓.
