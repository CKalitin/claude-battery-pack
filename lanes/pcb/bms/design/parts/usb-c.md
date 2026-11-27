# J10 USB-C programming port (ESP32-S3 native USB-Serial-JTAG)

**Pick:** GCT USB4105-GF-A receptacle on the +y edge, ST USBLC6-2SC6 on D+/D−/VBUS, 2 × 5.1 kΩ CC resistors, **TI TPS2116 power mux** feeding only the 3.3 V LDO, IO0/EN/GND test pads. Tag-Connect dropped (Chris).

## 1. Requirements
| # | Requirement | From |
|---|---|---|
| R1 | USB 2.0 full speed, flash and console | Chris; ESP32-S3 USB-Serial-JTAG |
| R2 | Flash a board with no pack: VBUS powers the 3.3 V rail | team lead |
| R3 | **Never back-feed** the host, and never back-feed the buck | team lead; buck VOUT must not exceed VIN |
| R4 | Height ≤ 12 mm, catalog part with a KiCad footprint | intent §6 |

## 2. Receptacle candidates
| Part | Type | KiCad footprint (`Connector_USB:`) | Stock | Verdict |
|---|---|---|---|---|
| **GCT USB4105-GF-A** | 16-pin USB 2.0, top mount, SMT + shell stakes, 3.31 mm high | `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | in stock | **✓** maker drawing and spec |
| Molex 217179-0001 | 16-pin top mount | none matched | in stock (reel) | ✗ footprint |
| JAE DX07S016JA1R1500 | 24-pin shell | exists | in stock | ✗ no gain |
| Amphenol 12401610E4#2A | USB 3.1, 24-pin | exists | in stock | ✗ more pins to solder |
| HRO TYPE-C-31-M-12 | 16-pin (LCSC) | exists | not checked | ✗ weak datasheet |
| GCT mid-mount parts | — | not compared ⚠️ | — | not needed: 3.31 mm clears easily |

USB4105: 48 V; 5 A over the VBUS pins; −40…+85 °C; 20 000 cycles; shell stake 0.95 mm (below the 1.6 mm board ✓ R4). Spec Rev A3, drawing 18/12/23.

## 3. ESD, CC, data
| Item | Value | Note |
|---|---|---|
| ESD | **USBLC6-2SC6** (ST), `Package_TO_SOT_SMD:SOT-23-6` | 3.5 pF max, I_RM ≤ 150 nA, IEC 61000-4-2 8 kV contact (DS4260 Rev 7). Pins 1/6 = I/O1, 3/4 = I/O2, 2 GND, 5 VBUS. Order only ST (clones carry the same number) |
| CC1, CC2 | **5.1 kΩ 1 %** each to GND, separate | tells a USB-C host to supply 5 V |
| D+/D− | GPIO20 / GPIO19; A6+B6 and A7+B7 joined at the receptacle | |
| Series R | **22 Ω** each, close to the module; cap pads to GND left DNP | Espressif HW design guidelines ("reserve series resistors 22/33 Ω and capacitors", §USB) |
| Shield | to GND directly ⚠️ | board ground = pack− (see §6) |
Layout: D+/D− as a 90 Ω differential pair, receptacle → USBLC6 → resistors → module, no stubs.

## 4. Power: VBUS → mux → LDO only

### 4a. Can the buck be back-driven at its output? **No.**
| LMR60430 datasheet (SNAS875E) | Says |
|---|---|
| §6.1 abs max | SW to PGND ≤ **V_IN + 0.3 V** |
| §8.3 | if the input falls below the output, "the output capacitors discharge through the device back to the input. This uncontrolled current flow can damage the device." |
With no pack (V_IN = 0), a diode from VBUS into the 5 V rail drives SW through L1 to ≈ 4.6 V: the high-side body diode conducts into B+, past the abs max, and tries to power the whole B+ net from the laptop. **So VBUS must not reach the buck output** (the brief's "VBUS → diode → 5 V rail" needs a second blocking element in the buck path, or has to join downstream).

| Option | Back-feed | Drop | Verdict |
|---|---|---|---|
| One Schottky VBUS → 5 V rail | **drives the buck output with VIN = 0** (through the high-side body diode into B+) and lets USB feed the LEDs | 0.3–0.5 V | ✗ R3 |
| Two Schottkys OR into the LDO input | blocked | 0.3–0.5 V both paths; reverse leakage µA–mA hot | works, two parts |
| 2 × LM66100 ideal diodes | blocked | low | two parts (not audited) |
| Ideal-diode mux into the **whole 5 V rail** (TI TPS2121, 4.5 A, 56 mΩ typ, VQFN-HR 2 × 2.5; SLVSEA3F) | blocked both ways, buck protected | ≈ 0.14 V at 2.45 A: rail min ≈ 4.76 V vs the shunt's 4.7 V ⚠️ | works and matches the brief literally; ✗ puts a part in the 3 A path, ≈ 200 µA while running, USB can reach the LEDs and shunt (needs firmware care), one more fine-pitch footprint |
| **TPS2116** priority mux into the LDO input | **reverse-current blocking on both inputs** | 40 mΩ | **✓ one part** |

```
5V (buck) ──┬── VIN1 ┐
            301k      TPS2116 ── VOUT ── "5V_LDO" ── TLV1117LV IN
            PR1       │
            100k     │
