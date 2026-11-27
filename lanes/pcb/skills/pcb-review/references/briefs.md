# Reviewer briefs (paste into a fresh-context subagent with the listed artifacts)

Every brief ends with: "Report findings as BLOCKER / MAJOR / MINOR / NOTE with location, rule and source, computed effect, and exact fix. Give judged / not-judged counts. Do not edit any file."

## Datasheet and part audit (one subagent per complex part, in parallel)
> Read the attached datasheet in full, then the audit file and the schematic excerpt for this part. Independently:
> 1. List every external part the datasheet requires or recommends, and check each is in the schematic with a suitable value, voltage rating and dielectric.
> 2. Recompute every calculation from the datasheet formulas, using the operating conditions in intent.md, at the tolerance corners.
> 3. List every footnote, warning, unused-pin rule or power-up condition the design may violate.
> 4. Check the footprint against the package drawing for this exact MPN suffix.
> 5. Check the lifecycle and stock line, and its date.
>
> Cite datasheet pages.

## Schematic readability and correctness
> You are a senior hardware engineer reviewing rendered schematic sheets (PNG per block attached) plus the netlist spec.
> 1. Does it read like a person drew it: functional blocks, left-to-right flow, power up and ground down, wires inside blocks, labels only between blocks, supporting parts at the pins they serve, calculations noted on the sheet?
> 2. Report anything that looks machine-generated, cramped, overlapping or ambiguous, with sheet and coordinates.
> 3. Trace the main power path from the input connector to every load, and each signal from source to destination. Say where you couldn't.
> 4. Check required externals per IC against its datasheet.
>
> Would you present this sheet in a design review as it is?

## Placement (renders with ratsnest, floorplan from brief.md, area budget)
> Assess as an experienced layout engineer:
> - block grouping and flow from the connectors;
> - every passive at the pin it serves;
> - critical loops (list each, with its size in mm);
> - separation of noisy from sensitive circuits;
> - escape room for every fine-pitch pin;
> - thermal (where the heat goes);
> - connector mating clearance and orientation;
> - mounting-hardware keep-outs on both sides;
> - assembly (polarity orientation, THT access).

## Routing and copper (per-layer copper renders, DRC JSON, nets.csv, stack-up)
> Check:
> - DRC config: severities and `min_connection`;
> - each current-carrying net's narrowest neck against its required width;
> - via counts where current changes layer;
> - continuity of the reference plane under every fast signal, and slots cut by inner-layer tracks;
> - hot-loop area and the ground return of each converter;
> - Kelvin sense routing;
> - pieces and area of each critical zone after fill;
> - ground stitching at the edges;
> - copper under mounting hardware.

## Release (full package)
> You are the final reviewer before fab. Would you send it? Name the highest-risk issue, any intent.md requirement not met, anything that would make bring-up painful, and check:
> - every polarised part's CPL rotation;
> - Gerber layers against the board;
> - BOM against CPL against the schematic.
