# Handoff: new charger and inverter (2026-11-27)

The next agent runs on **Chris's own server**. It has his Chromium (Claude in Chrome, signed in to his accounts), more CPU and more RAM than the Anthropic VM, which was too small. Read `CLAUDE.md` and `docs/owner-requirements.md` first; this doc says what to do next and why.

Repo: `CKalitin/claude-battery-pack`, branch `power-train-rethink`, head 4b99fa5 or later.

## 1. What Chris said (2026-11-27, voice transcript, lightly cleaned)

> "The reason we got into this mess in the first place is because of the charger and the inverter. We need to fix that because that's the decision that actually sent us down the wrong branch of the design space."

> "The principle behind making a pack like this is that cells are your dominant constraint and your control board has to fit within them in some way. In this case, we're setting the area as the top of the cells as the constraint, and you're not allowed to go above that, because then we get on into all of these little silly issues. The reason we're above that is because of … the charger and the inverter. So we need a different charger and a different inverter."

> "Let's open up that search again. You have access to Chromium on my server. Just think for as long as you can until you find a solution that doesn't involve going over the area of the … top face of the cells."

## 2. The new rule

**Everything above the cells sits inside the plan footprint of the cells' top faces.** That covers the converters, the power bay and the control board. Nothing overhangs that area, and the box is sized by the cells, not by the electronics.

The rule is in `owner-requirements.md` §3. It overrides the side power spine (option B) and the W 204 / B1 / B2 question, which are now paused (§5).

**Footprint numbers.** All come from `cad/tower15.py`, so recompute them if the cells change.

| Item | Value |
|---|---|
| Cells | 8 × EVE LF105, 4S2P, in one row along x, upright |
| Can footprint | 8 × 36.7 = 295.3 mm (x) × 130.3 mm (y), plus Mylar |
| Module with end plates | ≈ 312 (x) × 158 (y, end-plate width `EP_W`) |
| Heights | Can top z 201.85; terminal face and busbars z 206.85; tray 1 top z 221.6 today |

⚠️ **Not confirmed with Chris:**
- Whether "the area" means the can footprint (295 × 130) or the module with end plates (312 × 158).
- Whether the lid connectors and the fan count.

Use 295 × 130 as the hard target and say where the 312 × 158 reading would change the answer. Height above the cells is not capped, but keep it small; today's stack is ≈ 113 mm above the can tops.

**Why today's parts break the rule:**
- **NPB-450-12 charger** (205 × 135 × 55) is wider than the cells (135 > 130.3).
- **NTS-400P-112 inverter** (186 × 100.5 × 34) needs connector ends that point along x.
- **Fan and power bay:** the two converters stacked use up the plan length, so the fan and power bay are pushed off the ends. That is the 91 mm rear void and the whole A–H architecture study (`docs/architecture.md`).

## 3. The task

Find a charger and an inverter, or one combined unit, plus a layout, so that:
- the converters, the power bay (contactor, main fuse, branch fuses, shunt, SB175), the fan(s) and the control board all fit above the cells inside the footprint in §2;
- their connector ends, airflow and service access also stay inside it.

Think as long as needed. Chris asked for the whole search to be reopened, not a tweak.

### Requirements (current baseline; change any only with a recorded trade-off)

| # | Requirement | Source |
|---|---|---|
| R1 | Pack 4S2P LFP, 12.8 V nominal, 10.0–14.6 V; charge to 14.2 V, 2-stage, inhibit below 2 ℃ | v14-baseline.md |
| R2 | Charge current ≈ 25 A (8.4 h for 210 Ah). Less is allowed only if Chris accepts the longer charge time; give the hours | baseline, R §0a |
| R3 | Inverter 400 W continuous, pure sine, 120 V 60 Hz, NEMA 5-15 outlet, floating output (outlet ground to chassis), low idle draw / power-saving mode, remote off | baseline, N §3 |
| R4 | Universal AC input via IEC C14 on the lid | baseline |
| R5 | Charger controllable from the ESP32: CAN preferred; at minimum remote on/off and a CV setpoint ≥ 14.2 V | baseline, R M3 |
| R6 | Catalog parts with real manufacturer datasheets (MEAN WELL, Victron, TDK-Lambda, etc.), with buy links and dated prices. No parts that need emailing a vendor; no sketchy datasheets | CLAUDE.md |
| R7 | Purchased parts are never modified | CLAUDE.md |
| R8 | Cooling: show the thermal path at the rated load (see cooling.md for how the NTS-400P failed this) | cooling.md |
| R9 | Branch fusing stays MRBF on the load bus; re-size it for the new parts | baseline |
| R10 | SendCutSend total < $2,000 | CLAUDE.md |

