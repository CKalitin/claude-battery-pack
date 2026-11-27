# Cells: how the EVE LF105 was chosen, how to buy it, what to watch for

**Status 2026-11-24:** 8 × EVE LF105, 4S2P (v14). Not yet purchased.
⚠️ marks values that are unconfirmed.

This doc records the whole exploration: what was tried, what was rejected and why, and the traps found along the way. Per-version detail is in `versions/v01…v14/README.md`.

---

## 1. Requirements the cell has to meet

| # | Requirement | Source |
|---|---|---|
| R1 | ≥ 1 kWh | Owner's principles list (`blog-notes.md`) |
| R2 | Busbars on top: inspectable, torqueable, away from the shell | Owner, v06 rejection |
| R3 | Narrow, tall tower proportion; body ≈ 190 mm wide | Design brief, v02 |
| R4 | Few cells and few joints (assembly time) | Owner: "I will not spend 200 hours doing assembly" |
| R5 | LFP chemistry: thermally stable, no BMS heroics | v01 decision |
| R6 | Buyable from a stocked reseller with a real datasheet. No email-the-vendor parts | Owner's standing rule |
| R7 | Can supply the DC-out rating: **500 A for 30 s**, 210 A continuous (v14 D2) | `v14-design-review.md` §0 |
| R8 | Cells alone ≤ 30 kg per container and ≤ 150 kg total, so they can be carried home under TDG 1.15 | §5 |

## 2. Path through the design space

| Versions | Cell | Config | Energy | What it taught us | Why it moved on |
|---|---|---|---|---|---|
| v01–v04 | EVE **LF50K** (135.3 × 29.3 × 185.3 mm, 50 Ah) | 8S1P | 1.28 kWh | Prismatic LFP works with end plates + tie rods | Twice the cells and joints for the same energy (R4) |
| v05 | EVE **LF100MA** (160 × 50.1 × 118.5 mm, 100 Ah) | 4S1P | 1.28 kWh | Half the joints | 160 mm wide → 222 mm body (R3) |
| v06 | LF100MA laid on edge | 4S1P | 1.28 kWh | Body 180 mm wide | **Busbars on the side wall: rejected by the owner (R2).** A whole branch was thrown away, because R2 was unstated until then. |
| v07–v09 | EVE **LF105** (130.3 × 36.7 × 200.5 mm, 105 Ah, 1.98 kg) | 4S1P | 1.34 kWh | Narrow *and* tall: 190 mm body with busbars on top. **The fix was a different cell, not a different orientation.** | Cost review: four more cells add only about $300, against ≈ $2,000 of enclosure and electronics. 8 cells: $1.15/Wh vs $1.94/Wh |
| v10–v13 | LF105 | 8S1P | 2.69 kWh | Half the current of 4S2P at 24 V | v14 D1: the owner fixed 4S2P (12 V class) |
| **v14** | LF105 | **4S2P** | 2.69 kWh | 500 A power train in bolted copper | — |

**Width check (v07):** $W_\text{body} = W_\text{cell} + 2 \times 29.85 = 130.3 + 59.7 = 190$ mm
- $W_\text{body}$ = body outer width [mm]
- $W_\text{cell}$ = cell width [mm]
- 29.85 = per-side allowance for the tie rods at y = ±72, wall clearance and the 1.6 mm wall [mm]

**Energy:** $E = N \cdot V_\text{nom} \cdot C = 8 \times 3.2 \times 105 = 2688$ Wh
- $E$ = pack energy [Wh]
- $N$ = number of cells [–]
- $V_\text{nom}$ = cell nominal voltage, 3.2 V [V]
- $C$ = cell capacity [Ah]

### Candidates never evaluated (post-hoc check, 2026-11-24)
These weren't compared at the time. That is a documentation gap, recorded here so the question isn't reopened blind.

| Cell | Why it loses here |
|---|---|
| EVE LF280K / MB31 (≈ 174 × 72 × 207 mm, ≈ 5.4 kg ⚠️ from memory) | 72 mm thick, ~5 kg each. 4 cells already make 3.6 kWh at 12.8 V (4S1P), far over R1, and each cell is heavier to handle. Width is fine for R3. **The strongest alternative if more energy is ever wanted.** |
| LF230 / LF304 | Same family as the LF280K; same reasoning |
| 18650 / 21700 cylindrical | Hundreds of cells and welded or bonded joints (R4); needs a cell holder that SendCutSend can't make (R6) |
| Pouch LFP | Needs compression fixtures and tab welding (R4) |

