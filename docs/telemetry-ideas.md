# Telemetry ideas (running list)

Everything the pack could measure or compute and show. Each entry lists the source (hardware the pack already has) and what it's for. Add ideas as they come up.

> **Future task: telemetry dashboard.** A web page served locally by the ESP32 over Wi-Fi. It must be **extremely beautiful**: plan real design effort (typography, a Roadster-red accent, motion, a dark theme), not a default chart library. Design it as its own version step once the sensor list settles.

## Cell and group health
| Idea | Source | Purpose |
|---|---|---|
| Group/cell voltage, live, plus min/max/spread | BQ76952 | Balance state, imbalance trend |
| **Equivalent resistance per group**, $R_g = \Delta V_g/\Delta I$ on each load step | BQ76952 ΔV + shunt ΔI | Ageing per cell (8S); open-cell detection in a pair (4S2P, ≈ 2× jump) |
| Resistance trend over time / cycles | Logged $R_g$ | End-of-life prediction |
| Self-discharge rate per group (voltage drift at rest) | BQ76952, long idle | Detects a soft internal short |
| Balancing duty per group | BQ76952 balance status | A group that always needs balancing is suspect |
| Cell temperatures | Thermistors on the flex | Thermal map, derating |

## Pack state
| Idea | Source | Purpose |
|---|---|---|
| State of charge (coulomb count + voltage correction at the steep ends of the curve) | Shunt + BQ76952 | Main gauge |
| State of health (Ah delivered between full and empty; resistance growth) | Logged | Capacity fade |
| Energy in/out [Wh], cycle count, equivalent full cycles | Shunt × V | Lifetime ledger |
| Peak current, I²t of the last burst vs rating | Shunt | 3C/30 s budget, contactor I²t margin |
| Remaining runtime at the present load | SoC ÷ P | Main user-facing number |
| Time to full while charging | SoC + charge current | |

## Safety
| Idea | Source | Purpose |
|---|---|---|
| **IMD ratio $V_\text{ch}/V_\text{pack}$** and estimated leakage resistance | Divider → ESP32 ADC | First-fault detection; a hard short reports *which node* |
| Contactor state, coil current, closure count | Board | Wear |
| Precharge time / voltage curve | Board | Detects capacitor and load faults |
| Fault log with timestamps | Firmware | Post-mortem |

## Converters and environment
| Idea | Source | Purpose |
|---|---|---|
| Charger on/off, charge current, charge stage | Shunt sign + NPB status | |
| Inverter power out (from DC current × V, with η) | Shunt | AC load estimate |
| Board and ambient temperature, fan RPM and command | Sensors / tach | Thermal health; fan failure |
| Enclosure ΔT, inlet to exhaust | 2 thermistors | Actual airflow check vs the 6 K estimate |
| Lid-open switch (if one is ever added) | — | Not planned: best part is no part |

## Dashboard features
- Live pack "hero" gauge: SoC, power, runtime.
- 8 (or 4) group bars showing voltage and resistance, colour-coded by deviation.
- History charts: V, I, T, $R_g$ trend, energy ledger.
- Fault and IMD panel that is quiet until something happens.
- Export to CSV; OTA firmware update page.
