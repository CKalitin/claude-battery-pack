# Review checklist

Each area ends in a recorded output: a table or a number. An area without one is NOT CHECKED. *(Structure after jvanderberg/kicad-skills review-checklist, MIT; rewritten and condensed.)*

## 1. Power entry and protection
- Trace every input from the connector to the last load under: full load, reversed polarity or miswiring, a short on each output, hot-plug, the lowest and highest input, and one source present while others are absent.
- Connector and wire rating per pin at the claimed current, derated.
- Fuse coordination:
  - a holder's continuous rating is about 80 % of the fuse;
  - a PTC's hold current derates with temperature;
  - a PTC's I_max must exceed what upstream can deliver;
  - **rate fuses for the peak and duration of each load** (coil pick-up, inrush), not only the steady current.
- **Operating point:** solve the current with every series resistance (source, FETs at real gate drive, fuse, contacts, copper) instead of P/V. Compare it with each element's limit, latching trips first.
- TVS: clamp voltage at the surge current against every downstream absolute maximum. A small-signal zener is not a surge clamp.
- Enable and UVLO pins: abs max at the highest input; threshold and hysteresis from the datasheet equation.
- **Output:** a path-rating table, weakest element named.

## 2. Start-up, shutdown, transients
- Each switch's turn-on time against upstream soft-start.
- Inrush C·dV/dt on top of the running load, against every trip and its delay.
- Sequencing; back-feed through IO pins or body diodes into unpowered rails.
- Hot-plug ringing (up to 2× input).
- Brown-out oscillation: load step × path resistance compared with UVLO hysteresis.
- Precharge energy in the resistor for normal and worst-case (shorted bus, timeout) events, against its pulse rating.

## 3. Copper capacity and heat
- Narrowest neck per power net against its IPC-2152 width.
- Vias at each layer change carrying current.
- Thin inner copper.
- **Output:** a heat-source table per corner: I²R for FETs, fuses and shunts; converter losses from the efficiency at that operating point; LDO (Vin − Vout)·I; coil hold power. Then board and part temperatures, with an h range stated for the real enclosure.

## 4. Ground and returns
- Plane continuity: every inner-layer track is a slot. List what returns must detour round it.
- Stitching at the edges and under cable exits.
- Single-point grounds (AGND/PGND, Kelvin) still single after the pours fill.
- Board ground referenced at the right node (e.g. the cell side of a low-side shunt).

## 5. Regulators and decoupling
- Each hot loop against the datasheet layout example, item by item.
- Switch-node area; FB and EN lines away from SW.
- Inductor I_sat above the current limit.
- MLCC effective capacitance at the working voltage.
- Output capacitance within the stable range.
- **Output:** the nearest decoupling capacitor and its via for each IC supply pin.

## 6. Signals, EMC, external interfaces
- Reference plane under every fast signal; a ground via beside each layer change.
- Series resistors at the source of long clocks and SPI.
- ESD at the connector, in front of the IC.
- Lines that leave the board on cables (sense leads, shunt SPI, buttons): ESD, series R, filtering, and the shield or return path.
- Level and direction of every inter-chip link at power-up, in reset and asleep.
- Pins floating during sleep or SHUTDOWN.

## 7. Datasheet compliance and derating
- For each IC, a supply table: each supply, regulator and reference pin, the part on it, and the net at its far end. Compare it with the application diagram.
- Abs max per pin at the worst case. Unused pins as the datasheet says.
- Strap pins at reset.
- Derating: MLCC voltage, resistor power and pulse, FET SOA hot.

## 8. Sourcing and assembly
- Exact MPN suffix; lifecycle from the maker; stock at the fab's source, dated, for boards × qty + attrition.
- Single-source parts have a plan.
- Packages the assembler places.
- Polarity marks; CPL rotation for every polarised part.
- THT parts: formed leads and tail length noted.

## 9. Mechanical and silkscreen
- Outline, holes and connector positions match the brief and the enclosure.
- Heights, with mated plugs, within the envelope.
- No other-net copper under mounting hardware.
- Every connector labelled with function, polarity and rating.
- Identity and revision present.
- 0 silk overlaps; designators readable next to their parts.

## 10. Schematic readability
- Blocks, flow, power up and ground down.
- Wires inside blocks; label joins inside blocks = 0.
- Support parts at their pins; calculations noted.
- Meaningful values; MPN and datasheet fields complete.
- Spec netlist = drawn netlist.

## 11. Firmware-visible consequences
- A pin map for firmware: every GPIO with its function, direction, level, pull and strap behaviour.
- Thresholds that firmware must enforce: limits stated as hardware capability plus the firmware limit.
- What the hardware does with no firmware running (safe defaults: coils off, outputs off).
