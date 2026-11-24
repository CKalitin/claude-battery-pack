# v14: 4S2P, 500 A power train, controls-only board

> **Current design.** It implements [`docs/v14-baseline.md`](../../docs/v14-baseline.md); every decision is justified in [`v14-design-review.md`](../../docs/v14-design-review.md) and [`v14-design-notes.md`](../../docs/v14-design-notes.md). ⚠️ marks a dimension modelled from an estimate, to replace once measured or once the manufacturer drawing is in hand.

![hero](renders/v14_01_hero.jpg)

*Renders are drafts (no anti-aliasing) for fast iteration; studio versions come at the next milestone.*

| At a glance | v13 | **v14** |
|---|---|---|
| Configuration | 8S1P, 25.6 V, 105 Ah | **4S2P, 12.8 V, 210 Ah** (2.69 kWh unchanged) |
| Rating | 105 A continuous / 315 A for 30 s | **210 A continuous / 500 A for 30 s** |
| DC output | Anderson SB50 | **2 × M10 copper terminal risers through the lid** |
| Power path | Straps bolted *to the PCB* ✗ | **Bolted copper:** Class T JJN-500 → TE EV200 → loads; Tesla shunt low side |
| Board | Power + control | **Controls only** |
| Converters | NTS-400P-124 / NPB-450-24 | NTS-400P-112 / NPB-450-12 |
| Envelope (L × W × H) | 379 × 206 × 389 mm | **389 × 206 × 390 mm** (+10 mm at the rear for converter service bays; terminals stay below the handle tops) |
| Body height | 316.6 mm | 318.1 mm (G10 deck 2 is 1.575 mm thicker) |
| Mass | 26.2 kg | **≈ 27.7 kg** (+1.1 kg copper, +0.4 kg power parts) |
| CAD | 83 parts | **90 parts, interference check clean** |
| Files | — | [`tower_a_v14_assembly.step`](tower_a_v14_assembly.step) · `cad/tower14.py` · `cad/run_tower14.py` · `cad/render_v14_nice.py` |

## What changed and why

| # | Change | Why | Ref |
|---|---|---|---|
| 1 | **4S2P**: 3 series bars across 4 terminals each (A +y cells 1–4, B −y 3–6, C +y 5–8); pairs alternate orientation; pack− and pack+ collectors both on −y | Owner decision D1: 500 A DC from 2 cells in parallel; no reconfiguration | R §0a |
| 2 | **Straps no longer touch the PCB.** COP-187 Z-straps: pack+ → fuse front blade; pack− → shunt node A | v13 put 315 A through PCB pads (review C1) | R C1 |
| 3 | **JJN-500 Class T** on a G10 power deck. Body rests on the deck; blades bolt to the pack+ flange and the line bar | Short-circuit current 5–7 kA needs a 20 kA interrupt rating | R C2, §0a |
| 4 | **EV200** (500 A continuous, coil economizer) on tray 1 | Rated for 500 A; 1.7 W hold | R §0a |
| 5 | **Tesla shunt** (35 × 83.5 mm ⚠️) on the G10 deck with a harness keepout ≥ 35 mm, plus a board cutout | Owner decision D3; owner measurements | [`tesla-shunt.md`](../../docs/tesla-shunt.md) |
| 6 | **Load bus + 2 MRBFs** (inverter 50 A, charger 30 A) on a riser in the drop zone | Branch protection; nothing on the PCB | R §0a |
| 7 | **M10 terminals** = COP-250 risers through lid slots with G10 .250 insulating plates; horizontal M10 holes, so the **lid lifts straight off** | 500 A; floating pack must not touch the aluminium lid; lid removal stays tool-light | R §0a, M8 |
| 8 | **Controls-only board**, 68 × 72 mm plus a tongue, at z 262 on 3 standoffs above the fuse and shunt | Owner decision (R4) | N §8 |
| 9 | **Terminal screws M4 × 8** (pole thread M4 × 6 ⚠️) | EVE spec rev B | R C3 |
| 10 | **Flex:** spine at y −17, 5 M3 taps into tapped busbars, ring + FR4 stiffener, **NTC on each tap tab**, tail up at x 146–148 to the board | Flex baselined; fusible taps; thermistors on the clamped joint | N §1 |
| 11 | **Front checkerboard:** 287 air holes (Ø6 in the diffuser and LED board vs Ø4.8 in the plate); panel fitted inside the ±93.4 mm interior; 4 M3 screws behind text pixels into module standoffs | No air inlet in v13 (review C4); v13 panel clashed with the walls | N §10, §10a |
| 12 | **Rear grid kept full** (looks). Cooling check: ≈ 10 K air rise at 75 W, thanks to the front air holes | Through-flow needs an inlet at the opposite end | N §11 |
| 13 | **G10 deck 2** (inverter isolation); inverter screws M3 × 5 (1.8 mm penetration ≤ 2.5) | Floating pack; inverter DC input assumed bonded to its case | R M6 |
| 14 | **Antenna** behind the light-pipe slot; ESP32-S3-WROOM-1U | Metal box ≈ 26 dB loss | R C5 |
| 15 | **Lid:** outlet, C14 inlet, **push-button**, 2 terminal slots; M12 and Anderson removed | Button-only wake; CAN is internal | N §9a |

