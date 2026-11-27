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
| J2 | −x | Tesla shunt 1016792-00-C (Micro-Fit 2×4, **or Mini-Fit Jr 2×5 taking the shunt's own pigtail directly if Chris's test-fit passes**: +281 mm², occupancy ≈ 59 %) | 5V, GND, NSS, SCK, MISO, MOSI, OC, spare | 5 V logic (VIH 3.5 V); SPI mode 0, 500 kHz; 5 V supply ≈ 30–50 mA ⚠️ |
| J3 | −y | Power taps + chassis (**1×4**, Chris 2026-11-27) | B+, LOAD+, GND, CHASSIS (ring lug on a chassis screw, for the IMD) | B+ ≤ 5 A peak (coil pick-up 3.9 A, 75 ms); LOAD+ ≤ 1.46 A (precharge) |
| J4 | +x | GV14 coil (1×2) | X1 (+ = B+ switched), X2 | 12 V coil; 3.9 A pick-up for 75 ms, 0.23 A hold (built-in economizer) |
| J5 | +x | LED board (1×3) | 5V (switched), DATA (5 V level), GND | ≈ 287 lit pixels on a 15.6 mm checkerboard lattice (main-battery, v16 grid ⚠️ option D may change it). 5 V WS2812-protocol RGB 2020 LEDs (Würth 1312020030000 proposed, Inolux IN-PI20TAT5R5G5B alternate ⚠️ audit in the LED-board phase). **Power cap ≤ 5 W typical / ≤ 10 W peak (2 A) in firmware** (main-battery: box cooling is marginal). High-side load switch so the LED rail is fully off when the display is off. Shows SOC as digits + a fill bar |
| J6 | +y | Charger relay (1×3) | coil 86, coil 85, AC_SENSE | coil 12 V 90 Ω: 162 mA at 14.6 V; AC_SENSE 0–14.6 V, µA |
| J7 | +y | Inverter CN301 (1×2) | dry contact | short = inverter remote OFF (NTS-400P-SPEC) |
| J8 | +y | Lid button (1×2) | BTN, GND | momentary; wakes the BQ76952 via TS2; long press = off |
| J9 | +y | Box-air NTC (1×2) | NTC, GND | 10 k NTC ⚠️ |
| — | — | U.FL on the WROOM-1U | 50 Ω coax ≈ 150–200 mm to the front-plate flex antenna | signal-wiring.md |
| — | — | Chassis reference for the IMD | J3 pin 4 → ring lug (Q2 answered) | — |
| J10 | +y | Programming / debug: **USB-C** (Chris) | VBUS, D+, D−, CC1/CC2, GND | USB 2.0 FS (ESP32-S3 USB-Serial-JTAG); VBUS 5 V → diode → 5 V rail |

