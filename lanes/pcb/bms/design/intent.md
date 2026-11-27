# BMS board: design intent (phase 0) — DRAFT for Chris's sign-off

**Board:** the pack's BMS / control board. 4S2P LFP, 12.8 V nominal. Sits flat over the inverter under the lid.
**Rev:** A (first). **Date:** 2026-11-27. **Author:** pcb lane. **Open source:** yes (public repo); no UBC Solar content.

Every line is a number or an explicit "don't care". ⚠️ = unconfirmed. **Q#** = question for Chris (§9).

## 1. Purpose
The board measures the cells (BQ76952) and current (Tesla shunt over SPI), and decides when the pack is on. It drives the contactor, precharge, charger relay and inverter remote; hosts Wi-Fi telemetry (ESP32-S3); and watches insulation to the chassis. It carries **no power current** except precharge (≤ 1.46 A for ≤ 0.5 s) and coil currents.

## 2. Electrical environment
| Item | Value | Source |
|---|---|---|
| Pack voltage (B+ to GND) | 10.0–14.6 V operating; design abs max **20 V** on every pack-connected part (margin over 14.6 V; transients clamped by TVS) | interface §1 |
| Cell voltage | 2.50–3.65 V (EVE LF105); UV ladder 2.90 firmware → 2.80 BQ UV → 2.75 inverter off → **2.60 BQ SHUTDOWN** | interface §1 |
| Board ground | Pack− at **node A** (cell side of the Tesla shunt), through J3 | tesla-shunt.md §1, §5 |
| Chassis | Floating from the pack; insulation monitored by the IMD divider (§5) | v14-design-notes §2, §4 |
| Taps | B+ (after the main fuse, before the GV14) through a 5 A ATM; LOAD+ (inverter fuse stud) through a 2 A ATM; 18 AWG | interface §4 |
| Transients | Contactor and relay coil kick (handled on board); load-bus spikes on LOAD+ from inverter/charger switching ⚠️ (TVS on LOAD+); hot-plug of J3 | design |
| Temperature (board air) | **−10 to +60 °C** operating ⚠️ (box air ≈ 10–24 K over a 25–35 °C room, board over the inverter); storage −20 to +60 °C (LFP storage) | cooling.md, converters §4 ⚠️ |
| ESD | Harness-only exposure (inside the closed box); lid button lead and LED-board lead leave the board area → ESD diode at their pins | design |

