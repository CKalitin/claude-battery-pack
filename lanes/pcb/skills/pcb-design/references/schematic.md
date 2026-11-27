# Schematic: readable, wired, proven

A schematic is a document for people. If it looks script-generated (symbols floating on a grid, every pin a stub with a label stacked on it), it fails however correct the netlist is. Owners who have drawn boards for years spot this at a glance. A real professional sheet is mostly wires with a handful of labels: KiCad's StickHub demo has 470 wires and 26 labels.

## Method (correctness is never taken on trust)
1. **Write the spec first:** `PARTS` (ref → symbol, value, footprint, MPN, manufacturer) and `NETS` (net → list of (ref, pin)), with pin numbers read from the actual symbol, plus `NO_CONNECT`. This is the source of truth.
2. **Lint the spec** before drawing (`schlib.lint_spec`): unknown pins, a pin in two nets, open power inputs, rails without decoupling, I²C without pull-ups, single-pin nets (typos), differential-pair names KiCad won't pair (they must end `_P`/`_N`).
3. **Plan sheets and blocks.** Past about 25 parts or 3 functions, go hierarchical: one sheet per function, and a root sheet drawn as the block diagram. One block per *circuit*: "5 V BUCK", not "buck input / buck controller / buck output". Aim for A3 or smaller per sheet.
4. **Draw with `scripts/vendor_diode663/schlib.py`:**
   - `s.place`, `s.wire`, `s.stub(..., power=)`, `s.note`;
   - a `with s.block("TITLE"):` around each circuit;
   - `s.arrange()` and `d.write()`.

   Anchor every wire on `s.pin(ref, pin)`, never on typed coordinates. Its format and rotation facts are in `scripts/vendor_diode663/kicad-format.md`.
5. **Prove it:**
   - `d.verify(NETS, NO_CONNECT)`: KiCad's own netlist must match the spec exactly.
   - `d.erc()`: 0 errors. Explain every remaining warning.
   - `d.check_text()`: 0 collisions.
   - `d.render(dir)`, then `pdftoppm -r 110 -png` and **look at every page** zoomed by block (`block_crops.py`).
6. **Independent visual review** (pcb-review skill) before the gate.

## Drafting rules
**Flow and orientation**
- Signals flow left → right: connectors and inputs at the left, outputs at the right. Feedback can run right → left.
- Supplies at the top, ground at the bottom. Supply arrows point up, ground symbols hang down. Higher voltages sit higher on the page.
- Turn parts so their pins face what they connect to. Mirror a connector rather than rotating it.
- Parts to a rail (pull-ups, decoupling, dividers) are drawn vertical. Series parts (series R, fuse, ferrite, sense R) are drawn horizontal, *in* the line, in the order current meets them.
- Draw what the datasheet's typical application draws. That is the picture the reader already has.

**Wire or label**
- **Inside a block: wire. Between blocks: label.** Two same-name labels inside one block means part of the circuit's shape exists only as text. Target 0 such joins (schlib prints the count).
- Use a label when a wire would cross another net, pass through a body, detour round the page, or when pin orders interleave (USB-C D+/D−/D+/D−).
- A label sits at the end of a ≥ 2.54 mm stub, never on the pin.
- Local labels within a sheet; hierarchical labels only for signals that leave it. Rails are **power ports**, which are global; never use text labels for rails, and don't add sheet pins for rails.
- Give each supply pin its own short stub ending in a port, rather than one long rail across the sheet. Tie EN high with a port at the EN stub, not a loop back to VIN.
- No 4-way junctions: use two offset T junctions. No wire through a symbol or text.

**Supporting parts**
- Decoupling, pull-ups, feedback dividers, crystals and their load caps sit next to the pin they serve, with a note when placement matters ("C12 within 2 mm of U3 pin 7").
- A separate "decoupling section" across the page fails. *(Seen in the schlib smoke test, 2026-11-27: the ESP32's 10 µF + 100 nF were drawn 20 mm from its 3V3 pin. Move them to the pin.)*
- Unused pins get no-connect flags. Unused op-amp or comparator sections are wired as followers, with a note.

**Symbols**
- Pins by function, not by package number: inputs and control left, outputs right, power top, ground bottom. Make a project symbol if the library one is in package order. Split big MCUs into units.
- Connector pin order matches the physical connector, with each pin's function next to it.
- Every part has a meaningful value ("100n 50V X7R", "TPS62933") and the fields MPN, Manufacturer, Footprint, Datasheet.

**Text and notes (the engineering lives here)**
- Put calculations and constraints next to the circuit: divider maths, shunt sizing, strap-pin rules, "no pull-up here", why a part was chosen. Text sizes: notes 1.0 mm, default 1.27 mm, block titles 1.6 mm bold.
- Reference and value stay off the body. For ICs and connectors: reference above, value below. For a vertical 2-pin part: stacked beside it.
- A long value ("10R 2W snubber") becomes a short value plus a separate visible property; never lengthen Value.
- Net labels carry an angle *and* a justification. Without `justify`, KiCad centres the text on the anchor, on top of the pin. Text reads away from the symbol: 0° → `left bottom`, 90° → `left bottom`, 180° → `right bottom`, 270° → `right bottom`. *(From joseluu/kicad-skills, no licence; idea only, restated.)*

**Grid and names**
- Connection grid 1.27 mm; symbol origins on 2.54 mm. One off-grid point can break junctions across a sheet.
- Name every net that leaves a block or matters for routing, firmware or debug (`EN`, `IO0`, `SW_BUCK`, `CELL3_P`). Differential pairs end `_P`/`_N`.
- Put PWR_FLAG where a rail enters the board and at regulator outputs, or ERC reports "power pin not driven".

## Gate (schematic)
- [ ] Spec lint: 0 errors; warnings explained in sheet notes
- [ ] `verify`: netlist = spec (output pasted)
- [ ] ERC 0 errors; every warning explained; global sym/fp lib tables present (`references/kicad-headless.md`)
- [ ] Label joins inside blocks: 0, or each explained
- [ ] Every part cross-checked against its `design/parts/*.md` audit: required externals present, values match the calculations
- [ ] Every symbol has value, footprint, MPN, manufacturer and datasheet
- [ ] Rendered pages looked at; independent visual review passed (findings pasted)
