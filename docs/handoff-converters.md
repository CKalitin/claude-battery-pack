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

## 2a. Why the converters are the root cause (the numbers)

Full study: `docs/architecture.md` §2–4. Figures in `versions/v16-c1-power-module/renders/`: `rear_end_void.png` (the problem), `architecture_options.png`, `architecture_3d_A.png` / `_B.png`, `front_view_A_B.png`, `spine_packing.png`, `v16_04_lid_off.jpg` and `v16_07_section.jpg` (the v16.3 layout as built).

**v16.3 as built:**
- Inside the box is 424 × 186.8 × 318 mm (x × y × z).
- The cell module is 312 mm long, so the shell overhangs it by ≈ 91 mm at the rear and 21 mm at the front.
- The rear 91 mm is a void of 91 × 164 × 187 mm (2.8 L) at cell level.
- The front 21 mm holds the front board: the front plate inside face is at x +177.05, the board back at +169.95, and its parts stand ≈ 15 mm proud, to ≈ x 155.
- Both decks above the cells are 312 mm long. The charger sits on tray 1 (top z 221.6), the inverter on tray 2 (top z 282.3), and the lid inside is at z 318.1.

**Row-length budget in x for each deck:**

| Deck | Fan | AC plug | Converter | DC plug | Power bay | Sum | vs 312 |
|---|---|---|---|---|---|---|---|
| Charger | 25 | 36 + 4 | 205 | 27 | 113 | 410 | **+98** |
| Inverter | 25 | 20 | 186 | 42 | 113 | 386 | +74 |

The power bay sat end to end with the converters, and the 140 mm NF-A14 fan is taller than the ≈ 103 mm free above the cells. So everything spilled off the rear end.

**Width is no better:**
- Charger 135 + inverter 100.5 = 235.5 > 186.8 inside.
- The 135 mm charger is wider than the 130.3 mm cans.
- The charger (205) can't turn crosswise.

That is why every layout tried (A–H, B1, B2) either overhangs the cells or grows the box.

## 2b. What else must fit in the same footprint (space claims the converters compete with)

Every converter candidate must be checked with all of these in the same plan area. A converter that fits alone proves nothing.

| Item | Size [mm] | Notes / source |
|---|---|---|
| Shunt (Tesla 1016792-00-C) | 83.5 × 35 | ⚠️ dims unconfirmed, tesla-shunt.md |
| Contactor GV141BAX (kept, owner) | Ø55.7 body, 72.5 with studs | contactor-mounting.md |
| Main fuse block Blue Sea 5191 (MRBF) | 62 × 23 incl. fuse | power-train.md |
| Branch fuse block Blue Sea 2151 | 88.5 × 20 (23 with fuses) | power-train.md |
| SB175 output (lid-mounted) | 55.6 × 25.4 | power-train.md |
| Fan(s) | NF-A14 140 × 140 × 25, or 2 × NF-A9 92 × 92 × 25 | cooling.md, architecture.md B |
| Front/control board | ≈ 21 mm of x behind the front plate (parts dict `CTRL` in tower15.py, z 228–285) | design-notes |
| Lid connectors | NEMA 5-15 outlet, IEC C14 inlet, SB175, push-button; each needs its depth under the lid and a 150 mm service loop | baseline M8, tower15 `CONNS` |
| Plug room at each converter connector | e.g. charger DC 30, right-angle C13 36, PP45 42, CN500 20 | architecture.md A4 |
| Compression rods | M6 at y ±72, outside the cans (±65.15), inside the end plates (±79) | structure.md |
| Pack busbars | on top of the terminals at z 206.85; the flex sense board sits on them | baseline |
| Clearances | + to − ≥ 10 mm; pack copper to chassis ≥ 7 mm; fuses lift out with the lid off; everything installed top-down, bolts tightened from above | CLAUDE.md |

The power bay alone needs ≈ 270–390 mm of strip depending on how it is packed (`spine_packing.png`). The best packing found so far uses two lanes of ≈ 30 mm. Any layout must say where the bay goes.

## 2c. Electrical and thermal interface the replacement must meet
- **Inverter DC input range covers 11.0–14.6 V.**
  - 11.0 V is the inverter's own cutoff in the UV ladder (2.75 V/cell). The ladder is 2.90 firmware → 2.80 BQ UV → 2.75 inverter → 2.60 BQ SHUTDOWN.
  - Check the inverter's low-voltage cutoff against this ladder.
- **Today's parts, as the baseline to beat:**

| Part | Rating | Efficiency | Other | Source |
|---|---|---|---|---|
| NPB-450-12 charger | 25 A, 420 W | 92 % typ (≈ 37 W loss) | CAN on DF11 | NPB-450-SPEC 2026-07-06 |
| NTS-400P-112 inverter | 400 W continuous | — | no-load draw 10 W, 1.3 W in power-saving mode (SW4); remote on/off on CN301 | NTS-400P-SPEC 2026-03-26 |

