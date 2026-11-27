# Signal and low-power wiring (v16.1, 2026-11-25)

Every lead that isn't pack copper or a converter power lead: shunt, contactor coil, board supply and sense taps, converter control, fan, lid button, antenna, and the AC mains leads. All of them are modelled as parts in `cad/concepts/contactor/harness.py`: a plug at each end, the wire bundle as a tube along its route, ring terminals on existing studs, inline fuse holders, and cable ties. They are included in the power-module check (`c1_power_module.py gv14up`: 0 interferences) and in the assembly check (`cad/assembly_v16.py`). Lengths and bundle sizes come from `calcs_v16.py` §9 ([v16-calcs.txt](v16-calcs.txt)).

Renders: `versions/v16-c1-power-module/renders/harness_*.jpg` (iso, top, shunt close-up, board end, fan lead).

## 1. Requirements

| # | Requirement | From |
|---|---|---|
| R1 | Tesla shunt lead leaves the J1 connector on the **side the connector overhangs the copper** (+x, toward the front board), wires straight up | Owner 2026-11-24; [tesla-shunt.md](tesla-shunt.md) §2 |
| R2 | **No new holes in purchased parts**; ring terminals only on studs that already carry a joint | Owner rule (CLAUDE.md) |
| R3 | The **Z-strap must come out** (service disconnect) with every lead in place, lid off | v16 D2; assembly check |
| R4 | **Every MRBF fuse must lift out** after only its own lug and nut are moved | v16 D6; assembly check |
| R5 | **Every nut can take a socket** (thin-wall 3/8″ drive: M6 15 mm, M8 18 mm, M10 23.5 mm OD) after the leads are in | Found in this pass (T12–T14) |
| R6 | Every wire tapped off pack copper is **fused at the source end**, within 178 mm (7 in) along the wire | ABYC E-11 (fuse within 7 in of the source) ⚠️ wording from memory, not re-read |
| R7 | Connectors mate **from above** (top-down assembly) | Owner rule |
| R8 | Board ground at **node A** (the cell side of the shunt) | [tesla-shunt.md](tesla-shunt.md) §1, §5 |
| R9 | Mains wiring never bundled with low-voltage leads | Good practice |
| R10 | Long runs supported (ties into slots in our own G10 parts) | Owner: "converter cable runs supported" |

## 2. What was built