## Key checks

| Check | Value | Result |
|---|---|---|
| Series bar at 500 A, 30 s, adiabatic | J = 500 / (25 × 3.175) = 6.3 A/mm², ΔT = J²ρt/c_v = **5.9 K** | ✓ |
| Pack straps, COP-187, 25 mm | J = 4.2 A/mm², ΔT = 2.6 K | ✓ |
| Terminal risers, COP-250 | J = 3.1 A/mm² | ✓ |
| Fuse top vs board underside | 258.2 vs 262.0 mm | ✓ 3.8 mm |
| Line bar (z 292–297) vs board components (≤ 279) | — | ✓ |
| Inverter top vs lid inner | 314.7 vs 316.5 mm | ✓ 1.8 mm |
| Load-bus tab top vs lid inner | 303.5 vs 316.5 mm | ✓ |
| Shunt harness keepout | connector top 236.6 → ≥ 271.6, through a board cutout | ✓ |
| LED board vs tray 1 | tray 1 ends at x 169.05, LED board starts at 169.95 | ✓ |
| Terminal-riser lid slots vs the lid's flat-to-facet edge | y −74 vs −76.4 | ⚠️ 2.4 mm; check SendCutSend's hole-to-bend rule |
| Interference (90 parts, pairwise) | — | **none** |

## Modelled from estimates (⚠️, replace when known)

- **EV200 outline:** 66 × 81 base, body Ø60 × 72.3, M8 studs 12.6 tall, 52 mm apart. TE's drawing wasn't retrievable; measure the part or get the drawing.
- **JJN-500:** 31.8 × 77.8 mm is confirmed; blade length 14, thickness 4.8 and width 25.4 are estimates.
- **MRBF:** 22 × 20 × 8 mm.
- **Tesla shunt:** bolt size (M8 placeholder), connector position.
- **SendCutSend COP-187 / COP-250 bend rules:** min flange and joggle not yet checked; both risers are long (≥ 22 mm).
- **LF105 pole thread.**

## Plain renders (fast, current)

| | |
|---|---|
| ![](renders/v14p_01_hero.jpg) | ![](renders/v14p_02_rear.jpg) |
| ![](renders/v14p_03_lid_off.jpg) | ![](renders/v14p_04_power_pcb.jpg) |
| ![](renders/v14p_05_busbars.jpg) | ![](renders/v14p_06_front.jpg) |
| ![](renders/v14p_07_panel.jpg) | ![](renders/v14p_08_terminals.jpg) |
| ![](renders/v14p_09_section.jpg) | ![](renders/v14p_10_pcb_exploded.jpg) |
| ![](renders/v14p_11_connections.jpg) | ![](renders/v14p_12_service_bays.jpg) |

## Gallery (studio drafts; predate the service-bay change)

| | |
|---|---|
| ![lid off](renders/v14_03_lid_off.jpg) | ![power](renders/v14_04_power.jpg) |
| Lid off | Power train |
| ![busbars](renders/v14_05_busbars.jpg) | ![front](renders/v14_06_front.jpg) |
| 4S2P busbars + flex | Front checkerboard |
| ![panel](renders/v14_07_panel.jpg) | ![top](renders/v14_08_top.jpg) |
| LED panel sandwich | Lid |
| ![rear](renders/v14_02_rear.jpg) | ![section](renders/v14_09_section.jpg) |
| Rear grid | Section at the fuse axis |
| ![pcb](renders/v14_10_pcb_exploded.jpg) | |
| Control board lifted from its spot | |

---
← [v13](../v13-lip-rods-zstraps/README.md) · [index](../README.md)
