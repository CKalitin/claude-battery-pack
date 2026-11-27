# Reference style: Chris Kalitin's HVC rev 1.0 schematic (UBC Solar, Altium)

Chris named his UBC Solar **HVC rev 1.0** schematic (Altium 365 project `E_BMS_HVC`, variant Rev1.0) as the reference for schematics made for him. It was read on 2026-11-27 through his logged-in browser. This file records **style only**. The design is UBC Solar's: don't copy its circuits, images or values into public repos.

## Structure
- **Hierarchical, one small sheet per function** (about 18 A4 sheets): startup level-shifting, power prioritiser, LV current sensor, power, CAN, MCU, fan control, debug LEDs, LV control, e-stop level-shifting, contactor control, thermistor, pre-charge monitoring, pre-charge relay control, discharge relay control, HV current sensor, connectors.
- **Top sheet = block diagram:**
  - sheet symbols around the MCU, ports named by signal, inputs on the left and outputs on the right;
  - the HV section enclosed in a dashed box labelled "HV";
  - a link to the design-review document on the sheet.
- Sheets are **numbered in the title** ("3. POWER", "18. CONNECTORS"). **Designators carry the sheet number** (Q4.1, R4.3, TP4.5 on sheet 4), so a part's sheet can be read from its reference.
- **Related signals between sheets travel as harnesses** (e.g. a CONTACTOR_CTRL harness carrying POS/NEG/LLIM/HLIM). KiCad equivalent: buses with named members, or grouped hierarchical labels.
- Title block filled in on every sheet (file, date, size).

## Inside a sheet
- **Each repeated channel is drawn complete and identical, side by side:** input label → series gate resistor → MOSFET, gate pull-down, the load's net on the drain. Wires inside the channel; labels only where it meets the sheet's ports.
- **MCU sheet:** net labels on the MCU pins (this is a hub sheet; the rule is labels between blocks, wires within). Decoupling drawn as a row with a note citing the application note it follows. Debug headers (SWD, UART, boot) drawn next to the MCU.
- **Connectors sheet:** **one connector per destination, each titled by what it connects to** ("Junction Board", "Primary Contactor Board", "Shunt Resistor", "Pack Fans"), with the MPN under it (Molex Micro-Fit 172447-02xx and similar). Pins labelled with net names.
- **Actives carry the MPN as their value** (DMN3023L-7, DMP2110U-7); passives carry the value.

## Debug and test features (treat as required)
- **A test point on every rail and every control signal.**
- **An indicator LED on every rail and on every switched output** (e.g. an LED from 3V3 to each contactor driver's drain), plus a "debug LEDs" sheet driven by the MCU.
- **Bench-test hooks:** test points that let a pull-down be toggled by hand to close a FET during board testing, explained in a note.
- **Current flags on nets:** a circled current value (e.g. "0.2A") on each switched output net, to feed routing widths. KiCad: a net-class directive or a `Current` field, carried into nets.csv.

## Notes on the sheet (the engineering is written where it applies)
- Yellow note boxes beside the circuit:
  - why an extra FET exists;
  - what a disable line is for and how it is driven;
  - truth tables for multi-input control;
  - which supply wins when several are present;
  - how a part is used during bench testing;
  - application-note citations ("follows ST AN2586 §2.2").
- **Datasheet links on the sheet** for parts whose values come from the datasheet (inductor and capacitor values specified in the datasheet). Links to design-review and test documents.

## How this maps to our rules (`schematic.md`)
| Chris's practice | Our rule |
|---|---|
| One sheet per function + block-diagram top sheet | Hierarchical past ~25 parts; root sheet is the block diagram |
| Sheet-numbered designators | **Adopt:** annotate by sheet (R4.3 style, or a 100-per-sheet offset if KiCad's annotation can't do dotted references) ⚠️ check KiCad 10 options |
| Test point + LED on every rail and switched output | **Adopt as default** on his boards; budget their area in the sizing BOM |
| Per-destination connectors titled by destination | Already decided for the BMS (J1–J9) |
| Current flags on nets | Carry into nets.csv and the DRC width rules |
| Notes with truth tables, intent, app-note citations, datasheet links | Required (calculations and intent on the sheet) |
| Labels at MCU pins, wires inside channels | Same rule: wires within a block, labels between blocks |
