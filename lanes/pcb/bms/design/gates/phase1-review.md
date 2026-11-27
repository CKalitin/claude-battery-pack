# BMS board: phase 1 gate review (architecture + parts)

**Reviewer:** `pcb-review-parts` (independent). **Date:** 2026-11-27. **Revision:** `17d9c8c`. **Scope:** intent.md, decisions.md, parts/*.md, datasheets/, interface §1, §2, §4. No schematic or layout exists, so copper, EMC layout, footprint geometry and silkscreen are **NOT CHECKED**.

**Verdict: do not start the schematic yet.** 1 BLOCKER, 5 MAJOR, 14 MINOR, 8 NOTE. B1 and M5 change the pin plan; M3 adds parts.

Abbreviations: DS = BQ76952 datasheet SLUSE13B; TRM = SLUUBY2B (`datasheets/`). Pages are printed page numbers.

## BLOCKER

### B1. Nothing but firmware can stop charging on a cell fault
- **Where:** intent §4 (Cell monitor, Charger relay); bq76952.md §2 (DCHG used as an NTC); charger-relay-driver.md.
- **Rule / source:** CHG-side faults (COV, OTC, UTC; OCC is inert here, SRP = SRN) can only act on the CHG driver and DCHG. `DSG FET Protections A/B/C` have **no** COV, OTC, UTC or OCC bit (TRM p. 161–162), so DDSG cannot report them. The example text on TRM p. 60 suggests otherwise; the register definitions don't allow it. Chip CHG and DCHG outputs are both unused.
- **Effect:** the GV14 hardware AND covers discharge-side faults only. The charger relay is one ESP32 GPIO. With firmware running but wrong (threshold, logic, stale SPI data, SPI dead), a cell can be driven over voltage (the 14.2 V charger CV limits the sum, not each cell) or charged below 0 °C, with no backstop. Cells are damaged.
- **Fix:**
  1. Configure DCHG as DCHG, active-low, REG1 drive (`DCHG Pin Config = 0xAA`, same bit map as DDSG, TRM p. 150).
  2. Add a second DMN61D8L in series in the J6-85 low side, gated by DCHG. Drive both gates through SN74LV1T34 buffers as in the GV14 channel (direct 3.3 V logic leaves the upper FET only ≈ 2.3–2.9 V of V_GS, below the 3 V R_DS(on) spec), 100 kΩ pull-downs on both buffer inputs. Hi-Z in SHUTDOWN = relay blocked. Two FETs at 1.8 Ω max drop 0.6 V → coil 9.4 V at 10 V pack ≥ 8.2 V hot ✓. Check the two internal clamps in series at turn-off.
  3. Move flex NTC 4 to an ESP32 ADC (3 NTCs stay on the BQ). Alternative: put that NTC on ALERT and poll (keeps 4 BQ NTCs, frees a GPIO, loses the interrupt used in m1).
  4. Enable COV, UTC, OTC (and CHG FET Protections A/B) and program them in OTP (M1). Add `SNS_RLY` test steps for each FET.
- **To do.** If firmware-only charge protection is intended, only the owner can accept it; record it in decisions.md.

## MAJOR

### M1. Protections and the UV latch do not exist until the ESP32 writes them
- **Where:** intent §2 (UV ladder), §4 (UV latch); bq76952.md §1, §5 ("OTP optional"); v14-design-notes §9 ("independent of firmware").
- **Source (TRM):** factory defaults: `Enabled Protections A` = 0x88, so only SCD (disabled in effect, SRP = SRN) and COV at 86 × 50.6 mV = 4.35 V; **CUV off** (p. 157, 179); `Enabled Protections B` = 0, so **no temperature protection** (p. 158); `Shutdown Cell Voltage` = **0 = disabled**; `Shutdown Stack Voltage` = 6.00 V (p. 176); `Auto Shutdown Time` = 0 (p. 177; TRM p. 69 says it must be in OTP to cover an accidental wake). RAM is lost in SHUTDOWN.
- **Effect:** button bumped with a dead, bricked or half-flashed ESP32 → board stays on and discharges the cells until the stack reaches 6.0 V (1.5 V per cell). The "2.60 V hardware latch" and "2.80 V BQ UV" are firmware-dependent.
- **Fix:** make OTP programming **mandatory**: protections, thresholds, Vcell Mode (M2), Shutdown Cell Voltage 2600 mV, Auto Shutdown Time, DDSG/DCHG pin configs, SPI config. OTP needs **BAT 10–12 V** and −40…+45 °C (DS p. 9): the pack sits above 12 V, so write a bench step (board only, B+ from a supply at about 11.5 V so BAT, after its diode, is inside the window) before pack connection. Check `OTP_WR_CHECK` there. Correct the intent and README wording.

### M2. `Vcell Mode` is missing; the 4S wiring needs 0x8007 before anything else
- **Source:** TRM p. 154: default 0x0000 = **all 16 inputs are cells**. VC4–VC15 are shorted, so 12 "cells" read 0 V.
- **Effect:** enabling CUV trips it permanently on those inputs (DSG blocked, contactor never closes); writing a non-zero Shutdown Cell Voltage (exempts only inputs marked as not cells, TRM §7) puts the BQ into SHUTDOWN about 1 s later: every button press boots, configures and dies.
- **Fix:** `Settings:Configuration:Vcell Mode = 0x8007` (cells 1, 2, 3, 16), written first and stored in OTP. Add to bq76952.md §2 as a rule.

### M3. Precharge has no hardware time limit
- **Where:** precharge-fets.md; intent §4 (≤ 0.5 s timeout).
- **Calc:** both control lines stuck high with LOAD+ shorted: I = 14.6 / 10.2 = 1.43 A; AC05 = **20.4 W continuous on a 5 W part** (4×; its rating is 50 W for 5 s only, power-train §9); the 2 A ATM carries 1.43 A and **never opens**.
- **Effect:** the timeout exists only in firmware. A task watchdog covers a hang, not a logic bug that leaves the pins high. Resistor overheats on the board under the lid.
- **Fix:** AC-couple one of the two control lines so only a toggling GPIO holds it on (series C + diode pump + bleed into T2's base, release ≤ 1 s with no edges), or a hardware one-shot. Recheck self-test P2/P3. Alternative to justify: a series thermal fuse / fusible resistor.

### M4. Required externals of U1 and two intent §4 circuits have no part or value
Nothing in parts/ specifies (the schematic would be drawn from these files):

| Item | Requirement | Source |
|---|---|---|
| REGIN capacitor | 22 nF, **15–27 nF**, > 7 nF after derating; a "usual" 1 µF is out of spec | DS p. 13 |
| REG1 capacitor | ≥ 1 µF (also the buck EN net) | DS p. 14 |
| BREG | ≤ 150 pF to VSS; **10 MΩ BREG→VSS recommended** for SHUTDOWN leakage (add to sleep budget) | DS p. 13, 69 |
| BAT | series diode + resistor + capacitor MPNs and ratings; separate collector diode MPN | DS p. 64–66 |
| VC0–VC3, VC16 | 20–100 Ω / 0.1–1 µF: MPN, voltage rating; balance resistors (≥ 250 mW anti-surge, "MPN at schematic") | DS p. 9; bq76952.md §3, §6 |
| TS RC, PACK 10 k, REG18 cap | values/MPN | DS p. 65, 74–75 |
| FCX491ATA | no datasheet in `datasheets/`, no abs-max or pinout/footprint row (reviewer fetched DS33055: V_CEO 40 V, SOT89: passes) | |
| AC_SENSE divider | **no audit at all** (values, ADC clamp when unpowered, cable ESD) | intent §4 |
| IMD resistors | no MPN, tolerance or voltage rating; no chassis-lead ESD note | intent §4 |
| AC05 | datasheet not in `datasheets/`/sources.csv | |

**Fix:** add these rows to the audits (or `parts/ad-dividers.md`) with values and MPNs; archive the datasheets.

### M5. No ESP32 pin plan, and the ESP32 audit never opened the datasheet
- **Where:** esp32-s3.md (⚠️ "download… at schematic"). Reviewer read v1.8 (36 module GPIOs, Table 3-1; strapping §4).
- **Count:** digital: BQ SPI 4, ALERT 1, RST_SHUT 1, shunt SPI + OC 5, GV14 1, precharge 2, charger relay 1, inverter 3, LED 3, self-test 3, button 1 = **25**; ADC1: AC sense, box NTC, flex NTC5, board NTC, IMD = **5**. Total **30**, +2 optional (USB_ST, status LED), **+1 after B1** (ADC), +1 if M3/m1 adds a line. Available: 36 − USB (19, 20) = 34, of which 4 are strapping (0, 3, 45, 46). Non-strapping = **30, including TXD0**, which drives the ROM log at boot.
- **Effect:** it fits only by using strapping pins and with ≤ 2 spare. A wrong choice gives boot-mode faults or an actuator pulsing at reset.
- **Fix:** write the pin map now (ADC on GPIO1–10 only; GPIO3 usable as ADC; no actuator on TXD0 or on pins with a reset pull-up or power-up high glitch; GPIO45 must be low at reset), save the datasheet. If short: drop USB_ST or the status LED.

## MINOR

| # | Where | Finding, computed effect, source | Fix |
|---|---|---|---|
| m1 | GV14 / UV latch | BQ CUV recovers by itself (hysteresis default 101 mV, TRM p. 179); DDSG returns high and, if the ESP32 line is still high, the GV14 **re-closes without precharge** onto a discharged load bus. Breaks "every UV trip latches" | Rule: any ALERT/XDSG drops the ESP32 GV14 line and requires the full precharge sequence; or block autonomous recovery. Bench-test |
| m2 | bq76952.md | SRP = SRN = VSS, so the BQ always sees "no current" and enters SLEEP (default enabled, TRM p. 136): voltage and temperature updates every 5 s | Clear `Power Config[SLEEP]` (or SLEEP_DISABLE); put in OTP |
| m3 | bq76952.md | SPI MISO may default to **REG18 = 1.8 V** (DS p. 57; TRM default MISO_REG1 = 0, p. 139). ESP32 V_IH ≈ 2.48 V: replies unreadable | Confirm -04 default; firmware writes 0x60 blind then SWAP_TO_SPI, and OTP it. Or one LV1T34 at 3.3 V on MISO |
| m4 | bq76952.md §1 | The board boots only if the -04 also enables **REG0**. The datasheet states only "REG1 enabled, 3.3 V" (p. 4); the family default is REG0 off (TRM p. 137) ⚠️ | Confirm with TI or on an EVM before ordering. Fallback exists: overdrive the REG1 test point to power up and write OTP |
| m5 | self-test.md, input-protection.md §4 | BSS138 gate = B+ + ≈ 0.9 V: at the SMAJ15A full clamp 24.4 V → **25.3 V on a ±20 V gate** (5.3 V over). The BAS116 clamp follows B+, so it can't help. Also breaks intent §2 "20 V design max" | A sense FET with ±30 V V_GS (e.g. a 2N7002 variant rated ±30 V; check V_th against §6), or clamp to a rail that doesn't follow B+ without adding sleep current |
| m6 | precharge-fets.md §5 | V_SG at 24.4 V with 1 % corners: 101/(101 + 21.8) × 24.35 = **20.0 V**, zero margin on ±20 V | R_g 27 kΩ: 19.2 V max; 7.8 V at 10 V pack ✓. Recheck dv/dt |
| m7 | gv14-driver.md §7–8 | Upper FET gate is ground-referenced; its source (mid node) rises capacitively during the 70–80 V kick. Estimate from C_iss 1000 pF, C_oss ≈ 400 pF average (Infineon p. 4): mid ≈ 17–19 V → V_GS ≈ **−17…−19 V** (limit −20 V). Estimate, not simulated | 15 V zener source-to-gate on the upper FET, or scope V_GS at 14.6 V and 20 V B+ |
| m8 | J2, J1 | Cable lines without series protection: shunt SPI/MISO/OC direct to TXU0304; flex NTC lines direct to BQ TS pins (abs V_REG18 + 0.3) and ESP32 (3.6 V). A flex fault to a cell tap puts up to 14.6 V on them | 33–100 Ω series on SPI at the driver end (+ ESD if wanted); 1 kΩ series on each flex NTC (check BQ temperature error), 100 nF/≤ 4 nF per DS p. 65. J9: fit the "optional" 1 kΩ |
| m9 | usb-c.md §4 | Cable hot-plug into 1 µF ceramic can ring well above 5 V; TPS2116 abs max **6 V**; USBLC6 V_BR is only a 6 V minimum | Damp VIN2 (≈ 1 Ω in series with the 1 µF) or a VBUS TVS; scope it |
| m10 | usb-c.md §6 | AC plugged (chassis earthed) + earthed laptop = pack− bonded to chassis through the USB cable and board ground: a chassis fault becomes an unfused short through them, and the IMD is blinded meanwhile | Rule on silk/README: flash with AC unplugged or laptop on battery (or USB isolator) |
| m11 | usb-c.md | USB powers the ESP32 while the BQ is in SHUTDOWN; precharge and charger relay run from B+ and the ESP32 alone | Firmware: ST low → all outputs held off. B1's DCHG FET also blocks the relay |
| m12 | README | Single source: BQ7695204, LMR60430, BSZ146, TPS2595, TXU0304, EE2, SI2319DDS. SI2319DDS-T1-BE3 and DMP4065S-7 are **not stocked** (DigiKey, 2026-11-27) | Audit one stocked SOT-23 P-FET alternate (≥ 40 V, ±20 V); state the plan for the others (buy spares) |
| m13 | IMD | Alarm band at 12.8 V = 0.02 × 12.8 × 0.1 = **25.6 mV** at the ADC node (healthy 0.40 V); ESP32 ADC error at high attenuation can exceed it ⚠️ (chip datasheet not read) | Specify 0 dB attenuation, calibration and averaging; check input leakage × 180 kΩ |
| m14 | gv14-driver.md, connectors.md, intent §3 | 3.9 A is at nominal 12 V, 25 °C. At 14.6 V and −10 °C (coil R −14 %, path 0.17 Ω) pick-up ≈ **5.2 A**; J3 B+ ≈ 6.5 A for 75 ms (+1.1 A buck, 0.2 A relay) vs ≈ 7.5 A reference rating; ATM and FETs still pass | Update the tables; size J3/J4 traces for 5.5 A |

## NOTE
| # | Finding |
|---|---|
| n1 | inverter-remote.md §7 is wrong: at coil turn-off the idle winding sees the clamp voltage, so the idle FET's **body diode does conduct** (≈ 28 mA back into 5 V, flux in the same direction). Harmless; correct the text. Pin names are now **confirmed** from KEMET p. 3 (diagram) and p. 9 (footnote 4): coils 1(+)/12, 6(+)/7; COM 4, 9; NO 5, 8: the ⚠️ can close |
| n2 | Balancing: 0.4 W worst heat pairs max current with max R; consistent value ≈ 0.17 W for 2 cells. Cells 3 and "16" are physically adjacent: confirm autonomous mode treats them so, else Max Cells = 1 |
| n3 | Button V_OL: BAS116 typical V_F at ≈ 60 µA, −10 °C is about 0.65–0.7 V vs V_IL 0.825 V. A 100 kΩ external pull-up widens the margin |
| n4 | PACK and stack readings are each ±0.5 V (DS p. 10): "precharge done" threshold must allow ≈ 1 V, or add an ESP32 divider on LOAD+ (none from B+: sleep) |
| n5 | BQ outputs ride REG1 (≤ 3.6 V) into an ESP32 on a 3.25 V minimum rail: marginally over VDD + 0.3 at the corner |
| n6 | Never use DEEPSLEEP: REG1 off by default there and the button doesn't exit it (DS p. 52) |
| n7 | intent.md contradicts itself: §9 Q3 says VBUS → diode → 5 V rail (superseded by mux → LDO); §4 "≈ 10.7 µA" vs README 11; README still lists "ESP32 module (pcb picks)". Fix before owner sign-off |
| n8 | Self-test shorted-coil pulse drives ≈ 80 A through J3/J4: generate it with a hardware timer (RMT), never a software delay |

## Architecture questions
| Question | Answer |
|---|---|
| Button wake → self-powered (REG1 → buck → mux → 3V3 → ESP32)? | **Yes on paper**: EN 1.35 V max vs REG1 ≥ 3.0 V; mux switches at 3.7–4.3 V vs buck ≥ 4.9 V; TPS2116 also works with VIN1 = MODE = 0 (VIN2 selected). Conditional on REG0 (m4) |
| Sleep ≤ 10 µA typical? | **Yes**: recomputed 4.4 µA typ, 11.0 µA summed 25 °C max. Add the BREG resistor line; bench-measure |
| Safe with no firmware? | Outputs: **yes** (pull-downs, DDSG hi-Z, relay unchanged). Cell protection: **no** (M1) |
| Hardware AND for the contactor? | **Yes** for DSG-side faults after configuration; DDSG 0xAA decodes correctly (TRM p. 152–153). Charge side: B1. Re-close: m1 |
| Precharge ≤ 0.5 s, single-fault tolerant? | One shorted FET or driver: **yes**. 0.5 s: firmware only (M3) |
| USB flashing without back-feed? | **Yes** (mux blocks both inputs; buck not driven). m9–m11 |
| Missing from intent §4 | AC sense and IMD parts (M4); status LED, 0 Ω link and test points have no parts (optional) |

## Checks that re-computed correctly
Buck f_sw 993 kHz, ΔI 1.00 A, ripple 4.5 mV / 114 mV, L and C_OUT per Table 8-2, I_sat ≥ 7.5 A; LDO 113 °C; TPS2116 4.01 V; eFuse 2.58 A and 0.89 V/ms; charger relay 0.16–0.20 A, 9.6 V; precharge V_SG table (nominal), dv/dt 0.42 V, AC05 10.7 J; GV14 pick-up ≈ 9.3 V (≈ 9.2 V with buck current in the shared fuse); NTC voltages; OC divider 2.93 V; IMD 2.28 µA. BQ pin terminations match Table 16-3.

## Sourcing (DigiKey API, 2026-11-27)
All 35 picked or option MPNs queried returned **Active** and **stocked** (USBLC6-2SC6 found under its DigiKey part number, 39-30-1102 as 0039301102). Not stocked: the two second-source candidates (m12). This includes FCX491ATA. Not queried: passives with no MPN yet.

## Judged / not judged, per file
| File | Judged: pass | Judged: finding | Not judged (reason) |
|---|---|---|---|
| bq76952.md | 11 | 9 (B1, M1, M2, M4, m2, m3, m4, m1, n2) | PFB land pattern (layout) |
| esp32-s3.md | 5 | 1 (M5) | footprint; power-up glitch table (chip datasheet not read); RF |
| buck-5v.md | 13 | 0 | RAK0009A footprint; MLCC bias values (maker graphs not re-read); efficiency assumption; auto-mode output tolerance; L land |
| reg-3v3.md | 8 | 0 | — |
| usb-c.md | 8 | 3 (m9, m10, m11) | footprint vs GCT drawing; routing |
| precharge-fets.md | 8 | 3 (M3, m6, m12) | pulse-power chart (not re-read) |
| gv14-driver.md | 9 | 3 (m1, m7, m14) | TSDSON-8 footprint; tolerance of the 55 V clamp (unpublished) |
| charger-relay-driver.md | 7 | 1 (B1) | coil inductance (unpublished) |
| inverter-remote.md | 7 | 1 (n1) | CN301 levels (unpublished); pad geometry |
| input-protection.md | 5 | 1 (m5) | real spike energy (unmeasured) |
| led-link.md | 8 | 0 | LED-board C and V_IH (not chosen); SS14 surge |
| self-test.md | 4 | 2 (m5, n8) | pulse behaviour (bench) |
| esd.md | 3 | 2 (m8, n3) | — |
| ntc.md | 4 | 1 (m8) | AWG30 splice |
| shunt-spi-translator.md | 5 | 1 (m8) | OC polarity, shunt 5 V load (bench) |
| connectors.md | 5 | 1 (m14) | footprints vs SD drawings (names exist; geometry at layout); FH12 ratings not re-read; J2 test fit |
| README.md / intent.md | 3 | 3 (M4, m12, n7) | — |

Datasheets not reviewed because the part isn't picked: LMR43620, TPS62933, AP63357, LMR51430, TPS629210, TPS563300, TLV757P, AP7361C, SI2309, DMN10H170, AQY212S/412S, TQ2SA, G6K, TPS22810, FH34SRJ.