### Seed ideas (all ⚠️ unverified; check each one against its datasheet)
- **Smaller MEAN WELL parts in the same families:** NPB-360 / NPB-240 chargers; NTS-250 / TS-400 inverters. Compare footprint, current and CAN against R2 and R5.
- **Low-profile or open-frame supplies used as a CV/CC charger:** e.g. MEAN WELL UHP, RSP, HRP, or other 1U units with remote on/off and PMBus/CAN. These can lie flat in a thin layer.
- **Victron:** Phoenix 12/250 and 12/375 inverters, Blue Smart IP22 / IP65 chargers, and a combined inverter-charger. Compare size, VE.Direct vs CAN, and idle draw.
- **Combined inverter-charger in one box:** removes one housing and one set of AC terminals.
- **Converters side by side in one flat layer** instead of stacked, with the power bay on top or between them.
- **Drop the internal AC charger:** external brick, or USB-C PD / EPR at 240 W (≈ 17 A at 14.2 V, ≈ 12 h). This changes a baseline decision; present it to Chris, don't adopt it.
- Record any idea not tried as "not tried" and say why.

## 4. How to deliver (CLAUDE.md rules apply)

1. **Write `docs/converters.md`** in the `cells.md` pattern:
   - Requirements with sources.
   - Every candidate with footprint, mass, efficiency, idle draw, control interface, price and its fit against §2, including the losers.
   - Sources with ✓ / ⚠️.
   - Traps.
   - Buy links with dated prices.
   - Open items.

   This also closes the documentation gap "NPB-450 / NTS-400P selection never compared" in CLAUDE.md.
2. **Draw a plan-view packing figure** for each serious candidate, with the cell footprint outlined (the same style as `cad/analysis/spine_packing_fig.py`), and send it to Chris. Label only visible parts.
3. **Bring Chris a short recommendation:** conclusion first, numbers, and the decisions only he can make (charge time, external charger, cost).
4. **After he picks,** build the CAD (`cad/tower17.py` + power-bay module), then:
   - run the interference, clearance and assembly checks (`run_tower15.py` ALLOW list, `clearance_v15.py`, `assembly_v16.py`);
   - fast renders;
   - redo the cooling check;
   - update the BOM and the SCS total.
5. **Record every decision Chris states** in `owner-requirements.md` in the same session, plus a row in `docs/v16-decisions.md` (next free: D39).
6. Commit and push often.

## 5. State at handoff
- **Done and pushed:** v16.3 (Mylar, SCS ≈ $1,825, M6 rods, structure check, firmware-rating baseline), the architecture study (`architecture.md`) and the spine packing check (§4a).
- **Paused by this handoff:**
  - option B / W 204 (D38);
  - the B1 vs B2 question;
  - the planned v17 CAD of the side spine (`tower17.py` doesn't exist yet).

  Keep the analysis as a losing branch in `architecture.md`. Don't delete it.
- **Still true whatever converter is chosen:**
  - GV14 contactor kept (Chris, 2026-11-27);
  - busbars on top;
  - button-only wake;
  - firmware ratings;
  - M6 rods;
  - + to − ≥ 10 mm, pack copper to chassis ≥ 7 mm.
- **Other open items** (owner-requirements.md §7):
  - Chris still has to send the Zep reply (Gmail draft) and delete the 2 older Zep drafts;
  - inverter cooling bench test (may disappear with a new inverter);
  - end-plate local stress at 30 kN;
  - re-quote the bent pack busbars;
  - front .125 plate price ⚠️.
- **Environment:**
  - `pip install -r cad/requirements.txt`;
  - renders need `xvfb-run`;
  - run long jobs in the background;
  - security: emails stay drafts unless Chris approves sending; SCS guest quotes only, no orders or accounts.
