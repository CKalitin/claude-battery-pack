# Layout: nets, stack-up, rules, placement, routing, silkscreen

## 1. Net classification: `design/nets.csv`
`net,class,v_max,i_cont,i_peak,impedance,length_limit,reason`. Every net joining two or more pins gets a row, including KiCad's auto-names (`Net-(D1-A)`). This table drives widths, via counts, clearances and which nets get special routing.

| Class | Examples | Drives |
|---|---|---|
| POWER_HI | battery, > 3 A | pours, via arrays, calculated widths |
| POWER | logic rails | planes or wide tracks |
| SWITCH | buck/boost switch node | minimal area; nothing sensitive on the adjacent layer |
| GATE | gate/coil drive | short, beside its return |
| ANALOG(_DIFF) | cell sense, shunt Kelvin, ADC inputs | away from switching, Kelvin, routed as pairs |
| CLOCK | crystal | very short, guarded, no vias |
| DIFF_HS / SE_HS | USB, fast SPI | impedance, solid reference |
| RF | U.FL feed, antenna | 50 Ω coplanar, keep-outs |
| HV | > 50 V, mains | creepage and clearance per standard |
| SIGNAL | the rest | defaults |

Widths from IPC-2152 at a stated temperature rise (inner layers run hotter). Via count = ceil(I_peak / per-via capacity × 1.5). Clearance from IPC-2221B for v_max (outer, uncoated: ≤ 30 V 0.1 mm; 31–150 V 0.6 mm; 151–300 V 1.25 mm), never below the fab minimum.

## 2. Stack-up and rules
- **Default: 4 layers.** L1 parts and signals; **L2 solid GND (no tracks, no slots)**; L3 power areas and slow signals; L4 signals and GND pour. Two layers only for simple, slow boards.
- Use the **fab's own stack-up**, with its page and date recorded in `design/stackup.md`, and name its code on the order. *PCBWay standard 4-layer 1.6 mm (2026-11-27):*
  - outer copper 0.5 oz plated to 1 oz;
  - 7628 prepreg 0.186 mm after lamination, Dk 4.74;
  - inner copper 1 oz;
  - 1.03 mm core, Dk 4.6.
- **Fab minimums** are lower bounds, not targets. Design to 0.15 mm track and space and 0.3/0.6 mm vias unless density forces less.
  - *PCBWay:* 0.1 mm track/space; 0.15 mm annular ring; drills < 0.2 mm cost extra; track to edge 0.25 mm; silk ≥ 0.15 mm line and ≥ 0.8 mm text.
- Every `nets.csv` class becomes a KiCad net class. Every current-carrying net also gets a `.kicad_dru` rule `track_width (min …)`, because a router will neck a net down to the board minimum and DRC will pass it.
- **DRC severities:** make these errors:
  - unconnected items and clearance;
  - courtyard overlap, silk over pad, silk overlap;
  - track width, annular ring, hole clearance;
  - footprint vs library mismatch, schematic parity;
  - track and via dangling, copper sliver, isolated copper, connection width.

  Set `min_connection` to the minimum track width. Run `kicad-cli pcb drc --severity-all`.

## 3. Placement (it decides most of the board's quality)
**Order**
1. Outline, holes, keep-outs, edge band. Lock them.
2. Connectors at their mechanical positions, mating faces out, and locked.
3. Blocks in flow order from the connectors inward. Noisy blocks away from sensitive ones.
4. **Critical loops first:**
   - buck: input cap, switch and ground return;
   - gate and coil drivers beside their FETs;
   - crystal at the oscillator pins;
   - shunt and cell sense as Kelvin pairs.
5. ICs turned so their pins face what they connect to.
6. **Satellites at their pins:**
   - decoupling: smallest value closest, supply pad toward the pin, GND pad toward its via;
   - pull-ups, FB dividers (on the side away from SW), bootstrap caps.
