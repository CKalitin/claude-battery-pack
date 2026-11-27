# BMS board: area and height estimate (2026-11-27)

**Freeze: 150 × 90 mm, top-side parts ≤ 12 mm, bottom side no parts.** ⚠️ Estimate from courtyard allowances. No schematic or placement yet.

**Accepted by main-battery into `spec/interface.md` §4 (`aa40b9f`, 2026-11-27); the spec is authoritative.** It changed the mounting to 3 mm standoffs on a G10 bridge (rows below).

## 1. Space claim (option D coordinates, `cad/analysis/converter_packing.py`)
| Item | Value | Conf. |
|---|---|---|
| Board (x × y × thickness) | 150 × 90 × 1.6 mm | ⚠️ |
| Position | x −105…45, y −15…75 mm | proposal |
| Standoffs | 3 mm on a G10 .125 bridge → board z 317.5…319.1 mm | interface.md §4 |
| Top-side parts, mated plugs included | ≤ 12 mm (to z 331.1, 1.9 mm under the lid at z 333) | ⚠️ |
| Bottom side | no components; through-hole tails ≤ 2.5 mm (≥ 0.5 mm to the G10 bridge) | rule |
| Holes | 4 × M3, centres 5 mm from the edges, 8 × 8 mm keep-out | ⚠️ |
| Connectors | right-angle. −x edge (90 mm), plus the −y edge for x −105…−62 (43 mm) | ⚠️ |
| Plug and wire-bend keep-out | 25 mm beyond those two edges | ⚠️ |

Why those edges:
- Clear of the fan (ends at x −136, 31 mm gap) and far from the mains parts at x ≥ 100.
- No plug over an MRBF lift-out column (x 20…78 and 121…149, y < −20).
- Along the rest of the −y edge the SB175 (x −60…−4, y ≤ −33) leaves only 18 mm.

## 2. Area
| Block | Courtyard allowance [mm²] ⚠️ |
|---|---|
| ESP32-S3-WROOM-1U (18 × 19.2 mm) + decoupling, U.FL clearance | 750 |
| Programming / debug connector | 150 |
| BQ76952 + tap filters, balance resistors, NTC networks, regulator | 1400 |
| Shunt SPI level shifter (TXU0104) | 150 |
| GV14 coil driver (ESP32 AND BQ) + TVS | 400 |
| Precharge relay + 10 Ω resistor | 750 |
| Inverter remote PhotoMOS | 100 |
| Charger relay coil driver | 150 |
| 2 A fuse, protection, 5 V buck, 3.3 V | 900 |
| UV latch | 150 |
| IMD divider | 150 |
| Edge connectors (≈ 95 mm of edge × 15 mm deep: sense FPC, shunt, power, coil, charger relay, inverter remote, button, LED link) | 1500 |
| 4 mounting holes | 260 |
| Test points | 300 |
| **Total** | **7110** |

| Size [mm] | Area [mm²] | Courtyard fill | Verdict |
|---|---|---|---|
| 120 × 90 | 10 800 | 66 % | Not picked: tight with no schematic, and 43 mm less room for the −y connectors |
| **150 × 90** | 13 500 | 53 % | **Picked** |
| 175 × 90 (placeholder) | 15 750 | 45 % | Not needed; releases 25 mm of x |

Other sizes, a two-board split and double-sided assembly were not studied.

## 3. Height
| Part | Height [mm] | Source |
|---|---|---|
| ESP32-S3-WROOM-1U | 3.2 | third-party copy of Espressif datasheet v1.1 ⚠️ |
| Omron G6S (precharge relay candidate, 2 A) | 9.2–9.4 | DigiKey / Omron excerpts via search ⚠️ |
| Micro-Fit 3.0 right-angle header, mated | 10.06 (one 2-circuit variant, 430450223) | Molex datasheet via search ⚠️ |

So the placeholder's ≤ 10 mm is too tight for the connectors; 12 mm fits under the lid. The v15 model's 15 mm relay does not fit and must change.

## 4. Open
- ⚠️ Precharge resistor: pulse energy depends on the inverter's input capacitance (unknown). 25 × 12 mm footprint assumed. interface.md §4 sets **10 Ω / 10 W**; a 10 W part is likely nearer 50 × 10 mm (about +200 mm², still fits the fill) ⚠️ part and height not checked.
- ⚠️ Board temperature above the inverter: not analysed.
- ⚠️ Antenna (interface.md §4): U.FL coax, ≈ 150–200 mm, to a flex antenna behind the front-plate light-pipe slot.
- `cad/tower15.py` CTRL models the WROOM-1U as 18 × 25.5 mm; 18 × 19.2 mm is the 1U size ⚠️.