## 4. Functions and their numbers
| Function | Requirement | Source |
|---|---|---|
| Cell monitor | BQ76952 (TQFP-48); 4 cells on VC1–VC4 with VC16 tied per Table 16-3; 6 NTCs (5 flex + 1 board) on TS1, TS3, CFETOFF, DFETOFF, HDQ, DCHG; balancing internal | owner-req §5; afe.md |
| Current | Tesla shunt over SPI, through **TXU0304** (3 out, 1 in); OC (5 V) → divider → ESP32 | tesla-shunt.md §3 |
| Contactor | Low-side driver for 3.9 A / 75 ms pick-up; enable = **ESP32 GPIO AND BQ76952 DDSG**, in hardware; coil kick clamped; LED + TP on the output | interface §4; Chris's HVC style |
| Precharge | **2 P-MOSFETs in series, same orientation**, B+ → AC05 10 Ω → LOAD+; each FET with its own driver and its own control line; ≤ 0.5 s timeout; LOAD+ measured (BQ PACK pin and/or ESP32 ADC) for "precharge done" | Chris 2026-11-27 |
| Charger relay | Low-side driver + flyback, 162 mA; LED + TP | interface §2 |
| Inverter remote | Dry contact (PhotoMOS); **Q4:** default with the BMS off (form A: inverter runs when the contactor is closed unless commanded off; form B: inverter off unless commanded on) | NTS-400P-SPEC |
| AC present | Divider from J6 AC_SENSE → ESP32 ADC | interface §4 |
| Box-air temperature | NTC bias + filter → ESP32 ADC | interface §4 |
| IMD | R₊ 2.2 MΩ (pack+ → chassis), R₋ 0.9 + 0.1 MΩ (chassis → pack−); ESP32 reads across 100 k; r₀ = 0.312; alarm at |r − 0.312| > 0.02 | v14-design-notes §4 |
| Board supply | B+ (J3) → TVS → **5 V buck, EN ← BQ76952 REG1** → 3.3 V (LDO) → ESP32, TXU0304 A-side | v14-design-notes §9 |
| Sleep | **≤ 10 µA total in SHUTDOWN** (BQ 1 µA + buck off ≈ 2 µA + IMD 4.6 µA + leakage); nothing else may draw from B+ when off | v14-design-notes §9 |
| Wake / off | Button → TS2 wakes from SHUTDOWN; same button to an ESP32 GPIO; long press = SHUTDOWN. **No charger wake** (D33). LD held low | v14-design-notes §9a; D33 |
| UV latch | Every UV trip latches (BQ SHUTDOWN is the hardware latch); re-enable by button with min cell ≥ 3.00 V | v14-design-notes §9a |
| Safe states | With no firmware: GV14 off, precharge off, charger relay open, inverter remote per Q4 | design |
| Telemetry | ESP32-S3 Wi-Fi, U.FL external antenna; module variant **Q5** (flash / PSRAM) | owner-req §1 |

## 5. Power budget (awake, worst case) ⚠️ estimates until part audits
| Load | 5 V rail | 3.3 V rail |
|---|---|---|
| ESP32-S3 Wi-Fi TX peaks | — | 350 mA peak, ≈ 100 mA average |
| Tesla shunt module | 50 mA ⚠️ | — |
| TXU0304, BQ76952 I²C pull-ups, LEDs (≈ 8 × 1 mA) | 5 mA | 15 mA |
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
- **Test points only where a probe is needed at bring-up:** B+, LOAD+, 5V, 3V3, REG1 (BQ76952 LDO), GND, plus the Tag-Connect. Everything else is read by firmware.
- **One status LED** (heartbeat/fault), visible with the lid off ⚠️ optional: the LED board shows state in normal use.
- Bring-up isolation: one 0 Ω link between the buck and its loads, so the 5 V rail can be checked before the ESP32 sees it ⚠️.

## 9. Answers (Chris, 2026-11-27) and what's left
- Q1 LED board: decided with main-battery (panel facts in J5 row): addressable 5 V RGB 2020 behind each lit hole, 3 mm gap to the diffuser ⚠️, 10 W peak cap. ✓
- Q2: ring lug, J3 → 1×4. ✓
- Q3: Chris wants to plug in a USB-C cable to flash → **USB-C receptacle on the +y edge** (ESP32-S3 native USB-Serial-JTAG: flash, console, debug); VBUS feeds the 5 V rail through a diode, so a board with no pack can be flashed; IO0/EN pads as a fallback. Tag-Connect dropped. ⚠️ A laptop on an earthed charger joins pack− to earth through USB GND: the IMD will read it as an insulation fault while plugged in (expected; note it in firmware).
- Q4 inverter remote: Chris wants **zero holding current to keep it off** → a **latching (bistable) signal relay** on CN301, set and reset by pulses (no current while holding either state; keeps its state through an ESP32 restart). A second pole reads the state back for self-test. PhotoMOS form A is the runner-up (3 mA while holding off). NTS-400P-SPEC 2026-03-26 says only "dry contact (by RELAY)" for CN301, with no pin reference, so a bare MOSFET isn't safe to assume ⚠️.
- Q5: pcb's choice of ESP32 module. ✓
- Q6: 5 boards. ✓