## 3. Datasheet facts used, and where each comes from

| Value | Used for | Source | Confidence |
|---|---|---|---|
| 3.2 V nominal, 2.5–3.65 V | UV/OV ladder, converter selection | EVE spec F | ✓ |
| 105 Ah | Energy | EVE spec F | ✓ |
| 1.98 kg | Mass (15.84 kg of cells) | EVE spec F | ✓ |
| 130.3 × 36.7 × 200.5 mm | CAD | EVE spec F, NKON listing | ✓ |
| ≤ 0.5 mΩ AC IR (0.32 mΩ measured on new cells) | Short-circuit current (5.0–6.9 kA), fuse AIC | EVE spec F, NKON reviews | ✓ |
| 1C continuous | 210 A continuous (4S2P) | EVE spec F, resellers | ✓ |
| **3C for 30 s** | **The whole 500 A / 30 s rating** | 18650batterystore listing: it says "1C/3C" for 30 s and doesn't say whether that means charge or discharge | ⚠️ **Weak.** Several resellers (NKON, Fogstar, Battery Junction) list only "max discharge 1C". Get the EVE spec's own pulse-discharge row before baselining 500 A. |
| Charge 0–55 °C | Low-temperature charge inhibit (M3) | EVE spec F | ✓ |
| Poles: internal M4, 6 mm effective depth | Terminal screws M4 × 8 | EVE spec rev B | ⚠️ Resellers say M6. Check on the first cell. |
| 300 kgf clamping fixture in EVE cycle tests | Tie-rod preload (736 N per rod) | EVE spec F | ✓ |

**Datasheet hygiene:** at least two EVE revisions (rev B and rev F) are reposted by resellers, and some reseller pages carry FAQ text for the wrong cell (the 18650batterystore LF105 page answers LF280K questions). Always cite the EVE revision, never a reseller summary, for any value the design depends on.

## 4. Where to buy (checked 2026-11-24)

