# Connectors: Molex Micro-Fit 3.0 THT right-angle (J2–J9) + Hirose FH12 FPC (J1); J10 USB-C

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | One connector per destination, right-angle, mated height ≤ 12 mm | spec §4; Chris |
| R2 | B+ pin: 5.2 A pick-up (75 ms, cold coil at 14.6 V) + ≈ 1.3 A board (buck at peak, relay) ≈ **6.5 A for 75 ms**, ≤ 1.8 A continuous, 18–22 AWG; **traces on J3 B+ and J4 sized for 5.5 A** | gv14-driver.md, buck-5v.md, review m14 |
| R6 | J3 is **1×4**: B+, LOAD+, GND, CHASSIS (IMD ring lug) | Chris 2026-11-27 |
| R3 | THT tails and pegs ≤ 2.5 mm below the board | intent §6 |
| R4 | J1: 12-pin, 0.5 mm FPC (0.3 mm thick) | intent §3 |
| R5 | Vendor-built harnesses from catalog parts | owner-requirements §2 |

## 2. THT vs SMT right angle (Molex drawings SD-43650-001 D8, SD-43045-001 H1, SD-43650-004 E4, SD-43045-004 G8)
| | THT (chosen) | SMT right angle |
|---|---|---|
| MPNs 2 / 3 / 4 / 2×4 | 43650-0200 / -0300 / -0400 / 43045-0800 (tin) | 43650-0209 / -0309 / -0409 / 43045-0809 (tin; -x10/-x11 are gold) |
| Retention | soldered pins + plastic pegs | metal clips (single row: still need plated holes) or solder nails (dual row) |
| Below board (1.6 mm) | pins 3.18 − 1.6 = 1.6 mm; pegs 3.3 − 1.6 = 1.7 mm ✓ | single-row clips ≈ 0.4 mm ✓ |
| Assembly | THT step (already needed for the AC05) | reflow |
| Stock (DigiKey API) | in stock | in stock |
**Pick THT:** cable pull and latch release load soldered pins, the board has a THT step anyway, and the KiCad footprints used in the area proof already exist. SMT is the fallback; footprints exist too. Vertical headers: ✗ mated ≈ 17.6 mm tall.

