# Workflow: intent, brief, gates, decisions

## Project layout
```
<board>/
  design/
    intent.md         phase 0: what the board must do, as numbers
    parts/            one audit per part or passive group
    datasheets/       PDFs (gitignored) + sources.csv (committed)
    sizing/           sizing BOM, courtyards table, placement proof + render
    brief.md          outline, holes, connector edges, layers, sides, keep-outs, floorplan
    nets.csv          net classes: source of every rule
    stackup.md        fab stack-up with URL and date
    decisions.md      decision, options with numbers, why, date; every waiver
    gates/phaseN.md   checklist + pasted outputs + reviewer findings
    bringup.md        power-up plan and expected values
  hw/                 KiCad project (.kicad_pro/.kicad_sch/.kicad_pcb/.kicad_dru) + generator scripts
  fab/                release outputs, one folder per revision
```
Generators (schematic, placement, routing pre-routes) are scripts in the repo, so a re-run rebuilds the same board. Never hand-edit a generated file; port the edit into the generator.

## Phase 0: intent (owner signs off)
Each item gets a number or an explicit "don't care":
- **purpose:** one paragraph;
- **every external interface:** connector, direction, signal, voltage range including transients, hot-plug and miswiring, continuous and peak current, the mating part;
- **power:** input range, every rail with its load, sequencing, sleep current budget;
- **environment:** temperature inside the enclosure, airflow, vibration, ESD exposure;
- **mechanical:** envelope, heights per side, mounting, connector access directions;
- **manufacturing:** fab and assembler, quantity, cost, single- or double-sided, hand-soldered parts allowed;
- **serviceability:** test points, debug, designator policy;
- **known risks.**

## Phase 2: brief (owner signs off)
Work from the outside in, decided before any placement:
- board size from the area budget;
- holes and their keep-outs;
- each connector's edge, position, mating direction and plug room;
- assembly sides;
- layer count;
- density philosophy (0402 vs 0603, test points);
- block floorplan in flow order (noisy away from sensitive);
- thermal path;
- silkscreen policy and identity;
- keep-outs (antenna, hardware, creepage).

Show a render of the outline with connectors and holes placed.

## Gates
Each phase ends with `design/gates/phaseN.md`:
1. **Checklist** from the phase's reference file.
2. **Evidence pasted from the actual tools** (ERC/DRC/verify output, calculations, render paths). Never write "passed" for a check you didn't run.
3. **Independent review** for judgement-heavy phases (pcb-review skill): parts, schematic, placement, routing render, release.
4. **Each finding fixed, or disputed** in `decisions.md` with reasoning. Re-review if a blocker or major finding was fixed.
5. **Inputs recorded:** git hash of the files the gate judged. A later change upstream makes that gate and every later one stale: re-run them, and never patch downstream to hide an upstream change.

Owner sign-off pages are rendered (PDF/PNG or a published page) with the decision in plain words and the options. Never point an owner at a raw `.md` path.

## Decisions log (`design/decisions.md`)
One row per non-obvious choice, as it happens:
- the decision;
- the options **including the ones not tried** (say so);
- numbers for each;
- why the winner won;
- sources with confidence (✓ / ⚠️);
- the date.

This is what lets the owner defend every choice later.

## Status and reporting
- Keep the lane's STATUS file current after every meaningful step.
- Report terse, conclusion first, units on every number, ⚠️ on every unconfirmed value.
- Lead with what's missing or unsigned, not with DRC counts.
