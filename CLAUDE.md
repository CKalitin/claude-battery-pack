# Handoff for the next Claude

Owner: Chris Kalitin. Goal: Claude designs a complete, beautiful ~1 kWh+ battery pack end to end. Current version **v14**.

## Read first
1. `docs/v14-baseline.md`: one-page spec.
2. `docs/v14-design-review.md`: decisions (§0) and every issue found.
3. `docs/v14-design-notes.md`: design justifications (flex, floating pack + IMD, wake/latch, cooling calc, service bays).
4. `docs/tesla-shunt.md`: the only source for shunt data. Dims are unconfirmed.
4a. `docs/cells.md`: cell selection, sourcing, import and incoming inspection.
5. `cad/tower14.py`: the model. `versions/v14-4s2p-power-train/`: renders and STEP.

## Working rules (from the owner)
- Never add a part without need. The best part is no part.
- Every fabricated part comes from SendCutSend or a catalog. No parts that need emailing a vendor. No sketchy datasheets. Give buy links.
- Busbars on top.
- The pack has no name. Never call it "Tower A" (old placeholder, removed 2026-11-24); say "the pack" or "Claude battery pack".
- Do checks yourself (datasheets, vendor sites, browser). Don't ask Chris to check things; report results at the end.
- Flag every unconfirmed value with ⚠️.
- Run long jobs (builds, renders) in the background and keep working. Never block on a polling loop.
- Use the fast render for iteration. The beautiful render is for milestones only (see Rendering).
- No dead space. Chris likes the full rear hole grid.
- Every interference pair must be either fixed or listed in `run_tower14.py`'s ALLOW list.
- Terse answers, conclusion first, units on every variable.

## Document every exploration of the design space
**Every time a choice is explored, write it down, including the branches that lost.** A decision without its losing options, its sources and its traps gets re-litigated, or silently broken by the next change. This is mandatory, not optional polish. Chris has to be able to justify every decision himself.

The reference example is [`docs/cells.md`](docs/cells.md). Each write-up needs:
1. **Requirements** the choice must meet, each with where it came from (owner rule, calc, standard).
2. **Candidates**, including the ones not tried (say so explicitly), and why each won or lost, with numbers.
3. **The path taken**, version by version: what each step taught and why it moved on.
4. **Sources** for every value the design depends on, each with a confidence level (✓ / ⚠️). Cite the manufacturer's document and revision, not a reseller summary.
5. **Traps found**, and the rule each one created.
6. **Buy links with dated prices**, and import/shipping if relevant.
7. **Open items.**

Where it goes: a subsystem gets its own `docs/<topic>.md` (as `cells.md` and `tesla-shunt.md` do). A one-off choice goes as a row in the decision table of the current design review. Version-to-version changes go in `versions/vNN/README.md`. If a doc already covers the topic, extend it rather than starting a new one.

**Examples already in the repo (follow this pattern):**
- `cells.md`: LF50K → LF100MA → on-edge (rejected) → LF105; 4S1P → 8S1P → 4S2P; sourcing and import.
- `tesla-shunt.md`: keep the Tesla module vs a plain shunt (D3), with every measurement flagged.
- `v14-design-notes.md` §1: flex vs rigid sense board, with the failure modes of each.
- `v14-design-notes.md` §11: sealed box (38 K) vs full rear grid (≈ 10 K) vs blanked rear (3–6 K).
- `v14-design-notes.md` §3–4: symmetric vs asymmetric IMD divider (r₀ = 0.5 sits on a cell node, so 0.312).
- `v14-design-review.md` §0a: EV-B (250 A) vs EV200 (500 A); Anderson SB50 vs M10 studs.

**Explorations to write up the same way when they come up (brainstorm):**
- Charger and inverter: why MEAN WELL; alternatives (Victron, a combined inverter-charger, a single bidirectional unit); efficiency, idle draw, connectors, CAN.
- Fan: NF-A14 vs 120 mm or 92 mm, 5 V vs 12 V, airflow vs noise vs the rear-grid area.
- Cell monitor: BQ76952 vs alternatives (BQ76942, LTC6813, MAX17841), driven by cell count, the SHUTDOWN mode and coulomb counting.
- Main fuse class: Class T vs ANL vs MRBF vs a pyro fuse, by AIC vs the 5–7 kA prospective fault current.
- Enclosure: 5052 vs 6061 vs steel; powder-coat colour and finish; SendCutSend limits.
- DC output: M10 studs vs Anderson vs Amphenol Surlok; 500 A vs what you'd actually plug in.
- Wake sources: button vs charger detect vs load detect, and the shutdown current of each.
- Terminal and busbar fasteners: thread inserts vs screws into the pole, by torque and pull-out.
- Telemetry stack: ESP32 web page vs BLE app vs CAN-only.