VBUS ──┬────── VIN2 ┘        MODE = VIN1, ST → GPIO (pull-up)
       ├─ 100 nF ─ GND
       └─ 1.8 Ω ─ 4.7 µF ─ GND     (hot-plug damping)
```
Everything else on 5 V (shunt, translator, buffers, relay coils, LED switch) stays on the **buck rail**, so USB can never run them.

| Item | Value |
|---|---|
| MPN | TPS2116DRLR, SOT-583, `Package_TO_SOT_SMD:SOT-583-8` |
| Datasheet | SLVSFG1A (rev. May 2021); ACTIVE ⚠️ maker page not checked; in stock |
| Pins | 1 GND, 2+7 VOUT, 3 VIN1, 4 PR1, 5 MODE, 6 VIN2, 8 ST |
| Limits | 1.6–5.5 V (abs 6 V), 2.5 A; I_Q 1.3 µA typ |
| Switch threshold | V_REF 1 V (0.92–1.08) × (301 + 100)/100 = **4.0 V** (3.7–4.3 V): buck present → VIN1 |
| ST | open drain, low = powered from VIN2 (USB) → firmware knows it has no pack power |
| Caps | VIN2 (VBUS): **100 nF** (CC0402KRX7R9BB104) + **1.8 Ω** (CRCW08051R80FKEA) in series with **4.7 µF** 16 V X7R (CL21B475KOFNNNE); total 4.8 µF ≤ 10 µF USB inrush rule. VIN1: buck caps; VOUT: the LDO's 22 µF (soft start ≈ 1–2 ms → ≈ 0.1 A inrush ✓) |

**VBUS hot-plug (review m9; TPS2116 abs max 6 V).** ngspice: 5.25 V step, cable R 0.1–0.2 Ω, 4.7 µF taken as 3.5–4.7 µF effective.
| VIN2 network | Peak, L = 0.5–3 µH |
|---|---|
| 1 µF only (old) | **7.2–10 V** ✗ |
| 100 nF + 1 Ω + 1 µF | up to ≈ 7.5 V ✗ (damping cap too small) |
| **100 nF + 1.8 Ω + 4.7 µF** | **≤ 5.85 V** ✓ (thin margin) |
| 5 V TVS instead | ✗ clamps near 9 V at amperes, above 6 V |
⚠️ Source softness, ESR and the USBLC6 are not modelled: scope VBUS on a hot plug.

**USB-only power budget:** ESP32 ≤ 355 mA peak + ≈ 15 mA ✓ under a 500 mA default port. LDO input 4.75 V − 0.02 V; headroom ≥ 1.3 V ✓.

## 5. BOOT fallback
Test pads **IO0, EN, GND** side by side. Hold IO0 low while pulsing EN → download mode (GPIO46 low by its default pull-down; ESP32-S3 boot-mode table). Normally the USB-Serial-JTAG resets into the loader by itself.

## 6. Traps
- **Pack connected:** USB ground joins pack− to the laptop's earth. The IMD reads an insulation fault while plugged in and the chassis is earthed: expected; firmware note (intent Q3).
- The pack's board ground is node A: don't program while heavy load current flows through other ground paths ⚠️.
- The +y plug room is 25 mm: a USB-C plug overmold may be longer ⚠️; program with the lid off.
- Receptacle front edge position per the GCT drawing (1.85 mm min to the plug face) at layout.
- Unplugged, VBUS floats; the receptacle sees no voltage from the board (mux blocks) ✓.

## 7. Open
- ⚠️ Check the KiCad footprint against the 18/12/23 drawing.
- Disable USB-OTG download boot by eFuse if unused (Espressif guideline).
