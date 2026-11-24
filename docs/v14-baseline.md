# v14 baseline: the spec the v14 CAD is built to

**One page, everything decided as of 2026-11-24.** Each line points to where its justification lives:
- **R** = [`v14-design-review.md`](v14-design-review.md)
- **N** = [`v14-design-notes.md`](v14-design-notes.md)
- **S** = [`tesla-shunt.md`](tesla-shunt.md)

⚠️ = unconfirmed input; the design tolerates it until it's measured.

## Pack

| Item | Baseline | Ref |
|---|---|---|
| Cells | 8 × EVE LF105, **4S2P fixed**. 12.8 V nominal (10.0–14.6 V), 210 Ah, 2.69 kWh | R §0a |
| Rating | **500 A for ≤ 30 s, 210 A continuous** (1C continuous, 3C for 30 s per cell) | R §0a |
| Busbars | COP-125, 25 mm. Series bars A (+y, cells 1–4), B (−y, 3–6), C (+y, 5–8); collectors pack− (−y, 1–2) and pack+ (−y, 7–8); pairs alternate orientation | R §0a |
| Terminal screws | M4 × 8 A2 flange head + washer, ≈ 2 N·m. Holes 6.6 mm (also fit M6) ⚠️ thread | R C3 |
| Pack straps | COP-187, 25 mm, Z-joggles; land on the fuse and shunt, never the PCB | R C1, §0a |
| Compression | 4 × M5 rods at 0.207 h / 0.793 h; 736 N per rod (≈ 0.74 N·m); assemble at 30–40 % SOC | v13, R m3 |
| Matching | Same date code; pair by 1 kHz AC IR; voltage-match at 3.65 V before bolting | N §7 |

## Power path (all bolted copper, nothing on the PCB)

| Item | Baseline | Ref |
|---|---|---|
| Main fuse | Bussmann **JJN-500** Class T (31.8 × 77.8 mm, 20 kA at 160 VDC), bolted between the pack+ strap and the contactor | R §0a |
| Contactor | TE **EV200**, 500 A continuous, built-in coil economizer (1.7 W hold), coil straight from the pack; mounts to tray 1 through a board cutout | R §0a |
| Precharge | 10 Ω / 10 W + small relay; close the contactor at ≥ 95 % of stack voltage, 0.5 s timeout | R C7 |
| Shunt | Tesla module, low side, VSS at node A (⚠️ bonded end inconclusive); R_sh ≈ 20 µΩ ⚠️ | S |
| Branch fuses | MRBF on the load bus: inverter 50 A, charger 30 A | R §0a |
| DC output | 2 × M10 terminals on COP-250 bars through a G10 .250 lid plate, with boots | R §0a |
| Isolation | Pack floats; IMD = 2.2 MΩ / (900 k + 100 k) divider into the ESP32, r₀ = 0.312, trip ±0.02 | N §2, §4 |
| Earth | Inlet PE + outlet ground → body, via a lug under an existing front-plate screw | R M7 |

## Converters and AC

| Item | Baseline | Ref |
|---|---|---|
| Inverter | NTS-400P-112. Power-saving DIP SW4 on; remote off via PhotoMOS; **G10 .125 deck 2**; M3 × 5 screws (≤ 2.5 mm penetration) | R §0a, M2, M6 |
| Charger | NPB-450-12, 25 A, **2-stage, 14.2 V** over CAN; remote ON-OFF wired; CAN to the ESP32 | R §0a, M3 |
| Charge time | 210 Ah / 25 A ≈ 8.4 h | R §0a |
| AC outlet | Floating output; outlet ground to chassis; no GFCI | N §3 |

## Control board (controls only)

