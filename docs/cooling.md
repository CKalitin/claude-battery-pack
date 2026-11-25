# Cooling (v16.1 re-run, 2026-11-25)

Model: `cad/cooling_v16.py` (output: [v16-cooling.txt](v16-cooling.txt)). It replaces the v14 area-ratio estimate ([v14-design-notes.md](v14-design-notes.md) §11) with a flow network: fan curve, every perforated plate as an orifice, the 8 mm gap behind the LED board, and three parallel paths at the converter plane (inverter level, charger level, the gaps beside the cells), with a short circuit through the rear holes around the fan.

## Result

| Quantity | v14 estimate | **v16.1 model** |
|---|---|---|
| Heat (UPS case: 400 W out + charging at 25 A) | 75 W | **77.1 W** |
| Front air holes | 287 | **244** (43 lost under control parts, T17) |
| Fan flow / through the box / short circuit | 45 / ≈ 17 / — m³/h | **53 / 11.3 / 41.8 m³/h** |
| Air rise inside the box | ≈ 10 K (allow 10–15) | **12.7 K** ✓ (sealed box: 34 K) |
| Flow along the inverter | not checked | **3.7 m³/h** (0.22 × MEAN WELL's 10 CFM) ✗ |

**The box is fine; the inverter at 400 W continuous is not proven.** The rear-gap growth (18 → 40 mm) and the rear lid cut-outs (filled by the pass-throughs) don't change the picture; losing 43 front holes and the full rear grid's short circuit do.

## The inverter's rating
From the vector data of MEAN WELL's derating curve (NTS-400P-SPEC 2026-03-26, page 3, read with pdf.js):
- **Forced air, "10 CFM fan" 5 cm from the DC end** (mechanical drawing, page 6): 100 % load to 40 °C, falling to 40 % at 70 °C.
- **Natural convection:** about 60 % (240 W) up to about 55 °C, 50 % at 60 °C. ⚠️ The axis labels on this curve aren't evenly spaced; read as labelled.
- The NTS-400P has **no fan of its own**: CN100 is a fan output (12 V, 0.4 A, PWM) for an optional 4020 fan (suggested: CCHV CHT4012BH-W20D).
- Its over-temperature protection shuts it down, so this is a capacity limit, not a safety hazard.

## Options

| Option | Inverter flow (vs 10 CFM = 17 m³/h) | Box rise | Cost | |
|---|---|---|---|---|
| A. As drawn (fan exhausts at the rear, full rear grid) | 3.7 m³/h (0.22×) | 12.7 K | — | ✗ for 400 W continuous |
| A′. Same, **fan flipped to intake** (blows straight at the converter AC ends, 40 mm away) | jet ≈ 5.9 m³/h (0.35×) onto the inverter end ⚠️ (annulus-share estimate) | ≈ 12.7 K | free | better, still short |
| B. **Blanking sheet** behind the rear plate outside the fan circle (5052 .063, black, clamped by the 7 plate screws; holes still visible outside) | 10.1 m³/h (0.6×) | 6.1 K | 1 SCS part, ~$20 ⚠️ | better, still short |
| C. **MEAN WELL's own condition**: 40 × 40 × 20 fan on CN100, 5 cm in front of the DC end | 10 CFM by definition | — | 1 fan ($7.25, Sunon MF40201VX-1000U-G99, Digi-Key, 10.8 CFM) + a bracket | No mount point found yet: the 5 cm spot at x 54–74 sits over the shunt, with nothing under it to fix a bracket to |
| D. Limit the inverter in firmware to 240 W continuous (natural-convection rating) | — | — | free | Changes the 400 W spec (owner decision) |

**Decision:** A′ now, because it is free. B, C and D each add a part or change the spec, so they wait for the bench test. Order:
1. **Flip the NF-A14 to intake** (zero parts; the jet then lands on the converters instead of the box pulling air past them).
2. **Bench test** at 400 W pass-through: log inlet/exhaust air and watch for inverter OTP/derating (telemetry list). Target ≤ 15 K box rise, no OTP in 2 h.
3. If it derates: **B** (one flat SCS sheet, no extra fasteners), then **C**.

## Model assumptions (⚠️)
- Fan curve shape between Noctua's two published points (140.2 m³/h free, 2.08 mm H₂O shut-off): p = p₀(1 − (Q/Q₀)^1.4).
- Orifice Cd 0.78 for 4.75 mm plates with Ø4.8 holes and for the 4.6 mm diffuser + board stack with Ø6 holes.
- Converter bodies as a lumped K = 4 on their end-face area; bypass channels K = 1.5. No MEAN WELL data on internal impedance.
- Walls: U = 9.5 W/(m²·K) outside in series with 7 inside (v14 §11); enclosure area 0.563 m².

## Heat sources (UPS case)
| Source | W | |
|---|---|---|
| NTS-400P-112 at 400 W, η 91 % | 39.6 | MEAN WELL spec 2026-03-26 ✓ |
| NPB-450-12 at 25 A × 14.2 V, η 92 % | 30.9 | MEAN WELL spec 2026-07-06 ✓ (v14 had assumed 92 %) |
| GV141BAX coil hold 0.23 A × 12 V | 2.8 | GV14 datasheet rev 28-Apr-2022 ✓ |
| Control board | 2.0 | estimate ⚠️ |
| Shunt module, fan motor, power path at 40 A | 1.9 | estimates / Noctua 0.99 W ✓ |
| **Total** | **77.1** | |
