# Owner requirements and standing decisions

**The project's long-term memory.** Anything Chris has asked for, decided or ruled out lives here, with the date. Chat memory is not kept between sessions. If a requirement isn't in this file (or in a doc it links to), assume it will be forgotten.

- **Rule:** when Chris states a requirement, preference or decision in chat, add it here in the same session, with the date.
- Decisions with losing options still go in the current decision table (`v16-decisions.md`); this file holds the one-line rule and a link.

## 1. Goal and scope
| Requirement | Since |
|---|---|
| Claude designs a complete ~1 kWh+ battery pack end to end (electrical, mechanical, firmware, every PCB) to show Claude can do hardware design. Built in public (X, LinkedIn, GitHub, blog) | project start |
| ~1 kWh minimum; now 8 × EVE LF105, **4S2P fixed**, 12.8 V, 2.69 kWh (cells.md) | v14, Nov 2026 |
| Built-in 120 V charger (≈ 450 W, ~3 h) and 120 V outlet (400 W inverter; relaxed from ~1 kW to keep the box small) | early |
| DC output: **175 A** continuous (SB175), burst rating below | Nov 2026 |
| Debug info easy to reach: Wi-Fi (ESP32) telemetry | early |
| Off-the-shelf AFE for cell monitoring and balancing (BQ76952) | early |
| Keep Chris's Tesla Model S shunt module in the pack (tesla-shunt.md) | v14 |
| Pack floats from chassis; simple divider-type IMD read by the ESP32 | v14 |

## 2. Manufacturing and assembly
| Requirement | Since |
|---|---|
| Assembly ≤ about one night of wrench work. Pre-cut parts and a few bolts; extra cost is acceptable to save assembly time. Chris will not lay up composites | project start |
| Every fabricated part from SendCutSend or a catalog ("if SendCutSend can't do it, you're likely incorrect"). Protolabs only for large-radius bends, and only if ≤ 1.5× the SendCutSend cost | early |
| **SendCutSend order < $2,000 USD** (SendCutSend sponsorship) | 2026-11-27 |
| No parts that need emailing a vendor; no sketchy datasheets; cite the manufacturer's own document | early |
| Every part installable top-down in the README order | v16 |
| Bent SCS parts quoted from DXF flats with bend lines (`cad/flats15.py`) | 2026-11-27 |

## 3. Layout and look
| Requirement | Since |
|---|---|
| Busbars on top. Prefer busbars over cables (less assembly) | early |
| Tall, narrow tower proportions; cells upright (on-edge and squat layouts rejected) | early |
| Charger and inverter stacked; control electronics on the front PCB's back, facing the bay | v12–v15 |
| Don't grow the envelope without a reason; no dead space. **2026-11-27: Chris dislikes the empty rear end (fan + AC column + cell-level void, ≈ 91 mm behind the module) — layout to be reworked** | early / 2026-11-27 |
| Full rear hole grid (looks better) | v14 |
| Roadster-red gloss powder coat on the shell | v12 |
| The pack has no name. Never "Tower A" | 2026-11-24 |
| Renders: label only parts visible in that view | Nov 2026 |

## 4. Engineering principles
- Best part is no part; simplest design wins; remove a failure by removing the part.
- Separate + and − by distance, not plastic insulation (plastic tears): + to − ≥ 10 mm, pack copper to chassis ≥ 7 mm.
- Purchased parts are never modified.
- Every exploration is documented, with its losing options (CLAUDE.md).

## 5. Electrical baseline decisions
| Decision | Since | Ref |
|---|---|---|
| **Burst rating is a firmware rating.** 500 A for ≤ 30 s is allowed only where EVE's 30 s pulse MAP allows ≥ 2.38C per cell: ≥ 30 % SOC and ≥ 10 ℃. Elsewhere the firmware caps discharge at 2 × 105 A × C_MAP(T, SOC), and continuous at 2 × 105 A × C_cont(T, SOC) (EVE rev E Tables 12–13). The hardware (fuse, copper, contactor) is sized for 500 A; the firmware is what keeps the cells inside their rating. **Every future rating is stated this way: hardware capability plus the firmware limit that enforces the cell spec.** | 2026-11-27 | cells.md T4, D37 |
| Wake is button-only: a charger plugged into a sleeping pack does nothing until the button is pressed | 2026-11-27 | D33 |
| Cell-sense board is a flex PCB, screwed (M3) into tapped busbars | v14 | design notes §1 |
| Control board is controls-only, on the back of the front LED board; no separate slot-in BMS board | v14–v15 | power-train.md |
| Compression rods M6 316 (A4-70), sized for EVE's EOL swelling ≤ 30 kN | 2026-11-27 | structure.md, D36 |

## 6. PCB sponsorship and fabs
- **NextPCB (Zep)** is the PCB sponsor (2026-11-25). Their offer (2026-11-26): either sponsor the front board's revisions, or a fixed amount per round. Chris prefers **front board only, fab + assembly, up to 3 rounds**.
- **Flex PCB: shop around** (Chris, 2026-11-27). Don't commit the flex to NextPCB; quote it at several fabs and pick the cheapest that meets the spec.
- PCBWay (Liam) declined politely on 2026-11-26; Chris would work with them on a later project.
- Assembly (PCBA) wanted on both boards, the flex included.

## 7. Open items Chris has asked for (carry until done)
- Rework the layout so the rear void disappears (2026-11-27: "take two steps back… I want to solve this problem", not a 10 mm trim): study in architecture.md, **Chris picked B (side power spine) on 2026-11-27.** **Keep the GV14 contactor** (Chris, 2026-11-27), so W 190 → 204 mm: the 55.7 mm contactor body passes beside the 135 mm charger, and a 190 box leaves a 48.8 mm strip (13.3 mm short). See option_b_width.png.
- Inverter 400 W continuous: bench test, then decide the cooling fix (cooling.md).
- Control board schematic: a separate agent, later.
- Send the Zep reply (draft in Gmail).
