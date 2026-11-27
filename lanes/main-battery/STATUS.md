# main-battery status

- **Current task (Chris, 2026-11-27):** reopen the charger/inverter search so that everything above the cells fits in the module footprint (≈ 312 × 158 mm incl. end plates). Brief: `docs/handoff-converters.md`. Deliver `docs/converters.md`, a top-view packing figure per serious candidate, and a recommendation. No CAD until Chris picks.
- **Last result:** datasheets read (MEAN WELL NPB-240/360/450, NPP-450, PB-230/600, HEP-600C, ENC-360, HLG-320H, RSP-320, RPB-1600, NPB-750/1200, PB-1000, NTS-250P/400P/450, TS-400, BIC-2200, NTN-5K; Victron MultiPlus 12/500/20 120V, Phoenix VE.Direct 120V, Blue Smart IP67 120V; Samlex PST-300; Cotek SE350). Prices from Octopart / NAZ Solar, 2026-11-27.
  - Combined unit: only the MultiPlus 12/500/20 is small enough to consider; its connections are on its 183 × 101 end, so it fails all three orientations (183 > 158 flat; 312 + cable bend > 312 on its side; 312 tall upright). ⚠️ packing figure pending.
  - Strongest separate pair so far: **MEAN WELL RPB-1600-12 (1U charger, 300 × 85 × 41, PMBus/CAN, 20–100 A programmable, all connections on one end) + NTS-400P-112 + its 40 mm fan.** Packing not yet proven.
- **Blockers / waiting on:** none.
- **Next step:** 3D box-packing check + top-view figures (`cad/analysis/converter_packing.py`), then `docs/converters.md`, then recommendation and trade questions to Chris.
- **Key decisions so far (with reasons):**
  - Cells are the dominant constraint: nothing goes outside the module footprint (Chris).
  - Separate BMS board; the front zone is for the LED board only (Chris).
  - Charger internal, ≥ 17 A. Inverter: combined > internal ≥ 300 W > USB-C last resort (Chris).
  - GV14 contactor kept (Chris).
