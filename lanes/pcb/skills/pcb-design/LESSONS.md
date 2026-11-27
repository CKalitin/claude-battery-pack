# Lessons

One rule per correction: `- [area] what went wrong → what to do instead (date, board)`. Read this at the start of every session, and add to it in the same turn as any correction. Entries marked *(boardroom)* come from sequoia-hope/boardroom's LESSONS.md (MIT), reworded and generalised. The rest are ours.

## Ours
- [area] BMS board sized at 150 × 90 mm from guessed area allowances per block; the owner rejected it ("prove you need that space"). Real KiCad footprints totalled 2,421 mm², and a placement proof fit everything on 95 × 55 mm at 49 % occupancy → never quote a board size before a sizing BOM of real footprints and a placement check (`references/area-budget.md`). (2026-11-27, BMS)
- [connectors] Right-angle connectors placed at their default rotation pointed their mating faces into the board → orient every edge connector from its geometry (pads → housing points out of the edge), then check it in a render. (2026-11-27, BMS)
- [parts] A scope line said "TXU0104" for an SPI link; SPI needs 3 lines out and 1 in (TXU0304) → check that each interface part's channel directions match the bus, not just its family name. (2026-11-27, BMS)
- [power] A coil with a 3.9 A / 75 ms pick-up was fed through a 2 A ATM fuse (195 % of rating) → rate every series element (fuse, connector pin, trace) for the peak and its duration from the load's datasheet, not the hold current. (2026-11-27, BMS harness)
- [tools] The first `add-apt-repository` failed on DNS (the host had lost IPv4) → one retry, then report; don't loop on network failures. (2026-11-27)

- [privacy] The reference schematic (UBC Solar HVC) belongs to the team, not this public repo → record style only; never save its images, circuits or values here. (2026-11-27)

## Carried over (boardroom, generalised)
- [schematic] Symbols on a grid joined by global labels → group by function in signal-flow order; wires inside a block; labels only between blocks or sheets.
- [schematic] Inputs and outputs scattered round a symbol → inputs left, outputs right, power up, ground down; make a project symbol if the library one fights this.
- [placement] ICs placed, then their passives dumped in a row → every passive at the pin it serves, in the order the datasheet layout implies.
- [routing] Hand-routing by typing coordinates → pours and planes for power, short critical routes enabled by placement, an autorouter for the rest under full net-class rules.
- [power] One via on a high-current net → via arrays sized by calculation.
- [sync] A part number changed in only one of schematic or PCB → the schematic is the source; sync check at every gate.
- [silkscreen] Designators under parts, cut by vias or overlapping; connectors with no explanation → every designator visible next to its part; every connector labelled with function, polarity and rating.
- [datasheets] Parts chosen without reading the fine print → a full audit per part; an independent reviewer recomputes the calculations.
- [sourcing] Took the first part-number match: a discontinued part with zero stock → check lifecycle on the maker's page and stock at the fab's own source, with the date, for the exact orderable suffix.
- [routing] A net class's width is only the router's target; the router necked a power net to the board minimum and DRC passed it → put a `track_width (min …)` DRC rule on every current-carrying net.
- [routing] Copper locked after routing stayed behind when a part moved and shorted pads → never lock routed copper; only parts fixed by the mechanics.
- [routing] DRC passed boards with dangling stubs and end-cap-only joins because `min_connection` was 0 and dangling/sliver checks were warnings → set `min_connection` to the minimum track width; make track/via dangling, copper sliver, isolated copper and connection width **errors**; run DRC with `--severity-all`.
- [routing] Scripted zones kept KiCad's default 0.5 mm clearance and shredded the ground plane → set clearance explicitly on every scripted zone; after any fill, check each zone's area and piece count, not just DRC.
- [routing] A pin-to-cap link drawn as a thin zone got carved into islands → links are tracks; zones are areas.
- [placement] An exposed pad was tiled so other nets' vias could pass → an exposed pad is one solid pad with only its own vias.
- [pads] Scripts used `pad.GetLayer()`, which returns F.Cu for flipped parts → use `pad.IsOnLayer(...)`.
- [parts] Connector chosen by series name ("JST 1.25"), not by the plug on the mating cable → choose a connector by the real part it mates with.
- [parts] A current-limit "only for milliseconds" was assumed; a limiting switch holds its limit through a stall → rate series elements for the switch's maximum limit held continuously.
- [gates] A routed, DRC-clean board was called "basically finished" with no gate files → readiness is gate files with independent review, not DRC counts.
- [review] Asked the owner to open `.md` files on a phone → every sign-off gets a readable rendered page with images inline.
- [cost] Recommended a recurring fab charge (filled vias) to avoid layout work → price layout fixes, including a slightly larger board, before a per-board charge.