| Item | Baseline | Ref |
|---|---|---|
| AFE | BQ76952, 5 sense taps (VC0–VC4). **Thermistors: one 0603 NTC on each of the 5 flex tap tabs**, right beside the M3-clamped ring, so it senses the busbar and terminal, which is the cells' best thermal path, between each cell pair; plus 1 on the board near the fuse and contactor. 6 of the BQ76952's 9 thermistor inputs | R m5 |
| MCU | **ESP32-S3-WROOM-1U** + flex antenna behind the light-pipe slot | R C5 |
| Supply | Battery side of the contactor, 2 A fuse → 5 V buck (EN ← BQ REG1) → 3.3 V. No 12 V rail | N §9 |
| Shunt interface | 5 V supply; level shifter (TXU0104) on SPI; J1 = 10-pin Mini-Fit ⚠️ | S §3 |
| Protection | Contactor enable = ESP32 AND BQ76952 status (hardware). Under-voltage ladder: 2.90 V firmware off → 2.80 BQ UV → 2.75 inverter → **2.60 BQ SHUTDOWN (board off, ≈ 7 µA)** | R M4, N §9 |
| Latch | Every UV trip latches; re-enable needs a button press with minimum cell ≥ 3.00 V | N §9a |
| Wake | **Lid push-button → TS2 only.** Long press = off. Charger wake **deferred** | N §9a |
| Charge inhibit | Below 2 °C cell temperature (EVE: 0–55 °C) | R M3 |
| Group check | R_g = ΔV_g / ΔI per load step; flag > 1.6 × median (an open cell in a pair) | N §5 |

## Sense flex

| Item | Baseline | Ref |
|---|---|---|
| Type | **Flex** (chosen over rigid FR4); tail plugs into the control board | N §1 |
| Taps | M3 into SendCutSend-tapped busbar holes, mid-span, 5 mm from the edge on the spine side; FR4 stiffener behind each ring; S-loop tabs | N §1 |
| Robustness | Inside corners R ≥ 1 mm + tear-stops; tail bend ≥ 3 mm with no vias, pads or pours in it; spine taped down; **fusible necked trace at each tap** | N §1 |

## Enclosure and thermal

| Item | Baseline | Ref |
|---|---|---|
| Body | v13 shell: 3 × 30° corners, L-halves, body lead-in lip, Gloss Red | v13 |
| Front panel | **Checkerboard**: alternate lit and air holes through the diffuser + LED board (≈ 5,200 mm² open); "WE WILL WIN" stays as unlit pixels | N §10 |
| Panel mount | Diffuser + LED board sandwich, 4 M3 screws into standoffs on the module's front end plate; air holes Ø6.0 vs Ø4.8 mm in the plate; fit inside the ±93.4 mm interior | N §10a |
| Rear plate | Remove the holes in the deck zone outside the fan circle | R C4 |
| Fan | NF-A14 **5 V PWM** (pack voltage would over-drive the 12 V model) | R §0a |
| Lid | NEMA 5-15 outlet, IEC C14 inlet, M10 terminal plate, push-button; **no M12**; 150 mm service loops | R §0a, M8, m4 |
| Converter fans | Point intakes toward the board side (verify from MEAN WELL drawings) | R C4 |

## Unconfirmed inputs (the design tolerates them; measure later)

- ⚠️ LF105 terminal thread (M4 × 6 per EVE rev B vs M6 resellers). Check on the first delivered cell.
- ⚠️ Tesla shunt: R_sh, bonded end, bolt thread, connector part number and orientation, J1 pins 8–10. Owner will characterise later (S §7).
- ⚠️ +12Vaux behaviour with AC off (only matters if charger wake comes back).
- To pull from datasheets during the CAD: EV200 and JJN-500 outlines and hole patterns, SendCutSend COP-187 bend rules, MEAN WELL fan directions.

## Deferred (not blocking the v14 CAD)

- Charger or AC wake.
- Shunt characterisation.
- Telemetry dashboard ([`telemetry-ideas.md`](telemetry-ideas.md)).
- Firmware.
- Using the shunt's J1 pin 7 as a hardware over-current trip.
- SendCutSend v14 quote.