| Vendor | Price per cell | Ships to | Notes | Link |
|---|---|---|---|---|
| 18650batterystore (CA store) | 35.00, currency ⚠️ (CA storefront) | North America | "Grade A", busbar + 2 bolts included, serial numbers, 1-year replacement warranty, test report on request | [en-ca](https://www.18650batterystore.com/en-ca/products/eve-lf105) |
| 18650batterystore (US) | $37.50 USD | US (GA warehouse) | Same | [us](https://18650batterystore.com/products/eve-lf105) |
| Battery Junction | $59.95 USD | US | 30-day warranty | [link](https://www.batteryjunction.com/products/eve-lf105) |
| 18650battery.com | $49.99 USD | US (Houston) | Sold out 2026-11-24 | [link](https://18650battery.com/products/eve-lf105-105ah-3-2v-lifepo4-prismatic-battery-grade-a) |
| NKON | €31.95 (€27.60 ×4) | EU | Good reviews; cells arrive voltage-matched | [link](https://www.nkon.nl/en/eve-lf105-prismatic-105ah-105a-lifepo4-a-grade.html) |
| Full Battery | ⚠️ not re-checked | US | The vendor named in v07–v13 docs. The reason it was picked isn't recorded. | — |

- The README budget uses **$65 per cell**, with no source. At today's prices it's high by about 40 %. ⚠️ Re-estimate it.
- "Regular price $99" strike-throughs are anchors, not market prices.
- Ignore Alibaba and AliExpress "EVE Grade A" listings unless a test report and QR date codes come with the order (§6).

## 5. Getting cells into Canada

Plan of record: order from a US reseller, ship to a parcel depot in Blaine, WA, and drive the cells across the border.

| Item | Value | Source |
|---|---|---|
| Duty | **7 % MFN** on tariff item 8507.60.90 (lithium-ion accumulators). The cells are Chinese-origin, so CUSMA doesn't apply | [Canada Gazette, SOR/2026-173](https://gazette.gc.ca/rp-pr/p2/2026/2026-08-26/html/sor-dors173-eng.html) (that order removes the duty only for e-bike manufacturing inputs) |
| China surtax | ⚠️ **Unchecked.** Canada's China Surtax Order (2024) has a 25 % schedule, and in 2024 batteries were consulted on for it. I couldn't read the schedule this session. | [SOR/2024-187](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2024-187) |
| Sales tax | 5 % GST at the border, plus ⚠️ BC PST | CBSA |
| Transport by car | TDG 1.15 exempts a purchaser carrying ≤ 150 kg gross, each container ≤ 30 kg | [TDG Regs s. 1.15](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2001-286/section-1.15.html) |
| Our load | 8 × 1.98 = 15.84 kg in one box | ✓ under both limits |

**Watch for:** couriers can't use the 1.15 exemption, which covers only the purchaser or the retailer. A courier shipment to Canada becomes a fully regulated Class 9 (UN3480) dangerous-goods shipment, which most small resellers refuse.

## 6. Traps found, and what to do about them

| # | Trap | What happened / why it matters | Rule now |
|---|---|---|---|
| T1 | Cell geometry sets the box | v05→v07: the box width was set by the cell width, and no orientation trick fixed it | Choose the cell from the required envelope, not the other way round |
| T2 | **Silent carry-over of cell-specific numbers** | The tie-rod heights for the 118.5 mm LF100MA were carried through 7 versions onto the 195.5 mm LF105. End-plate deflection was 0.655 mm, against 0.078 mm with the corrected layout (v13) | When the cell changes, re-derive everything that depends on its dimensions (rods, plates, spacers, straps, flex) |
| T3 | Terminal thread conflict | EVE rev B says M4; resellers say M6 | 6.6 mm busbar holes fit both. Confirm on the first cell. Torque ≤ 2 N·m for M4 |
| T4 | Burst rating comes from a reseller | The 500 A spec rests on "3C / 30 s" from a reseller page | ⚠️ Find it in the EVE spec. Otherwise derate to what EVE states |
| T5 | "Grade A" can't be verified from a listing | Resellers relabel B-grade cells; the cell QR code gives the production date and line | Scan every QR code. Reject date codes older than about 12 months. Ask for the vendor's test report |
| T6 | Parallel pairs hide a bad cell | The BQ76952 sees pairs, not cells. A 10 % IR mismatch at 630 A puts 3.14C on one cell | Same date code. Pair cells by 1 kHz AC IR. Voltage-match at 3.65 V before bolting (τ ≈ 36 min, 100 A inrush per 0.1 V) |
| T7 | Clamping | EVE rates cycle life with a 300 kgf fixture | End plates + 4 × M5 rods at 736 N each; assemble at 30–40 % SOC |
| T8 | Cold charging | Charging is allowed only from 0 to 55 °C | ESP32 inhibits the NPB-450 over CAN below 0 °C (M3) |
| T9 | Budget drift | $65 per cell entered once and never re-checked | Every price carries a date and a link |

## 7. Incoming inspection (do this before assembly)

1. Photograph every cell. Scan its QR code, log the date code, and check all are from one batch.
2. Measure OCV and 1 kHz AC IR for each cell. Accept AC IR ≤ 0.5 mΩ and OCV spread ≤ 20 mV ⚠️ (threshold to confirm).
3. Check the terminal thread with an M4 and an M6 screw by hand. Record the result in §3 and `v14-baseline.md`.
4. Pair cells by IR: sort them, then pair 1–2, 3–4 and so on. Put the pairs in series positions.
5. Top-balance all 8 cells in parallel to 3.65 V, rest them, then bolt the pairs together.
6. Run a capacity test on at least 2 cells at 0.5C ⚠️ (rig not designed yet). Also check the burst current on one pair if T4 is still open.

## 8. Open items
- ⚠️ T4: EVE's own pulse-discharge rating.
- ⚠️ China surtax status for 8507.60; BC PST on personal imports.
- ⚠️ Why Full Battery was picked, and its current price; choose the vendor.
- ⚠️ Re-estimate the budget at today's prices.
- Decide whether to buy a 9th cell as a matching spare (about $40).