7. Test points (each rail and ground, probe-able), programming pads.
8. Reserve silkscreen room now, not after routing.

**Numbers (edge to edge; targets, fab minimums in brackets)**
| Rule | Value |
|---|---|
| 100 nF decoupling to its pin pair | ≤ 1 mm; 1 µF ≤ 3 mm; 10 µF ≤ 5 mm; bulk ≤ 15 mm; cap to its via ≤ 0.5 mm |
| Buck | input cap 0.5–2 mm on the IC's layer; bootstrap ≤ 1 mm; inductor ≤ 3 mm; FB/RT ≤ 2 mm away from SW; SW copper ≤ 15 mm² |
| Crystal | ≤ 5 mm from the MCU (target 3), load caps beside it, nothing switching near |
| TVS / ESD | ≤ 5 mm from the connector pin; protected IC ≤ 10 mm behind it; short wide GND via |
| Relay / solenoid / coil | freewheel diode or TVS at the driver or connector; driver rated for pick-up current |
| Analog vs switching | ≥ 10–15 mm apart |
| RF module | antenna end at or beyond the board edge, keep-out per the module datasheet on all layers; U.FL modules: none, but keep the feed short |
| Passive–passive / SOT / SOIC / QFN–passive | 0.30 (0.15) / 0.50 (0.40) / 0.60 (0.40) / 1.0 (decoupling 0.3) mm |
| Connector to anything | 1.0 mm; THT pins 1.5 mm; plus room for the mating plug and fingers |
| Copper / SMD pad / body to edge | 0.4 / 0.8 / 0.5 mm |
| Mounting hardware | no other-net copper under the screw head, washer or standoff on **either** outer layer |

*(Values: studio-edul/pcb-layout-skill §4–5, MIT; rules of thumb ⚠️. The datasheet's own layout guidance wins.)*

**Never** place passives in a row for tidiness: each belongs to a pin. Every "no copper under…" line in a part audit becomes a rule area that DRC enforces.

Check: courtyards don't overlap; occupancy is in the area budget's band; render top and bottom (`kicad-cli pcb render`); a reviewer looks at it.

## 4. Routing (Claude is bad at routing by typed coordinates; let structure do the work)
1. **Planes and pours first** (GND on L2, power areas), with explicit clearance on every scripted zone. After every fill, check each zone's area and piece count.
2. **Via arrays** where current changes layer, sized from `nets.csv`.
3. **Short critical connections by script from pad positions:** gate and coil drive, crystal, shunt and cell Kelvin pairs, the buck hot loop. Placement should have made them a few mm long.
4. **Autorouter for the rest:** Freerouting, governed. Lock only what the mechanics fix. Run `nice -n 15`, with a wall-clock `timeout`, a memory cap (`systemd-run --user --scope -p MemoryMax=…`), one run at a time and a fixed seed. If it can't finish, the fix is almost always placement (a part blocking a pin's escape), not more compute.
5. **Clean-up:** acute angles, detours, dangling stubs and vias, then refill and DRC.
6. **Ground stitching** along edges and pours. A GND via beside every fast signal's layer change.

**Checks:**
- DRC 0 errors and 0 unrouted, every warning explained;
- schematic parity;
- per-net minimum width met;
- no track on L2;
- no fast signal over a plane split;
- each critical zone still one piece with its intended area;
- copper renders per layer looked at.

## 5. Silkscreen (the board's user interface)
- **Identity:** board name, revision, date, project URL or part number.
- **Every connector:** function ("SHUNT", "B+ LOAD+ GND"), pin 1, polarity, rating ("14.6 V MAX"). Every button and test point named.
- Designators next to their own part, not under any part, not on pads or vias. At most two rotations. ≥ 0.8 mm text and ≥ 0.15 mm stroke (PCBWay).
- 0 silk overlaps. Fix a colliding footprint outline with a board-local footprint copy, never by waiving the DRC.
- Reserve silk areas as no-via rule areas before routing, or there will be no room after.
