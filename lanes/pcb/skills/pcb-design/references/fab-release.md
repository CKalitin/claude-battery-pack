# Release: files, checks and the order

## Before generating files
- [ ] Every earlier gate current: nothing changed upstream since it passed
- [ ] Sync check: every designator is in the schematic, the PCB and the BOM/CPL, with the same value, footprint, MPN and DNP flag
- [ ] DRC (`--severity-all`) and ERC re-run on the final files: clean
- [ ] Stock and lifecycle re-checked today for every MPN at the fab's source

## Files (KiCad 10, headless)
```bash
B=board.kicad_pcb; S=board.kicad_sch; O=fab
kicad-cli pcb export gerbers --output $O/gerber/ $B              # RS-274X; uses the board's plot settings
kicad-cli pcb export drill --format excellon --excellon-separate-th --output $O/gerber/ $B
kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp --output $O/cpl.csv $B
kicad-cli sch export bom --output $O/bom.csv \
  --fields 'Reference,Value,Footprint,${QUANTITY},Manufacturer,MPN,${DNP}' --group-by 'Value,Footprint,MPN' $S
kicad-cli sch export pdf --output $O/schematic.pdf $S
kicad-cli pcb export step --output $O/board.step $B
kicad-cli pcb export ipcd356 --output $O/netlist.ipc $B              # lets the fab test copper against the netlist
```
Then reshape the BOM and CPL into the fab's format with a script (never by hand).

| Fab | BOM columns | Centroid |
|---|---|---|
| **PCBWay** (assembly-file-requirements, 2026-11-27) | Line#, Qty, Reference Designator, Part Number, Description, Package, Type (SMD / THT / Hybrid); turnkey adds **Manufacturer, MPN, Distributor PN**. R/C without an MPN: value and package. xls/xlsx/csv only | Designator, X, Y, Rotation, Side (Top/Bottom); SMD only; designators must match the BOM and silk. Gerbers RS-274X with copper, silk and paste |
| **NextPCB** | Manufacturer Part Number, Designator, Quantity; optional Customer Supply (Y / DNP) | Designator, X, Y, Rotation, Side; THT optional |
| **JLCPCB** | Comment, Designator, Footprint, LCSC C-number | Designator, Mid X, Mid Y, Layer, Rotation |

## Checks no CAD tool does for you
1. **CPL rotation and polarity.** Library footprints and the assembler's part orientations disagree silently. Overlay the CPL on the board render, or use the fab's placement preview, and check pin 1 and polarity of **every** polarised part and IC. Paste the list. Put persistent corrections in a footprint field, not in the exported file by hand.
2. **Gerber review in a separate viewer** (gerbv, or KiCad's GerbView). Check layer by layer: outline closed, drills present, mask openings, paste only on SMD pads, silk not clipped, no missing pours. A blank layer looks "fine": count objects against what the board should have.
3. **Netlist vs copper:** upload the IPC-D-356 so the fab's electrical test checks against it.
4. **Stack-up on the order form:** name the fab's stack-up code. The Gerber job file carries KiCad's table, often still the default.
5. **Assembly drawing** (F.Fab and B.Fab with designators, at a readable scale) and assembly notes: formed THT leads, tail length, polarity, anything non-standard.
6. **Bring-up plan** `design/bringup.md`:
   - power-up order with a current-limited supply;
   - expected value at each test point, taken from the part audits;
   - isolation points;
   - the firmware smoke test.
7. **Final independent review** (pcb-review), then the owner's approval. Tag the release in git: `<board>-rev<X>`.

## Ordering notes
- PCBWay quotes assembly after a person reviews the files ⚠️ (about 1–2 business days, per kicad-happy notes; not stated on PCBWay's pages). Upload early. Minimum 5 assembled boards.
- Price layout fixes (a slightly larger board, a different package) before accepting any recurring per-board charge (filled vias, special processes).
- Record the order: files' git hash, fab, options, price, date.