## 3. Board parts
| J | MPN (board) | Footprint (`Connector_Molex:`) | Mating receptacle | Mated height |
|---|---|---|---|---|
| J2 | 43045-0800 (0430450800), unless §3a | `Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal` | 43025-0800 | **10.82 mm** (PS-43045 §11) |
| J3 | **43650-0400** (0436500400) | `..._43650-0400_1x04_P3.00mm_Horizontal` | 43645-0400 | 7.17 mm (PS-43650 §11) |
| J5, J6 | 43650-0300 (0436500300) | `..._43650-0300_1x03_P3.00mm_Horizontal` | 43645-0300 | 7.17 mm |
| J4, J7, J8, J9 | 43650-0200 (0436500200) | `..._43650-0200_1x02_P3.00mm_Horizontal` | 43645-0200 | 7.17 mm |
| J10 | USB-C GCT USB4105-GF-A | see [usb-c.md](usb-c.md) | USB-C cable | 3.31 mm |
Totals: 1 × 2×4, 1 × 1×4, 2 × 1×3, 4 × 1×2. Lifecycle: **Active** (molex.com part pages, 2026-11-27, for 43045-0800, 43650-0200/-0300; 43650-0400 by DigiKey API); all in stock (API). Finish: matte tin on header and terminal (don't mix gold and tin).

## 3a. J2 option: Mini-Fit Jr 2×5 taking the shunt's own pigtail (if Chris's test fit passes)
| Item | Value | |
|---|---|---|
| Header | Molex 5569 right angle, 10 circuit, snap-in pegs: **39-30-1102** (30 µin gold, 94V-0, bulk), tin 39-30-0100; tray gold 46999-0542 (not stocked) | gold to match the pigtail's gold-looking terminals ⚠️ (tesla-shunt.md §3a); 39-30-1102 in stock (API) |
| Drawing | Molex 55690002-SD rev A2 (`039300020_sd.pdf`): bulk-packed numbers are "not recommended for new applications" | |
| Footprint | `Connector_Molex:Molex_Mini-Fit_Jr_5569-10A2_2x05_P4.20mm_Horizontal` | |
| **Mated height** | **13.8 mm** (drawing, "mated height to the top of board") | ✗ **over the 12 mm limit**: ≈ 0.1 mm under the lid with the board top at z 319.1 and lid z 333 |
| THT tail | 3.6 ± 0.76 mm below the seating face → 2.0 mm (max 2.76) below a 1.6 mm board | ⚠️ can exceed 2.5 mm |
| Area | ≈ +281 mm² (intent J2) | |
| Mating | tesla-shunt.md §3a: the pigtail housing isn't catalog; a catalog header is expected to clash at circuits 6–7 and 9–10 ⚠️ | test fit decides |

Pin map (header circuit = receptacle circuit): 1 VDD 5 V, 2 PC4, 3 MISO, 4 SCK, 5 OC_FLAG, 6 GND, 7 NSS, 8 MOSI, 9–10 empty. It differs from the Micro-Fit map, so the schematic changes with the choice.
**Recommendation:** keep the Micro-Fit 2×4 unless the test fit passes **and** main-battery accepts 13.8 mm under the lid.

Cable-side terminals (harness, main-battery's lane): 43030-0007 (20–24 AWG, tin), 43030-0038 (18 AWG, tin), 43030-0010 (26–30 AWG, tin).

## 4. Current rating (PS-43650 Rev. P, PS-43045 Rev. R §4.3; 30 K rise, reference values, all circuits powered)
| Wire | 2-circuit wire-to-board | 6-circuit |
|---|---|---|
| 18 AWG | 8.5 A | 7 A (1-row) / 6.5 A (2-row) |
| 20 AWG | 7 A | ≈ 5.5 A |
| 22 AWG | 6 A (interpolated) | ≈ 4.5 A |
- J3 B+ (4-circuit, between the 2- and 6-circuit values: ≈ 7.5 A on 18 AWG): ≈ 6.5 A for 75 ms, ≤ 1.8 A continuous ✓. J4: 5.2 A pulse ✓. J5 5 V: 2 A on 20–22 AWG ✓. J2: 50 mA ✓.
- 600 V rating ✓. Rated field temperature 65 °C / 10 yr (PS) vs 60 °C board air ✓; tin header 105 °C.

## 5. FPC (J1)
| Part | Contacts | Height | Temp | KiCad | Verdict |
|---|---|---|---|---|---|
| **Hirose FH12-12S-0.5SH(55)** | **bottom**, flip lock | 2.0 mm | −40…+85 °C | `Connector_FFC-FPC:Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal` | **✓** in the area proof, footprint exists |
| FH12A-12S-0.5SH(55) | top | 2.0 mm | −40…+85 | not checked | if the flex must face up |
| FH34SRJ-12S-0.5SH(50) | **top and bottom**, back lock | 1.0 mm | −55…+105 | none ⚠️ | best against a wrong-side flex; custom footprint |
| FH19C-12S-0.5SH | bottom | 0.9 mm | — | — | ✗ 0.2 mm FPC |
FH12 (catalog as of 01/2017): 0.5 A per contact (70 % if all loaded), 50 V ✓ (14.6 V), FPC 0.3 ± 0.05 mm gold-plated, **20 mating cycles**. Lifecycle Active (DigiKey API) ⚠️ Hirose part page not found. In stock.

## 6. Rules / traps
- **Header ≤ 10.16 mm from the board edge** (to the location peg), or the receptacle hits the board (SD notes).
- **Max wire insulation OD 1.85 mm** (PS §4.2). Thick-wall 18 AWG (e.g. UL1015 ⚠️ ≈ 2.4 mm) won't fit: the H1 harness must call thin-wall wire (tell main-battery).
- J1 flex: contacts face **down** (toward the board). Draw the flex stiffener to 0.3 mm total.
- Mated length 17.56 mm from the header back: fits the 25 mm plug room ✓.
- Adjacent FPC pins carry different cell potentials: the flex's fusible necks are the protection (v14-design-notes §1).

## 7. Open
- ⚠️ Check each KiCad footprint against the SD drawing at layout (hole sizes, peg hole 3.00 mm).
- ⚠️ J2 depends on Chris's pigtail test fit (§3a) and the 13.8 mm height.
