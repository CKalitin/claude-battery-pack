# Pack architecture: where the converters and the power bay go (design-space study, 2026-11-27)

Trigger: Chris, 2026-11-27: "We're on a very bad branch… take two steps back… I want to solve this problem," about the 91 mm × 164 mm × 187 mm (2.8 L) void behind the cells (D38, `rear_end_void.png`).

Figure (to scale, catalog envelopes plus plug room): `versions/v16-c1-power-module/renders/architecture_options.png`, from `cad/analysis/architecture_fig.py`.

## 1. Requirements
| # | Requirement | Source |
|---|---|---|
| A1 | No dead space: the void must disappear, not shrink 10 mm | Owner 2026-11-27, owner-requirements §3 |
| A2 | Busbars on top; everything bolted from above, top-down install | Owner rule; contactor-mounting.md A1 |
| A3 | Tall, narrow proportions; cells upright | Owner |
| A4 | Each converter connector gets its plug room: charger DC 30, charger AC (right-angle C13) 36, inverter DC (PP45) 42, inverter AC (CN500) 20 mm | power-train.md "Converter plug room" |
| A5 | Fuses serviceable with the lid off | power-train.md P5, D19 |
| A6 | + to − ≥ 10 mm, pack copper to chassis ≥ 7 mm | Owner rule |
| A7 | Inverter cooling at least as good as now (it's already short, cooling.md) | cooling.md |

## 2. Root cause: a row-length budget that can't close
Above the cells there are two decks (charger, then inverter), each 312 mm long (the module length) and 187 mm wide. Lengths needed in x:

| Deck | Fan | AC plug | Converter | DC plug | Power bay | Sum | Over the module |
|---|---|---|---|---|---|---|---|
| Charger | 25 | 36 (+4) | 205 | 27 | 113 | 410 | **+98** |
| Inverter | 25 | 20 | 186 | 42 | 113 | 386 | +74 |

The power bay (113 mm) sits **end-to-end** with the converters on the same decks. Each deck therefore needs ≈ 400 mm over a 312 mm module, so the converters overhang the cells at the rear. The 140 mm fan is taller than the 103 mm above the cells, so it has to stand behind the module. **The void is the overhang plus the fan, projected down to cell level.** No millimetre trimming fixes this: even removing the fan and the C13 room leaves +37 mm.

## 3. The two branches that led here
1. **v13, 140 mm NF-A14 on the rear plate** (v13 README §8). It needs 140 mm of height, but only 103 mm exists above the cells. So it sits behind the module and sets a full-height rear zone. *Not questioned since.*
2. **v15 Concept D / C1, the power bay placed in front of the converters on the same two decks** (power-train.md, contactor-mounting.md). It was chosen for short copper and a single copper plane. It made each deck ≈ 400 mm long. Option A (2026-11-24, +42 mm at the rear for plug room) then grew the overhang instead of questioning the arrangement.

## 4. Candidates
Figure rows A–C; the rest are evaluated in the table only.

| | Architecture | Inside L × W × H [mm] | Volume | Void | Verdict |
|---|---|---|---|---|---|
| A | v16.3 as built | 424 × 187 × 318 | 25.2 L | 2.8 L behind the cells | ✗ the problem |
| **B** | **Side power spine**: converters pushed to one wall, the bay in the strip **beside** them along the whole module; 2 × 92 mm fans over the cells at the rear | **326 × 201 × 318** (W +14 for the GV14 contactor; 326 × 187 with a FET switch) | **20.8 L** (19.4 with the FET) | ≈ 0 at cell level; small at the deck ends | **Recommended** |
| C | Three-deck tower, power layer on top of the inverter | 326 × 187 × 390 | 23.7 L | ≈ 2 L on the top deck (the bay needs 113 of its 312 mm) | ✗ moves the void up |
| D | Converters upright in a rear column behind the cells | ≈ 421 long | ≈ same as A | ≈ 3.7 L over the cells (the bay only needs 113 of 312) | ✗ |
| E | Bay as a full-height column in front of the cells | ≈ 420 long | — | — | ✗ bolts go in sideways (fails A2; contactor-mounting.md M4) |
| F | Converters crosswise or side by side | — | — | — | ✗ geometry: charger 205 > 186.8 inside width; 135 + 100.5 = 235.5 side by side |
| G | One bidirectional inverter-charger instead of two units | — | — | — | Not searched in this pass. Known units in this power class are wider than the box ⚠️ (unverified) |
| H | Cells in 2 rows of 4 (squat box) | — | — | — | ✗ owner rejected squat layouts |

### Why B works
- **Width is the unused dimension.** The charger is 135 wide and the inverter 100.5, in a 186.8 inside width. That leaves a 52–86 mm strip along the whole deck length, today mostly air.
- **The bay moves into that strip** (the "spine"), so each deck only holds a converter plus its plugs:
  - charger deck: 25 + 36 + 205 + 30 = 296 ≤ 312;
  - inverter deck: 25 + 20 + 186 + 42 = 273 ≤ 312.
- **The fan changes from one 140 mm to two 92 mm fans side by side** (NF-A9 5V PWM: 92 × 92 × 25, 78.9 m³/h and 2.28 mmH₂O each, vs the NF-A14 5V PWM's 140.2 m³/h and 2.08 mmH₂O; noctua.at, read 2026-11-27).
  - The pair moves 158 m³/h at a slightly higher pressure, and it fits in the 103 mm above the cells.
  - Nothing stands behind the module any more, and the rear plate sits at the module's rear face.
- **The box gets 98 mm shorter and 14 mm wider at the same height.** Inside volume drops 17 %. Proportions become 333 × 216 × 320 mm outside, which reads more like a tower than today's 430 × 206 × 320.
- **Plug room is met at every connector** (A4).
- **The DC terminals are already on the spine side:**
  - The inverter's DC terminals (TB1) are at +y (MEAN WELL photo, D27 era) and the charger's DC block is in its +y half, so the spine goes on +y.
  - The cell orientation is mirrored, so pack + and pack − land on +y too.
  - Pack − still runs as a band from the rear cells, and pack + rises at the front cells.
- **Busbars stay on top** as one copper plane at z ≈ 232–238 (as in C1), now a long strip beside the charger. Every bolt is still tightened from above (A2), and the fuses stay under the lid (A5).

### Risks and checks before B is adopted
- ⚠️ **Spine packing.** In single file the bay parts need 361 mm of x (SB175 56, contactor 72, 5191 62, 2151 88, shunt 83) against ≈ 287 mm available. Two parts have to overlap in z or sit side by side, which the 62 mm strip can't do at charger level.
  - Candidate fix 1: the 2151 branch block above the charger end, in the inverter-level strip (86 wide). It is 45 tall in 42 of height ⚠️, so −3 mm.
  - Candidate fix 2: SB175 output leads instead of bolting the SB175 to the plane.
  - Proven only in CAD.
- ⚠️ **W +14 mm** comes from the GV14 contactor body (Ø ≈ 56 mm + clearances) passing the charger deck. A FET switch board (C1-FET variant, 8 mm tall) keeps W at 190, but carries its known short-circuit design risk (contactor-mounting.md M15).
- ⚠️ **Cooling.** The pressure-flow curve with two 92 mm fans and a different flow path has to be re-run (`cooling_v16.py`). Moving the inverter against the −y wall changes its side gap.
- ⚠️ **Re-done downstream:** shell flats, the SCS quote (shorter but wider; expected cheaper), the harness, the assembly order and the structure check.

## 4a. Spine packing check (2026-11-27, before CAD): W 204 as approved does not fit
Figure: `versions/v16-c1-power-module/renders/spine_packing.png` (`cad/analysis/spine_packing_fig.py`).
- **The strip** runs from the fan face to the front board's back parts: x −131.9 to 152, so **284 mm**. At W 204 it is 59.8 mm wide beside the charger.
- **In single file the bay parts need ≈ 390 mm:**

| Part | Length [mm] |
|---|---|
| Shunt | 83.5 |
| SB175 | 55.6 |
| GV14 | 72.5 |
| 5191 | 62 |
| 2151 | 88.5 |
| Gaps | ≈ 30 |

- **Parts can only share the width in pairs:**
  - 5191 + 2151 (both +, 23 + 23 mm with fuses) fit side by side in 59.8.
  - Shunt + SB175 (35 + 25.4 + 10 mm for +/−) = 70 do not.
- **Strip volume:** 284 × 59.8 × 97 = 1.6 L, against ≈ 2.3 L for the v16 bay. The study's "≈ 0 void" for W 204 was wrong: the strip was not packed before it was claimed.

| Fix | Strip use | Cost |
|---|---|---|
| **B1: W 204, SB175 off the plane** (two short 1/0 AWG leads from the plane up to an SB175 held in the lid), 5191 beside the 2151 | 272 of 284 mm | +2 cables, +4 lugs; breaks "busbars, not cables" for the output only |
| **B2: W 225** (+35 vs today), everything bolted to the plane in two lanes (shunt + SB175, 5191 + 2151) | 272 of 284 mm | Box 334 × 225 × 320 inside, ≈ 23.6 L (−6 % vs A, no void); squatter |
| Shunt or bay at cell level beside the cells (21 mm slot, y 79–100) | — | ✗ bolts sideways; the rods sit in the slot |
| Shunt on a raised plane over the fuses | — | ✗ fuses can't lift out |

## 5. Recommendation
Adopt B: a side power spine plus twin 92 mm fans. Build it first as a sandbox in `cad/concepts/` against the current module, and prove the spine packing and the assembly sweep before changing `tower15.py`. Owner decisions needed:
1. W +14 mm (GV14), or a FET switch at W 190.
2. Twin 92 mm fans instead of the NF-A14.

## 6. Sources
- Noctua NF-A9 5V PWM and NF-A14 5V PWM spec pages (airflow, static pressure, size), read 2026-11-27 ✓.
- Converter envelopes and plug room: power-train.md (MEAN WELL drawings) ✓ / ⚠️ as flagged there.
- Module length 312 mm: `tower15.STACK_L` after D29 (Mylar) ✓.

## 7. Open items
- Owner choice on §5.
- CAD sandbox of B; spine packing; cooling re-run.
