# Wire harnesses: what's needed, pinouts, lengths, and who builds them (option D, 2026-11-27)

**Owner rule (Chris, 2026-11-27): "I want to make none myself."** Every harness arrives built and tested. The vendor also terminates any purchased part that comes with flying leads (GV14 coil, fan), so nothing gets crimped at home.

**Status:** pre-CAD. Lengths come from the option D packing coordinates (`cad/analysis/converter_packing.py`): Manhattan route + 30 mm per end + service loops. **Every length is ⚠️ until the tower17 CAD routes them.** BMS-side connectors follow the pcb lane's placement (`lanes/pcb/bms-area.md` §4); their pin numbers are proposals that pcb fixes in the schematic. This replaces `signal-wiring.md` (v16) for option D. Its rules (R1–R10) still apply.

## 1. Requirements
| # | Requirement | Source |
|---|---|---|
| W1 | Chris builds no harness: no crimping, no soldering, no cutting | Chris 2026-11-27 |
| W2 | Ordered online from a vendor with a configurator or instant quote; no emailing to get a part | owner-req §2 |
| W3 | Every wire tapped off pack copper is fused at the source end, within 178 mm (7 in) | signal-wiring R6 (ABYC E-11 ⚠️ from memory) |
| W4 | Connectors mate from above; no new holes in purchased parts | CLAUDE.md, signal-wiring R2, R7 |
| W5 | Mains leads never bundled with low-voltage leads | signal-wiring R9 |
| W6 | Lid-mounted parts get a 150 mm service loop so the lid can stand beside the pack | baseline M8 |
| W7 | Wire gauge sized for current and fuse; 105 ℃ insulation | — |
| W8 | Board ground at shunt node A | tesla-shunt.md |

## 2. Who builds them
| Vendor | How you order | Range | Notes | Verdict |
|---|---|---|---|---|
| **Loombotic** (loombotic.com, YC-backed, US) | **Online harness editor + instant quote**; in practice the guest editor is view-only (2026-11-27: "Couldn't load this harness"), so a price needs a free account, which Chris would create ⚠️; add to cart; or upload a drawing PDF and AI reads it | 32 AWG–4/0, qty 1–10,000+, ~7 days; IPC/WHMA-A-620; **100 % electrically tested**; every order reviewed by an engineer | Verified catalog in the editor (read 2026-11-27): **Molex Mini-Fit Jr (62), Micro-Fit 3.0 (46), Mega-Fit, Amphenol AT/ATM/ATP, Panduit, Phoenix, Alpha Wire**. JST XH/VH, Anderson PP45 and FASTONs are **not** in the verified catalog: they'd be "new custom part" lines (engineering review) ⚠️. Shipping to Canada not stated ⚠️ | **Recommended:** one vendor for signal and power cables (4/0 covers our 10 AWG), true online ordering |
| **NextPCB cable assembly** (nextpcb.com/cable-assembly-quote) | Online quote tool (estimated price) → sales review within 1 working day. **Live estimate 2026-11-27: $99 for a 300 mm Micro-Fit 2×4 ↔ 2×4, 22 AWG UL1007, the same at qty 1 and qty 5:** a per-design minimum. Service launched 2026-08-14; "Free assembly for 5 pcs" banner ⚠️ terms unread | JST, Molex, Hirose, IDC; MOQ 1 | China. Already our PCB sponsor; could ship with the front board, and may fold into the sponsorship (ask Zep) | **Alternative**, or first choice if Zep includes harnesses |
| PCBWay | "Cable Wire Harness Assembly" as an add-on to a PCB/PCBA order; price after file review | — | Natural bundle with the BMS PCBA if it stays at PCBWay | Alternative |
| CurrentConnected (custom battery cables) | Online builder | **6 AWG–4/0 only** | Our DC leads are 10 AWG | ✗ gauge |
| Molex off-the-shelf Micro-Fit cable assemblies (Digi-Key) | Catalog | Fixed lengths, straight-through | Only fits harnesses with Micro-Fit at both ends; we have none | ✗ not useful here |
| WellPCB, OurPCB/cableharnessassembly.com, RushPCB, Miniproto | Quote by email or review | — | Fails W2, or no configurator found | ✗ |

