# Handoff for the next Claude

Owner: Chris Kalitin. Goal: Claude designs a complete, beautiful ~1 kWh+ battery pack ("Tower A") end to end. Current version **v14**.

## Read first
1. `docs/v14-baseline.md`: one-page spec.
2. `docs/v14-design-review.md`: decisions (§0) and every issue found.
3. `docs/v14-design-notes.md`: design justifications (flex, floating pack + IMD, wake/latch, cooling calc, service bays).
4. `docs/tesla-shunt.md`: the only source for shunt data. Dims are unconfirmed.
5. `cad/tower14.py`: the model. `versions/v14-4s2p-power-train/`: renders and STEP.

## Working rules (from the owner)
- Never add a part without need. The best part is no part.
- Every fabricated part comes from SendCutSend or a catalog. No parts that need emailing a vendor. No sketchy datasheets. Give buy links.
- Busbars on top.
- Do checks yourself (datasheets, vendor sites, browser). Don't ask Chris to check things; report results at the end.
- Flag every unconfirmed value with ⚠️.
- Run long jobs (builds, renders) in the background and keep working. Never block on a polling loop.
- Use the plain renderer for iteration. Studio renders only at milestones.
- No dead space. Chris likes the full rear hole grid.
- Every interference pair must be either fixed or listed in `run_tower14.py`'s ALLOW list.
- Terse answers, conclusion first, units on every variable.

## Environment notes
- `pip install -r cad/requirements.txt`. Renders need `xvfb-run` on a headless box.
- On a 2-core, 8 GB VM, running a rebuild alongside renders got the rebuild OOM-killed. Run them one at a time.
- `cad/out*/` is gitignored. Regenerate it with `run_tower14.py`; the committed STEP lives in `versions/v14-4s2p-power-train/`.

## Open items (v14)
- ⚠️ Which end the MEAN WELL NPB-450 / NTS-400P connectors are on. If the charger's AC inlet is on its −y half, flip the unit: only 12.5 mm to the risers there.
- ⚠️ True dims for the EV200, the JJN-500 blades and the MRBFs; LF105 terminal thread.
- ⚠️ SendCutSend bend rules for COP-187/250 copper. Lid slot hole-to-bend distance (2.4 mm).
- ⚠️ Shunt: bolt thread, connector part number, resistance characterization (deferred).
- Control board area is tight (4-layer). Schematic not started.
- Charger-wake behaviour deferred (button-only wake for now).
- Later: ESP32-hosted telemetry dashboard (`docs/telemetry-ideas.md`); re-estimate the budget; blog notes (`docs/blog-notes.md`).
