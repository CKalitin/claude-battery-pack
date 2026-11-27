# Tesla Model S shunt module (1016792-00-C): pack integration notes

This is the single source of truth for the shunt in the pack. Reverse-engineering detail (netlist, protocol, firmware) lives in the shunt repo: [CKalitin/tesla-model-s-2012-shunt-resistor](https://github.com/CKalitin/tesla-model-s-2012-shunt-resistor).

> ⚠️ Values marked **(U)** are **unconfirmed**: first hand measurements or one-count meter readings. Re-measure before freezing CAD or firmware constants.

## 1. Role in the pack (v14: 4S2P, 500 A for 30 s / 210 A continuous)

- Low-side in pack−, between the cells (**node A**) and the load-negative bus (**node B**). Path: cells → node A → bar → node B → inverter, charger, DC-out −.
- The control-board ground connects at node A. The module's J1 GND is the bar itself, so no isolator is needed here: the bar sits at board ground. The shunt repo warns against connecting J1 to a shunt in an HV pack, but that applies when the bar is at a different potential from the reader. In this pack it isn't.
- Kept as the current sensor by owner decision D3 (2026-11-24) over a plain shunt into the BQ76952.

## 2. Physical (U)

| Feature | Value |
|---|---|
| Bar | 1/8" (3.175 mm) copper, **35 × 83.5 mm** |
| Bolts | On the long centre line, **15 mm from each end**, so **53.5 mm** apart. **Through bolts** (owner, 2026-11-24 ✓). Thread and size **unknown**: modelled as **M8** until measured ⚠️ |
| Module PCB | **2 mm** thick, **25 mm** wide, centred along the bar; overhangs the bar's long edge by **8 mm**, so the footprint is **43 × 25 mm** |
| Component height | **5 mm** above the copper |
| Connector | **On the side that overhangs the copper** (owner, 2026-11-24 ✓): **on top of the 8 mm overhang strip** (the part of the PCB that hangs past the bar's long edge), at one end of the module. Top is **5 mm above the PCB (7 mm above the copper)**. Wires exit **straight up**, normal to the bar. |
| Keepout | Connector footprint × **≥ 35 mm** above the connector top, for the mated plug and the wire bend (estimate) |
| Still unknown | Bolt thread, a mate for the pigtail receptacle (§3a), which way the connector faces, which end of the strip it sits at (v16 models the end away from node B ⚠️) |

## 3. Interface

| Item | Value | Source |
|---|---|---|
| Connector | **Soldered pigtail (2026-11-27, §3a):** the harness is **soldered directly to the module PCB** (Chris, 2026-11-27 ✓). The two black 1×4 blocks on the overhang are **not a separable connector**. A ≈ 300 mm pigtail ends in a **10-position (2×5) Mini-Fit-Jr-style receptacle** with **8 cavities loaded**. That receptacle is **not a catalog Molex 5557**: it has non-standard polarization and a bridge between circuits 6 and 7 (the "key slot between pins 1 and 2"). The repo's "J1 pin n" numbers the 8 wires; they are **not** Molex circuit numbers (map in §3a). | Photos in the shunt repo; Molex SD-46992-0000 rev A10, SD-5557-003 rev K1 |
| J1 pin 1 | VDD +5 V | shunt repo `firmware/README.md` |
| J1 pin 2 | GND (the bar) | same |
| J1 pins 3–6 | NSS, SCK, MISO, MOSI | same |
| J1 pin 7 | OUT1 + OUT2 tied together (LM2903 over-current comparator outputs) | shunt repo `annotations/board/netlist.md` |
| J1 pin 8 | PC4 (STM8 TIM1_CH4), function unknown. Receptacle circuits 9 and 10 are empty | shunt repo `schematic/connections.csv`, `annotations/connector/` |
| Supply | 5 V (IHM-A-1500 VDDA 4.7–5.3 V; the STM8 runs at 5 V) | IHM datasheet |
| Logic | The STM8 needs VIH = 0.7 × 5 = 3.5 V. The STM32 bench reader worked at 3.3 V anyway, with 5 V-tolerant pins. **The ESP32 is not 5 V-tolerant (absolute max 3.6 V), so it needs a level shifter** on NSS, SCK, MOSI (up) and MISO (down), e.g. a TXU0104. | shunt repo, ESP32 datasheet |
| Protocol | SPI mode 0, MSB first, 500 kHz, 8-byte frames with CRC-8 (poly 0x07); init sequence in `src/shunt.c` | shunt repo |
| Scale | Raw value from command 0x41 ≈ **50 mA per count**: 1, 2 and 3 A read 19.3, 39.1 and 58.9 counts. Calibrated in firmware (offset and scale in the last flash page). | shunt repo commit 2bda143 |

## 3a. Connector J1: identification (2026-11-27)

**Conclusion.** The module has **one connector**, at the end of a pigtail soldered to its PCB:
1. **Board end (on the shunt module PCB itself, `photos/Shunt-1.jpeg`):** the 8 wires are **soldered directly to the module PCB** (Chris, 2026-11-27 ✓). The two black 1×4 blocks on the overhang strip (≈ 2.5–2.67 mm per position, ≈ 5 mm tall) are where the wires enter. Chris says they are soldered, so the blocks are **not a separable connector** to design around. The shunt repo calls this end **J1** (`schematic/parts.csv`: "8-way harness connector, pins numbered left to right in photo").
2. **Pigtail end (the module's only connector):** a ≈ 300 mm black jacketed pigtail (amber Kapton tape at both jacket ends; this is **factory Tesla construction**, not a repair ✓, see "Other units" below). It ends in a **10-position, 2×5 receptacle** with **female, gold-coloured terminals** and **8 cavities loaded**. The housing is **Mini-Fit-Jr-style** (4.20 mm pitch per the owner ⚠️, not measured from the photos). It is **not a catalog Molex Mini-Fit Jr. 5557 / 46992 housing** ⚠️: its polarization differs from Molex's drawing and it has three features the catalog part lacks (table below). **No catalog Molex plug or header is known to mate with it.** A standard 5559 plug or 5566 header is expected to clash at circuits 6–7 and 9–10 ⚠️ (inferred from the drawings, not test-fitted).

Confidence: soldered board end ✓ (Chris, 2026-11-27; photos); receptacle 2×5, female, 8 loaded, latch row, bridge ✓ (photos); "not catalog 5557" ⚠️ (photo against drawing, no physical comparison); pitch 4.20 mm ⚠️ (owner's statement; the photos have no scale, so Micro-Fit 3.0 is not excluded by the photos alone).

### Requirements
| # | Requirement | Source |
|---|---|---|
| R1 | A harness vendor can build H1 from catalog parts with buy links | Owner rule (catalog parts only) |
| R2 | The Tesla shunt module is not modified (no cutting its pigtail or housing) | Owner rule (purchased parts never modified) |
| R3 | Pinout known per physical cavity, not just per wire label | harnesses.md H1 |

### Evidence (shunt repo, commit 84f7515)
| File | Shows |
|---|---|
| `photos/Shunt-1.jpeg`, `Shunt-2.jpeg`, `Shunt-3.jpeg` | Module PCB: the board connector is **two 1×4 housings**, each with 2 square latch windows. 8 wires (brown, grey, purple, red / white, orange, black, blue) go straight up into a black jacket. Scale from the 25 mm PCB width (≈ 60 px/mm in Shunt-1): each housing ≈ 10.7 mm wide, so ≈ 2.67 mm per position (2.54 or 2.5 mm pitch ⚠️). In Shunt-2 and Shunt-3 the far end of the jacket goes to the black 10-way receptacle. |
| `annotations/connector/connector-3.jpg`, `connector_annotated.pdf` / `.xopp` | Mating face of the 10-way receptacle, latch up. Female terminals in 8 cavities; latch-row positions 4 and 5 are empty. The annotation labels each cavity (map below). |
| `photos/connector-1.jpeg`, `connector-2.jpeg` | Same receptacle from the latch side: a centred latch arm with a **raised guard rib on each side**, and the **two left latch-row towers joined into one block**. |
| **Other units (eBay, 2026-11-27):** [ebay.com/p/22054540490](https://www.ebay.com/p/22054540490) ("1016792-00-C") | Listing photos from three different sellers (EV Parts Guy, Pleasant Auto, and one on a white background) show **the same pigtail on every unit**: two 1×4 black blocks on the module PCB, ≈ 300 mm black jacket with **amber Kapton tape at both jacket ends**, a push-in fir-tree clip on the jacket, and the same black 2×5 receptacle. So the tape is factory construction, not a repair ✓. One photo shows the PCB underside: the **8 pins are through-hole soldered** (two rows of 4) with two locating-peg holes, which matches Chris's "soldered to the PCB" ✓. Label in one photo: "Tesla Motors 1016792-00-C REV01". Chris's unit has no fir-tree clip (removed or lost; it doesn't matter). |
| `measurements/2026-11-24_…md` | "10-pin Molex Mini-Fit (part TBD), key slot between pins 1 and 2. Top 5 mm above the PCB." The 5 mm height describes the **board** housings; the Mini-Fit is the pigtail end. Two different parts were merged into one line there. |

### Photo against the Molex drawing (mating face, latch up; S = square tower, C = chamfered tower, pointing where the chamfers point)
| Row | Molex catalog 10-ckt receptacle (SD-46992-0000 rev A10 bottom view; same shell as 5557) | Tesla pigtail receptacle (connector-3.jpg) |
|---|---|---|
| Latch row (ckts 6–10, L→R) | C↓ S S C↓ C↓ | **6+7 joined by a bridge**, 8 ?, 9 C↑, 10 C↑ (chamfers toward the latch) |
| Other row (ckts 1–5, L→R) | S C↓ C↓ S S | S C↓ C↓ **C↓** S |
| Latch | Plain centred arm | Centred arm **flanked by two guard ribs** |
| End wall at ckt 10 | Solid | **Window/slot** (light shows through) |

Circuit numbering is Molex's convention (SD-5557-003 sheet 2, "Circuit size layout", wire-entry view; mating view per sheet 1, third-angle projection). Applying it to a non-catalog housing is ⚠️.

### Pin map (Molex circuit ↔ repo J1 wire ↔ signal)
| Receptacle circuit | Position (mating face, latch up) | Repo J1 pin | Signal |
|---|---|---|---|
| 1 | bottom row, left | 1 | VDD +5 V |
| 2 | bottom row, 2nd | 8 | PC4 ("PIN 8") |
| 3 | bottom row, 3rd | 5 | MISO |
| 4 | bottom row, 4th | 4 | SCK |
| 5 | bottom row, right | 7 | OC_FLAG ("PIN 7") |
| 6 | latch row, left (bridged to 7) | 2 | GND = the bar (VSS) |
| 7 | latch row, 2nd (bridged to 6) | 3 | NSS |
| 8 | latch row, 3rd | 6 | MOSI |
| 9, 10 | latch row, 4th and 5th | — | empty |

Source: cavity labels in `annotations/connector/connector.xopp` (owner's continuity probing) ✓; Molex circuit numbers ⚠️ (convention applied to a non-catalog housing). Chris's "notch between the top-left first and second pins" is the **bridge between circuits 6 (GND) and 7 (NSS)**.

### Candidates
| Candidate | Result | Why |
|---|---|---|
| Molex Mini-Fit Jr. 5557 receptacle, 39-01-2100 (94V-2) / 39-01-2105 (94V-0) / 39-01-3105 (black) | ✗ as the Tesla housing | Same family and size, but the polarization pattern, the 6–7 bridge, the latch guards and the end window don't match SD-5557-003 / SD-46992-0000 |
| Molex 46992-1010 (glow-wire 5557) | ✗ | Same tower pattern as 5557 (SD-46992-0000 A10) |
| Molex Mini-Fit Sigma 172708-1010 | ✗ | Wide ribbed lever latch, released 2019 (SD 1727080002 C7). Doesn't match the photo or a 2012 part |
| Molex polarizing key 15-04-0211 (42232-BA) in a 5557 | ✗ | Goes into a terminal cavity from the wire side and is natural colour (SD-42232). The photo has no key in a cavity; the bridge is moulded |
| Molex Mini-Fit TPA (receptacle 30067, plug 15976101, keys 30072) | Not checked ⚠️ | 15976101's drawing mates it with receptacle 30067; the 30067 drawing wasn't fetched. Its "keys" are the next thing to check |
| Molex Micro-Fit 3.0 43025-1000 (3.0 mm) | Not excluded by photos ⚠️ | Same look. Excluded only by the owner's statement that it's Mini-Fit (4.2 mm) |
| Amphenol Minitek Pwr 4.2, TE Mini-Universal MATE-N-LOK, Würth WR-MPC4 (4.2 mm clones) | Not checked ⚠️ | Some clones have latch guards; none compared |
| Tesla-specific (customer-coded) Molex housing | **Most likely** ⚠️ | Explains catalog look plus non-catalog coding; Tesla's mating header is on the vehicle BMS board, not a catalog part |

### What mates, and the recommended harness
- **The pigtail receptacle has no known catalog mate** (R1 fails). A standard Mini-Fit Jr. plug **39-01-3103** (5559, 10 ckt, no ears; SD 55590001 A4 ✓ exists) or vertical header **39-28-1103** (5566) has a wall between circuits 6 and 7 and chamfered cavities where this housing has square towers. Inferred: it won't mate ⚠️ (test fit open). Cutting the bridge or the plug's wall modifies a part (R2) and voids the keying.
- **The pigtail is part of the module** (soldered at the PCB, Chris 2026-11-27), so replacing it at the board would mean desoldering a purchased part (R2). H1 therefore has to **mate with the Tesla 10-way receptacle**.
- **Recommended next step:** test-fit a catalog Mini-Fit Jr. plug **39-01-3103** (+ male 5558 terminals) and a vertical header **39-28-1103** against the receptacle. If one mates without modification, H1 = that plug (or the BMS board carries that header, a pcb-lane decision) → J2.
- **If neither mates:** no catalog route exists (R1 vs R2 conflict). The options are for Chris to decide: (a) desolder the pigtail and solder a new one (breaks R2), (b) cut the pigtail behind the receptacle and splice a catalog connector (breaks R2), or (c) find Tesla's mating harness (the BMS-side connector of the Model S pack, from salvage) ⚠️.
- Catalog Mini-Fit Jr. parts (molex.com part pages ✓, fetched 2026-11-27): female crimp 5556 **39-00-0039** (24–18 AWG, tin) / **39-00-0047** (28–22 AWG, tin); male crimp 5558 **39-00-0041** (24–18 AWG, tin) / **39-00-0049** (28–22 AWG, tin). The Tesla terminals look **gold** ⚠️: don't mate tin against gold, so pick the gold 5558 variant if the adapter is used (MPN not selected ⚠️). Prices not collected (DigiKey and Mouser block scripted access).

### Traps found
- **"The connector" described two ends of one harness.** The 2026-11-24 measurements merged the 5 mm soldered board end and the 10-position receptacle at the pigtail end into one line. Rule: name each end by where it sits (soldered board end / pigtail connector) and give each its own photo.
- **Repo J1 pin numbers aren't cavity numbers.** J1-2 (GND) is receptacle circuit 6, J1-3 (NSS) is circuit 7, and so on. Rule: a harness drawing uses the cavity map above, never "pin n".
- **Mini-Fit look-alike ≠ Mini-Fit catalog.** Tower shapes and bridges are customer-specific. Rule: compare the polarization against the Molex drawing before naming an MPN.
- Molex, DigiKey and Mouser block curl. Molex part pages load in a headful Playwright browser under `xvfb-run` (drawings saved from there).

### Sources
- ✓ Molex SD-5557-003 rev K1 (39-01-2100 / 5557 receptacle, 2024-03-04): circuit layout, dims (A = 22.20 mm for 10 ckt).
- ✓ Molex SD-46992-0000 rev A10 (46992-1010, 2024-02-22): mating-face polarization detail.
- ✓ Molex 55590001-SD rev A4 (5559 plug 39-01-3103, 2025-09-15): mates with 5557 and 172708; male terminal 5558.
- ✓ Molex SD-42232 (polarizing key 15-04-0211): installs from the wire side into a cavity.
- ✓ Molex 1727080002-SD rev C7 (Mini-Fit Sigma 172708).
- ✓ Molex part pages 39000039 / 39000047 / 39000041 / 39000049 (terminal descriptions).
- ✓ Shunt repo photos and annotations (above). ⚠️ 4.20 mm pitch: owner's statement only.

### Open items
- [ ] ⚠️ **Measure the receptacle pitch** with calipers: centre to centre across 5 cavities = 16.8 mm (Mini-Fit, 4.20) or 12.0 mm (Micro-Fit, 3.0). Also the overall width (22.2 mm Mini-Fit catalog).
- [ ] ⚠️ **Test-fit a catalog Mini-Fit Jr. plug 39-01-3103 and header 39-28-1103** against the Tesla receptacle: does either mate fully and latch, with no force at circuits 6–7 and 9–10? This decides H1.
- [ ] ⚠️ Fetch the Molex Mini-Fit TPA 30067 receptacle and 30072 key drawings to rule them in or out.
- [x] Kapton-taped pigtail: original Tesla construction (2026-11-27, other units below).

## 4. Electrical

| Quantity | Value | Notes |
|---|---|---|
| R_sh | **≈ 20 µΩ (U)**, range 10–30 µΩ | 0.1 mV bolt to bolt at 5 A, one meter count. Replaces the earlier assumed 100 µΩ. |
| At 500 A for 30 s | 10 mV, **5 W**, 150 J | Negligible heating |
| At 210 A continuous | 4.2 mV, 0.9 W | — |
| Front-end rating | IHM-A-1500: 1,500 A starter (cranking) class, ±300 A continuous | 500 A for 30 s is above the continuous figure but in the starter class. Acceptable on heat. Bench-verify at ≥ 300 A if possible. |
| Resolution | ≈ 50 mA per count | 10,000 counts at 500 A |

## 5. Grounding and orientation (updated for R_sh ≈ 20 µΩ)

![Shunt orientation](img/04_shunt_orientation.svg)

*(Figure from the 8S design: the topology is unchanged, but its numbers assume 100 µΩ. Use the table below.)*

- **Correct orientation:** the module's VSS bond sits at node A, the cell side, where the board ground is. Then no current flows in the harness ground wire.
- **Wrong orientation:** the bond sits at node B. The harness ground wire (R_h ≈ 26 mΩ, 22 AWG × 0.5 m) then runs in parallel with R_sh:

$$I_h = I\,\frac{R_{sh}}{R_{sh}+R_h} = I\,\frac{20\,\mu\Omega}{26.02\,\text{m}\Omega} \approx 0.077\,\%\ \text{of } I$$

- $I_h$ = harness ground current [A]
- $I$ = pack current [A]
- $R_{sh}$ = shunt resistance [Ω]
- $R_h$ = harness ground wire resistance [Ω]

| Case | I | I_h | Reading error | Ground offset |
|---|---|---|---|---|
| 500 A burst | 500 A | 0.38 A | −0.08 % | 10 mV |
| 210 A continuous | 210 A | 0.16 A | −0.08 % | 4.2 mV |

- 0.38 A is well within 22 AWG's capacity, so **orientation is no longer a safety item**. Keep the rule anyway (correct orientation is free); it is now about accuracy only.
- The current sign flips with orientation. Fix the sign in firmware from a known-direction bench current.

## 6. Bench tests

**2026-11-24: bonded end and bar resistance (U)**

Setup:
- Bench supply in constant current, 5 A, bolt to bolt.
- DMM on the 200 mV range (0.1 mV resolution).
- COM on J1 GND at the connector.
- Module powered from the NUCLEO (a jumper also reads the STM32).

| Measurement | Current on / off | Reversed current |
|---|---|---|
| Bolt to bolt | 0.1 mV | — |
| J1 GND → bolt "A" (supply − in the first run) | 0.0 / 0.0 mV | 0.0 mV |
| J1 GND → bolt "B" | +0.1 / 0.0 mV | −0.0 mV |

An earlier attempt measured against the NUCLEO GND through a jumper and read about 3.5 mV on both bolts. That's an offset: module supply current through the jumper's resistance. Removed by measuring at the connector and differencing on/off.

**Conclusions (preliminary):**
- R_sh ≈ 20 µΩ.
- Leaning towards VSS bonded at bolt "A". The sign flip on bolt "B" sits below one meter count, so this is **not conclusive**.
- **Action:** physically mark bolt "A".

## 6a. Harness (v16.1, modelled)
- J1 (modelled as a Mini-Fit Jr 2×5 envelope 9.6 × 21 × 13 mm ⚠️; in reality the harness is soldered to the PCB through two 1×4 blocks ≈ 21 × 5 mm, and the Mini-Fit-style receptacle is ≈ 300 mm away on the pigtail, §3a) on the **+x overhang**, the side facing the front board. Wires go straight up 30 mm, then +y to y 7 to stay out of the Z-strap's lift-out prism, over the contactor, and down into j_shunt (Micro-Fit 3.0 2×4) on the board's top edge. 7 × 22 AWG (J1 pins 1–7), 188 mm. Details: [signal-wiring.md](signal-wiring.md).
- Board ground is a separate 18 AWG wire from a ring under the **node-A nut** (the cell side), per §5. J1 pin 2 still connects to the same ground through the bar, as analysed in §5.

## 7. Open items (deferred: characterise the shunt properly)

- [ ] 4-wire R_sh with a µV-resolution meter (5½ digit or better), or 20–50 A of test current. Measure at 2+ temperatures for the temperature coefficient.
- [ ] Repeat the bonded-end test with real resolution. Confirm bolt "A".
- [ ] Compare the module's calibrated SPI reading against a reference shunt across 0–300 A.
- [ ] Bolt thread and size. Connector: see §3a open items (pitch, board-end part, test fit).
- [ ] Decide whether to use J1 pin 7 (hardware over-current comparator) as a second trip input to the contactor driver.
- [ ] Check that the IHM-A-1500 gain range resolves the 10 mV full-scale signal at 500 A well enough at low currents.
