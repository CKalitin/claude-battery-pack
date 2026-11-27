# Enclosure material and finish (written 2026-11-27)

Closes the CLAUDE.md documentation gap "enclosure material and Roadster-red powder coat: no rationale or SendCutSend finish options recorded". The choices themselves date from v5–v16 (5052 shell, 6061 plates, gloss red from v12). This page records why they hold and what else SendCutSend offers.

## 1. Requirements
| # | Requirement | Source |
|---|---|---|
| E1 | SendCutSend or catalog only; SCS order < $2,000 | owner-req §2 |
| E2 | Shell bent from sheet (L-halves, 30° facets, lip, lid) | v13 |
| E3 | Carries the 1 g handle load and the pack's ≈ 25 kg ⚠️ | structure.md, v16-structure.txt |
| E4 | Chassis is protective earth (inlet PE, outlet ground), so it must conduct and bond | review M7 |
| E5 | Walls help shed heat (U ≈ 4 W/m²K through the wall, cooling model) | cooling.md |
| E6 | Looks good: gloss colour, crisp hole grids | owner |

## 2. Material
| Option | Bends (E2) | Mass of the option D shell, ≈ 0.36 m² of sheet | Notes | Verdict |
|---|---|---|---|---|
| **5052-H32 aluminium .063 (shell)** | ✓ the standard bendable aluminium at SCS; tight radii | 0.36 m² × 1.6 mm × 2.68 g/cm³ ≈ **1.5 kg** | Conducts and bonds; corrosion-resistant | **✓ shell and lid** |
| **6061-T6 aluminium (flat plates: .125 front/rear, .313 module end plates)** | ✗ T6 cracks on tight bends, but these parts are flat | — | Stiffer and stronger (yield ≈ 276 vs 193 MPa ⚠️ handbook values) where the plates carry the rods and the handle load | **✓ plates** (D31: .187 → .125 saved ≈ $128) |
| Mild steel (.060) | ✓ | ≈ **4.3 kg** (7.85 g/cm³) | Heavier for no structural need; rusts at every chip in the coat | ✗ +2.8 kg |
| 304 stainless | ✓ | ≈ 4.4 kg | No coat needed, but the look is not red | ✗ mass, look |
| 7075-T6 | ✗ poor bending | — | — | ✗ |

**SCS powder coat (sendcutsend.com/services/powder-coating, read 2026-11-27):**
- Applies to all 7 SCS powder-coat materials (5052, 6061, 7075, 4130, mild steel, 304, 316), .048–.750″ thick.
- Max part 30 × 36″ (762 × 914 mm) ✓ for the option D shell.
- Min hole Ø .063″ ✓ (grid holes Ø4.8).
- +3–5 days.

## 3. Finish
SCS offers **15 colours:**

| Black | Grey | White | Colours |
|---|---|---|---|
| Gloss, Matte, Textured, Wrinkle | Gloss, Metallic, Textured | Gloss, Matte | Gloss Blue, Bronze, Gloss Green, Safety Orange, **Gloss Red**, Gloss Yellow |

- **Gloss Red is the colour used since v12.** "Roadster red" is the design name; SCS calls it **Gloss Red**, and there is no custom-colour option.
- The other parts stay as they are: copper bare, G10 natural, the white acrylic diffuser.
- ⚠️ **Not checked:** SCS's exact RAL or Pantone for Gloss Red, and whether masking is offered for grounding pads. The PE bond lands under an existing front-plate screw, which scrapes through the coat; a star washer would be a better guarantee.

## 4. Open items
- ⚠️ Re-quote the shell from the tower17 flats (docs/budget.md scaled it).
- ⚠️ PE bond through the powder coat: star washer, or a masked pad if SCS offers masking.
