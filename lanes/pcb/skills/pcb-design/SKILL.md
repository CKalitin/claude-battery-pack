---
name: pcb-design
description: Design a PCB end to end in KiCad, headless and autonomous, to the standard of an experienced board designer. Covers requirements, part selection and datasheet audits, area budgeting, human-readable schematics (wired, not net labels), net classes and stack-up, placement, routing, silkscreen, and fab/PCBA release for PCBWay, NextPCB or JLCPCB. Use for any new board, board revision, schematic redraw, board-size estimate, part choice for a board, or fab hand-off. For an independent review of someone's (or your own) board, use the pcb-review skill.
---

# PCB design

The bar: a board an experienced designer would sign off without redrawing anything. The schematic reads like a person drew it. The layout follows the physics. Every part is checked against its own datasheet. Every number has a source.

Read **LESSONS.md** first. It lists the corrections owners have already had to give. Repeating one is the worst kind of mistake.

## Hard rules
1. **Datasheet or nothing.** Download every IC's datasheet and read the parts you use before choosing values. Never fill a pin, limit or required external part from memory or a search snippet. If a PDF won't download, run `pdftotext -layout`, then try a browser. Only then stop and ask.
2. **Numbers come from scripts or written calculations**, never mental arithmetic: widths, via counts, dividers, inductor ripple and I_sat, MLCC derating, power, temperatures. Record each formula with its inputs and datasheet page.
3. **Size a board from real footprints, never from guessed areas** (`references/area-budget.md`). The first guess is usually 2–3× too big.
4. **Schematics are wired.** Inside a functional block, connections are wires. Labels are only for links between blocks or sheets, and power ports for rails. A sheet that is symbols plus net labels fails, however correct its netlist (`references/schematic.md`).
5. **The schematic is the source of truth** for values, footprints and MPNs. Change the schematic, update the PCB, run the sync check. Never edit those in the PCB.
6. **Prove, then claim.** ERC/DRC with real severities, the netlist compared with the written spec, renders looked at. "Done" means the gate file exists with pasted outputs (`references/workflow.md`).
7. **Never silence a check.** Every waiver goes in `design/decisions.md` with its reason.
8. **The best part is no part.** For every part, ask what fails without it. Remove what can't answer.
9. **Flag every unconfirmed value with ⚠️.** Cite the manufacturer's document and revision, never a reseller page.
10. **Write down every exploration,** losing options included: requirements, candidates with numbers, path taken, sources, traps, buy links with dated prices, open items.
11. **Independent review at every gate** that needs judgement, by a fresh-context reviewer (`pcb-review` skill).
12. **Run long jobs in the background** (renders, routing, DRC on big boards). One heavy job at a time on a small VM.

## Toolchain (verified 2026-11-27 on Ubuntu 26.04)
- **KiCad 10.0.8** from `ppa:kicad/kicad-10.0-releases`. Not the nightly: KiCad 11 removes SWIG `pcbnew` and changes the file format.
- **Headless:** `kicad-cli` (ERC, DRC, netlist, exports) and `import pcbnew` (board scripting). Details and traps: `references/kicad-headless.md`.
- **Schematic writer:** `scripts/vendor_diode663/schlib.py` (MIT, vendored unmodified). It writes native KiCad 10 schematics with real wires, power ports and titled blocks. `verify()` checks the drawing against your written netlist; `check_text()` and `render()` cover the visual pass.
- **Area proof:** `scripts/courtyards.py` (courtyards read from library footprints) plus a placement script on the same pattern as `place.py` in the BMS project.
- **Routing:** placement and critical nets by script. Freerouting only for leftover low-speed nets, governed (`references/layout.md`).
- **Simulation:** ngspice (apt) for precharge, drivers, latches, converter start-up.

## Phases (detail in `references/`; read each file when you start that phase)
| # | Phase | Output | Read |
|---|---|---|---|
| 0 | Intent | `design/intent.md`: every interface, rail, limit, environment, fab, quantity, each as a number or "don't care" | workflow.md |
| 1 | Architecture and parts | block diagram; `design/parts/*.md` audit per part; sourcing checked at the chosen fab | parts.md |
| 2 | Area budget and brief | sizing BOM → courtyards → placement proof; outline, holes, connector edges, layers, sides, keep-outs | area-budget.md, workflow.md |
| 3 | Schematic | wired, block-structured sheets; ERC clean; netlist = spec; visual review | schematic.md, owner-style-chris.md |
| 4 | Nets, stack-up, rules | `design/nets.csv` (class, V, I, impedance, reason); fab stack-up; net classes and DRC rules, each with a source | layout.md |
| 5 | Placement | blocks in flow order, satellites at their pins, critical loops first; render reviewed | layout.md |
| 6 | Routing | planes, then power copper, critical nets, the rest; DRC 0 / unrouted 0 | layout.md |
| 7 | Silkscreen | identity, every connector labelled with function, polarity and rating; 0 overlaps | layout.md |
| 8 | Release | Gerber/drill, BOM and CPL in the fab's format, rotation check, Gerber review, bring-up plan | fab-release.md |

Sign-offs that belong to the owner: intent (0), brief (2), release (8). Show them rendered pages (PNG/PDF or a published page), never raw file paths.

## Owner standards this skill was built for
**Reference schematic style:** `references/owner-style-chris.md`, from Chris's UBC Solar HVC rev 1.0. Read it before any schematic for Chris.

Chris Kalitin, ex-UBC Solar electrical lead:
- full PCBA at a catalog fab (PCBWay / NextPCB), nothing hand-soldered unless agreed;
- readable schematics;
- boards no bigger than proven;
- terse reports, conclusion first, units on every number.

When an owner corrects you, add the rule to LESSONS.md in the same turn.
