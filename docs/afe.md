# Cell monitor (AFE) selection: why BQ76952 (written 2026-11-27)

**Orderable part (pcb, 2026-11-27): BQ7695204PFBR**, the same BQ76952 silicon factory-set for SPI + CRC with REG1 on at 3.3 V.
- BQ76952PFBR and BQ7695202 are out of stock with a 26-week lead (DigiKey API, 2026-11-27).
- The plain part also wakes from SHUTDOWN with REG1 off, so the board buck could never start without an OTP step (SLUSE13B §12.3.2).
- SPI uses HDQ and CFETOFF, so 4 NTCs sit on the BQ; flex NTC 5, the board NTC and the box NTC go on ESP32 ADCs.
- The BQ76942 is the same 48-pin 7 × 7 TQFP, so no area gain (answered by pcb).

Details: lanes/pcb/bms/design/parts/bq76952.md, decisions B4–B6.

**Status:** the BQ76952 was chosen in early versions with no recorded comparison (CLAUDE.md documentation gap). Chris has since fixed it for the BMS board (pcb lane, `lanes/pcb/toolchain.md` R1). This page records the reasons after the fact, the alternatives, and one equivalent that was never tried.

## 1. Requirements
| # | Requirement | Source |
|---|---|---|
| A1 | Measure 4 series groups (4S2P LF105) via the sense flex: 5 taps VC0–VC4 | cells.md, v14-baseline |
| A2 | **Protection that works with the firmware hung:** a hardware fault output gates the GV14 driver (ESP32 **AND** AFE) | power-train P3, review M4 |
| A3 | **Autonomous SHUTDOWN** at 2.60 V/cell that turns the whole board off (≈ µA), plus an LDO output that enables the board's buck | v14-design-notes §9 |
| A4 | Wake from the lid button with no MCU running | v14-design-notes §9a, D33 |
| A5 | ≥ 6 thermistor inputs (5 flex tabs + 1 board) | v14-baseline |
| A6 | Balancing | baseline |
| A7 | Current is measured by the Tesla shunt (D3), so the AFE's coulomb counter and current protections may be unused | tesla-shunt.md |
| A8 | Catalog part with a manufacturer datasheet; JLC/PCBWay-assemblable package | CLAUDE.md |

## 2. Candidates
| Part | Series range | Fits A2 (digital fault out) | A3 (SHUTDOWN + LDO) | A4 (wake pin) | A5 (thermistors) | Verdict |
|---|---|---|---|---|---|---|
| **TI BQ76952** (SLUSE13B, Nov 2021) | 3–16S | ✓ DDSG/DCHG pins as digital outputs | ✓ REG1/REG2 programmable LDOs; SHUTDOWN at a set min-cell voltage | ✓ TS2 pulled low wakes it | ✓ up to 9 multifunction pins (TS1–3, CFETOFF, DFETOFF, ALERT, HDQ, DCHG, DDSG); pcb uses all of them (6 NTC + DDSG + ALERT + TS2) | **✓ chosen.** Meets every requirement. 48-pin TQFP. 3–16S range is unused beyond 4S |
| TI BQ76942 (SLUSE14B, Dec 2021) | 3–10S | ✓ same DDSG/DCHG | ✓ same REG1/REG2 | ✓ same TS2 | same TS1–3 + multifunction pins ⚠️ count to check | **Not tried.** Same family and firmware model in a smaller package. Look at it if board area or price matters; the pcb lane decides with Chris |
| TI BQ76905 (SLUSE97, Nov 2023) / BQ76907 (SLUSE96A) | 2–5S / 2–7S | ALERT only; integrated **low-side** NFET drivers aimed at FET-switched packs | one REGOUT LDO | — ⚠️ | fewer TS inputs ⚠️ | ✗ built around low-side FET switching (not our GV14 + high-side copper); fewer thermistor/digital pins than A2 + A5 need |
| TI BQ76920 (BQ769x0, SLUSBK2I) | 3–5S | ALERT | REGOUT; SHIP mode | boot pin | up to 3 thermistors in the family ⚠️ (1 on the BQ76920) | ✗ too few thermistors (A5); older generation |
| ADI LTC6813 / ADBMS681x | up to 18S | ✗ a monitor only; no standalone protector | ✗ | ✗ | GPIOs | ✗ needs an MCU for every protection, which fails A2 |
| Maxim MAX17841 | — | — | — | — | — | ✗ an isoSPI-to-SPI bridge, not an AFE |
| Renesas ISL94202 | 3–8S | ✓ standalone protector | ✓ | ✓ | ⚠️ 2 external thermistors | **Not tried in depth.** Thermistor count is short for A5 without a mux ⚠️ |

## 3. Notes and traps
- **SRP/SRN unused:** with current from the Tesla shunt, the BQ76952's current-sense inputs tie to VSS (datasheet Table 16-3), so its OCC/OCD/SCD protections are off. **Over-current protection is the MRBF fuses plus firmware, not the AFE** (pcb lane, `bms-area.md`).
- **All 9 multifunction pins are used,** so the box-air NTC for the cooling thermostat goes on an ESP32 ADC (converters.md §4).
- **Price is not decisive:** a few USD either way. Octopart's 2026-11-27 listings for BQ76952PFBR and BQ76942PFBR were mostly non-authorized brokers ⚠️.

## 4. Sources
- TI BQ76952 datasheet SLUSE13B, rev. Nov 2021 ✓
- TI BQ76942 datasheet SLUSE14B, rev. Dec 2021 ✓
- TI BQ76905 SLUSE97 (Nov 2023), BQ76907 SLUSE96A (rev. Jul 2026), BQ769x0 SLUSBK2I (rev. Mar 2022) ✓, front pages only; the ⚠️ cells weren't checked in the body
- LTC6813, MAX17841, ISL94202: from general knowledge, **not re-read this session** ⚠️

## 5. Open items
- ✓ BQ76942: same package as the BQ76952, no area gain (pcb, 2026-11-27).
