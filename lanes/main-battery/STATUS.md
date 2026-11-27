# main-battery status

- **Current task (from Chris, 2026-11-27):** find a new charger and inverter, or ideally one combined inverter-charger, so that everything above the cells fits in the module footprint, end plates included (≈ 312 × 158 mm). The full brief is in **`docs/handoff-converters.md`**. Chris's dated answers are in `docs/owner-requirements.md`.
- **Last result:** the anthropic-cloud session merged `power-train-rethink` into `master`. That brings in:
  - v16.3: Mylar insulators, M6 rods, structure check, SCS ≈ $1,825, firmware-rating baseline;
  - the architecture study (`docs/architecture.md`);
  - the spine packing check;
  - the converter handoff.

  Option B (side spine, W 204) is paused.
- **Blockers / waiting on:** none. Ask Chris trade-off questions directly, with numbers.
- **Next step:**
  - write `docs/converters.md` in the cells.md pattern;
  - draw a top-view packing figure for each serious candidate;
  - send Chris a recommendation.

  No CAD until he picks.
- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A.
  - Inverter order of preference: combined unit > internal inverter ≥ 300 W > last resort, USB-C PD out + maybe an external inverter.
  - GV14 contactor kept.
