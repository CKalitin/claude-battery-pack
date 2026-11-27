# Gate: phase 1 (architecture and parts) — PASSED 2026-11-27

**Inputs judged:** intent.md, decisions.md B1–B12, parts/*.md (17 files), datasheets/ (sources.csv), sim/precharge-pump/, at commit `9b433be`.
**Reviews:** `pcb-review-parts` (independent, gates/phase1-review.md: 1 BLOCKER, 5 MAJOR, 14 MINOR, 8 NOTE) → fixes (decisions B8–B12 + `pcb-bms-review-fixes`) → `pcb-review-parts-recheck` (independent, gates/phase1-recheck.md: 23 closed, 4 partly, 1 accepted risk; new R1 BLOCKER, R2 MAJOR, R3–R6 MINOR, R7–R11 NOTE) → R1–R7, R10, R11 fixed exactly as the re-check prescribed (`9b433be`).

## Checklist (skill references/parts.md)
| Item | Evidence | |
|---|---|---|
| Block diagram; every block maps to parts; losers written down | intent.md §4; parts/README.md; decisions.md | ✓ |
| Audit per non-trivial part, datasheet saved | parts/*.md; datasheets/sources.csv (PDFs gitignored) | ✓ |
| Abs max vs worst case | per audit; both reviews recomputed | ✓ |
| Every value calculated | per audit; ad-dividers.md; the reviewers' recomputations match | ✓ |
| MLCC derating; resistor power and pulse | buck-5v.md, bq76952.md §3, self-test.md | ✓ |
| Footprint matches the exact package suffix | names checked; geometry of RAK0009A, TSDSON-8 FL, Panasonic SOP4 (if used), USB4105, SRP5030 lands **deferred to layout** | ⚠️ layout |
| Lifecycle and stock at the fab's source, dated | DigiKey API 2026-11-27: all 35 picks active and stocked (BQ7695204, not the out-of-stock BQ76952) | ✓ |
| Independent reviewer re-read datasheets and recomputed | two reviews above | ✓ |

## Carried to the bench (not closable on paper)
- **REG0 on by default in the -04** (B12, accepted risk with the REG1 overdrive fallback).
- **RAM trial before the first OTP write** (bq76952.md §7.2): DDSG/DCHG must enable with FET_CTRL_EN set and Mfg Status Init FET_EN = 1 (R1).
- Stacked relay clamps ≤ ≈ 150 V (clamp max unpublished); GV14 kick on the upper gate (scope V_GS); 18 V zener leakage at 14.6 V and 60 °C (sleep budget ≈ 10.8 µA summed max, R8).
- CN301 levels; shunt OC polarity; flex NTC B value; OTD/UTD vs EVE discharge limits.

## Owner
Phase 1 needs no owner sign-off. Phase 0 (intent.md) still needs Chris's sign-off before the schematic.