| Lead | Wires | From (device end) | To (board) | Route | Length ✓ model |
|---|---|---|---|---|---|
| Shunt | 7 × 22 AWG | Tesla J1, Mini-Fit Jr 2×5 ⚠️ on the +x overhang | j_shunt, Micro-Fit 3.0 2×4 | Straight up 30 mm, +y to y 7 (outside the Z-strap prism), over the contactor at z 312, along the plug tops, down into the plug | 188 mm |
| GND | 1 × 18 | Ring (M8) under a new **node-A nut** (the model had none, T15) | j_pwr pin 3 | Up beside node A, +y at z 280, up between the SB175 and the contactor at y 2, over the contactor | 217 mm |
| B+ | 1 × 18 | Ring (M6) under the Z-strap foot nut: in-bar, after the 250 A fuse, before the contactor | j_pwr pin 1 | Tongue −x; 2 A ATM holder upright at x 97; up and over the contactor | 112 mm |
| LOAD+ | 1 × 18 | Ring (M8) on the 2151 inverter-fuse stud, on top of the inverter lug, under the washer | j_pwr pin 2 | Tongue −y; 2 A ATM holder lying flat on the contactor top along −y | 121 mm |
| Coil | 2 × 20 (the GV141BAX's own 38 cm flying leads, cut and crimped) | Contactor top (lead exit ⚠️ not dimensioned by Gigavac) | j_coil 1×2 | Up and +x | 53 mm |
| Converter control | 4 × 24 (charger DF11: remote, CAN H/L) + 2 × 24 (inverter CN301: remote) | DF11 ⚠️ pin count; JST XHP-2 | j_conv 2×4 | DF11 lead tied to tray 1 (2 slots at x 46), up to a junction, along the −y wall corridor (y −86), up over the plug tops | 95 + 47 + 183 mm |
| Button | 2 × 22 | Lid push-button | j_btn 1×2 | Along the −y wall corridor; 250 mm service loop so the lid can stand beside the pack | 114 mm + loop |
| Fan | 4 × 24 (Noctua lead + NA-EC1 extension) | NF-A14 frame corner | j_fan (2.54 mm 4-pin) | Along +y on tray 2 at y 64 (two ties through tray-2 slots), past the SB175 at y 68.5, over the contactor at y 50 | 418 mm |
| Antenna | 1.13 mm coax | ESP32-S3-WROOM-1U U.FL | Flex antenna above the board edge | Along the board's back at z 275, below the headers | 110 mm |
| AC in / out | 3 × 16 each | Lid C14 inlet / inverter CN500 | Charger C14 (right-angle C13) / lid outlet | Rear only (v15 routes, restored: the v16 merge had dropped them with the `cable_` prefix, T16) | — |
| IMD chassis reference | **none** | — | — | One board mounting hole is plated and lands on a metal panel standoff (module front end plate = chassis). The best part is no part. | — |

**Two runs to the board.** Everything reaches the board's top-edge headers by one of two runs, and neither crosses the Z-strap prism (x 106.6–153.5, y −78.9…−2) or a fuse lift-out prism:
- **S run** (over the contactor, y 0…11, z 303–315): shunt, GND, B+, LOAD+, coil.
- **N run** (along the −y wall, y −84…−86.5, z 286–292): converter control, button.

The wires then run along x 162–168 above the plug tops and drop into their plugs.

## 3. Choices explored

### 3a. Where the board headers go
| Option | Result |
|---|---|
| **Top edge of the board's back face, right-angle Micro-Fit, plug mates from above** | **Chosen.** Mates top-down (R7); 8 mm board-to-end-plate gap rules out anything below z 192 ([power-train.md](power-train.md) §8) |
| v15 scattered `conn_harness`/`conn_shunt` blocks at z 270–281 | Dropped. They sat on top of air holes in the LED board (T17) and mated horizontally |
| One big harness connector | Rejected. One plug for coil + shunt + fan + button means the button lead (lid) and the shunt lead share a plug, and any lid removal unplugs the shunt |

### 3b. B+ tap (board supply + precharge source)
| Option | Result |
|---|---|
| **Ring under the Z-strap foot nut (in-bar)** | **Chosen.** Downstream of the main fuse; dead when the strap is out (service disconnect kills the board too) |
| Ring on the 5191 M10 stud (before the fuse) | Rejected: stays live with the strap out |
| Ring on the strap's fuse-top nut | Rejected: comes off with the strap and then dangles on a live stud |
| New tapped hole in the in-bar | Rejected: only y −2…4 of the in-bar is not under the contactor, too narrow for a ring |

### 3c. LOAD+ tap (precharge target + load-bus sense)
| Option | Result |
|---|---|
| Ring under the 2151's M10 mounting nut (x 70.7) | Tried first. The lead then has to get round the SB175, which runs from the plate to above the lid at x 58–83, and every route crossed the converter leads |
| Tapped hole in our load bar | No free load-bar surface ≥ 7 mm wide outside the contactor, the 2151 and the SB175 |
| **Ring on the 2151 inverter-fuse stud, on top of the 90° lug** | **Chosen.** No new hole; the stud already carries a ring. Senses the load bus through the 50 A MRBF, so a blown inverter fuse reads as "precharge never completes", which is a useful fault in itself |

### 3d. Fusing the taps (R6)
| Option | Result |
|---|---|
| **Eaton Bussmann ATM-FHID inline holder, 2 A ATM fuse, per tap** | **Chosen** for B+ and LOAD+. 39.6 × 10.4 × 15.0 mm, 16 AWG leads |
| Rely on the board's 2 A fuse | Rejected: it doesn't protect the 18 AWG wire between the tap and the board |
| Rely on the upstream MRBF (LOAD+ through 50 A) | Rejected: 18 AWG adiabatic withstand ≈ (143 × 0.82)² ≈ 1.4 × 10⁴ A²s, i.e. ~55 ms at 500 A; MRBF at 10× is only "< 0.2 s" (Bussmann). Not proven safe |
| Fusible-link wire | Considered; not needed once the ATM holder fitted |

Placement found by trial against the model: the first LOAD+ holder position (upright at x 162) had only 13 mm of height under the lid for a 39.6 mm holder (T18 below). Final: lying flat on the contactor top.

### 3e. Shunt lead side (R1)
The Tesla module's PCB overhangs the bar by 8 mm on its +x long edge, and J1 sits on that overhang ([tesla-shunt.md](tesla-shunt.md) §2). +x faces the front board, so the lead goes straight up and then toward the board. The plug envelope (Mini-Fit Jr 2×5, 9.6 × 21 × 13 mm ⚠️) covers 21 of the strip's 25 mm, so the route holds whichever end of the strip J1 turns out to be at.

## 4. Traps found (rules added)
| # | Trap | Rule |
|---|---|---|
| T12 | **Z-strap foot nut could not be fitted.** M8 washer Ø17 between the strap leg (y −10.8) and the contactor body (y 4.1): 14.9 mm of room. Hidden by an ALLOW pair | Foot stud → **M6** carriage bolt at y −4.3; leg moved 3 mm to −y (in-bar extended to y −17). CDA busbar practice is M6 for a 14 mm wide bar. New rule: every nut gets a socket check (`assembly_v16.py`) |
| T13 | **Leads routed over nuts.** Inverter + lead over both 2151 nuts; inverter − lead over the node-B nut; GND barrel and LOAD+ barrel inside socket walls | Routes moved; inverter − lug barrel offset 12 → 14 mm; ring barrels start 3.5 mm beyond the ring |
| T14 | **First harness crossed the Z-strap prism** (shunt, GND and converter leads went straight from the bay to the board): the service disconnect could not come out | Two runs (S and N) outside every service prism; the strap's 150 mm sweep is part of the check |
| T15 | **Node-A carriage bolt had no nut** in the model | Nut + washer added (with the GND ring) |
| T16 | **v16 merge dropped the AC leads and the fan lead** (they shared the `cable_` prefix with the v15 bay cables) | Restored in harness.py; the fan lead re-routed |
| T17 | **Control parts sat on LED-board air holes** (v15 layout) | Air holes under any control part (+2.5 mm) removed: 287 → 244 air holes (`tower15.CTRL`, `ctrl_blocks`) |
| T18 | Inline fuse holder modelled as a Ø10 capsule fitted anywhere; the real holder is 39.6 × 10.4 × 15 mm | Model the catalog envelope (Bussmann ATM-FHID) |
| T19 | Coil-lead exit assumed at the base end; the GV14 drawing puts it on the cap rim, 90° from the terminals, which inverted faces the 2151 at 0–4 mm. Rotating the contactor 180° is not allowed: the break rating is for A1(+) → A2(−) only (GV14 rev 28-Apr-2022 p. 6) | Read the lead exit off the drawing before placing anything against a relay or contactor face |

## 5. Sources
| Value | Source | |
|---|---|---|
| GV141BAX coil B: 3.9 A pick-up (75 ms), 0.23 A hold, 2.8 W; flying leads A = 38 cm; red X1+, black X2− | Gigavac GV14 datasheet, Rev 28-Apr-2022 (RS-hosted copy) | ✓ |
| Coil lead exit: X1/X2 leave through two notches in the cap rim (terminal end), 90° from the A1–A2 axis, opposite the aux notches. Inverted with A1(+) at −x, that is the +y face, at the copper. Exit height in the notch not dimensioned | Sensata GV14 datasheet rev 28-Apr-2022 p. 3 (upright-mount top view), read 2026-11-27 | ✓ side / ⚠️ height |
| NTS-400P CN301: 2-pin, open = run, short = remote off, JST S2B-XH-A; CN100: fan 12 V 0.4 A, PWM, JST XH 3-pin | MEAN WELL NTS-400P-SPEC 2026-03-26 / 2023-12-11 | ✓ |
| NPB-450 control connector: HRS DF11-14DP on the unit, mate DF11-14DS + DF11-**SC crimps. 1 A1, 2 A0 (CAN address; NFC model: N.C.), 3 +3.3 V, 4 GND(signal), 5 Battery Full, 6 Charger OK (TTL, ref GND-AUX), 7 Remote ON-OFF (short to 8 = on), 8 +12 V aux, 9–10 GND-AUX, 11 CANH, 12 CANL (isolated, ref GND-AUX), 13–14 NTC 5 k | MEAN WELL NPB-450-SPEC 2026-07-06, read 2026-11-27. The A0/A1 order differs between two tables in the same file ⚠️ (not used: address set by DIP/app) | ✓ |
| Tesla J1: 10-pin Mini-Fit (U), pins 1–7 | [tesla-shunt.md](tesla-shunt.md) §3 | ⚠️ |
| 18 AWG 105 °C = 20 A; 10 AWG 105 °C = 60 A (30 °C); × 0.85 at 50 °C | 33 CFR 183.425 table 5 (= ABYC E-11 table) | ✓ |
| ATM-FHID 1.56 × 0.41 × 0.59 in, 16 AWG, 20 A | Zoro listing (Eaton Bussmann), 2026-11-25 | ✓ |
| Micro-Fit 3.0 43025-0800: 3.0 mm pitch, 5 A per circuit | Molex via RS/Digi-Key listings, 2026-11-25 | ✓ |

## 6. Buy list (prices 2026-11-25)
| Item | Part | Qty | Price | Link |
|---|---|---|---|---|
| Inline fuse holder, ATM, 16 AWG | Eaton Bussmann ATM-FHID | 2 | $9.49 ea | zoro.com (item G1285042) |
| ATM fuse 2 A | Littelfuse 0297002 or equal ⚠️ not priced | 2 + spares | ~$1 ⚠️ | — |
| Micro-Fit 3.0 receptacle 2×4 | Molex 43025-0800 | 2 | £0.41 ea (Digi-Key UK, WM1786-ND) ⚠️ USD not read | digikey.com |
| Micro-Fit 1×2 / 1×3 receptacles, R/A headers (43650 series), crimp terminals 43030 | Molex | ~6 housings, ~30 pins | ≈ $15 total ⚠️ | digikey.com |
| Mini-Fit Jr 2×5 receptacle + terminals (shunt end) | Molex 39-01-2100 + 39-00-0039 ⚠️ confirm against J1 | 1 | ≈ $3 ⚠️ | digikey.com |
| JST XHP-2, XHP-3 + SXH-001T | JST | 1 each | ≈ $1 ⚠️ | digikey.com |
| Hirose DF11 receptacle (charger) | DF11-14DS + DF11-2428SC crimps | 1 | ≈ $2 ⚠️ | digikey.com |
| Ring terminals 18 AWG: M6 ×1, M8 ×2 (5/16″) | Any insulated, 22–18 AWG | 3 | ≈ $3 ⚠️ | — |
| Wire 105 °C: 18, 20, 22, 24 AWG | Ancor / UL1015 | ~2 m total | ≈ $10 ⚠️ | — |
| U.FL–U.FL 1.13 mm coax, 100 mm | any | 1 | ≈ $5 ⚠️ | — |

## 7. Open items
- ✓ NPB-450 DF11: 14-pin; j_conv uses 7–8 (remote: short = on), 11–12 (CAN), 9 (GND-AUX). Remote is opto-isolated from pack−, so the BMS drives it with a dry contact (PhotoMOS), as modelled.
- ✓ GV141BAX coil leads exit on the +y face at the cap rim, i.e. down at the copper, facing the 2151 (T19). Route v16.3: the 4.2 mm slot between the contactor body (y 59.85) and the 2151 base (y 64.0), below the MRBFs (z 250.3), −x to x 89, then up past the 2151's end. ⚠️ exit height in the notch; the leads lie on the bus_mod_load copper there (silicone 20 AWG, 12 V) — add a Kapton strip if chafe shows.
- ⚠️ Tesla J1 exact part number and which end of the overhang strip it sits at (the route works for either).
- ✓ NTS-400P terminal side **confirmed 2026-11-25** from MEAN WELL's own photos (NTS-400P-SPEC 2026-03-26 p1, "DC input side"; saved as `docs/img/nts400p_dc_end_meanwell.png`, `nts400p_iso_meanwell.png`): cover up, PCB down, looking at the DC end the PP45 pairs (TB1) are on the **right** and the white JST connector left of them. Facing the DC end from outside = facing −x in the pack, right = +y, so TB1 is at +y and the drawing is a top view. The model was right; the mirrored keep-out is no longer needed.
- The board's schematic must take: 2 A board fuse on B+, precharge relay + resistor between j_pwr 1 and 2, coil driver for 3.9 A pick-up, CN301 dry contact (relay or photo-MOS, it must look like a relay contact), plated IMD mounting hole.