- **Standby budget.** Today: ON-idle 7.7 W → 13.8 days. A higher-idle inverter shortens this; report the days.
- **Cooling.**
  - The NTS-400P needs a 10 CFM (17 m³/h) fan 5 cm from its DC end for 100 % load at 40 ℃. The pack fan gives it only 3.7 m³/h (0.22×), so **400 W continuous is unproven today** (cooling.md).
  - A replacement with its own fan, or one rated for convection at 400 W, removes this open item. Say which.
- **Branch fuses** (MRBF, today inverter 50 A, charger 30 A): re-size for the new input currents.

## 2d. Chris's answers (2026-11-27)
- **Footprint includes the end plates:** ≈ 312 × 158 mm is the hard limit (supersedes the 295 × 130 target in §2).
- **The front board zone is preferably for the LED board only.** Chris prefers a **separate BMS board**, which reverses the v14–v15 "controls on the back of the LED board" decision. The BMS board needs its own place inside the footprint: add it to the §2b space claims and to the packing figures.
- **No height cap above the cells,** "but be reasonable."
- **Performance trades (Chris, 2026-11-27, chat):**
  - **Charge current ≥ 17 A** (≈ 12 h for 210 Ah; was 25 A / 8.4 h).
  - **Inverter ≥ 300 W continuous** (was 400 W), and "the inverter requirement may be relaxed" further if a USB-C output covers laptops.
  - **Charger must be internal** (AC inlet on the pack). No external brick, no USB-C-only charging.
  - **A USB-C PD output for laptops is welcome.** PD 3.0 is 100 W (20 V × 5 A); PD 3.1 EPR is up to 240 W (48 V × 5 A). ⚠️ Pick the module from a catalog. Evaluate an "inverter ≥ 300 W + USB-C" option against a "smaller inverter + USB-C" option, and show Chris the trade.
  - **Inverter priority order (Chris, 2026-11-27, 12:33):**
    1. **A combined inverter-charger is "extremely ideal."** Search this first and hardest.
    2. Otherwise a separate internal inverter (≥ 300 W preferred).
    3. **Only if an internal inverter is really impossible:** no internal inverter, a **USB-C PD output** (direct from the pack) for laptops, and maybe an external inverter. Chris "can tolerate no inverter internally" in that case. This is a last resort; document why the first two failed, with numbers, before proposing it.
- If a new trade comes up, ask Chris directly with numbers and concrete options; don't leave it open-ended.

### Original questions
1. **Footprint:** does it mean the cans only (295 × 130), or the module with end plates (312 × 158)? Does the 21 mm front board zone count?
2. **Height:** is there any cap above the cells? Today it is ≈ 113 mm above the can tops; a taller stack inside the footprint (architecture.md option C) was rejected only for leaving a void on the top deck.
3. **Performance trades,** if needed:
   - charge current below 25 A (give hours);
   - inverter below 400 W;
   - an external charger.

## 2e. How to evaluate a candidate (method that would have caught the v15 mistake)
For each candidate, before claiming a fit:
- write the row budget (as in §2a) for every deck;
- write the width budget;
- draw the plan view with the cell footprint outlined and every §2b item placed.

The fit claim for option B ("≈ 0 void at W 204") was made without packing the strip and turned out wrong (architecture.md §4a). Don't repeat that: pack first, claim second.

## 3. The task

Find a charger and an inverter, or one combined unit, plus a layout, so that:
- the converters, the power bay (contactor, main fuse, branch fuses, shunt, SB175), the fan(s) and the control board all fit above the cells inside the footprint in §2;
- their connector ends, airflow and service access also stay inside it.

Think as long as needed. Chris asked for the whole search to be reopened, not a tweak.

### Requirements (current baseline; change any only with a recorded trade-off)

| # | Requirement | Source |
|---|---|---|
| R1 | Pack 4S2P LFP, 12.8 V nominal, 10.0–14.6 V; charge to 14.2 V, 2-stage, inhibit below 2 ℃ | v14-baseline.md |
| R2 | Charge current **≥ 17 A** (≈ 12 h for 210 Ah); 25 A was the old baseline. The charger must be internal | Chris 2026-11-27 |
| R3 | Inverter **≥ 300 W continuous** (Chris 2026-11-27). Priority: combined inverter-charger ("extremely ideal") > separate internal inverter > last resort, no internal inverter + USB-C PD out (+ maybe external inverter); see §2d. pure sine, 120 V 60 Hz, NEMA 5-15 outlet, floating output (outlet ground to chassis), low idle draw / power-saving mode, remote off | baseline, N §3 |
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
- **Combined inverter-charger in one box (top priority, Chris 2026-11-27):** removes one housing and one set of AC terminals.
- **Converters side by side in one flat layer** instead of stacked, with the power bay on top or between them.
- ~~Drop the internal AC charger~~: rejected by Chris 2026-11-27 (the charger must be internal). Add a **USB-C PD output** instead (his idea).
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
