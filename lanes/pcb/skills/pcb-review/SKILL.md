---
name: pcb-review
description: Independent design review of a PCB (schematic, part choices, placement, routing, fab package), done the way an experienced reviewer would - re-deriving every number from the datasheets, judging rendered images, ranking findings BLOCKER/MAJOR/MINOR/NOTE. Use at every pcb-design gate (run as a fresh-context subagent with only the artifacts), when asked to review or audit any KiCad board, or before ordering. Reviews write nothing to the design.
---

# PCB review

The agent that did the work is never the one that says it is good enough. A review is independent, evidence-based and complete for its scope.

## Protocol
1. **Fresh context.** The reviewer gets the artifacts and the checklist only: files, rendered images, tool outputs, datasheets. It does not get the author's conversation or explanations. When you're the author, spawn a subagent with this skill and a brief (`references/briefs.md`).
2. **Scope it first.** Name:
   - the gate or phase;
   - the board and revision (git hash);
   - the stack-up;
   - the criteria: datasheet requirements, owner rules, our in-house thresholds (labelled as in-house).
3. **Re-derive, don't re-read.** Recompute every calculation from the datasheet with the operating conditions in `intent.md`. Read datasheets yourself; download them if missing. Look at rendered images for anything visual, zoomed by block.
4. **Judge every item** the scope walks: pass, fail, or not judged with the reason. Report the counts ("0 deviations out of 37 judged, 3 not judged: …"). An area with no recorded output is reported as **NOT CHECKED**, never as fine.
5. **Rank findings:**
   - **BLOCKER:** will not work, will be damaged, or can't be built;
   - **MAJOR:** fix unless justified in `decisions.md`;
   - **MINOR:** fix if cheap;
   - **NOTE.**
6. **Make every finding actionable:**
   - where (ref, net, sheet and coordinates);
   - the rule and its source (datasheet page, standard, owner rule);
   - the computed effect, with its direction in words ("12 mV over the limit");
   - the exact fix (part, value, position, by type of run);
   - "To do: …" or "Nothing to do".
7. **The designer decides.** The author fixes or disputes each finding in `decisions.md`. Only the owner accepts a deviation. Re-review after any BLOCKER or MAJOR fix.
8. **Write nothing** to the design files during a review. Output goes to `design/gates/phaseN.md` (or a review file).

## What to check
`references/checklist.md`, by area:
- power entry and protection;
- start-up and transients;
- copper and heat;
- ground and returns;
- regulators and decoupling;
- signal integrity and EMC;
- external interfaces and ESD;
- datasheet compliance and derating;
- sourcing and assembly;
- mechanical and silkscreen;
- schematic readability;
- firmware-visible consequences.

## How reviews go wrong
`references/failure-modes.md`. Read it before the first review of a session. Main points:
- set the target before computing;
- a DRC pass checks minimums, not intent;
- a capacitance in a calculation is its value at the working voltage;
- a scenario is not a bound;
- describe a tool from its code, not its header.
