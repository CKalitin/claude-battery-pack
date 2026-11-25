# v16: C1 power module, real fuse blocks, pack +49 mm at the rear

> Decisions, losing options and calculations: [`docs/v16-decisions.md`](../../docs/v16-decisions.md) and [`docs/v16-calcs.txt`](../../docs/v16-calcs.txt). Contactor study: [`docs/contactor-mounting.md`](../../docs/contactor-mounting.md). Converters: [`docs/power-train.md`](../../docs/power-train.md).

![bay](renders/c1_module_gv14up_close_b.jpg)

## Changes vs v15
| | v15 | **v16** |
|---|---|---|
| Power bay | Parts placed one by one; GX12 upright; 2151 on the contactor stud | **C1 module**: G10 plate + 1/8″ copper plane. GV141BAX upside down and turned 90°; SB175; shunt crosswise |
| Main fuse | MRBF on a 5191 on the + flange | Same, pointing −y, with a **Z-strap (fuse top → in-bar) as the service disconnect** |
| Branch fuses | 2151 on the contactor load stud | **2151 on the load-bar branch along the +y wall**, 90° lugs; fuses lift out past the contactor |
| Converter leads | Envelopes | + leads from the 2151; − leads on M8 bolts through the shunt bar (node B side); all end at the converters' real terminals |
| Inside length | 375 mm | **424 mm**, all added at the rear. Converters −27 mm (DC plug room 30.2 / 50.8 mm); rear gap 18 → 40 mm (right-angle C13) |
| AC pass-throughs | Lid front, beside the SB175 | **Lid rear**, either side of the inverter's CN500 |
| Inverter DC | "PP75" | **PP45** (Anderson 1327/1327G6), 10 AWG |
| Joints after the cells (+) | 7 | 7: 5191 tab, fuse bottom, fuse top, strap foot, T1, T2, SB+ |

## Checks
- **`run_tower15.py`:** 0 interferences.
- **`clearance_v15.py`:** pack copper to chassis 7.4 mm.
- **`c1_power_module.py`, all 3 contactor variants:** 0 interferences.
  - + to − 10.5 mm (rule ≥ 10).
  - Pack copper to chassis 7.3 mm (rule ≥ 7).
  - All plug keep-outs clear, including the mirrored inverter one.
  - All 3 fuses lift out.
- **Envelope:** 437.9 × 206 × 391.7 mm.

## Model
- `cad/tower15.py`: shell (L_IN 424), converters, terminals and keep-outs.
- `cad/concepts/contactor/c1_power_module.py`: the power module.
- `cad/run_v16.py`: merges the two into `claude_battery_pack_v16_assembly.step`.

## Assembly order (top-down)
1. **Bench, pack module:** cells, series bars, flex. − band + riser; + collector + riser (x 124) + flange.
   - Put the M10 carriage bolt into the + flange's square hole **now**: its head sits under the flange.
2. **G10 tray 1** drops onto the standoffs. Both risers come up through their open cuts.
3. **Bench, power module** (plate face down on the bench, so all hardware goes in from what becomes the underside):
   - All carriage bolts into the plate's square holes.
   - Copper plane parts over them: in-bar, load bar with branch, − tab, shunt bar.
   - Contactor terminals and SB175 contact studs down through copper and plate; nuts underneath.
   - Flip upright. Shunt board, G10 cheeks + SB175, Blue Sea 2151 + M10 nut.
4. **Power module drops into the bay** onto the front standoffs. Its − shunt bar seats on the − flange (node A carriage bolt).
5. **5191** onto the + flange's M10 stud, nut, MRBF 250 A.
6. Charger. Its + lead goes to 2151 stud A, its − lead to the shunt-bar stud at (62, 1).
7. **Deck 2 + inverter.** PP45 plugs on; + lead to 2151 stud B, − lead to the stud at (82, 1).
8. **AC:** right-angle C13 onto the charger inlet; CN500 plug onto the inverter.
9. **Z-strap last** (service disconnect). Then front PCB, then lid with the rear AC pass-throughs, then wire the lid inlet/outlet before closing.