## 3. Interfaces (connectors one per destination; Micro-Fit 3.0 unless noted)
| J | Edge | To | Pins | Signal levels and currents |
|---|---|---|---|---|
| J1 | −x | Sense flex (FPC 12-pin 0.5 mm ZIF) | VC0–VC4, 5 × NTC, GND ×2 | cells 0–14.6 V common-mode, µA; NTC 10 k ⚠️ part |
| J2 | −x | Tesla shunt 1016792-00-C (Micro-Fit 2×4, **or Mini-Fit Jr 2×5 taking the shunt's own pigtail directly if Chris's test-fit passes**: 13.8 mm mated, so it needs main-battery's lid raise to z 335 + 4 mm standoffs; layout reserves its 23.2 × 22.2 mm courtyard so the swap moves nothing) | 5V, GND, NSS, SCK, MISO, MOSI, OC, spare | 5 V logic (VIH 3.5 V); SPI mode 0, 500 kHz; 5 V supply ≈ 30–50 mA ⚠️ |
| J3 | −y | Power taps + chassis (**1×4**, Chris 2026-11-27) | B+, LOAD+, GND, CHASSIS (ring lug on a chassis screw, for the IMD) | B+ ≤ 6.5 A peak for 75 ms (GV14 pick-up ≈ 5.2 A cold at 14.6 V + buck + relay; recheck m14); LOAD+ ≤ 1.46 A (precharge) |
| J4 | +x | GV14 coil (1×2) | X1 (+ = B+ switched), X2 | 12 V coil; pick-up 3.9 A nominal, **≈ 5.2 A at 14.6 V / −10 °C**, 75 ms; 0.23 A hold (built-in economizer) |
| J5 | +x | LED board (1×3) | 5V (switched by a TPS259530 eFuse, 2.58 A limit, off by default), DATA (SN74LV1T34 on the switched rail, 100 Ω series, TPD1E10B09 ESD), GND | ≈ 287 lit pixels on a 15.6 mm checkerboard lattice (main-battery, v16 grid ⚠️ option D may change it). 5 V WS2812-protocol RGB 2020 LEDs (Würth 1312020030000 proposed, Inolux IN-PI20TAT5R5G5B alternate ⚠️ audit in the LED-board phase). **Power cap ≤ 5 W typical / ≤ 10 W peak (2 A) in firmware** (main-battery: box cooling is marginal). High-side load switch so the LED rail is fully off when the display is off. Shows SOC as digits + a fill bar |
| J6 | +y | Charger relay (1×3) | coil 86, coil 85, AC_SENSE | coil 12 V 90 Ω: 162 mA at 14.6 V; AC_SENSE 0–14.6 V, µA |
| J7 | +y | Inverter CN301 (1×2) | dry contact | short = inverter remote OFF (NTS-400P-SPEC) |
| J8 | +y | Lid button (1×2) | BTN, GND | momentary; wakes the BQ76952 via TS2; long press = off |
| J9 | +y | Box-air NTC (1×2) | NTC, GND | 10 k NTC ⚠️ |
| — | — | U.FL on the WROOM-1U | 50 Ω coax ≈ 150–200 mm to the front-plate flex antenna | signal-wiring.md |
| — | — | Chassis reference for the IMD | J3 pin 4 → ring lug (Q2 answered) | — |
| J10 | +y | Programming / debug: **USB-C** (Chris) | VBUS, D+, D−, CC1/CC2, GND | USB 2.0 FS (ESP32-S3 USB-Serial-JTAG; GCT USB4105-GF-A, USBLC6-2SC6). **VBUS → TPS2116 power mux → 3.3 V LDO only** (not the 5 V rail: that would back-feed the buck and feed the LEDs). A pack-less board can be flashed; the BQ, shunt and LEDs stay unpowered (firmware keeps their I/O low or high-Z when the BQ is absent ⚠️) |

## 4. Functions and their numbers
| Function | Requirement | Source |
|---|---|---|
| Cell monitor | **BQ7695204PFBR** (BQ76952 family; SPI + CRC; REG1 on at 3.3 V by default, so no OTP is needed to boot) in TQFP-48. Cells on VC0–VC3 + VC16 (VC4–VC15 tied to VC3, Table 16-3). **3 NTCs on the BQ** (TS1, TS3, DFETOFF: SPI uses HDQ and CFETOFF, DCHG gates the charger relay, B8); flex NTC 4 and 5, the board NTC and the box NTC on ESP32 ADC1. Balancing internal, ≈ 50 mA | parts/bq76952.md |
| Current | Tesla shunt over SPI, through **TXU0304** (3 out, 1 in); OC (5 V) → divider → ESP32 | tesla-shunt.md §3 |
| Contactor | Low-side driver for ≤ 5.2 A / 75 ms pick-up: **2 × 100 V N-FETs in series** (BSZ146N10LS5), each gated by its own 5 V buffer: one from the ESP32, one from **BQ76952 DDSG** = hardware AND. **No external coil clamp: Sensata forbids it** (internal TVS; X2 reaches B+ + 55 V). Self-test sense on X2 | parts/gv14-driver.md |
| Precharge | **2 P-MOSFETs in series, same orientation**, B+ → AC05 10 Ω → LOAD+; each with its own driver and control line; **one channel AC-coupled = hardware time limit ≤ 1 s** (B10); LOAD+ measured by the BQ PACK pin (1 V threshold) for "precharge done" | Chris 2026-11-27; decisions B10 |
| Charger relay | **2 × DMN61D8L in series**: upper from the ESP32 (CHG_RLY_EN, buffered), lower from **BQ DCHG** = hardware AND (B8). Internal 60 V clamps, **no flyback diode** (TE: a diode slows release, risks welding); 0.16–0.20 A. Firmware: any ALERT/XCHG drops CHG_RLY_EN and latches until re-qualified, so COV/OTC/UTC auto-recovery can't re-close the relay (recheck R6). Self-test sense on the drain | parts/charger-relay-driver.md |
| Inverter remote | **Latching relay, zero holding current in either state** (Chris): KEMET EE2-5TNUH-L double-coil, set/reset by 2 × DMN61D8L pulses from ESP32 GPIOs; pole B reads the state back. PhotoMOS AQY212S is the runner-up | parts/inverter-remote.md |
| AC present | Divider from J6 AC_SENSE → ESP32 ADC | interface §4 |
| Box-air temperature | NTC bias + filter → ESP32 ADC | interface §4 |
| IMD | **R₊ 4.4 MΩ (2 × 2.2 M), R₋ 1.8 + 0.2 MΩ** (doubled from v14's 2.2 / 0.9 + 0.1 M to halve sleep draw: 14.6 V / 6.4 MΩ = 2.3 µA); ESP32 reads across 200 k with 100 nF (τ 20 ms); r₀ = 0.3125 unchanged; alarm at |r − 0.312| > 0.02. ⚠️ Fault sensitivity per v14 table scales with R: a fault is now visible up to ≈ 2× higher resistance; recheck the table at schematic | v14-design-notes §4; pcb 2026-11-27 |
| Board supply | B+ (J3) → TVS → **5 V buck, EN ← BQ76952 REG1** → 3.3 V (LDO) → ESP32, TXU0304 A-side | v14-design-notes §9 |
| Sleep | **≤ 10 µA typical in SHUTDOWN** (≈ 4.6 µA typ, ≈ 10.6 µA summing 25 °C datasheet maxima: parts/README.md budget, IMD halved); nothing else may draw from B+ when off; bench-measure | v14-design-notes §9 |
| Wake / off | Button → TS2 wakes from SHUTDOWN; same button to an ESP32 GPIO; long press = SHUTDOWN. **No charger wake** (D33). LD held low | v14-design-notes §9a; D33 |
| UV latch | Every UV trip latches (BQ SHUTDOWN at 2.60 V is the hardware latch); re-enable by button with min cell ≥ 3.00 V. **Works with a dead ESP32 only because the thresholds are in OTP** (B9). Firmware rule: any ALERT/XDSG drops GV14_EN and requires a full precharge before re-closing (review m1) | v14-design-notes §9a; decisions B9 |
| Charge stop in hardware | Charger relay = ESP32 CHG_RLY_EN **AND** BQ DCHG (COV, OTC, UTC) | decisions B8 |
| OTP bring-up | Mandatory bench step before any pack connection: cells disconnected, 10–12 V on BAT and VC16 (test pads), the ESP32 writes and checks OTP | decisions B9 |
| USB rules | Flash with AC unplugged or the laptop on battery (an earthed laptop + earthed chassis bonds pack− to earth through USB; review m10). When the BQ is absent (USB only), firmware holds every output off (m11) | review m10, m11 |
| Safe states | With no firmware: GV14 off (both FETs off), precharge off, charger relay open; inverter remote **keeps its last latched state** (harmless: with the GV14 open the inverter has no power) | design |
| Telemetry | **ESP32-S3-WROOM-1U-N8** (8 MB flash, no PSRAM), Wi-Fi, U.FL external antenna | parts/esp32-s3.md |

## 5. Power budget (awake, worst case) ⚠️ estimates until part audits
| Load | 5 V rail | 3.3 V rail |
|---|---|---|
| ESP32-S3 Wi-Fi TX peaks | — | 350 mA peak, ≈ 100 mA average |
| Tesla shunt module | 50 mA ⚠️ | — |
| TXU0304, LV1T34 buffers, SPI/ALERT pull-ups | 5 mA | 5 mA |
| LED board (J5) | ≤ 1 A typical, ≤ 2 A peak (firmware cap) | — |
| **Total** | ≈ 2.5 A peak incl. the 3V3 rail's input → **5 V buck ≥ 3 A** | ≈ 365 mA peak |
Coil currents (GV14, charger relay) come straight from B+ through their drivers, not from the 5 V rail.

## 6. Mechanical (from spec §4, final)
95 × 55 × 1.6 mm, 4 layers; 4 × M3 at 5 mm from the edges on 3 mm standoffs on the G10 bridge; top-side parts only, ≤ 12 mm including mated plugs; THT tails ≤ 2.5 mm; plug room 25 mm beyond −x, +x, +y and the −y strip at x −105…−84.

## 7. Manufacturing
- Fab: **PCBWay full PCBA** (or NextPCB if Zep sponsors both boards; owner-req §6). Design to rules both meet (0.15/0.15 mm, 0.3/0.6 mm vias).
- Quantity: **5** assembled (PCBWay minimum) ⚠️ Chris to confirm.
- Single-sided assembly. THT parts: the AC05 resistor and the Micro-Fit headers (or SMT Micro-Fit if available: phase 1).
- 4-layer standard 1.6 mm stack-up, ENIG ⚠️ (TQFP-48 0.5 mm pitch and the 0.5 mm FPC prefer ENIG).

## 8. Test and debug (Chris, 2026-11-27: "consider what is likely to break or you'd want me to test… you should do better" than student-board habits)
- **Firmware self-test instead of LEDs:** every switched output (GV14 low side, the precharge FETs, the charger-relay low side, the inverter remote) gets an ESP32-readable sense, so firmware detects a stuck-on FET, an open coil or a shorted coil and reports it over Wi-Fi. No per-output LEDs, no manual force-on hooks.
- **Test points only where a probe is needed at bring-up:** B+, LOAD+, 5V, 3V3, REG1 (also the B12 overdrive fallback), **BAT and VC16 (OTP programming, B9)**, GND. Everything else is read by firmware.
- **One status LED** (heartbeat/fault), visible with the lid off ⚠️ optional: the LED board shows state in normal use.
- Bring-up isolation: one 0 Ω link between the buck and its loads, so the 5 V rail can be checked before the ESP32 sees it ⚠️.

## 9. Answers (Chris, 2026-11-27) and what's left
- Q1 LED board: decided with main-battery (panel facts in J5 row): addressable 5 V RGB 2020 behind each lit hole, 3 mm gap to the diffuser ⚠️, 10 W peak cap. ✓
- Q2: ring lug, J3 → 1×4. ✓
- Q3: Chris wants to plug in a USB-C cable to flash → **USB-C receptacle on the +y edge** (ESP32-S3 native USB-Serial-JTAG: flash, console, debug); VBUS feeds only the 3.3 V LDO through a TPS2116 power mux (see J10), so a board with no pack can be flashed; IO0/EN pads as a fallback. Tag-Connect dropped. ⚠️ A laptop on an earthed charger joins pack− to earth through USB GND: the IMD will read it as an insulation fault while plugged in (expected; note it in firmware).
- Q4 inverter remote: Chris wants **zero holding current to keep it off** → a **latching (bistable) signal relay** on CN301, set and reset by pulses (no current while holding either state; keeps its state through an ESP32 restart). A second pole reads the state back for self-test. PhotoMOS form A is the runner-up (3 mA while holding off). NTS-400P-SPEC 2026-03-26 says only "dry contact (by RELAY)" for CN301, with no pin reference, so a bare MOSFET isn't safe to assume ⚠️.
- Q5: pcb's choice of ESP32 module. ✓
- Q6: 5 boards. ✓