**Live quotes 2026-11-27 (pre-CAD lengths, drawings `docs/harness-drawings/harness_*_preCAD.pdf`, each with a BOM page; qty 1):**

| Assembly | Loombotic instant quote (unit, qty 1) | qty 10+ | NextPCB tool estimate |
|---|---|---|---|
| A BMS LV harness (10 branches, GV14 consigned) | **$1,040.10** (quote #822) | $967.29 | $99 min, final after review |
| B Charger DC set (3 cables) | **$236.84** (#823) | $220.26 | $99 min |
| C Inverter DC set (2 cables, PP45) | **$277.77** (#824) | $258.33 | $99 min |
| D Mains set | **$440.30** (#825) | $409.48 | $99 min |
| E Fan pigtail (2 wires + XH) | **$249.56** (#826) | $232.09 | $99 min |
| **Total** | **$2,244.57** | | ≈ $495 + review |

- Loombotic has a floor of about $230–250 per design even for a 2-wire pigtail (E).
- The first A quote (#820, drawing without a BOM) was $1,012.35. Without a BOM page, the B quote failed ("couldn't find a Bill of Materials").
- These are instant AI quotes; Loombotic says an engineer reviews every order ⚠️.

**Price and quality (searched 2026-11-27):**
- **No independent reviews exist** for any of the three harness services (Loombotic: directory listing only; NextPCB: own pages only; PCBWay: no harness-specific reviews). All three claim IPC/WHMA-A-620, which is the quality bar to hold them to. Loombotic and NextPCB claim 100 % electrical test.
- **Price is per design, not per wire.** NextPCB's $99 minimum per harness design means **15 separate harnesses ≈ $1,400** vs ≈ $105 in docs/budget.md.
- **So consolidate into 4 multi-branch assemblies:**
  1. BMS low-voltage harness: J3–J9 branches to the taps, GV14, relay coil + AC sense, CN301, button, LED, NTC;
  2. charger DC set: P1a, P1b, P2 with the relay;
  3. inverter DC set: P3, P4 with PP45;
  4. mains set: A1, A2, A3.

  Add the fan pigtail as a 5th small line, or buy a fan that already has an XH plug. That's **≈ 5 × $99 ≈ $500 at NextPCB** list (or $0 if Zep sponsors). Loombotic is unpriced until there's an account.

**Plan:**
- Order every harness below as one Loombotic order, or one NextPCB order if Zep covers it, after tower17 fixes the lengths.
- The vendor procures the device-side parts it terminates: GV14 (if consigned, ship it), Sunon fan, relay receptacles, PP45, JST housings, the right-angle C13.
- ⚠️ Get a live quote from the editor once lengths are final. The price is unknown today.

## 3. Harness list
Coordinates are option D (x front +, y, z up; mm). BMS connectors (pcb lane):
**One connector per destination** (Chris, 2026-11-27; pcb `bms-area.md` §13). All Micro-Fit 3.0: right-angle **43650-0200 / -0300** on the board, **43645** housings on the cables.

| Edge | Connector | Pins (proposal) |
|---|---|---|
| −x | J1 sense-flex FPC (the flex's own tail) | — |
| −x | J2 shunt, Micro-Fit 2×4 | per H1 |
| −y (x −105…−84) | J3 power, **1×4** | B+, LOAD+, GND, CHASSIS (IMD reference; Chris OK'd 2026-11-27) |
| +x | J4 GV14 coil, 1×2 | X1, X2 |
| +x | J5 LED board, 1×3 | 5V, DATA, GND |
| +y (new edge, plug room y 40…65 confirmed free) | J6 charger relay, 1×3 | 86, 85, AC_SENSE |
| +y | J7 inverter CN301, 1×2 | CN301-1, CN301-2 |
| +y | J8 lid button, 1×2 | BTN, GND |
| +y | J9 box-air NTC, 1×2 | NTC, GND |

**Pin numbers are proposals until pcb's schematic.**

**BMS-connector facts (pcb audit, 2026-11-27):**
- **Micro-Fit 3.0 crimps take insulation ≤ 1.85 mm OD.** Thick-wall 18 AWG (UL1015, ≈ 2.5 mm) won't fit. Use thin-wall 18 AWG on the J3 branches, e.g. UL1061 or XLPE UL3266 ⚠️ (verify OD). The 18 AWG terminal is **43030-0038**.
- **J3 is 43650-0400 (1×4)** on the board.
- **Box-air NTC = Vishay NTCLE413E2103F102L** (10 k, B 3435 K) with AWG30 leads, too thin for a Micro-Fit crimp. The vendor splices it to 22–24 AWG with heat shrink, or we pick a probe with thicker leads ⚠️.
- **GV14 coil:** Sensata forbids an external diode (internal TVS; X2 can reach B+ + 55 V at turn-off). The board uses 100 V FETs; the harness wire must be ≥ 100 V rated (any normal hook-up wire is).

### Signal (BMS side Molex Micro-Fit 3.0 43025 housings, 43030 crimps; 22–24 AWG unless noted)
| ID | From → to | Wires | Device-side connector | Pinout (device → BMS) | Length ⚠️ |
|---|---|---|---|---|---|
| **H1 Shunt** | Shunt pigtail receptacle → J2 | The existing harness is the module's pigtail, **soldered directly to the shunt module PCB** (Chris, 2026-11-27 ✓). Its free end is a **10-position 2×5 Mini-Fit-Jr-style receptacle, 8 loaded, non-catalog Tesla coding** (bridge between ckts 6–7, non-standard polarization). **No catalog mate known** ⚠️. H1 = a plug that mates with it → J2 ([tesla-shunt.md §3a](tesla-shunt.md)) | Candidate: Mini-Fit Jr. plug 39-01-3103 + 5558 terminals, **test fit first** ⚠️ | Receptacle ckt → signal: 1 VDD, 2 PC4, 3 MISO, 4 SCK, 5 OC_FLAG, 6 GND, 7 NSS, 8 MOSI, 9–10 empty. To J2 (proposal): VDD, GND, NSS, SCK, MISO, MOSI, OC_FLAG → J2-1…7; PC4 unused | ⚠️ length to confirm (v16.1 route 188 mm) |
| H1 options | If Chris's test-fit passes: J2 = Molex 39-30-1102 right-angle Mini-Fit Jr 2×5 and the Tesla pigtail plugs straight in (no harness). Needs 13.8 mm mated height (vs 12 limit) and 2.76 mm tails, so the lid goes up 2 mm (z 333 → 335) and the bridge standoffs to 4 mm. Otherwise: J2 Micro-Fit 2×4 plus a short Mini-Fit Jr ↔ Micro-Fit adapter harness (pcb audit, 2026-11-27) | — | — | — | — |
| **H2 Power taps** | B+ (in-bar, (135, −15, 256)); LOAD+ (2151 inverter stud (64, −37, 285)); GND (node A (−143, −55, 253)) → J3 | 3 × 18 AWG | B+: M6 ring + **Eaton ATM-FHID inline holder, 5 A ATM**; LOAD+: M10 (3/8″) ring + ATM-FHID, 2 A; GND: M8 ring ⚠️ (node-A bolt size unknown) | B+ → J3-1; LOAD+ → J3-2; GND → J3-3 | B+ ≈ 360, LOAD+ ≈ 280, GND ≈ 220 mm (holders within 178 mm of the ring, W3) |
| **H2b IMD chassis reference** | J3-4 → ring lug under a rear-plate screw: top-row +y corner screw, ≈ (−158, +y wall, z ≈ 281) ⚠️ exact screw set by tower17 | 1 × 22 AWG green/yellow | M4 ring (rear-plate screws are M4 button heads) | CHASSIS → J3-4 | ≈ 100 mm |
| **H3 Outputs** | J4 → GV14 coil; J6 → charger relay coil (+ AC sense); J7 → inverter CN301 | 6 × 20 AWG | GV14: its own **38 cm flying leads**, red X1+ / black X2−, terminated by the vendor at full length (no cut; W1, R7). Relay: 2 × 6.3 mm FASTON receptacles + boots on pins 85/86 ⚠️ (coil tab size to check). CN301: **JST XHP-2 + SXH-001T** | J4: X1, X2. J6: 86, 85, AC_SENSE. J7: CN301-1, CN301-2 (*proposals*) | GV14 ≈ 270 (lead 380 ✓), relay ≈ 310, CN301 ≈ 210 mm |
| **H4 Lid + front** | J8 → lid button; J5 → LED board; J9 → box-air NTC | 2 + 3 + 2 | Button: its own terminals (part TBD ⚠️); LED link: Micro-Fit 1×3 (5 V, GND, DATA); NTC: 10 k NTC on a 2-wire lead, sealed tip, near the inverter AC end | J5: 5V, DATA, GND. J8: BTN, GND. J9: NTC, GND (*proposals*) | button ≈ 250 + 150 loop, LED ≈ 310, NTC ≈ 200 mm |
| **H5 AC-present sense** | Charger side of the relay (−141, 66, 250) → BMS | 1 × 22 AWG + ring/FASTON piggyback | piggyback FASTON on relay pin 30 ⚠️ | → J6-3 AC_SENSE (*proposal*); no return wire (ground via J3) | ≈ 260 mm |
| **H6 Inverter fan** | Sunon MF40201VX-1000U-G99 leads → inverter CN100 | 2 or 3 × 26 AWG | **JST XHP-3 + SXH-001T** (1 +V, 2 −V, 3 PWM if the fan has a tach/PWM lead; the -G99 is 2-wire ⚠️) | fan red → CN100-1, black → CN100-2 | ≈ 130 mm (fan's own lead length ⚠️) |
| H7 Antenna | ESP32-S3-WROOM-1U U.FL → flex antenna behind the front plate's light-pipe slot | coax 1.13 mm | **catalog flex antenna with a U.FL pigtail** (e.g. Molex 146153 series, ⚠️ length to confirm) | — | ≈ 250 mm |
| — Sense flex | Flex PCB tail → J1 FPC | — | made with the flex (pcb lane) | — | — |

### DC power (105 ℃ fine-strand, tinned lugs, adhesive heat shrink)
| ID | From → to | Wire | Ends | Current / fuse | Length ⚠️ |
|---|---|---|---|---|---|
| **P1a Charger + to relay** | NPB-360 TB V+ (−126, 40, 240) → relay pin 30 (−141, 66, 245) | 10 AWG red | TB: bootlace ferrule ⚠️ (DT-66 screw terminal) → 6.3 mm FASTON receptacle for 10–12 AWG ⚠️ | 20 A | ≈ 90 mm |
| **P1b Relay to fuse** | relay pin 87 → 2151 charger stud (34, −37, 285) | 10 AWG red | FASTON → 3/8″ ring | 20 A; MRBF 30 A | ≈ 360 mm |
| **P2 Charger −** | NPB-360 TB V− → shunt node B (−81, −55, 260) | 10 AWG black | ferrule → M8 ring ⚠️ | 20 A | ≈ 180 mm |
| **P3 Inverter +** | NTS-400P TB1 (red 1327) (−86, 10, 290) → 2151 inverter stud (64, −37, 285) | 10 AWG red (max for 261G2) | **Anderson 1327 + 261G2-LPBK** → 3/8″ ring | 41 A at 400 W, 11 V; MRBF 50 A | ≈ 240 mm |
| **P4 Inverter −** | TB1 (black 1327G6) → node B | 10 AWG black | 1327G6 + 261G2-LPBK → M8 ring ⚠️ | 41 A | ≈ 130 mm |

### Mains (UL 1015 / 105 ℃, 18 AWG, kept apart from LV, W5)
| ID | From → to | Ends | Pinout | Length ⚠️ |
|---|---|---|---|---|
| **A1 AC in** | Lid IEC C14 inlet (138, 20, 308) → NPB-360 C14 inlet (front) | Inlet side: 3 × 6.3 mm FASTON + boots ⚠️ (inlet part TBD); charger side: **L-com ACPWRC-C13LR** right-angle C13 (field-term, screw terminals: the vendor terminates it) | L → L, N → N, PE → PE + PE jumper to chassis | ≈ 180 + 150 loop |
| **A2 AC out** | NTS-400P CN500 (front, +y) → lid NEMA 5-15R | CN500: **JST VHR-6N + SVH-21T-P1.1**; outlet: FASTON or screw ⚠️ (outlet part TBD) | CN500-6 L → outlet brass (hot); CN500-4 N → outlet silver (neutral); CN500-1 FG → outlet ground → chassis; CN500-2, 3, 5 empty | ≈ 50 + 150 loop |
| **A3 PE bonds** | Inlet PE, outlet ground, inverter FG → chassis lug (front-plate screw, star washer, enclosure.md) | M4 ring | — | ≈ 100 mm each |

**Not harnesses (no cable):** SB175 (busbar contacts bolted to the bay copper), all bay copper, the sense flex.

## 4. Findings for the pcb lane (sent 2026-11-27)
- ✓ **Resolved:** one connector per destination, J1–J9 (Chris approved, 2026-11-27); every branch has its own GND.
- The G6S precharge relay is gone (two P-FETs), so the board no longer has a relay coil for precharge. **H3 still carries the charger-relay coil.**
- **NTS-400P CN50** is a UART (GND/RX/TX, CHYAO SHIUNN JS-2001). The inverter could report its status to the ESP32 over it. Not in scope; noted as an option ⚠️ (protocol not published in the datasheet).

## 5. Traps
| # | Trap | Rule |
|---|---|---|
| T1 | Purchased parts with flying leads (GV14 38 cm, fan) can't be "harnessed" without the part | The vendor procures or receives the part and terminates its leads at full length; no cutting at home (W1, R7) |
| T2 | v16's "GV14 leads cut and crimped" (signal-wiring §2) means cutting a purchased part's leads | Terminate at full length, or have the vendor cut. Never DIY |
| T3 | Loombotic's verified catalog is Molex/Amphenol-heavy: JST XH/VH, PP45 and FASTONs are custom lines | Prefer Micro-Fit/Mini-Fit on our side; accept custom lines for fixed device-side connectors |
| T4 | The NPB-450's DF11 CAN connector disappeared with the NPB-360 | No charger signal harness. Charger stop = relay; AC sense = H5 |

## 6. Sources
- Loombotic home page and harness editor catalog, read 2026-11-27 ✓
- NextPCB cable-assembly quote page; PCBWay quote page (web search, 2026-11-27) ⚠️ not opened in the browser
- NTS-400P-SPEC 2026-03-26 p.6–7: TB1, CN500, CN301, CN100, CN50 pinouts and mates ✓
- Sensata GV14 datasheet: coil termination A = flying leads 38 cm, red X1+ / black X2− ✓
- TE F4 relay datasheet (Rev 0217) ✓; NPB-360-SPEC (TB terminal DT-66-B11W-02, 40 A) ✓
- Tesla J1 pinout: tesla-shunt.md §3 (Mini-Fit type unconfirmed) ⚠️

## 7. Open items
- tower17 CAD: route every harness and replace the ⚠️ lengths (W6 loops included); then quotes: NextPCB (live tool) and Loombotic (needs an account).
- Chris: the existing shunt harness, its far-end connector and length (H1).
- Chris: vendor. Loombotic ≈ $2,245 vs NextPCB ≈ $495 (estimate, or $0 if Zep sponsors) vs PCBWay (unquoted).
- ⚠️ Parts still to pick: lid C14 inlet, NEMA 5-15R outlet, push-button, NTC lead, U.FL antenna (with their terminals).
- ⚠️ Confirm: Tesla J1 housing, shunt node-A/B bolt size, relay coil tab size, fan lead wires and length, NPB-360 TB wire range for 10 AWG.
