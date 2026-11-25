# v16 decisions (2026-11-24)

Every number here comes from `cad/concepts/contactor/calcs_v16.py`; its output is in [`v16-calcs.txt`](v16-calcs.txt). The earlier study, with every contactor-mounting method and its losing options, is [`contactor-mounting.md`](contactor-mounting.md). Converter details are in [`power-train.md`](power-train.md). ✓ = from a source or the model; ⚠️ = estimate.

## Decision table
| # | Decision | Options considered (losers in italics) | Why the winner | Numbers / source |
|---|---|---|---|---|
| D1 | **C1 "PCB-style" power module**: a G10 plate with a flat 1/8″ copper plane; the contactor is mounted upside down, its terminals bolted through the copper | *upright contactor + bent bars*; *15 other methods (M1–M16)* | The SB175 busbar face sits at z 238 and an upright contactor's studs at ≥ 256, so pointing the terminals down puts every joint on one plane | contactor-mounting.md §3–6 |
| D2 | **Main fuse: MRBF 250 A on a Blue Sea 5191 block, plus a Z-strap from the fuse top down to the in-bar** | *flat MRBF link between two bars (my error, T6)*; *bare MRBF on a stud (Blue Sea forbids it, T7)*; *Class T* | An MRBF is a stack fuse whose output is its top face, so a strap is needed. The strap goes in last, so it is the service disconnect | 211.6 A worst case vs 250 A = 1.18× ✓; Blue Sea resources/640 ✓ |
| D3 | **5191 points −y**, Z-strap is an L in plan | *5191 pointing −x (hits the shunt board once the board is turned crosswise)*; *5191 at the +x flange end (bolt head hits the precharge resistor)* | Clears the shunt board by 10.5 mm | + to − 10.5 mm ✓ |
| D4 | **Branch fuses: Blue Sea 2151 (30 A charger, 50 A inverter) on the load-bar branch along the +y wall** | *flat box (wrong concept)*; *two 5191 singles (no room for both)*; *2151 beside the contactor along x (only 41.6 mm free, 49.5 needed)* | The only spot where both fuses fit, metal stays ≥ 7 mm from the wall (7.4 mm), and both fuses lift out | 2151 geometry from Blue Sea's dimensioned drawing (scaled ±0.5 mm ⚠️) |
| D5 | **90° lugs (barrel up)** on the 2151 | *straight lugs* | With two studs in a row and cables leaving along that row, the far lug hits the near stud (T8). ±y is blocked by the wall and the contactor | Del City 929605 (6 AWG), MAX 5950-050EL (8 AWG); the inverter now needs a 10 AWG version |
| D6 | **Contactor turned 90°**, now at (122, 32) | *A: flange-less GV14 PCB-mount (0 in stock, MOQ 11)*; *C: move it 4.3 mm further (strap clash, + to − 10.07 mm)*; *D: pull the module to change a fuse* | The GV141BAX flange had blocked the 2151 fuses from lifting out. Now it stops at y 59.85, 2.25 mm short of the fuse housings | Lift = 33.5 mm. The lift check covers all 3 fuses in all 3 contactor variants ✓ (T10) |
| D7 | **Shunt sense board crosswise on the bar**, flush at −x, connectors overhanging +x by 8 mm | — (correction from the owner's photo) | Matches the real part | Overhang scaled from the photo ⚠️ |
| D8 | **In-bar column moved to x 106.6–120.6** | *x 101.6 (5.4 mm to the board)* | Gives 10.4 mm to the board (now modelled at − potential). Line-to-load gap at T2 is 6.75 mm; both are + with only 12.8 V across them when open | J = 4.8 A/mm² ✓ |
| D9 | **Pack +49 mm, all at the rear (375 → 424 inside)**; front plate and power bay unchanged | *B: +30 mm at the front only*; *C: pigtails pre-wired on the bench, no growth (bend room still needed)*; *D: shorter converters (not searched)* | Fits every plug and cable bend. Converters move −27 mm, rear gap 18 → 40 mm | Needed vs have: 27/30.2, 42/50.8, 40/40, 20/40 mm. +~0.33 kg ⚠️ |
| D10 | **AC pass-throughs moved to the rear of the lid** (NEMA 5-15 outlet at y −40, C14 inlet at y +45, in the 40 mm column between fan and converters) | *keep them at the front (300 mm AC run)*; *beside the inverter (the lid's top is flat only to y ±74.5)* | Both converters have AC at the rear. AC wiring drops to ~60 mm, and AC and DC sit at opposite ends | Clinch nuts run along y to stay off the inverter top |
| D11 | **Charger AC lead: right-angle C13, L-com ACPWRC-C13LR** (rewireable, screw terminals) | *straight C13 (≥ 40 mm)*; *Quail 3514.024S jumper (depth unknown)* | Screw terminals allow a custom 60 mm lead. Rear gap is sized for the worse of the two possible depth readings | Drawing dims 41.9 × 30.1 and 35.6/37.9 mm; depth is 30.1 or 37.9 → gap 40 ✓ |
| D12 | **The inverter DC connector is Powerpole PP45, not PP75** → 10 AWG lead | — (correction) | Anderson 1327/1327G6 are PP15-45 housings: wire #20 to #10 AWG, housing 24.6 mm, mated 41.2 mm | 36.6 A vs PP45 45 A = 1.23×. 10 AWG at 90 °C = 40 A, only 1.09× ⚠️ (see open items) |
| D13 | **Converter terminal positions** placed from the MEAN WELL drawings | — | NPB-450: terminal block at y +5…+21, V+ on the −y side. NTS-400P: TB1 at y +25…+41. Mirrored inverter keep-out also checked | Read by extracting the PDFs' vector text (pdf.js); screenshots of PDFs froze |
| D14 | **Converter − leads on M8 carriage bolts through the shunt bar, beyond node B**: charger at (62, 1), inverter at (82, 1) | *on the − flange (bypasses the shunt)*; *one shared stud (barrels collide)* | The shunt measures converter current | Inverter lug 1.25 mm from the board ⚠️ |
| D15 | **Copper sizes** (1/8″ plane) | — | Worst current density is 5.3 A/mm² in the Blue Sea strap; the copper plane's worst is 4.8 A/mm² | + path copper 90 µΩ, 4.0 W at 212 A (excludes joints, fuse and contactor) |
| D16 | **Check rules added**: fuse lift-out sweep; plug keep-outs as obstacles; no `("hw_","")` wildcard in ALLOW | — | Each rule came from a miss: T9 (a wildcard hid a real clash), T10 (static checks miss removal paths) | contactor-mounting.md §11 |

## SendCutSend limits (read 2026-11-24, sendcutsend.com/materials/processing-min-max, in Chrome)
| Item | Limit | v16 | |
|---|---|---|---|
| 5052 .063″ bending: flat size | 30 × 44 in | body half ≈ 17.1 × 16.6 in ⚠️ (flat estimated) | ✓ |
| 5052 .063″ bending: max bend length | 44 in | 17.1 in | ✓ |
| 5052 powder coat | 30 × 36 in | 17.1 × 16.6 in | ✓ |
| Copper .125″: bend radius | .050″ | | |
| Copper .125″: min flange after bend | .471″ = 12.0 mm | Z-strap leg 30.5 ✓, foot 12.0 (exactly at the limit) | ✓ |

## Open items
- ⚠️ **Inverter − lug 1.25 mm from the shunt sense board** (both are at − potential). Shown in `issue_inv_neg_lug.jpg`. Not resolved, per the owner.
- ⚠️ **Inverter lead ampacity.** 10 AWG (the PP45 maximum) carries 36.6 A against a 40 A rating at 90 °C, only 1.09× before any derating for heat inside the box. Peak power not yet read from the datasheet.
- ⚠️ **NTS drawing view.** It's assumed to be the top view; the mirrored keep-out passes too, so the layout works either way.
- ⚠️ **Blue Sea block internals and cap outline, MRBF contact faces, 90° lug dimensions:** all modelled from drawing outlines and typical values.
- **The power-bay figures in contactor-mounting.md §6 (sections, levels, profile) predate D3–D14.**