## Known documentation gaps (fix these)
- **MEAN WELL NPB-450 / NTS-400P selection:** never compared against alternatives. Only the 24 V → 12 V model switch is recorded (review §0a).
- **NF-A14 fan:** choice of model and size not justified; only the 5 V vs 12 V point is recorded.
- **BQ76952:** chosen in early versions with no recorded comparison.
- **Enclosure material and Roadster-red powder coat:** no rationale or SendCutSend finish options recorded.
- **Service bays (`v14-design-notes.md` §12):** only option 2, the chosen one, is written up. Options 1 and 3, and the diagrams of them, aren't in the repo.
- **Cell burst rating (3C / 30 s):** comes from a reseller page; the 500 A rating depends on it (`cells.md` T4).
- **Budget (README):** prices undated and unsourced, and it predates v14.
- **Full Battery:** named as the vendor in v07–v13 with no reason given.

## Rendering: two renderers
Chris calls these **"fast render"** and **"beautiful render"**.

| | **Fast render** (plain, v1–v11 style) | **Beautiful render** (studio, v12 onward) |
|---|---|---|
| Script | `cad/render_tower14_plain.py` | `cad/render_v14_nice.py` |
| Lineage | `render_tower.py` … `render_tower12.py` | `render_v2_nice.py`, `render_v12_nice.py`, `render_v13_nice.py` |
| Look | Flat colours, black edge lines, white background | PBR materials, procedural studio cubemap, SSAO, SSAA, ground shadow, transparent background |
| Time | ~10 s/view (12 views in ~2 min on 2 cores) | `DRAFT=1`: ~50 s/view (no SSAA, light SSAO, 1× scale). Full: several min/view ⚠️ not timed |
| Output | `cad/out_tower14/img/v14p_*.png` | `cad/out_tower14/img_nice/v14_*.png` |
| Run | `xvfb-run python render_tower14_plain.py all` (or named views: `hero rear open power conn top bays`) | `DRAFT=1 xvfb-run python render_v14_nice.py` |
| Use | **Default.** Every design iteration, checking clearances, exploded/section views | Milestones only, when Chris asks for it |

Both read the STLs that `run_tower14.py` writes, so rebuild first. Run renders in the background, and one job at a time on a small VM. Save JPGs to `versions/<version>/renders/`: plain ones are `v14p_*`, studio ones are `v14_*`.

## Environment notes
- `pip install -r cad/requirements.txt`. Renders need `xvfb-run` on a headless box.
- On a 2-core, 8 GB VM, running a rebuild alongside renders got the rebuild OOM-killed. Run them one at a time.
- `cad/out*/` is gitignored. Regenerate it with `run_tower14.py`; the committed STEP lives in `versions/v14-4s2p-power-train/`.

## Open items (v14)
- ⚠️ **LF105 burst rating (3C / 30 s) comes from a reseller page only.** The 500 A rating depends on it. Find EVE's own pulse-discharge row (`cells.md` T4).
- ⚠️ Which end the MEAN WELL NPB-450 / NTS-400P connectors are on. If the charger's AC inlet is on its −y half, flip the unit: only 12.5 mm to the risers there.
- ⚠️ True dims for the EV200, the JJN-500 blades and the MRBFs; LF105 terminal thread.
- ⚠️ SendCutSend bend rules for COP-187/250 copper. Lid slot hole-to-bend distance (2.4 mm).
- ⚠️ Shunt: bolt thread, connector part number, resistance characterization (deferred).
- Control board area is tight (4-layer). Schematic not started.
- Charger-wake behaviour deferred (button-only wake for now).
- Later: ESP32-hosted telemetry dashboard (`docs/telemetry-ideas.md`); re-estimate the budget; blog notes (`docs/blog-notes.md`).
