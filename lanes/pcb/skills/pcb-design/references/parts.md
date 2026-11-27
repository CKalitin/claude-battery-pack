# Parts: selection, datasheet audit, sourcing

A part has to be right three ways:
- **electrically:** it survives and works in this circuit, per its own datasheet;
- **physically:** footprint, height, side, and a package the assembler places;
- **commercially:** active, in stock at the fab's source for the exact orderable suffix, at an acceptable price.

## Choosing
- Start from the block diagram. For each block, list candidates, including the ones you don't pursue, and compare them with numbers: rating, Iq, size, price, stock. Pick one and write down why the others lost.
- **Ask of every part: what fails without it?** A fuse that duplicates an upstream fuse, a relay a MOSFET can replace, a connector two signals could share. Remove it, or justify it.
- Switching regulators: start from the vendor's reference design or design tool (TI WEBENCH), then check its picks against the datasheet yourself.
- **Interface parts: check directions and levels, not the family name.** SPI is 3 lines out and 1 in, so a 4-same-direction translator is wrong.
- Prefer one package size for passives (0402 for logic, 0603 where voltage or power needs it) and the fewest unique MPNs.

## One audit file per part: `design/parts/<ref-or-function>.md`
Download the datasheet into `design/datasheets/` and record it in `sources.csv` (gitignore the PDFs, commit the list). For text: `pdftotext -layout ds.pdf ds.txt`, then search it for "Absolute Maximum", "Typical Application", "Layout", "Unused", "must", "should", "do not". Read the figures as rendered pages (`pdftoppm -f N -l N -png`).

Each audit has:
- **Identity:** datasheet title, revision and date, the pages read; exact MPN and suffix; lifecycle from the maker's page (ACTIVE / NRND / LTB / OBSOLETE) with the date; stock and price at the fab's source with the date.
- **Footprint** checked against the package drawing for that exact suffix.
- **Absolute maximum vs our worst case**, per pin, including pin currents and transients (hot-plug ringing, load dump, inductive kick).
- **Required external parts**, pin by pin, with values and page numbers. Mapped to designators.
- **Calculations:** formula, page, inputs, result, chosen standard value, and the result recomputed with the chosen value.
- **Fine print:** every footnote, "must", "should", "do not", and recommended-vs-required distinction. Unused-pin handling. Pin states at power-up and in reset. Supply current from every table that lists one.
- **Layout guidance** copied from the datasheet: it becomes placement rules and rule areas.
- **Dependencies:** values derived from this part (a trip current from R_DS(on), a UVLO divider from a threshold). When the part changes, every one is re-derived.

## Derating (record which applies)
- **MLCC:** voltage rating ≥ 1.5–2× the working voltage. Use capacitance from the DC-bias curve of that exact part: a 10 µF 0603 at 12 V can be 3 µF. C0G for timing and filters, X7R/X5R for decoupling, never Y5V.
- **Resistors:** ≤ 50 % of rated power. Check voltage rating on high-voltage dividers and pulse rating for inrush, snubber and precharge parts.
- **Semiconductors:** FET SOA at the real case temperature. Inductor I_sat above the converter's current limit, not just the load. TVS clamp voltage at the surge current, compared with downstream absolute maximums.
- **Series elements** (fuses, connector pins, traces): rate them for the load's peak and its duration, from the load's datasheet (pick-up currents, inrush), and for a current-limited switch held at its maximum limit.

## Sourcing at the target fab
| Fab | Sources by | BOM key | Notes (checked 2026-11-27) |
|---|---|---|---|
| **PCBWay** | MPN, global distributors; "no mark-up on parts" for turnkey | Manufacturer + MPN (+ distributor PN) | Turnkey, partial turnkey (combo) or consigned; min 5 pcs; 0402 / 0201 / 01005; 0.25 mm pitch; SMT + THT, double-sided. Assembly quote is reviewed by a person ⚠️ (1–2 days per kicad-happy notes) |
| **NextPCB** | MPN, matched against DigiKey, Mouser, HQ Online | Manufacturer Part Number, Designator, Quantity (+ Customer Supply Y/DNP) | No minimum for assembly; 01005; 0.38 mm fine pitch; SMT + THT, double-sided, flex |
| **JLCPCB** | LCSC part number from its own library | LCSC C-number | Basic vs extended parts (loading fee per extended); stock per warehouse region |

- For MPN-sourced fabs (PCBWay, NextPCB), check stock and lifecycle at DigiKey and Mouser (APIs if keys exist, otherwise their pages through a browser) for the **exact orderable MPN**, quantity = boards × qty per board + attrition. Record the stock line with its date.
- A part with no second source (modules, specific relays, the AFE) needs a plan before the order: buy extra, consign, or name an alternate.
- Re-check stock at each hand-off (schematic done, layout done, order); it moves daily.

## Gate (parts)
- [ ] Block diagram; every block maps to parts; candidates and losers written down
- [ ] Audit per non-trivial part with its datasheet saved; abs max vs worst case; every value calculated
- [ ] MLCC derating checked; resistor power and pulse checked
- [ ] Every footprint matches the exact package suffix
- [ ] Lifecycle and stock checked at the fab's source, with dates
- [ ] Independent reviewer re-read each datasheet and recomputed each calculation
