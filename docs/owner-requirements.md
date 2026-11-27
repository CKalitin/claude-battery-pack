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
| **Cells are the dominant constraint: everything above the cells (converters, power bay, control board) fits inside the plan footprint of the cells' top faces; nothing goes past it.** "We're setting the area as the top of the cells as the constraint, and you're not allowed to go above that." The charger and inverter caused the overrun, so replace them (handoff-converters.md) **Footprint = the module including the end plates (≈ 312 × 158 mm)** (Chris, 2026-11-27). No height cap above the cells, "but be reasonable" | 2026-11-27 |
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
| **Charger internal, ≥ 17 A** (≈ 12 h); **inverter ≥ 300 W** continuous, priority: **combined inverter-charger ("extremely ideal")** > separate internal inverter > last resort only if an internal inverter is really impossible: no internal inverter, USB-C PD out, maybe an external inverter | 2026-11-27 | handoff-converters.md §2d |
| **Converters: separate units, option D** (NPB-360-12TB 20 A + NTS-400P-112 + its 40 mm fan), chosen over the upright MultiPlus combined unit. **No USB-C PD port for now.** **Charger stop: NPB-360 + a normally-open DC relay in the charger + lead** (chosen over PB-230-12 once it was clear the PB-230 has no CAN) | 2026-11-27 | converters.md, D39 |
| **BMS board 95 × 55 mm is FINAL** at x −105…−10, y −15…40, reserved as is; the layout aims for credit-card size inside it (Chris to pcb, 2026-11-27, relayed; lanes/pcb/bms-area.md §10) | 2026-11-27 | spec §4 |
| **BMS board scope confirmed** (Chris, 2026-11-27): BQ76952 cell monitor/balance/protection; ESP32-S3 brain and Wi-Fi telemetry; Tesla shunt SPI (level shifter, 5 V); GV14 coil driver (ESP32 AND BQ in hardware) + precharge (**2 series P-MOSFETs + AC05 10 Ω**, replacing the relay: Chris to pcb, 2026-11-27, relayed); inverter remote off; charger relay coil; fused pack tap → 5 V buck → 3.3 V, SHUTDOWN ≈ 7 µA, UV latch; IMD divider; lid button + LED-board link. No power current. CAN transceiver and pack-fan header dropped (option D). Size and place it after this | 2026-11-27 | converters.md §6 Q3 |
| Wake is button-only: a charger plugged into a sleeping pack does nothing until the button is pressed | 2026-11-27 | D33 |
| Cell-sense board is a flex PCB, screwed (M3) into tapped busbars | v14 | design notes §1 |
| ~~Control board is controls-only, on the back of the front LED board; no separate slot-in BMS board~~ **Reversed 2026-11-27: Chris prefers a separate BMS board. The front zone is preferably for the LED board only.** | v14–v15 → 2026-11-27 | power-train.md, handoff-converters.md |
| Compression rods M6 316 (A4-70), sized for EVE's EOL swelling ≤ 30 kN | 2026-11-27 | structure.md, D36 |

## 6. PCB sponsorship and fabs
- **NextPCB (Zep)** is the PCB sponsor (2026-11-25). Their offer (2026-11-26): either sponsor the front board's revisions, or a fixed amount per round. Chris prefers **front board only, fab + assembly, up to 3 rounds**.
- **Flex PCB: shop around** (Chris, 2026-11-27). Don't commit the flex to NextPCB; quote it at several fabs and pick the cheapest that meets the spec.
- PCBWay (Liam) declined politely on 2026-11-26; Chris would work with them on a later project.
- **Fab split (Chris, 2026-11-27): BMS board → PCBWay (full PCBA); front/LED board → NextPCB** (sponsored, as above). Flex: shop around. "Put more effort into sourcing the PCBs." ⚠️ PCBWay declined *sponsorship* on 2026-11-26, so the BMS board is a paid order unless PCBWay is re-approached (Chris to decide). Supersedes the relayed "BMS by NextPCB, PCBWay second".
- **Tentative (Chris to the pcb lane, 2026-11-27; relayed by pcb): "we may use NextPCB for this board" (the BMS).** Not final: the PCBWay split above stands until Chris decides, and BMS sponsorship at NextPCB is pending Zep's answer. pcb designs to rules both fabs meet, with an MPN-based BOM, so there is no design impact.
- **Re-offer to NextPCB (Chris, 2026-11-27): ask for one sponsored round of both rigid boards (front + BMS), fab + PCBA, instead of 3 rounds of the front board only.** **Sent to Zep 2026-11-27** (reply to his 2026-11-26 offer); the 3 older drafts were deleted. Awaiting his answer. If NextPCB says no, the BMS board goes to PCBWay as a paid order (split above).
- **BMS schematic must be human-readable:** parts drawn wired together, not only connected by net labels (Chris to the pcb lane, 2026-11-27; relayed by pcb).
- Assembly (PCBA) wanted on both boards, the flex included.

## 7. Open items Chris has asked for (carry until done)
- Rework the layout so the rear void disappears (2026-11-27: "take two steps back… I want to solve this problem", not a 10 mm trim): study in architecture.md, **Chris picked B (side power spine) on 2026-11-27.** **Keep the GV14 contactor** (Chris, 2026-11-27), so W 190 → 204 mm: the 55.7 mm contactor body passes beside the 135 mm charger, and a 190 box leaves a 48.8 mm strip (13.3 mm short). See option_b_width.png. Packing check then showed W 204 is too narrow for an all-busbar spine; awaiting choice B1/B2 (architecture.md §4a). **Superseded the same day:** Chris traced the root cause to the charger and inverter and reopened their selection under the cell-footprint rule (§3). Option B is paused; see `docs/handoff-converters.md`.
- ~~Find a new charger + inverter (or a combined unit) that fits within the cells' top-face footprint~~ → option D picked 2026-11-27 (`docs/converters.md`, D39). Next: BMS board responsibilities, then CAD.
- Inverter 400 W continuous: bench test, then decide the cooling fix (cooling.md).
- **Cooling / rear-plate hole spacing at the inverter fan: iterate after the option D CAD** (Chris, 2026-11-27). Options on the table: Ø6.5 holes in front of the 40 mm fan + charge-pause thermostat; blanking sheet; second fan (converters.md §4).
- Control board schematic: a separate agent, later.
- Await Zep's answer to the one-round, both-boards ask (sent 2026-11-27).
